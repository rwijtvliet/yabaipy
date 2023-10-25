"""Module to manipulate windows."""

# # Specifying a window to yabai:
# - Use the window id.

from __future__ import annotations
from typing import Any, List, Dict
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from .shared import run_command
import json
from . import displays, spaces
from .decorators import (
    accept_space_instance,
    accept_window_instance,
    accept_display_instance,
)


def verify_window_selector(window_sel: str) -> str:
    """Verify and adjust window selector to avoid inadvertently selecting incorrect window."""
    if window_sel == "":
        raise ValueError(
            "window selector cannot be the empty string (use None to select current window."
        )
    if window_sel is None:
        window_sel = ""
    return window_sel


def dictionary_from_window_sel(window_sel: str) -> Dict[str, Any]:
    window_sel = verify_window_selector(window_sel)
    return json.loads(run_command(f"yabai -m query --windows --window {window_sel}"))


def dictionaries() -> List[Dict[str, Any]]:
    return json.loads(run_command("yabai -m query --windows"))


def get_all_windows() -> List[Window]:
    """Create Window for all windows."""
    return [Window(dic["id_"]) for dic in dictionaries()]


@dataclass_json
@dataclass(frozen=True)
class Props:
    """Class to hold the properties of a window. The properties are queried and stored
    at the moment of creation, and not updated afterwards."""

    id_: int = field(metadata=config(field_name="id"))
    pid: int
    app: str
    title: str
    frame: Dict[str, float]
    role: str
    subrole: str
    display: int
    space: int
    level: int
    opacity: float
    split_type: str = field(metadata=config(field_name="split-type"))
    split_child: str = field(metadata=config(field_name="split-child"))
    stack_index: str = field(metadata=config(field_name="stack-index"))
    can_move: bool = field(metadata=config(field_name="can-move"))
    can_resize: bool = field(metadata=config(field_name="can-resize"))
    has_focus: bool = field(metadata=config(field_name="has-focus"))
    has_shadow: bool = field(metadata=config(field_name="has-shadow"))
    has_border: bool = field(metadata=config(field_name="has-border"))
    has_parent_zoom: bool = field(metadata=config(field_name="has-parent-zoom"))
    has_fullscreen_zoom: bool = field(metadata=config(field_name="has-fullscreen-zoom"))
    is_native_fullscreen: bool = field(
        metadata=config(field_name="is-native-fullscreen")
    )
    is_visible: bool = field(metadata=config(field_name="is-visible"))
    is_minimized: bool = field(metadata=config(field_name="is-minimized"))
    is_hidden: bool = field(metadata=config(field_name="is-hidden"))
    is_floating: bool = field(metadata=config(field_name="is-floating"))
    is_sticky: bool = field(metadata=config(field_name="is-sticky"))
    is_topmost: bool = field(metadata=config(field_name="is-topmost"))
    is_grabbed: bool = field(metadata=config(field_name="is-grabbed"))

    @classmethod
    def from_window_sel(cls, window_sel: str) -> Props:
        return cls.from_dict(dictionary_from_window_sel(window_sel))


class Window:
    """Class to manipulate windows. The properties are accessible via the `.props()`
    method. This information is fetched whenever called, so you may want to store it in
    a temporary variable (if the relevant properties do not change before they are)
    needed.

    Internally, the uuid and the label are stored, which are always kept up-to-date.
    That way, other methods of this class can always be called, even if mission-control
    index, or label, or display (or any other property) has changed. (For unlabeled
    spaces, this is done by using the uuid to find the space's index every time it's
    needed. For labeled spaces, this is done using the label. Additional logic is
    implemented to cache the label whenever it is changed, and to ensure a label isn't
    used twice.)

    Parameters
    ----------
    window_sel : str, optional (default: None)
        <window_id> | prev | next | first | last | recent | mouse | largest | smallest |
        sibling | first_nephew | second_nephew | uncle | first_cousin | second_cousin |
        stack.prev | stack.next | stack.first | stack.last | stack.recent
        Use None for current window.
    """

    def __init__(self, window_sel: str = None):
        data = Props.from_window_sel(window_sel)
        self._id: int = data.id_

    id_: int = property(lambda self: self._id)

    @property
    def window_sel(self) -> str:
        """Currently-correct (unique) window selector with minimal queries."""
        return self.id_

    # --- fetch properties

    def props(self) -> Props:
        """Query yabai API and return the current window properties."""
        return Props.from_window_sel(self.window_sel)

    # --- dunder

    def __repr__(self) -> str:
        return f"Window object with id '{self.id_}'."

    def __eq__(self, other: Any) -> bool:
        return type(self) is type(other) and self.id_ == other.id_

    # --- from yabai API

    def focus(self) -> None:
        """Focus windows."""
        try:
            run_command(f"yabai -m window --focus {self.window_sel}")
        except ValueError as e:
            if "already focused window" not in e.args[0]:
                raise e

    @accept_window_instance
    def swap_with(self, window_sel: str) -> None:
        """Swap window with window ``window_sel``."""
        try:
            run_command(f"yabai -m window {self.window_sel} --swap {window_sel}")
        except ValueError as e:
            if "cannot swap window with itself" not in e.args[0]:
                raise e

    @accept_window_instance
    def warp_onto(self, window_sel: str) -> None:
        """Warp window onto window ``window_sel`` (i.e., re-insert the window, splitting
        the given window)."""
        run_command(f"yabai -m window {self.window_sel} --warp {window_sel}")

    @accept_window_instance
    def stack_onto(self, window_sel: str) -> None:
        """Stack window onto window ``window_sel``."""
        run_command(f"yabai -m window {self.window_sel} --stack {window_sel}")

    def set_insert_mode(self, mode: str) -> None:
        """Set the splitting mode of the window. If current splitting mode matches the
        selected mode, the action will be undone. Parameter ``mode``: {'north', 'south',
        'east', 'west', 'stack'}."""
        run_command(f"yabai -m window {self.window_sel} --insert {mode}")

    def set_grid(
        self, rows: int, cols: int, startx: int, starty: int, width: int, height: int
    ) -> None:
        """Set frame of window based on self-defined grid. Parameters ``startx`` and
        ``starty`` are 1-indexed."""
        run_command(
            f"yabai -m window {self.window_sel} --grid {rows}:{cols}:{startx}:{starty}:{width}:{height}"
        )

    def move(self, relabs: str, dx: int, dy: int) -> None:
        """Move window. If ``relabs``=='abs', ``dx`` and ``dy`` are new window position
        in pixels. If ``relabs``=='rel', they are the change in the position."""
        run_command(f"yabai -m window {self.window_sel} --move {relabs}:{dx}:{dy}")

    def resize(self, handle: str, dx: int, dy: int) -> None:
        """Resize window. If ``handle``=='abs', ``dx`` and ``dy`` are its new size in
        pixels (not usable on managed windows). If ``handle`` is one of {'top', 'left',
        'bottom', 'right', 'top_left', 'top_right', 'bottom_right', 'bottom_left'},
        they are the distance the handle is moved by."""
        run_command(f"yabai -m window {self.window_sel} --resize {handle}:{dx}:{dy}")

    def set_ratio(self, relabs: str, dr: float) -> None:
        """Set split ratio (when the window is split into two). If ``relabs``=='abs',
        ``dr`` is the new split ratio. If ``relabs``=='rel', it is the change in the
        split ratio (<0 to descrease size of left child)."""
        run_command(f"yabai -m window {self.window_sel} --ratio {relabs}:{dr:0.3f}")

    def toggle(self, what: str) -> None:
        """Toggle window setting. Parameter ``what`` is one of {'float', 'sticky',
        'topmost', 'pip', 'shadow', 'border', 'split', 'zoom-parent', 'zoom-fullscreen',
        'native-fullscreen', 'expose'}. (SIP must be partially disabled for some.)"""
        run_command(f"yabai -m window {self.window_sel} --toggle {what}")

    def set_layer(self, layer: int) -> None:
        """Set stacking layer of window. (SIP must be partially disabled.)"""
        run_command(f"yabai -m window {self.window_sel} --layer {layer}")

    def set_opacity(self, opacity: float) -> None:
        """Set opacity of window. The window will no longer be eligible for automatic
        change in opacity upon focus change. (Set to 0.0 to reset back to full opacity
        OR have it be automatically managed through focus changes.) (SIP must be
        partially disabled.)"""
        run_command(f"yabai -m window {self.window_sel} --opacity {opacity:0.3f}")

    @accept_display_instance
    def send_to_display(self, display_sel: str) -> None:
        """Send window to display ``display_sel``."""
        run_command(f"yabai -m window {self.window_sel} --display {display_sel}")

    @accept_space_instance
    def send_to_space(self, space_sel: str) -> None:
        """Send window to space ``space_sel``."""
        run_command(f"yabai -m window {self.window_sel} --space {space_sel}")

    def minimize(self) -> None:
        """Minimize window. Only works on windows with minimize button in titlebar."""
        run_command(f"yabai -m window --minimize {self.window_sel}")

    def deminimize(self) -> None:
        """Restore window if minimized. Window will only get focus if owning application
        has focus. (Use .focus() method to restore as focused window.)"""
        run_command(f"yabai -m window --deminimize {self.window_sel}")

    def close(self) -> None:
        """Close window. Only works on windows with close button in titlebar."""
        run_command(f"yabai -m window --close {self.window_sel}")

    # --- own additions

    def get_display(self) -> displays.Display:
        """Display of the window."""
        display_idx = self.props().display
        return displays.Display(display_idx)

    def get_space(self) -> spaces.Space:
        """Space of the window."""
        space_idx = self.props().space
        return spaces.Space(space_idx)

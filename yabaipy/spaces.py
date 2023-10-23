"""Module to manipulate spaces."""

# Difficulties in keeping track of space:
# - Not each space has a label.
# - The label of a space changes if space is relabelled.
# - The mission-control index of a space changes if space is moved.
# - The uuid of a space IS constant, but cannot be easily be used to select a space.
#
# Specifying a space to yabai:
# - If the space has a (non-emptystring) label, use that.
# - Otherwise, use the uuid to find the mission-control index, and use that.
#
# Consequences:
# - The label, if not the emptystring, must be unique. This is assumed to be true, and
#   enforced for new labels when using the Space.set_label() method.
# - The label is stored in the Space instance, and must be updated when the space is
#   given a new label. This is done automatically when using the Space.set_label() method.

from __future__ import annotations
from typing import Any, List, Dict
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from .shared import run_command
import json
from . import displays, windows


FORBIDDEN_LABELS = ["prev", "next", "first", "last", "recent", "mouse"]


def assert_label_allowed(label: str) -> None:
    """Raise ValueError if label is not allowed."""
    label = label.strip().lower()
    if not label:
        raise ValueError("Label forbidden; cannot be the emptystring.")
    if label in FORBIDDEN_LABELS:
        raise ValueError(f"Label '{label}' forbidden; reserved keyword.")
    if label.isdigit():
        raise ValueError(f"Label '{label}' forbidden; cannot be number.")
    if label in (dic["label"].lower() for dic in dictionaries()):
        raise ValueError(f"Label '{label}' forbidden; already exists.")


def verify_space_selector(space_sel: str) -> str:
    """Verify and adjust space selector to avoid inadvertently selecting incorrect space."""
    if space_sel == "":
        raise ValueError(
            "Space selector cannot be the empty string (use None to select current space)."
        )
    if space_sel is None:
        space_sel = ""
    return space_sel


def dictionary_from_space_sel(space_sel: str) -> Dict[str, Any]:
    space_sel = verify_space_selector(space_sel)
    return json.loads(run_command(f"yabai -m query --spaces --space {space_sel}"))


def dictionary_from_uuid(uuid: str) -> Dict[str, Any]:
    for dic in dictionaries():
        if dic["uuid"] == uuid:
            return dic
    raise ValueError(f"Cannot find space with uuid {uuid}.")


def dictionaries() -> List[Dict[str, Any]]:
    return json.loads(run_command("yabai -m query --spaces"))


def get_all_spaces() -> List[Space]:
    """Create Space for all spaces."""
    return [Space(dic["index"]) for dic in dictionaries()]


@dataclass_json
@dataclass(frozen=True)
class Props:
    """Class to hold the properties of a space. The properties are queried and stored
    at the moment of creation, and not updated afterwards."""

    id_: int = field(metadata=config(field_name="id"))
    uuid: str
    index: int
    label: str
    type_: str = field(metadata=config(field_name="type"))
    display: int
    windows: List[int]
    first_window: int = field(metadata=config(field_name="first-window"))
    last_window: int = field(metadata=config(field_name="last-window"))
    has_focus: bool = field(metadata=config(field_name="has-focus"))
    is_visible: bool = field(metadata=config(field_name="is-visible"))
    is_native_fullscreen: bool = field(
        metadata=config(field_name="is-native-fullscreen")
    )

    @classmethod
    def from_space_sel(cls, space_sel: str) -> Props:
        return cls.from_dict(dictionary_from_space_sel(space_sel))

    @classmethod
    def from_uuid(cls, uuid: str) -> Props:
        return cls.from_dict(dictionary_from_uuid(uuid))


class Space:
    """Class to manipulate spaces. The properties are accessible via the `.props()`
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
    space_sel : str, optional (default: None)
        LABEL | mission-control index | prev | next | first | last | recent | mouse
        Use None for current space.
    """

    def __init__(self, space_sel: str = None):
        data = Props.from_space_sel(space_sel)
        self._label: str = data.label  # cache label
        self._uuid: str = data.uuid  # for backup: cache uuid

    label: str = property(lambda self: self._label)
    uuid: str = property(lambda self: self._uuid)

    @property
    def space_sel(self) -> str:
        """Currently-correct (unique) space selector with minimal queries."""
        if self._uuid is None:
            raise ValueError("This space has been destroyed.")
        # Use label if possible (no queries needed)
        if (label := self._label) != "":
            return label
        # Otherwise, use uuid to find index (slower)
        return dictionary_from_uuid(self._uuid)["index"]

    # ---

    def props(self) -> Props:
        """Query yabai API and return the current space properties."""
        return Props.from_space_sel(self.space_sel)

    # ---

    def __repr__(self) -> str:
        return f"Space object with uuid '{self._uuid}' and label '{self._label}'."

    def __eq__(self, other: Any) -> bool:
        return type(self) is type(other) and self.uuid == other.uuid

    # ---

    def get_display(self) -> displays.Display:
        """Display of the space."""
        display_idx = self.props().display
        return displays.Display(display_idx)

    def get_windows(self) -> List[windows.Window]:
        """Windows of the space."""
        space_idx = self.props().index
        wis = windows.get_all_windows()
        return [wi for wi in wis if wi.props().space == space_idx]

    # ---

    def focus(self) -> None:
        """Focus space."""
        try:
            run_command(f"yabai -m space --focus {self.space_sel}")
        except ValueError as e:
            if "already focused space" not in e.args[0]:
                raise e

    def destroy(self) -> None:
        """Destroy space."""
        run_command(f"yabai -m space --destroy {self.space_sel}")
        self._uuid = None

    def move_to(self, space_sel: str) -> None:
        """Move space to position of space ``space_sel`` (must be on the same display)."""
        try:
            run_command(f"yabai -m space {self.space_sel} --move {space_sel}")
        except ValueError as e:
            if "cannot move space to itself" in e.args[0]:
                pass  # no move necessary
            else:
                raise e

    def swap_with(self, space_sel: str) -> None:
        """Swap space with space ``space_sel`` (must be on the same display)."""
        try:
            run_command(f"yabai -m space {self.space_sel} --swap {space_sel}")
        except ValueError as e:
            if "cannot swap space with itself" in e.args[0]:
                pass  # no move necessary
            else:
                raise e

    def send_to_display(self, display_sel: str) -> None:
        """Send space to display ``display_sel``."""
        try:
            run_command(f"yabai -m space {self.space_sel} --display {display_sel}")
        except ValueError as e:
            if "already located on the given display" in e.args[0]:
                pass
            else:
                raise e

    def balance(self, axis: str = "xy") -> None:
        """Adjust split ratios on space so that windows along given axis occupy same distance.
        Parameter ``axis`` is one of {'x', 'y', 'xy'}."""
        if "x" in axis and "y" in axis:
            arg = ""
        elif "x" in axis:
            arg = "x-axis"
        elif "y" in axis:
            arg = "y-axis"
        else:
            raise ValueError("Parameter ``axis`` must contain 'x', 'y', or both.")
        run_command(f"yabai -m space {self.space_sel} --balance {arg}")

    def mirror(self, axis: str = "x") -> None:
        """Flip the windows on space along given axis. Parameter ``axis`` is one of
        {'x', 'y'}."""
        if axis == "x":
            arg = "x-axis"
        elif axis == "y":
            arg = "y-axis"
        else:
            raise ValueError("Parameter ``axis`` must be 'x' or 'y'.")
        run_command(f"yabai -m space {self.space_sel} --mirror {arg}")

    def rotate(self, angle: int = 0) -> None:
        """Rotate the windows on space through given angle in counterclockwise direction.
        Parameter ``angle``: {90, 180, 270}."""
        if angle == 0 or angle == 360:
            return
        run_command(f"yabai -m space {self.space_sel} --rotate {angle}")

    def set_padding(
        self, relabs: str, top: int, bottom: int, left: int, right: int
    ) -> None:
        """Set padding around space. If ``relabs``=='abs', the other values are the new
        padding in pixels. If ``relabs``=='rel', they are the change in the padding.
        Parameters ``top``, ``bottom``, ``left``, ``right``: padding on resp. side."""
        run_command(
            f"yabai -m space {self.space_sel} --padding {relabs}:{top}:{bottom}:{left}:{right}"
        )

    def set_gap(self, relabs: str, gap: int) -> None:
        """Set gap between windows on space to ``gap``. Parameter ``relabs`` is one of
        {'rel', 'abs'}."""
        run_command(f"yabai -m space {self.space_sel} --gap {relabs}:{gap}")

    def toggle(self, what: str) -> None:
        """Toggle space setting. Parameter ``what`` is one of {'padding', 'gap',
        'mission-control', 'show-desktop'}."""
        run_command(f"yabai -m space {self.space_sel} --toggle {what}")

    def set_layout(self, what: str) -> None:
        """Set layout on space. Parameter ``what`` is one of {'bsp', 'stack', 'float'}."""
        run_command(f"yabai -m space {self.space_sel} --layout {what}")

    def set_label(self, label: str) -> None:
        """Set label of space."""
        assert_label_allowed(label)
        run_command(f"yabai -m space {self.space_sel} --label {label}")
        self._label = label  # store because used as space_sel

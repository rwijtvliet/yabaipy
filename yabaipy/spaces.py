"""Module to manipulate spaces."""

# Difficulties in keeping track of space:
# - Not each space has a label.
# - The label of a space changes if space is relabelled.
# - The mission-control index of a space changes if space is moved.
# - The uuid of a space IS constant, but cannot be easily be used to select a space.
#
# Handling:
# - Use mission-control index to specify a space to yabai.
# - Update space information to find correct mission-control index whenever calling yabai.

# Use cases:
#
# Initial setup:
# . Several spaces may exist without label; must be able to be labeled.

from __future__ import annotations
from typing import Any, List, Dict
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from .shared import run_command
import json
from .displays import Display


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

    @classmethod
    def get_all(cls) -> List[Space]:
        """Create Space for all spaces."""
        return [cls(dic["index"]) for dic in dictionaries()]

    def __init__(self, space_sel: str = None):
        data = Props.from_space_sel(space_sel)
        self._label: str = data.label  # cache label
        self._uud: str = data.uuid  # for backup: cache uuid

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

    def props(self) -> Props:
        """Query yabai API and return the current space properties."""
        return Props.from_space_sel(self.space_sel)

    def focus(self) -> None:
        """Focus space."""
        try:
            run_command(f"yabai -m space --focus {self.space_sel}")
        except ValueError as e:
            if "already focused space" not in e.args[0]:
                raise e

    def create_here(self) -> Space:
        """Create new space on same display as this space; returning the created space."""
        display_sel = self.props().display
        run_command(f"yabai -m space --create {self.space_sel}")
        # new space is last one in this display; get mission-control index
        new_space_sel = Display(display_sel).spaces[-1]
        return Space(new_space_sel)

    def destroy(self) -> None:
        """Destroy space."""
        run_command(f"yabai -m space --destroy {self.space_sel}")
        self._uuid = None

    def move_to_other(self, space_sel: str) -> None:
        """Move space to position of space ``space_sel`` (must be on same display)."""
        try:
            run_command(f"yabai -m space {self.space_sel} --move {space_sel}")
        except ValueError as e:
            if "cannot move space to itself" not in e.args[0]:
                raise e

    def swap_with_other(self, space_sel: str) -> None:
        """Swap space with space ``space_sel`` (must be on the same display)."""
        try:
            run_command(f"yabai -m space {self.space_sel} --swap {space_sel}")
        except ValueError as e:
            if "cannot swap space with itself" not in e.args[0]:
                raise e

    def send_to_display(self, display_sel: str) -> None:
        """Send space to display ``display_sel``."""
        try:
            run_command(f"yabai -m space {self.space_sel} --display {display_sel}")
        except ValueError as e:
            if "already located on the given display" not in e.args[0]:
                raise e

    def balance(self, axis: str = "xy") -> None:
        """Adjust split ratios on space so that windows along given axis occupy same distance.
        Parameter ``axis``: {'x', 'y', 'xy'}."""
        if "x" in axis and "y" in axis:
            arg = ""
        elif "x" in axis:
            arg = "x-axis"
        elif "y" in axis:
            arg = "y-axis"
        else:  # 'x' not in axis and 'y' not in axis:
            raise ValueError("Parameter ``axis`` must contain 'x', 'y', or both.")
        run_command(f"yabai -m space {self.space_sel} --balance {arg}")

    def mirror(self, axis: str = "x") -> None:
        """Flip the windows on space along given axis. Parameter ``axis``: {'x', 'y'}."""
        if axis == "x":
            arg = "x-axis"
        elif axis == "y":
            arg = "y-axis"
        else:  # 'x' not in axis and 'y' not in axis:
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
        """Set padding around space. Parameter ``relabs``: one of {'rel', 'abs'}.
        Parameters ``top``, ``bottom``, ``left``, ``right``: padding on resp. side."""
        run_command(
            f"yabai -m space {self.space_sel} --padding {relabs}:{top}:{bottom}:{left}:{right}"
        )

    def set_gap(self, relabs: str, gap: int) -> None:
        """Set gap between windows on space to ``gap``. Parameter ``relabs``: one of {'rel', 'abs'}."""
        run_command(f"yabai -m space {self.space_sel} --gap {relabs}:{gap}")

    def toggle(self, what: str) -> None:
        """Toggle setting on/off on space.
        Parameter ``what``: one of {'padding', 'gap', 'mission-control', 'show-desktop'}.
        """
        run_command(f"yabai -m space {self.space_sel} --toggle {what}")

    def set_layout(self, what: str) -> None:
        """Set layout on space. Parameter ``what``: one of {'bsp', 'stack', 'float'}."""
        run_command(f"yabai -m space {self.space_sel} --layout {what}")

    def set_label(self, label: str) -> None:
        """Set label of space."""
        assert_label_allowed(label)
        run_command(f"yabai -m space {self.space_sel} --label {label}")
        self._label = label  # store because used as space_sel


# @verify_space_sel
# def focus(space_sel: Any) -> None:
#     """Focus space ``space_sel``."""
#     try:
#         run_command(f"yabai -m space --focus {space_sel}")
#     except ValueError as e:
#         if "already focused space" not in e.args[0]:
#             raise e
#
#
# @verify_space_sel
# def create(space_sel: Any) -> None:
#     """Create space on same display as ``space_sel`` (use None for current space)."""
#     run_command(f"yabai -m space --create {space_sel}")
#
#
# @verify_space_sel
# def destroy(space_sel: Any) -> None:
#     """Destroy space ``space_sel`` (use None for current space)."""
#     run_command(f"yabai -m space --destroy {space_sel}")
#
#
# @verify_space_sel
# def move_to_other(space_sel: Any, space_sel_target: Any) -> None:
#     """Move space ``space_sel`` (use None for current space) to position of space
#     ``space_sel_target`` (must be on same display)."""
#     try:
#         run_command(f"yabai -m space {space_sel} --move {space_sel_target}")
#     except ValueError as e:
#         if "cannot move space to itself" not in e.args[0]:
#             raise e
#
#
# @verify_space_sel
# def swap_with_other(space_sel: Any, space_sel_target: Any) -> None:
#     """Swap space ``space_sel`` (use None for current space) with space
#     ``space_sel_target`` (must be on the same display)."""
#     try:
#         run_command(f"yabai -m space {space_sel} --swap {space_sel_target}")
#     except ValueError as e:
#         if "cannot swap space with itself" not in e.args[0]:
#             raise e
#
#
# @verify_space_sel
# def send_to_display(space_sel: Any, display_sel: Any) -> None:
#     """Send space ``space_sel`` (use None for current space) to display ``display_sel``."""
#     try:
#         run_command(f"yabai -m space {space_sel} --display {display_sel}")
#     except ValueError as e:
#         if "already located on the given display" not in e.args[0]:
#             raise e
#
#
# @verify_space_sel
# def balance(space_sel: Any, axis: str = "xy") -> None:
#     """Adjust split ratios on space ``space_sel`` (use None for current space) so that
#     windows along given axis occupy same space. Parameter ``axis``: {'x', 'y', 'xy'}."""
#     if "x" in axis and "y" in axis:
#         arg = ""
#     elif "x" in axis:
#         arg = "x-axis"
#     elif "y" in axis:
#         arg = "y-axis"
#     else:  # 'x' not in axis and 'y' not in axis:
#         raise ValueError("Parameter ``axis`` must contain 'x', 'y', or both.")
#     run_command(f"yabai -m space {space_sel} --balance {arg}")
#
#
# @verify_space_sel
# def mirror(space_sel: Any, axis: str = "x") -> None:
#     """Flip the windows on space ``space_sel`` (use None for current space) along given
#     axis. Parameter ``axis``: {'x', 'y'}."""
#     if axis == "x":
#         arg = "x-axis"
#     elif axis == "y":
#         arg = "y-axis"
#     else:  # 'x' not in axis and 'y' not in axis:
#         raise ValueError("Parameter ``axis`` must be 'x' or 'y'.")
#     run_command(f"yabai -m space {space_sel} --mirror {arg}")
#
#
# @verify_space_sel
# def rotate(space_sel: Any, angle: int = 0) -> None:
#     """Rotate the windows on space ``space_sel`` (use None for current space) through
#     given angle in counterclockwise direction. Parameter ``angle``: {90, 180, 270}."""
#     if angle == 0 or angle == 360:
#         return
#     run_command(f"yabai -m space {space_sel} --rotate {angle}")
#
#
# @verify_space_sel
# def set_padding(space_sel: Any, relabs: str, t: int, b: int, l: int, r: int) -> None:
#     """Set padding around space ``space_sel`` (use None for current space). Parameter
#     ``relabs``: one of {'rel', 'abs'}. Parameters ``t``, ``b``, ``l``, ``r``: top,
#     bottom, left, right padding, respectively."""
#     run_command(f"yabai -m space {space_sel} --padding {relabs}:{t}:{b}:{l}:{r}")
#
#
# @verify_space_sel
# def gap(space_sel: Any, relabs: str, gap: int) -> None:
#     """Set gap between windows on space ``space_sel`` (use None for current space) to
#     ``gap``. Parameter ``relabs``: one of {'rel', 'abs'}."""
#     run_command(f"yabai -m space {space_sel} --gap {relabs}:{gap}")
#
#
# @verify_space_sel
# def toggle(space_sel: Any, what: str) -> None:
#     """Toggle setting on/off on space ``space_sel`` (use None for current space).
#     Parameter ``what``: one of {'padding', 'gap', 'mission-control', 'show-desktop'}."""
#     run_command(f"yabai -m space {space_sel} --toggle {what}")
#
#
# @verify_space_sel
# def set_layout(space_sel: Any, what: str) -> None:
#     """Set layout on space ``space_sel`` (use None for current space).
#     Parameter ``what``: one of {'bsp', 'stack', 'float'}."""
#     run_command(f"yabai -m space {space_sel} --layout {what}")
#
#
# @verify_space_sel
# def set_label(space_sel: Any, label: str) -> None:
#     """Set label of space ``space_sel`` (use None for current space)."""
#     assert_label_allowed(label)
#     run_command(f"yabai -m space {space_sel} --label {label}")

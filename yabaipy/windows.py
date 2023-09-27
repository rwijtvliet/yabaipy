"""Module to manipulate windows."""

from __future__ import annotations
from typing import Any, List, Dict
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from .shared import run_command
import json
from .displays import Display


# FORBIDDEN_LABELS = ["prev", "next", "first", "last", "recent", "mouse"]
#
#
# def assert_label_allowed(label: str) -> None:
#     """Raise ValueError if label is not allowed."""
#     label = label.strip().lower()
#     if not label:
#         raise ValueError("Label forbidden; cannot be the emptystring.")
#     if label in FORBIDDEN_LABELS:
#         raise ValueError(f"Label '{label}' forbidden; reserved keyword.")
#     if label.isdigit():
#         raise ValueError(f"Label '{label}' forbidden; cannot be number.")
#     if label in (dic["label"].lower() for dic in dictionaries()):
#         raise ValueError(f"Label '{label}' forbidden; already exists.")


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


def dictionary_from_uuid(uuid: str) -> Dict[str, Any]:
    for dic in dictionaries():
        if dic["uuid"] == uuid:
            return dic
    raise ValueError(f"Cannot find window with uuid {uuid}.")


def dictionaries() -> List[Dict[str, Any]]:
    return json.loads(run_command("yabai -m query --windows"))


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

    @classmethod
    def from_uuid(cls, uuid: str) -> Props:
        return cls.from_dict(dictionary_from_uuid(uuid))


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

    @classmethod
    def get_all(cls) -> List[Window]:
        """Create Space for all spaces."""
        return [cls(dic["index"]) for dic in dictionaries()]

    def __init__(self, window_sel: str = None):
        data = Props.from_window_sel(window_sel)
        self._label: str = data.label  # cache label
        self._uud: str = data.uuid  # for backup: cache uuid

    @property
    def window_sel(self) -> str:
        """Currently-correct (unique) window selector with minimal queries."""
        if self._uuid is None:
            raise ValueError("This space has been destroyed.")
        # Use label if possible (no queries needed)
        if (label := self._label) != "":
            return label
        # Otherwise, use uuid to find index (slower)
        return dictionary_from_uuid(self._uuid)["index"]

    def props(self) -> Props:
        """Query yabai API and return the current window properties."""
        return Props.from_space_sel(self.space_sel)


#
#     def focus(self) -> None:
#         """Focus space."""
#         try:
#             run_command(f"yabai -m space --focus {self.space_sel}")
#         except ValueError as e:
#             if "already focused space" not in e.args[0]:
#                 raise e
#
#     def create_here(self) -> Space:
#         """Create new space on same display as this space; returning the created space."""
#         display_sel = self.data().display
#         run_command(f"yabai -m space --create {self.space_sel}")
#         # new space is last one in this display; get mission-control index
#         new_space_sel = Display(display_sel).spaces[-1]
#         return Space(new_space_sel)
#
#     def destroy(self) -> None:
#         """Destroy space."""
#         run_command(f"yabai -m space --destroy {self.space_sel}")
#         self._uuid = None
#

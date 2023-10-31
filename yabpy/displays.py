"""Module to manipulate displays."""

# Specifying a space to yabai:
# - Use the uuid to find the arrangement index, and use that.

from __future__ import annotations
from typing import Any, List, Dict
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from .shared import run_bash
from . import spaces, windows
import json


def verify_display_selector(display_sel: str) -> Any:
    """Verify and adjust display selector to avoid inadvertently selecting incorrect display."""
    if display_sel == "":
        raise ValueError(
            "display selector cannot be the empty string (use None to select current display)."
        )
    if display_sel is None:
        display_sel = ""
    return display_sel


def dictionary_from_display_sel(display_sel: str) -> Dict[str, Any]:
    display_sel = verify_display_selector(display_sel)
    return json.loads(run_bash(f"yabai -m query --displays --display {display_sel}"))


def dictionary_from_uuid(uuid: str) -> Dict[str, Any]:
    for dic in dictionaries():
        if dic["uuid"] == uuid:
            return dic
    raise ValueError(f"Cannot find display with uuid {uuid}.")


def dictionaries() -> List[Dict[str, Any]]:
    return json.loads(run_bash("yabai -m query --displays"))


def get_all_displays() -> List[Display]:
    """Create Display for all displays."""
    return [Display(dic["index"]) for dic in dictionaries()]


@dataclass_json
@dataclass(frozen=True)
class Props:
    """Class to hold the properties of a display. The properties are queried and stored
    at the moment of creation, and not updated afterwards."""

    id_: int = field(metadata=config(field_name="id"))
    uuid: str
    index: int
    frame: Dict[str, float]
    spaces: List[int]

    @classmethod
    def from_display_sel(cls, display_sel: Any) -> Props:
        return cls.from_dict(dictionary_from_display_sel(display_sel))

    @classmethod
    def from_uuid(cls, uuid: str) -> Props:
        return cls.from_dict(dictionary_from_uuid(uuid))


class Display:
    """Class to manipulate displays. The properties are accessible via the `.props()`
    method. This information is fetched whenever called, so you may want to store it in
    a temporary variable (if the relevant properties do not change before they are)
    needed.

    Internally, the uuid is stored, so that the other methods of this class (which is
    only .focus()) can always be called, even if the arrangement index (or any other
    property) has changed. (This is done by using the uuid to find the display's index
    every time it's needed.

    Parameters
    ----------
    display_sel : str, optional (default: None)
        arrangement index | prev | next | first | last | recent | mouse | north | east
        | west | south
        Use None for current display.
    """

    def __init__(self, display_sel: str = None):
        props = Props.from_display_sel(display_sel)
        self._uuid: str = props.uuid  # cache uuid

    uuid: str = property(lambda self: self._uuid)

    @property
    def display_sel(self) -> str:
        """Currently-correct (unique) display selector with minimal queries."""
        return dictionary_from_uuid(self.uuid)["index"]

    # --- fetch properties

    def props(self) -> Props:
        """Query yabai API and return the current space properties."""
        return Props.from_uuid(self.uuid)

    # --- dunder

    def __repr__(self) -> str:
        return f"Display object with uuid '{self.uuid}'."

    def __eq__(self, other: Any) -> bool:
        return type(self) is type(other) and self.uuid == other.uuid

    # --- from yabai API

    def focus(self) -> None:
        """Focus display."""
        run_bash(f"yabai -m display --focus {self.display_sel}")

    # --- own additions

    def create_here(self) -> spaces.Space:
        """Create new space on display; returning the created space."""
        run_bash(f"yabai -m space --create {self.display_sel}")
        # new space is last one in this display; get mission-control index
        new_space_sel = self.props().spaces[-1]
        return spaces.Space(new_space_sel)

    def get_spaces(self) -> List[spaces.Space]:
        """Spaces on the display."""
        space_idxs = self.props().spaces
        return [spaces.Space(space_idx) for space_idx in space_idxs]

    def get_windows(self) -> List[windows.Window]:
        """Windows of the display."""
        display_idx = self.props().index
        wis = windows.get_all_windows()
        return [wi for wi in wis if wi.props().display == display_idx]

    def sort(self) -> None:
        """Sort spaces on display in order of their labels."""
        current = self.get_spaces()
        sorted = spaces.sort_spaces(current)
        # Apply order.
        space_idx = self.props().spaces[0]
        moved_any = False
        for sp, sp_current in zip(sorted, current):
            if moved_any or sp != sp_current:
                print(
                    f'Putting space "{sp.label}" at mission control index {space_idx}'
                )
                sp.move_to(space_idx)
                moved_any = True
            space_idx += 1

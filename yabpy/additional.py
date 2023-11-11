"""Additional functionality."""

from typing import List, Dict
from .shared import run_osascript
from .spaces import Space, get_all_spaces
from .displays import Display, get_all_displays
from .spacedef import SpaceDef, get_all_spacedefs
from enum import Enum

KEYCODES_OF_NUMBERKEYS = {
    "1": 18,
    "2": 19,
    "3": 20,
    "4": 21,
    "5": 23,
    "6": 22,
    "7": 26,
    "8": 28,
    "9": 25,
}


class SpaceProp(str, Enum):
    label = "label"
    index = "index"
    space_sel = "space_sel"  # e.g. 'prev, next, ...'
    display = "display"
    icon = "icon"
    abbr = "abbr"
    key = "key"
    color = "color"  # as "#rrbbgg"
    name = "name"


def focus_space_using_keypress(sp: Space) -> None:
    """Instead of calling `yabai -m ...`, switch to the correct space using the
    shortcut keys ctrl+1 ... ctrl+9. Only works if shortcuts for space switching are
    enabled."""
    # Find index of space.
    index = property_of_space(sp, SpaceProp.index)
    # Find the keycode this number corresponds to.
    keycode = KEYCODES_OF_NUMBERKEYS[str(index)]
    # Press that key.
    run_osascript(
        f'tell application "System Events" to key code {keycode} using {{control down}}'
    )


def create_spaces() -> None:
    """Create spaces; ensuring that all wanted labels (and no excess labels) exist."""
    sps: List[Space] = get_all_spaces()  # found
    sds: Dict[str, SpaceDef] = get_all_spacedefs()  # wanted

    # Create the spaces.

    # Find spaces that already correspond to a wanted spacedef.
    labels_found = [sp.label for sp in sps if sp.label in sds]
    # . spaces that are found but not wanted
    sps_excess = [sp for sp in sps if sp.label not in labels_found]
    print(f". Found but not wanted: {[sp.label for sp in sps_excess]}")
    # . spaces that are wanted but not found
    sds_excess = {label: sd for label, sd in sds.items() if label not in labels_found}
    print(f". Wanted but not found: {sds_excess.keys()}")

    # Rename excess spaces to other wanted spacedef.
    incommon = min(len(sps_excess), len(sds_excess))
    for _ in range(incommon):
        sp = sps_excess.pop()
        label, sd = sds_excess.popitem()
        print(f".. Renaming space to {label}")
        sp.set_label(label)

    # Now, we either have excess spaces left, which must get deleted...
    for sp in sps_excess:
        print(f".. Destroying excess space with label {sp.label}.")
        sp.destroy()

    # ...or we have spacedefs left, for which a space must be created. (or, neither)
    di = Display(1)
    for label, sd in sds_excess.items():
        print(f".. Creating missing space, with label {label}")
        di.create_here().set_label(label)


def send_spaces_to_displays() -> None:
    """Send all spaces to their preferred display (if possible)."""
    sds = get_all_spacedefs()
    # cache all spaces, to avoid handling them twice:
    sps_per_display = {di.props().index: di.get_spaces() for di in get_all_displays()}

    # Loop through displays, and spaces on each display, and send space if necessary and possible.
    # NOTE: unhandled edge case: all spaces on first display must be moved.
    for di_index, sps in sps_per_display.items():
        for sp in sps:
            sd = sds.get(sp.label)
            if sd is None:  # space not corresponding to a space definition
                print(f". Space with unknown label {sp.label}; don't move.")
                continue
            if sd.display == di_index:  # space is already on correct display
                print(f". Space {sp.label} already on correct display; don't move.")
                continue
            if sd.display not in sps_per_display:  # correct display does not exist
                print(
                    f". For space {sp.label}, wanted display ({sd.display}) is unavailable; don't move."
                )
                continue
            print(f". Space {sp.label} is sent to display {sd.display}")
            sp.send_to_display(sd.display)


def sort_displays() -> None:
    """Sort spaces on all displays."""
    for di in get_all_displays():
        di.sort()


def space_from_propery(prop: SpaceProp, value: str) -> Space:
    """Get space from some identifying property."""
    if prop in [SpaceProp.label, SpaceProp.index, SpaceProp.space_sel]:
        return Space(value)
    elif prop in [SpaceProp.icon, SpaceProp.abbr, SpaceProp.key, SpaceProp.color]:
        attr = prop._value_
        for label, sd in get_all_spacedefs().items():
            if getattr(sd, attr) == value:
                return Space(label)
        raise ValueError(f"Couldn't find space definition where .{prop} equals {value}")
    elif prop == SpaceProp.display:
        sps = Display(value).props.spaces()
        if len(sps) == 1:
            return Space(sps[0])
        raise ValueError(
            "Can only identify space by its display, if display has exactly 1 space."
        )
    raise ValueError(
        f"Unexpected value for ``prop``. Expected one of {SpaceProp}; got {prop}."
    )


def property_of_space(sp: Space, prop: SpaceProp) -> str:
    """Return property of a space."""
    if prop == SpaceProp.label:
        return sp.label
    elif prop == SpaceProp.index:
        return sp.props().index
    elif prop == SpaceProp.display:
        return sp.props().display
    elif prop in [
        SpaceProp.icon,
        SpaceProp.abbr,
        SpaceProp.key,
        SpaceProp.color,
        SpaceProp.name,
    ]:
        sd = SpaceDef.from_space(sp)
        return getattr(sd, prop._value_)
    raise ValueError(
        f"Unexpected value for parameter ``prop``. Expected one of {SpaceProp}; got {prop}."
    )

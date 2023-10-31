"""Additional functionality."""

from typing import List, Dict
from .spaces import Space, get_all_spaces
from .displays import Display, get_all_displays
from .spacedef import SpaceDef, get_all_spacedefs


def create_spaces() -> None:
    """Create spaces; ensuring that all wanted labels (and no excess labels) exist."""
    sps: List[Space] = get_all_spaces()  # found
    sds: Dict[str, SpaceDef] = get_all_spacedefs()  # wanted

    # Create the spaces.

    # Find spaces that already correspond to a wanted spacedef.
    labels_found = [sp.label for sp in sps if sp.label in sds]
    # . spaces that are found but not wanted
    sps_excess = [sp for sp in sps if sp.label not in labels_found]
    # . spaces that are wanted but not found
    sds_excess = {label: sd for label, sd in sds.items() if label not in labels_found}

    # Rename excess spaces to other wanted spacedef.
    incommon = min(len(sps_excess), len(sds_excess))
    for _ in range(incommon):
        sp = sps_excess.pop()
        label, sd = sds_excess.popitem()
        sp.set_label(label)

    # Now, we either have excess spaces left, which must get deleted...
    for sp in sps_excess:
        sp.destroy()

    # ...or we have spacedefs left, for which a space must be created. (or, neither)
    di = Display(1)
    for label, sd in sds_excess.items():
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
                continue
            if sd.display == di_index:  # space is already on correct display
                continue
            if sd.display not in sps_per_display:  # correct display does not exist
                continue
            sp.send_to_display(sd.display)

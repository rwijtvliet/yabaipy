"""Additional functionality."""

from typing import Any
from .spaces import Space
from .displays import Display, get_all_displays


def send_space_to_display(space_sel: str, display_sel: str) -> None:
    """Send space ``space_sel`` to display ``display_sel`` while keeping the correct
    space order."""
    sp = Space(space_sel)
    di = Display(sp.props().display)  # original display
    # Check if target display exists.
    try:
        di2 = Display(display_sel)  # target display
    except ValueError as e:
        if "could not locate" in e.args[0]:
            return
        raise e
    # Check if move is needed.
    if di == di2:
        return
    # Check if move is passible.
    if len(di.props().spaces) == 1:
        raise ValueError("Cannot move this space; it's the last space on its display.")

    sp.send_to_display(di2.display_sel)
    sort_display(di2.display_sel)
    di2.focus()


def sort_display(display_sel: Any) -> None:
    """Sort spaces on display ``display_sel``."""
    # Get spaces in current order.
    di = Display(display_sel)
    sps_current = di.get_spaces()
    sps_sorted = sorted(sps_current, key=lambda sp: sp.label)
    # Apply order.
    space_idx = di.props().spaces[0]
    moved_any = False
    for sp, sp_current in zip(sps_sorted, sps_current):
        if moved_any or sp != sp_current:
            print(f'Putting space "{sp.label}" at mission control index {space_idx}')
            sp.move_to(space_idx)
            moved_any = True
        space_idx += 1


def sort_displays() -> None:
    """Sort spaces on all displays."""
    for di in get_all_displays():
        sort_display(di.display_sel)


def assert_display_sorted(display_sel) -> None:
    """Assert that the spaces on display `display_sel` are sorted."""
    di = Display(display_sel)
    sps = di.get_spaces()
    sps_in_order = sorted(sps, key=lambda sp: sp.label)
    for sp1, sp2 in zip(sps, sps_in_order):
        if sp1 != sp2:
            print(
                "Spaces not in order.\n"
                f"Found: {[sp.label for sp in sps]}\n"
                f"Expected: {[sp.label for sp in sps_in_order]}"
            )
            raise AssertionError("Not in order")


def assert_displays_sorted() -> None:
    """Assert that the spaces on all displays are sorted."""
    for di in get_all_displays():
        assert_display_sorted(di.display_sel)

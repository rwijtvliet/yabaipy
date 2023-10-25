"""Additional functionality."""

from .spaces import Space, sort_spaces
from .displays import Display, get_all_displays


def send_space_to_display(space_sel: str, display_sel: str) -> None:
    """Send space ``space_sel`` to display ``display_sel`` while keeping the correct
    space order."""
    sp = Space(space_sel)
    di = Display(sp.props().display)  # original display
    di2 = Display(display_sel)  # target display
    # Check if move is passible.
    if len(di.props().spaces) == 1:
        raise ValueError("Cannot move this space; it's the last space on its display.")
    # Do move.
    print("do move")
    sp.send_to_display(di2)
    di2.sort()
    di2.focus()


def sort_displays() -> None:
    """Sort spaces on all displays."""
    for di in get_all_displays():
        di.sort()


def assert_display_sorted(di: Display | str) -> None:
    """Assert that the spaces on display `display_sel` are sorted."""
    if not isinstance(di, Display):
        di = Display(di)
    current = di.get_spaces()
    sorted = sort_spaces(current)
    for sp1, sp2 in zip(current, sorted):
        if sp1 != sp2:
            raise AssertionError(
                f"Found: {[sp.label for sp in current]}\n"
                f"Expected: {[sp.label for sp in sorted]}"
            )


def assert_displays_sorted() -> None:
    """Assert that the spaces on all displays are sorted."""
    for di in get_all_displays():
        assert_display_sorted(di)

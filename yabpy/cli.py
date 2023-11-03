"""Functionality that is used in cli. Combines multiple functions."""

import typer
from .spaces import Space
from .windows import Window
from .displays import Display
from .shared import notify, run_bash
from .spacedef import fullname, get_all_spacedefs
from . import additional

app = typer.Typer()


def main():
    app()


@app.command("prepare-spaces")
def prepare_spaces() -> None:
    """Create/delete/move spaces, so that all desired spaces exist, on the display of choice, in the correct order."""
    # Do.
    additional.create_spaces()
    additional.send_spaces_to_displays()
    additional.sort_displays()
    # Notify.
    notify("Preparing spaces")


@app.command("focus-space")
def focus_space(space_sel: str) -> None:
    """Focus space ``space_sel`` and notify user."""
    # Collect.
    sp = Space(space_sel)
    # Do.
    sp.focus()
    # Notify.
    notify(fullname(sp, False), title="Focusing")


@app.command("window-to-space")
def window_to_space(space_sel: str) -> None:
    """Move current window to space ``space_sel`` and notify user."""
    # Collect.
    wi, sp = Window(), Space(space_sel)
    # Do.
    wi.send_to_space(sp)
    sp.focus()
    # Notify.
    notify(fullname(sp, False), title="Moving window to")
    run_bash("sketchybar --trigger windows_on_spaces")


@app.command("space-to-display")
def space_to_display(display_sel: str) -> None:
    """Send current space to display ``display_sel``, while keeping the correct order,
    and then focus the space."""
    sp = Space()
    di = Display(display_sel)  # target display
    # Check.
    if len(sp.get_display().props().spaces) == 1:
        raise ValueError("Cannot move this space; it's the last space on its display.")
    # Do.
    sp.send_to_display(di)
    di.sort()
    di.focus()
    # Notify.
    notify(f"{fullname(sp, False)} to display {di.props().index}", title="Moving space")


@app.command("spaces-to-displays")
def spaces_to_displays() -> None:
    """Send all spaces to their preferred displays (if possible) and ensure correct space order."""
    # Do.
    additional.send_spaces_to_displays()
    additional.sort_displays()
    # Notify.
    notify("All spaces to their preferred displays", title="Moving spaces")


@app.command("sort-display")
def sort_display() -> None:
    """Sort spaces on current display."""
    # Do.
    Display().sort()
    # Notify.
    notify("Current display", title="Sorting spaces")


@app.command("sort-displays")
def sort_displays() -> None:
    """Sort spaces on all displays."""
    # Do.
    additional.sort_displays()
    # Notify.
    notify("All displays", title="Sorting spaces")


# @app.command("get-spacedefs")
# def get_spacedefs() -> None:
#     """Return all space definitions."""
#     print(get_all_spacedefs())
#


@app.command("space-prop")
def space_prop(
    prop_in: additional.SpaceProp, value: str, prop_out: additional.SpaceProp
) -> None:
    """Obtain property of a space, by specifying another property of it. The 'in-going'
    information must be unique to the space."""
    sp = additional.space_from_propery(prop_in, value)
    prop = additional.property_of_space(sp, prop_out)
    print(prop)

"""Functionality that is used in cli. Combines multiple functions."""

import typer
import functools
from typing import Optional
from typing_extensions import Annotated
from .spaces import Space
from .windows import Window
from .displays import Display
from .shared import notify, run_bash
from .spacedef import fullname
from . import additional

app = typer.Typer()
state = {}


@app.callback()
def globl(
    verbose: Annotated[
        Optional[bool],
        typer.Option("--verbose", "-v", help="Flag to increase output on command line"),
    ] = False,
    notify: Annotated[
        Optional[bool],
        typer.Option("--notify", "-n", help="Flag to inform user with notification"),
    ] = False,
):
    """Interact with yabpy through command line.

    Yabpy is a wrapper around yabai, written in python, which aims to make common tasks
    easier. This includes sorting the spaces on a display; moving spaces to another
    display while maintaining this order; and querying information about a space to
    obtain a property."""
    state["verbose"] = verbose
    state["notify"] = notify


def main():
    app()


def maybe_print(msg: str):
    if state["verbose"]:
        print(msg)


@functools.wraps(notify)
def maybe_notify(*args, **kwargs):
    if state["notify"]:
        notify(*args, **kwargs)


@app.command("prepare-spaces")
def prepare_spaces() -> int:
    """Create/delete/move spaces, so that all desired spaces exist, on the display of
    choice, in the order of their labels."""
    # Do.
    maybe_print("Creating spaces")
    additional.create_spaces()
    maybe_print("Sending spaces to displays")
    additional.send_spaces_to_displays()
    maybe_print("Sorting displays")
    additional.sort_displays()
    # Notify.
    maybe_notify("Preparing spaces", title="Yabpy")
    # Success.
    return 0


@app.command("focus-space")
def focus_space(space_sel: str) -> int:
    """Focus space ``space_sel`` and notify user."""
    # Collect.
    sp = Space(space_sel)
    # Do.
    maybe_print(f"Focusing space {space_sel}")
    sp.focus()
    # Notify.
    maybe_notify(fullname(sp, False), title="Focusing")
    # Success.
    return 0


@app.command("window-to-space")
def window_to_space(space_sel: str) -> int:
    """Move current window to space ``space_sel`` and notify user."""
    # Collect.
    wi, sp = Window(), Space(space_sel)
    # Do.
    maybe_print(f"Moving current window to space {space_sel}")
    wi.send_to_space(sp)
    sp.focus()
    # Notify.
    maybe_notify(fullname(sp, False), title="Moving window to")
    # Trigger sketchybar.
    run_bash("sketchybar --trigger windows_on_spaces")
    # Success.
    return 0


@app.command("space-to-display")
def space_to_display(display_sel: str) -> int:
    """Send current space to display ``display_sel``, while keeping them in order
    (according to their label), and then focus the space."""
    sp = Space()
    di = Display(display_sel)  # target display
    # Check.
    if len(sp.get_display().props().spaces) == 1:
        maybe_print("Cannot move this space; it's the last space on its display.")
        return 1
    # Do.
    maybe_print(f"Sending current space to display {display_sel}")
    sp.send_to_display(di)
    maybe_print("Sorting display")
    di.sort()
    maybe_print("Focussing display")
    di.focus()
    # Notify.
    maybe_notify(
        f"{fullname(sp, False)} to display {di.props().index}", title="Moving space"
    )
    # Success.
    return 0


@app.command("spaces-to-displays")
def spaces_to_displays() -> int:
    """Send all spaces to their preferred displays (if possible) and order the spaces
    (according to their label)."""
    # Do.
    maybe_print("Sending spaces to displays")
    additional.send_spaces_to_displays()
    maybe_print("Sorting displays")
    additional.sort_displays()
    # Notify.
    maybe_notify("All spaces to their preferred displays", title="Moving spaces")
    # Success.
    return 0


@app.command("sort-display")
def sort_display() -> int:
    """Sort spaces on current display (according to their label)."""
    # Do.
    maybe_print("Sorting current display")
    Display().sort()
    # Notify.
    maybe_notify("Current display", title="Sorting spaces")
    # Success.
    return 0


@app.command("sort-displays")
def sort_displays() -> int:
    """Sort spaces on all displays (accoring to their label)."""
    # Do.
    maybe_print("Sorting displays")
    additional.sort_displays()
    # Notify.
    maybe_notify("All displays", title="Sorting spaces")
    # Success.
    return 0


# @app.command("get-spacedefs")
# def get_spacedefs() -> int:
#     """Return all space definitions."""
#     print(get_all_spacedefs())
#


@app.command("space-prop")
def space_prop(
    prop_in: additional.SpaceProp, value: str, prop_out: additional.SpaceProp
) -> int:
    """Obtain property of a space, by specifying another property of it. The 'in-going'
    information must be unique to the space."""
    try:
        sp = additional.space_from_propery(prop_in, value)
    except Exception:
        maybe_print(
            f"Could not find (exactly 1) space with value '{value}' for property '{prop_in}'."
        )
        print(value)
        return 1

    try:
        prop = additional.property_of_space(sp, prop_out)
    except Exception:
        maybe_print(
            f"Could not get property {prop_out} for the selected space (with label '{sp.label}')."
        )
        print(sp.label)  # fallback value
        return 1

    print(prop)
    return 0

"""Functionality that is used in cli. Combines multiple functions."""

import typer
import functools
import os
import sys
from typing import Optional, Tuple, Callable
from typing_extensions import Annotated
from .spaces import Space
from .windows import Window
from .displays import Display
from .shared import notify
from .spacedef import fullname
from . import additional


# Custom Types

CliResult = Tuple[int, str]
SpaceSel = Annotated[
    str,
    typer.Argument(
        help=(
            "Something to identify the space with. Allowed values: LABEL | "
            "mission-control index | prev | next | first | last | recent | mouse. "
            "In addition, the shortcut key may be used, when the --key option is set."
        )
    ),
]
DisplaySel = Annotated[
    str,
    typer.Argument(
        help=(
            "Something to identify the display with. Allowed values: arrangement index | "
            "prev | next | first | last | recent | mouse | north | east | west | south."
        )
    ),
]
Key = Annotated[
    Optional[bool],
    typer.Option(
        "--key",
        "-k",
        help=(
            "Indicates that the space_sel is a shortcut key. To avoid collision, "
            "e.g. with the index of the space."
        ),
    ),
]
Presses = Annotated[
    Optional[bool],
    typer.Option(
        "--presses",
        "-p",
        help=(
            "Perform action using keypresses instead of yabai. Use when yabai (or "
            "its scripting additions) does not work on the current macos version. "
            "This is a less optimal solution; only use if necessary."
            "Switching to spaces using control+number must be enabled."
        ),
    ),
]


# General functions


@functools.wraps(notify)
def maybe_notify(*args, **kwargs):
    if state["notify"]:
        notify(*args, **kwargs)


class PrintIfVerbose:
    def __enter__(self):
        if state["verbose"]:
            self._original_stdout = None
        else:
            self._original_stdout = sys.stdout
            sys.stdout = open(os.devnull, "w")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._original_stdout is not None:
            sys.stdout.close()
            sys.stdout = self._original_stdout


def handle_verboseness_and_cliresult(fn: Callable[[...], CliResult]):
    """Suppress all print statements unless verbose wanted. Print message and return ok
    or nok value."""

    @functools.wraps(fn)
    def wrapped(*args, **kwargs) -> int:
        with PrintIfVerbose():
            nok, msg = fn(*args, **kwargs)
        print(msg)
        return nok

    return wrapped


# Run app


app = typer.Typer()
state = {}


def main():
    app()


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


@app.command("create-spaces")
@handle_verboseness_and_cliresult
def create_spaces() -> CliResult:
    """Create/delete spaces, so that all desired spaces exist, in the order of their
    labels. To also move the spaces to their preferred display, use ``prepare-spaces``
    instead."""
    # Do.
    print("Creating spaces")
    additional.create_spaces()
    print("Sorting displays")
    additional.sort_displays()
    # Notify.
    maybe_notify("Creating spaces", title="Yabpy")
    # Success.
    return 0, "Spaces have been created"


@app.command("prepare-spaces")
@handle_verboseness_and_cliresult
def prepare_spaces() -> CliResult:
    """Create/delete/move spaces, so that all desired spaces exist, on the display of
    choice, in the order of their labels."""
    # Do.
    print("Creating spaces")
    additional.create_spaces()
    print("Sending spaces to displays")
    additional.send_spaces_to_displays()
    print("Sorting displays")
    additional.sort_displays()
    # Notify.
    maybe_notify("Preparing spaces", title="Yabpy")
    # Success.
    return 0, "Spaces have been prepared"


@app.command("focus-space")
@handle_verboseness_and_cliresult
def focus_space(
    space_sel: SpaceSel, key: Key = False, presses: Presses = False
) -> CliResult:
    """Focus a space."""
    # Collect.
    if not key:
        print(f"Selecting space directly using {space_sel=}.")
        sp = Space(space_sel)
    else:
        print(f"Selecting space from shortcut key {space_sel}.")
        sp = additional.space_from_propery(additional.SpaceProp.key, space_sel)
    # Do.
    if not presses:
        print("Focusing space with yabai.")
        sp.focus()
    else:
        print("Focusing space with by pressing control+number.")
        additional.focus_space_using_keypress(sp)
    # Notify.
    maybe_notify(fullname(sp, False), title="Focusing")
    # Success.
    return 0, "Space has been focused"


@app.command("window-to-space")
@handle_verboseness_and_cliresult
def window_to_space(
    space_sel: SpaceSel, key: Key = False, presses: Presses = False
) -> CliResult:
    """Move current window to another space."""
    # Collect.
    wi = Window()
    if not key:
        print(f"Selecting space directly using {space_sel=}.")
        sp = Space(space_sel)
    else:
        print(f"Selecting space from shortcut key {space_sel}.")
        sp = additional.space_from_propery(additional.SpaceProp.key, space_sel)
    # Do.
    if not presses:
        print("Moving window with yabai.")
        wi.send_to_space(sp)
        sp.focus()
    else:
        return (
            1,
            "Cannot send window to space using keypresses; mac does not have a shortcut key for it.",
        )
    # Notify.
    maybe_notify(fullname(sp, False), title="Moving window to")
    # Success.
    return 0, "Window has been moved to space"


@app.command("space-to-display")
@handle_verboseness_and_cliresult
def space_to_display(display_sel: DisplaySel) -> CliResult:
    """Send current space to display ``display_sel``, while keeping them in order
    (according to their label), and then focus the space."""
    sp = Space()
    di = Display(display_sel)  # target display
    # Check.
    if len(sp.get_display().props().spaces) == 1:
        return 1, "Cannot move this space; it's the last space on its display."
    # Do.
    print(f"Sending current space to display {display_sel}")
    sp.send_to_display(di)
    print("Sorting display")
    di.sort()
    print("Focussing display")
    di.focus()
    # Notify.
    maybe_notify(
        f"{fullname(sp, False)} to display {di.props().index}", title="Moving space"
    )
    # Success.
    return 0, "Space has been moved to display"


@app.command("spaces-to-displays")
@handle_verboseness_and_cliresult
def spaces_to_displays() -> CliResult:
    """Send all spaces to their preferred displays (if possible) and order the spaces
    (according to their label)."""
    # Do.
    print("Sending spaces to displays")
    additional.send_spaces_to_displays()
    print("Sorting displays")
    additional.sort_displays()
    # Notify.
    maybe_notify("All spaces to their preferred displays", title="Moving spaces")
    # Success.
    return 0, "All spaces have been mowved to displays"


@app.command("sort-display")
@handle_verboseness_and_cliresult
def sort_display() -> CliResult:
    """Sort spaces on current display (according to their label)."""
    # Do.
    print("Sorting current display")
    Display().sort()
    # Notify.
    maybe_notify("Current display", title="Sorting spaces")
    # Success.
    return 0, "Current display has been sorted"


@app.command("sort-displays")
@handle_verboseness_and_cliresult
def sort_displays() -> CliResult:
    """Sort spaces on all displays (accoring to their label)."""
    # Do.
    print("Sorting displays")
    additional.sort_displays()
    # Notify.
    maybe_notify("All displays", title="Sorting spaces")
    # Success.
    return 0, "Displays have been sorted"


@app.command("space-prop")
@handle_verboseness_and_cliresult
def space_prop(
    prop_in: additional.SpaceProp, value: str, prop_out: additional.SpaceProp
) -> CliResult:
    """Obtain property of a space, by specifying another property of it. The 'in-going'
    information must be unique to the space."""
    try:
        sp = additional.space_from_propery(prop_in, value)
    except Exception:
        print(
            f"Could not find (exactly 1) space with value '{value}' for property '{prop_in}'."
        )
        return 1, value

    try:
        prop = additional.property_of_space(sp, prop_out)
    except Exception:
        print(
            f"Could not get property {prop_out} for the selected space (with label '{sp.label}')."
        )
        return 1, sp.label  # fallback value

    return 0, prop

from __future__ import annotations
from typing import Any, List, Any
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from .shared import run_command, none_not_allowed, none_means_current, assert_not_none
import json
from . import displays


def get_all() -> List[Space]:
    """Get info on all spaces."""
    spaces = json.loads(run_command("yabai -m query --spaces"))
    return [Space.from_dict(space) for space in spaces]


@none_means_current
def get(space_sel: Any) -> Space:
    """Get info on space ``space_sel`` (use None for current space)."""
    if space_sel is None:
        space_sel = ""
    space = json.loads(run_command(f"yabai -m query --spaces --space {space_sel}"))
    return Space.from_dict(space)


@dataclass_json
@dataclass
class Space:
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

    def update(self) -> Space:
        """Update, i.e., find space again after e.g. moving (but not renaming)."""
        return get(self.label)

    focus: Space = lambda self: focus(self.label)

    create_here: Space = lambda self: create(self.label)

    destroy: None = lambda self: destroy(self.label)

    move_to: Space = lambda self, space_sel_target: move(self.label, space_sel_target)

    swap_with: Space = lambda self, space_sel_target: swap(self.label, space_sel_target)

    send_to_display: Space = lambda self, display_sel: display(self.label, display_sel)

    balance: Space = lambda self, which: balance(self.label, which)

    mirror: Space = lambda self, which: mirror(self.label, which)


def focus(space_sel: Any) -> Space:
    """Focus space ``space_sel``.
    Returns the focused space."""
    try:
        run_command(f"yabai -m space --focus {space_sel}")
    except ValueError as e:
        if "already focused space" not in e.args[0]:
            raise e
    return get(space_sel)


@none_means_current
def create(space_sel: Any) -> Space:
    """Create space on same display as ``space_sel`` (use None for current space).
    Returns the created space."""
    if space_sel is None:
        space_sel = ""
    run_command(f"yabai -m space --create {space_sel}")
    # new space is last one in this display
    display_sel = get(space_sel).display
    new_space_sel = displays.get(display_sel).spaces[-1]
    return get(new_space_sel)


@none_means_current
def destroy(space_sel: Any) -> None:
    """Destroy space ``space_sel`` (use None for current space).
    Returns None."""
    if space_sel is None:
        space_sel = ""
    run_command(f"yabai -m space --destroy {space_sel}")
    return None


@none_means_current
def move(space_sel: Any, space_sel_target: Any) -> Space:
    """Move space ``space_sel`` (use None for current space) to position of space ``space_sel_target``.
    (must be on same display).
    Returns the moved space."""
    if space_sel is None:
        space_sel = ""
    # we need space now in case `space_sel` is property that changes after move
    space = get(space_sel)
    try:
        run_command(f"yabai -m space {space_sel} --move {space_sel_target}")
    except ValueError as e:
        if "cannot move space to itself" not in e.args[0]:
            raise e
    return space.update()


@none_means_current
def swap(space_sel: Any, space_sel_target: Any) -> Space:
    """Swap space ``space_sel`` (use None for current space) with space ``space_sel_target``.
    Returns the moved space."""
    if space_sel is None:
        space_sel = ""
    # we need space now in case `space_sel` is property that changes after move
    space = get(space_sel)
    try:
        run_command(f"yabai -m space {space_sel} --swap {space_sel_target}")
    except ValueError as e:
        if "cannot swap space to itself" not in e.args[0]:
            raise e
    return space.update()


def display(space_sel: Any, display_sel: Any) -> Space:
    """Send space ``space_sel`` (use None for current space) to display ``display_sel``.
    Returns the moved space."""
    if space_sel is None:
        space_sel = ""
    # we need space now in case `space_sel` is property that changes after move
    space = get(space_sel)
    try:
        run_command(f"yabai -m space {space_sel} --display {display_sel}")
    except ValueError as e:
        if "already located on the given display" not in e.args[0]:
            raise e
    return space.update()


def balance(space_sel: Any, which: str = "xy") -> Space:
    """Adjust split ratios on space ``space_sel`` (use None for current space) so that
    windows along given axis occupy same space. Parameter ``which``: on of {'x', 'y', 'xy'}.
    Returns the adjusted space."""
    if space_sel is None:
        space_sel = ""
    elif "x" in which and "y" in which:
        arg = ""
    elif "x" in which:
        arg = "x-axis"
    elif "y" in which:
        arg = "y-axis"
    else:  # 'x' not in which and 'y' not in which:
        raise ValueError("Parameter ``which`` must contain 'x', 'y', or both.")
    run_command(f"yabai -m space {space_sel} --balance {arg}")
    return get(space_sel)


def mirror(space_sel: Any, which: str = "x") -> Space:
    """Flip the windows on space ``space_sel`` (use None for current space) along given
    axis. Parameter ``which``: one of {'x', 'y'}.
    Returns the adjusted space."""
    if space_sel is None:
        space_sel = ""
    if which == "x":
        arg = "x-axis"
    elif which == "y":
        arg = "y-axis"
    else:  # 'x' not in which and 'y' not in which:
        raise ValueError("Parameter ``which`` must be 'x' or 'y'.")
    run_command(f"yabai -m space {space_sel} --mirror {arg}")
    return get(space_sel)


def rotate(space_sel: Any, angle: int = 0) -> Space:
    """Rotate the windows on space ``space_sel`` (use None for current space) through
    given angle in counterclockwise direction. Parameter ``angle``: one of {90, 180, 270}.
    Returns the adjusted space."""
    if space_sel is None:
        space_sel = ""
    if angle == 0 or angle == 360:
        return get(space_sel)
    run_command(f"yabai -m space {space_sel} --rotate {angle}")
    return get(space_sel)

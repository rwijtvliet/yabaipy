# Assumptions:
# * All spaces on each display are in correct order.

from dataclasses import dataclass
from typing import List, Any
from . import spaces, windows, displays


@dataclass
class SpaceDef:
    label: str
    icon: str
    text: str


SPACES_DEFS = [
    SpaceDef("1_files", "", "1"),  # 1
    SpaceDef("2_www", "", "2"),  # 2
    SpaceDef("3_office", "", "3"),  # 3
    SpaceDef("4_terminal", "", "4"),  # 4
    SpaceDef("5_vscode", "󰨞", "5"),  # 5
    SpaceDef("6_", " ", "6"),  # 6
    SpaceDef("7_teams", "󰊻", "7"),  # 7
    SpaceDef("8_email", "󰇰", "8"),  # 8
    SpaceDef("9_media", "󰎈", "9"),  # 9
]


def _orderpos(label: str) -> int:
    """Return the position of the label in the predefined/wanted space order.
    (Return -1 if label not found.)"""
    for i, space_def in enumerate(SPACES_DEFS):
        if space_def.label == label:
            return i
    return -1


def _space_labels_on_display(display_sel: Any) -> List[str]:
    space_idxs = displays.get(display_sel).spaces
    return [spaces.get(space_idx).label for space_idx in space_idxs]


def move_correct_order(display_sel: Any) -> None:
    """Move current space to display ``display_sel`` and move to correct position
    (to keep correct order)."""
    target_display = displays.get(display_sel)
    current_display = displays.get()
    if target_display == current_display:
        return  # don't need to move; end
    # Move to display (space keeps focus).
    spaces.move(display_sel)
    # Move to correct position.
    this = _orderpos(spaces.get().label)
    # . Move to top.
    if this > -1:  # only move to top if labeled
        while True:
            try:
                prev = _orderpos(spaces.get("prev").label)
            except ValueError as e:
                if "could not locate" in e.args[0]:
                    break  # already at top
                raise e
            if prev > -1 and this > prev:
                break
            spaces.swap("prev")
    # . Move to bottom.
    while True:
        try:
            next = _orderpos(spaces.get("next").label)
        except ValueError as e:
            if "could not locate" in e.args[0]:
                break  # already at bottom
            raise e
        if this < next:
            break
        spaces.swap("next")


def sort_spaces_on_display(display_sel: Any) -> None:
    """Sort spaces on display ``display_sel``."""
    # Get labels in current order.
    space_idxs = displays.get(display_sel).spaces
    space_labels = [spaces.get(space_idx).label for space_idx in space_idxs]
    # Find wanted order.
    space_order = []
    for space_def in SPACES_DEFS:
        label_tosearch = space_def.label
        for label in space_labels:
            if label == label_tosearch:
                space_order.append(label)
                continue
    # Apply order.
    move_to_idx = space_idxs[0]
    for space_label in space_order:
        print(f'moving space "{space_label}" to position {move_to_idx}')
        spaces.focus(space_label)
        spaces.move(move_to_idx)
        move_to_idx += 1


def sort_spaces_on_displays() -> None:
    """Sort spaces on all displays."""
    for display in displays.get_all():
        sort_spaces_on_display(display.index)


# Set-up spaces as wanted.

# Ensure each space exists (checking the label).

# Per monitor, put spaces in correct order.

# If >1 display, move space 7,8,9 to secondary monitor.

# Delete any surplus spaces.

# Set correct background color


# Add rules to ensure spaces remain in correct order.
# TODO: when moving space to other display.
# TODO: when a display is added/removed.

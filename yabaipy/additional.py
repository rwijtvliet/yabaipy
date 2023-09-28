"""Additional functionality."""

from typing import Any, Iterable
from .spaces import Space
from .displays import Display


labelorder: Iterable[str] = []


def set_labelorder(order: Iterable[str]) -> None:
    global labelorder
    labelorder = order


def send_to_display_keep_order(space_sel: str, display_sel: str) -> None:
    """Send space ``space_sel`` to display ``display_sel`` while keeping the correct
    space order."""
    sp = Space(space_sel)
    di = Display(sp.props().display)
    di2 = Display(display_sel)
    # Check if move is needed.
    if di == di2:
        return
    # Check if other dummy space must be created (to prevent display without spaces).
    dummy_needed = len(di.props().spaces) == 1
    # Find correct insertion point.
    orderpos = _orderpos(sp.label)
    for space_sel_2 in Display(display_sel).props().spaces:
        sp2 = Space(space_sel_2)
        orderpos_2 = _orderpos(sp2.label)
        if -1 < orderpos < orderpos_2 or orderpos_2 == -1:  # Insert space here.
            if dummy_needed:
                sp_dummy = sp.create_here()  # add dummy if needed
            sp.send_to_display(di2.display_sel)
            sp.move_to(sp2.space_sel)  # do move
            if dummy_needed:
                # send last space back to original display if necessary.
                Space(di2.props().spaces[-1]).send_to_display(di.display_sel)
                sp_dummy.destroy()  # destroy dummy
            return
    # Insert space at end.
    if dummy_needed:
        sp_dummy = sp.create_here()  # add dummy if needed
    sp.send_to_display(di2.display_sel)
    if dummy_needed:
        # send last space back to original display if necessary.
        Space(di2.props().spaces[-2]).send_to_display(di.display_sel)
        sp_dummy.destroy()  # destroy dummy


def _orderpos(label: str) -> int:
    """Return the position of the label in the predefined/wanted space order.
    (Return -1 if label not found.)"""
    for i, label_avail in enumerate(labelorder):
        if label_avail == label:
            return i
    return -1


# def move_correct_order(display_sel: Any) -> None:
#     """Move current space to display ``display_sel`` and move to correct position
#     (to keep correct order)."""
#     target_display = displays.get(display_sel)
#     current_display = displays.get()
#     if target_display == current_display:
#         return  # don't need to move; end
#     # Move to display (space keeps focus).
#     spaces.move(display_sel)
#     # Move to correct position.
#     this = _orderpos(spaces.get().label)
#     # . Move to top.
#     if this > -1:  # only move to top if labeled
#         while True:
#             try:
#                 prev = _orderpos(spaces.get("prev").label)
#             except ValueError as e:
#                 if "could not locate" in e.args[0]:
#                     break  # already at top
#                 raise e
#             if prev > -1 and this > prev:
#                 break
#             spaces.swap("prev")
#     # . Move to bottom.
#     while True:
#         try:
#             next = _orderpos(spaces.get("next").label)
#         except ValueError as e:
#             if "could not locate" in e.args[0]:
#                 break  # already at bottom
#             raise e
#         if this < next:
#             break
#         spaces.swap("next")


def sort_spaces_on_display(display_sel: Any) -> None:
    """Sort spaces on display ``display_sel``."""
    # Get spaces.
    space_idxs = Display(display_sel).spaces
    sps = [Space(space_sel) for space_sel in space_idxs]
    # Find wanted order.
    sps_in_order = []
    for label_sought in labelorder:
        for sp in sps:
            if sp.label == label_sought:
                sps_in_order.append(sp)
                continue
    # Apply order.
    move_to_idx = space_idxs[0]
    for sp in sps_in_order:
        print(f'moving space "{sp.label}" to position {move_to_idx}')
        sp.move_to_other(move_to_idx)
        move_to_idx += 1


def sort_spaces_on_displays() -> None:
    """Sort spaces on all displays."""
    for display in Display.get_all():
        sort_spaces_on_display(display.index)

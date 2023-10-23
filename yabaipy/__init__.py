"""Package to interact with yabai window manager."""

from .windows import Window, get_all_windows
from .spaces import Space, get_all_spaces
from .displays import Display, get_all_displays
from . import windows, spaces, displays
from .additional import (
    send_space_to_display,
    sort_display,
    sort_displays,
    assert_display_sorted,
    assert_displays_sorted,
)

"""Package to interact with yabai window manager."""

from .windows import Window, get_all_windows
from .spaces import Space, get_all_spaces
from .displays import Display, get_all_displays
from . import windows, spaces, displays
from .additional import (
    set_labelorder,
    send_to_display_keep_order,
    sort_spaces_on_display,
    sort_spaces_on_displays,
)

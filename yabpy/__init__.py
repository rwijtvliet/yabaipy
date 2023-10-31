"""Package to interact with yabai window manager."""

from .windows import Window, get_all_windows
from .spaces import Space, get_all_spaces
from .displays import Display, get_all_displays
from . import windows, spaces, displays
from .additional import *

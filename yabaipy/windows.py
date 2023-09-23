from __future__ import annotations
from .shared import run_command, none_means_current
from typing import Any, Callable, List, Dict, Optional
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
import json


def get_all() -> List[Window]:
    """Get info on all windows."""
    windows = json.loads(run_command("yabai -m query --windows"))
    return [Window.from_dict(window) for window in windows]


@none_means_current
def get(window_sel: Optional[Any] = None) -> Window:
    """Get info on window ``window_sel`` (if none provided: current window)."""
    window = json.loads(run_command(f"yabai -m query --windows --window {window_sel}"))
    return Window.from_dict(window)


@dataclass_json
@dataclass
class Window:
    id_: int = field(metadata=config(field_name="id"))
    pid: int
    app: str
    title: str
    frame: Dict[str, float]
    role: str
    subrole: str
    display: int
    space: int
    level: int
    opacity: float
    split_type: Optional[str] = field(metadata=config(field_name="split-type"))
    split_child: Optional[str] = field(metadata=config(field_name="split-child"))
    stack_index: Optional[str] = field(metadata=config(field_name="stack-index"))
    can_move: bool = field(metadata=config(field_name="can-move"))
    can_resize: bool = field(metadata=config(field_name="can-resize"))
    has_focus: bool = field(metadata=config(field_name="has-focus"))
    has_shadow: bool = field(metadata=config(field_name="has-shadow"))
    has_border: bool = field(metadata=config(field_name="has-border"))
    has_parent_zoom: bool = field(metadata=config(field_name="has-parent-zoom"))
    has_fullscreen_zoom: bool = field(metadata=config(field_name="has-fullscreen-zoom"))
    is_native_fullscreen: bool = field(
        metadata=config(field_name="is-native-fullscreen")
    )
    is_visible: bool = field(metadata=config(field_name="is-visible"))
    is_minimized: bool = field(metadata=config(field_name="is-minimized"))
    is_hidden: bool = field(metadata=config(field_name="is-hidden"))
    is_floating: bool = field(metadata=config(field_name="is-floating"))
    is_sticky: bool = field(metadata=config(field_name="is-sticky"))
    is_topmost: bool = field(metadata=config(field_name="is-topmost"))
    is_grabbed: bool = field(metadata=config(field_name="is-grabbed"))

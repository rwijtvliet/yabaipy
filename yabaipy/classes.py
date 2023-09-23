"""Definition of classes."""

from typing import List, Dict, Optional
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config


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


@dataclass_json
@dataclass
class Display:
    id_: int = field(metadata=config(field_name="id"))
    uuid: str
    index: int
    frame: Dict[str, float]
    spaces: List[int]


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

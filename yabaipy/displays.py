from __future__ import annotations
from .shared import run_command, none_means_current
from typing import Any, Callable, List, Dict, Optional
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
import json


def get_all() -> List[Display]:
    """Get info on all displays."""
    displays = json.loads(run_command("yabai -m query --displays"))
    return [Display.from_dict(display) for display in displays]


@none_means_current
def get(display_sel: Optional[Any] = None) -> Display:
    """Get info on display ``display_sel`` (if none provided: current display)."""
    display = json.loads(
        run_command(f"yabai -m query --displays --display {display_sel}")
    )
    return Display.from_dict(display)


@dataclass_json
@dataclass
class Display:
    id_: int = field(metadata=config(field_name="id"))
    uuid: str
    index: int
    frame: Dict[str, float]
    spaces: List[int]

    # def focus(self) -> None:
    #     """Focus the display."""
    #     run_command(f"yabai -m display --focus {self.label}")

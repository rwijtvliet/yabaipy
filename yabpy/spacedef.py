"""Defining spaces."""
from __future__ import annotations
import dataclasses
import json
from typing import Dict
import pathlib
from .spaces import Space

SPACEDEFPATH = pathlib.Path(__file__).parent / "spaces.json"


@dataclasses.dataclass
class SpaceDef:
    key: str  # shortcut key for this space
    name: str
    icon: str
    color: str
    display: int  # preferred display for this space

    @classmethod
    def from_space(cls, sp: Space) -> SpaceDef:
        for sd in get_all_spacedefs():
            if sd.label == sp.label:
                return sd
        return cls("", "", "", "", "")

    @classmethod
    def from_key(cls, key: str) -> SpaceDef:
        for sd in get_all_spacedefs():
            if sd.key == key:
                return sd
        return cls("", "", "", "", "")

    @classmethod
    def from_label(cls, label: str) -> SpaceDef:
        try:
            return get_all_spacedefs().get(label)
        except KeyError:
            return cls("", "", "", "", "")

    @property
    def abbr(self) -> str:
        return f"{self.key}{self.icon}"

    def fullname(self, include_icon: bool = True) -> str:
        icon = f"{self.icon} " if include_icon else ""
        return f"{self.key}: {icon}{self.name}"


def get_all_spacedefs() -> Dict[str, SpaceDef]:
    return {
        label: SpaceDef(**sd_dict)
        for label, sd_dict in json.load(open(SPACEDEFPATH, "r")).items()
    }


def fullname(sp: Space, include_icon: bool = True) -> str:
    sd = get_all_spacedefs()[sp.label]
    icon = f"{sd.icon} " if include_icon else ""
    return f"{sd.key}: {icon}{sd.name}"

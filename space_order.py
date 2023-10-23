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

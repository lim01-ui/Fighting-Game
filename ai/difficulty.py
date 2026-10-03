from dataclasses import dataclass


@dataclass(frozen=True)
class Difficulty:
    name: str
    reaction_frames: int
    attack_chance: float
    block_chance: float
    preferred_distance: int
    attack_range: int
    jump_chance: float
    attack_cooldown: int
    heavy_chance: float = 0.25
    special_chance: float = 0.10


EASY = Difficulty("EASY", 24, 0.20, 0.20, 250, 110, 0.03, 60,
                  heavy_chance=0.15, special_chance=0.05)
NORMAL = Difficulty("NORMAL", 12, 0.45, 0.60, 160, 120, 0.05, 40,
                    heavy_chance=0.35, special_chance=0.15)
HARD = Difficulty("HARD", 8, 0.72, 0.72, 125, 135, 0.06, 30,
                  heavy_chance=0.50, special_chance=0.22)
ALL = {"EASY": EASY, "NORMAL": NORMAL, "HARD": HARD}


def get(name):
    return ALL.get(name.upper(), NORMAL)

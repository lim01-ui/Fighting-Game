"""Asset-backed City and Ocean arenas, cached for match and menu rendering."""

from functools import lru_cache
from pathlib import Path

import pygame
import settings

ASSET_ROOT = Path(__file__).resolve().parent.parent / "assets" / "Stage_Background"

# Retain the existing wire IDs so the lobby, defaults, and LAN setup agree.
# Display names now describe the supplied artwork rather than old palettes.
_LEGACY_PALETTES = ("classic", "night", "snow", "fire", "ice", "storm", "golden")
STAGE_KEYS = ["sunset", "dojo", "neon"]
_WIRE_IDS = [(stage, palette) for stage in STAGE_KEYS for palette in _LEGACY_PALETTES]
_BACKGROUNDS = [("City", f"city {i}", f"CITY {i:02}") for i in range(1, 9)]
_BACKGROUNDS += [("Ocean", f"Ocean_{i}", f"OCEAN {i:02}") for i in range(1, 9)]
CATALOG = dict(zip(_WIRE_IDS, _BACKGROUNDS))


def all_stage_combos():
    return list(CATALOG)


def background_info(stage_key, palette_key="classic"):
    return CATALOG.get((stage_key, palette_key), CATALOG[("sunset", "classic")])


def display_name(stage_key, palette_key="classic"):
    return background_info(stage_key, palette_key)[2]


@lru_cache(maxsize=32)
def _background(group, folder, width, height):
    directory = ASSET_ROOT / group / folder
    paths = sorted(directory.glob("*.png"), key=lambda path: int(path.stem))
    if not paths:
        raise FileNotFoundError(f"No stage backgrounds in {directory}")
    # Each pack includes individual transparent layers and a finished composite.
    # The composite is the largest image, avoiding accidental layer/preview stacking.
    images = [pygame.image.load(str(path)) for path in paths]
    image = max(images, key=lambda image: image.get_width() * image.get_height())
    return pygame.transform.scale(image, (width + 64, height)).convert()


def draw(surface, stage_key, t, scroll=0.0, palette_key="classic"):
    group, folder, _ = background_info(stage_key, palette_key)
    width, height = surface.get_size()
    image = _background(group, folder, width, height)
    offset = 32 + round(max(-1.0, min(1.0, scroll)) * 24)
    surface.blit(image, (-offset, 0))

    # A foreground rooftop/dock anchors feet to the unchanged combat ground line.
    ground_y = round(settings.GROUND_Y * height / settings.WINDOW_HEIGHT)
    floor, edge, seam = ((24, 24, 44), (112, 120, 152), (42, 42, 66)) if group == "City" else (
        (66, 48, 56), (168, 128, 96), (94, 68, 64))
    pygame.draw.rect(surface, floor, (0, ground_y, width, height - ground_y))
    pygame.draw.rect(surface, edge, (0, ground_y, width, 6))
    for y in range(ground_y + 24, height, 24):
        pygame.draw.line(surface, seam, (0, y), (width, y), 2)
    for x in range(-64, width + 64, 64):
        pygame.draw.line(surface, seam, (x, ground_y + 6), (x, height), 2)

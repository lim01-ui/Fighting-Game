"""Cached animation frames from assets/Fighting_Effect's vertical sprite strips."""

from functools import lru_cache
from pathlib import Path

import pygame


ASSET_ROOT = Path(__file__).resolve().parent.parent / "assets" / "Fighting_Effect"
_GAMEBOY_FILES = {
    1: "Effect1 Gameboy Spritesheet.png",
    2: "Effectst2 Gameboy Spritesheet.png",
    3: "Effect3 Gameboy Spritesheet.png",
    4: "Effect4 Gameboy Spritesheet.png",
}


@lru_cache(maxsize=8)
def frames(effect, gameboy=False):
    filename = _GAMEBOY_FILES[effect] if gameboy else f"Effect {effect} - Sprite Sheet.png"
    sheet = pygame.image.load(str(ASSET_ROOT / filename)).convert_alpha()
    cells = [sheet.subsurface((0, y, sheet.get_width(), 32)).copy()
             for y in range(0, sheet.get_height(), 32)]
    # The strips contain blank padding cells; start on the first visible frame.
    cells = [cell for cell in cells if cell.get_bounding_rect().width]
    if not cells:
        raise ValueError(f"Empty fighting effect: {filename}")
    # One shared crop preserves the animation's alignment and size between frames.
    bounds = cells[0].get_bounding_rect()
    for cell in cells[1:]:
        bounds.union_ip(cell.get_bounding_rect())
    return tuple(cell.subsurface(bounds).copy() for cell in cells)


@lru_cache(maxsize=128)
def scaled_frames(effect, size, facing=1, gameboy=False):
    source = frames(effect, gameboy)
    scale = size / max(source[0].get_size())
    dimensions = tuple(max(1, round(value * scale)) for value in source[0].get_size())
    images = tuple(pygame.transform.scale(frame, dimensions) for frame in source)
    if facing < 0:
        images = tuple(pygame.transform.flip(frame, True, False) for frame in images)
    return images


def draw(surface, effect, x, y, progress, size=96, facing=1, gameboy=False, alpha=255):
    images = scaled_frames(effect, size, facing, gameboy)
    index = min(len(images) - 1, int(max(0.0, progress) * len(images)))
    image = images[index]
    if alpha < 255:
        image = image.copy()
        image.set_alpha(max(0, alpha))
    surface.blit(image, image.get_rect(center=(round(x), round(y))))

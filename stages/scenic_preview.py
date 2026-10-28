"""Archived scenic renderer for regenerating previews; not the active stage catalog."""
from functools import lru_cache
from pathlib import Path
import pygame
from stages.catalog import ARENAS, DEFAULT_STAGE
from stages import ambient

ASSET_ROOT = Path(__file__).resolve().parent.parent / 'assets/stages/scenic'
STAGE_KEYS = list(ARENAS)
CATALOG = {(key, 'classic'): ('Scenic', spec['image'], spec['name'])
           for key, spec in ARENAS.items()}
NATIVE_SIZE = (640, 360)


def all_stage_combos():
    return list(CATALOG)


def definition(stage_key):
    return ARENAS.get(stage_key, ARENAS[DEFAULT_STAGE])


def background_info(stage_key, palette_key='classic'):
    spec = definition(stage_key)
    return 'Scenic', spec['image'], spec['name']


def display_name(stage_key, palette_key='classic'):
    return definition(stage_key)['name']


@lru_cache(maxsize=6)
def _background(stage_key):
    image = pygame.image.load(str(ASSET_ROOT / definition(stage_key)['image']))
    return pygame.transform.scale(image, NATIVE_SIZE).convert()


@lru_cache(maxsize=12)
def _animated_frame(stage_key, tick):
    source = _background(stage_key)
    frame = source.copy()
    ambient.draw(frame, source, stage_key, definition(stage_key), tick / 20)
    return frame


def draw(surface, stage_key, t, scroll=0.0, palette_key='classic'):
    key = stage_key if stage_key in ARENAS else DEFAULT_STAGE
    frame = _animated_frame(key, round(max(0, t) * 20))
    if scroll:
        width, height = surface.get_size()
        expanded = pygame.transform.scale(frame, (width + 16, height))
        surface.blit(expanded, (-8 - round(max(-1, min(1, scroll)) * 7), 0))
    else:
        pygame.transform.scale(frame, surface.get_size(), surface)

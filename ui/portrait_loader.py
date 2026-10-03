# ui/portrait_loader.py
"""
Loads character portraits from assets/characters/<key>/portrait.png.

If the PNG exists, it's loaded and cached. If not, the caller receives
None and is expected to fall back to a procedural drawing.

Naming convention:
    assets/characters/rook/portrait.png
    assets/characters/vex/portrait.png
    ...

Recommended portrait size: 220 x 260 px (or any 4:5-ish aspect).
"""

import os
import pygame


_CACHE = {}


def _portrait_path(character_key):
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(here, "assets", "characters", character_key, "portrait.png")


def load_portrait(character_key):
    """
    Return a pygame.Surface for the portrait, or None if no file exists.
    Loaded surfaces are cached so this is cheap to call every frame.
    """
    if character_key in _CACHE:
        return _CACHE[character_key]

    path = _portrait_path(character_key)
    if not os.path.isfile(path):
        _CACHE[character_key] = None
        return None

    try:
        surface = pygame.image.load(path).convert_alpha()
        _CACHE[character_key] = surface
        return surface
    except pygame.error as exc:
        print(f"[portrait_loader] could not load {path}: {exc}")
        _CACHE[character_key] = None
        return None


def scaled_portrait(character_key, size):
    """
    Return the portrait scaled to fit inside `size` (w, h), preserving aspect.
    Returns None if no portrait exists.
    """
    original = load_portrait(character_key)
    if original is None:
        return None
    return pygame.transform.smoothscale(original, size)


def clear_cache():
    """Call this if you replace portrait files at runtime (rarely needed)."""
    _CACHE.clear()

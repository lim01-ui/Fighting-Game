"""Resizable, aspect-preserving presentation around the 1280x720 game canvas.

SDL's logical renderer scales both pixels and mouse coordinates, so menus,
combat and LAN simulation continue to use the same game coordinates.
"""

import os

import pygame

import settings


def create_window(fullscreen: bool = False) -> pygame.Surface:
    """Create a scalable window, or fullscreen at the desktop's resolution."""
    # Pygame uses this compatibility hint to permit fractional window scales
    # (e.g. 1.5x at 1080p). The separate SDL filter hint keeps pixel art sharp.
    os.environ["SDL_HINT_RENDER_SCALE_QUALITY"] = "1"
    os.environ["SDL_RENDER_SCALE_QUALITY"] = "nearest"
    flags = pygame.SCALED | pygame.RESIZABLE
    if fullscreen:
        flags |= pygame.FULLSCREEN
    # SCALED sets SDL's minimum client size to this logical size and uses
    # desktop fullscreen with letterboxing on other aspect ratios. SDL handles
    # resize events; recreating the surface on VIDEORESIZE would break scaling.
    # Frame pacing belongs to the existing scene clocks, including LAN's
    # faster rendering loop, rather than an additional vsync wait.
    screen = pygame.display.set_mode(
        (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), flags, vsync=0,
    )
    pygame.display.set_caption(settings.WINDOW_TITLE)
    return screen


def set_fullscreen(screen, enabled):
    """Switch modes while retaining the current window size when supported."""
    if pygame.display.is_fullscreen() == enabled:
        return screen
    try:
        pygame.display.toggle_fullscreen()
    except pygame.error:
        # Some drivers (including SDL's headless test driver) cannot toggle
        # in place. Tear down the renderer before rebuilding: recreating a
        # live scaled fullscreen renderer is unsafe on some SDL backends.
        pass
    else:
        if pygame.display.is_fullscreen() == enabled:
            return pygame.display.get_surface()
    pygame.display.quit()
    pygame.display.init()
    return create_window(enabled)

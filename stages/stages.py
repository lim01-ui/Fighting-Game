# stages/stages.py
"""
Three base stages, each rendered from a color palette.

Every color comes from the palette dict, so 7 palettes x 3 stages gives
21 genuinely different-looking stages.
"""

import math
import pygame
import settings
from stages import stage_palettes

_atmosphere_surface = None
_atmosphere_size = None


def _scroll_offset(scroll, factor):
    return int(scroll * factor)


def _vgrad(surface, top_color, bottom_color, x, y, w, h):
    for i in range(h):
        t = i / max(1, h - 1)
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
        pygame.draw.rect(surface, (r, g, b), (x, y + i, w, 1))


# =============================================================
# SUNSET / CITY
# =============================================================
def _stage_sunset(surface, t, scroll, pal):
    W, H = settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT
    GY = settings.GROUND_Y

    # Sky
    _vgrad(surface, pal["sky_top"], pal["sky_bottom"], 0, 0, W, GY)

    # Sun / moon
    sun_x = int(W * 0.75) + _scroll_offset(scroll, 15)
    sun_y = int(GY * 0.45)
    pygame.draw.circle(surface, pal["sun"], (sun_x, sun_y), 90)
    pygame.draw.circle(surface, pal["sun_core"], (sun_x, sun_y), 70)

    # Distant city (mid layer)
    mid_off = _scroll_offset(scroll, 45)
    base_y = GY - 20
    buildings = [
        (60, 180, "far"), (140, 240, "far"), (220, 160, "near"),
        (300, 280, "far"), (390, 200, "near"), (480, 260, "far"),
        (580, 180, "near"), (680, 300, "far"), (780, 220, "near"),
        (880, 260, "far"), (980, 200, "near"), (1080, 240, "far"),
    ]
    for bx, bh, layer in buildings:
        top = base_y - bh
        color = pal["far_buildings"] if layer == "far" else pal["near_buildings"]
        pygame.draw.rect(surface, color, (bx - mid_off, top, 80, bh))
        for wy in range(top + 20, base_y - 20, 24):
            for wx in range(bx + 12, bx + 68, 20):
                if (wx + wy) % 5 < 2:
                    pygame.draw.rect(surface, pal["windows"],
                                     (wx - mid_off, wy, 8, 12))

    # Ground
    near_off = _scroll_offset(scroll, 90)
    pygame.draw.rect(surface, pal["ground"], (0, GY, W, H - GY))
    pygame.draw.rect(surface, pal["ground_top"], (0, GY, W, 10))
    for i in range(-1, W + 200, 80):
        x = i - near_off % 80
        pygame.draw.line(surface, pal["ground"], (x, GY + 12), (x, H), 2)


# =============================================================
# DOJO
# =============================================================
def _stage_dojo(surface, t, scroll, pal):
    W, H = settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT
    GY = settings.GROUND_Y

    # Sky
    _vgrad(surface, pal["sky_top"], pal["sky_bottom"], 0, 0, W, GY)

    # Far hills
    far_off = _scroll_offset(scroll, 12)
    pygame.draw.polygon(surface, pal["far_hills"], [
        (0 - far_off, GY - 120), (250 - far_off, GY - 260),
        (500 - far_off, GY - 140), (750 - far_off, GY - 300),
        (1050 - far_off, GY - 160), (W - far_off, GY - 220),
        (W - far_off, GY), (0 - far_off, GY)])

    # Sun
    pygame.draw.circle(surface, pal["sun"],
                       (int(W * 0.25) + _scroll_offset(scroll, 18),
                        GY - 180), 70)

    # Near hills
    mid_off = _scroll_offset(scroll, 35)
    pygame.draw.polygon(surface, pal["near_hills"], [
        (0 - mid_off, GY - 80), (300 - mid_off, GY - 180),
        (600 - mid_off, GY - 100), (950 - mid_off, GY - 200),
        (W - mid_off, GY - 140), (W - mid_off, GY), (0 - mid_off, GY)])

    # Floor
    near_off = _scroll_offset(scroll, 70)
    pygame.draw.rect(surface, pal["floor"], (0, GY, W, H - GY))
    for i in range(-200, W + 200, 80):
        x = i - near_off % 80
        pygame.draw.line(surface, pal["floor_line"], (x, GY), (x, H), 2)
    pygame.draw.rect(surface, pal["floor_edge"], (0, GY, W, 6))

    # Shoji screens
    panel_w = 220
    for x in (0, W - panel_w):
        px = x - _scroll_offset(scroll, 30)
        pygame.draw.rect(surface, pal["screen"], (px, GY - 340, panel_w, 340))
        pygame.draw.rect(surface, pal["screen_frame"], (px, GY - 340, panel_w, 340), 6)
        for i in range(1, 4):
            pygame.draw.line(surface, pal["screen_frame"],
                             (px, GY - 340 + i * 85),
                             (px + panel_w, GY - 340 + i * 85), 4)
        for j in range(1, 3):
            pygame.draw.line(surface, pal["screen_frame"],
                             (px + j * (panel_w // 3), GY - 340),
                             (px + j * (panel_w // 3), GY), 4)


# =============================================================
# NEON ARENA
# =============================================================
def _stage_neon(surface, t, scroll, pal):
    W, H = settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT
    GY = settings.GROUND_Y

    _vgrad(surface, pal["sky_top"], pal["sky_bottom"], 0, 0, W, GY)

    # Neon strips
    strip_off = _scroll_offset(scroll, 20)
    for i, y in enumerate(range(60, GY - 40, 40)):
        color = pal["strip_a"] if i % 2 == 0 else pal["strip_b"]
        pygame.draw.rect(surface, color, (100 - strip_off, y, W - 200, 3))

    # Rings
    mid_off = _scroll_offset(scroll, 40)
    cx = W // 2 - mid_off
    pygame.draw.circle(surface, pal["ring_outer"], (cx, GY - 120), 200, 4)
    pygame.draw.circle(surface, pal["ring_mid"],   (cx, GY - 120), 160, 3)
    pygame.draw.circle(surface, pal["ring_inner"], (cx, GY - 120), 120, 2)

    # Floor
    near_off = _scroll_offset(scroll, 80)
    pygame.draw.rect(surface, pal["floor"], (0, GY, W, H - GY))
    for i in range(-200, W + 200, 60):
        x = i - near_off % 60
        pygame.draw.line(surface, pal["floor_grid"], (x, GY), (x, H), 2)
    for y in range(GY, H, 12):
        pygame.draw.line(surface, pal["floor_grid"], (0, y), (W, y), 1)
    pygame.draw.rect(surface, pal["floor_edge"], (0, GY, W, 3))


def _draw_atmosphere(surface, stage_key, t, scroll, pal):
    global _atmosphere_surface, _atmosphere_size
    size = surface.get_size()
    if _atmosphere_size != size:
        _atmosphere_surface = pygame.Surface(size, pygame.SRCALPHA)
        _atmosphere_size = size
    atmosphere = _atmosphere_surface
    atmosphere.fill((0, 0, 0, 0))

    glow_color = pal.get("sun_core", pal.get("ring_inner", (180, 140, 255)))
    if stage_key == "neon":
        glow_color = pal["ring_inner"]
    glow = pygame.Surface((size[0], 190), pygame.SRCALPHA)
    glow_center_x = size[0] // 2 - _scroll_offset(scroll, 18)
    for index, alpha in enumerate((4, 7, 10, 14, 18)):
        width = size[0] - index * 120
        height = 170 - index * 25
        if width <= 0 or height <= 0:
            continue
        pygame.draw.ellipse(
            glow, (*glow_color, alpha),
            (glow_center_x - width // 2, 100 - height // 2, width, height),
        )
    atmosphere.blit(glow, (0, settings.GROUND_Y - 180))

    # Slowly drifting, deterministic motes keep the background alive without
    # introducing random state into lockstep network matches.
    for index in range(22):
        phase = t * (0.18 + (index % 5) * 0.035) + index * 2.399
        x = int((index * 173 + math.sin(phase) * 28 - scroll * 14) % size[0])
        vertical_range = max(1, settings.GROUND_Y - 90)
        y = int(42 + ((index * 97 + t * (5 + index % 4)) % vertical_range))
        radius = 1 if index % 4 else 2
        alpha = 24 + int((math.sin(phase * 1.7) + 1) * 22)
        pygame.draw.circle(
            atmosphere, (*glow_color, alpha), (x, y), radius,
        )
        if index % 7 == 0:
            pygame.draw.line(
                atmosphere, (*glow_color, alpha // 2),
                (x - 4, y), (x + 4, y), 1,
            )
            pygame.draw.line(
                atmosphere, (*glow_color, alpha // 2),
                (x, y - 4), (x, y + 4), 1,
            )

    if stage_key == "neon":
        for index in range(5):
            y = int((index * 137 + t * 18) % settings.GROUND_Y)
            x = (index * 251 - _scroll_offset(scroll, 12)) % size[0]
            pygame.draw.line(
                atmosphere, (*glow_color, 18),
                (x, y), (x + 26, y - 8), 2,
            )
    surface.blit(atmosphere, (0, 0))


STAGE_FUNCS = {
    "sunset": _stage_sunset,
    "dojo":   _stage_dojo,
    "neon":   _stage_neon,
}

STAGE_KEYS = ["sunset", "dojo", "neon"]


def draw(surface, stage_key, t, scroll=0.0, palette_key="classic"):
    pal = stage_palettes.get(stage_key, palette_key)
    STAGE_FUNCS.get(stage_key, _stage_sunset)(surface, t, scroll, pal)
    _draw_atmosphere(surface, stage_key, t, scroll, pal)


def all_stage_combos():
    combos = []
    for s in STAGE_KEYS:
        for p in stage_palettes.PALETTE_KEYS:
            combos.append((s, p))
    return combos

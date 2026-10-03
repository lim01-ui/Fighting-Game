# stages/stage_palettes.py
"""
Real palette data for stages.

Each stage's drawing code reads colors from the palette dict it is
handed. Different palettes produce genuinely different-looking stages,
not tinted versions of the same image.

Structure:
    PALETTES[stage_key][palette_key] = { named colors }
"""

import pygame


# ---------- SUNSET / CITY ----------
SUNSET = {
    "classic": {
        "sky_top": (250, 130, 90), "sky_bottom": (255, 210, 150),
        "sun": (255, 220, 130), "sun_core": (255, 240, 200),
        "far_buildings": (50, 35, 70), "near_buildings": (80, 50, 90),
        "windows": (255, 220, 130),
        "ground": (70, 45, 55), "ground_top": (100, 65, 75),
    },
    "night": {
        "sky_top": (10, 15, 45), "sky_bottom": (30, 40, 80),
        "sun": (230, 235, 245), "sun_core": (255, 255, 255),
        "far_buildings": (15, 20, 40), "near_buildings": (25, 30, 55),
        "windows": (255, 240, 150),
        "ground": (20, 25, 45), "ground_top": (40, 45, 70),
    },
    "snow": {
        "sky_top": (200, 220, 240), "sky_bottom": (240, 245, 250),
        "sun": (255, 255, 240), "sun_core": (255, 255, 255),
        "far_buildings": (180, 195, 215), "near_buildings": (200, 215, 235),
        "windows": (255, 250, 200),
        "ground": (225, 235, 245), "ground_top": (245, 250, 255),
    },
    "fire": {
        "sky_top": (80, 15, 10), "sky_bottom": (200, 60, 20),
        "sun": (255, 100, 30), "sun_core": (255, 200, 80),
        "far_buildings": (40, 10, 10), "near_buildings": (70, 20, 15),
        "windows": (255, 200, 80),
        "ground": (60, 20, 15), "ground_top": (100, 35, 20),
    },
    "ice": {
        "sky_top": (140, 200, 240), "sky_bottom": (200, 235, 250),
        "sun": (240, 250, 255), "sun_core": (255, 255, 255),
        "far_buildings": (140, 180, 220), "near_buildings": (170, 210, 240),
        "windows": (220, 240, 255),
        "ground": (170, 210, 235), "ground_top": (200, 230, 250),
    },
    "storm": {
        "sky_top": (30, 30, 55), "sky_bottom": (70, 70, 100),
        "sun": (150, 150, 170), "sun_core": (200, 200, 220),
        "far_buildings": (35, 35, 55), "near_buildings": (55, 55, 75),
        "windows": (200, 180, 130),
        "ground": (40, 40, 60), "ground_top": (70, 70, 90),
    },
    "golden": {
        "sky_top": (200, 130, 40), "sky_bottom": (255, 220, 120),
        "sun": (255, 230, 140), "sun_core": (255, 250, 210),
        "far_buildings": (90, 60, 20), "near_buildings": (130, 90, 30),
        "windows": (255, 240, 150),
        "ground": (110, 70, 25), "ground_top": (150, 100, 40),
    },
}


# ---------- DOJO ----------
DOJO = {
    "classic": {
        "sky_top": (200, 170, 140), "sky_bottom": (230, 200, 165),
        "far_hills": (110, 90, 110), "near_hills": (90, 70, 90),
        "sun": (255, 200, 150),
        "floor": (110, 70, 40), "floor_line": (80, 50, 25), "floor_edge": (60, 40, 20),
        "screen": (230, 210, 180), "screen_frame": (140, 90, 50),
    },
    "night": {
        "sky_top": (15, 20, 50), "sky_bottom": (35, 45, 75),
        "far_hills": (20, 25, 45), "near_hills": (12, 18, 35),
        "sun": (230, 235, 245),
        "floor": (55, 35, 25), "floor_line": (35, 20, 15), "floor_edge": (25, 15, 10),
        "screen": (180, 160, 130), "screen_frame": (60, 35, 15),
    },
    "snow": {
        "sky_top": (200, 215, 235), "sky_bottom": (235, 245, 255),
        "far_hills": (170, 190, 215), "near_hills": (200, 220, 240),
        "sun": (255, 255, 250),
        "floor": (200, 180, 150), "floor_line": (160, 140, 110), "floor_edge": (120, 100, 70),
        "screen": (250, 250, 245), "screen_frame": (140, 100, 60),
    },
    "fire": {
        "sky_top": (120, 40, 20), "sky_bottom": (200, 90, 40),
        "far_hills": (60, 20, 10), "near_hills": (40, 12, 8),
        "sun": (255, 140, 40),
        "floor": (110, 50, 25), "floor_line": (70, 25, 10), "floor_edge": (50, 18, 8),
        "screen": (200, 140, 90), "screen_frame": (90, 40, 15),
    },
    "ice": {
        "sky_top": (170, 210, 240), "sky_bottom": (215, 235, 250),
        "far_hills": (150, 190, 220), "near_hills": (180, 210, 235),
        "sun": (245, 250, 255),
        "floor": (170, 200, 220), "floor_line": (130, 160, 180), "floor_edge": (100, 130, 150),
        "screen": (235, 245, 250), "screen_frame": (100, 140, 170),
    },
    "storm": {
        "sky_top": (60, 60, 80), "sky_bottom": (100, 100, 120),
        "far_hills": (45, 45, 65), "near_hills": (30, 30, 45),
        "sun": (170, 170, 190),
        "floor": (70, 50, 40), "floor_line": (45, 30, 20), "floor_edge": (30, 20, 15),
        "screen": (150, 140, 120), "screen_frame": (60, 40, 25),
    },
    "golden": {
        "sky_top": (200, 150, 60), "sky_bottom": (255, 220, 140),
        "far_hills": (140, 100, 40), "near_hills": (110, 75, 25),
        "sun": (255, 230, 150),
        "floor": (160, 110, 45), "floor_line": (110, 70, 20), "floor_edge": (80, 50, 15),
        "screen": (250, 220, 160), "screen_frame": (150, 90, 30),
    },
}


# ---------- NEON ARENA ----------
NEON = {
    "classic": {
        "sky_top": (15, 5, 25), "sky_bottom": (30, 10, 45),
        "strip_a": (180, 0, 140), "strip_b": (0, 120, 220),
        "ring_outer": (60, 0, 90), "ring_mid": (0, 60, 140), "ring_inner": (120, 0, 180),
        "floor": (15, 15, 30), "floor_grid": (40, 20, 70), "floor_edge": (200, 40, 200),
    },
    "night": {
        "sky_top": (5, 5, 15), "sky_bottom": (15, 10, 30),
        "strip_a": (100, 0, 90), "strip_b": (0, 70, 140),
        "ring_outer": (40, 0, 60), "ring_mid": (0, 40, 90), "ring_inner": (80, 0, 120),
        "floor": (8, 8, 20), "floor_grid": (25, 15, 45), "floor_edge": (120, 20, 130),
    },
    "snow": {
        "sky_top": (200, 220, 245), "sky_bottom": (235, 245, 255),
        "strip_a": (180, 200, 240), "strip_b": (200, 220, 250),
        "ring_outer": (170, 200, 240), "ring_mid": (200, 225, 250), "ring_inner": (230, 240, 255),
        "floor": (200, 215, 235), "floor_grid": (170, 190, 215), "floor_edge": (220, 235, 250),
    },
    "fire": {
        "sky_top": (40, 5, 5), "sky_bottom": (90, 15, 10),
        "strip_a": (255, 60, 20), "strip_b": (255, 140, 40),
        "ring_outer": (120, 20, 5), "ring_mid": (200, 60, 20), "ring_inner": (255, 120, 40),
        "floor": (35, 10, 5), "floor_grid": (80, 20, 10), "floor_edge": (255, 80, 30),
    },
    "ice": {
        "sky_top": (150, 200, 235), "sky_bottom": (190, 225, 250),
        "strip_a": (100, 180, 240), "strip_b": (140, 200, 240),
        "ring_outer": (140, 190, 230), "ring_mid": (170, 210, 245), "ring_inner": (200, 230, 255),
        "floor": (170, 200, 225), "floor_grid": (130, 170, 200), "floor_edge": (100, 180, 240),
    },
    "storm": {
        "sky_top": (25, 25, 45), "sky_bottom": (50, 50, 80),
        "strip_a": (120, 120, 150), "strip_b": (150, 150, 180),
        "ring_outer": (70, 70, 100), "ring_mid": (100, 100, 130), "ring_inner": (140, 140, 170),
        "floor": (30, 30, 45), "floor_grid": (55, 55, 75), "floor_edge": (140, 140, 170),
    },
    "golden": {
        "sky_top": (60, 40, 5), "sky_bottom": (120, 80, 20),
        "strip_a": (255, 200, 60), "strip_b": (255, 220, 120),
        "ring_outer": (150, 100, 20), "ring_mid": (200, 140, 40), "ring_inner": (255, 220, 100),
        "floor": (50, 35, 15), "floor_grid": (100, 70, 25), "floor_edge": (255, 200, 80),
    },
}


ALL_PALETTES = {
    "sunset": SUNSET,
    "dojo":   DOJO,
    "neon":   NEON,
}


PALETTE_KEYS = ["classic", "night", "snow", "fire", "ice", "storm", "golden"]


def get(stage_key, palette_key):
    return ALL_PALETTES[stage_key][palette_key]


def display_name(stage_key, palette_key):
    return f"{stage_key.upper()} {palette_key.upper()}"

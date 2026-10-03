# ui/stage_select.py
"""
Stage pick screen with 21 tiles (3 stages x 7 palettes).

- 15-second countdown at the top
- Arrow keys / WASD to move cursor
- Enter confirms and locks in
- When time expires, a random stage is picked
- Returns (stage_key, palette_key) as a tuple
"""

import math
import random
import pygame

import settings
from stages import stages, stage_palettes
from audio import sound_fx


TILE_W = 160
TILE_H = 110
TILE_GAP = 12
COLS = 7
ROWS = 3
GRID_LEFT = (settings.WINDOW_WIDTH - (COLS * (TILE_W + TILE_GAP) - TILE_GAP)) // 2
GRID_TOP = 130

COUNTDOWN_SECONDS = 15


def _tile_rect(index):
    row = index // COLS
    col = index % COLS
    x = GRID_LEFT + col * (TILE_W + TILE_GAP)
    y = GRID_TOP + row * (TILE_H + TILE_GAP)
    return pygame.Rect(x, y, TILE_W, TILE_H)


def _make_thumbnail(stage_key, palette_key):
    """Render a small preview of the stage in that palette."""
    surf = pygame.Surface((TILE_W, TILE_H))
    # Render at full size, then downscale
    full = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
    stages.draw(full, stage_key, t=0.0, scroll=0.0, palette_key=palette_key)
    thumb = pygame.transform.smoothscale(full, (TILE_W, TILE_H - 22))
    return thumb


def run_stage_select(screen, clock, title="CHOOSE YOUR STAGE"):
    """
    Show the stage pick screen.
    Returns (stage_key, palette_key) as a tuple.
    """
    title_font = pygame.font.SysFont("Arial", 40, bold=True)
    timer_font = pygame.font.SysFont("Arial", 44, bold=True)
    small_font = pygame.font.SysFont("Arial", 14, bold=True)
    hint_font  = pygame.font.SysFont("Arial", 18)

    combos = stages.all_stage_combos()   # list of (stage, palette)
    total = len(combos)
    selected = 0

    # Build thumbnails once (they don't change)
    thumbnails = [_make_thumbnail(s, p) for (s, p) in combos]

    # Countdown in frames (60 fps)
    timer_frames = COUNTDOWN_SECONDS * 60

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return combos[selected]
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return combos[selected]
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    selected = (selected + 1) % total
                    sound_fx.play("menu_move")
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    selected = (selected - 1) % total
                    sound_fx.play("menu_move")
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + COLS) % total
                    sound_fx.play("menu_move")
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - COLS) % total
                    sound_fx.play("menu_move")
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    sound_fx.play("menu_confirm")
                    return combos[selected]

        # Tick countdown
        timer_frames -= 1
        if timer_frames <= 0:
            # Auto-pick random
            random_pick = random.choice(combos)
            sound_fx.play("menu_confirm")
            return random_pick

        # Warn at 5s and 10s
        secs_left = max(0, timer_frames // 60)

        # ---- Draw ----
        screen.fill((12, 12, 26))

        # Title
        title_img = title_font.render(title, True, settings.WHITE)
        screen.blit(title_img, title_img.get_rect(
            center=(settings.WINDOW_WIDTH // 2, 55)))

        # Timer
        timer_color = (255, 80, 80) if secs_left <= 5 else (255, 240, 120)
        timer_img = timer_font.render(f"{secs_left}", True, timer_color)
        screen.blit(timer_img, timer_img.get_rect(
            center=(settings.WINDOW_WIDTH // 2, 100)))

        # Grid
        for i, ((sk, pk), thumb) in enumerate(zip(combos, thumbnails)):
            tile = _tile_rect(i)
            is_sel = (i == selected)
            # 1. Background
            pygame.draw.rect(screen, (30, 30, 50), tile)
            # 2. Thumbnail
            screen.blit(thumb, tile.topleft)
            # 3. Dark strip under the label
            strip = pygame.Rect(tile.x, tile.bottom - 22, tile.width, 22)
            s = pygame.Surface((strip.width, strip.height), pygame.SRCALPHA)
            s.fill((0, 0, 0, 210))
            screen.blit(s, strip.topleft)
            # 4. Label text on top of strip
            label = stage_palettes.display_name(sk, pk)
            label_img = small_font.render(label, True, (240, 240, 240))
            screen.blit(label_img, label_img.get_rect(center=strip.center))
            # 5. Border last (so it outlines everything cleanly)
            border_color = (255, 240, 100) if is_sel else (90, 90, 120)
            thickness = 4 if is_sel else 2
            pygame.draw.rect(screen, border_color, tile, thickness)

        # Hint
        hint = hint_font.render(
            "Arrows / WASD to move    ENTER to lock in    Auto-pick when timer hits 0",
            True, (200, 200, 200))
        screen.blit(hint, hint.get_rect(
            center=(settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT - 30)))

        pygame.display.flip()
        clock.tick(settings.FPS)

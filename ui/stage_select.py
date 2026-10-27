# ui/stage_select.py
"""
Stage pick screen for the imported City and Ocean backgrounds.

- Live arena preview and a wall-clock 15-second countdown
- Arrow keys / WASD to move cursor
- Enter confirms and locks in
- When time expires, a random stage is picked
- Returns (stage_key, palette_key) as a tuple
- Mouse hover previews a tile; the lock-in button confirms it
"""

import math
import random
import pygame
from ui import retro, theme

import settings
from stages import stages, stage_palettes
from audio import sound_fx
from ui.text_layout import draw_text_fit


TILE_W = 160
TILE_H = 62
TILE_GAP = 12
COLS = 7
ROWS = 3
GRID_LEFT = (settings.WINDOW_WIDTH - (COLS * (TILE_W + TILE_GAP) - TILE_GAP)) // 2
GRID_TOP = 435

COUNTDOWN_SECONDS = 15


def _tile_rect(index):
    row = index // COLS
    col = index % COLS
    x = GRID_LEFT + col * (TILE_W + TILE_GAP)
    y = GRID_TOP + row * (TILE_H + 8)
    return pygame.Rect(x, y, TILE_W, TILE_H)


def _make_thumbnail(stage_key, palette_key):
    """Render a small preview of the stage in that palette."""
    # Render at full size, then downscale
    full = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
    stages.draw(full, stage_key, t=0.0, scroll=0.0, palette_key=palette_key)
    thumb = pygame.transform.scale(full, (TILE_W, TILE_H - 22))
    return thumb


def run_stage_select(screen, clock, title="CHOOSE YOUR STAGE"):
    """Browse all arenas with an animated preview and mouse or keyboard input."""
    fonts = {name: retro.font("Arial", size, bold=True)
             for name, size in (("title", 38), ("heading", 30), ("body", 19), ("small", 14))}
    combos = stages.all_stage_combos()
    thumbnails = [pygame.transform.scale(_make_thumbnail(*combo), (TILE_W, 42))
                  for combo in combos]
    selected = 0
    elapsed = 0.0
    deadline = pygame.time.get_ticks() + COUNTDOWN_SECONDS * 1000
    world = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
    preview = pygame.Surface((650, 300))
    confirm = pygame.Rect(850, 338, 330, 48)
    tiles = [_tile_rect(i) for i in range(len(combos))]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return combos[selected]
            if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                for index, tile in enumerate(tiles):
                    if tile.collidepoint(event.pos):
                        if selected != index:
                            sound_fx.play("menu_move")
                        selected = index
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if confirm.collidepoint(event.pos):
                        sound_fx.play("menu_confirm")
                        return combos[selected]
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return combos[selected]
                offsets = {pygame.K_RIGHT: 1, pygame.K_d: 1, pygame.K_LEFT: -1,
                           pygame.K_a: -1, pygame.K_DOWN: COLS, pygame.K_s: COLS,
                           pygame.K_UP: -COLS, pygame.K_w: -COLS}
                if event.key in offsets:
                    selected = (selected + offsets[event.key]) % len(combos)
                    sound_fx.play("menu_move")
                elif event.key == pygame.K_r:
                    selected = random.randrange(len(combos))
                    sound_fx.play("menu_move")
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    sound_fx.play("menu_confirm")
                    return combos[selected]
        remaining = max(0, (deadline - pygame.time.get_ticks()) / 1000)
        if remaining <= 0:
            sound_fx.play("menu_confirm")
            return random.choice(combos)
        theme.background(screen, shade=130)
        def text(key, value, color, rect, align="left"):
            draw_text_fit(screen, fonts[key], value, color, pygame.Rect(rect), align=align)
        text("small", f"ARENA SELECT / {len(combos)} BACKGROUNDS", theme.GOLD, (48, 18, 900, 24))
        text("title", title, theme.PALE, (46, 46, 1040, 55))
        text("heading", f"{math.ceil(remaining):02}s", (255, 185, 99), (1120, 46, 110, 55), "right")
        pygame.draw.rect(screen, theme.NAVY, (48, 112, 1184, 3))
        pygame.draw.rect(screen, theme.GOLD, (48, 112, round(1184 * remaining / COUNTDOWN_SECONDS), 3))
        sk, pk = combos[selected]
        stages.draw(world, sk, elapsed, scroll=math.sin(elapsed * 0.25) * 0.3, palette_key=pk)
        pygame.transform.scale(world, preview.get_size(), preview)
        retro.pixelate(preview, 3)
        screen.blit(preview, (48, 128))
        pygame.draw.rect(screen, theme.GOLD, (48, 128, 650, 300), 1)
        pygame.draw.rect(screen, theme.PANEL, (720, 128, 512, 300), border_radius=0)
        group, _, _ = stages.background_info(sk, pk)
        heading, line1, line2 = (
            ("CITY ROOFTOPS", "Fight above a layered pixel skyline.", "Eight cityscapes. One rooftop arena.")
            if group == "City" else
            ("OCEAN FRONT", "Face your rival beside the open sea.", "Eight ocean views. A dockside arena.")
        )
        text("small", heading, theme.GOLD, (748, 148, 450, 28))
        text("heading", stage_palettes.display_name(sk, pk), theme.PALE, (748, 184, 450, 46))
        text("body", line1, theme.MUTED, (748, 242, 450, 28))
        text("body", line2, theme.MUTED, (748, 275, 450, 28))
        pygame.draw.rect(screen, theme.BLUE, confirm, border_radius=0)
        pygame.draw.rect(screen, theme.GOLD, confirm, 1, border_radius=0)
        text("body", "ENTER / CLICK: LOCK IN ARENA", theme.PALE, confirm, "center")
        for i, ((stage, palette), thumb) in enumerate(zip(combos, thumbnails)):
            tile = tiles[i]
            screen.blit(thumb, tile)
            pygame.draw.rect(screen, theme.PANEL, (tile.x, tile.y + 40, tile.w, 22))
            text("small", stage_palettes.display_name(stage, palette), theme.PALE, (tile.x + 4, tile.y + 40, tile.w - 8, 22), "center")
            pygame.draw.rect(screen, theme.GOLD if i == selected else theme.MUTED, tile, 3 if i == selected else 1)
        text("small", "ARROWS / WASD: BROWSE    MOUSE: PREVIEW    R: RANDOM    ENTER: CONFIRM    ESC: USE CURRENT", (155, 172, 195), (40, 661, 1200, 40), "center")
        theme.footer(screen, "ARROWS / WASD: BROWSE    R: RANDOM    ENTER / CLICK: CONFIRM    ESC: USE CURRENT")
        retro.present(screen)
        elapsed += clock.tick(settings.FPS) / 1000.0

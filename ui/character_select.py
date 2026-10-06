# ui/character_select.py
"""
KOF-style character select screen with portrait support.

Portraits are ALWAYS drawn preserving their original aspect ratio.
If a portrait doesn't fill its box, it's centered with empty space
around it — never stretched.
"""

import math
import pygame

import settings
from characters import character_data
from characters import pixel_fighter
from characters import sprite_fighter
from audio import sound_fx
from ui import portrait_loader
from ui.text_layout import draw_text_fit


GRID_COLS = 4
GRID_ROWS = 4
CELL_W = 120
CELL_H = 100
CELL_GAP = 14
GRID_LEFT = 60
GRID_TOP = 140

PANEL_LEFT = GRID_LEFT + GRID_COLS * (CELL_W + CELL_GAP) + 40
PANEL_TOP = 140
PANEL_W = settings.WINDOW_WIDTH - PANEL_LEFT - 60
PANEL_H = GRID_ROWS * (CELL_H + CELL_GAP) - CELL_GAP


def _cell_rect(index):
    row = index // GRID_COLS
    col = index % GRID_COLS
    x = GRID_LEFT + col * (CELL_W + CELL_GAP)
    y = GRID_TOP + row * (CELL_H + CELL_GAP)
    return pygame.Rect(x, y, CELL_W, CELL_H)


def _draw_fighter_preview(surface, rect, character, t):
    """Simple procedural preview, used as fallback when no portrait exists."""
    body = character["body"]
    colors = character["colors"]
    margin = 18
    avail_w = rect.width - margin * 2
    avail_h = rect.height - margin * 2
    scale = min(avail_w / body["width"], avail_h / body["height"])
    w = int(body["width"] * scale)
    h = int(body["height"] * scale)
    cx = rect.centerx
    bottom = rect.bottom - margin
    bob = int(math.sin(t * 3.0) * 2)
    body_rect = pygame.Rect(cx - w // 2, bottom - h + bob, w, h)
    pygame.draw.rect(surface, colors["body"], body_rect)
    pygame.draw.rect(surface, colors["accent"], body_rect, 2)
    eye_w = max(6, w // 8)
    eye_x = body_rect.right - eye_w - 6
    eye_y = body_rect.top + max(10, h // 6)
    pygame.draw.rect(surface, colors["eye"], (eye_x, eye_y, eye_w, eye_w))


def _blit_fit(surface, image, box_rect, border_color=None):
    """
    Draw `image` centered inside `box_rect`, scaled to fit while
    PRESERVING aspect ratio. Never stretches.

    Optionally draws a border around the actual drawn image.
    """
    iw, ih = image.get_size()
    if iw <= 0 or ih <= 0:
        return
    scale = min(box_rect.width / iw, box_rect.height / ih)
    new_w = max(1, int(iw * scale))
    new_h = max(1, int(ih * scale))
    scaled = pygame.transform.smoothscale(image, (new_w, new_h))
    r = scaled.get_rect(center=box_rect.center)
    surface.blit(scaled, r)
    if border_color is not None:
        pygame.draw.rect(surface, border_color, r.inflate(4, 4), 2)


def _draw_stat_bar(surface, font, x, y, w, label, value, max_value):
    label_img = font.render(label, True, settings.WHITE)
    surface.blit(label_img, (x, y))
    bar_x = x + 100
    bar_y = y + 4
    bar_w = w - 100
    bar_h = 16
    pygame.draw.rect(surface, (30, 30, 40), (bar_x, bar_y, bar_w, bar_h))
    ratio = max(0.0, min(1.0, value / max_value))
    fill_w = int(bar_w * ratio)
    pygame.draw.rect(surface, (240, 200, 80), (bar_x, bar_y, fill_w, bar_h))
    pygame.draw.rect(surface, settings.WHITE, (bar_x, bar_y, bar_w, bar_h), 1)


def run_character_select(screen, clock, title="SELECT YOUR FIGHTER",
                         allow_random=False):
    title_font = pygame.font.SysFont("Arial", 44, bold=True)
    item_font  = pygame.font.SysFont("Arial", 20, bold=True)
    small_font = pygame.font.SysFont("Arial", 16, bold=True)
    hint_font  = pygame.font.SysFont("Arial", 18)

    roster = character_data.all_characters()
    total = len(roster)
    selected = 0
    cursor_angle = 0.0

    while True:
        t = pygame.time.get_ticks() / 1000.0
        cursor_angle += 0.05

        # ---------------- INPUT ----------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sound_fx.play("menu_back")
                    return None
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    selected = (selected + 1) % total
                    sound_fx.play("menu_move")
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    selected = (selected - 1) % total
                    sound_fx.play("menu_move")
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + GRID_COLS) % total
                    sound_fx.play("menu_move")
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - GRID_COLS) % total
                    sound_fx.play("menu_move")
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    sound_fx.play("menu_confirm")
                    return roster[selected]["key"]
                if allow_random and event.key == pygame.K_r:
                    return None

        # ---------------- DRAW ----------------
        screen.fill((12, 12, 26))

        draw_text_fit(
            screen, title_font, title, settings.WHITE,
            pygame.Rect(30, 24, settings.WINDOW_WIDTH - 60, 72),
        )

        # ----- GRID -----
        for i, ch in enumerate(roster):
            cell = _cell_rect(i)
            is_selected = (i == selected)
            bg = (40, 40, 60) if not is_selected else (70, 70, 110)
            pygame.draw.rect(screen, bg, cell)

            if is_selected:
                pulse = int(3 + 2 * math.sin(cursor_angle * 4))
                pygame.draw.rect(screen, (255, 240, 100), cell, 2 + pulse)
            else:
                pygame.draw.rect(screen, (90, 90, 120), cell, 2)

            # Cell art: portrait if available, else procedural preview
            cell_inner = pygame.Rect(
                cell.x + 6, cell.y + 6,
                cell.width - 12, cell.height - 34,
            )
            portrait = portrait_loader.load_portrait(ch["key"])
            if portrait is not None:
                _blit_fit(screen, portrait, cell_inner)
            elif ch.get("sprite_sheet"):
                pixel_fighter.blit_fit(
                    screen, pixel_fighter.preview_frame(), cell_inner
                )
            elif ch.get("sprite_asset"):
                sprite_fighter.blit_fit(
                    screen,
                    sprite_fighter.preview_frame(ch["sprite_asset"]),
                    cell_inner,
                )
            else:
                _draw_fighter_preview(screen, cell, ch, t + i * 0.3)

            # Name strip at the bottom of the cell
            name_img = item_font.render(ch["name"], True, settings.WHITE)
            name_rect = name_img.get_rect(center=(cell.centerx, cell.bottom - 12))
            if name_rect.width > cell.width - 12:
                name_img = pygame.transform.smoothscale(
                    name_img,
                    (cell.width - 12, max(1, int(name_img.get_height()
                                                  * (cell.width - 12) / name_rect.width))),
                )
                name_rect = name_img.get_rect(center=(cell.centerx, cell.bottom - 12))
            strip = pygame.Rect(cell.left + 4, name_rect.top - 2,
                                cell.width - 8, name_rect.height + 4)
            s = pygame.Surface((strip.width, strip.height), pygame.SRCALPHA)
            s.fill((0, 0, 0, 140))
            screen.blit(s, strip.topleft)
            screen.blit(name_img, name_rect)

        # ----- SIDE PANEL -----
        panel = pygame.Rect(PANEL_LEFT, PANEL_TOP, PANEL_W, PANEL_H)
        pygame.draw.rect(screen, (25, 25, 45), panel)
        pygame.draw.rect(screen, (90, 90, 120), panel, 2)

        ch = roster[selected]

        # Portrait box (fixed shape, portrait centered inside, NOT stretched)
        portrait_area = pygame.Rect(panel.x + 20, panel.y + 20,
                                    panel.width - 40, 200)
        pygame.draw.rect(screen, (15, 15, 30), portrait_area)

        big_portrait = portrait_loader.load_portrait(ch["key"])
        if big_portrait is not None:
            _blit_fit(screen, big_portrait, portrait_area,
                      border_color=ch["colors"]["accent"])
        elif ch.get("sprite_sheet"):
            pixel_fighter.blit_fit(
                screen, pixel_fighter.preview_frame(), portrait_area
            )
        elif ch.get("sprite_asset"):
            sprite_fighter.blit_fit(
                screen,
                sprite_fighter.preview_frame(ch["sprite_asset"]),
                portrait_area,
            )
        else:
            _draw_fighter_preview(screen, portrait_area, ch, t)

        # Name + archetype
        draw_text_fit(
            screen, title_font, ch["name"], settings.WHITE,
            pygame.Rect(panel.x + 20, panel.y + 224, panel.width - 40, 46),
            align="left",
        )
        draw_text_fit(
            screen, item_font, ch["archetype"], (200, 220, 255),
            pygame.Rect(panel.x + 20, panel.y + 274, panel.width - 40, 28),
            align="left",
        )
        ultimate_name = character_data.ultimate_for(ch["key"])["name"]
        draw_text_fit(
            screen, small_font, f"ULTIMATE: {ultimate_name}",
            (255, 220, 115),
            pygame.Rect(panel.x + 20, panel.y + 298, panel.width - 40, 22),
            align="left",
        )

        # Stats
        stats = ch["stats"]
        stat_defs = [
            ("SPEED",   stats["speed"],   1.6),
            ("JUMP",    stats["jump"],    1.6),
            ("HEALTH",  stats["health"],  1.6),
            ("DAMAGE",  stats["damage"],  1.6),
            ("DEFENSE", 2.0 - stats["defense"], 1.6),
            ("REACH",   ch["attack_mods"]["reach"], 1.6),
        ]
        sy = panel.y + 328
        for i, (label, val, mx) in enumerate(stat_defs):
            _draw_stat_bar(screen, small_font, panel.x + 20,
                           sy + i * 19, panel.width - 40, label, val, mx)

        hint_text = "Arrows / WASD to move    ENTER to confirm    ESC to go back"
        if allow_random:
            hint_text += "    R for random"
        draw_text_fit(
            screen, hint_font, hint_text, (200, 200, 200),
            pygame.Rect(20, settings.WINDOW_HEIGHT - 52,
                        settings.WINDOW_WIDTH - 40, 40),
        )

        pygame.display.flip()
        clock.tick(settings.FPS)

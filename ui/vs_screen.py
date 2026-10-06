# ui/vs_screen.py
"""
VS screen -- shown before ROUND 1 of each match.

Displays:
    - Left portrait / fighter preview for Player 1
    - Right portrait / fighter preview for Player 2
    - Big "VS" in the middle
    - Names sliding in from the sides
    - Stage name at the bottom
    - "PRESS ENTER TO BEGIN" prompt

Returns "start" when the player presses Enter/Space, or None on ESC.
"""

import math
import pygame
import settings
from characters import character_data
from characters import pixel_fighter
from characters import sprite_fighter
from ui import portrait_loader
from effects import easing
from ui.text_layout import draw_text_fit


def _draw_preview(surface, rect, character, t, facing=1):
    body = character["body"]
    colors = character["colors"]
    margin = 20
    avail_w = rect.width - margin * 2
    avail_h = rect.height - margin * 2
    scale = min(avail_w / body["width"], avail_h / body["height"])
    w = int(body["width"] * scale)
    h = int(body["height"] * scale)
    cx = rect.centerx
    bottom = rect.bottom - margin
    bob = int(math.sin(t * 3.0) * 3)
    body_rect = pygame.Rect(cx - w // 2, bottom - h + bob, w, h)
    pygame.draw.rect(surface, colors["body"], body_rect)
    pygame.draw.rect(surface, colors["accent"], body_rect, 3)
    eye_w = max(6, w // 8)
    eye_x = (body_rect.right - eye_w - 6) if facing == 1 else (body_rect.left + 6)
    eye_y = body_rect.top + max(10, h // 6)
    pygame.draw.rect(surface, colors["eye"], (eye_x, eye_y, eye_w, eye_w))


def _draw_side(surface, side_rect, character, t, facing, side):
    """side: 'left' or 'right'."""
    portrait = portrait_loader.load_portrait(character["key"])
    inner = side_rect.inflate(-40, -40)
    pygame.draw.rect(surface, (25, 25, 45), inner)
    pygame.draw.rect(surface, character["colors"]["accent"], inner, 3)

    if portrait is not None:
        iw, ih = portrait.get_size()
        sc = min(inner.width / iw, inner.height / ih)
        new_size = (int(iw * sc), int(ih * sc))
        scaled = pygame.transform.smoothscale(portrait, new_size)
        r = scaled.get_rect(center=inner.center)
        surface.blit(scaled, r)
    elif character.get("sprite_sheet"):
        image = pixel_fighter.preview_frame()
        if facing < 0:
            image = pygame.transform.flip(image, True, False)
        pixel_fighter.blit_fit(surface, image, inner)
    elif character.get("sprite_asset"):
        sprite_fighter.blit_fit(
            surface,
            sprite_fighter.preview_frame(character["sprite_asset"], facing),
            inner,
        )
    else:
        _draw_preview(surface, inner, character, t, facing=facing)

    name_font = pygame.font.SysFont("Arial", 36, bold=True)
    strip = pygame.Rect(inner.x, inner.bottom + 10, inner.width, name_font.get_height() + 8)
    pygame.draw.rect(surface, (0, 0, 0, 160), strip)
    draw_text_fit(
        surface, name_font, character["name"], (255, 255, 255),
        strip.inflate(-8, -4),
    )


def run_vs_screen(screen, clock, p1_key, p2_key,
                  p1_label="PLAYER 1", p2_label="PLAYER 2",
                  stage_key="sunset"):
    """
    Show the VS screen. Blocking loop. Returns "start" or None.
    """
    ch1 = character_data.get(p1_key)
    ch2 = character_data.get(p2_key)

    title_font = pygame.font.SysFont("Arial", 34, bold=True)
    vs_font = pygame.font.SysFont("Arial", 120, bold=True)
    hint_font = pygame.font.SysFont("Arial", 22, bold=True)
    small_font = pygame.font.SysFont("Arial", 18, bold=True)

    total_frames = 60
    frame = 0

    while True:
        frame += 1
        t = pygame.time.get_ticks() / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return "start"

        # Side rects
        side_w = int(settings.WINDOW_WIDTH * 0.34)
        side_h = int(settings.WINDOW_HEIGHT * 0.62)
        side_y = (settings.WINDOW_HEIGHT - side_h) // 2 - 20
        left_rect = pygame.Rect(30, side_y, side_w, side_h)
        right_rect = pygame.Rect(settings.WINDOW_WIDTH - side_w - 30,
                                 side_y, side_w, side_h)

        # Background
        screen.fill((10, 10, 24))
        for y in range(0, settings.WINDOW_HEIGHT, 6):
            shade = 10 + int(y * 0.03)
            pygame.draw.rect(screen, (shade, shade // 2, shade + 20),
                             (0, y, settings.WINDOW_WIDTH, 6))

        # Slide-in: first 30 frames
        p = easing.ease_out_cubic(min(1.0, frame / 30))
        offset = int((1.0 - p) * 400)
        left_pos = left_rect.move(-offset, 0)
        right_pos = right_rect.move(offset, 0)

        _draw_side(screen, left_pos, ch1, t, facing=1, side="left")
        _draw_side(screen, right_pos, ch2, t, facing=-1, side="right")

        # Player labels above portraits
        for (label, rect, color) in (
            (p1_label, left_pos, (255, 240, 120)),
            (p2_label, right_pos, (255, 240, 120)),
        ):
            label_rect = pygame.Rect(
                rect.left + 8, rect.top - 58, rect.width - 16, 50
            )
            draw_text_fit(screen, title_font, label, color, label_rect)

        # VS in the middle
        vs_color = (255, 60, 60)
        vs_img = vs_font.render("VS", True, vs_color)
        # Pulse
        pulse = 1.0 + 0.08 * math.sin(t * 4.0)
        vs_scaled = pygame.transform.smoothscale(
            vs_img,
            (int(vs_img.get_width() * pulse),
             int(vs_img.get_height() * pulse)))
        vs_outline = vs_font.render("VS", True, (0, 0, 0))
        vs_rect = vs_scaled.get_rect(center=(settings.WINDOW_WIDTH // 2,
                                             settings.WINDOW_HEIGHT // 2))
        for dx in (-4, 0, 4):
            for dy in (-4, 0, 4):
                if dx == 0 and dy == 0:
                    continue
                screen.blit(vs_outline,
                            (vs_rect.x + dx, vs_rect.y + dy))
        screen.blit(vs_scaled, vs_rect)

        # Stage name at bottom
        draw_text_fit(
            screen, small_font, "STAGE: " + stage_key.upper(),
            (200, 220, 255),
            pygame.Rect(40, settings.WINDOW_HEIGHT - 108,
                        settings.WINDOW_WIDTH - 80, 36),
        )

        # Hint
        if frame > 30:
            alpha = min(255, int(255 * easing.ease_out_cubic((frame - 30) / 30)))
            draw_text_fit(
                screen, hint_font, "PRESS ENTER TO BEGIN", (255, 255, 255),
                pygame.Rect(40, settings.WINDOW_HEIGHT - 62,
                            settings.WINDOW_WIDTH - 80, 40),
                alpha=alpha,
            )

        pygame.display.flip()
        clock.tick(settings.FPS)

# ui/transitions.py
import math
from functools import lru_cache
import pygame
from ui import retro, theme
import settings
from effects import easing


def _center_text(surface, font, text, y, color, alpha=255):
    theme.bold_text(
        surface, font, text, color,
        pygame.Rect(30, y - font.get_height() // 2,
                    settings.WINDOW_WIDTH - 60, font.get_height()),
        alpha=alpha, weight=1,
    )


@lru_cache(maxsize=24)
def _impact_letters(text, color, size):
    face = retro.font(size=size).render(text, False, (255, 255, 255))
    image = pygame.Surface((face.get_width() + 58, face.get_height() + 58), pygame.SRCALPHA)
    dark = face.copy()
    dark.fill((4, 11, 27), special_flags=pygame.BLEND_RGBA_MULT)
    for x, y in ((14, 24), (26, 24), (20, 18), (20, 30)):
        image.blit(dark, (x, y))
    shade = face.copy()
    shade.fill((151, 67, 34), special_flags=pygame.BLEND_RGBA_MULT)
    for depth in range(16, 0, -2):
        image.blit(shade, (18 + depth, 18 + depth))
    outline = face.copy()
    outline.fill((255, 247, 218), special_flags=pygame.BLEND_RGBA_MULT)
    for dx, dy in ((-4, 0), (4, 0), (0, -4), (0, 4)):
        image.blit(outline, (18 + dx, 18 + dy))
    gradient = pygame.Surface(face.get_size(), pygame.SRCALPHA)
    for y in range(face.get_height()):
        amount = y / max(1, face.get_height() - 1)
        shade = tuple(round(255 * (1 - amount) + c * amount) for c in color)
        pygame.draw.line(gradient, shade, (0, y), (face.get_width(), y))
    gradient.blit(face, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    image.blit(gradient, (18, 18))
    return image


def _hero_text(surface, text, progress, y, color, size=144):
    if progress <= 0:
        return
    image = _impact_letters(text, tuple(color), size)
    scale = max(.05, easing.ease_out_back(min(1, progress / .28), overshoot=1.25))
    scale = min(scale, (surface.get_width() - 100) / image.get_width())
    image = pygame.transform.scale(image, (max(1, round(image.get_width() * scale)),
                                          max(1, round(image.get_height() * scale))))
    shake = round(math.sin(progress * 110) * max(0, 1 - progress / .15) * 8)
    surface.blit(image, image.get_rect(center=(surface.get_width() // 2 + shake, y)))


def _backdrop(surface, progress, center_y, color, celebration=False):
    width, height = surface.get_size()
    amount = easing.ease_out_cubic(progress)
    layer = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    layer.fill((4, 12, 28, round(165 * amount)))
    center = (width // 2, center_y)
    for index in range(14):
        angle = index * math.tau / 14 + progress * .18
        radius = width * .72
        points = [center]
        points += [(center[0] + math.cos(a) * radius, center[1] + math.sin(a) * radius)
                   for a in (angle, angle + .055)]
        pygame.draw.polygon(layer, (*color, round(26 * amount)), points)
    slide = round((1 - easing.ease_out_cubic(min(1, progress / .2))) * width)
    left, right = width // 2 - 475 - slide, width // 2 + 475 - slide
    points = ((left + 35, center_y - 90), (right, center_y - 90),
              (right - 35, center_y + 90), (left, center_y + 90))
    pygame.draw.polygon(layer, (13, 30, 50, 225), points)
    pygame.draw.polygon(layer, (*color, 235), points, 3)
    surface.blit(layer, (0, 0))
    seconds = pygame.time.get_ticks() / 1000 if celebration else progress * 2.8
    for index in range(48):
        if celebration:
            x = (index * 127 + math.sin(seconds + index) * 27) % width
            y = (index * 61 + seconds * (32 + index % 5 * 7)) % height
        else:
            angle = index * 2.399
            distance = 80 + seconds * (55 + index % 7 * 17)
            x = center[0] + math.cos(angle) * distance
            y = center[1] + math.sin(angle) * distance * .6 + seconds * seconds * 14
        c = (255, 247, 201) if index % 3 == 0 else color
        pygame.draw.rect(surface, c, (round(x), round(y), 3 + index % 3, 3 if index % 2 else 6))
    # One brief impact flash as the KO lands, followed by a sustained display.
    if 0 < progress < .07:
        flash = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        flash.fill((255, 242, 190, round(75 * (1 - progress / .07))))
        surface.blit(flash, (0, 0))


def _crown(surface, y, progress):
    x = surface.get_width() // 2
    y += round(math.sin(pygame.time.get_ticks() / 500) * 3)
    points = ((x - 51, y + 33), (x - 60, y - 11), (x - 28, y + 7),
              (x, y - 30), (x + 28, y + 7), (x + 60, y - 11), (x + 51, y + 33))
    pygame.draw.polygon(surface, (5, 13, 29), points, 8)
    pygame.draw.polygon(surface, theme.GOLD, points)
    pygame.draw.line(surface, (255, 246, 198), (x - 48, y + 26), (x + 48, y + 26), 5)
    pygame.draw.rect(surface, theme.BLUE, (x - 7, y + 4, 14, 14))


def draw_countdown(surface, round_number, progress, fonts):
    overlay = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
    overlay.set_alpha(160)
    overlay.fill(theme.NAVY)
    surface.blit(overlay, (0, 0))

    big_font = fonts["big"]
    huge_font = fonts["huge"]

    if progress < 0.70:
        p = easing.ease_out_cubic(progress / 0.70)
        combined = "ROUND " + str(round_number)
        img = big_font.render(combined, True, theme.GOLD)
        start_x = settings.WINDOW_WIDTH // 2 - 500
        end_x = settings.WINDOW_WIDTH // 2
        cx = easing.lerp(start_x, end_x, p)
        r = img.get_rect(center=(cx, settings.WINDOW_HEIGHT // 2 - 30))
        surface.blit(img, r)
    else:
        p = (progress - 0.70) / 0.30
        scale = easing.ease_out_back(p, overshoot=1.6)
        img = huge_font.render("FIGHT!", True, theme.GOLD)
        base_size = img.get_size()
        scaled = pygame.transform.scale(
            img, (int(base_size[0] * scale), int(base_size[1] * scale)))
        r = scaled.get_rect(center=(settings.WINDOW_WIDTH // 2,
                                    settings.WINDOW_HEIGHT // 2))
        surface.blit(scaled, r)


def draw_round_over(surface, winner, round_end_reason, progress, fonts, winner_name=None):
    progress = easing.clamp01(progress)
    color = (255, 174, 66) if round_end_reason == 'ko' else theme.BLUE
    _backdrop(surface, progress, 258, color)
    _hero_text(surface, 'K.O.' if round_end_reason == 'ko' else 'TIME UP', progress, 246, color)
    if progress > .25:
        alpha = round(255 * easing.ease_out_cubic((progress - .25) / .4))
        name = winner_name or ('PLAYER 1' if winner == 'p1' else 'PLAYER 2')
        message = f'{name} WINS THE ROUND' if winner in ('p1', 'p2') else 'DRAW ROUND'
        rect = pygame.Rect(surface.get_width() // 2 - 430, 393, 860, 68)
        theme.panel(surface, rect, selected=True)
        theme.bold_text(surface, fonts['big'], message, theme.GOLD, rect.inflate(-24, -10), alpha=alpha)


def draw_match_over(surface, header, rounds_text, progress, fonts,
                    winner_color=None, prompt="ENTER / R = new match     ESC = back to menu"):
    progress = easing.clamp01(progress)
    lost = 'LOSE' in header.upper() or 'BOT WINS' in header.upper()
    color = (119, 198, 255) if lost else theme.GOLD
    _backdrop(surface, progress, 286, color, celebration=not lost)
    if not lost and progress > .12:
        _crown(surface, 140, progress)
    _hero_text(surface, 'DEFEAT' if lost else 'VICTORY!', progress, 276, color, size=116)
    if progress > .25:
        alpha = round(255 * easing.ease_out_cubic((progress - .25) / .45))
        banner = pygame.Rect(surface.get_width() // 2 - 470, 405, 940, 77)
        theme.panel(surface, banner, selected=True)
        theme.bold_text(surface, fonts['big'], header, theme.PALE, banner.inflate(-24, -10), alpha=alpha)
        _center_text(surface, fonts['mid'], rounds_text.upper(), 527, theme.GOLD, alpha=alpha)
        _center_text(surface, fonts['small'], prompt.upper(), surface.get_height() - 62, theme.PALE, alpha=alpha)

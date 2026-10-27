"""Night-city arcade presentation shared by the intro, menus, and match HUD."""

import math
from functools import lru_cache

import pygame

from stages import stages
from ui import retro
from ui.text_layout import draw_text_fit


NAVY = (20, 39, 65)
PANEL = (28, 54, 82)
BLUE = (62, 169, 219)
PALE = (212, 234, 247)
GOLD = (255, 213, 113)
MUTED = (163, 192, 218)


def background(surface, elapsed=None, shade=85):
    elapsed = pygame.time.get_ticks() / 1000 if elapsed is None else elapsed
    width, height = surface.get_size()
    skyline = stages._background("City", "city 1", width, height)
    surface.blit(skyline, (-32 + round(math.sin(elapsed * 0.09) * 18), 0))
    # Tiny deterministic stars twinkle rather than flickering randomly per frame.
    for index in range(30):
        x = (index * 193 + 42) % width
        y = (index * 67 + 24) % max(1, height // 2)
        pulse = (math.sin(elapsed * 1.4 + index * 2.1) + 1) / 2
        color = tuple(round(c * (0.45 + pulse * 0.55)) for c in PALE)
        pygame.draw.rect(surface, color, (x, y, 2, 2))
        if pulse > 0.94 and index % 3 == 0:
            pygame.draw.line(surface, color, (x - 3, y + 1), (x + 4, y + 1))
            pygame.draw.line(surface, color, (x + 1, y - 3), (x + 1, y + 4))
    # Slow-moving fireflies bring the foreground to life without obscuring text.
    for index in range(14):
        x = int((index * 151 + elapsed * (5 + index % 4)) % width)
        y = int(height * 0.48 + (index * 41) % max(1, int(height * 0.42))
                + math.sin(elapsed * 0.7 + index) * 12)
        pygame.draw.rect(surface, GOLD if index % 3 == 0 else BLUE, (x, y, 2, 2))
    if shade:
        veil = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        veil.fill((*NAVY, shade))
        surface.blit(veil, (0, 0))


def panel(surface, rect, selected=False):
    rect = pygame.Rect(rect)
    pygame.draw.rect(surface, (10, 24, 43), rect.move(5, 6))
    pygame.draw.rect(surface, PANEL, rect)
    pygame.draw.rect(surface, GOLD if selected else (93, 135, 169), rect, 2)
    pygame.draw.line(surface, PALE, (rect.left + 4, rect.top + 3),
                     (rect.right - 5, rect.top + 3), 1)


@lru_cache(maxsize=16)
def _logo_line(text, size, blue):
    letters = retro.font(size=size).render(text, False, (255, 255, 255))
    # Thicken the letter faces before adding the gold outline and extrusion.
    weight = max(1, round(size / 30))
    mask = pygame.Surface((letters.get_width() + weight * 2,
                           letters.get_height() + weight * 2), pygame.SRCALPHA)
    for dx in range(-weight, weight + 1):
        for dy in range(-weight, weight + 1):
            mask.blit(letters, (weight + dx, weight + dy))
    image = pygame.Surface((mask.get_width() + 20, mask.get_height() + 24), pygame.SRCALPHA)
    silhouette = mask.copy()
    silhouette.fill((15, 45, 74), special_flags=pygame.BLEND_RGBA_MULT)
    for depth in range(12, 2, -2):
        image.blit(silhouette, (depth, depth + 6))
    outline = mask.copy()
    outline.fill(GOLD, special_flags=pygame.BLEND_RGBA_MULT)
    for offset in ((0, 3), (6, 3), (3, 0), (3, 6)):
        image.blit(outline, offset)
    face = pygame.Surface(mask.get_size(), pygame.SRCALPHA)
    start, end = ((104, 214, 247), (23, 131, 189)) if blue else ((255, 250, 212), GOLD)
    for y in range(face.get_height()):
        ratio = y / max(1, face.get_height() - 1)
        color = tuple(round(a + (b - a) * ratio) for a, b in zip(start, end))
        pygame.draw.line(face, color, (0, y), (face.get_width(), y))
    face.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    image.blit(face, (3, 3))
    return image


def logo(surface, elapsed=0.0, y=20):
    bob = round(math.sin(elapsed * 1.2) * 3)
    for text, size, offset, blue in (("PYTHON", 61, 0, False), ("FIGHTERS", 100, 67, True)):
        image = _logo_line(text, size, blue)
        max_width = surface.get_width() - 140
        if image.get_width() > max_width:
            factor = max_width / image.get_width()
            image = pygame.transform.scale(image, (max_width, round(image.get_height() * factor)))
        surface.blit(image, image.get_rect(midtop=(surface.get_width() // 2, y + offset + bob)))


def footer(surface, text="ARROWS / W S: SELECT     ENTER / CLICK: CONFIRM     ESC: BACK"):
    rect = pygame.Rect(0, surface.get_height() - 60, surface.get_width(), 60)
    pygame.draw.rect(surface, (42, 72, 99), rect)
    pygame.draw.line(surface, PALE, rect.topleft, rect.topright, 3)
    pygame.draw.line(surface, (15, 36, 59), (0, rect.bottom - 4), (rect.right, rect.bottom - 4), 3)
    draw_text_fit(surface, retro.font(size=18), text, PALE, rect.inflate(-50, -20))

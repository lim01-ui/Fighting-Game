"""Animated night-city title scene. Any input continues into the arcade lobby."""

import math
import pygame
from ui import retro, theme
from ui.text_layout import draw_text_fit


def _continue_to_menu_event(event):
    kinds = {pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.JOYBUTTONDOWN}
    controller = getattr(pygame, "CONTROLLERBUTTONDOWN", None)
    if controller is not None:
        kinds.add(controller)
    return event.type in kinds


def draw_title(screen, elapsed):
    theme.background(screen, elapsed, shade=20)
    entrance = max(0, 1 - elapsed / 0.85)
    theme.logo(screen, elapsed, y=95 - round(entrance * entrance * 130))
    draw_text_fit(screen, retro.font(size=22), "THE CITY IS AWAKE. ENTER THE ARENA.",
                  theme.PALE, pygame.Rect(110, 330, screen.get_width() - 220, 38))
    pulse = 0.65 + math.sin(elapsed * 3) * 0.35
    color = tuple(round(channel * pulse) for channel in theme.GOLD)
    draw_text_fit(screen, retro.font(size=30), "PRESS ANY KEY TO START", color,
                  pygame.Rect(100, 435, screen.get_width() - 200, 54))
    draw_text_fit(screen, retro.font(size=16), "SOLO ARCADE  /  TRAINING  /  LAN BATTLES",
                  theme.MUTED, pygame.Rect(100, 511, screen.get_width() - 200, 32))
    theme.footer(screen, "ENTER / SPACE / CLICK: START     PYTHON FIGHTERS")


def run_title_video(screen, clock):
    # Keep the entrypoint used by main.py while replacing the old video intro.
    elapsed = 0.0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if _continue_to_menu_event(event):
                return True
        draw_title(screen, elapsed)
        retro.present(screen)
        elapsed += clock.tick(60) / 1000.0

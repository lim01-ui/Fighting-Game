"""Animated night-city title scene. Any input enters the arcade lobby."""

import math
import pygame
from ui import retro, theme


def _continue_to_menu_event(event):
    kinds = {pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN, pygame.JOYBUTTONDOWN}
    controller = getattr(pygame, "CONTROLLERBUTTONDOWN", None)
    if controller is not None:
        kinds.add(controller)
    return event.type in kinds


def draw_title(screen, elapsed):
    theme.background(screen, elapsed, shade=50)
    entrance = max(0, 1 - elapsed / 0.85)
    theme.logo(screen, elapsed, y=95 - round(entrance * entrance * 130))
    theme.bold_text(screen, retro.font(size=25), "16 ARENAS. ONE CHAMPION.",
                    theme.PALE, (80, 330, screen.get_width() - 160, 48))
    prompt = pygame.Rect(screen.get_width() // 2 - 410, 415, 820, 90)
    theme.panel(screen, prompt, selected=True)
    pygame.draw.rect(screen, theme.GOLD, prompt.inflate(round(math.sin(elapsed * 3) * 4), 0), 2)
    theme.bold_text(screen, retro.font(size=38), "PRESS ANY KEY TO START", theme.GOLD,
                    prompt.inflate(-20, -20))
    theme.bold_text(screen, retro.font(size=19), "SOLO ARCADE  /  TRAINING  /  LAN BATTLES",
                    theme.PALE, (90, 525, screen.get_width() - 180, 38), weight=0)
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

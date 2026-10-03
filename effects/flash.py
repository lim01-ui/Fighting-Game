# effects/flash.py
"""
Full-screen color flash. Fades over its life.
Useful for KO frames, super-move impacts, screen freeze moments.
"""

import pygame
import settings


class Flash:
    def __init__(self, color=(255, 255, 255), life=12, max_alpha=220):
        self.color = color
        self.life = life
        self.max_life = life
        self.max_alpha = max_alpha

    def update(self):
        self.life -= 1
        return self.life <= 0

    def draw(self, surface):
        ratio = max(0.0, self.life / self.max_life)
        alpha = int(self.max_alpha * ratio)
        s = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT),
                           pygame.SRCALPHA)
        s.fill((*self.color, alpha))
        surface.blit(s, (0, 0))

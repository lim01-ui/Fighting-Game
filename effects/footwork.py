"""Bounded, visual-only landing dust and movement trails."""
import pygame
import settings


class Footwork:
    def __init__(self):
        self.previous = {}
        self.dust = []
        self.frame = 0
        self.layer = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), pygame.SRCALPHA)

    def update(self, fighters):
        self.frame += 1
        self.dust = [(x, y, age + 1, strength) for x, y, age, strength in self.dust if age < 17]
        for index, fighter in enumerate(fighters):
            x = fighter.rect.centerx
            last_x, grounded = self.previous.get(index, (x, fighter.on_ground))
            moved = abs(x - last_x)
            landed = fighter.on_ground and not grounded
            if landed or (fighter.on_ground and moved > 2 and self.frame % 5 == 0):
                self.dust.append((x, settings.GROUND_Y, 0, 1.8 if landed else 0.8))
            self.previous[index] = (x, fighter.on_ground)
        self.dust = self.dust[-32:]

    def draw(self, surface):
        self.layer.fill((0, 0, 0, 0))
        for x, y, age, strength in self.dust:
            alpha = int(90 * (1 - age / 18))
            radius = int((8 + age * 2) * strength)
            pygame.draw.ellipse(self.layer, (220, 218, 210, alpha), (int(x) - radius, int(y) - 5 - age // 3, radius * 2, 8 + age // 3), 2)
            for direction in (-1, 1):
                px = int(x + direction * age * 2 * strength)
                pygame.draw.circle(self.layer, (220, 218, 210, alpha // 2), (px, int(y) - 4 - age // 2), max(1, 5 - age // 4))
        surface.blit(self.layer, (0, 0))

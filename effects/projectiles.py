# effects/projectiles.py
"""Simple projectiles for special moves."""

import math
import pygame
import settings


class Projectile:
    def __init__(self, x, y, vx, owner_facing, color, kind="orb",
                 damage=10, hitstun=20, owner=None, vy=0):
        self.x = float(x)
        self.y = float(y)
        self.vx = vx * owner_facing
        self.vy = float(vy)
        self.owner = owner
        self.color = color
        self.kind = kind
        self.damage = damage
        self.hitstun = hitstun
        self.life = 90
        self.radius = 12 if kind == "orb" else 8
        self.rect = pygame.Rect(x - self.radius, y - self.radius,
                                self.radius * 2, self.radius * 2)
        self.trail = []

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 8:
            self.trail.pop(0)
        self.x += self.vx
        self.y += self.vy
        self.rect.x = int(self.x - self.radius)
        self.rect.y = int(self.y - self.radius)
        self.life -= 1
        return self.life <= 0 or self.x < -50 or self.x > settings.WINDOW_WIDTH + 50

    def draw(self, surface):
        # Trail behind the projectile
        for i, (tx, ty) in enumerate(self.trail):
            a = int(200 * (i / max(1, len(self.trail))))
            r = max(2, self.radius - (len(self.trail) - i))
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, a), (r, r), r)
            surface.blit(s, (int(tx) - r, int(ty) - r))
        if self.kind == "orb":
            pygame.draw.circle(surface, (20, 20, 30),
                               (int(self.x), int(self.y)), self.radius + 3)
            pygame.draw.circle(surface, self.color,
                               (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(surface, (255, 255, 255),
                               (int(self.x), int(self.y)), self.radius // 2)
        elif self.kind == "knife":
            # Small spinning blade
            ang = self.life * 0.4
            a = math.radians(ang)
            tip_x = self.x + math.cos(a) * 12
            tip_y = self.y + math.sin(a) * 12
            pygame.draw.line(surface, (20, 20, 30),
                             (self.x - math.cos(a) * 12, self.y - math.sin(a) * 12),
                             (tip_x, tip_y), 6)
            pygame.draw.line(surface, self.color,
                             (self.x - math.cos(a) * 12, self.y - math.sin(a) * 12),
                             (tip_x, tip_y), 3)
        elif self.kind == "spark":
            for i in range(4):
                a = i * math.pi / 2 + self.life * 0.2
                x1 = self.x + math.cos(a) * 4
                y1 = self.y + math.sin(a) * 4
                x2 = self.x + math.cos(a) * 12
                y2 = self.y + math.sin(a) * 12
                pygame.draw.line(surface, self.color, (x1, y1), (x2, y2), 3)
            pygame.draw.circle(surface, (255, 255, 255),
                               (int(self.x), int(self.y)), 4)

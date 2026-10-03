# effects/hit_spark.py
"""
A simple particle burst — used as a hit spark when attacks connect.

Each spark is a list of small particles that fly outward from a point
and fade over time. The spark removes itself when all particles are gone.
"""

import random
import math
import pygame


class HitSpark:
    def __init__(self, x, y, color, count=14, speed=6, life=14):
        self.x = x
        self.y = y
        self.color = color
        self.speed = speed
        self.life = life
        self.max_life = life
        self.particles = []
        for _ in range(count):
            angle = random.uniform(0, math.tau)
            spd = random.uniform(speed * 0.4, speed)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            size = random.randint(2, 5)
            self.particles.append([x, y, vx, vy, size])

    def update(self):
        """Advance one frame. Returns True when finished."""
        self.life -= 1
        for p in self.particles:
            p[0] += p[2]
            p[1] += p[3]
            p[2] *= 0.92   # drag
            p[3] *= 0.92
            p[3] += 0.3    # slight gravity
        return self.life <= 0

    def draw(self, surface):
        ratio = max(0.0, self.life / self.max_life)
        alpha = int(255 * ratio)

        # An expanding ring and sharp rays make heavy impacts read at a glance.
        radius = int((1.0 - ratio) * (self.speed * 4 + 14))
        if radius > 0:
            diameter = radius * 2 + 4
            ring = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
            pygame.draw.circle(
                ring, (*self.color, alpha), (diameter // 2, diameter // 2),
                radius, max(1, int(4 * ratio)),
            )
            surface.blit(ring, (int(self.x) - diameter // 2,
                                int(self.y) - diameter // 2))
            if self.speed >= 8:
                ray_color = tuple(int(channel * ratio) for channel in self.color)
                for angle in range(0, 360, 45):
                    inner = radius + 4
                    outer = radius + 14
                    start = (int(self.x + math.cos(math.radians(angle)) * inner),
                             int(self.y + math.sin(math.radians(angle)) * inner))
                    end = (int(self.x + math.cos(math.radians(angle)) * outer),
                           int(self.y + math.sin(math.radians(angle)) * outer))
                    pygame.draw.line(surface, ray_color, start, end, 2)

        for (px, py, _vx, _vy, size) in self.particles:
            # Cheap alpha: draw a smaller circle as life fades
            r = max(1, int(size * ratio))
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (r, r), r)
            surface.blit(s, (int(px) - r, int(py) - r))

        # Bright core flash for the first few frames
        if self.life > self.max_life - 4:
            core = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(core, (255, 255, 255, 180), (20, 20), 16)
            surface.blit(core, (int(self.x) - 20, int(self.y) - 20))


class BlockSpark:
    """A different visual for blocks — small blue shield-ish arcs."""

    def __init__(self, x, y, life=10):
        self.x = x
        self.y = y
        self.life = life
        self.max_life = life

    def update(self):
        self.life -= 1
        return self.life <= 0

    def draw(self, surface):
        ratio = max(0.0, self.life / self.max_life)
        r = int(30 * (1.0 - ratio) + 10)
        alpha = int(200 * ratio)
        s = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
        pygame.draw.circle(s, (140, 210, 255, alpha), (r + 4, r + 4), r, 3)
        surface.blit(s, (int(self.x) - r - 4, int(self.y) - r - 4))

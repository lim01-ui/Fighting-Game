# effects/projectiles.py
"""Simple projectiles for special moves."""

import math
import pygame
import settings
from effects import sprite_effect


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
        if self.kind in ("orb", "spark"):
            effect = 2 if self.kind == "orb" else 4
            progress = ((90 - self.life) % 16) / 16
            facing = 1 if self.vx >= 0 else -1
            for index, (tx, ty) in enumerate(self.trail[::3]):
                sprite_effect.draw(surface, effect, tx, ty, progress, size=32,
                                   facing=facing, alpha=45 + index * 25)
            sprite_effect.draw(surface, effect, self.x, self.y, progress,
                               size=64, facing=facing)
            return
        # Trail behind the projectile
        for i, (tx, ty) in enumerate(self.trail):
            a = int(200 * (i / max(1, len(self.trail))))
            r = max(2, self.radius - (len(self.trail) - i))
            s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, a), (r, r), r)
            surface.blit(s, (int(tx) - r, int(ty) - r))
        if self.kind == "knife":
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
        elif self.kind == "arrow":
            arrow_img = _get_arrow_sprite()
            if arrow_img is not None:
                # The arrow image points East (right).
                angle = -math.degrees(math.atan2(self.vy, self.vx))
                rotated = pygame.transform.rotate(arrow_img, angle)
                r = rotated.get_rect(center=(int(self.x), int(self.y)))
                surface.blit(rotated, r)
            else:
                # Fallback vector arrow
                angle = math.atan2(self.vy, self.vx)
                tip_x = self.x + math.cos(angle) * 18
                tip_y = self.y + math.sin(angle) * 18
                tail_x = self.x - math.cos(angle) * 18
                tail_y = self.y - math.sin(angle) * 18
                pygame.draw.line(surface, (230, 230, 240), (tail_x, tail_y), (tip_x, tip_y), 4)
                pygame.draw.circle(surface, self.color, (int(tip_x), int(tip_y)), 4)


_arrow_sprite = None

def _get_arrow_sprite():
    global _arrow_sprite
    if _arrow_sprite is None:
        from pathlib import Path
        p = Path(__file__).resolve().parent.parent / "assets" / "characters" / "Minamoto" / "minamoto_Arrow.png"
        if p.exists():
            try:
                _arrow_sprite = pygame.image.load(str(p)).convert_alpha()
            except Exception:
                _arrow_sprite = None
    return _arrow_sprite


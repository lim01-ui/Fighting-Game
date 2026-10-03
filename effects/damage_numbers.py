# effects/damage_numbers.py
import pygame
import settings


def _color_for_damage(dmg, blocked=False):
    if blocked:
        return (170, 200, 230)
    if dmg >= 20:
        return (255, 70, 70)
    if dmg >= 13:
        return (255, 150, 50)
    if dmg >= 6:
        return (255, 220, 80)
    return (255, 255, 255)


class DamageNumber:
    def __init__(self, x, y, value, blocked=False, style="chunky"):
        self.x = float(x)
        self.y = float(y)
        self.value = int(value)
        self.style = style
        self.blocked = blocked
        self.life = 40 if style == "chunky" else 28
        self.max_life = self.life
        self.vy = -0.9 if style == "chunky" else -0.6
        self.vx = 0.0
        self.pop = 0.0
        self.color = _color_for_damage(self.value, blocked)
        if style == "chunky":
            self.font = pygame.font.SysFont("Arial", 34, bold=True)
            self.outline_thickness = 3
        else:
            self.font = pygame.font.SysFont("Arial", 20, bold=True)
            self.outline_thickness = 1

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy *= 0.94
        self.life -= 1
        self.pop = min(1.0, self.pop + 0.25)
        return self.life <= 0

    def draw(self, surface):
        ratio = self.life / self.max_life
        alpha = int(255 * min(1.0, ratio * 1.6))
        if self.style == "chunky":
            scale = 1.0 + 0.4 * (1.0 - self.pop)
        else:
            scale = 1.0
        base = self.font.render(str(self.value), True, self.color)
        if scale != 1.0:
            w = max(1, int(base.get_width() * scale))
            h = max(1, int(base.get_height() * scale))
            base = pygame.transform.smoothscale(base, (w, h))
        if self.outline_thickness > 0 and self.style == "chunky":
            outline_surf = self.font.render(str(self.value), True, (0, 0, 0))
            if scale != 1.0:
                outline_surf = pygame.transform.smoothscale(
                    outline_surf,
                    (int(outline_surf.get_width() * scale),
                     int(outline_surf.get_height() * scale)))
            outline_surf.set_alpha(alpha)
            ox, oy = base.get_rect(center=(int(self.x), int(self.y))).topleft
            for dx in (-self.outline_thickness, 0, self.outline_thickness):
                for dy in (-self.outline_thickness, 0, self.outline_thickness):
                    if dx == 0 and dy == 0:
                        continue
                    surface.blit(outline_surf, (ox + dx, oy + dy))
        base.set_alpha(alpha)
        rect = base.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(base, rect)


def spawn(numbers_list, x, y, value, blocked=False):
    style = "small" if (blocked or value <= 5) else "chunky"
    numbers_list.append(DamageNumber(x, y, value, blocked=blocked, style=style))

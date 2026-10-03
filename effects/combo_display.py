# effects/combo_display.py
import pygame
import settings


def _style_for_hits(hits):
    if hits >= 10:
        return {"size": 78, "color": (255, 60, 60)}
    if hits >= 7:
        return {"size": 64, "color": (255, 140, 40)}
    if hits >= 4:
        return {"size": 52, "color": (255, 220, 60)}
    return {"size": 40, "color": (255, 255, 255)}


class ComboDisplay:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hits = 0
        self.damage = 0
        self.best_hits = 0
        self.displayed_hits = 0
        self.pop = 0.0
        self.frames_since_hit = 999
        self.visible = False

    def register_hit(self, damage=0):
        self.hits += 1
        self.damage += damage
        self.best_hits = max(self.best_hits, self.hits)
        self.frames_since_hit = 0
        self.pop = 1.0
        self.visible = True

    def reset(self):
        self.hits = 0
        self.damage = 0
        self.displayed_hits = 0
        self.visible = False
        self.frames_since_hit = 999

    def update(self):
        if not self.visible:
            return
        self.frames_since_hit += 1
        if self.pop > 0:
            self.pop = max(0.0, self.pop - 0.12)
        if self.frames_since_hit > settings.COMBO_WINDOW_FRAMES:
            self.reset()
            return
        if self.displayed_hits != self.hits:
            self.displayed_hits = self.hits

    def draw(self, surface):
        if not self.visible or self.hits < settings.COMBO_MIN_DISPLAY:
            return
        style = _style_for_hits(self.hits)
        size = style["size"]
        color = style["color"]

        scale = 1.0 + 0.35 * self.pop
        big_font = pygame.font.SysFont("Arial", int(size * scale), bold=True)
        small_font = pygame.font.SysFont("Arial", int(20 * scale), bold=True)

        big_text = "{} HIT".format(self.hits)
        label_text = f"{self.damage} DAMAGE"

        big_img = big_font.render(big_text, True, color)
        label_img = small_font.render(label_text, True, color)

        cx = self.x
        cy = self.y

        outline_thickness = 3
        outline_img = big_font.render(big_text, True, (0, 0, 0))
        rect = big_img.get_rect(center=(cx, cy))
        for dx in (-outline_thickness, 0, outline_thickness):
            for dy in (-outline_thickness, 0, outline_thickness):
                if dx == 0 and dy == 0:
                    continue
                surface.blit(outline_img, (rect.x + dx, rect.y + dy))
        surface.blit(big_img, rect)

        label_rect = label_img.get_rect(center=(cx, cy + int(size * 0.8)))
        label_outline = small_font.render(label_text, True, (0, 0, 0))
        for dx in (-2, 0, 2):
            for dy in (-2, 0, 2):
                if dx == 0 and dy == 0:
                    continue
                surface.blit(label_outline, (label_rect.x + dx, label_rect.y + dy))
        surface.blit(label_img, label_rect)

# effects/special_moves.py
"""
Per-character special-move visuals.

Each special is a short-lived effect that appears when a special move
reaches its active phase. Effects draw themselves and expire.

SpecialEffect selects an imported sprite animation for each move kind.
"""

import pygame
from ui import retro
from effects import sprite_effect


class UltimatePresentation:
    def __init__(self, x, y, color, fighter_name, ultimate_name,
                 effect_kind="aura", duration=42):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.fighter_name = fighter_name
        self.ultimate_name = ultimate_name
        self.effect_kind = effect_kind
        self.life = duration
        self.max_life = duration
        self.title_font = retro.font("Arial", 42, bold=True)
        self.label_font = retro.font("Arial", 17, bold=True)

    def update(self):
        self.life -= 1
        return self.life <= 0

    def draw(self, surface, offset=(0, 0)):
        progress = 1 - self.life / self.max_life
        fade_in = min(1.0, progress / 0.16)
        fade_out = min(1.0, (1 - progress) / 0.22)
        envelope = max(0.0, min(fade_in, fade_out))
        flash = max(0.0, 1.0 - abs(progress - 0.12) / 0.12)
        center_x = int(self.x + offset[0])
        center_y = int(self.y + offset[1])

        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((3, 5, 18, int(100 * envelope + 90 * flash)))
        surface.blit(overlay, (0, 0))
        sprite_effect.draw(
            surface, 1, center_x, center_y, progress, size=280,
            alpha=int(255 * envelope),
        )

        banner_width = min(880, surface.get_width() - 80)
        banner_height = 92
        banner_y = int(180 - 28 * (1 - envelope))
        banner = pygame.Surface((banner_width, banner_height), pygame.SRCALPHA)
        banner.fill((5, 8, 20, int(205 * envelope)))
        pygame.draw.rect(
            banner, (*self.color, int(235 * envelope)),
            banner.get_rect(), width=2,
        )
        pygame.draw.line(
            banner, (255, 255, 255, int(170 * envelope)),
            (16, 3), (banner_width - 16, 3), 1,
        )
        surface.blit(
            banner,
            banner.get_rect(center=(surface.get_width() // 2,
                                    banner_y + banner_height // 2)),
        )
        label = self.label_font.render(
            f"{self.fighter_name}  /  ULTIMATE", True, self.color
        )
        label.set_alpha(int(255 * envelope))
        title = self.title_font.render(
            self.ultimate_name, True, (255, 245, 210)
        )
        max_title_width = banner_width - 36
        if title.get_width() > max_title_width:
            title = pygame.transform.scale(
                title,
                (max_title_width, max(1, int(
                    title.get_height() * max_title_width / title.get_width()
                ))),
            )
        title.set_alpha(int(255 * envelope))
        banner_center = banner_y + banner_height // 2
        surface.blit(label, label.get_rect(
            center=(surface.get_width() // 2, banner_center - 22)
        ))
        surface.blit(title, title.get_rect(
            center=(surface.get_width() // 2, banner_center + 17)
        ))


class SpecialEffect:
    """Use the new strips for each move while preserving its lifetime and facing."""

    def __init__(self, kind, x, y, facing, color, duration=24):
        self.kind = kind
        self.x, self.y = float(x), float(y)
        self.facing = facing
        self.color = color
        self.life = self.max_life = duration

    def update(self):
        self.life -= 1
        return self.life <= 0

    def draw(self, surface):
        if self.life <= 0:
            return
        progress = 1 - self.life / self.max_life
        slash_kinds = {"slash", "double_slash", "whip_arc", "spear_streak", "afterimage", "spin_kick", "knife_fan"}
        if self.kind in slash_kinds:
            effect, size = 3, 156
            x = self.x + self.facing * 36
        elif self.kind in {"shockwave", "meteor_burst", "leafburst"}:
            effect, size, x = 1, 200, self.x
        elif self.kind in {"aura", "void_ring", "orb", "nova_orbit"}:
            effect, size, x = 2, 172, self.x
        else:
            effect, size, x = 4, 156, self.x
        sprite_effect.draw(surface, effect, x, self.y, progress,
                           size=size, facing=self.facing)
        if self.kind == "double_slash":
            sprite_effect.draw(surface, 3, x + self.facing * 28, self.y + 16,
                               progress, size=132, facing=-self.facing)

# effects/special_moves.py
"""
Per-character special-move visuals.

Each special is a short-lived effect that appears when a special move
reaches its active phase. Effects draw themselves and expire.

A single SpecialEffect class handles all 12 kinds, switching on `kind`.
"""

import math
import random
import pygame


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
        self.title_font = pygame.font.SysFont("Arial", 42, bold=True)
        self.label_font = pygame.font.SysFont("Arial", 17, bold=True)

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
        ray_alpha = int(115 * envelope)
        for index in range(20):
            angle = index * math.tau / 20 + progress * 0.48
            end = (
                center_x + math.cos(angle) * surface.get_width(),
                center_y + math.sin(angle) * surface.get_height(),
            )
            pygame.draw.line(
                overlay, (*self.color, ray_alpha),
                (center_x, center_y), end, 3 if index % 3 == 0 else 1,
            )
        bar_height = int(48 * envelope)
        pygame.draw.rect(overlay, (2, 3, 10, int(235 * envelope)),
                         (0, 0, surface.get_width(), bar_height))
        pygame.draw.rect(
            overlay, (2, 3, 10, int(235 * envelope)),
            (0, surface.get_height() - bar_height,
             surface.get_width(), bar_height),
        )
        pygame.draw.line(
            overlay, (*self.color, int(205 * envelope)),
            (0, bar_height), (surface.get_width(), bar_height), 2,
        )
        pygame.draw.line(
            overlay, (*self.color, int(205 * envelope)),
            (0, surface.get_height() - bar_height),
            (surface.get_width(), surface.get_height() - bar_height), 2,
        )
        ring_radius = max(1, int(28 + progress * 225))
        ring_surface = pygame.Surface(
            (ring_radius * 2 + 12, ring_radius * 2 + 12), pygame.SRCALPHA
        )
        ring_alpha = int(230 * envelope + 25 * flash)
        pygame.draw.circle(
            ring_surface, (*self.color, ring_alpha),
            (ring_radius + 6, ring_radius + 6), ring_radius,
            max(2, int(14 * (1 - progress))),
        )
        pygame.draw.circle(
            ring_surface, (255, 255, 255, int(ring_alpha * 0.8)),
            (ring_radius + 6, ring_radius + 6), max(1, ring_radius - 9), 2,
        )
        ellipse_rect = pygame.Rect(
            ring_radius // 3, ring_radius * 2 // 3,
            ring_radius * 4 // 3, ring_radius * 2 // 3,
        )
        pygame.draw.ellipse(
            ring_surface, (*self.color, int(ring_alpha * 0.75)),
            ellipse_rect, 3,
        )
        surface.blit(
            ring_surface,
            (center_x - ring_radius - 6, center_y - ring_radius - 6),
        )

        orbit_radius = 62 + int(26 * math.sin(progress * math.pi))
        orbit_direction = -1 if self.effect_kind in ("void_ring", "afterimage") else 1
        for index in range(10):
            angle = progress * orbit_direction * 8 + index * math.tau / 10
            px = center_x + math.cos(angle) * orbit_radius
            py = center_y + math.sin(angle) * orbit_radius * 0.68
            tip = 8 + (index % 3) * 3
            shard = [
                (px + math.cos(angle) * tip, py + math.sin(angle) * tip),
                (px + math.cos(angle + 2.2) * tip * 0.55,
                 py + math.sin(angle + 2.2) * tip * 0.55),
                (px + math.cos(angle - 2.2) * tip * 0.55,
                 py + math.sin(angle - 2.2) * tip * 0.55),
            ]
            pygame.draw.polygon(overlay, (*self.color, int(245 * envelope)), shard)
            pygame.draw.circle(overlay, (255, 255, 255, int(220 * envelope)),
                               (int(px), int(py)), 2)
        surface.blit(overlay, (0, 0))

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
            title = pygame.transform.smoothscale(
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
    def __init__(self, kind, x, y, facing, color, duration=24):
        self.kind = kind
        self.x = float(x)
        self.y = float(y)
        self.facing = facing
        self.color = color
        self.life = duration
        self.max_life = duration
        self.particles = []
        self._seed_particles()

    def _seed_particles(self):
        if self.kind == "shockwave":
            for _ in range(20):
                a = random.uniform(0, math.tau)
                spd = random.uniform(3, 8)
                self.particles.append([self.x, self.y + 20,
                                       math.cos(a) * spd,
                                       math.sin(a) * spd * 0.4,
                                       random.randint(2, 5)])
        elif self.kind == "leafburst":
            for _ in range(16):
                a = random.uniform(0, math.tau)
                spd = random.uniform(2, 6)
                self.particles.append([self.x, self.y,
                                       math.cos(a) * spd,
                                       math.sin(a) * spd,
                                       random.randint(2, 4)])
        elif self.kind in {"arcane_burst", "nova_orbit", "prismatic_wave",
                           "void_ring", "meteor_burst", "crystal_wave"}:
            for _ in range(28):
                a = random.uniform(0, math.tau)
                distance = random.uniform(18, 90)
                self.particles.append([
                    self.x + math.cos(a) * distance,
                    self.y + math.sin(a) * distance * 0.7,
                    math.cos(a) * random.uniform(1.6, 4.8),
                    math.sin(a) * random.uniform(1.2, 3.8),
                    random.randint(3, 7),
                ])

    def update(self):
        self.life -= 1
        for p in self.particles:
            p[0] += p[2]
            p[1] += p[3]
            p[2] *= 0.94
            p[3] *= 0.94
            p[3] += 0.3
        return self.life <= 0

    def draw(self, surface):
        r = self.life / self.max_life  # 1.0 -> 0.0

        if self.kind == "slash":
            self._draw_slash(surface, r)

        elif self.kind == "double_slash":
            self._draw_double_slash(surface, r)

        elif self.kind == "shockwave":
            self._draw_shockwave(surface, r)

        elif self.kind == "whip_arc":
            self._draw_whip_arc(surface, r)

        elif self.kind == "aura":
            self._draw_aura(surface, r)

        elif self.kind == "spear_streak":
            self._draw_spear_streak(surface, r)

        elif self.kind == "leafburst":
            self._draw_leafburst(surface, r)

        elif self.kind == "afterimage":
            self._draw_afterimage(surface, r)

        elif self.kind == "spin_kick":
            self._draw_spin_kick(surface, r)

        elif self.kind == "knife_fan":
            self._draw_knife_fan(surface, r)

        elif self.kind in {"arcane_burst", "nova_orbit", "prismatic_wave",
                           "void_ring", "meteor_burst", "crystal_wave"}:
            self._draw_magical_burst(surface, r)

    # ---------- individual renderers ----------
    def _draw_slash(self, surface, r):
        # A wide colored wedge that sweeps forward
        size = int(90 * (1.2 - r * 0.6))
        cx = self.x + self.facing * 30
        color = (*self.color, int(230 * r))
        s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pts = [(size, size - size * 0.9),
               (size + size * 0.9, size),
               (size, size + size * 0.9),
               (size + size * 0.5, size)]
        if self.facing < 0:
            pts = [(2 * size - p[0], p[1]) for p in pts]
        pygame.draw.polygon(s, color, pts)
        pygame.draw.polygon(s, (255, 255, 255, int(180 * r)), pts, 3)
        surface.blit(s, (cx - size, self.y - size))

    def _draw_double_slash(self, surface, r):
        # Two crossed slashes
        size = int(70 * (1.2 - r * 0.5))
        cx = self.x + self.facing * 30
        s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        color = (*self.color, int(220 * r))
        pygame.draw.line(s, color, (size * 0.2, size * 0.2),
                         (size * 1.8, size * 1.8), 12)
        pygame.draw.line(s, color, (size * 0.2, size * 1.8),
                         (size * 1.8, size * 0.2), 12)
        pygame.draw.line(s, (255, 255, 255, int(180 * r)),
                         (size * 0.2, size * 0.2),
                         (size * 1.8, size * 1.8), 4)
        pygame.draw.line(s, (255, 255, 255, int(180 * r)),
                         (size * 0.2, size * 1.8),
                         (size * 1.8, size * 0.2), 4)
        surface.blit(s, (cx - size, self.y - size))

    def _draw_shockwave(self, surface, r):
        # Expanding ring on the ground
        rad = int(30 + (1 - r) * 120)
        width = max(2, int(10 * r))
        alpha = int(230 * r)
        s = pygame.Surface((rad * 2 + 20, rad * 2 + 20), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha),
                           (rad + 10, rad + 10), rad, width)
        pygame.draw.circle(s, (255, 255, 255, int(alpha * 0.6)),
                           (rad + 10, rad + 10), rad - 6, 2)
        surface.blit(s, (self.x - rad - 10, self.y - rad - 10 + 40))

        # Particles
        for (px, py, _, _, size) in self.particles:
            a = int(220 * r)
            ps = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(ps, (*self.color, a), (size, size), size)
            surface.blit(ps, (int(px) - size, int(py) - size))

    def _draw_whip_arc(self, surface, r):
        # A long curving line from the fighter forward
        length = 320
        alpha = int(230 * r)
        color = (*self.color, alpha)
        px, py = self.x + self.facing * 10, self.y
        points = [(px, py)]
        for i in range(1, 14):
            t = i / 13
            tx = px + self.facing * (length * t)
            ty = py + math.sin(t * math.pi) * 40 - 20
            points.append((tx, ty))
        if len(points) >= 2:
            for i in range(len(points) - 1):
                pygame.draw.line(surface, color,
                                 points[i], points[i + 1],
                                 max(2, int(10 * r)))

    def _draw_aura(self, surface, r):
        # Blue/colored glow around the fighter
        rad = int(60 + (1 - r) * 30)
        alpha = int(180 * r)
        s = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
        for i in range(3):
            pygame.draw.circle(s, (*self.color, alpha // 3),
                               (rad, rad), rad - i * 8)
        surface.blit(s, (self.x - rad, self.y - rad))

    def _draw_spear_streak(self, surface, r):
        # A long white streak forward
        length = 220
        alpha = int(240 * r)
        y = self.y
        w = max(2, int(14 * r))
        pygame.draw.line(surface, (*self.color, alpha),
                         (self.x, y),
                         (self.x + self.facing * length, y), w)
        pygame.draw.line(surface, (255, 255, 255, alpha),
                         (self.x, y),
                         (self.x + self.facing * length, y), max(2, w // 3))

    def _draw_leafburst(self, surface, r):
        for (px, py, _, _, size) in self.particles:
            a = int(230 * r)
            ps = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
            # leaf shape as a small ellipse
            pygame.draw.ellipse(ps, (*self.color, a),
                                (0, 0, size * 3, int(size * 1.2)))
            surface.blit(ps, (int(px) - size, int(py) - size))
        # central ring
        rad = int(20 + (1 - r) * 40)
        s = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, int(200 * r)),
                           (rad, rad), rad, max(2, int(8 * r)))
        surface.blit(s, (self.x - rad, self.y - rad))

    def _draw_afterimage(self, surface, r):
        # Ghost strip that trails behind the fighter
        length = 100
        alpha = int(200 * r)
        s = pygame.Surface((length, 100), pygame.SRCALPHA)
        s.fill((*self.color, alpha // 3))
        surface.blit(s, (self.x - self.facing * length // 2,
                         self.y - 50))
        # Fast slash
        size = int(80 * (1.2 - r * 0.5))
        cx = self.x + self.facing * 40
        sl = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.line(sl, (255, 255, 255, alpha),
                         (size, size * 0.2), (size * 1.8, size * 1.5), 8)
        surface.blit(sl, (cx - size, self.y - size))

    def _draw_spin_kick(self, surface, r):
        # A ring of red arcs orbiting the fighter
        rad = int(50 + (1 - r) * 30)
        for i in range(4):
            ang = i * math.pi / 2 + (1 - r) * 6
            x1 = self.x + math.cos(ang) * rad
            y1 = self.y + math.sin(ang) * rad
            x2 = self.x + math.cos(ang) * (rad + 20)
            y2 = self.y + math.sin(ang) * (rad + 20)
            pygame.draw.line(surface, (*self.color, int(230 * r)),
                             (x1, y1), (x2, y2), 6)

    def _draw_knife_fan(self, surface, r):
        # Three knife-lines fanning out
        for offset in (-30, 0, 30):
            a = math.radians(offset)
            ex = self.x + self.facing * math.cos(a) * 90
            ey = self.y + math.sin(a) * 90
            pygame.draw.line(surface, (*self.color, int(230 * r)),
                             (self.x, self.y), (ex, ey), 4)
            pygame.draw.circle(surface, (255, 255, 255),
                               (int(ex), int(ey)), 3)

    def _draw_magical_burst(self, surface, r):
        # Dramatic spell burst with layered rings and particle sparks.
        alpha = int(180 * r)
        ring_radius = int(22 + (1 - r) * 135)
        ring_thickness = max(2, int(12 * r))
        draw_surface = pygame.Surface((ring_radius * 2 + 32, ring_radius * 2 + 32), pygame.SRCALPHA)

        for idx in range(3):
            offset = idx * 8
            pygame.draw.circle(
                draw_surface,
                (*self.color, alpha // (idx + 1)),
                (ring_radius + 16, ring_radius + 16),
                ring_radius - offset,
                ring_thickness,
            )
        for (px, py, _, _, size) in self.particles:
            spark = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
            pygame.draw.circle(spark, (*self.color, alpha), (size + 1, size + 1), size)
            surface.blit(spark, (int(px) - size, int(py) - size))

        glow = pygame.Surface((ring_radius * 3, ring_radius * 3), pygame.SRCALPHA)
        pygame.draw.ellipse(
            glow,
            (*self.color, alpha),
            (ring_radius // 2, ring_radius // 2, ring_radius * 2, ring_radius * 2),
        )
        surface.blit(glow, (self.x - ring_radius * 1.5, self.y - ring_radius * 1.5))
        surface.blit(draw_surface, (self.x - ring_radius - 16, self.y - ring_radius - 16))

# characters/weapons.py
"""
Weapons drawn in each fighter's hand.

Each weapon is drawn from the wrist position, oriented along the forearm
direction. During attacks, the weapon extends forward; during idle it hangs.
"""

import math
import pygame


def draw_weapon(surface, weapon_type, handle_x, handle_y, angle_deg,
                color, handle_color, scale=1.0, trail=None):
    """
    Draw a weapon whose handle is at (handle_x, handle_y), pointing in
    the direction of `angle_deg` (0 = right, 90 = down, -90 = up).

    `trail` is an optional list of previous (angle, tip_x, tip_y) tuples
    used for motion blur (implemented in Phase 7.2).
    """
    a = math.radians(angle_deg)
    dx = math.cos(a)
    dy = math.sin(a)

    def tip(length):
        return handle_x + dx * length * scale, handle_y + dy * length * scale

    def rot(px, py, tx, ty):
        # rotate a 2D point around the handle by the current angle
        cos_a = math.cos(a)
        sin_a = math.sin(a)
        return (int(round(handle_x + px * cos_a - py * sin_a)),
                int(round(handle_y + px * sin_a + py * cos_a)))

    if weapon_type == "sword":
        # Long blade with a crossguard
        tx, ty = tip(46)
        # Handle grip
        hx1, hy1 = rot(-8, 0, 0, 0)
        pygame.draw.line(surface, handle_color, (hx1, hy1),
                         (handle_x, handle_y), 8)
        # Crossguard
        gx1, gy1 = rot(-2, -8, 0, 0)
        gx2, gy2 = rot(-2, 8, 0, 0)
        pygame.draw.line(surface, (40, 40, 50), (gx1, gy1), (gx2, gy2), 6)
        pygame.draw.line(surface, handle_color, (gx1, gy1), (gx2, gy2), 3)
        # Blade
        pygame.draw.line(surface, (20, 20, 30), (handle_x, handle_y),
                         (tx, ty), 10)
        pygame.draw.line(surface, color, (handle_x, handle_y), (tx, ty), 6)
        # Bright edge
        bx, by = tip(44)
        pygame.draw.line(surface, (255, 255, 255), (handle_x, handle_y),
                         (bx, by), 2)

    elif weapon_type == "daggers":
        # Short stubby blades, drawn on one hand but as two
        for offset in (-4, 4):
            ox, oy = rot(-6, offset, 0, 0)
            tx, ty = rot(24, offset, 0, 0)
            pygame.draw.line(surface, (20, 20, 30), (ox, oy), (tx, ty), 8)
            pygame.draw.line(surface, color, (ox, oy), (tx, ty), 5)
            # Handle
            gx, gy = rot(-12, offset, 0, 0)
            pygame.draw.line(surface, handle_color, (gx, gy), (ox, oy), 6)

    elif weapon_type == "hammer":
        # Shaft + big head
        tx, ty = tip(38)
        pygame.draw.line(surface, (20, 20, 30), (handle_x, handle_y),
                         (tx, ty), 12)
        pygame.draw.line(surface, handle_color, (handle_x, handle_y),
                         (tx, ty), 7)
        # Head (big rectangle at the tip)
        hw, hh = 22, 30
        hx, hy = rot(38, 0, 0, 0)
        pts = [rot(38, -hw // 2, 0, 0), rot(38, hw // 2, 0, 0),
               rot(38 + hh, hw // 2, 0, 0), rot(38 + hh, -hw // 2, 0, 0)]
        pts = [rot(38 - (py - handle_y) * 0.0, px - handle_x, 0, 0) for px, py in [(0,0),(0,0),(0,0),(0,0)]]  # placeholder
        # Simpler: draw a circle at the tip
        pygame.draw.circle(surface, (20, 20, 30), (int(hx), int(hy)), 16)
        pygame.draw.circle(surface, color, (int(hx), int(hy)), 13)
        pygame.draw.circle(surface, handle_color, (int(hx), int(hy)), 13, 2)

    elif weapon_type == "whip":
        # Curved length of segments
        seg = 8
        px, py = handle_x, handle_y
        for i in range(10):
            t = i / 9
            nx, ny = tip(60 * t + 6)
            # slight sine wave to fake a whip curve
            wave = math.sin(t * math.pi) * 10
            nx2, ny2 = rot(60 * t + 6, wave, 0, 0)
            pygame.draw.line(surface, (20, 20, 30), (px, py), (nx2, ny2), 6)
            pygame.draw.line(surface, color, (px, py), (nx2, ny2), 3)
            px, py = nx2, ny2

    elif weapon_type == "orb":
        # Small energy sphere floating in the hand
        tx, ty = tip(14)
        pygame.draw.circle(surface, (20, 20, 30), (int(tx), int(ty)), 14)
        pygame.draw.circle(surface, color, (int(tx), int(ty)), 11)
        pygame.draw.circle(surface, (255, 255, 255),
                           (int(tx), int(ty)), 5)

    elif weapon_type == "shield":
        # Rectangular shield strapped to the forearm
        sx, sy = rot(6, 0, 0, 0)
        pts = [rot(0, -14, 0, 0), rot(0, 14, 0, 0),
               rot(30, 14, 0, 0), rot(30, -14, 0, 0)]
        pygame.draw.polygon(surface, (20, 20, 30), pts)
        pygame.draw.polygon(surface, color, pts)
        pygame.draw.polygon(surface, handle_color, pts, 3)

    elif weapon_type == "knives":
        # Single small throwing knife (multiple thrown during attack)
        tx, ty = tip(22)
        pygame.draw.line(surface, (20, 20, 30), (handle_x, handle_y),
                         (tx, ty), 7)
        pygame.draw.line(surface, color, (handle_x, handle_y), (tx, ty), 4)
        # Small blade tip triangle
        bx1, by1 = rot(22, -5, 0, 0)
        bx2, by2 = rot(22, 5, 0, 0)
        bx3, by3 = rot(30, 0, 0, 0)
        blade_tip = [(bx1, by1), (bx2, by2), (bx3, by3)]
        pygame.draw.polygon(surface, (20, 20, 30), blade_tip)
        pygame.draw.polygon(surface, color, blade_tip)

    elif weapon_type == "spear":
        # Long shaft with pointed tip
        tx, ty = tip(64)
        pygame.draw.line(surface, (20, 20, 30), (handle_x, handle_y),
                         (tx, ty), 8)
        pygame.draw.line(surface, handle_color, (handle_x, handle_y),
                         (tx, ty), 5)
        # Tip triangle (each point is a (x,y) tuple)
        p1 = rot(60, -6, 0, 0)
        p2 = rot(60,  6, 0, 0)
        p3 = rot(74,  0, 0, 0)
        pygame.draw.polygon(surface, (20, 20, 30), [p1, p2, p3])
        pygame.draw.polygon(surface, color, [p1, p2, p3])

    elif weapon_type == "club":
        # Thick wooden club with knobby head
        tx, ty = tip(30)
        pygame.draw.line(surface, (20, 20, 30), (handle_x, handle_y),
                         (tx, ty), 14)
        pygame.draw.line(surface, handle_color, (handle_x, handle_y),
                         (tx, ty), 9)
        # Head bulge
        hx, hy = rot(34, 0, 0, 0)
        pygame.draw.circle(surface, (20, 20, 30), (int(hx), int(hy)), 18)
        pygame.draw.circle(surface, color, (int(hx), int(hy)), 15)
        # Knobs
        for ang in (-40, 0, 40):
            kx, ky = rot(34, ang * 0.6, 0, 0)
            pygame.draw.circle(surface, (20, 20, 30), (int(kx), int(ky)), 6)
            pygame.draw.circle(surface, handle_color, (int(kx), int(ky)), 4)

    elif weapon_type == "katana":
        # Long slightly curved blade
        tx, ty = tip(50)
        # Curve the blade a bit by drawing two segments
        mid_x, mid_y = rot(25, 3, 0, 0)
        pygame.draw.line(surface, (20, 20, 30), (handle_x, handle_y),
                         (mid_x, mid_y), 10)
        pygame.draw.line(surface, color, (handle_x, handle_y),
                         (mid_x, mid_y), 6)
        pygame.draw.line(surface, (20, 20, 30), (mid_x, mid_y), (tx, ty), 10)
        pygame.draw.line(surface, color, (mid_x, mid_y), (tx, ty), 6)
        # Bright edge
        ex, ey = rot(48, 4, 0, 0)
        pygame.draw.line(surface, (255, 255, 255), (mid_x, mid_y),
                         (ex, ey), 2)
        # Handle
        hx1, hy1 = rot(-10, 0, 0, 0)
        pygame.draw.line(surface, handle_color, (hx1, hy1),
                         (handle_x, handle_y), 8)
        # Guard
        gx1, gy1 = rot(-4, -8, 0, 0)
        gx2, gy2 = rot(-4, 8, 0, 0)
        pygame.draw.line(surface, (40, 40, 50), (gx1, gy1), (gx2, gy2), 5)

    elif weapon_type == "gauntlets":
        # Chunky fist with a colored plate
        fx, fy = rot(8, 0, 0, 0)
        pygame.draw.circle(surface, (20, 20, 30), (int(fx), int(fy)), 12)
        pygame.draw.circle(surface, color, (int(fx), int(fy)), 9)
        # knuckle plates
        for off in (-6, 0, 6):
            kx, ky = rot(12, off, 0, 0)
            pygame.draw.circle(surface, (255, 255, 255), (int(kx), int(ky)), 3)

    elif weapon_type == "baton":
        # Short rod with an electric tip
        tx, ty = tip(28)
        pygame.draw.line(surface, (20, 20, 30), (handle_x, handle_y),
                         (tx, ty), 10)
        pygame.draw.line(surface, handle_color, (handle_x, handle_y),
                         (tx, ty), 6)
        # Sparking tip
        ex, ey = rot(30, 0, 0, 0)
        pygame.draw.circle(surface, (20, 20, 30), (int(ex), int(ey)), 12)
        pygame.draw.circle(surface, color, (int(ex), int(ey)), 9)
        # Tiny arcs
        for ang in (-45, 45, 135, -135):
            ax1 = ex + math.cos(math.radians(ang)) * 9
            ay1 = ey + math.sin(math.radians(ang)) * 9
            ax2 = ex + math.cos(math.radians(ang)) * 15
            ay2 = ey + math.sin(math.radians(ang)) * 15
            pygame.draw.line(surface, (255, 255, 255),
                             (ax1, ay1), (ax2, ay2), 2)

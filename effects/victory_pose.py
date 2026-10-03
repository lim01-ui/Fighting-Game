# effects/victory_pose.py
"""
Victory and defeat pose overlays.

Used on the match-over screen. Draws the winner in a triumphant pose
(arms raised) and the loser slumped on the ground, using the same
chunky arcade style as Player.draw().
"""

import math
import pygame


def _darken(color, factor=0.5):
    return (int(color[0] * factor), int(color[1] * factor), int(color[2] * factor))


def draw_victor(surface, fighter, t):
    """Winner: arms raised, small bounce, glowing accent ring."""
    r = fighter.rect
    body_c = fighter.color
    outline = _darken(body_c, 0.35)
    accent = fighter.attack_color

    cx = r.centerx
    base_bottom = r.bottom
    bob = int(math.sin(t * 4.0) * 4)

    head_r = fighter.head_r
    torso_w = fighter.torso_w
    torso_h = fighter.torso_h

    head_cy = base_bottom - torso_h - head_r * 2 - 8 + bob
    torso_cy = base_bottom - torso_h // 2 - head_r - 4

    # Ground glow
    glow = pygame.Surface((r.width * 3, 40), pygame.SRCALPHA)
    pygame.draw.ellipse(glow, (*accent, 90), glow.get_rect())
    surface.blit(glow, (cx - glow.get_width() // 2, base_bottom - 12))

    # Legs
    hip_y = torso_cy + torso_h // 2
    leg_len = fighter.leg_len
    for off_x, ang in ((-fighter.shoulder_w // 3, 100),
                       (fighter.shoulder_w // 3, 80)):
        lx = cx + off_x
        ly = hip_y + leg_len // 2
        a = math.radians(ang)
        hx = math.cos(a) * leg_len / 2
        hy = math.sin(a) * leg_len / 2
        pygame.draw.line(surface, outline,
                         (lx - hx, ly - hy), (lx + hx, ly + hy),
                         fighter.leg_thick + 4)
        pygame.draw.line(surface, body_c,
                         (lx - hx, ly - hy), (lx + hx, ly + hy),
                         fighter.leg_thick)

    # Torso
    torso = pygame.Rect(0, 0, torso_w, torso_h)
    torso.center = (cx, torso_cy)
    pygame.draw.rect(surface, outline, torso.inflate(4, 4), border_radius=8)
    pygame.draw.rect(surface, body_c, torso, border_radius=6)
    stripe = pygame.Rect(torso.x + 6, torso.centery - 2,
                         torso.width - 12, 4)
    pygame.draw.rect(surface, accent, stripe)

    # Arms raised: both point up-outward
    shoulder_y = torso_cy - torso_h // 2 + 6
    arm_len = fighter.arm_len
    for off_x, ang in ((-fighter.shoulder_w // 2, -60),
                       (fighter.shoulder_w // 2, -120)):
        ax = cx + off_x
        ay = shoulder_y + arm_len // 2
        a = math.radians(ang)
        hx = math.cos(a) * arm_len / 2
        hy = math.sin(a) * arm_len / 2
        pygame.draw.line(surface, outline,
                         (ax - hx, ay - hy), (ax + hx, ay + hy),
                         fighter.arm_thick + 4)
        pygame.draw.line(surface, body_c,
                         (ax - hx, ay - hy), (ax + hx, ay + hy),
                         fighter.arm_thick)

    # Head
    pygame.draw.circle(surface, outline, (cx, head_cy + bob), head_r + 3)
    pygame.draw.circle(surface, body_c, (cx, head_cy + bob), head_r)
    # Eye
    eye_r = max(2, head_r // 3)
    pygame.draw.circle(surface, fighter.eye_color,
                       (cx + head_r // 3, head_cy + bob - head_r // 6), eye_r)

    # Sparkle stars around the winner
    for i in range(3):
        ang = t * 2.0 + i * (math.tau / 3)
        sx = cx + int(math.cos(ang) * (r.width * 0.9))
        sy = head_cy + int(math.sin(ang) * 30)
        _draw_star(surface, sx, sy, int(head_r * 0.7), accent)


def _draw_star(surface, cx, cy, size, color):
    points = []
    for i in range(8):
        a = math.radians(i * 45)
        rr = size if i % 2 == 0 else size // 2
        points.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, (255, 255, 255), points, 1)


def draw_defeated(surface, fighter):
    """Loser: slumped horizontally on the floor."""
    r = fighter.rect
    body_c = (90, 90, 100)
    outline = _darken(body_c, 0.35)

    ground_y = r.bottom
    length = int(fighter.height * 0.95)
    thickness = max(14, fighter.width // 3)

    x = r.centerx - length // 2
    y = ground_y - thickness - 2

    rect = pygame.Rect(x, y, length, thickness)
    pygame.draw.rect(surface, outline, rect.inflate(4, 4), border_radius=10)
    pygame.draw.rect(surface, body_c, rect, border_radius=8)

    head_cx = x + (thickness + 4 if fighter.facing == 1 else length - thickness - 4)
    pygame.draw.circle(surface, outline, (head_cx, y + thickness // 2),
                       fighter.head_r + 3)
    pygame.draw.circle(surface, body_c, (head_cx, y + thickness // 2),
                       fighter.head_r)
    # X eye (KO)
    ex = head_cx
    ey = y + thickness // 2
    er = max(3, fighter.head_r // 3)
    pygame.draw.line(surface, (255, 80, 80), (ex - er, ey - er), (ex + er, ey + er), 3)
    pygame.draw.line(surface, (255, 80, 80), (ex - er, ey + er), (ex + er, ey - er), 3)

# combat/attack.py
"""
Attack -- a data container describing one attack and tracking its lifecycle.

An attack goes through three phases:
    STARTUP  -> wind-up, hitbox not yet active
    ACTIVE   -> hitbox exists, can connect
    RECOVERY -> hitbox gone, attacker is punished if they whiffed
"""

from dataclasses import dataclass
import pygame


@dataclass
class AttackData:
    name: str
    startup: int
    active: int
    recovery: int
    damage: int
    hitstun: int
    blockstun: int
    knockback: int
    reach: int
    height: int
    vertical_offset: int = 0


class Attack:
    def __init__(self, data: AttackData, owner_facing: int, owner_rect: pygame.Rect):
        self.data = data
        self.facing = owner_facing
        self.frame = 0
        self.total = data.startup + data.active + data.recovery
        self.has_connected = False
        self.hitbox = None
        self._owner_rect_at_spawn = owner_rect.copy()
        self._spawn_hitbox()

    def _spawn_hitbox(self):
        reach = self.data.reach
        h = self.data.height
        cy = self._owner_rect_at_spawn.centery
        if self.facing == 1:
            x = self._owner_rect_at_spawn.right
        else:
            x = self._owner_rect_at_spawn.left - reach
        y = cy - h // 2 + self.data.vertical_offset
        self._hitbox_rect = pygame.Rect(x, y, reach, h)

    @property
    def in_startup(self):
        return self.frame < self.data.startup

    @property
    def in_active(self):
        s = self.data.startup
        return s <= self.frame < s + self.data.active

    @property
    def in_recovery(self):
        s = self.data.startup + self.data.active
        return s <= self.frame < self.total

    @property
    def is_finished(self):
        return self.frame >= self.total

    def update(self, owner_rect: pygame.Rect):
        self.frame += 1
        reach = self.data.reach
        h = self.data.height
        if self.facing == 1:
            x = owner_rect.right
        else:
            x = owner_rect.left - reach
        y = owner_rect.centery - h // 2 + self.data.vertical_offset
        if self.in_active:
            self.hitbox = pygame.Rect(x, y, reach, h)
        else:
            self.hitbox = None

    def mark_connected(self):
        self.has_connected = True

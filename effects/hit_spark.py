"""Animated hit and guard impacts using the imported fighting effect strips."""

from effects import sprite_effect


class HitSpark:
    def __init__(self, x, y, color, count=14, speed=6, life=14):
        self.x, self.y = x, y
        self.color = color
        self.life = self.max_life = life
        self.effect = 1 if speed >= 8 else 2
        self.size = 144 if speed >= 8 else 96

    def update(self):
        self.life -= 1
        return self.life <= 0

    def draw(self, surface):
        if self.life > 0:
            sprite_effect.draw(surface, self.effect, self.x, self.y,
                               1 - self.life / self.max_life, size=self.size)


class BlockSpark:
    def __init__(self, x, y, life=10):
        self.x, self.y = x, y
        self.life = self.max_life = life

    def update(self):
        self.life -= 1
        return self.life <= 0

    def draw(self, surface):
        if self.life > 0:
            sprite_effect.draw(surface, 4, self.x, self.y,
                               1 - self.life / self.max_life, size=80, gameboy=True)

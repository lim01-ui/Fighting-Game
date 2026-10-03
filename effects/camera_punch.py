"""Short visual camera zoom pulses for heavy combat impacts."""

import pygame


class CameraPunch:
    def __init__(self):
        self.strength = 0.0
        self.frames_left = 0
        self.duration = 1
        self.focus = (640.0, 360.0)

    def kick(self, strength, frames, focus):
        if frames <= 0:
            return
        if self.frames_left <= 0 or strength >= self.strength:
            self.focus = (float(focus[0]), float(focus[1]))
            self.strength = strength
            self.frames_left = frames
            self.duration = frames
        else:
            self.frames_left = max(self.frames_left, frames)
            self.duration = max(self.duration, frames)

    def update(self):
        if self.frames_left <= 0:
            self.strength = 0.0
            return 1.0
        progress = 1.0 - self.frames_left / self.duration
        envelope = min(1.0, progress * 5, (1.0 - progress) * 2.5)
        self.frames_left -= 1
        return 1.0 + self.strength * max(0.0, envelope)

    def draw(self, world, screen, offset=(0, 0)):
        scale = self.update()
        if scale <= 1.001:
            screen.blit(world, offset)
            return
        size = (
            int(world.get_width() * scale),
            int(world.get_height() * scale),
        )
        scaled_world = pygame.transform.smoothscale(world, size)
        focus_x, focus_y = self.focus
        x = int(focus_x + offset[0] - focus_x * scale)
        y = int(focus_y + offset[1] - focus_y * scale)
        screen.blit(scaled_world, (x, y))

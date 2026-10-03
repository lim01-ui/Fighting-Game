# effects/screen_shake.py
"""
Screen shake — a temporary offset applied to everything drawn.

Usage:
    shake = ScreenShake()
    shake.kick(8, 12)          # magnitude 8 px, 12 frames
    ...
    ox, oy = shake.update()    # get current offset, decays each frame
"""

import random


class ScreenShake:
    def __init__(self):
        self.magnitude = 0
        self.frames_left = 0

    def kick(self, magnitude, frames):
        """Trigger a shake. Stacks with existing by taking the larger."""
        self.magnitude = max(self.magnitude, magnitude)
        self.frames_left = max(self.frames_left, frames)

    def update(self):
        """Advance one frame. Returns (offset_x, offset_y)."""
        if self.frames_left <= 0:
            return 0, 0
        self.frames_left -= 1
        # Decay magnitude as frames run out
        decay = self.frames_left / max(1, self.frames_left + 1)
        m = self.magnitude * decay
        self.magnitude *= 0.85
        ox = random.uniform(-m, m)
        oy = random.uniform(-m, m)
        if self.frames_left <= 0:
            self.magnitude = 0
        return int(ox), int(oy)

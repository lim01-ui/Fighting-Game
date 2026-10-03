# combat/combo.py
"""
ComboTracker -- counts consecutive hits and resets when the window expires.
"""

import settings


class ComboTracker:
    def __init__(self):
        self.hits = 0
        self.frames_since_last_hit = 999

    def register_hit(self):
        self.hits += 1
        self.frames_since_last_hit = 0

    def reset(self):
        self.hits = 0
        self.frames_since_last_hit = 999

    def update(self):
        if self.hits == 0:
            return
        self.frames_since_last_hit += 1
        if self.frames_since_last_hit > settings.COMBO_WINDOW_FRAMES:
            self.reset()

    @property
    def display_text(self):
        if self.hits < settings.COMBO_MIN_DISPLAY:
            return ""
        return f"{self.hits} HIT COMBO"

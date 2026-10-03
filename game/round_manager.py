# game/round_manager.py
ROUND_COUNTDOWN = "COUNTDOWN"
ROUND_FIGHTING  = "FIGHTING"
ROUND_OVER      = "OVER"
ROUND_HOLD      = "HOLD"

COUNTDOWN_FRAMES  = 300   # total length of the ROUND/FIGHT animation
FIGHT_HOLD_FRAMES = 50    # frames the FIGHT! text stays after the animation   # a bit longer for the intro animation
ROUND_OVER_FRAMES = 180


class RoundManager:
    def __init__(self, round_number, timer_seconds=99):
        self.round_number = round_number
        self.timer_seconds = timer_seconds
        self.timer_frames = timer_seconds * 60
        self.state = ROUND_COUNTDOWN
        self.state_timer = COUNTDOWN_FRAMES
        self.winner = None

    # ---- progress helpers (0.0 -> 1.0) ----
    @property
    def countdown_progress(self):
        """0 at start of countdown, 1 at the moment FIGHT begins."""
        if self.state == ROUND_COUNTDOWN:
            return 1.0 - (self.state_timer / COUNTDOWN_FRAMES)
        return 1.0

    @property
    def over_progress(self):
        """0 at KO moment, 1 when pause is over."""
        if self.state != ROUND_OVER:
            return 0.0
        return 1.0 - (self.state_timer / ROUND_OVER_FRAMES)

    @property
    def timer_display(self):
        return max(0, self.timer_frames // 60)

    @property
    def is_fighting(self):
        return self.state == ROUND_FIGHTING

    @property
    def is_over(self):
        return self.state == ROUND_OVER

    @property
    def accepts_input(self):
        return self.state == ROUND_FIGHTING

    @property
    def over_pause_done(self):
        return self.state == ROUND_OVER and self.state_timer <= 0

    def update(self, p1, p2):
        if self.state == ROUND_COUNTDOWN:
            self.state_timer -= 1
            if self.state_timer <= 0:
                # Enter a short HOLD state where FIGHT! stays on screen
                self.state = ROUND_HOLD
                self.state_timer = FIGHT_HOLD_FRAMES
            return None

        if self.state == ROUND_HOLD:
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.state = ROUND_FIGHTING
            return None

        if self.state == ROUND_FIGHTING:
            self.timer_frames -= 1
            if p1.health <= 0 and p2.health <= 0:
                self._end("draw"); return "round_ended"
            elif p1.health <= 0:
                self._end("p2"); return "round_ended"
            elif p2.health <= 0:
                self._end("p1"); return "round_ended"
            if self.timer_frames <= 0:
                if p1.health > p2.health:
                    self._end("p1")
                elif p2.health > p1.health:
                    self._end("p2")
                else:
                    self._end("draw")
                return "round_ended"
            return None

        if self.state == ROUND_OVER:
            self.state_timer -= 1
            return None

    def _end(self, winner):
        self.state = ROUND_OVER
        self.state_timer = ROUND_OVER_FRAMES
        self.winner = winner

# game/match_manager.py
WINS_TO_WIN_MATCH = 2


class MatchManager:
    def __init__(self, total_rounds=3, wins_needed=WINS_TO_WIN_MATCH):
        self.total_rounds = total_rounds
        self.wins_needed = wins_needed
        self.round_number = 1
        self.p1_wins = 0
        self.p2_wins = 0
        self.match_over = False
        self.match_winner = None

    def register_round_winner(self, winner):
        if winner == "p1":
            self.p1_wins += 1
        elif winner == "p2":
            self.p2_wins += 1
        if self.p1_wins >= self.wins_needed:
            self.match_over = True
            self.match_winner = "p1"
        elif self.p2_wins >= self.wins_needed:
            self.match_over = True
            self.match_winner = "p2"

    def next_round(self):
        self.round_number += 1

    def pips_display(self):
        return self.p1_wins, self.p2_wins, self.wins_needed

import random
from ai import difficulty

B_IDLE = "IDLE"
B_APPROACH = "APPROACH"
B_RETREAT = "RETREAT"
B_ATTACK = "ATTACK"
B_BLOCK = "BLOCK"
B_JUMP = "JUMP"


class Bot:
    def __init__(self, player, opponent, difficulty_name="NORMAL"):
        self.player = player
        self.opponent = opponent
        self.diff = difficulty.get(difficulty_name)
        self.state = B_IDLE
        self.state_timer = 0
        self.attack_cooldown = 0
        self.action_frames = 0
        self.keys = {
            "left": False, "right": False, "jump": False,
            "crouch": False, "light": False, "heavy": False, "special": False,
        }

    def update(self):
        self.keys["light"] = self.keys["heavy"] = self.keys["special"] = False
        self.keys["jump"] = False

        if self.player.state in ("HITSTUN", "BLOCKSTUN", "KNOCKDOWN"):
            self._clear_movement()
            self._apply_keys()
            return

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.player.state == "ATTACK":
            self._apply_keys()
            return

        self.state_timer -= 1
        if self.state_timer <= 0:
            self._decide()
        self._act()
        self._apply_keys()

    def _decide(self):
        self.state_timer = self.diff.reaction_frames
        p, o = self.player, self.opponent
        dist = abs(p.rect.centerx - o.rect.centerx)
        threatening = (
            o.is_attacking
            and o.get_hitbox() is not None
            and self._facing_each_other()
        )

        if threatening and random.random() < self.diff.block_chance:
            self.state = B_BLOCK
            self.action_frames = 20
            return

        if dist <= self.diff.attack_range and self.attack_cooldown <= 0:
            if random.random() < self.diff.attack_chance:
                self.state = B_ATTACK
                self.action_frames = 1
                return

        if random.random() < self.diff.jump_chance:
            self.state = B_JUMP
            self.action_frames = 1
            return

        if dist > self.diff.preferred_distance:
            self.state = B_APPROACH
            self.action_frames = random.randint(15, 35)
        elif dist < self.diff.preferred_distance - 60:
            self.state = B_RETREAT
            self.action_frames = random.randint(10, 25)
        else:
            self.state = B_IDLE
            self.action_frames = random.randint(5, 15)

    def _act(self):
        self._clear_movement()
        p, o = self.player, self.opponent
        toward = 1 if o.rect.centerx > p.rect.centerx else -1

        if self.state == B_APPROACH:
            self.keys["right" if toward == 1 else "left"] = True
        elif self.state == B_RETREAT:
            self.keys["left" if toward == 1 else "right"] = True
        elif self.state == B_BLOCK:
            self.keys["left" if toward == 1 else "right"] = True
        elif self.state == B_JUMP:
            self.keys["jump"] = True
        elif self.state == B_ATTACK:
            if random.random() < self.diff.special_chance:
                self.keys["special"] = True
            elif random.random() < self.diff.heavy_chance:
                self.keys["heavy"] = True
            else:
                self.keys["light"] = True
            self.attack_cooldown = self.diff.attack_cooldown
            self.state = B_IDLE
            self.state_timer = self.diff.reaction_frames

        self.action_frames -= 1
        if self.action_frames <= 0:
            self.state_timer = min(self.state_timer, 1)

    def _facing_each_other(self):
        p, o = self.player, self.opponent
        if o.rect.centerx > p.rect.centerx:
            return o.facing == -1
        return o.facing == 1

    def _clear_movement(self):
        self.keys["left"] = self.keys["right"] = self.keys["crouch"] = False

    def _apply_keys(self):
        p = self.player
        mapping = {}
        for action, pressed in self.keys.items():
            if action not in p.keymap:
                continue
            keycode = p._key(p.keymap[action])
            mapping[keycode] = pressed
        p.handle_input(_FakeKeys(mapping))


class _FakeKeys:
    def __init__(self, mapping):
        self._map = mapping

    def __getitem__(self, key):
        return self._map.get(key, False)

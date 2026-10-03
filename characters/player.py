# characters/player.py
"""
Player -- stickman fighter with a weapon.

Style:
    - Thin stickman lines for torso, arms, legs
    - Circular joints at elbows, knees
    - Torso filled with the character's body color (a "shirt")
    - Head circle with two eyes and a mouth
    - A distinct weapon drawn in the front hand, oriented with the arm
    - Attack trails: a ghost arc behind fast-moving weapons
"""

import math
import pygame

import settings
from combat.attack import Attack, AttackData
from characters import character_data
from characters import pixel_fighter
from characters import sprite_fighter
from characters import weapons
from effects import combat_behaviors


S_IDLE      = "IDLE"
S_WALK      = "WALK"
S_JUMP      = "JUMP"
S_CROUCH    = "CROUCH"
S_ATTACK    = "ATTACK"
S_HITSTUN   = "HITSTUN"
S_BLOCKSTUN = "BLOCKSTUN"
S_KNOCKDOWN = "KNOCKDOWN"


OUTLINE = (18, 18, 26)


def _darken(color, factor=0.5):
    return (int(color[0] * factor), int(color[1] * factor), int(color[2] * factor))


def _build_attack_blueprints(character):
    mods = character["attack_mods"]
    stats = character["stats"]
    eff = character.get("weapon_effect", {})
    ultimate = character_data.ultimate_for(character["key"])
    ultimate_hit_count = ultimate.get("extra_hits", 0) + 1

    startup_mult  = eff.get("startup_mult", 1.0)
    reach_mult    = eff.get("reach_mult", 1.0)
    kb_mult       = eff.get("knockback_mult", 1.0)
    hitstun_mult  = eff.get("hitstun_mult", 1.0)

    def make(kind, base, vertical_offset=0):
        return AttackData(
            name=kind,
            startup=max(2, int(base["startup"] * mods["startup"] * startup_mult)),
            active=base["active"],
            recovery=max(4, int(base["recovery"] * mods["cooldown"])),
            damage=max(1, int(base["damage"] * stats["damage"])),
            hitstun=int(base["hitstun"] * hitstun_mult),
            blockstun=base["blockstun"],
            knockback=int(base["knockback"] * kb_mult),
            reach=max(30, int(base["reach"] * mods["reach"] * reach_mult)),
            height=base["height"],
            vertical_offset=vertical_offset,
        )

    lb = {"startup": settings.LIGHT_STARTUP, "active": settings.LIGHT_ACTIVE,
          "recovery": settings.LIGHT_RECOVERY, "damage": settings.LIGHT_DAMAGE,
          "hitstun": settings.LIGHT_HITSTUN, "blockstun": settings.LIGHT_BLOCKSTUN,
          "knockback": settings.LIGHT_KNOCKBACK, "reach": settings.LIGHT_REACH,
          "height": settings.LIGHT_HEIGHT}
    hb = {"startup": settings.HEAVY_STARTUP, "active": settings.HEAVY_ACTIVE,
          "recovery": settings.HEAVY_RECOVERY, "damage": settings.HEAVY_DAMAGE,
          "hitstun": settings.HEAVY_HITSTUN, "blockstun": settings.HEAVY_BLOCKSTUN,
          "knockback": settings.HEAVY_KNOCKBACK, "reach": settings.HEAVY_REACH,
          "height": settings.HEAVY_HEIGHT}
    sb = {"startup": settings.SPECIAL_STARTUP, "active": settings.SPECIAL_ACTIVE,
          "recovery": settings.SPECIAL_RECOVERY, "damage": settings.SPECIAL_DAMAGE,
          "hitstun": settings.SPECIAL_HITSTUN, "blockstun": settings.SPECIAL_BLOCKSTUN,
          "knockback": settings.SPECIAL_KNOCKBACK, "reach": settings.SPECIAL_REACH,
          "height": settings.SPECIAL_HEIGHT}
    crouch_light = {
        **lb,
        "startup": lb["startup"] + 2,
        "recovery": lb["recovery"] + 4,
        "damage": max(1, int(lb["damage"] * 0.8)),
        "reach": int(lb["reach"] * 0.9),
        "height": max(14, int(lb["height"] * 0.65)),
    }
    crouch_heavy = {
        **hb,
        "startup": hb["startup"] + 2,
        "recovery": hb["recovery"] + 4,
        "damage": max(1, int(hb["damage"] * 0.9)),
        "reach": int(hb["reach"] * 0.9),
        "height": max(18, int(hb["height"] * 0.7)),
    }
    air_light = {
        **lb,
        "startup": lb["startup"] + 1,
        "recovery": lb["recovery"] + 3,
        "damage": max(1, int(lb["damage"] * 0.85)),
        "height": max(20, int(lb["height"] * 0.8)),
    }
    air_heavy = {
        **hb,
        "startup": hb["startup"] + 2,
        "recovery": hb["recovery"] + 5,
        "damage": max(1, int(hb["damage"] * 0.9)),
        "height": max(24, int(hb["height"] * 0.8)),
    }
    return {"light": make("light", lb),
            "heavy": make("heavy", hb),
            "crouch_light": make("crouch_light", crouch_light, 22),
            "crouch_heavy": make("crouch_heavy", crouch_heavy, 25),
            "air_light": make("air_light", air_light, -24),
            "air_heavy": make("air_heavy", air_heavy, -28),
            "special": make("special", sb),
            "ultimate": AttackData(
                name="ultimate",
                startup=max(
                    6,
                    int(ultimate.get(
                        "startup", sb["startup"] * mods["startup"] * 1.2
                    )),
                ),
                active=max(4, int(ultimate.get(
                    "active", sb["active"] * 1.25
                ))),
                recovery=max(
                    18,
                    int(ultimate.get(
                        "recovery", sb["recovery"] * mods["cooldown"] * 1.3
                    )),
                ),
                damage=max(
                    1,
                    int(sb["damage"] * stats["damage"]
                        * ultimate.get("damage_mult", 1.5)
                        / ultimate_hit_count),
                ),
                hitstun=int(
                    sb["hitstun"] * hitstun_mult
                    * ultimate.get("hitstun_mult", 1.3)
                ),
                blockstun=int(sb["blockstun"] * 1.25),
                knockback=int(
                    sb["knockback"] * kb_mult
                    * ultimate.get("knockback_mult", 1.5)
                ),
                reach=max(
                    40,
                    int(sb["reach"] * mods["reach"] * reach_mult
                        * ultimate.get("reach_mult", 1.0)),
                ),
                height=max(70, int(sb["height"] * 1.35)),
            )}


class Player:
    def __init__(self, x, y, character_key, keymap, facing=1):
        self.character = character_data.get(character_key)
        self.keymap = keymap
        self.facing = facing

        body = self.character["body"]
        stats = self.character["stats"]

        self.width  = int(body["width"]  * settings.FIGHTER_SCALE)
        self.height = int(body["height"] * settings.FIGHTER_SCALE)
        self.crouch_ratio = body["crouch_ratio"]

        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.spawn_x = x
        self.spawn_y = y

        self.vel_y = 0
        self.on_ground = True

        self.move_speed = settings.MOVE_SPEED * stats["speed"]
        self.jump_power = settings.JUMP_POWER * stats["jump"]
        self.max_health = int(settings.MAX_HEALTH * stats["health"])
        self.health = self.max_health
        self.defense = stats["defense"]

        self.attacks = _build_attack_blueprints(self.character)

        self.state = S_IDLE
        self.state_timer = 0
        self.is_crouching = False
        self.current_attack = None
        self.hit_pause = 0
        self._holding_back = False

        self.color        = self.character["colors"]["body"]
        self.attack_color = self.character["colors"]["accent"]
        self.eye_color    = self.character["colors"]["eye"]
        self.walk_phase   = 0.0

        h = self.height
        self.head_r    = int(h * 0.11)
        self.torso_len = int(h * 0.32)
        self.arm_len   = int(h * 0.30)
        self.leg_len   = int(h * 0.36)
        self.shoulder_w = int(self.width * 0.55)
        self.stick_thick = max(12, int(h * 0.07))

        self.weapon_type   = self.character.get("weapon", "sword")
        self.weapon_color  = self.character.get("weapon_color", (220, 220, 240))
        self.weapon_handle = self.character.get("weapon_handle", (100, 100, 120))
        self.weapon_trail = []
        self.super_armor_frames = 0
        self._opponent_ref = None
        self._stun_on_hit = 0
        self.ultimate_meter = 0.0

    def _key(self, name):
        if hasattr(pygame, f"K_{name}"):
            return getattr(pygame, f"K_{name}")
        if hasattr(pygame, f"K_{name.upper()}"):
            return getattr(pygame, f"K_{name.upper()}")
        return getattr(pygame, f"K_{name.lower()}")

    def handle_input(self, keys):
        self.face_opponent()
        if self.state in (S_HITSTUN, S_BLOCKSTUN, S_KNOCKDOWN):
            return
        if self.hit_pause > 0:
            return

        left    = keys[self._key(self.keymap["left"])]
        right   = keys[self._key(self.keymap["right"])]
        jump    = keys[self._key(self.keymap["jump"])]
        crouch  = keys[self._key(self.keymap["crouch"])]
        light   = keys[self._key(self.keymap["light"])]
        heavy   = keys[self._key(self.keymap["heavy"])]
        special = keys[self._key(self.keymap["special"])]

        if self.state != S_ATTACK:
            if light or heavy:
                attack_type = "light" if light else "heavy"
                if not self.on_ground:
                    attack_type = f"air_{attack_type}"
                elif crouch:
                    attack_type = f"crouch_{attack_type}"
                    self.is_crouching = True
                self._start_attack(attack_type)
                return
            if special:
                self._start_attack(
                    "ultimate" if self.ultimate_meter >= 100 else "special"
                )
                return

        if self.state == S_ATTACK:
            return

        self.is_crouching = crouch and self.on_ground

        moving = False
        if not self.is_crouching:
            if left and not right:
                self.rect.x -= self.move_speed; moving = True
            elif right and not left:
                self.rect.x += self.move_speed; moving = True

        if jump and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False

        if not self.on_ground:  self.state = S_JUMP
        elif self.is_crouching: self.state = S_CROUCH
        elif moving:            self.state = S_WALK
        else:                   self.state = S_IDLE

        self._holding_back = (
            (self.facing == 1 and left and not right)
            or (self.facing == -1 and right and not left)
        )

    def _start_attack(self, kind):
        data = self.attacks[kind]
        self.current_attack = Attack(data, self.facing, self.rect)
        self.state = S_ATTACK
        self._multi_hit_counter = 0
        if kind == "ultimate":
            self.ultimate_meter = 0.0
            combat_behaviors.on_start(self, ultimate=True)
        elif kind == "special":
            combat_behaviors.on_start(self)

    def gain_ultimate_meter(self, damage):
        """Charge the ultimate meter from dealt or received health damage."""
        if damage > 0:
            self.ultimate_meter = min(100.0, self.ultimate_meter + damage * 0.55)

    def _end_attack(self):
        self.current_attack = None
        self.state = S_IDLE
        self._stun_on_hit = 0

    def receive_hit(self, attack, blocked):
        data = attack.data
        incoming = data.damage * self.defense
        # Super-armor: take damage but ignore hitstun / knockback
        if self.super_armor_frames > 0 and not blocked:
            damage = int(incoming)
            self.health = max(0, self.health - damage)
            self.hit_pause = settings.HIT_PAUSE_FRAMES
            return True
        if blocked:
            damage = int(incoming * settings.BLOCK_REDUCTION)
            self.health = max(0, self.health - damage)
            self.blockstun_left = data.blockstun
            self.state = S_BLOCKSTUN
            self.state_timer = data.blockstun
            kb = int(data.knockback * settings.BLOCK_KNOCKBACK_MULT)
            self._apply_knockback(attack.facing, kb)
        else:
            damage = int(incoming)
            self.health = max(0, self.health - damage)
            self.hitstun_left = data.hitstun
            self.state = S_HITSTUN
            self.state_timer = data.hitstun
            self._apply_knockback(attack.facing, data.knockback)
        return True

    def _apply_knockback(self, attacker_facing, amount):
        self.rect.x += amount * attacker_facing

    def get_hurtbox(self):
        r = self.rect.copy()
        r.x += settings.HURTBOX_INSET_X
        r.width -= settings.HURTBOX_INSET_X * 2
        if self.is_crouching:
            new_h = int(r.height * self.crouch_ratio)
            r.y = r.bottom - new_h
            r.height = new_h
        return r

    def get_hitbox(self):
        if self.current_attack is None:
            return None
        return self.current_attack.hitbox

    @property
    def is_attacking(self):
        return self.state == S_ATTACK

    @property
    def attack_has_connected(self):
        return self.current_attack is not None and self.current_attack.has_connected

    def mark_attack_connected(self):
        if self.current_attack is not None:
            self.current_attack.mark_connected()

    def update(self, opponent=None):
        if opponent is not None:
            self._opponent_ref = opponent
        self.face_opponent()
        if self.hit_pause > 0:
            self.hit_pause -= 1
            return

        self.vel_y += settings.GRAVITY
        self.rect.y += self.vel_y
        if self.rect.bottom >= settings.GROUND_Y:
            self.rect.bottom = settings.GROUND_Y
            self.vel_y = 0
            self.on_ground = True

        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > settings.WINDOW_WIDTH: self.rect.right = settings.WINDOW_WIDTH

        if self.super_armor_frames > 0:
            self.super_armor_frames -= 1

        if self.state == S_WALK:
            self.walk_phase += 0.25

        if self.state == S_HITSTUN:
            self.state_timer -= 1
            if self.state_timer <= 0: self.state = S_IDLE
        elif self.state == S_BLOCKSTUN:
            self.state_timer -= 1
            if self.state_timer <= 0: self.state = S_IDLE
        elif self.state == S_ATTACK and self.current_attack is not None:
            self.current_attack.update(self.rect)
            if self.current_attack.is_finished: self._end_attack()
        elif self.state == S_KNOCKDOWN:
            self.state_timer -= 1
            if self.state_timer <= 0: self.state = S_IDLE

        if opponent is not None:
            self._resolve_body_collision(opponent)

    def face_opponent(self):
        if self._opponent_ref is None:
            return
        opponent_x = self._opponent_ref.rect.centerx
        if opponent_x != self.rect.centerx:
            self.facing = 1 if opponent_x > self.rect.centerx else -1

    def _resolve_body_collision(self, other):
        if self.state in (S_HITSTUN, S_BLOCKSTUN, S_KNOCKDOWN): return
        if self.rect.colliderect(other.rect):
            if self.rect.centerx < other.rect.centerx:
                self.rect.right = other.rect.left
            else:
                self.rect.left = other.rect.right

    def go_knockdown(self):
        self.state = S_KNOCKDOWN
        self.state_timer = settings.KNOCKDOWN_FRAMES

    def reset(self):
        self.rect.x = self.spawn_x
        self.rect.y = self.spawn_y
        self.vel_y = 0
        self.on_ground = True
        self.health = self.max_health
        self.state = S_IDLE
        self.state_timer = 0
        self.current_attack = None
        self.is_crouching = False
        self.hit_pause = 0
        self._holding_back = False
        self.walk_phase = 0.0
        self.weapon_trail = []
        self.super_armor_frames = 0
        self._stun_on_hit = 0

    def _compute_pose(self):
        pose = {
            "torso_dx": 0, "torso_dy": 0,
            "head_dx": 0, "head_dy": 0,
            "arm_upper_front": 80, "arm_fore_front": 80,
            "arm_upper_back":  100, "arm_fore_back":  100,
            "leg_upper_front": 90, "leg_lower_front": 90,
            "leg_upper": 90, "leg_lower": 90,
            "arm_len": self.arm_len,
            "stance_dx": 0,
        }
        f = self.facing

        if self.state == S_IDLE:
            pose["arm_upper_front"] = 48
            pose["arm_fore_front"]  = 128
            pose["arm_upper_back"]  = 112
            pose["arm_fore_back"]   = 52
            pose["leg_upper_front"] = 76
            pose["leg_lower_front"] = 116
            pose["leg_upper"] = 104
            pose["leg_lower"] = 72

        elif self.state == S_WALK:
            s = math.sin(self.walk_phase) * 32
            pose["arm_upper_front"] = 70 + s
            pose["arm_fore_front"]  = 110 - s * 0.25
            pose["arm_upper_back"]  = 110 - s
            pose["arm_fore_back"]   = 70 + s * 0.25
            pose["leg_upper_front"] = 90 + s
            pose["leg_lower_front"] = 90 - s * 0.6
            pose["leg_upper"] = 90 - s
            pose["leg_lower"] = 90 + s * 0.6
            pose["torso_dy"] = int(abs(math.sin(self.walk_phase)) * 2)
            pose["torso_dx"] = int(math.sin(self.walk_phase) * 2)

        elif self.state == S_JUMP:
            pose["torso_dy"] = -int(min(8, abs(self.vel_y) * 0.35))
            pose["arm_upper_front"] = 38
            pose["arm_fore_front"]  = 48
            pose["arm_upper_back"]  = 142
            pose["arm_fore_back"]   = 110
            pose["leg_upper_front"] = 60
            pose["leg_lower_front"] = 100
            pose["leg_upper"] = 100
            pose["leg_lower"] = 60

        elif self.state == S_CROUCH:
            pose["arm_upper_front"] = 60
            pose["arm_fore_front"]  = 110
            pose["arm_upper_back"]  = 120
            pose["arm_fore_back"]   = 70
            pose["leg_upper_front"] = 60
            pose["leg_lower_front"] = 130
            pose["leg_upper"] = 120
            pose["leg_lower"] = 60

        elif self.state == S_HITSTUN:
            pose["head_dx"] = -f * 5
            pose["torso_dx"] = -f * 4
            pose["arm_upper_front"] = 60
            pose["arm_fore_front"]  = 120
            pose["arm_upper_back"]  = 130
            pose["arm_fore_back"]   = 60
            pose["leg_upper_front"] = 95
            pose["leg_lower_front"] = 85
            pose["leg_upper"] = 85
            pose["leg_lower"] = 95

        elif self.state == S_BLOCKSTUN:
            pose["head_dx"] = -f * 3
            pose["torso_dx"] = -f * 3
            pose["arm_upper_front"] = 18
            pose["arm_fore_front"]  = 8
            pose["arm_upper_back"]  = 42
            pose["arm_fore_back"]   = 12

        elif self.state == S_ATTACK and self.current_attack is not None:
            atk = self.current_attack
            name = atk.data.name
            startup_end = atk.data.startup
            active_end = startup_end + atk.data.active

            if atk.frame < startup_end:
                wind = atk.frame / max(1, startup_end)
                wind = wind * wind * (3 - 2 * wind)
                t_extend = -0.55 * wind
            elif atk.frame < active_end:
                t_extend = 1.0
            else:
                rec = (atk.frame - active_end) / max(1, atk.data.recovery)
                rec = min(1.0, max(0.0, rec))
                rec = rec * rec * (3 - 2 * rec)
                t_extend = max(0.0, 1.0 - rec * 1.8)

            reach = {
                "light": 0.9, "heavy": 1.15, "special": 1.35,
                "crouch_light": 0.85, "crouch_heavy": 1.0,
                "air_light": 1.0, "air_heavy": 1.25,
                "ultimate": 1.5,
            }[name]
            if name in ("heavy", "crouch_heavy", "air_heavy"):
                t_extend *= 1.18

            front_base = 0 if f == 1 else 180
            back_base  = 180 if f == 1 else 0

            pose["arm_upper_front"] = front_base + (1 - t_extend) * 58 * (1 if f == 1 else -1)
            pose["arm_fore_front"]  = front_base + (1 - t_extend) * 30 * (1 if f == 1 else -1)
            pose["arm_upper_back"]  = back_base  - t_extend * 20 * (1 if f == 1 else -1)
            pose["arm_fore_back"]   = back_base  - t_extend * 10 * (1 if f == 1 else -1)

            pose["leg_upper_front"] = 90 - t_extend * 25 * f
            pose["leg_lower_front"] = 90 + t_extend * 24
            pose["leg_upper"] = 90 + t_extend * 15 * f
            pose["leg_lower"] = 90 + t_extend * 5

            pose["torso_dx"] = int(f * 12 * max(0.0, t_extend))
            pose["head_dx"]  = int(f * 9 * max(0.0, t_extend))
            pose["stance_dx"] = int(f * 12 * max(0.0, t_extend))
            if name.startswith("crouch_"):
                pose["torso_dy"] = int(self.height * 0.14)
                pose["torso_dx"] += int(f * 3)
                pose["arm_upper_front"] = (
                    front_base + (1 - t_extend) * 72 * (1 if f == 1 else -1)
                )
                pose["arm_fore_front"] = (
                    front_base + (1 - t_extend) * 34 * (1 if f == 1 else -1)
                )
                pose["arm_upper_back"] = back_base - 34 * (1 if f == 1 else -1)
                pose["arm_fore_back"] = back_base - 18 * (1 if f == 1 else -1)
                pose["leg_upper_front"] += 28
                pose["leg_lower_front"] -= 22
                pose["leg_upper"] += 28
                pose["leg_lower"] -= 22
                pose["stance_dx"] = int(f * 5)
            elif name.startswith("air_"):
                pose["torso_dy"] = -int(self.height * 0.12)
                pose["torso_dx"] -= int(f * 5)
                pose["arm_upper_front"] = (
                    front_base + (1 - t_extend) * 42 * (1 if f == 1 else -1)
                )
                pose["arm_fore_front"] = (
                    front_base + (1 - t_extend) * 22 * (1 if f == 1 else -1)
                )
                pose["leg_upper_front"] -= 26
                pose["leg_lower_front"] += 18
                pose["leg_upper"] += 30
                pose["leg_lower"] -= 16
                pose["stance_dx"] = int(-f * 8)
            base = self.arm_len
            pose["arm_len"] = int(base * (1.0 + 0.35 * reach * max(0.0, t_extend)))

        if self.facing < 0 and self.state != S_ATTACK:
            for key in ("arm_upper_front", "arm_fore_front",
                        "arm_upper_back", "arm_fore_back"):
                pose[key] = 180 - pose[key]

        return pose

    def draw(self, surface):
        if self.character.get("sprite_asset"):
            self._draw_sprite_asset(surface)
            self._draw_debug_boxes(surface)
            return
        if self.character.get("sprite_sheet"):
            self._draw_pixel_fighter(surface)
            self._draw_debug_boxes(surface)
            return

        if self.state == S_ATTACK:      body_c = self.attack_color
        elif self.state == S_HITSTUN:   body_c = (235, 110, 110)
        elif self.state == S_BLOCKSTUN: body_c = (150, 220, 255)
        elif self.state == S_KNOCKDOWN: body_c = (90, 90, 90)
        else:                           body_c = self.color

        r = self.rect
        if self.state == S_KNOCKDOWN:
            self._draw_knockdown(surface, body_c)
            self._draw_debug_boxes(surface)
            return

        pose = self._compute_pose()
        cx = r.centerx + pose["torso_dx"]

        if self.is_crouching:
            base_y = settings.GROUND_Y - int(self.height * self.crouch_ratio)
            squash = 0.62
        else:
            base_y = r.top + pose["torso_dy"]
            squash = 1.0

        head_r    = self.head_r
        torso_len = int(self.torso_len * squash)
        leg_len   = int(self.leg_len * squash)
        arm_len   = pose["arm_len"]

        head_cy    = base_y + head_r + 4 + pose["head_dy"]
        torso_top  = head_cy + head_r + 2
        torso_bot  = torso_top + torso_len
        hip_y      = torso_bot
        shoulder_y = torso_top + 4
        head_cx    = cx + pose["head_dx"]

        hip_dx = pose["stance_dx"]
        joint_r = self.stick_thick // 2 + 1

        # BACK LEG
        hip_x = cx - self.shoulder_w // 3 * self.facing + hip_dx
        kx, ky = self._joint_from(hip_x, hip_y, pose["leg_upper"], leg_len // 2)
        ax, ay = self._joint_from(kx, ky, pose["leg_lower"], leg_len // 2)
        self._stick_line(surface, (hip_x, hip_y), (kx, ky), OUTLINE, self.stick_thick + 3)
        self._stick_line(surface, (hip_x, hip_y), (kx, ky), _darken(body_c, 0.7), self.stick_thick - 1)
        self._stick_line(surface, (kx, ky), (ax, ay), OUTLINE, self.stick_thick + 3)
        self._stick_line(surface, (kx, ky), (ax, ay), _darken(body_c, 0.7), self.stick_thick - 1)
        pygame.draw.circle(surface, _darken(body_c, 0.72), (int(kx), int(ky)), joint_r)
        self._draw_foot(surface, _darken(body_c, 0.7), ax, ay)

        # BACK ARM
        back_off = -self.shoulder_w // 2 * self.facing
        sh_x = cx + back_off
        sh_y = shoulder_y
        ex, ey = self._joint_from(sh_x, sh_y, pose["arm_upper_back"], arm_len // 2)
        wx, wy = self._joint_from(ex, ey, pose["arm_fore_back"], arm_len // 2)
        self._stick_line(surface, (sh_x, sh_y), (ex, ey), OUTLINE, self.stick_thick + 3)
        self._stick_line(surface, (sh_x, sh_y), (ex, ey), _darken(body_c, 0.7), self.stick_thick - 1)
        self._stick_line(surface, (ex, ey), (wx, wy), OUTLINE, self.stick_thick + 3)
        self._stick_line(surface, (ex, ey), (wx, wy), _darken(body_c, 0.7), self.stick_thick - 1)
        pygame.draw.circle(surface, _darken(body_c, 0.72), (int(ex), int(ey)), joint_r)

        # Layered jacket silhouette gives the side-view fighter some volume.
        shoulder_half = max(self.stick_thick + 5, int(self.shoulder_w * 0.58))
        waist_half = max(self.stick_thick + 2, int(self.shoulder_w * 0.34))
        torso_shape = [
            (int(cx - shoulder_half), int(shoulder_y)),
            (int(cx - shoulder_half + 5), int(torso_top + 10)),
            (int(cx - waist_half), int(torso_bot - 4)),
            (int(cx), int(torso_bot + 3)),
            (int(cx + waist_half), int(torso_bot - 4)),
            (int(cx + shoulder_half - 5), int(torso_top + 10)),
            (int(cx + shoulder_half), int(shoulder_y)),
            (int(cx), int(shoulder_y - 3)),
        ]
        pygame.draw.polygon(surface, OUTLINE, torso_shape)
        inset = max(2, self.stick_thick // 4)
        inner_shape = [
            (int(cx - shoulder_half + inset), int(shoulder_y + inset)),
            (int(cx - shoulder_half + 7), int(torso_top + 11)),
            (int(cx - waist_half + inset), int(torso_bot - 5)),
            (int(cx + waist_half - inset), int(torso_bot - 5)),
            (int(cx + shoulder_half - 7), int(torso_top + 11)),
            (int(cx + shoulder_half - inset), int(shoulder_y + inset)),
            (int(cx), int(shoulder_y + 2)),
        ]
        pygame.draw.polygon(surface, body_c, inner_shape)
        highlight_x = int(cx - self.facing * max(3, shoulder_half // 4))
        pygame.draw.line(surface, tuple(min(255, c + 42) for c in body_c),
                         (highlight_x, int(shoulder_y + 10)),
                         (highlight_x, int(torso_bot - 12)),
                         max(2, self.stick_thick // 4))
        belt_y = int(torso_bot - 7)
        pygame.draw.line(surface, OUTLINE,
                         (int(cx - waist_half), belt_y),
                         (int(cx + waist_half), belt_y), max(4, self.stick_thick // 2))
        pygame.draw.circle(surface, self.attack_color,
                           (int(cx), belt_y), max(3, self.stick_thick // 3))
        collar = [
            (int(cx - self.stick_thick), int(shoulder_y - 1)),
            (int(cx), int(shoulder_y + self.stick_thick)),
            (int(cx + self.stick_thick), int(shoulder_y - 1)),
        ]
        pygame.draw.lines(surface, OUTLINE, False, collar, max(4, self.stick_thick // 2))
        pygame.draw.lines(surface, self.attack_color, False, collar, max(2, self.stick_thick // 4))

        # FRONT LEG
        front_hip_x = cx + self.shoulder_w // 3 * self.facing + hip_dx
        k2x, k2y = self._joint_from(front_hip_x, hip_y, pose["leg_upper_front"], leg_len // 2)
        a2x, a2y = self._joint_from(k2x, k2y, pose["leg_lower_front"], leg_len // 2)
        self._stick_line(surface, (front_hip_x, hip_y), (k2x, k2y), OUTLINE, self.stick_thick + 3)
        self._stick_line(surface, (front_hip_x, hip_y), (k2x, k2y), body_c, self.stick_thick - 1)
        self._stick_line(surface, (k2x, k2y), (a2x, a2y), OUTLINE, self.stick_thick + 3)
        self._stick_line(surface, (k2x, k2y), (a2x, a2y), body_c, self.stick_thick - 1)
        pygame.draw.circle(surface, body_c, (int(k2x), int(k2y)), joint_r)
        pygame.draw.ellipse(
            surface, self.attack_color,
            (int(k2x - joint_r), int(k2y - joint_r),
             joint_r * 2, max(3, joint_r)),
        )
        self._draw_foot(surface, body_c, a2x, a2y)

        # FRONT ARM + WEAPON
        front_off = self.shoulder_w // 2 * self.facing
        sh2_x = cx + front_off
        sh2_y = shoulder_y
        e2x, e2y = self._joint_from(sh2_x, sh2_y, pose["arm_upper_front"], arm_len // 2)
        w2x, w2y = self._joint_from(e2x, e2y, pose["arm_fore_front"], arm_len // 2)

        self._stick_line(surface, (sh2_x, sh2_y), (e2x, e2y), OUTLINE, self.stick_thick + 3)
        self._stick_line(surface, (sh2_x, sh2_y), (e2x, e2y), body_c, self.stick_thick)
        self._stick_line(surface, (e2x, e2y), (w2x, w2y), OUTLINE, self.stick_thick + 3)
        self._stick_line(surface, (e2x, e2y), (w2x, w2y), body_c, self.stick_thick)
        pygame.draw.circle(surface, body_c, (int(e2x), int(e2y)), joint_r)
        pygame.draw.circle(surface, self.attack_color,
                           (int(w2x), int(w2y)), max(4, self.stick_thick // 2))
        pygame.draw.line(
            surface, _darken(self.attack_color, 0.8),
            (int(e2x), int(e2y)), (int(w2x), int(w2y)),
            max(2, self.stick_thick // 5),
        )
        pygame.draw.line(
            surface, self.attack_color,
            (int(e2x), int(e2y)),
            (int(w2x), int(w2y)),
            max(2, self.stick_thick // 3),
        )

        # WEAPON
        weapon_angle = pose["arm_fore_front"]
        tip_a = math.radians(weapon_angle)
        tip_x = w2x + math.cos(tip_a) * 50
        tip_y = w2y + math.sin(tip_a) * 50
        if self.state == S_ATTACK and self.current_attack is not None:
            if self.current_attack.in_active:
                self.weapon_trail.append((tip_x, tip_y, 255))
        new_trail = []
        for (tx, ty, alpha) in self.weapon_trail:
            alpha -= 30
            if alpha > 0:
                new_trail.append((tx, ty, alpha))
        self.weapon_trail = new_trail[-12:]
        for previous, current in zip(self.weapon_trail, self.weapon_trail[1:]):
            x1, y1, alpha1 = previous
            x2, y2, alpha2 = current
            strength = min(alpha1, alpha2) / 255
            width = max(2, int(self.stick_thick * (0.45 + strength)))
            trail_color = tuple(int(channel * strength) for channel in self.attack_color)
            pygame.draw.line(surface, OUTLINE, (int(x1), int(y1)),
                             (int(x2), int(y2)), width + 4)
            pygame.draw.line(surface, trail_color, (int(x1), int(y1)),
                             (int(x2), int(y2)), width)
            if strength > 0.55:
                pygame.draw.line(surface, (255, 245, 215),
                                 (int(x1), int(y1)), (int(x2), int(y2)),
                                 max(1, width // 3))

        weapons.draw_weapon(surface, self.weapon_type,
                            w2x, w2y, weapon_angle,
                            self.weapon_color, self.weapon_handle)

        # HEAD
        skin = (238, 190, 154)
        pygame.draw.circle(surface, OUTLINE, (head_cx, head_cy), head_r + 3)
        pygame.draw.circle(surface, skin, (head_cx, head_cy), head_r)
        pygame.draw.arc(surface, (255, 226, 196),
                        pygame.Rect(head_cx - head_r + 3, head_cy - head_r + 3,
                                    head_r * 2 - 6, head_r * 2 - 6),
                        math.radians(205), math.radians(325), max(2, head_r // 8))
        hair_rect = pygame.Rect(0, 0, (head_r + 2) * 2, int((head_r + 2) * 1.2))
        hair_rect.center = (head_cx, head_cy - int(head_r * 0.4))
        pygame.draw.ellipse(surface, OUTLINE, hair_rect.inflate(3, 3))
        hair_color = _darken(self.weapon_handle, 0.72)
        pygame.draw.ellipse(surface, hair_color, hair_rect)
        fringe = [
            (head_cx - self.facing * head_r // 2, head_cy - head_r + 8),
            (head_cx + self.facing * head_r // 2, head_cy - head_r - head_r // 3),
            (head_cx + self.facing * head_r, head_cy - head_r // 3),
            (head_cx + self.facing * head_r // 3, head_cy - head_r // 2),
        ]
        pygame.draw.polygon(surface, hair_color, fringe)
        pygame.draw.line(surface, self.attack_color,
                         (head_cx - head_r // 2, head_cy - head_r + 5),
                         (head_cx + head_r // 2, head_cy - head_r + 5),
                         max(2, head_r // 5))
        eye_r = max(2, head_r // 5)
        ex_off = self.facing * max(2, head_r // 3)
        eye_y = head_cy - head_r // 8
        pygame.draw.ellipse(surface, (255, 255, 255),
                            (head_cx + ex_off - eye_r, eye_y - eye_r,
                             eye_r * 2 + 2, eye_r * 2))
        pygame.draw.circle(surface, (20, 20, 30),
                           (head_cx + ex_off + self.facing, eye_y), eye_r)
        mouth_y = head_cy + head_r // 2
        pygame.draw.line(surface, OUTLINE,
                         (head_cx + self.facing * 2, mouth_y),
                         (head_cx + self.facing * 8, mouth_y - 1), 2)

        if self.state == S_ATTACK and self.current_attack is not None:
            if self.current_attack.in_active:
                pygame.draw.circle(surface, self.attack_color,
                                   (head_cx, head_cy), head_r + 6, 3)

        self._draw_debug_boxes(surface)

    def _draw_sprite_asset(self, surface):
        image = sprite_fighter.frame_for_player(
            self.character["sprite_asset"], self
        )
        target_scale = 0.9
        if self.state == S_ATTACK and self.current_attack is not None:
            name = self.current_attack.data.name
            if name.startswith("crouch_"):
                target_scale = 0.70
            elif name.startswith("air_"):
                target_scale = 0.86
        target_h = int(self.height * target_scale)
        size = (
            max(1, int(image.get_width() * target_h / image.get_height())),
            target_h,
        )
        image = pygame.transform.scale(image, size)
        surface.blit(
            image,
            image.get_rect(midbottom=(self.rect.centerx, self.rect.bottom)),
        )

    def _draw_pixel_fighter(self, surface):
        image = pixel_fighter.frame_for_player(self)
        if self.facing < 0:
            image = pygame.transform.flip(image, True, False)
        target_scale = 0.42 if self.state == S_KNOCKDOWN else 0.9
        if self.state == S_ATTACK and self.current_attack is not None:
            name = self.current_attack.data.name
            if name.startswith("crouch_"):
                target_scale = 0.70
            elif name.startswith("air_"):
                target_scale = 0.86
        target_h = int(self.height * target_scale)
        scale = target_h / image.get_height()
        size = (
            max(1, int(image.get_width() * scale)),
            target_h,
        )
        image = pygame.transform.scale(image, size)
        surface.blit(image, image.get_rect(midbottom=(self.rect.centerx, self.rect.bottom)))

    def _stick_line(self, surface, p1, p2, color, thickness):
        pygame.draw.line(surface, color, p1, p2, thickness)
        pygame.draw.circle(surface, color, (int(p1[0]), int(p1[1])), thickness // 2)
        pygame.draw.circle(surface, color, (int(p2[0]), int(p2[1])), thickness // 2)

    def _joint_from(self, x, y, angle_deg, length):
        a = math.radians(angle_deg)
        return x + math.cos(a) * length, y + math.sin(a) * length

    def _draw_foot(self, surface, color, x, y):
        w = int(self.stick_thick * 2.4)
        h = int(self.stick_thick * 1.1)
        foot = pygame.Rect(x - w // 2, y - h // 2, w, h)
        pygame.draw.rect(surface, OUTLINE, foot.inflate(3, 3), border_radius=3)
        pygame.draw.rect(surface, color, foot, border_radius=2)

    def _draw_knockdown(self, surface, body_c):
        r = self.rect
        ground = settings.GROUND_Y
        length = int(self.height * 0.95)
        thickness = self.stick_thick * 2
        x = r.centerx - length // 2
        y = ground - thickness // 2 - 2
        self._stick_line(surface, (x, y), (x + length, y), OUTLINE, thickness + 4)
        self._stick_line(surface, (x, y), (x + length, y), body_c, thickness)
        head_cx = x + thickness if self.facing == 1 else x + length - thickness
        pygame.draw.circle(surface, OUTLINE, (head_cx, y), self.head_r + 3)
        pygame.draw.circle(surface, body_c, (head_cx, y), self.head_r)
        er = max(3, self.head_r // 3)
        pygame.draw.line(surface, (255, 80, 80),
                         (head_cx - er, y - er), (head_cx + er, y + er), 3)
        pygame.draw.line(surface, (255, 80, 80),
                         (head_cx - er, y + er), (head_cx + er, y - er), 3)

    def _draw_debug_boxes(self, surface):
        if not settings.DEBUG_HITBOXES:
            return
        hb = self.get_hitbox()
        if hb is not None:
            pygame.draw.rect(surface, self.attack_color, hb, 3)
        pygame.draw.rect(surface, (60, 220, 90), self.get_hurtbox(), 1)

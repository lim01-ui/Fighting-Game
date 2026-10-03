# game/fight_scene.py
"""
Fight scene with best-of-3 matches and an optional endless training mode.
Round transitions are animated via ui/transitions.py.
"""

import pygame

import settings
from characters import character_data
from characters.player import Player
from combat.combo import ComboTracker
from ai.bot import Bot
from effects.hit_spark import HitSpark, BlockSpark
from effects.screen_shake import ScreenShake
from effects.camera_punch import CameraPunch
from effects.flash import Flash
from effects import damage_numbers
from effects.projectiles import Projectile
from effects.special_moves import SpecialEffect, UltimatePresentation
from effects import combat_behaviors
from effects.combo_display import ComboDisplay
from effects import victory_pose
from stages import stages

from game.round_manager import (
    RoundManager,
    ROUND_COUNTDOWN, ROUND_FIGHTING, ROUND_OVER, ROUND_HOLD,
)
from game.match_manager import MatchManager
from ui import transitions
from ui import vs_screen
from audio import sound_fx
from audio import music
from network.lan import ACTIONS


STAGE_KEYS = stages.STAGE_KEYS

_SPECIAL_KINDS = {
    "rook": "slash",
    "vex": "double_slash",
    "golem": "shockwave",
    "sable": "whip_arc",
    "nova": "nova_orbit",
    "iron": "aura",
    "jinx": "knife_fan",
    "kestrel": "prismatic_wave",
    "bramble": "leafburst",
    "ash": "afterimage",
    "ryoko": "spin_kick",
    "volt": "meteor_burst",
    "saikyo": "spin_kick",
    "renegade": "double_slash",
    "soldier": "void_ring",
}


# ---- HUD helpers ----
def draw_health_bar(surface, x, y, w, h, current, maxv, color, flip=False,
                    trail_current=None):
    pygame.draw.rect(surface, (15, 18, 28), (x, y, w, h), border_radius=7)
    ratio = max(0.0, current / maxv)
    fg = int(w * ratio)
    fx = x + (w - fg) if flip else x
    if trail_current is not None:
        trail_width = int(w * max(0.0, trail_current / maxv))
        trail_x = x + (w - trail_width) if flip else x
        if trail_width > fg:
            pygame.draw.rect(
                surface, (255, 184, 66),
                (trail_x, y, trail_width, h), border_radius=6,
            )
    if fg > 0:
        pygame.draw.rect(surface, color, (fx, y, fg, h), border_radius=6)
    if fg > 8:
        pygame.draw.line(surface, tuple(min(255, c + 45) for c in color),
                         (fx + 4, y + 3), (fx + max(4, fg - 4), y + 3), 2)
    pygame.draw.rect(surface, (220, 225, 240), (x, y, w, h), 2, border_radius=7)


def draw_ultimate_meter(surface, x, y, w, value, color, flip=False):
    """Draw the meter that powers each fighter's ultimate move."""
    h = 11
    pygame.draw.rect(surface, (18, 20, 31), (x, y, w, h), border_radius=5)
    fill = int(w * max(0.0, min(100.0, value)) / 100)
    fill_x = x + w - fill if flip else x
    if fill:
        pygame.draw.rect(surface, color, (fill_x, y, fill, h), border_radius=5)
    pygame.draw.rect(surface, (195, 205, 225), (x, y, w, h), 1, border_radius=5)


def draw_round_pips(surface, x, y, wins, wins_needed, color, right_align=False):
    r = 10
    gap = 28
    for i in range(wins_needed):
        cx = x + i * gap if not right_align else x - i * gap
        filled = i < wins
        pygame.draw.circle(surface, color if filled else (60, 60, 60), (cx, y), r)
        pygame.draw.circle(surface, settings.WHITE, (cx, y), r, 2)


def draw_timer(surface, font, x, y, seconds):
    color = (255, 80, 80) if seconds <= 10 else settings.WHITE
    img = font.render(str(seconds), True, color)
    rect = img.get_rect(center=(x, y))
    surface.blit(img, rect)


def _draw_center_text(surface, font, text, y, color=None):
    color = color or settings.WHITE
    img = font.render(text, True, color)
    rect = img.get_rect(center=(settings.WINDOW_WIDTH // 2, y))
    surface.blit(img, rect)


class _VirtualKeys:
    def __init__(self, player, action_values):
        self.values = {
            player._key(player.keymap[action]): action_values[action]
            for action in ACTIONS[:7]
        }

    def __getitem__(self, key):
        return self.values.get(key, False)


# ---- Combat ----
def _spawn_hit_effects(sparks, flashes, attack_name, cx, cy, color, blocked, shake):
    if blocked:
        sparks.append(BlockSpark(cx, cy))
        shake.kick(3, 5)
        flashes.append(Flash((100, 180, 255), life=5, max_alpha=38))
        sound_fx.play("block")
        return
    if attack_name in ("light", "crouch_light", "air_light"):
        sparks.append(HitSpark(cx, cy, color,
                               count=settings.HIT_SPARK_COUNT_LIGHT,
                               speed=5, life=settings.HIT_SPARK_LIFE))
        shake.kick(*settings.SHAKE_LIGHT)
        sound_fx.play("hit_light")
    elif attack_name in ("heavy", "crouch_heavy", "air_heavy"):
        sparks.append(HitSpark(cx, cy, color,
                               count=settings.HIT_SPARK_COUNT_HEAVY,
                               speed=8, life=settings.HIT_SPARK_LIFE))
        shake.kick(*settings.SHAKE_HEAVY)
        flashes.append(Flash(color, life=4, max_alpha=38))
        sound_fx.play("hit_heavy")
    else:
        sparks.append(HitSpark(cx, cy, color,
                               count=settings.HIT_SPARK_COUNT_SPECIAL,
                               speed=11, life=settings.HIT_SPARK_LIFE))
        shake.kick(*settings.SHAKE_SPECIAL)
        flashes.append(Flash(color, life=6, max_alpha=68))
        sound_fx.play("hit_special")


def _resolve_combat(attacker, defender, attacker_combo, sparks, flashes, shake,
                    camera_punch, damage_numbers_list, combo_display):
    hb = attacker.get_hitbox()
    if hb is None: return False
    if attacker.attack_has_connected: return False
    if defender.state == "KNOCKDOWN": return False
    hurtbox = defender.get_hurtbox()
    if not hb.colliderect(hurtbox): return False

    defender_is_blocking = (
        defender.on_ground
        and defender._holding_back
        and defender.state not in ("HITSTUN", "BLOCKSTUN", "KNOCKDOWN")
    )

    contact = hb.clip(hurtbox)
    cx = contact.centerx if contact.width else hb.centerx
    cy = contact.centery if contact.height else hb.centery

    defender.receive_hit(attacker.current_attack, blocked=defender_is_blocking)
    attacker.mark_attack_connected()

    _data = attacker.current_attack.data
    if defender_is_blocking:
        _dealt = int(_data.damage * defender.defense * settings.BLOCK_REDUCTION)
    else:
        _dealt = int(_data.damage * defender.defense)
    _dealt = max(1, _dealt)
    attacker.gain_ultimate_meter(_dealt)
    defender.gain_ultimate_meter(_dealt)
    damage_numbers.spawn(damage_numbers_list, cx, cy - 20, _dealt,
                         blocked=defender_is_blocking)

    name = attacker.current_attack.data.name
    if not defender_is_blocking:
        impact_strength = (
            0.075 if name == "ultimate"
            else 0.055 if name in ("special", "heavy", "crouch_heavy", "air_heavy")
            else 0.025
        )
        camera_punch.kick(
            impact_strength, 12 if name == "ultimate" else 8,
            (cx, cy),
        )
    pause = (
        settings.HIT_PAUSE_FRAMES_LIGHT
        if name.endswith("light") else
        settings.HIT_PAUSE_FRAMES_HEAVY
        if name.endswith("heavy") else
        settings.HIT_PAUSE_FRAMES_SPECIAL
        if name in ("special", "ultimate") else
        settings.HIT_PAUSE_FRAMES
    )
    attacker.hit_pause = pause
    defender.hit_pause = pause

    if defender_is_blocking:
        attacker_combo.reset()
        combo_display.reset()
        reflect = defender.character.get("weapon_effect", {}).get("shield_reflect", 0.0)
        if reflect > 0:
            back = max(1, int(_dealt * reflect * 4))
            attacker.health = max(0, attacker.health - back)
            damage_numbers.spawn(damage_numbers_list,
                                 attacker.rect.centerx, attacker.rect.top - 20,
                                 back, blocked=True)
            sparks.append(BlockSpark(attacker.rect.centerx, attacker.rect.centery))
    else:
        attacker_combo.register_hit()
        combo_display.register_hit(_dealt)
        # Stun-on-hit (Volt's bolt)
        stun = combat_behaviors.consume_stun_on_hit(attacker)
        if stun > 0:
            defender.state_timer = max(defender.state_timer, stun)
            defender.state = "HITSTUN"

    # Multi-hit: if the behavior allows extra hits, mark not-connected again
    is_ultimate = _data.name == "ultimate"
    beh = (
        character_data.ultimate_for(attacker.character["key"])
        if is_ultimate else attacker.character.get("special_behavior", {})
    )
    extra_hits = beh.get("extra_hits", 0)
    if extra_hits > 0 and not defender_is_blocking:
        # Store a counter on the attacker so the same special can hit again
        counter = getattr(attacker, "_multi_hit_counter", 0)
        if counter < extra_hits:
            attacker._multi_hit_counter = counter + 1
            attacker.current_attack.has_connected = False
        else:
            attacker._multi_hit_counter = 0

    # Pierce: hitbox keeps going through the defender
    if beh.get("pierce", False):
        # Reset on next frame anyway; no early exit
        pass

    _spawn_hit_effects(sparks, flashes, name, cx, cy,
                       attacker.attack_color, defender_is_blocking, shake)
    if defender.health <= 0:
        defender.go_knockdown()
    return True


# ---- Main ----
def run_fight(screen, clock, difficulty_name=None, training_mode=False,
              p1_character="rook", p2_character="rook",
              stage_key="sunset", palette_key="classic",
              network_peer=None, local_player=1):
    if network_peer is not None and local_player not in (1, 2):
        raise ValueError("local_player must be 1 or 2 for a LAN match")

    fonts = {
        "small": pygame.font.SysFont("Arial", 20),
        "mid":   pygame.font.SysFont("Arial", 30, bold=True),
        "big":   pygame.font.SysFont("Arial", 44, bold=True),
        "huge":  pygame.font.SysFont("Arial", 96, bold=True),
    }
    font = fonts["mid"]
    timer_font = pygame.font.SysFont("Arial", 56, bold=True)

    match = MatchManager()
    bot = None
    sparks = []
    shake = ScreenShake()
    camera_punch = CameraPunch()
    flashes = []
    damage_numbers_list = []
    projectiles = []
    special_effects = []
    ultimate_presentations = []
    extra_boxes = []
    combo_display_p1 = ComboDisplay(300, 170)
    combo_display_p2 = ComboDisplay(settings.WINDOW_WIDTH - 300, 170)

    def make_players():
        p1 = Player(300, settings.GROUND_Y - 150,
                    character_key=p1_character, keymap=settings.P1_KEYS, facing=1)
        p2 = Player(900, settings.GROUND_Y - 150,
                    character_key=p2_character, keymap=settings.P2_KEYS, facing=-1)
        return p1, p2

    p1, p2 = make_players()
    p1._opponent_ref = p2
    p2._opponent_ref = p1
    combo_on_p2 = ComboTracker()
    combo_on_p1 = ComboTracker()

    if difficulty_name:
        bot = Bot(player=p2, opponent=p1, difficulty_name=difficulty_name)

    # Show the VS intro screen once, at the start of the match
    p2_label = (
        "LAN PLAYER 2" if network_peer is not None
        else "TRAINING DUMMY" if training_mode
        else ("BOT (" + bot.diff.name + ")") if bot
        else "PLAYER 2"
    )
    vs_result = vs_screen.run_vs_screen(
        screen, clock,
        p1_key=p1_character, p2_key=p2_character,
        p1_label="PLAYER 1",
        p2_label=p2_label,
        stage_key=stage_key,
    )
    if vs_result is None:
        return "MENU"
    music.play("fight", volume=0.3)

    round_mgr = RoundManager(round_number=match.round_number,
                             timer_seconds=99)
    if training_mode:
        round_mgr.state = ROUND_FIGHTING

    t = 0.0
    ko_slowmo = 0
    ko_flash_done = False
    round_end_registered = False
    round_end_reason = "ko"

    paused = False
    pause_selected = 0
    pause_options = ["RESUME", "RESET ROUND", "QUIT TO MENU"]
    training_dummy_modes = ("STAND", "BLOCK", "ATTACK")
    training_dummy_mode = "STAND"
    training_attack_timer = 0
    training_damage = 0
    show_controls = False
    show_move_list = False
    combat_callout = ""
    combat_callout_color = settings.WHITE
    combat_callout_timer = 0
    p1_health_trail = p1.max_health
    p2_health_trail = p2.max_health
    network_local_rematch = False
    network_local_leave = False
    network_waiting = False

    def reset_round_state():
        nonlocal match, round_mgr, ko_slowmo, ko_flash_done, round_end_registered, round_end_reason
        nonlocal camera_punch
        nonlocal training_attack_timer, training_damage, p1_health_trail, p2_health_trail
        nonlocal combat_callout_timer
        p1.reset(); p2.reset()
        combo_on_p1.reset(); combo_on_p2.reset()
        combo_display_p1.reset(); combo_display_p2.reset()
        sparks.clear(); flashes.clear()
        camera_punch = CameraPunch()
        projectiles.clear(); special_effects.clear(); damage_numbers_list.clear()
        ultimate_presentations.clear()
        round_mgr = RoundManager(round_number=match.round_number,
                                 timer_seconds=99)
        if training_mode:
            round_mgr.state = ROUND_FIGHTING
        ko_slowmo = 0
        ko_flash_done = False
        round_end_registered = False
        round_end_reason = "ko"
        training_attack_timer = 0
        if training_mode:
            training_damage = 0
            combo_display_p1.best_hits = 0
        p1_health_trail = p1.health
        p2_health_trail = p2.health
        combat_callout_timer = 0

    def start_new_match():
        nonlocal match
        match = MatchManager()
        reset_round_state()

    while True:
        dt = clock.tick(settings.FPS)
        t += dt / 1000.0

        # INPUT
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if network_peer is not None and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    network_local_leave = True
                    continue
                if match.match_over and event.key in (
                    pygame.K_RETURN, pygame.K_SPACE, pygame.K_r,
                ):
                    network_local_rematch = True
                    continue
                if event.key in (pygame.K_p, pygame.K_r):
                    continue
            if match.match_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "MENU"
                if network_peer is not None:
                    continue
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_r):
                    start_new_match()
                continue
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if not paused:
                    paused = True
                    pause_selected = 0
                else:
                    paused = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                paused = not paused
                pause_selected = 0
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_round_state()
                paused = False
            if training_mode and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    mode_index = training_dummy_modes.index(training_dummy_mode)
                    training_dummy_mode = training_dummy_modes[
                        (mode_index + 1) % len(training_dummy_modes)
                    ]
                    training_attack_timer = 0
                    p2._holding_back = training_dummy_mode == "BLOCK"
                    sound_fx.play("menu_confirm")
                elif event.key == pygame.K_v:
                    show_move_list = not show_move_list
                    sound_fx.play("menu_confirm")
            if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
                show_controls = not show_controls
            if paused and event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    pause_selected = (pause_selected + 1) % len(pause_options)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    pause_selected = (pause_selected - 1) % len(pause_options)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    choice = pause_options[pause_selected]
                    if choice == "RESUME":
                        paused = False
                    elif choice == "RESET ROUND":
                        reset_round_state()
                        paused = False
                    elif choice == "QUIT TO MENU":
                        return "MENU"

        keys = pygame.key.get_pressed()
        p1_keys = p2_keys = keys
        network_ready = True
        if network_peer is not None:
            local_values = {
                action: bool(keys[p1._key(settings.P1_KEYS[action])])
                for action in ACTIONS
                if action not in ("rematch", "leave")
            }
            local_values["rematch"] = network_local_rematch
            local_values["leave"] = network_local_leave
            remote_values = network_peer.poll_inputs(local_values)
            if remote_values is None:
                network_ready = False
                network_waiting = True
            else:
                network_local_rematch = False
                network_local_leave = False
                network_waiting = False
                if remote_values["leave"] or local_values["leave"]:
                    return "MENU"
                if match.match_over and (
                    remote_values["rematch"] or local_values["rematch"]
                ):
                    start_new_match()
            p1_values, p2_values = (
                (local_values, remote_values or {})
                if local_player == 1
                else (remote_values or {}, local_values)
            )
            p1_keys = _VirtualKeys(p1, p1_values)
            p2_keys = _VirtualKeys(p2, p2_values)

        # UPDATE
        if not paused and network_ready:
            do_update = True
            if ko_slowmo > 0:
                ko_slowmo -= 1
                do_update = (ko_slowmo % 3 == 0)

            if do_update:
                round_event = None if training_mode else round_mgr.update(p1, p2)
                if training_mode:
                    round_mgr.state = ROUND_FIGHTING
                _prev = getattr(round_mgr, "_prev_state", None)
                if _prev is None:
                    if round_mgr.state == ROUND_COUNTDOWN:
                        sound_fx.play("round_ready", volume=0.7)
                    elif training_mode and round_mgr.state == ROUND_FIGHTING:
                        sound_fx.play("round_fight", volume=0.9)
                elif _prev == ROUND_COUNTDOWN and round_mgr.state == ROUND_HOLD:
                    sound_fx.play("round_fight", volume=0.9)
                round_mgr._prev_state = round_mgr.state

                if round_mgr.accepts_input:
                    p1.handle_input(p1_keys)
                    if network_peer is not None:
                        p2.handle_input(p2_keys)
                    elif bot is None and not training_mode:
                        p2.handle_input(p2_keys)
                    elif bot is not None:
                        bot.update()
                    elif training_mode:
                        p2._holding_back = training_dummy_mode == "BLOCK"
                        if training_dummy_mode == "ATTACK":
                            if training_attack_timer > 0:
                                training_attack_timer -= 1
                            elif p2.state not in (
                                "ATTACK", "HITSTUN", "BLOCKSTUN", "KNOCKDOWN"
                            ):
                                p2._start_attack("light")
                                training_attack_timer = 60

                p1.update(opponent=p2)
                p2.update(opponent=p1)

                if round_mgr.is_fighting:
                    # Fire a projectile once per special move, on the first active frame
                    for attacker, defender in ((p1, p2), (p2, p1)):
                        atk = attacker.current_attack
                        if atk is None:
                            attacker._special_spawned = False
                            if getattr(attacker, "_projectile_fired", False):
                                attacker._projectile_fired = False
                            continue
                        eff = attacker.character.get("weapon_effect", {})
                        ultimate = character_data.ultimate_for(
                            attacker.character["key"]
                        )
                        is_ultimate = atk.data.name == "ultimate"
                        proj_kind = (
                            ultimate.get("projectile")
                            if is_ultimate else eff.get("projectile")
                        )
                        stun_frames = (
                            ultimate.get("stun_frames", 0)
                            if is_ultimate else attacker.character.get(
                                "special_behavior", {}
                            ).get("stun_frames", 0)
                        )
                        special_active = (
                            atk.data.name in ("special", "ultimate")
                            and atk.in_active
                        )
                        if (special_active
                                and not getattr(attacker, "_special_spawned", False)):
                            char_key = attacker.character["key"]
                            kind = (
                                ultimate["effect"]
                                if is_ultimate
                                else _SPECIAL_KINDS.get(char_key, "slash")
                            )
                            if kind not in ("orb", "spark"):
                                special_effects.append(SpecialEffect(
                                    kind,
                                    attacker.rect.centerx,
                                    attacker.rect.centery,
                                    attacker.facing,
                                    attacker.attack_color,
                                ))
                            attacker._special_spawned = True

                        if (special_active and proj_kind
                                and not getattr(attacker, "_projectile_fired", False)):
                            muzzle_x = attacker.rect.centerx + attacker.facing * (attacker.width // 2 + 15)
                            muzzle_y = attacker.rect.centery - 20
                            speed = {"orb": 10, "knife": 14, "spark": 11}.get(
                                proj_kind, 10
                            )
                            projectile_count = (
                                ultimate.get("projectiles", 1)
                                if is_ultimate else
                                attacker.character.get(
                                    "special_behavior", {}
                                ).get("projectiles", 1)
                            )
                            vertical_spread = (
                                ultimate.get("projectile_spread", 0)
                                if is_ultimate else 36
                            )
                            for projectile_index in range(projectile_count):
                                if projectile_count == 1:
                                    vertical_velocity = 0
                                else:
                                    spread_position = (
                                        projectile_index / (projectile_count - 1) - 0.5
                                    )
                                    vertical_velocity = spread_position * (
                                        vertical_spread / 10
                                    )
                                projectiles.append(Projectile(
                                    muzzle_x, muzzle_y,
                                    vx=speed,
                                    owner_facing=attacker.facing,
                                    color=attacker.attack_color,
                                    kind=proj_kind,
                                    damage=max(
                                        1, int(atk.data.damage / projectile_count)
                                    ),
                                    hitstun=max(
                                        atk.data.hitstun,
                                        stun_frames,
                                    ),
                                    owner=attacker,
                                    vy=vertical_velocity,
                                ))
                            attacker._stun_on_hit = 0
                            sound_fx.play("projectile_launch", volume=0.65)
                            attacker._projectile_fired = True

                        if atk.is_finished:
                            attacker._special_spawned = False

                    if (round_mgr.timer_display <= 10
                            and round_mgr.timer_display > 0
                            and round_mgr.timer_frames % 60 == 0):
                        sound_fx.play("timer_warn")
                    for _f in (p1, p2):
                        _was = getattr(_f, "_was_attacking", False)
                        _now = _f.is_attacking
                        if _now and not _was:
                            attack_name = _f.current_attack.data.name
                            sound_category = (
                                "special" if attack_name in ("special", "ultimate")
                                else "light" if attack_name.endswith("light")
                                else "heavy" if attack_name.endswith("heavy")
                                else attack_name
                            )
                            sound_fx.play(
                                "ultimate" if attack_name == "ultimate"
                                else f"attack_{sound_category}",
                                volume=0.9 if attack_name == "ultimate" else 0.62,
                            )
                            if attack_name == "ultimate":
                                camera_punch.kick(
                                    0.045, 30,
                                    (_f.rect.centerx, _f.rect.centery),
                                )
                                ultimate_name = character_data.ultimate_for(
                                    _f.character["key"]
                                )["name"]
                                ultimate_presentations.append(UltimatePresentation(
                                    _f.rect.centerx,
                                    _f.rect.centery,
                                    _f.attack_color,
                                    _f.character["name"],
                                    ultimate_name,
                                    effect_kind=character_data.ultimate_for(
                                        _f.character["key"]
                                    )["effect"],
                                ))
                        _f._was_attacking = _now
                    p2_health_before = p2.health
                    player_hit = _resolve_combat(
                        p1, p2, combo_on_p2, sparks, flashes,
                        shake, camera_punch, damage_numbers_list,
                        combo_display_p1,
                    )
                    if player_hit:
                        training_damage += (
                            max(0, int(p2_health_before - p2.health))
                            if training_mode else 0
                        )
                        combat_callout = (
                            "BLOCK!" if p2.state == "BLOCKSTUN" else "HIT!"
                        )
                        combat_callout_color = (
                            (120, 195, 255)
                            if p2.state == "BLOCKSTUN"
                            else (255, 225, 110)
                        )
                        combat_callout_timer = 28
                    p1_health_before = p1.health
                    opponent_hit = _resolve_combat(
                        p2, p1, combo_on_p1, sparks, flashes,
                        shake, camera_punch, damage_numbers_list,
                        combo_display_p2,
                    )
                    if opponent_hit:
                        combat_callout = (
                            "BLOCK!" if p1.state == "BLOCKSTUN" else "HIT!"
                        )
                        combat_callout_color = (
                            (120, 195, 255)
                            if p1.state == "BLOCKSTUN"
                            else (255, 225, 110)
                        )
                        combat_callout_timer = 28
                    if p1.health < p1_health_before:
                        combat_callout = "BLOCKED!" if p1.state == "BLOCKSTUN" else "HIT!"
                    combo_on_p1.update(); combo_on_p2.update()

                if training_mode:
                    p1.health = p1.max_health
                    if p2.health <= 0:
                        p2.reset()
                        combo_on_p1.reset()

                if round_event == "round_ended":
                    round_end_reason = "ko" if min(p1.health, p2.health) <= 0 else "time"
                    if round_end_reason == "ko":
                        sound_fx.play("ko")
                    ko_slowmo = settings.KO_SLOWMO_FRAMES
                    shake.kick(*settings.SHAKE_KO)
                    if not ko_flash_done:
                        flashes.append(Flash((255, 255, 255),
                                             life=settings.KO_FLASH_LIFE,
                                             max_alpha=230))
                        ko_flash_done = True
                    match.register_round_winner(round_mgr.winner)
                    round_end_registered = True
                    if match.match_over:
                        sound_fx.play("match_win")

                if (round_mgr.is_over and round_mgr.over_pause_done
                        and round_end_registered and not match.match_over):
                    match.next_round()
                    p1.reset(); p2.reset()
                    combo_on_p1.reset(); combo_on_p2.reset()
                    combo_display_p1.reset(); combo_display_p2.reset()
                    sparks.clear()
                    round_mgr = RoundManager(round_number=match.round_number,
                                             timer_seconds=99)
                    ko_slowmo = 0
                    ko_flash_done = False
                    round_end_registered = False

            # Update projectiles and check collision
            alive = []
            for pr in projectiles:
                if pr.update():
                    continue
                alive.append(pr)
                # Check hit
                for victim in (p1, p2):
                    if victim is pr.owner:
                        continue
                    if pr.rect.colliderect(victim.get_hurtbox()):
                        blocked = (victim.on_ground and victim._holding_back
                                   and victim.state not in ("HITSTUN", "BLOCKSTUN", "KNOCKDOWN"))
                        incoming = pr.damage * victim.defense
                        dmg = int(incoming * settings.BLOCK_REDUCTION) if blocked else int(incoming)
                        dmg = max(1, dmg)
                        victim.health = max(0, victim.health - dmg)
                        attacker_combo = combo_on_p2 if pr.owner is p1 else combo_on_p1
                        attacker_display = combo_display_p1 if pr.owner is p1 else combo_display_p2
                        if blocked:
                            victim.state = "BLOCKSTUN"
                            victim.state_timer = 8
                            if pr.owner is not None:
                                pr.owner.gain_ultimate_meter(dmg)
                            victim.gain_ultimate_meter(dmg)
                            attacker_combo.reset()
                            attacker_display.reset()
                            sparks.append(BlockSpark(pr.x, pr.y))
                            shake.kick(3, 5)
                            combat_callout = "BLOCK!"
                            combat_callout_color = (120, 195, 255)
                            combat_callout_timer = 28
                        else:
                            victim.state = "HITSTUN"
                            victim.state_timer = pr.hitstun
                            victim.rect.x += (1 if pr.vx > 0 else -1) * 6
                            if pr.owner is not None:
                                pr.owner.gain_ultimate_meter(dmg)
                                attacker_combo.register_hit()
                                attacker_display.register_hit(dmg)
                                pr.owner.hit_pause = settings.HIT_PAUSE_FRAMES_SPECIAL
                            victim.gain_ultimate_meter(dmg)
                            victim.hit_pause = settings.HIT_PAUSE_FRAMES_SPECIAL
                            sparks.append(HitSpark(
                                pr.x, pr.y, pr.color,
                                count=settings.HIT_SPARK_COUNT_SPECIAL,
                                speed=11, life=settings.HIT_SPARK_LIFE,
                            ))
                            shake.kick(*settings.SHAKE_SPECIAL)
                            camera_punch.kick(
                                0.05, 9, (pr.x, pr.y),
                            )
                            flashes.append(Flash(pr.color, life=5, max_alpha=60))
                            combat_callout = "HIT!"
                            combat_callout_color = (255, 225, 110)
                            combat_callout_timer = 28
                        if training_mode and pr.owner is p1:
                            training_damage += dmg
                        damage_numbers.spawn(damage_numbers_list,
                                             pr.x, pr.y - 20, dmg, blocked=blocked)
                        if victim.health <= 0:
                            victim.go_knockdown()
                        pr.life = 0
                        break
            projectiles = [pr for pr in alive if pr.life > 0]
            special_effects = [se for se in special_effects if not se.update()]
            ultimate_presentations = [
                presentation for presentation in ultimate_presentations
                if not presentation.update()
            ]
            sparks = [s for s in sparks if not s.update()]
            flashes = [f for f in flashes if not f.update()]
            damage_numbers_list = [d for d in damage_numbers_list if not d.update()]
            combo_display_p1.update()
            combo_display_p2.update()
            if combat_callout_timer > 0:
                combat_callout_timer -= 1
            p1_health_trail = max(p1.health, p1_health_trail - 0.6)
            p2_health_trail = max(p2.health, p2_health_trail - 0.6)
            ox, oy = shake.update()

        # DRAW world
        world = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        # Parallax scroll: -1.0 (left of center) .. 1.0 (right of center)
        _midpoint = (p1.rect.centerx + p2.rect.centerx) / 2
        _center = settings.WINDOW_WIDTH / 2
        _scroll = max(-1.0, min(1.0, (_midpoint - _center) / _center))
        stages.draw(world, stage_key, t, scroll=_scroll, palette_key=palette_key)

        for fighter in (p1, p2):
            sh = pygame.Surface((fighter.width + 20, 14), pygame.SRCALPHA)
            pygame.draw.ellipse(sh, (0, 0, 0, 90), sh.get_rect())
            world.blit(sh, (fighter.rect.centerx - (fighter.width + 20) // 2,
                            settings.GROUND_Y - 6))

        p1.draw(world); p2.draw(world)
        for s in sparks:
            s.draw(world)
        for se in special_effects:
            se.draw(world)
        for pr in projectiles:
            pr.draw(world)
        for d in damage_numbers_list:
            d.draw(world)

        screen.fill((0, 0, 0))
        camera_punch.draw(world, screen, (ox, oy))
        for presentation in ultimate_presentations:
            presentation.draw(screen, (ox, oy))

        if paused:
            overlay = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((8, 8, 16, 180))
            screen.blit(overlay, (0, 0))
            title = fonts["big"].render("PAUSED", True, settings.WHITE)
            screen.blit(title, title.get_rect(center=(settings.WINDOW_WIDTH // 2, 220)))
            for idx, label in enumerate(pause_options):
                color = (255, 220, 90) if idx == pause_selected else settings.WHITE
                txt = fonts["mid"].render(label, True, color)
                rect = txt.get_rect(center=(settings.WINDOW_WIDTH // 2, 330 + idx * 70))
                screen.blit(txt, rect)
            hint = fonts["small"].render("W/S or arrow keys to move • Enter to confirm", True, (200, 200, 200))
            screen.blit(hint, hint.get_rect(center=(settings.WINDOW_WIDTH // 2, 560)))

        if network_waiting:
            wait_overlay = pygame.Surface(
                (settings.WINDOW_WIDTH, 58), pygame.SRCALPHA
            )
            wait_overlay.fill((8, 12, 24, 210))
            wait_text = fonts["small"].render(
                "WAITING FOR OTHER PLAYER...",
                True, (130, 215, 255),
            )
            screen.blit(
                wait_overlay,
                (0, settings.WINDOW_HEIGHT - wait_overlay.get_height()),
            )
            screen.blit(
                wait_text,
                wait_text.get_rect(
                    center=(settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT - 29)
                ),
            )

        # HUD
        bar_w, bar_h = 400, 30
        left_x = 40
        right_x = settings.WINDOW_WIDTH - bar_w - 40
        draw_health_bar(screen, left_x, 30, bar_w, bar_h,
                        p1.health, p1.max_health,
                        settings.HEALTH_FG_P1, flip=False,
                        trail_current=p1_health_trail)
        draw_health_bar(screen, right_x, 30, bar_w, bar_h,
                        p2.health, p2.max_health,
                        settings.HEALTH_FG_P2, flip=True,
                        trail_current=p2_health_trail)
        draw_ultimate_meter(screen, left_x, 65, bar_w, p1.ultimate_meter,
                            (255, 206, 75))
        draw_ultimate_meter(screen, right_x, 65, bar_w, p2.ultimate_meter,
                            (255, 108, 130), flip=True)

        p1_name = p1.character["name"]
        p2_name = p2.character["name"]
        p2_label = (
            "LAN PLAYER 2" if network_peer is not None
            else "TRAINING DUMMY" if training_mode
            else f"BOT ({bot.diff.name})" if bot
            else "PLAYER 2"
        )
        screen.blit(font.render(f"P1  {p1_name}", True, settings.WHITE), (left_x, 2))
        p2_header = font.render(f"{p2_label}  {p2_name}", True, settings.WHITE)
        screen.blit(p2_header, (right_x + bar_w - p2_header.get_width(), 2))

        health_font = fonts["small"]
        p1_health = health_font.render(
            f"{max(0, int(p1.health))} / {p1.max_health}", True, settings.WHITE)
        p2_health = health_font.render(
            f"{max(0, int(p2.health))} / {p2.max_health}", True, settings.WHITE)
        screen.blit(p1_health, p1_health.get_rect(center=(left_x + bar_w // 2, 45)))
        screen.blit(p2_health, p2_health.get_rect(center=(right_x + bar_w // 2, 45)))
        p1_meter_label = health_font.render(
            "ULTIMATE READY" if p1.ultimate_meter >= 100
            else f"ULTIMATE {int(p1.ultimate_meter)}%",
            True, (255, 220, 115),
        )
        p2_meter_label = health_font.render(
            "ULTIMATE READY" if p2.ultimate_meter >= 100
            else f"ULTIMATE {int(p2.ultimate_meter)}%",
            True, (255, 160, 175),
        )
        screen.blit(p1_meter_label, (left_x, 78))
        screen.blit(
            p2_meter_label,
            (right_x + bar_w - p2_meter_label.get_width(), 78),
        )

        if not training_mode:
            p1_wins, p2_wins, wins_needed = match.pips_display()
            draw_round_pips(screen, 60, 140, p1_wins, wins_needed,
                            (240, 200, 80), right_align=False)
            draw_round_pips(screen, settings.WINDOW_WIDTH - 60, 140,
                            p2_wins, wins_needed,
                            (240, 200, 80), right_align=True)

        if training_mode:
            timer_img = timer_font.render("∞", True, settings.WHITE)
            screen.blit(timer_img, timer_img.get_rect(
                center=(settings.WINDOW_WIDTH // 2, 60)))
            round_text = "TRAINING"
        else:
            draw_timer(screen, timer_font, settings.WINDOW_WIDTH // 2, 60,
                       round_mgr.timer_display)
            round_text = f"ROUND {match.round_number}"
        round_label = font.render(round_text, True, settings.WHITE)
        screen.blit(round_label, round_label.get_rect(
            center=(settings.WINDOW_WIDTH // 2, 130)))

        if round_mgr.is_fighting:
            combo_display_p1.draw(screen)
            combo_display_p2.draw(screen)
        if training_mode:
            best_combo = combo_display_p1.best_hits
            practice_text = pygame.font.SysFont("Arial", 17, bold=True).render(
                f"BEST {best_combo} HITS   DAMAGE {training_damage}   "
                f"DUMMY {training_dummy_mode} [T]   MOVES [V]   RESET [R]   HELP [H]",
                True, (230, 235, 250),
            )
            screen.blit(practice_text, practice_text.get_rect(
                center=(settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT - 25)))
        elif not show_controls:
            hint_text = (
                "H: CONTROLS   ESC: LEAVE MATCH"
                if network_peer is not None
                else "H: CONTROLS   ESC: PAUSE"
            )
            guide_hint = health_font.render(hint_text, True, (210, 215, 230))
            screen.blit(guide_hint, guide_hint.get_rect(
                center=(settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT - 22)
            ))

        if combat_callout_timer > 0:
            callout = fonts["big"].render(combat_callout, True, combat_callout_color)
            screen.blit(callout, callout.get_rect(
                center=(settings.WINDOW_WIDTH // 2, 145)
            ))

        if show_controls:
            panel = pygame.Surface((680, 310), pygame.SRCALPHA)
            panel.fill((8, 10, 22, 225))
            panel_rect = panel.get_rect(center=(settings.WINDOW_WIDTH // 2, 365))
            screen.blit(panel, panel_rect)
            control_font = pygame.font.SysFont("Arial", 18)
            title = fonts["mid"].render("CONTROLS", True, (255, 225, 110))
            screen.blit(title, title.get_rect(
                center=(panel_rect.centerx, panel_rect.y + 34)
            ))
            control_lines = (
                [("LAN PLAYER CONTROLS", settings.P1_KEYS)]
                if network_peer is not None
                else [("P1", settings.P1_KEYS), ("P2", settings.P2_KEYS)]
            )
            for player_index, (label, keymap) in enumerate(control_lines):
                movement = (
                    f"LEFT {keymap['left']}    RIGHT {keymap['right']}    "
                    f"JUMP {keymap['jump']}"
                )
                attacks = (
                    f"CROUCH {keymap['crouch']}    LIGHT {keymap['light']}    "
                    f"HEAVY {keymap['heavy']}    SPECIAL {keymap['special']}"
                )
                y = panel_rect.y + 68 + player_index * 90
                screen.blit(control_font.render(label, True, settings.WHITE),
                            (panel_rect.x + 28, y))
                screen.blit(control_font.render(movement, True, settings.WHITE),
                            (panel_rect.x + 28, y + 22))
                screen.blit(control_font.render(attacks, True, settings.WHITE),
                            (panel_rect.x + 28, y + 44))
            ultimate_hint = pygame.font.SysFont("Arial", 15, bold=True).render(
                "Deal and take damage to charge meter; at 100%, SPECIAL uses your ULTIMATE.",
                True, (255, 220, 115),
            )
            screen.blit(ultimate_hint, ultimate_hint.get_rect(
                center=(panel_rect.centerx, panel_rect.bottom - 48)
            ))
            close_hint = health_font.render("H: CLOSE", True, (190, 195, 210))
            screen.blit(close_hint, close_hint.get_rect(
                center=(panel_rect.centerx, panel_rect.bottom - 22)
            ))

        if show_move_list and training_mode:
            panel = pygame.Surface((420, 300), pygame.SRCALPHA)
            panel.fill((8, 10, 22, 225))
            panel_rect = panel.get_rect(topleft=(30, 145))
            screen.blit(panel, panel_rect)
            title = health_font.render("PLAYER MOVES", True, (255, 225, 110))
            screen.blit(title, (panel_rect.x + 18, panel_rect.y + 12))
            move_font = pygame.font.SysFont("Arial", 17)
            actions = ("light", "heavy", "special", "ultimate")
            for index, action in enumerate(actions):
                data = p1.attacks[action]
                y = panel_rect.y + 43 + index * 54
                move_name = (
                    character_data.ultimate_for(p1.character["key"])["name"]
                    if action == "ultimate" else action.upper()
                )
                label_text = (
                    f"{settings.P1_KEYS['special'].upper()} ULTIMATE: {move_name}"
                    if action == "ultimate" else
                    f"{settings.P1_KEYS[action].upper()} {move_name} "
                    f"- {data.damage} DAMAGE"
                )
                label = move_font.render(
                    label_text, True,
                    (255, 220, 115) if action == "ultimate" else settings.WHITE,
                )
                frame_data = move_font.render(
                    f"{data.startup} startup / {data.active} active / "
                    f"{data.recovery} recovery / {data.reach} reach",
                    True, (180, 195, 220),
                )
                screen.blit(label, (panel_rect.x + 18, y))
                screen.blit(frame_data, (panel_rect.x + 18, y + 22))

        # ---- Transitions ----
        if round_mgr.state == ROUND_COUNTDOWN:
            transitions.draw_countdown(screen, match.round_number,
                                       round_mgr.countdown_progress, fonts)

        if round_mgr.state == ROUND_OVER and not match.match_over:
            transitions.draw_round_over(screen, round_mgr.winner,
                                        round_end_reason,
                                        round_mgr.over_progress, fonts)

        if match.match_over:
            # Progress is how far into the round-over pause we are
            progress = round_mgr.over_progress if round_mgr.state == ROUND_OVER else 1.0
            if network_peer is not None:
                local_won = (
                    (match.match_winner == "p1" and local_player == 1)
                    or (match.match_winner == "p2" and local_player == 2)
                )
                header = "YOU WIN THE MATCH" if local_won else "YOU LOSE THE MATCH"
                prompt = "ENTER / R = REMATCH     ESC = RETURN TO LOBBY"
                winner_color = p1.color if match.match_winner == "p1" else p2.color
            elif match.match_winner == "p1":
                header = "YOU WIN THE MATCH" if bot else "PLAYER 1 WINS THE MATCH"
                prompt = "ENTER / R = new match     ESC = back to menu"
                winner_color = p1.color
            else:
                header = "BOT WINS THE MATCH" if bot else "PLAYER 2 WINS THE MATCH"
                prompt = "ENTER / R = new match     ESC = back to menu"
                winner_color = p2.color
            rounds_text = f"Rounds: {match.p1_wins} - {match.p2_wins}"
            transitions.draw_match_over(screen, header, rounds_text,
                                        progress, fonts,
                                        winner_color=winner_color,
                                        prompt=prompt)

        for f in flashes:
            f.draw(screen)

        pygame.display.flip()

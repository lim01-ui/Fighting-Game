"""Combat cooldown boundaries and the roster's intended strength tradeoffs."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import math
from collections import defaultdict
import unittest
from unittest.mock import MagicMock, patch

import pygame
import settings
from ai.bot import Bot, B_ATTACK
from characters import character_data
from characters.player import Player, S_GUARD, S_HITSTUN, S_JUMP, S_WALK
from game.round_manager import RoundManager, ROUND_FIGHTING
from game.round_manager import COUNTDOWN_FRAMES, FIGHT_HOLD_FRAMES
from game import fight_scene


class Keys:
    def __init__(self, player, **actions):
        self.pressed = {
            player._key(player.keymap[action])
            for action, pressed in actions.items() if pressed
        }

    def __getitem__(self, code):
        return code in self.pressed


class RosterBalanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1280, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def player(self, key='rook', x=200):
        player = Player(x, 300, key, settings.P1_KEYS.copy())
        player.rect.bottom = settings.GROUND_Y
        return player

    def test_all_fighters_recover_special_only_after_five_simulation_seconds(self):
        self.assertEqual(settings.SPECIAL_COOLDOWN_FRAMES, settings.FPS * 5)
        for key in character_data.ROSTER_ORDER:
            with self.subTest(fighter=key):
                player = self.player(key)
                self.assertTrue(player.special_ready)
                self.assertTrue(player._start_attack('special'))
                for elapsed in range(1, settings.SPECIAL_COOLDOWN_FRAMES):
                    player.update()
                    self.assertFalse(player.special_ready)
                    if elapsed in (1, 150, settings.SPECIAL_COOLDOWN_FRAMES - 1):
                        remaining = player.special_cooldown_frames
                        self.assertFalse(player._start_attack('special'))
                        self.assertEqual(player.special_cooldown_frames, remaining)
                self.assertEqual(player.special_cooldown_frames, 1)
                player.update()
                self.assertTrue(player.special_ready)
                self.assertTrue(player._start_attack('special'))
                self.assertEqual(player.special_cooldown_frames,
                                 settings.SPECIAL_COOLDOWN_FRAMES)

    def test_matches_lock_special_for_five_seconds_after_fight_begins(self):
        for training in (True, False):
            with self.subTest(training=training):
                frame = [0]
                accepted = []
                fight_frame = 1 if training else COUNTDOWN_FRAMES + FIGHT_HOLD_FRAMES
                first_allowed = fight_frame + settings.SPECIAL_COOLDOWN_FRAMES
                original_start = Player._start_attack

                def events():
                    frame[0] += 1
                    return ([pygame.event.Event(pygame.QUIT)]
                            if frame[0] > first_allowed + 2 else [])

                def start(player, kind):
                    result = original_start(player, kind)
                    if result and kind in ('special', 'ultimate'):
                        accepted.append(frame[0])
                    return result

                keys = defaultdict(bool)
                keys[pygame.K_l] = True
                # Cooldowns follow simulation ticks, independent of render count.
                clock = type('Clock', (), {'tick': lambda self, fps: 1000 / 60})()
                with patch.object(fight_scene.vs_screen, 'run_vs_screen', return_value=True), \
                        patch.object(fight_scene.music, 'play'), \
                        patch.object(fight_scene.sound_fx, 'play'), \
                        patch('pygame.event.get', side_effect=events), \
                        patch('pygame.key.get_pressed', return_value=keys), \
                        patch.object(Player, '_start_attack', start), \
                        patch.object(fight_scene.retro, 'present'):
                    self.assertEqual(fight_scene.run_fight(
                        pygame.display.get_surface(), clock, training_mode=training), 'QUIT')
                self.assertEqual(accepted, [first_allowed])

    def test_keybind_overlay_displays_each_players_special_countdown_and_ready_state(self):
        players = [('P1', settings.P1_KEYS, settings.P1_COLOR),
                   ('P2', settings.P2_KEYS, settings.P2_COLOR)]
        with patch.object(fight_scene, 'draw_text_fit', wraps=fight_scene.draw_text_fit) as text:
            panel = fight_scene._make_keybind_overlay(
                1256, players, special_cooldowns=(50, 23))
        labels = [call.args[2] for call in text.call_args_list]
        self.assertIn('5.0S', labels)
        self.assertIn('2.3S', labels)
        with patch.object(fight_scene, 'draw_text_fit', wraps=fight_scene.draw_text_fit) as text:
            ready = fight_scene._make_keybind_overlay(
                1256, players, special_cooldowns=(0, 0))
        self.assertEqual([call.args[2] for call in text.call_args_list].count('READY'), 2)
        self.assertEqual(panel.get_size(), ready.get_size())

    def test_special_and_ultimate_share_timer_without_spending_rejected_meter(self):
        player = self.player('iron')
        self.assertTrue(player._start_attack('special'))
        player._end_attack()
        player.ultimate_meter = 100.0
        position = player.rect.copy()
        with patch('characters.player.combat_behaviors.on_start') as on_start:
            self.assertFalse(player._start_attack('ultimate'))
            on_start.assert_not_called()
        self.assertEqual(player.ultimate_meter, 100.0)
        self.assertEqual(player.rect, position)
        for _ in range(settings.SPECIAL_COOLDOWN_FRAMES):
            player.update()
        player.handle_input(Keys(player, special=True))
        self.assertEqual(player.current_attack.data.name, 'ultimate')
        self.assertEqual(player.ultimate_meter, 0.0)
        self.assertEqual(player.special_cooldown_frames,
                         settings.SPECIAL_COOLDOWN_FRAMES)
        player._end_attack()
        self.assertFalse(player._start_attack('special'))

    def test_interruption_does_not_refund_or_extend_cooldown(self):
        player, enemy = self.player(), self.player('golem', x=500)
        player._start_attack('special')
        enemy._start_attack('heavy')
        player.receive_hit(enemy.current_attack, blocked=False)
        self.assertEqual(player.state, S_HITSTUN)
        self.assertIsNone(player.current_attack)
        self.assertIsNone(player.get_hitbox())
        self.assertEqual(player.special_cooldown_frames,
                         settings.SPECIAL_COOLDOWN_FRAMES)
        for _ in range(30):
            player.update()
        self.assertEqual(player.special_cooldown_frames,
                         settings.SPECIAL_COOLDOWN_FRAMES - 30)
        player.go_knockdown()
        player.update()
        self.assertEqual(player.special_cooldown_frames,
                         settings.SPECIAL_COOLDOWN_FRAMES - 31)

    def test_interrupted_projectile_special_can_fire_again_after_recharging(self):
        player, enemy = self.player('nova'), self.player('golem', x=500)
        player._start_attack('special')
        for _ in range(player.attacks['special'].startup):
            player.update()
        self.assertIsNotNone(player.get_hitbox())
        player._projectile_fired = True
        player._special_spawned = True
        enemy._start_attack('heavy')
        player.receive_hit(enemy.current_attack, blocked=False)
        self.assertIsNone(player.get_hitbox())
        # A rejected request neither restarts the timer nor touches flags.
        self.assertFalse(player._start_attack('special'))
        self.assertTrue(player._projectile_fired)
        for _ in range(settings.SPECIAL_COOLDOWN_FRAMES):
            player.update()
        self.assertTrue(player._start_attack('special'))
        self.assertFalse(player._projectile_fired)
        self.assertFalse(player._special_spawned)

    def test_super_armor_keeps_the_active_move_when_hit(self):
        player, enemy = self.player('iron'), self.player('golem', x=500)
        player._start_attack('special')
        attack = player.current_attack
        self.assertGreater(player.super_armor_frames, 0)
        enemy._start_attack('heavy')
        player.receive_hit(enemy.current_attack, blocked=False)
        self.assertIs(player.current_attack, attack)
        self.assertTrue(player.is_attacking)
        self.assertLess(player.health, player.max_health)

    def test_fighters_have_independent_cooldowns_and_round_reset_clears_them(self):
        first, second = self.player(), self.player('sanya', x=700)
        first._start_attack('special')
        self.assertTrue(second.special_ready)
        for _ in range(40):
            first.update()
        second._start_attack('special')
        self.assertEqual(second.special_cooldown_frames,
                         settings.SPECIAL_COOLDOWN_FRAMES)
        self.assertEqual(first.special_cooldown_frames,
                         settings.SPECIAL_COOLDOWN_FRAMES - 40)
        first.reset()
        self.assertTrue(first.special_ready)
        self.assertEqual(first.special_cooldown_frames, 0)
        self.assertFalse(second.special_ready)
        self.assertTrue(first._start_attack('special'))

    def test_cooldown_uses_updates_and_continues_through_hit_pause(self):
        first, second = self.player(), self.player()
        first._start_attack('special')
        second._start_attack('special')
        with patch('pygame.time.get_ticks', return_value=1_000_000):
            first.handle_input(Keys(first))
            self.assertEqual(first.special_cooldown_frames,
                             settings.SPECIAL_COOLDOWN_FRAMES)
            first.hit_pause = 7
            for _ in range(120):
                first.update()
        with patch('pygame.time.get_ticks', return_value=2):
            for _ in range(120):
                second.update()
        self.assertEqual(first.special_cooldown_frames,
                         settings.SPECIAL_COOLDOWN_FRAMES - 120)
        self.assertEqual(first.special_cooldown_frames, second.special_cooldown_frames)

    def test_unavailable_held_special_does_not_block_movement_guard_or_jump(self):
        player = self.player()
        player._start_attack('special')
        player._end_attack()
        x = player.rect.x
        player.handle_input(Keys(player, special=True, right=True))
        self.assertEqual(player.state, S_WALK)
        self.assertGreater(player.rect.x, x)
        player.handle_input(Keys(player, special=True, block=True))
        self.assertEqual(player.state, S_GUARD)
        self.assertTrue(player._holding_back)
        player.handle_input(Keys(player, special=True, jump=True))
        self.assertEqual(player.state, S_JUMP)
        self.assertFalse(player.on_ground)
        self.assertLess(player.vel_y, 0)

    def test_normal_attacks_remain_available_during_special_cooldown(self):
        for action in ('light', 'heavy'):
            with self.subTest(action=action):
                player = self.player()
                player._start_attack('special')
                player._end_attack()
                player.handle_input(Keys(player, special=True, **{action: True}))
                self.assertEqual(player.current_attack.data.name, action)
                self.assertEqual(player.special_cooldown_frames,
                                 settings.SPECIAL_COOLDOWN_FRAMES)

    def test_bot_uses_normal_attack_when_special_is_unavailable(self):
        player, enemy = self.player(), self.player(x=500)
        player._start_attack('special')
        player._end_attack()
        bot = Bot(player, enemy)
        bot.state = B_ATTACK
        bot.action_frames = 1
        with patch('ai.bot.random.random', return_value=0.0):
            bot._act()
            bot._apply_keys()
        self.assertFalse(bot.keys['special'])
        self.assertEqual(player.current_attack.data.name, 'heavy')

    def test_sanya_is_fastest_and_most_fragile_and_creature_tanks_pay_for_bulk(self):
        players = {key: self.player(key) for key in character_data.ROSTER_ORDER}
        sanya, baseline = players['sanya'], players['raguel']
        for key, player in players.items():
            if key != 'sanya':
                self.assertGreater(sanya.move_speed, player.move_speed)
                self.assertLess(sanya.max_health, player.max_health)
        for key in ('golem', 'choom', 'renegade'):
            with self.subTest(tank=key):
                tank = players[key]
                self.assertGreater(tank.max_health / tank.defense,
                                   baseline.max_health / baseline.defense)
                self.assertLess(tank.move_speed, baseline.move_speed)
                self.assertLess(abs(tank.jump_power), abs(baseline.jump_power))
                self.assertGreater(tank.attacks['heavy'].recovery,
                                   baseline.attacks['heavy'].recovery)
                self.assertGreater(tank.render_height / baseline.render_height, 1.08)
                self.assertLess(tank.render_height / baseline.render_height, 1.15)
                self.assertGreater(tank.get_hurtbox().width, baseline.get_hurtbox().width)

    def test_roster_bonuses_stay_in_moderate_effective_ranges(self):
        for character in character_data.all_characters():
            with self.subTest(fighter=character['key']):
                stats, mods = character['stats'], character['attack_mods']
                effect = character['weapon_effect']
                self.assertGreaterEqual(stats['health'] / stats['defense'], 0.70)
                self.assertLessEqual(stats['health'] / stats['defense'], 1.40)
                self.assertGreaterEqual(stats['damage'], 0.80)
                self.assertLessEqual(stats['damage'], 1.25)
                self.assertGreaterEqual(mods['reach'] * effect['reach_mult'], 0.85)
                self.assertLessEqual(mods['reach'] * effect['reach_mult'], 1.25)
                self.assertGreaterEqual(mods['startup'] * effect['startup_mult'], 0.78)
                self.assertLessEqual(mods['startup'] * effect['startup_mult'], 1.35)
                # Faster than baseline costs damage, health, or reach; tank
                # durability costs speed or damage. No free stacked bonuses.
                if stats['speed'] > 1.10:
                    self.assertLess(stats['health'], 1.0)
                    self.assertLess(stats['damage'], 1.0)
                if stats['health'] / stats['defense'] > 1.20:
                    self.assertLess(stats['speed'], 1.0)

    def test_multihit_specials_share_one_damage_budget(self):
        for key in ('bramble', 'chib'):
            with self.subTest(fighter=key):
                player = self.player(key)
                hits = player.character['special_behavior'].get('extra_hits', 0) + 1
                full_move_damage = player.attacks['special'].damage * hits
                budget = settings.SPECIAL_DAMAGE * player.character['stats']['damage']
                self.assertLessEqual(full_move_damage, math.ceil(budget))
                self.assertGreater(full_move_damage, budget - hits)

    def test_normal_attacks_do_not_inherit_special_extra_hits(self):
        for key in ('bramble', 'chib'):
            for action in ('light', 'heavy'):
                with self.subTest(fighter=key, action=action):
                    attacker, defender = self.player(key), self.player('golem', x=500)
                    defender.rect.left = attacker.rect.right + 8
                    attacker._start_attack(action)
                    for _ in range(attacker.attacks[action].startup):
                        attacker.update()
                    fx = MagicMock()
                    args = (attacker, defender, fx, [], [], fx, fx, [], fx)
                    with patch.object(fight_scene.sound_fx, 'play'):
                        self.assertTrue(fight_scene._resolve_combat(*args))
                        health_after = defender.health
                        self.assertFalse(fight_scene._resolve_combat(*args))
                    self.assertTrue(attacker.attack_has_connected)
                    self.assertEqual(defender.health, health_after)
                    self.assertEqual(defender.max_health - health_after,
                                     int(attacker.attacks[action].damage * defender.defense))

    def test_projectile_abilities_cannot_add_an_invisible_melee_hit(self):
        for key in ('vex', 'nova', 'jinx', 'minamoto'):
            for action in ('special', 'ultimate'):
                with self.subTest(fighter=key, action=action):
                    attacker, defender = self.player(key), self.player('golem', x=500)
                    defender.rect.left = attacker.rect.right + 8
                    attacker._start_attack(action)
                    for _ in range(attacker.attacks[action].startup):
                        attacker.update()
                    self.assertTrue(attacker.get_hitbox().colliderect(defender.get_hurtbox()))
                    fx = MagicMock()
                    self.assertFalse(fight_scene._resolve_combat(
                        attacker, defender, fx, [], [], fx, fx, [], fx))
                    self.assertEqual(defender.health, defender.max_health)

    def test_fractional_walk_speeds_are_symmetric_and_match_the_stat(self):
        for key in character_data.ROSTER_ORDER:
            distances = []
            for action in ('left', 'right'):
                with self.subTest(fighter=key, direction=action):
                    player = self.player(key, x=500)
                    start = player.rect.x
                    for _ in range(30):
                        player.handle_input(Keys(player, **{action: True}))
                    distances.append(abs(player.rect.x - start))
                    self.assertAlmostEqual(distances[-1], player.move_speed * 30, delta=1)
            self.assertEqual(distances[0], distances[1])

    def test_timeout_uses_health_percentage_instead_of_favoring_larger_health_pools(self):
        tank, sanya = self.player('golem'), self.player('sanya')
        tank.health = tank.max_health * 0.60
        sanya.health = sanya.max_health * 0.90
        self.assertGreater(tank.health, sanya.health)
        manager = RoundManager(1)
        manager.state = ROUND_FIGHTING
        manager.timer_frames = 1
        self.assertEqual(manager.update(tank, sanya), 'round_ended')
        self.assertEqual(manager.winner, 'p2')
        tank.health = tank.max_health / 2
        sanya.health = sanya.max_health / 2
        manager = RoundManager(1)
        manager.state = ROUND_FIGHTING
        manager.timer_frames = 1
        manager.update(tank, sanya)
        self.assertEqual(manager.winner, 'draw')


if __name__ == '__main__':
    unittest.main()

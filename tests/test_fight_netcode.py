"""Exercise the real fight simulation behind the predictive LAN loop."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

from contextlib import ExitStack
import unittest
import time
from unittest.mock import Mock, patch

import pygame
import settings
from characters.player import Player
from effects.projectiles import Projectile
from game import fight_scene
from game.round_manager import RoundManager, ROUND_FIGHTING
from network.rollback import RollbackSession
from network import lan


def active_round(*args, **kwargs):
    manager = RoundManager(*args, **kwargs)
    manager.state = manager._prev_state = ROUND_FIGHTING
    return manager


class NoKeys:
    def __getitem__(self, code):
        return False


class FightNetcodeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen = pygame.display.set_mode((1280, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def create_session(self, *, local_player=1, renders=0, render_dt=1000 / 60,
                       pressed=None, no_remote=False, event_batches=None):
        sessions = []
        peer = Mock()
        submitted = {}
        peer.submit_input.side_effect = lambda frame, values: submitted.update({frame: dict(values)})
        def receive():
            frames = {} if no_remote else {frame: {} for frame in submitted}
            submitted.clear()
            return frames
        peer.receive_inputs.side_effect = receive
        peer.get_stats.return_value = {
            'ping_ms': 5, 'sent_rate': 60, 'received_rate': 60,
            'dropped_packets': None, 'last_received_age': 0,
        }
        clock = Mock()
        clock.tick.return_value = render_dt
        clock.get_fps.return_value = 1000 / render_dt
        def factory(*args, **kwargs):
            session = RollbackSession(*args, **kwargs)
            sessions.append(session)
            return session
        events = (event_batches if event_batches is not None else [[] for _ in range(renders)])
        events = events + [[pygame.event.Event(pygame.QUIT)]]
        with ExitStack() as stack:
            stack.enter_context(patch.object(fight_scene, 'RollbackSession', side_effect=factory))
            stack.enter_context(patch.object(fight_scene, 'RoundManager', side_effect=active_round))
            stack.enter_context(patch.object(fight_scene.vs_screen, 'run_vs_screen', return_value=True))
            stack.enter_context(patch.object(fight_scene.music, 'play'))
            stack.enter_context(patch.object(fight_scene.sound_fx, 'play'))
            stack.enter_context(patch.object(fight_scene.retro, 'present'))
            stack.enter_context(patch.object(fight_scene.stages, 'draw'))
            stack.enter_context(patch('pygame.key.get_pressed', return_value=pressed or NoKeys()))
            stack.enter_context(patch('pygame.event.get', side_effect=events))
            self.assertEqual(fight_scene.run_fight(
                self.screen, clock, network_peer=peer, local_player=local_player,
            ), 'QUIT')
        return sessions[0], peer

    @staticmethod
    def signature(state):
        def player(value):
            attack = value.current_attack
            return (tuple(value.rect), value.health, value.state, value.state_timer,
                    value.vel_y, value.on_ground, value.facing,
                    value.special_cooldown_frames, value.ultimate_meter,
                    value.hit_pause, value._holding_back, value._block_age,
                    None if attack is None else tuple(sorted(attack.__dict__.items())))
        return (player(state['p1']), player(state['p2']),
                dict(state['match'].__dict__), dict(state['round_mgr'].__dict__),
                tuple((p.x, p.y, p.vx, p.vy, p.damage, p.life,
                       1 if p.owner is state['p1'] else 2)
                      for p in state['projectiles']),
                state['ko_slowmo'], state['round_end_registered'])

    def test_local_keypress_moves_before_any_remote_packet(self):
        right = fight_scene.preferences.key_code_from_name(settings.P1_KEYS['right'])
        class Pressed:
            def __getitem__(self, code):
                return code == right
        for local_player in (1, 2):
            with self.subTest(local_player=local_player):
                session, peer = self.create_session(
                    local_player=local_player, renders=1, pressed=Pressed(), no_remote=True,
                )
                state = session.capture()
                local = state[f'p{local_player}']
                self.assertGreater(local.rect.x, 300 if local_player == 1 else 900)
                self.assertEqual(session.confirmed_frame, -1)
                self.assertEqual(session.frame, 1)
                peer.poll_inputs.assert_not_called()

    def test_render_rate_does_not_change_tick_count_or_gameplay(self):
        signatures = []
        frames = []
        for fps in (30, 60, 120):
            session, _ = self.create_session(renders=fps, render_dt=1000 / fps)
            frames.append(session.frame)
            signatures.append(self.signature(session.capture()))
        self.assertEqual(frames, [60, 60, 60])
        self.assertEqual(signatures[0], signatures[1])
        self.assertEqual(signatures[1], signatures[2])

    def test_brief_attack_tap_between_ticks_is_buffered(self):
        light = fight_scene.preferences.key_code_from_name(settings.P1_KEYS['light'])
        session, _ = self.create_session(
            render_dt=1000 / 120, no_remote=True,
            event_batches=[[], [pygame.event.Event(pygame.KEYDOWN, key=light)], []],
        )
        self.assertEqual(session.frame, 2)
        self.assertFalse(session.local_history[0]['light'])
        self.assertTrue(session.local_history[1]['light'])
        self.assertIsNotNone(session.capture()['p1'].current_attack)

    def test_real_combat_converges_after_delayed_reordered_inputs(self):
        first, _ = self.create_session(local_player=1)
        second, _ = self.create_session(local_player=2)
        reference, _ = self.create_session(local_player=1)
        for session in (first, second, reference):
            state = session.capture()
            state['p1'].rect.x = 490
            state['p2'].rect.x = 565
            state['p1'].special_cooldown_frames = 0
            state['p2'].special_cooldown_frames = 0
            session.restore(state)
        inputs1 = [{
            'right': tick < 6, 'light': tick % 45 < 3,
            'heavy': tick % 77 == 24, 'special': tick == 180,
            'jump': tick == 98,
        } for tick in range(360)]
        inputs2 = [{
            'left': tick < 4, 'block': 2 <= tick % 50 <= 10,
            'heavy': tick % 60 == 30, 'light': tick % 59 == 15,
        } for tick in range(360)]
        with patch.object(fight_scene.sound_fx, 'play'):
            for tick in range(360):
                reference.receive_inputs({tick: inputs2[tick]})
                self.assertTrue(reference.advance(inputs1[tick]))
                self.assertTrue(first.advance(inputs1[tick]))
                self.assertTrue(second.advance(inputs2[tick]))
                if tick >= 4 and tick % 2 == 1:
                    a, b = tick - 4, tick - 5
                    first.receive_inputs({a: inputs2[a], b: inputs2[b]})
                    second.receive_inputs({a: inputs1[a], b: inputs1[b]})
            first.receive_inputs({i: values for i, values in enumerate(inputs2) if i >= 350})
            second.receive_inputs({i: values for i, values in enumerate(inputs1) if i >= 350})
        expected = self.signature(reference.capture())
        self.assertEqual(self.signature(first.capture()), expected)
        self.assertEqual(self.signature(second.capture()), expected)
        self.assertEqual(first.confirmed_frame, 359)
        self.assertGreater(first.corrections + second.corrections, 0)
        state = reference.capture()
        self.assertLess(min(state['p1'].health, state['p2'].health), state['p1'].max_health)

    def test_projectile_parry_is_replayed_consistently(self):
        predicted, _ = self.create_session()
        reference, _ = self.create_session()
        for session in (predicted, reference):
            state = session.capture()
            p1, p2 = state['p1'], state['p2']
            p1.rect.x, p2.rect.x = 450, 530
            p2.health = 1
            # An approaching real projectile exercises owner references and
            # reflection when a late block corrects the first predicted tick.
            state['projectiles'].append(Projectile(
                p2.rect.centerx - 20, p2.rect.centery, 7, 1,
                (255, 180, 90), damage=9, owner=p1,
            ))
            session.restore(state)
        actual = [{'block': tick < 3} for tick in range(20)]
        with patch.object(fight_scene.sound_fx, 'play'):
            for tick in range(20):
                reference.receive_inputs({tick: actual[tick]})
                reference.advance({})
                self.assertTrue(predicted.advance({}))
                if tick >= 3:
                    predicted.receive_inputs({tick - 3: actual[tick - 3]})
            predicted.receive_inputs({tick: actual[tick] for tick in range(17, 20)})
        self.assertEqual(self.signature(predicted.capture()), self.signature(reference.capture()))
        self.assertGreater(predicted.corrections, 0)
        state = reference.capture()
        self.assertEqual(state['p2'].health, 1, 'Perfect guard must prevent lethal damage')
        self.assertLess(state['p1'].health, state['p1'].max_health,
                        'The reflected projectile must damage its original owner')

    def test_late_hit_replays_projectile_ko_and_round_winner(self):
        predicted, _ = self.create_session()
        reference, _ = self.create_session()
        for session in (predicted, reference):
            state = session.capture()
            p1, p2 = state['p1'], state['p2']
            p1.rect.x, p2.rect.x = 450, 530
            p2.health = 1
            # The previous actual remote block seeds a wrong held-block
            # prediction. Its release arrives after the first collision.
            session.restore(state)
            session.receive_inputs({0: {'block': True}})
            session.advance({})
            state = session.capture()
            p1, p2 = state['p1'], state['p2']
            state['projectiles'].append(Projectile(
                p2.rect.centerx - 20, p2.rect.centery, 7, 1,
                (255, 180, 90), damage=9, owner=p1,
            ))
            session.restore(state)
        with patch.object(fight_scene.sound_fx, 'play'):
            for tick in range(1, 21):
                reference.receive_inputs({tick: {}})
                reference.advance({})
                self.assertTrue(predicted.advance({}))
                if tick >= 4:
                    predicted.receive_inputs({tick - 3: {}})
            predicted.receive_inputs({tick: {} for tick in range(18, 21)})
        self.assertEqual(self.signature(predicted.capture()), self.signature(reference.capture()))
        state = reference.capture()
        self.assertEqual(state['p2'].health, 0)
        self.assertEqual(state['round_mgr'].winner, 'p1')
        self.assertTrue(state['round_end_registered'])
        self.assertGreater(predicted.corrections, 0)

    def test_remote_visual_interpolation_never_moves_collision_geometry(self):
        fighter = Player(400, settings.GROUND_Y - 150, 'rook', settings.P1_KEYS)
        fighter._start_attack('light')
        before = (fighter.rect.copy(), fighter.get_hurtbox().copy(), list(fighter.weapon_trail))
        fight_scene._draw_fighter_visual(self.screen, fighter, (50.5, 100.25))
        self.assertEqual(fighter.rect, before[0])
        self.assertEqual(fighter.get_hurtbox(), before[1])
        self.assertEqual(fighter.weapon_trail, before[2])

    def test_real_tcp_peers_drive_matching_fight_states(self):
        listener = lan.create_host(port=0)
        self.addCleanup(listener.close)
        guest = lan.connect_to_host('127.0.0.1', listener.getsockname()[1])
        self.addCleanup(guest.close)
        host = lan.accept_if_ready(listener)
        self.addCleanup(host.close)
        first, _ = self.create_session(local_player=1)
        second, _ = self.create_session(local_player=2)
        peers = (host, guest)
        sessions = (first, second)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            for peer, session in zip(peers, sessions):
                session.receive_inputs(peer.receive_inputs())
                if session.frame < 120:
                    values = {'right': session.frame < 45, 'light': session.frame % 20 == 0}
                    peer.submit_input(session.frame, values)
                    session.advance(values)
            if all(session.confirmed_frame == 119 for session in sessions):
                break
            time.sleep(0.001)
        self.assertEqual([session.confirmed_frame for session in sessions], [119, 119])
        self.assertEqual(self.signature(first.capture()), self.signature(second.capture()))


if __name__ == '__main__':
    unittest.main()

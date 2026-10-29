"""Both LAN players act on their own tick without a request/reply handshake."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import unittest
from contextlib import ExitStack
from unittest.mock import Mock, patch
import pygame
import settings
from game import fight_scene
from network.rollback import RollbackSession
import test_fight_netcode as fight_tests


class RealtimeLanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen = pygame.display.set_mode((1280, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.fight = fight_tests.FightNetcodeTests(methodName='runTest')
        self.fight.screen = self.screen

    def local_attack(self, local_player, action):
        key = fight_scene.preferences.key_code_from_name(settings.P1_KEYS[action])
        return self.fight.create_session(
            local_player=local_player, no_remote=True,
            event_batches=[[
                pygame.event.Event(pygame.KEYDOWN, key=key),
                pygame.event.Event(pygame.KEYUP, key=key),
            ]],
        )

    def test_both_players_short_keypresses_start_before_either_remote_reply(self):
        first, first_peer = self.local_attack(1, 'light')
        second, second_peer = self.local_attack(2, 'heavy')
        for session, peer, slot, action in (
                (first, first_peer, 'p1', 'light'),
                (second, second_peer, 'p2', 'heavy')):
            with self.subTest(local_player=slot):
                state = session.capture()
                self.assertEqual(session.frame, 1)
                self.assertEqual(session.confirmed_frame, -1)
                self.assertEqual(state[slot].state, 'ATTACK')
                self.assertEqual(state[slot].current_attack.data.name, action)
                self.assertTrue(peer.submit_input.call_args.args[1][action])
                peer.poll_inputs.assert_not_called()

    def test_simultaneous_attacks_converge_when_actual_inputs_arrive(self):
        first, _ = self.local_attack(1, 'light')
        second, _ = self.local_attack(2, 'heavy')
        reference, _ = self.fight.create_session()
        reference.receive_inputs({0: {'heavy': True}})
        reference.advance({'light': True})
        first.receive_inputs({0: {'heavy': True}})
        second.receive_inputs({0: {'light': True}})
        expected = self.fight.signature(reference.capture())
        self.assertEqual(self.fight.signature(first.capture()), expected)
        self.assertEqual(self.fight.signature(second.capture()), expected)
        self.assertEqual(first.confirmed_frame, 0)
        self.assertEqual(second.confirmed_frame, 0)

    def test_render_only_polls_never_freeze_a_future_tick_input(self):
        session, peer = self.fight.create_session(
            renders=3, render_dt=4, no_remote=True,
        )
        self.assertEqual(session.frame, 1)
        self.assertEqual(peer.submit_input.call_count, 1)
        self.assertEqual(peer.submit_input.call_args.args[0], 0)

    def test_default_view_draws_latest_remote_state_without_added_delay(self):
        with patch.object(fight_scene.RenderInterpolator, 'sample', return_value=(0, 0)) as sample, \
             patch.object(fight_scene, '_draw_fighter_visual', return_value=[]) as draw, \
             patch.object(fight_scene, 'draw_network_debug') as debug:
            session, _ = self.fight.create_session(renders=1, no_remote=True)
        sample.assert_not_called()
        remote_draw = draw.call_args_list[1]
        self.assertIsNone(remote_draw.args[2])
        self.assertEqual(remote_draw.args[1].rect,
                         session.capture()['p2'].rect)
        self.assertFalse(debug.call_args.kwargs['smooth_remote'])

    def test_f4_smoothing_is_optional_and_overlay_tracks_the_selection(self):
        toggle = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F4)
        with patch.object(fight_scene.RenderInterpolator, 'sample', return_value=(100, 200)) as sample, \
             patch.object(fight_scene, '_draw_fighter_visual', return_value=[]) as draw, \
             patch.object(fight_scene, 'draw_network_debug') as debug:
            session, _ = self.fight.create_session(
                no_remote=True, event_batches=[[toggle], [], [toggle]],
            )
        self.assertEqual(sample.call_count, 2)
        self.assertEqual([call.kwargs['smooth_remote'] for call in debug.call_args_list],
                         [True, True, False])
        self.assertEqual(draw.call_args_list[1].args[2], (100, 200))
        self.assertEqual(draw.call_args_list[3].args[2], (100, 200))
        self.assertIsNone(draw.call_args_list[5].args[2])
        self.assertNotEqual(tuple(session.capture()['p2'].rect.topleft), (100, 200))

    def test_packet_arriving_during_background_draw_corrects_same_display_frame(self):
        sessions = []
        peer = Mock()
        available = {}
        peer.receive_inputs.side_effect = lambda: dict(available)
        clock = Mock()
        clock.tick.return_value = 1000 / 60
        clock.get_fps.return_value = 120
        def factory(*args, **kwargs):
            session = RollbackSession(*args, **kwargs)
            sessions.append(session)
            return session
        def draw_background(*args, **kwargs):
            # Model a frame-zero movement arriving after simulation has already
            # predicted that the remote fighter remained idle.
            available[0] = {'left': True}
        with ExitStack() as stack:
            stack.enter_context(patch.object(fight_scene, 'RollbackSession', side_effect=factory))
            stack.enter_context(patch.object(fight_scene, 'RoundManager', side_effect=fight_tests.active_round))
            stack.enter_context(patch.object(fight_scene.vs_screen, 'run_vs_screen', return_value=True))
            stack.enter_context(patch.object(fight_scene.music, 'play'))
            stack.enter_context(patch.object(fight_scene.sound_fx, 'play'))
            stack.enter_context(patch.object(fight_scene.retro, 'present'))
            stack.enter_context(patch.object(fight_scene.stages, 'draw', side_effect=draw_background))
            stack.enter_context(patch.object(fight_scene, 'draw_network_debug'))
            draw = stack.enter_context(patch.object(fight_scene, '_draw_fighter_visual', return_value=[]))
            stack.enter_context(patch('pygame.key.get_pressed', return_value=fight_tests.NoKeys()))
            stack.enter_context(patch('pygame.event.get', side_effect=[[], [pygame.event.Event(pygame.QUIT)]]))
            result = fight_scene.run_fight(self.screen, clock, network_peer=peer)
        self.assertEqual(result, 'QUIT')
        self.assertEqual(sessions[0].corrections, 1)
        self.assertEqual(sessions[0].confirmed_frame, 0)
        self.assertLess(draw.call_args_list[1].args[1].rect.x, 900)
        self.assertIsNone(draw.call_args_list[1].args[2])
        self.assertEqual(peer.receive_inputs.call_count, 2)
        self.assertTrue(all(call.args[0] == settings.LAN_RENDER_FPS
                            for call in clock.tick.call_args_list))


if __name__ == '__main__':
    unittest.main()

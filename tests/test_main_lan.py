"""Exercise the join-to-match flow, including final fighter validation."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import unittest
from unittest.mock import Mock, patch
from contextlib import ExitStack
import main
import pygame
from network import lan


class LanRenderingTests(unittest.TestCase):
    def test_first_frames_waiting_for_peer_render_for_both_players(self):
        pygame.init()
        self.addCleanup(pygame.quit)
        screen = pygame.display.set_mode((1280, 720))
        for local_player in (1, 2):
            with self.subTest(local_player=local_player):
                peer = Mock()
                peer.poll_inputs.return_value = None
                peer.local_inputs = {action: False for action in lan.ACTIONS}
                clock = Mock()
                clock.tick.return_value = 16
                with patch.object(main.fight_scene.vs_screen, 'run_vs_screen', return_value=True), \
                     patch.object(main.fight_scene.music, 'play'), \
                     patch('pygame.display.flip') as flip, \
                     patch('pygame.event.get', side_effect=[
                         [], [], [pygame.event.Event(pygame.QUIT)]]):
                    result = main.fight_scene.run_fight(
                        screen, clock, network_peer=peer, local_player=local_player,
                    )
                self.assertEqual(result, 'QUIT')
                self.assertEqual(peer.poll_inputs.call_count, 2)
                self.assertEqual(flip.call_count, 2)


class JoinSetupTests(unittest.TestCase):
    def run_join(self, final_fighter):
        peer = Mock()
        host_choice = {
            'role': 'host', 'protocol': lan.PROTOCOL_VERSION,
            'p1_character': 'rook', 'stage_key': 'sunset', 'palette_key': 'classic',
        }
        final_setup = {**host_choice, 'p2_character': final_fighter}
        with ExitStack() as stack:
            stack.enter_context(patch.object(main.preferences, 'load'))
            stack.enter_context(patch('audio.sound_fx.init'))
            stack.enter_context(patch.object(main.music, 'play'))
            stack.enter_context(patch.object(main.music, 'stop'))
            stack.enter_context(patch.object(main.intro_video, 'run_title_video', return_value=True))
            stack.enter_context(patch.object(main.menu, 'run_main_menu', side_effect=['LAN_JOIN', 'EXIT']))
            stack.enter_context(patch.object(main.lan_lobby, 'run_join_lobby', return_value=peer))
            stack.enter_context(patch.object(main.character_select, 'run_character_select', return_value='vex'))
            stack.enter_context(patch.object(main.lan_lobby, 'exchange_setup_with_ui', return_value=host_choice))
            stack.enter_context(patch.object(main.lan_lobby, 'receive_setup_with_ui', return_value=final_setup))
            fight = stack.enter_context(patch.object(main.fight_scene, 'run_fight', return_value='MENU'))
            error = stack.enter_context(patch.object(main.lan_lobby, 'show_lan_message'))
            with self.assertRaises(SystemExit):
                main.main()
        peer.close.assert_called_once()
        return fight, error

    def test_guest_starts_with_its_selected_fighter(self):
        fight, error = self.run_join('vex')
        fight.assert_called_once()
        self.assertEqual(fight.call_args.kwargs['p2_character'], 'vex')
        self.assertEqual(fight.call_args.kwargs['local_player'], 2)
        error.assert_not_called()

    def test_host_cannot_replace_the_guests_selected_fighter(self):
        fight, error = self.run_join('golem')
        fight.assert_not_called()
        self.assertIn('does not match your fighter', error.call_args.args[3])


if __name__ == '__main__':
    unittest.main()

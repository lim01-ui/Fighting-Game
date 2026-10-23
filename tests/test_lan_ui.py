"""Verify LAN cancellation remains responsive during connection and gameplay."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import threading
import unittest
from unittest.mock import Mock, patch
import pygame
from game import fight_scene
from network import lan
from ui import lan_lobby


class LanUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen = pygame.display.set_mode((1280, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_cancel_join_closes_a_connection_that_finishes_late(self):
        finish_connection = threading.Event()
        closed = threading.Event()
        peer = Mock(spec=lan.LanPeer)
        peer.close.side_effect = closed.set
        def slow_connect(address):
            finish_connection.wait(2)
            return peer
        events = [
            [pygame.event.Event(pygame.TEXTINPUT, text='127.0.0.1:47611')],
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)],
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)],
        ]
        try:
            with patch.object(lan, 'connect_to_host', side_effect=slow_connect), \
                 patch('pygame.event.get', side_effect=events):
                self.assertIsNone(lan_lobby.run_join_lobby(self.screen, pygame.time.Clock()))
            self.assertFalse(finish_connection.is_set())
        finally:
            finish_connection.set()
        self.assertTrue(closed.wait(2), 'Canceled connection must not leak a socket')

    def test_escape_can_leave_a_stalled_fight(self):
        peer = Mock()
        with patch.object(fight_scene.vs_screen, 'run_vs_screen', return_value=True), \
             patch.object(fight_scene.music, 'play'), \
             patch('pygame.event.get', return_value=[
                 pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]):
            self.assertEqual(fight_scene.run_fight(self.screen, pygame.time.Clock(),
                                                 network_peer=peer), 'MENU')
        peer.poll_inputs.assert_not_called()


if __name__ == '__main__':
    unittest.main()

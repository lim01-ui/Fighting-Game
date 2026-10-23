"""Regression coverage for saved bindings and the mouse-driven options flow."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import pygame
import settings
from audio import preferences
from characters.player import Player
from game import fight_scene
from game.fight_scene import _VirtualKeys
from ui import menu, settings_menu


class ControlsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen = pygame.display.set_mode((1280, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.path_patch = patch.object(preferences, '_config_path', Path(self.directory.name) / 'settings.json')
        self.path_patch.start()
        preferences.reset()
        self.clock = pygame.time.Clock()

    def tearDown(self):
        preferences.reset()
        self.path_patch.stop()
        self.directory.cleanup()

    def test_any_normal_key_including_game_shortcuts(self):
        for key in (pygame.K_p, pygame.K_r, pygame.K_h, pygame.K_t, pygame.K_v,
                    pygame.K_SPACE, pygame.K_RETURN, pygame.K_KP_ENTER,
                    pygame.K_F12, pygame.K_LSHIFT, pygame.K_SEMICOLON):
            preferences.bind_control('light', key)
            self.assertEqual(preferences.key_code_from_name(settings.P1_KEYS['light']), key)

    def test_duplicate_binding_swaps_and_aliases_are_rejected(self):
        preferences.bind_control('light', pygame.K_a)
        self.assertEqual(settings.P1_KEYS['left'], 'j')
        preferences.bind_control('left', pygame.K_ESCAPE)
        preferences.bind_control('left', pygame.K_a)
        self.assertEqual(settings.P1_KEYS['light'], '')
        value = settings.P1_KEYS.copy()
        value['heavy'] = 'A'
        self.assertFalse(preferences.is_valid_control_map(value))

    def test_unbound_survives_save_and_does_not_read_unknown_key(self):
        for action in settings.P1_KEYS:
            preferences.bind_control(action, pygame.K_ESCAPE)
        preferences.save()
        preferences.reset()
        preferences.load()
        self.assertTrue(all(value == '' for value in settings.P1_KEYS.values()))
        player = Player(100, 200, 'rook', settings.P1_KEYS)
        class NoKeyAccess:
            def __getitem__(self, key):
                raise AssertionError('Unbound action must not sample a keyboard key')
        for action in settings.P1_KEYS:
            self.assertFalse(player.action_pressed(NoKeyAccess(), action))
        self.assertEqual(_VirtualKeys(player, {'light': True}).values, {})
        player.handle_input(NoKeyAccess())

    def test_mouse_rebind_escape_unbind_and_back(self):
        batches = [
            [],
            [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(800, 408))],
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F2)],
            [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(800, 408))],
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)],
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)],
        ]
        with patch('pygame.event.get', side_effect=batches):
            self.assertIs(settings_menu.run_controls_menu(self.screen, self.clock), self.screen)
        self.assertEqual(settings.P1_KEYS['light'], '')
        preferences.load()
        self.assertEqual(settings.P1_KEYS['light'], '')

    def test_start_options_and_settings_are_clickable(self):
        with patch('pygame.event.get', side_effect=[[], [pygame.event.Event(
                pygame.MOUSEBUTTONDOWN, button=1, pos=(200, 510))]]):
            self.assertEqual(menu.run_main_menu(self.screen, self.clock), 'SETTINGS')
        with patch.object(settings_menu, 'run_controls_menu', return_value=self.screen) as controls:
            with patch('pygame.event.get', side_effect=[[], [pygame.event.Event(
                    pygame.MOUSEBUTTONDOWN, button=1, pos=(500, 440))],
                    [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]]):
                self.assertIs(settings_menu.run_settings_menu(self.screen, self.clock), self.screen)
            controls.assert_called_once()

    def test_rebound_pause_and_reset_keys_attack_in_training(self):
        for key in (pygame.K_p, pygame.K_r):
            preferences.bind_control('light', key)
            players = []
            def create_player(*args, **kwargs):
                player = Player(*args, **kwargs)
                players.append(player)
                return player
            class PressedKey:
                def __getitem__(self, code):
                    return code == key
            with patch.object(fight_scene, 'Player', side_effect=create_player), \
                 patch.object(fight_scene.vs_screen, 'run_vs_screen', return_value=True), \
                 patch.object(fight_scene.music, 'play'), \
                 patch('pygame.key.get_pressed', return_value=PressedKey()), \
                 patch('pygame.event.get', side_effect=[
                     [pygame.event.Event(pygame.KEYDOWN, key=key)],
                     [pygame.event.Event(pygame.QUIT)]]):
                self.assertEqual(fight_scene.run_fight(self.screen, self.clock,
                                                     training_mode=True), 'QUIT')
            self.assertEqual(len(players), 2, 'Rebound R must not reset the round')
            self.assertIsNotNone(players[0].current_attack, 'Rebound P must not pause')


if __name__ == '__main__':
    unittest.main()

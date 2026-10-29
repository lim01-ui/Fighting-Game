"""Exercise the actual fight-scene snapshot callbacks across combat abilities."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import unittest
from unittest.mock import Mock, patch

import pygame
import settings
from characters import character_data
from characters.player import Player
from combat.attack import AttackData
from game import fight_scene
from game.round_manager import ROUND_FIGHTING
from ui.retro import PixelFont


def normalized(value, seen=None):
    """Compare full mutable state without object addresses or pixel resources."""
    if seen is None:
        seen = {}
    if isinstance(value, (str, int, float, bool, bytes, type(None))):
        return value
    if isinstance(value, pygame.Rect):
        return ('Rect', tuple(value))
    if isinstance(value, pygame.Surface):
        return ('Surface', value.get_size())
    if isinstance(value, (pygame.font.Font, PixelFont)):
        return ('Font', value.get_height())
    if isinstance(value, AttackData):
        return ('AttackData', tuple(vars(value).items()))
    if id(value) in seen:
        return ('reference', seen[id(value)])
    seen[id(value)] = len(seen)
    if isinstance(value, dict):
        return tuple((key, normalized(child, seen)) for key, child in value.items())
    if isinstance(value, (tuple, list)):
        return tuple(normalized(child, seen) for child in value)
    if hasattr(value, '__dict__'):
        ignored = {'character', 'keymap', 'attacks'} if isinstance(value, Player) else set()
        return (type(value).__name__, tuple((key, normalized(child, seen))
                for key, child in vars(value).items() if key not in ignored))
    raise TypeError(type(value).__name__)


class FightSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen = pygame.display.set_mode((1280, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def callbacks(self, character='rook'):
        captured = []
        clock = Mock()
        clock.tick.return_value = 16
        def create_session(step, capture, restore, **kwargs):
            captured.extend((step, capture, restore))
            return Mock()
        with patch.object(fight_scene, 'RollbackSession', side_effect=create_session), \
             patch.object(fight_scene.vs_screen, 'run_vs_screen', return_value=True), \
             patch.object(fight_scene.music, 'play'), \
             patch('pygame.event.get', return_value=[pygame.event.Event(pygame.QUIT)]):
            self.assertEqual(fight_scene.run_fight(self.screen, clock,
                p1_character=character, p2_character='golem', network_peer=Mock()), 'QUIT')
        return captured

    def prepare(self, capture, restore):
        start = capture()
        start['round_mgr'].state = ROUND_FIGHTING
        start['round_mgr']._prev_state = ROUND_FIGHTING
        for index, key in enumerate(('p1', 'p2')):
            start[key].rect.x = 450 + index * 200
            start[key].rect.bottom = settings.GROUND_Y
            start[key].ultimate_meter = 100
            start[key].special_cooldown_frames = 0
        restore(start)
        return capture()

    def test_every_ultimate_replays_full_captured_state_identically(self):
        for character in character_data.ROSTER_ORDER:
            with self.subTest(character=character):
                step, capture, restore = self.callbacks(character)
                start = self.prepare(capture, restore)
                for frame in range(65):
                    step(frame, {'special': frame == 0}, {}, False)
                expected = normalized(capture())
                restore(start)
                for frame in range(65):
                    step(frame, {'special': frame == 0}, {}, True)
                self.assertEqual(normalized(capture()), expected)

    def test_snapshot_with_live_projectiles_restores_owner_and_replays_collision(self):
        step, capture, restore = self.callbacks('vex')
        self.prepare(capture, restore)
        for frame in range(40):
            step(frame, {'special': frame == 0}, {}, False)
            snapshot = capture()
            if snapshot['projectiles']:
                break
        else:
            self.fail('Vex ultimate must produce live projectiles')
        self.assertTrue(all(pr.owner is snapshot['p1'] for pr in snapshot['projectiles']))
        for frame2 in range(frame + 1, frame + 30):
            step(frame2, {}, {}, False)
        expected = normalized(capture())
        restore(snapshot)
        restored = capture()
        self.assertTrue(all(pr.owner is restored['p1'] for pr in restored['projectiles']))
        for frame2 in range(frame + 1, frame + 30):
            step(frame2, {}, {}, True)
        self.assertEqual(normalized(capture()), expected)

    def test_interpolated_render_leaves_captured_combat_state_unchanged(self):
        step, capture, restore = self.callbacks('rook')
        self.prepare(capture, restore)
        step(0, {'light': True}, {}, False)
        snapshot = capture()
        before = normalized(snapshot)
        for _ in range(4):
            fight_scene._draw_fighter_visual(self.screen, snapshot['p1'], (100, 200))
        self.assertEqual(normalized(snapshot), before)


if __name__ == '__main__':
    unittest.main()

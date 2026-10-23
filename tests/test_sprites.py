"""Render the complete roster and validate generated pose sheets."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import unittest
from unittest.mock import patch
import pygame
import settings
from characters import character_data, sprite_fighter, pixel_fighter
from characters.player import Player, S_IDLE, S_WALK, S_GUARD, S_HITSTUN, S_BLOCKSTUN, S_KNOCKDOWN


class SpriteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1280, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_generated_poses_are_nonempty_and_flip_correctly(self):
        for asset in sprite_fighter.GENERATED_ASSETS:
            manifest = sprite_fighter._manifest(asset)
            self.assertGreater(manifest['body_height'], 0)
            for pose in ('idle', 'walk', 'block', 'jump', 'light', 'heavy', 'special', 'hit'):
                with self.subTest(asset=asset, pose=pose):
                    right = sprite_fighter._load_frame(asset, pose, 0, 1)
                    left = sprite_fighter._load_frame(asset, pose, 0, -1)
                    self.assertGreater(pygame.mask.from_surface(right).count(), 100)
                    self.assertLess(right.get_height(), manifest['body_height'] * 1.8,
                                    'Pose may include pixels from a neighboring atlas row')
                    self.assertTrue(right.get_flags() & pygame.SRCALPHA)
                    self.assertEqual(pygame.image.tostring(left, 'RGBA'),
                                     pygame.image.tostring(pygame.transform.flip(right, True, False), 'RGBA'))

    def test_every_fighter_renders_in_both_directions_and_combat_states(self):
        surface = pygame.Surface((1280, 720), pygame.SRCALPHA)
        for key in character_data.ROSTER_ORDER:
            for facing in (-1, 1):
                player = Player(500, 350, key, settings.P1_KEYS, facing=facing)
                for state in (S_IDLE, S_WALK, S_GUARD, S_HITSTUN, S_BLOCKSTUN, S_KNOCKDOWN):
                    with self.subTest(fighter=key, facing=facing, state=state):
                        surface.fill((0, 0, 0, 0))
                        player.state = state
                        player.draw(surface)
                        self.assertGreater(surface.get_bounding_rect().height, 0)
                for attack in player.attacks:
                    with self.subTest(fighter=key, facing=facing, attack=attack):
                        player._start_attack(attack)
                        surface.fill((0, 0, 0, 0))
                        player.draw(surface)
                        self.assertGreater(surface.get_bounding_rect().height, 0)

    def test_guard_uses_the_block_pose_and_saikyo_ultimate_uses_special(self):
        for asset in sprite_fighter.GENERATED_ASSETS + ('renegade', 'soldier'):
            player = Player(100, 200, asset, settings.P1_KEYS)
            player.state = S_GUARD
            with patch('pygame.time.get_ticks', return_value=0):
                image = sprite_fighter.frame_for_player(asset, player)
                block = sprite_fighter._load_frame(asset, 'block', 0, 1)
            self.assertEqual(pygame.image.tostring(image, 'RGBA'), pygame.image.tostring(block, 'RGBA'))
        player = Player(100, 200, 'saikyo', settings.P1_KEYS)
        player._start_attack('ultimate')
        with patch.object(pixel_fighter, 'get_frame', wraps=pixel_fighter.get_frame) as frame:
            pixel_fighter.frame_for_player(player)
        frame.assert_called_once_with(2, 2)


if __name__ == '__main__':
    unittest.main()

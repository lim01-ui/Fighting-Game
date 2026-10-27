"""Render the complete roster and validate generated pose sheets."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import unittest
import hashlib
import json
from unittest.mock import patch
import pygame
import settings
from characters import character_data, sprite_fighter
from ui import character_select
from characters.player import Player, S_IDLE, S_WALK, S_CROUCH, S_GUARD, S_HITSTUN, S_BLOCKSTUN, S_KNOCKDOWN


class SpriteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1280, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_reference_fighters_keep_their_original_sprite_packs(self):
        expected = {'iron': 'knight', 'sable': 'swordsman', 'nova': 'wizard',
                    'jinx': 'musketeer', 'kestrel': 'archer',
                    'bramble': 'enchantress'}
        for fighter, asset in expected.items():
            self.assertEqual(character_data.get(fighter)['sprite_asset'], asset)
            self.assertFalse(sprite_fighter.is_generated_asset(asset))
        self.assertEqual(set(character_data.ROSTER_ORDER) - set(expected),
                         set(sprite_fighter.GENERATED_ASSETS))

    def test_original_sprite_backups_match_the_recorded_hashes(self):
        fighters = set()
        for directory in ('pre-style-rework', 'pre-raguel-rework'):
            backup = sprite_fighter.ASSET_ROOT / 'backups' / directory
            manifest = json.loads((backup / 'manifest.json').read_text(encoding='utf-8'))
            fighters.update(manifest['fighters'])
            for relative, digest in manifest['sha256'].items():
                if relative.lower().endswith(('.png', '.gif')):
                    with self.subTest(file=relative):
                        self.assertEqual(hashlib.sha256((backup / relative).read_bytes()).hexdigest(),
                                         digest)
        self.assertEqual(fighters, set(sprite_fighter.GENERATED_ASSETS))

    def test_reworked_atlas_cells_are_in_bounds_and_do_not_overlap(self):
        for asset in sprite_fighter.GENERATED_ASSETS:
            manifest = sprite_fighter._manifest(asset)
            image = pygame.image.load(str(sprite_fighter.ASSET_ROOT / 'style-v2' / manifest['image']))
            cells = [pygame.Rect(rect) for pose, rect in manifest['poses'].items()
                     if pose != 'knockdown']
            self.assertEqual(len(cells), 12)
            for index, rect in enumerate(cells):
                with self.subTest(fighter=asset, cell=index):
                    self.assertTrue(image.get_rect().contains(rect))
                    self.assertFalse(any(rect.colliderect(other) for other in cells[index + 1:]))
            idle = sprite_fighter._load_frame(asset, 'idle', 0, 1)
            self.assertAlmostEqual(idle.get_bounding_rect(min_alpha=16).height,
                                   manifest['pixel_height'], delta=1)

    def test_idle_loops_have_distinct_frames_and_stable_canvas_and_feet(self):
        for asset in sprite_fighter.GENERATED_ASSETS:
            spec = sprite_fighter._manifest(asset)['idle_animation']
            sheet = pygame.image.load(str(sprite_fighter.ASSET_ROOT / 'style-v2' / spec['image']))
            self.assertEqual(len(spec['frames']), 4)
            for rect in spec['frames']:
                self.assertTrue(sheet.get_rect().contains(pygame.Rect(rect)))
            for facing in (-1, 1):
                with self.subTest(fighter=asset, facing=facing):
                    frames = []
                    for tick in (0, 180, 360, 540, 720):
                        with patch('pygame.time.get_ticks', return_value=tick):
                            frames.append(sprite_fighter.preview_frame(asset, facing))
                    self.assertEqual(len({frame.get_size() for frame in frames}), 1)
                    self.assertEqual(len({pygame.image.tobytes(frame, 'RGBA')
                                          for frame in frames[:4]}), 4)
                    self.assertIs(frames[0], frames[4])
                    bottoms = [frame.get_bounding_rect(min_alpha=16).bottom for frame in frames]
                    self.assertLessEqual(max(bottoms) - min(bottoms), 1)
                    for i, frame in enumerate(frames[:4]):
                        opposite = sprite_fighter._load_frame(asset, 'idle', i, -facing)
                        self.assertEqual(pygame.image.tobytes(frame, 'RGBA'),
                                         pygame.image.tobytes(pygame.transform.flip(opposite, True, False), 'RGBA'))

    def test_character_select_animates_reworked_cards_and_large_preview(self):
        screen = pygame.display.get_surface()
        clock = type('Clock', (), {'tick': lambda self, fps: 16})()
        screenshots = []
        for tick in (0, 360):
            with patch('pygame.time.get_ticks', return_value=tick), \
                 patch('pygame.event.get', side_effect=[[], [pygame.event.Event(pygame.QUIT)]]), \
                 patch('pygame.display.flip', side_effect=lambda: screenshots.append(screen.copy())):
                character_select.run_character_select(screen, clock)
        for asset in sprite_fighter.GENERATED_ASSETS:
            with self.subTest(fighter=asset):
                rect = character_select._cell_rect(character_data.ROSTER_ORDER.index(asset))
                self.assertNotEqual(pygame.image.tobytes(screenshots[0].subsurface(rect), 'RGB'),
                                    pygame.image.tobytes(screenshots[1].subsurface(rect), 'RGB'))
        preview = pygame.Rect(character_select.PANEL_LEFT + 20,
                              character_select.PANEL_TOP + 20,
                              character_select.PANEL_W - 40, 200)
        self.assertNotEqual(pygame.image.tobytes(screenshots[0].subsurface(preview), 'RGB'),
                            pygame.image.tobytes(screenshots[1].subsurface(preview), 'RGB'))

    def test_generated_poses_are_nonempty_and_flip_correctly(self):
        for asset in sprite_fighter.GENERATED_ASSETS:
            manifest = sprite_fighter._manifest(asset)
            self.assertGreater(manifest['body_height'], 0)
            for pose in manifest['poses']:
                with self.subTest(asset=asset, pose=pose):
                    right = sprite_fighter._load_frame(asset, pose, 0, 1)
                    left = sprite_fighter._load_frame(asset, pose, 0, -1)
                    self.assertGreater(pygame.mask.from_surface(right).count(), 100)
                    self.assertLess(right.get_height(), sprite_fighter.body_height(asset) * 1.8,
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

    def test_crouching_shortens_sprites_without_widening_them(self):
        surface = pygame.Surface((1280, 720), pygame.SRCALPHA)
        for key in character_data.ROSTER_ORDER:
            if not character_data.get(key).get('sprite_asset'):
                continue
            for facing in (-1, 1):
                with self.subTest(fighter=key, facing=facing), \
                     patch('pygame.time.get_ticks', return_value=0):
                    player = Player(500, 350, key, settings.P1_KEYS, facing=facing)
                    player.rect.bottom = settings.GROUND_Y
                    surface.fill((0, 0, 0, 0))
                    player._draw_sprite_asset(surface)
                    standing = surface.get_bounding_rect(min_alpha=16)
                    player.state = S_CROUCH
                    player.is_crouching = True
                    surface.fill((0, 0, 0, 0))
                    player._draw_sprite_asset(surface)
                    crouching = surface.get_bounding_rect(min_alpha=16)
                    # Allow a few pixels of nearest-neighbor raster rounding.
                    if sprite_fighter.is_generated_asset(player.character['sprite_asset']):
                        # Dedicated crouch poses may spread arms/knees, but must
                        # not be stretched to nearly twice the standing width.
                        self.assertLessEqual(crouching.width, standing.width * 1.5)
                        self.assertGreaterEqual(crouching.width, standing.width * 0.65)
                    else:
                        self.assertAlmostEqual(crouching.width, standing.width, delta=4)
                    self.assertAlmostEqual(crouching.height,
                                           standing.height * player.crouch_ratio, delta=4)
                    self.assertAlmostEqual(
                        settings.GROUND_Y - crouching.bottom,
                        (settings.GROUND_Y - standing.bottom) * player.crouch_ratio,
                        delta=4)

    def test_guard_and_ultimate_use_matching_poses(self):
        for asset in sprite_fighter.GENERATED_ASSETS:
            player = Player(100, 200, asset, settings.P1_KEYS)
            player.state = S_GUARD
            with patch('pygame.time.get_ticks', return_value=0):
                image = sprite_fighter.frame_for_player(asset, player)
                block = sprite_fighter._load_frame(asset, 'block', 0, 1)
            self.assertEqual(pygame.image.tostring(image, 'RGBA'), pygame.image.tostring(block, 'RGBA'))
        player = Player(100, 200, 'saikyo', settings.P1_KEYS)
        player._start_attack('ultimate')
        with patch.object(sprite_fighter, '_load_frame', wraps=sprite_fighter._load_frame) as frame:
            sprite_fighter.frame_for_player('saikyo', player)
        frame.assert_called_once_with('saikyo', 'special', 0, 1)

    def test_reworked_fighters_use_walk_cycles_and_attack_phase_poses(self):
        for asset in sprite_fighter.GENERATED_ASSETS:
            with self.subTest(fighter=asset):
                player = Player(100, 200, asset, settings.P1_KEYS)
                self.assertEqual(player.character['sprite_asset'], asset)
                self.assertFalse(player.character.get('sprite_sheet'))
                walk = [sprite_fighter._load_frame(asset, 'walk', i, 1) for i in range(3)]
                self.assertIs(walk[0], walk[2])
                self.assertNotEqual(pygame.image.tobytes(walk[0], 'RGBA'),
                                    pygame.image.tobytes(walk[1], 'RGBA'))
                for attack in ('light', 'heavy'):
                    player._start_attack(attack)
                    windup = sprite_fighter.frame_for_player(asset, player)
                    player.current_attack.frame = player.current_attack.data.startup
                    active = sprite_fighter.frame_for_player(asset, player)
                    self.assertIs(active, sprite_fighter._load_frame(asset, attack, 1, 1))
                    self.assertIsNot(windup, active)


if __name__ == '__main__':
    unittest.main()

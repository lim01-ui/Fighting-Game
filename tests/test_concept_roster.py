"""Behavioral checks for the eight concept-art replacements."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import hashlib
import json
import math
import unittest
from unittest.mock import patch
import pygame
import settings
from characters import character_data, sprite_fighter
from characters.player import Player, S_KNOCKDOWN


class ConceptRosterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1280, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_requested_names_art_and_equipment_are_active(self):
        expected = {
            'rook': ('ONI', 'oni-chibi.png', 'daggers'),
            'vex': ('ANGELIX', 'angelix-chibi.png', 'staff'),
            'sable': ('PHOENIX', 'phoenix-chibi.png', 'sword'),
            'chib': ('PO', 'po-chibi.png', 'katana'),
            'golem': ('GOLEM', 'golem-moss-chibi.png', 'hammer'),
            'sanya': ('SANYA', 'sanya-mecha-chibi.png', 'sword'),
            'soldier': ('NULL', 'null-chibi.png', 'axe'),
            'choom': ('GLACIER', 'glacier-chibi.png', 'fists'),
        }
        for key, (name, image, weapon) in expected.items():
            with self.subTest(fighter=key):
                character = character_data.get(key)
                manifest = sprite_fighter._manifest(key)
                self.assertEqual((character['name'], manifest['image'], character['weapon']),
                                 (name, image, weapon))
                self.assertEqual(len(manifest['poses']), 24)
                self.assertEqual(len(manifest['animations']['walk']), 4)
                for action in ('light', 'heavy', 'special'):
                    self.assertEqual(len(manifest['animations'][action]), 4)
                self.assertTrue(manifest['dedicated_knockdown'])
        for key in ('choom', 'soldier'):
            self.assertIsNone(character_data.get(key)['weapon_effect']['projectile'])
            self.assertIsNone(character_data.ultimate_for(key).get('projectile'))
        self.assertEqual(character_data.get('vex')['weapon_effect']['projectile'], 'orb')

    def test_flying_fighters_bob_without_changing_physics_and_land_when_down(self):
        surface = pygame.Surface((1280, 720), pygame.SRCALPHA)
        for key in ('vex', 'sable'):
            for facing in (-1, 1):
                with self.subTest(fighter=key, facing=facing), patch('pygame.time.get_ticks', return_value=0):
                    player = Player(500, 350, key, settings.P1_KEYS, facing)
                    player.rect.bottom = settings.GROUND_Y
                    rect = player.rect.copy()
                    bottoms = []
                    for time in (math.pi / .15, math.pi * 3 / .15):
                        player._animation_time = time
                        surface.fill((0, 0, 0, 0))
                        player._draw_sprite_asset(surface)
                        bottoms.append(surface.get_bounding_rect(min_alpha=80).bottom)
                    self.assertAlmostEqual(bottoms[1] - bottoms[0], 12, delta=1)
                    self.assertLess(max(bottoms), settings.GROUND_Y - 12)
                    self.assertEqual(player.rect, rect)
                    self.assertTrue(player.on_ground)
                    player.state = S_KNOCKDOWN
                    surface.fill((0, 0, 0, 0))
                    player._draw_sprite_asset(surface)
                    self.assertAlmostEqual(surface.get_bounding_rect(min_alpha=80).bottom,
                                           settings.GROUND_Y, delta=3)

    def test_oni_head_flame_changes_through_the_idle_loop(self):
        frames = [sprite_fighter._load_frame('rook', 'idle', i, 1) for i in range(4)]
        flame_area = pygame.Rect(0, 0, frames[0].get_width(), frames[0].get_height() // 4)
        self.assertEqual(len({pygame.image.tobytes(frame.subsurface(flame_area), 'RGBA')
                              for frame in frames}), 4)

    def test_new_specials_play_follow_through_and_recover(self):
        for key in ('rook', 'vex', 'sable', 'chib', 'golem', 'sanya', 'soldier', 'choom'):
            for name in ('special', 'ultimate'):
                with self.subTest(fighter=key, attack=name):
                    player = Player(400, 350, key, settings.P1_KEYS)
                    player._start_attack(name)
                    attack = player.current_attack
                    phases = (0, attack.data.startup,
                              attack.data.startup + attack.data.active - 1,
                              attack.data.startup + attack.data.active)
                    for expected, frame in enumerate(phases):
                        attack.frame = frame
                        self.assertIs(sprite_fighter.frame_for_player(key, player),
                                      sprite_fighter._load_frame(key, 'special', expected, 1))

    def test_previous_designs_and_stats_are_archived(self):
        directory = sprite_fighter.ASSET_ROOT / 'backups/pre-concept-integration'
        archive = json.loads((directory / 'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(set(archive['fighters']),
                         {'rook', 'vex', 'sable', 'chib', 'golem', 'sanya', 'soldier', 'choom'})
        for key, original in archive['fighters'].items():
            # Preserve the old balance records while allowing live rebalancing.
            self.assertEqual(set(original['stats']),
                             {'speed', 'jump', 'health', 'damage', 'defense'})
        for filename, digest in archive['sha256'].items():
            with self.subTest(file=filename):
                self.assertEqual(hashlib.sha256((directory / filename).read_bytes()).hexdigest(), digest)

    def test_preview_body_scale_is_independent_of_weapon_width(self):
        surface = pygame.Surface((140, 100), pygame.SRCALPHA)
        box = pygame.Rect(20, 12, 92, 62)
        body_bounds = []
        for width in (80, 270):
            frame = pygame.Surface((width, 72), pygame.SRCALPHA)
            pygame.draw.line(frame, (255, 0, 0), (0, 45), (width - 1, 45), 3)
            pygame.draw.rect(frame, (0, 255, 0), (width // 2 - 15, 0, 30, 72))
            surface.fill((0, 0, 0, 0))
            original_clip = surface.get_clip()
            with patch.object(sprite_fighter, 'preview_frame', return_value=frame):
                sprite_fighter.blit_preview(surface, 'raguel', box)
            self.assertEqual(surface.get_clip(), original_clip)
            green = pygame.mask.from_threshold(surface, (0, 255, 0, 255), (1, 1, 1, 1))
            body_bounds.append(green.get_bounding_rects()[0])
            self.assertTrue(box.contains(surface.get_bounding_rect()))
        self.assertEqual((body_bounds[0].top, body_bounds[0].bottom),
                         (body_bounds[1].top, body_bounds[1].bottom))
        self.assertAlmostEqual(body_bounds[0].width, body_bounds[1].width, delta=1)
        self.assertAlmostEqual(body_bounds[0].centerx, body_bounds[1].centerx, delta=1)
        self.assertAlmostEqual(body_bounds[0].height, box.height * .92, delta=1)

    def test_new_proportions_share_reference_scale_and_facing(self):
        for key in ('rook', 'vex', 'sable', 'chib', 'golem', 'sanya', 'soldier', 'choom'):
            with self.subTest(fighter=key):
                manifest = sprite_fighter._manifest(key)
                expected = 'renegade' if key in ('golem', 'choom') else 'raguel'
                self.assertEqual(manifest['proportion_reference'], expected)
                self.assertEqual(manifest['source_facing'], 1)
                self.assertEqual(manifest['pixel_height'], sprite_fighter.body_height(expected))

    def test_grounded_idle_boots_stay_near_the_player_in_both_directions(self):
        surface = pygame.Surface((1280, 720), pygame.SRCALPHA)
        for key in ('rook', 'soldier', 'sanya'):
            for facing in (-1, 1):
                with self.subTest(fighter=key, facing=facing):
                    player = Player(500, 350, key, settings.P1_KEYS, facing)
                    player.rect.bottom = settings.GROUND_Y
                    footprints, bottoms, frames = [], [], []
                    duration = sprite_fighter._manifest(key)['idle_animation']['frame_ms']
                    for tick in (0, duration, duration * 2, duration * 3, duration * 4):
                        player._animation_time = tick * .06
                        surface.fill((0, 0, 0, 0))
                        with patch('pygame.time.get_ticks', return_value=tick):
                            player._draw_sprite_asset(surface)
                        band = pygame.Rect(player.rect.centerx - 150, settings.GROUND_Y - 9, 300, 14)
                        boots = pygame.mask.from_surface(surface.subsurface(band), 200)
                        self.assertGreater(boots.count(), 100)
                        center = boots.centroid()[0] + band.x
                        footprints.append(boots)
                        bottoms.append(surface.get_bounding_rect(min_alpha=80).bottom)
                        self.assertLessEqual(abs(center - player.rect.centerx), 16)
                        frames.append(pygame.image.tobytes(surface, 'RGBA'))
                    # A planted stance keeps its footprint even while the boots
                    # flex and small chain effects alter their pixel mass.
                    # The old column origins moved the boots roughly 80-100px.
                    for boots in footprints[1:]:
                        overlap = footprints[0].overlap_area(boots, (0, 0))
                        self.assertGreaterEqual(overlap / min(footprints[0].count(), boots.count()), .7)
                    self.assertLessEqual(max(bottoms) - min(bottoms), 1)
                    self.assertAlmostEqual(bottoms[0], settings.GROUND_Y, delta=1)
                    self.assertEqual(frames[0], frames[4])
                    self.assertEqual(len(set(frames[:4])), 4)


if __name__ == '__main__':
    unittest.main()

"""Rollback copies preserve combat ownership and isolate mutable state."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import random
import unittest
from unittest.mock import Mock, patch

import pygame
import settings
from audio import sound_fx
from characters.player import Player
from effects.footwork import Footwork
from effects.hit_spark import HitSpark
from effects.projectiles import Projectile
from effects.special_moves import UltimatePresentation
from game.simulation_state import clone_state, simulation_tick


class SimulationStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1280, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def make_bundle(self):
        p1 = Player(300, 300, 'rook', settings.P1_KEYS)
        p2 = Player(700, 300, 'vex', settings.P2_KEYS, facing=-1)
        p1._opponent_ref = p2
        p2._opponent_ref = p1
        p1._start_attack('light')
        projectile = Projectile(400, 400, 10, 1, (100, 200, 255), owner=p1)
        return {
            'p1': p1, 'p2': p2, 'projectiles': [projectile],
            'spark': HitSpark(400, 400, (100, 200, 255)),
            'footwork': Footwork(),
            'ultimate': UltimatePresentation(400, 400, (100, 200, 255), 'ROOK', 'BURST'),
        }

    def test_restored_owner_and_opponent_references_remain_in_graph(self):
        bundle = self.make_bundle()
        snapshot = clone_state(bundle)
        restored = clone_state(snapshot)
        self.assertIsNot(restored['p1'], bundle['p1'])
        self.assertIs(restored['p1']._opponent_ref, restored['p2'])
        self.assertIs(restored['p2']._opponent_ref, restored['p1'])
        self.assertIs(restored['projectiles'][0].owner, restored['p1'])
        self.assertIs(restored['p1'].current_attack.data, restored['p1'].attacks['light'])

    def test_mutation_and_repeated_restores_do_not_change_saved_combat_state(self):
        snapshot = clone_state(self.make_bundle())
        for _ in range(3):
            restored = clone_state(snapshot)
            restored['p1'].health -= 50
            restored['p1'].rect.x += 100
            restored['p1'].current_attack.update(restored['p1'].rect)
            restored['projectiles'][0].update()
            restored['spark'].update()
            self.assertEqual(snapshot['p1'].health, snapshot['p1'].max_health)
            self.assertEqual(snapshot['p1'].rect.x, 300)
            self.assertEqual(snapshot['p1'].current_attack.frame, 0)
            self.assertEqual(snapshot['projectiles'][0].life, 90)
            self.assertEqual(snapshot['spark'].life, snapshot['spark'].max_life)

    def test_large_visual_assets_and_static_blueprints_are_shared(self):
        bundle = self.make_bundle()
        restored = clone_state(bundle)
        self.assertIs(restored['footwork'].layer, bundle['footwork'].layer)
        self.assertIs(restored['ultimate'].title_font, bundle['ultimate'].title_font)
        self.assertIs(restored['p1'].character, bundle['p1'].character)
        self.assertIs(restored['p1'].attacks, bundle['p1'].attacks)

    def test_tick_randomness_replays_and_external_random_state_is_restored(self):
        before = random.getstate()
        with simulation_tick(87):
            values = [random.random() for _ in range(5)]
        self.assertEqual(random.getstate(), before)
        with simulation_tick(87, replaying=True):
            self.assertEqual([random.random() for _ in range(5)], values)
        self.assertEqual(random.getstate(), before)
        with self.assertRaises(RuntimeError):
            with simulation_tick(87):
                random.random()
                raise RuntimeError('cancel tick')
        self.assertEqual(random.getstate(), before)

    def test_replay_suppresses_audio_without_disabling_future_sounds(self):
        sound = Mock()
        with patch.dict(sound_fx._sounds, {'hit_light': sound}), \
             patch.object(sound_fx, '_enabled', True):
            with simulation_tick(10, replaying=True):
                sound_fx.play('hit_light')
                with sound_fx.suppress(False):
                    sound_fx.play('hit_light')
            sound.play.assert_not_called()
            with simulation_tick(11):
                sound_fx.play('hit_light')
            sound.play.assert_called_once()


if __name__ == '__main__':
    unittest.main()

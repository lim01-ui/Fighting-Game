"""Validate imported effect strips and their combat lifecycle."""

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import unittest
import pygame

from effects import sprite_effect
from effects.hit_spark import HitSpark, BlockSpark
from effects.special_moves import SpecialEffect, UltimatePresentation
from effects.projectiles import Projectile


class EffectAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((1280, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_all_strips_have_visible_aligned_frames_and_flip_correctly(self):
        for effect in range(1, 5):
            for gameboy in (False, True):
                with self.subTest(effect=effect, gameboy=gameboy):
                    frames = sprite_effect.frames(effect, gameboy)
                    self.assertEqual(len(frames), 4)
                    self.assertEqual(len({frame.get_size() for frame in frames}), 1)
                    for frame in frames:
                        self.assertGreater(pygame.mask.from_surface(frame).count(), 0)
                    right = sprite_effect.scaled_frames(effect, 96, 1, gameboy)
                    left = sprite_effect.scaled_frames(effect, 96, -1, gameboy)
                    for a, b in zip(right, left):
                        self.assertEqual(pygame.image.tobytes(a, "RGBA"), pygame.image.tobytes(
                            pygame.transform.flip(b, True, False), "RGBA"))

    def test_impacts_and_specials_render_and_expire_at_their_existing_lifetime(self):
        effects = [HitSpark(640, 400, (255, 200, 100)), BlockSpark(640, 400)]
        effects += [SpecialEffect(kind, 640, 400, facing, (100, 200, 255))
                    for kind in ("slash", "double_slash", "shockwave", "aura", "spark", "leafburst")
                    for facing in (-1, 1)]
        surface = pygame.Surface((1280, 720), pygame.SRCALPHA)
        for effect in effects:
            for tick in range(effect.max_life):
                surface.fill((0, 0, 0, 0))
                effect.draw(surface)
                self.assertGreater(surface.get_bounding_rect().width, 0)
                self.assertEqual(effect.update(), tick == effect.max_life - 1)

    def test_ultimate_and_projectile_animations_render_without_changing_damage(self):
        surface = pygame.Surface((1280, 720), pygame.SRCALPHA)
        ultimate = UltimatePresentation(640, 400, (100, 200, 255), "ROOK", "BREAKER")
        for _ in range(ultimate.max_life):
            ultimate.draw(surface)
            ultimate.update()
        for kind in ("orb", "spark"):
            projectile = Projectile(400, 400, 3, 1, (100, 200, 255), kind=kind, damage=17)
            for _ in range(32):
                surface.fill((0, 0, 0, 0))
                projectile.draw(surface)
                self.assertGreater(surface.get_bounding_rect().width, 0)
                projectile.update()
            self.assertEqual(projectile.damage, 17)
            self.assertEqual(projectile.x, 496)


if __name__ == "__main__":
    unittest.main()

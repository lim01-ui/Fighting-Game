"""Check City/Ocean stages, selection, archived ambient effects and results."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import unittest
from unittest.mock import patch
import pygame
from stages import stages, ambient, scenic_preview
from ui import stage_select, retro, transitions


class StageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen = pygame.display.set_mode((1280, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_all_eight_cities_and_eight_oceans_are_selectable(self):
        combos = stages.all_stage_combos()
        self.assertEqual(len(combos), 16)
        expected = {('City', f'city {i}') for i in range(1, 9)}
        expected.update(('Ocean', f'Ocean_{i}') for i in range(1, 9))
        actual = {stages.background_info(*combo)[:2] for combo in combos}
        self.assertEqual(actual, expected)
        self.assertEqual(stages.STAGE_KEYS, ['sunset', 'dojo', 'neon'])
        for index, combo in enumerate(combos):
            group, folder, _ = stages.background_info(*combo)
            self.assertTrue(any((stages.ASSET_ROOT / group / folder).glob('*.png')))
            self.assertTrue(pygame.Rect(0, 0, 1280, 660).contains(
                stage_select._tile_rect(index)))

    def test_each_background_renders_with_parallax_without_mutating_source(self):
        surface = pygame.Surface((640, 360))
        for key, palette in stages.all_stage_combos():
            with self.subTest(scene=stages.display_name(key, palette)):
                group, folder, _ = stages.background_info(key, palette)
                image = stages._background(group, folder, 640, 360)
                source = pygame.image.tobytes(image, 'RGB')
                stages.draw(surface, key, 1.0, palette_key=palette)
                first = pygame.image.tobytes(surface, 'RGB')
                floor = surface.get_at((320, 340))
                stages.draw(surface, key, 3.75, scroll=.8, palette_key=palette)
                self.assertNotEqual(first, pygame.image.tobytes(surface, 'RGB'))
                self.assertEqual(floor, surface.get_at((320, 340)))
                stages.draw(surface, key, 1.0, palette_key=palette)
                self.assertEqual(first, pygame.image.tobytes(surface, 'RGB'))
                self.assertEqual(source, pygame.image.tobytes(image, 'RGB'))

    def test_water_foliage_sky_lanterns_and_particles_animate_independently(self):
        cases = (
            ('moonlit_shrine', lambda s, b, k, p, t: ambient._water(s, b, p['water'], t)),
            ('angkor_sanctuary', lambda s, b, k, p, t: ambient._sway(s, b, k, p['foliage'], t)),
            ('aurora_lake', ambient._sky),
            ('moonlit_shrine', lambda s, b, k, p, t: ambient._lights(s, {**p, 'fireflies': 0}, t)),
            ('sakura_relic', lambda s, b, k, p, t: ambient._leaves_and_grass(s, p, t)),
        )
        for key, effect in cases:
            with self.subTest(scene=key, effect=effect):
                base = scenic_preview._background(key)
                first, second = base.copy(), base.copy()
                effect(first, base, key, scenic_preview.definition(key), .3)
                effect(second, base, key, scenic_preview.definition(key), 2.3)
                self.assertNotEqual(pygame.image.tobytes(first, 'RGB'), pygame.image.tobytes(second, 'RGB'))

    def test_stage_selector_confirms_city_and_last_ocean_with_keyboard_and_mouse(self):
        clock = type('Clock', (), {'tick': lambda self, fps: 16})()
        with patch('pygame.event.get', side_effect=[[], [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)]]):
            self.assertEqual(stage_select.run_stage_select(self.screen, clock), stages.all_stage_combos()[0])
        last = len(stages.all_stage_combos()) - 1
        target = stage_select._tile_rect(last).center
        with patch('pygame.event.get', side_effect=[[], [
            pygame.event.Event(pygame.MOUSEMOTION, pos=target),
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(1000, 360)),
        ]]):
            self.assertEqual(stage_select.run_stage_select(self.screen, clock), stages.all_stage_combos()[last])

    def test_ko_victory_defeat_and_draw_render_from_first_to_last_frame(self):
        fonts = {name: retro.font(size=size) for name, size in
                 (('small', 20), ('mid', 30), ('big', 44), ('huge', 96))}
        for progress in (0, .01, .12, .4, 1):
            for winner, reason in (('p1', 'ko'), ('p2', 'time'), ('draw', 'time')):
                self.screen.fill((30, 50, 80))
                transitions.draw_round_over(self.screen, winner, reason, progress, fonts, winner_name='ONI')
            for header in ('YOU WIN THE MATCH', 'YOU LOSE THE MATCH', 'BOT WINS THE MATCH'):
                transitions.draw_match_over(self.screen, header, 'ROUNDS: 2 - 0', progress, fonts)
        # Celebration continues after the entrance animation finishes.
        frames = []
        for tick in (1000, 1800):
            self.screen.fill((30, 50, 80))
            with patch('pygame.time.get_ticks', return_value=tick):
                transitions.draw_match_over(self.screen, 'ONI WINS THE MATCH', 'ROUNDS: 2 - 0', 1, fonts)
            frames.append(pygame.image.tobytes(self.screen, 'RGB'))
        self.assertNotEqual(*frames)


if __name__ == '__main__':
    unittest.main()

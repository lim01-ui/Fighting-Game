"""Smoke checks for the animated intro and shared night-city menu theme."""

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import unittest
from unittest.mock import patch

import pygame

from ui import intro_video, theme


class ThemeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.screen = pygame.display.set_mode((1280, 720))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_city_scene_animates_and_is_repeatable_at_the_same_time(self):
        theme.background(self.screen, elapsed=1)
        first = pygame.image.tobytes(self.screen, "RGB")
        theme.background(self.screen, elapsed=1)
        self.assertEqual(first, pygame.image.tobytes(self.screen, "RGB"))
        theme.background(self.screen, elapsed=4)
        self.assertNotEqual(first, pygame.image.tobytes(self.screen, "RGB"))

    def test_intro_can_start_or_close_and_renders_before_input(self):
        clock = pygame.time.Clock()
        for event, expected in ((pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN), True),
                                (pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(640, 400)), True),
                                (pygame.event.Event(pygame.QUIT), False)):
            with self.subTest(event=event.type), patch("pygame.event.get", side_effect=[[], [event]]):
                self.assertEqual(intro_video.run_title_video(self.screen, clock), expected)

    def test_logo_and_shared_chrome_render_at_multiple_resolutions(self):
        for size in ((1280, 720), (960, 540)):
            surface = pygame.Surface(size)
            theme.background(surface, elapsed=2)
            theme.logo(surface, elapsed=2)
            theme.panel(surface, pygame.Rect(30, 240, 300, 150), selected=True)
            theme.footer(surface, "ENTER: SELECT")
            self.assertEqual(surface.get_size(), size)


if __name__ == "__main__":
    unittest.main()

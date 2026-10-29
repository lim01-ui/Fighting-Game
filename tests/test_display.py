"""Native SDL scaling, minimum sizing, pointer mapping and fullscreen settings."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')

import ctypes
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import warnings
from unittest.mock import patch

import pygame
from pygame._sdl2.video import Renderer

import settings
from audio import preferences
from ui import display, settings_menu


ROOT = Path(__file__).resolve().parent.parent
BASE_SIZE = (1280, 720)


class DisplayTests(unittest.TestCase):
    def setUp(self):
        self.warning_context = warnings.catch_warnings()
        self.warning_context.__enter__()
        warnings.filterwarnings('ignore', message='no fast renderer available')
        warnings.filterwarnings('ignore', message='Please use Window.get_surface')
        self.environment = patch.dict(os.environ)
        self.environment.start()
        pygame.init()

    def tearDown(self):
        pygame.quit()
        self.environment.stop()
        self.warning_context.__exit__(None, None, None)

    def test_native_resizes_keep_logical_canvas_and_letterbox_without_stretching(self):
        screen = display.create_window()
        window = pygame.Window.from_display_module()
        renderer = Renderer.from_window(window)
        for size in (BASE_SIZE, (1600, 900), (1920, 1080),
                     (1920, 1200), (3440, 1440), (3840, 2160)):
            with self.subTest(physical_size=size):
                window.size = size
                pygame.event.pump()
                self.assertEqual(pygame.display.get_window_size(), size)
                self.assertEqual(screen.get_size(), BASE_SIZE)
                self.assertEqual(renderer.logical_size, BASE_SIZE)
                scale = min(size[0] / BASE_SIZE[0], size[1] / BASE_SIZE[1])
                self.assertAlmostEqual(renderer.scale[0], scale, places=5)
                self.assertAlmostEqual(renderer.scale[1], scale, places=5)
                viewport = renderer.get_viewport()
                self.assertEqual(viewport.size, BASE_SIZE)
                self.assertAlmostEqual(viewport.x * scale,
                                       (size[0] - BASE_SIZE[0] * scale) / 2, delta=1)
                self.assertAlmostEqual(viewport.y * scale,
                                       (size[1] - BASE_SIZE[1] * scale) / 2, delta=1)

    def test_native_window_rejects_dimensions_below_1280_by_720(self):
        screen = display.create_window()
        window = pygame.Window.from_display_module()
        self.assertEqual(window.minimum_size, BASE_SIZE)
        for requested in ((800, 600), (1700, 500), (1000, 1000)):
            with self.subTest(requested=requested):
                window.size = requested
                pygame.event.pump()
                width, height = pygame.display.get_window_size()
                self.assertGreaterEqual(width, BASE_SIZE[0])
                self.assertGreaterEqual(height, BASE_SIZE[1])
                self.assertEqual(screen.get_size(), BASE_SIZE)

    def test_fullscreen_uses_desktop_and_roundtrip_restores_minimum_resizable_window(self):
        # Isolate the SDL renderer lifecycle so a driver failure cannot take
        # down the entire regression suite, and bound it in case it hangs.
        script = '''
import json
import pygame
from ui import display
pygame.init()
desktop = pygame.display.get_desktop_sizes()[0]
screen = display.create_window()
screen = display.set_fullscreen(screen, True)
fullscreen = (pygame.display.is_fullscreen(), screen.get_size(), pygame.display.get_window_size())
screen = display.set_fullscreen(screen, False)
window = pygame.Window.from_display_module()
result = {'desktop': desktop, 'fullscreen': fullscreen,
          'windowed': [pygame.display.is_fullscreen(), screen.get_size(), window.minimum_size, window.resizable]}
print(json.dumps(result))
pygame.quit()
'''
        completed = subprocess.run([sys.executable, '-B', '-c', script], cwd=ROOT,
                                   env=os.environ.copy(), capture_output=True,
                                   text=True, timeout=12)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = json.loads(completed.stdout.strip().splitlines()[-1])
        self.assertEqual(result['fullscreen'], [True, list(BASE_SIZE), result['desktop']])
        self.assertEqual(result['windowed'], [False, list(BASE_SIZE), list(BASE_SIZE), True])

    def test_fullscreen_helper_leaves_an_already_matching_mode_alone(self):
        screen = pygame.Surface(BASE_SIZE)
        with patch.object(pygame.display, 'is_fullscreen', return_value=True), \
                patch.object(pygame.display, 'toggle_fullscreen') as toggle, \
                patch.object(display, 'create_window') as create:
            self.assertIs(display.set_fullscreen(screen, True), screen)
        toggle.assert_not_called()
        create.assert_not_called()

    def test_fullscreen_helper_reuses_the_display_after_successful_toggle(self):
        original, toggled = pygame.Surface(BASE_SIZE), pygame.Surface(BASE_SIZE)
        with patch.object(pygame.display, 'is_fullscreen', side_effect=[False, True]), \
                patch.object(pygame.display, 'toggle_fullscreen') as toggle, \
                patch.object(pygame.display, 'get_surface', return_value=toggled), \
                patch.object(display, 'create_window') as create:
            self.assertIs(display.set_fullscreen(original, True), toggled)
        toggle.assert_called_once()
        create.assert_not_called()

    def test_unsupported_toggle_restarts_display_before_rebuilding_renderer(self):
        original, rebuilt = pygame.Surface(BASE_SIZE), pygame.Surface(BASE_SIZE)
        with patch.object(pygame.display, 'is_fullscreen', return_value=False), \
                patch.object(pygame.display, 'toggle_fullscreen', side_effect=pygame.error('unsupported')), \
                patch.object(pygame.display, 'quit') as stop, \
                patch.object(pygame.display, 'init') as start, \
                patch.object(display, 'create_window', return_value=rebuilt) as create:
            self.assertIs(display.set_fullscreen(original, True), rebuilt)
        stop.assert_called_once()
        start.assert_called_once()
        create.assert_called_once_with(True)

    def test_settings_fullscreen_toggle_is_saved_for_the_next_launch(self):
        screen = display.create_window()
        clock = type('Clock', (), {'tick': lambda self, fps: 16})()
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(preferences, '_config_path', Path(directory) / 'settings.json'):
            preferences.reset()
            try:
                batches = [[pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(800, 380))],
                           [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]]
                with patch('pygame.event.get', side_effect=batches), \
                        patch.object(display, 'set_fullscreen', return_value=screen) as toggle, \
                        patch.object(settings_menu.sound_fx, 'play'), \
                        patch.object(settings_menu.retro, 'present'):
                    self.assertIs(settings_menu.run_settings_menu(screen, clock), screen)
                toggle.assert_called_once_with(screen, True)
                self.assertTrue(preferences.get('fullscreen'))
                preferences.reset()
                self.assertFalse(preferences.get('fullscreen'))
                preferences.load()
                self.assertTrue(preferences.get('fullscreen'))
            finally:
                preferences.reset()

    @unittest.skipUnless(sys.platform == 'win32', 'SDL DLL pointer-event probe is Windows-specific')
    def test_native_mouse_clicks_remain_aligned_with_controls_after_scaling(self):
        dll = Path(pygame.__file__).parent / 'SDL2.dll'
        if not dll.exists():
            self.skipTest('Installed pygame does not expose its SDL2 DLL')
        sdl = ctypes.CDLL(str(dll))
        sdl.SDL_GetWindowFromID.argtypes = [ctypes.c_uint32]
        sdl.SDL_GetWindowFromID.restype = ctypes.c_void_p
        sdl.SDL_WarpMouseInWindow.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]
        sdl.SDL_PushEvent.argtypes = [ctypes.c_void_p]
        sdl.SDL_PushEvent.restype = ctypes.c_int

        class Button(ctypes.Structure):
            _fields_ = [('type', ctypes.c_uint32), ('timestamp', ctypes.c_uint32),
                        ('windowID', ctypes.c_uint32), ('which', ctypes.c_uint32),
                        ('button', ctypes.c_uint8), ('state', ctypes.c_uint8),
                        ('clicks', ctypes.c_uint8), ('padding1', ctypes.c_uint8),
                        ('x', ctypes.c_int), ('y', ctypes.c_int)]

        class Event(ctypes.Union):
            _fields_ = [('button', Button), ('padding', ctypes.c_uint8 * 56)]

        screen = display.create_window()
        window = pygame.Window.from_display_module()
        native_window = sdl.SDL_GetWindowFromID(window.id)
        light_binding_box = pygame.Rect(740, 390, 260, 38)
        logical_target = (800, 408)
        click = None
        for size in ((1600, 900), (1920, 1200), (3440, 1440)):
            with self.subTest(physical_size=size):
                window.size = size
                pygame.event.pump()
                scale = min(size[0] / 1280, size[1] / 720)
                physical = (round((size[0] - 1280 * scale) / 2 + logical_target[0] * scale),
                            round((size[1] - 720 * scale) / 2 + logical_target[1] * scale))
                pygame.event.clear()
                sdl.SDL_WarpMouseInWindow(native_window, *physical)
                native_event = Event()
                native_event.button = Button(0x401, 0, window.id, 0, 1, 1, 1, 0, *physical)
                self.assertEqual(sdl.SDL_PushEvent(ctypes.byref(native_event)), 1)
                pygame.event.pump()
                clicks = [event for event in pygame.event.get() if event.type == pygame.MOUSEBUTTONDOWN]
                self.assertEqual(len(clicks), 1)
                click = clicks[0]
                self.assertTrue(light_binding_box.collidepoint(click.pos))
                self.assertAlmostEqual(click.pos[0], logical_target[0], delta=1)
                self.assertAlmostEqual(click.pos[1], logical_target[1], delta=1)

        # Feed the SDL-converted click through the real controls menu: it must
        # select Light Attack, bind F2 and save it, even after an ultrawide resize.
        clock = type('Clock', (), {'tick': lambda self, fps: 16})()
        with tempfile.TemporaryDirectory() as directory, \
                patch.object(preferences, '_config_path', Path(directory) / 'settings.json'):
            preferences.reset()
            try:
                with patch('pygame.event.get', side_effect=[
                        [click], [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F2)],
                        [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]]), \
                        patch.object(settings_menu.sound_fx, 'play'), \
                        patch.object(settings_menu.retro, 'present'):
                    self.assertIs(settings_menu.run_controls_menu(screen, clock), screen)
                self.assertEqual(preferences.key_code_from_name(settings.P1_KEYS['light']), pygame.K_F2)
            finally:
                preferences.reset()


if __name__ == '__main__':
    unittest.main()

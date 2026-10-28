"""Verify held-special timing through real matches and capture the updated HUD."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
from collections import defaultdict
from pathlib import Path
import sys
from unittest.mock import patch
import pygame

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import settings
from characters.player import Player
from game import fight_scene
from ui import character_select


def main():
    pygame.init()
    screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
    destination = ROOT / 'design/balance/2026-10-28'
    destination.mkdir(parents=True, exist_ok=True)
    clock = type('Clock', (), {'tick': lambda self, fps: 16})()
    original_start = Player._start_attack
    for left, right in (('golem', 'sanya'), ('choom', 'renegade')):
        frame = [0]
        accepted = []

        def events():
            frame[0] += 1
            return [pygame.event.Event(pygame.QUIT)] if frame[0] > 630 else []

        def keys():
            # Hold through the initial lockout and a second full recharge.
            pressed = defaultdict(bool)
            pressed[pygame.K_l] = frame[0] != 300
            return pressed

        def start(player, kind):
            result = original_start(player, kind)
            if result and kind in ('special', 'ultimate'):
                accepted.append((player.character['key'], frame[0]))
            return result

        def present(*args):
            if frame[0] in (80, 300):
                state = 'cooldown' if frame[0] == 80 else 'ready'
                pygame.image.save(screen, str(destination / f'{left}-{right}-{state}.png'))

        with patch.object(fight_scene.vs_screen, 'run_vs_screen', return_value=True), \
                patch.object(fight_scene.music, 'play'), \
                patch.object(fight_scene.sound_fx, 'play'), \
                patch('pygame.event.get', side_effect=events), \
                patch('pygame.key.get_pressed', side_effect=keys), \
                patch.object(Player, '_start_attack', start), \
                patch.object(fight_scene.retro, 'present', side_effect=present):
            result = fight_scene.run_fight(screen, clock, training_mode=True,
                                           p1_character=left, p2_character=right)
        assert result == 'QUIT', result
        assert accepted == [(left, 301), (left, 601)], accepted
        print(f'{left} / {right}: 630 real match frames, accepted specials at 301 and 601')

    with patch('pygame.event.get', side_effect=[
            [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d),
             pygame.event.Event(pygame.KEYDOWN, key=pygame.K_d)],
            [pygame.event.Event(pygame.QUIT)]]), \
            patch.object(character_select.retro, 'present', side_effect=lambda *args:
                         pygame.image.save(screen, str(destination / 'selection-golem.png'))):
        character_select.run_character_select(screen, clock)
    pygame.quit()


if __name__ == '__main__':
    main()

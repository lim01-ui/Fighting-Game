"""Exercise four real training matches headlessly, saving in-game captures."""
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
from game import fight_scene
from characters.player import Player
import settings


def main():
    pygame.init()
    screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
    destination = ROOT / 'design/character-concepts/2026-10-27'
    pairs = (('rook', 'vex'), ('sable', 'chib'), ('golem', 'sanya'), ('soldier', 'choom'))
    original_update = Player.update
    for left, right in pairs:
        frame = [0]

        def events():
            frame[0] += 1
            return [pygame.event.Event(pygame.QUIT)] if frame[0] > 145 else []

        def update(player, *args, **kwargs):
            if frame[0] == 1:
                player.rect.centerx = 485 if player.facing == 1 else 815
            for tick, action in ((35, 'light'), (60, 'heavy'), (95, 'special'), (125, 'ultimate')):
                if frame[0] == tick:
                    player._start_attack(action)
            return original_update(player, *args, **kwargs)

        def present():
            if frame[0] in (25, 106):
                label = 'idle' if frame[0] == 25 else 'combat'
                pygame.image.save(screen, str(destination / f'match-{left}-{right}-{label}.png'))

        clock = type('Clock', (), {'tick': lambda self, fps: 16})()
        with patch.object(fight_scene.vs_screen, 'run_vs_screen', return_value=True), \
                patch('pygame.event.get', side_effect=events), \
                patch('pygame.key.get_pressed', return_value=defaultdict(bool)), \
                patch.object(Player, 'update', update), \
                patch.object(fight_scene.retro, 'present', side_effect=lambda *args: present()):
            result = fight_scene.run_fight(screen, clock, training_mode=True,
                                           p1_character=left, p2_character=right,
                                           stage_key='sunset', palette_key='classic')
            assert result == 'QUIT', result
        print(left, right, '145 frames, light/heavy/special/ultimate: OK')
    pygame.quit()


if __name__ == '__main__':
    main()

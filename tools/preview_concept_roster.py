"""Render an in-engine overview and animated combat preview of the new roster."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
from pathlib import Path
import sys
from unittest.mock import patch
import pygame

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import settings
from characters.player import Player, S_WALK
from characters import sprite_fighter

KEYS = ('rook', 'vex', 'sable', 'chib', 'golem', 'sanya', 'soldier', 'choom')


def render(tick=0, action=None, phase=0, keys=KEYS):
    screen = pygame.Surface((1600, ((len(keys) + 3) // 4) * 380))
    screen.fill((17, 25, 43))
    font = pygame.font.Font(None, 27)
    with patch('pygame.time.get_ticks', return_value=tick):
        for index, key in enumerate(keys):
            x, y = (index % 4) * 400, (index // 4) * 380
            pygame.draw.rect(screen, (55, 80, 109), (x + 3, y + 3, 394, 374), 2)
            ground = y + 330
            pygame.draw.line(screen, (100, 155, 185), (x + 5, ground), (x + 395, ground))
            player = Player(x + 150, y + 100, key, settings.P1_KEYS)
            player.rect.centerx, player.rect.bottom = x + 200, ground
            player._animation_time = tick / (1000 / 60)
            if action == 'walk':
                player.state = S_WALK
            elif action:
                player._start_attack(action)
                attack = player.current_attack
                attack.frame = (0 if phase == 0 else attack.data.startup if phase == 1
                                else attack.data.startup + max(1, attack.data.active - 1)
                                if phase == 2 else attack.data.startup + attack.data.active)
            player._draw_sprite_asset(screen)
            label = font.render(player.character['name'] + (' / ' + action.upper() if action else ''), False, (240, 213, 123))
            screen.blit(label, label.get_rect(center=(x + 200, y + 353)))
    return screen


def main():
    from PIL import Image
    pygame.init()
    pygame.display.set_mode((1, 1))
    destination = ROOT / 'design/character-concepts/2026-10-27'
    pygame.image.save(render(), str(destination / 'integrated-roster-preview.png'))
    pygame.image.save(render(keys=('raguel', 'nova', 'renegade') + KEYS),
                      str(destination / 'chibi-reference-comparison.png'))
    # Capture the actual selection screen, including the unchanged reference
    # fighters, so proportions can be compared in their real menu cards.
    from ui import character_select
    menu_screen = pygame.display.set_mode((1280, 720))
    clock = type('Clock', (), {'tick': lambda self, fps: 16})()
    with patch('pygame.time.get_ticks', return_value=0), \
            patch('pygame.event.get', side_effect=[[], [pygame.event.Event(pygame.QUIT)]]), \
            patch.object(character_select.retro, 'present', side_effect=lambda *args: pygame.image.save(
                menu_screen, str(destination / 'chibi-selection-preview.png'))):
        character_select.run_character_select(menu_screen, clock)
    frames = []
    for action in (None, 'walk', 'light', 'heavy', 'special'):
        for phase in range(4):
            screen = render(phase * 180, action, phase)
            screen = pygame.transform.scale(screen, (1200, 570))
            frames.append(Image.frombytes('RGB', screen.get_size(), pygame.image.tobytes(screen, 'RGB')))
    frames[0].save(destination / 'integrated-roster-animation.gif', save_all=True,
                   append_images=frames[1:], duration=180, loop=0, disposal=2)
    pygame.quit()


if __name__ == '__main__':
    main()

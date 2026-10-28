"""Capture the three grounded idle loops at their real in-game scale."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import argparse
from pathlib import Path
import sys
from unittest.mock import patch
import pygame
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import settings
from characters.player import Player
from ui import retro


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--label', choices=('before', 'after'), default='after')
    label = parser.parse_args().label
    pygame.init()
    pygame.display.set_mode((1, 1))
    surface = pygame.Surface((960, 340))
    players = [Player(0, 0, key, settings.P1_KEYS) for key in ('rook', 'soldier', 'sanya')]
    frames = []
    for index in range(32):
        tick = index * 60
        surface.fill((17, 25, 43))
        with patch('pygame.time.get_ticks', return_value=tick):
            for column, player in enumerate(players):
                player.rect.centerx, player.rect.bottom = column * 320 + 160, 285
                player._animation_time = tick * 60 / 1000
                pygame.draw.line(surface, (83, 113, 138), (column * 320 + 8, 285), (column * 320 + 312, 285))
                pygame.draw.line(surface, (47, 64, 88), (column * 320 + 160, 55), (column * 320 + 160, 293))
                player._draw_sprite_asset(surface)
                text = retro.font(size=18).render(player.character['name'] + ' / ' + label.upper(), False, (255, 220, 138))
                surface.blit(text, text.get_rect(center=(column * 320 + 160, 317)))
        frames.append(Image.frombytes('RGB', surface.get_size(), pygame.image.tobytes(surface, 'RGB')))
    destination = ROOT / 'design/diagnostics/idle-stability'
    destination.mkdir(parents=True, exist_ok=True)
    frames[0].save(destination / f'idle-{label}.gif', save_all=True, append_images=frames[1:], duration=60, loop=0, disposal=2)
    pygame.quit()
    print(f'Saved idle-{label}.gif')


if __name__ == '__main__':
    main()

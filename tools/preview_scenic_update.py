"""Capture the six animated arenas, bold menus and arcade result animations."""
import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
from pathlib import Path
import sys
from unittest.mock import patch
import pygame
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import settings
from stages import scenic_preview as stages
from characters.player import Player, S_KNOCKDOWN
from ui import retro, intro_video, transitions, stage_select
from ui.lobby_view import LobbyView

DESTINATION = ROOT / 'design/stage-concepts/2026-10-27'


def gallery(t):
    image = pygame.Surface((1152, 488))
    image.fill((11, 24, 39))
    for index, key in enumerate(stages.STAGE_KEYS):
        x, y = (index % 3) * 384, (index // 3) * 244
        frame = pygame.Surface((384, 216))
        stages.draw(frame, key, t)
        image.blit(frame, (x, y))
        text = retro.font(size=18).render(stages.display_name(key), False, (255, 224, 155))
        image.blit(text, text.get_rect(center=(x + 192, y + 230)))
    return image


def save_gif(frames, filename, duration):
    images = [Image.frombytes('RGB', frame.get_size(), pygame.image.tobytes(frame, 'RGB')) for frame in frames]
    images[0].save(DESTINATION / filename, save_all=True, append_images=images[1:],
                   duration=duration, loop=0, disposal=2)


def match_background(screen, t):
    stages.draw(screen, 'moonlit_shrine', t)
    for key, x, facing in (('rook', 350, 1), ('choom', 830, -1)):
        player = Player(x, 300, key, settings.P1_KEYS, facing)
        player.rect.bottom = settings.GROUND_Y
        if key == 'choom':
            player.state = S_KNOCKDOWN
        player.draw(screen)


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    DESTINATION.mkdir(parents=True, exist_ok=True)
    pygame.image.save(gallery(2), str(DESTINATION / 'six-arenas.png'))
    save_gif([gallery(index / 8) for index in range(24)], 'living-arenas.gif', 125)
    intro_video.draw_title(screen, 2)
    pygame.image.save(screen, str(DESTINATION / 'startup-title.png'))
    LobbyView().draw(screen, 0, 2, .016)
    pygame.image.save(screen, str(DESTINATION / 'startup-menu.png'))
    clock = type('Clock', (), {'tick': lambda self, fps: 16})()
    with patch('pygame.event.get', side_effect=[[], [pygame.event.Event(pygame.QUIT)]]), \
            patch.object(stage_select.retro, 'present', side_effect=lambda *args:
                         pygame.image.save(screen, str(DESTINATION / 'stage-selection.png'))):
        stage_select.run_stage_select(screen, clock)
    fonts = {name: retro.font(size=size) for name, size in
             (('small', 20), ('mid', 30), ('big', 44), ('huge', 96))}
    for kind in ('ko', 'victory'):
        frames = []
        for index in range(26):
            t = index / 12
            with patch('pygame.time.get_ticks', return_value=round(t * 1000)):
                match_background(screen, t)
                progress = min(1, index / 18)
                if kind == 'ko':
                    transitions.draw_round_over(screen, 'p1', 'ko', progress, fonts, winner_name='ONI')
                else:
                    transitions.draw_match_over(screen, 'ONI WINS THE MATCH', 'ROUNDS: 2 - 0', progress, fonts)
                if index == 18:
                    pygame.image.save(screen, str(DESTINATION / f'{kind}-preview.png'))
                frames.append(pygame.transform.scale(screen, (768, 432)))
        save_gif(frames, f'{kind}-animation.gif', 83)
    pygame.quit()
    print('Saved arena gallery, animations, menus and KO/victory previews.')


if __name__ == '__main__':
    main()

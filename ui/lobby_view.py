"""Presentation for the main arcade lobby."""
import math
import pygame
import settings
from characters.player import Player
from stages import stages
from ui.text_layout import draw_text_fit


MODES = (
    ("SOLO ARCADE", "Take on the CPU", "Choose your fighter and difficulty.", "Win the set. Make every hit count.", "OFFLINE / VS CPU"),
    ("TRAINING ROOM", "Build your next combo", "Practice timing, parries and ultimate moves.", "Track your damage with no pressure.", "OFFLINE / PRACTICE"),
    ("HOST LAN MATCH", "Your arena. Your rules.", "Create a match on your local network.", "Choose the stage and invite a friend.", "LOCAL NETWORK / HOST"),
    ("JOIN LAN MATCH", "Challenge a friend", "Connect using your host's IP address.", "Both players must be on the same network.", "LOCAL NETWORK / JOIN"),
    ("HOW TO PLAY", "Learn the essentials", "Movement, attacks, defense and combos.", "Get ready for your first fight.", "FIGHTER FIELD GUIDE"),
    ("OPTIONS", "Make it yours", "Adjust audio, display and key bindings.", "Set up your controls before the fight.", "GAME SETTINGS"),
    ("EXIT GAME", "Until the next round", "Close Python Fighters.", "Your saved settings will be kept.", "LEAVE THE ARENA"),
)


class LobbyView:
    def __init__(self):
        self.fonts = {
            'title': pygame.font.SysFont('Arial', 60, bold=True),
            'heading': pygame.font.SysFont('Arial', 32, bold=True),
            'item': pygame.font.SysFont('Arial', 24, bold=True),
            'body': pygame.font.SysFont('Arial', 19),
            'small': pygame.font.SysFont('Arial', 15, bold=True),
        }
        # One set of rectangles drives drawing and mouse hit testing.
        self.rows = [pygame.Rect(87, 245 + i * 49, 506, 42) for i in range(len(MODES))]
        self.background = pygame.Surface((1280, 720))
        for y in range(720):
            fraction = y / 720
            pygame.draw.line(self.background, (8 + int(8 * fraction), 12 + int(5 * fraction), 24 + int(12 * fraction)), (0, y), (1280, y))
        for x in range(-720, 1400, 100):
            pygame.draw.line(self.background, (21, 29, 45), (x, 720), (x + 720, 0))
        self.arena = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        stages.draw(self.arena, 'sunset', 0, palette_key='classic')
        self.world = self.arena.copy()
        self.preview = pygame.Surface((520, 218))
        self.fighters = (
            Player(390, settings.GROUND_Y - 150, 'rook', settings.P1_KEYS, facing=1),
            Player(800, settings.GROUND_Y - 150, 'vex', settings.P2_KEYS, facing=-1),
        )
        self.animation_accumulator = 0.0
        self.highlight_y = float(self.rows[0].y)

    def text(self, surface, font, text, color, rect, align='left'):
        draw_text_fit(surface, self.fonts[font], text, color, pygame.Rect(rect), align=align)

    def draw(self, screen, selected, elapsed, dt):
        cyan, white, muted = (85, 215, 250), (238, 242, 251), (147, 162, 188)
        accent = (255, 185, 99) if selected == 6 else cyan
        screen.blit(self.background, (0, 0))
        pygame.draw.rect(screen, accent, (70, 47, 5, 82), border_radius=2)
        self.text(screen, 'small', 'THE ARENA IS YOURS', accent, (94, 31, 600, 24))
        self.text(screen, 'title', 'PYTHON FIGHTERS', white, (90, 55, 780, 72))
        self.text(screen, 'body', 'Pick your mode. Find your rhythm. Own the fight.', muted, (96, 131, 760, 28))
        pygame.draw.circle(screen, cyan, (1090, 77), 4 + int(math.sin(elapsed * 2) > 0))
        self.text(screen, 'small', 'ARCADE LOBBY', muted, (1105, 65, 140, 26))
        pygame.draw.line(screen, (45, 57, 79), (70, 178), (1210, 178))

        pygame.draw.rect(screen, (14, 21, 36), (70, 190, 540, 438), border_radius=16)
        self.text(screen, 'small', 'SELECT GAME MODE', muted, (99, 207, 350, 24))
        self.text(screen, 'small', f'{selected + 1:02} / 07', accent, (510, 207, 70, 24), 'right')
        self.highlight_y += (self.rows[selected].y - self.highlight_y) * min(1.0, dt * 18)
        trail = pygame.Rect(87, round(self.highlight_y), 506, 42)
        pygame.draw.rect(screen, (23, 43, 62), trail, border_radius=8)
        for index, row in enumerate(self.rows):
            active = index == selected
            if active:
                pygame.draw.rect(screen, (30, 61, 80), row, border_radius=8)
                pygame.draw.rect(screen, accent, row, 1, border_radius=8)
                pygame.draw.rect(screen, accent, (row.x, row.y + 9, 3, 24), border_radius=1)
            self.text(screen, 'small', f'{index + 1:02}', accent if active else (84, 105, 131), (row.x + 16, row.y + 8, 32, 26))
            self.text(screen, 'item', MODES[index][0], white if active else muted, (row.x + 62, row.y + 3, 390, 36))
            if active:
                self.text(screen, 'item', '>', accent, (row.right - 34, row.y + 3, 22, 36))

        pygame.draw.rect(screen, (16, 23, 39), (636, 190, 574, 438), border_radius=16)
        self.text(screen, 'small', 'FIGHTER SHOWCASE', accent, (662, 205, 400, 26))
        self.animation_accumulator += min(dt, 0.1) * settings.FPS
        while self.animation_accumulator >= 1:
            for fighter in self.fighters:
                fighter.update()
            self.animation_accumulator -= 1
        self.world.blit(self.arena, (0, 0))
        for fighter in self.fighters:
            fighter.draw(self.world)
        arena_crop = self.world.subsurface((160, 150, 960, settings.WINDOW_HEIGHT - 150))
        pygame.transform.smoothscale(arena_crop, self.preview.get_size(), self.preview)
        screen.blit(self.preview, (663, 243))
        pygame.draw.rect(screen, (65, 77, 100), (663, 243, 520, 218), 1, border_radius=2)
        self.text(screen, 'small', 'ROOK', white, (677, 251, 180, 24))
        self.text(screen, 'small', 'VEX', white, (990, 251, 180, 24), 'right')
        # A solid caption strip gives mode details a consistent readable backdrop.
        pygame.draw.rect(screen, (16, 23, 39), (651, 462, 544, 155))
        _, heading, line1, line2, tag = MODES[selected]
        self.text(screen, 'small', tag, accent, (663, 470, 520, 24))
        self.text(screen, 'heading', heading, white, (663, 499, 520, 43))
        self.text(screen, 'body', line1, muted, (663, 548, 520, 27))
        self.text(screen, 'body', line2, muted, (663, 576, 520, 27))
        pygame.draw.line(screen, (45, 57, 79), (70, 652), (1210, 652))
        self.text(screen, 'small', 'W / S  OR  UP / DOWN', muted, (74, 668, 270, 26))
        self.text(screen, 'small', 'ENTER / CLICK  SELECT', cyan, (405, 668, 340, 26))
        self.text(screen, 'small', 'ESC  EXIT', muted, (1020, 668, 184, 26), 'right')

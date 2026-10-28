"""Presentation for the main arcade lobby."""
import math
import pygame
from ui import retro, theme
import settings
from characters import character_data, sprite_fighter


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
        # Shared drawing/hit rectangles preserve keyboard and mouse navigation.
        self.rows = [pygame.Rect(72, 242 + i * 55, 540, 48) for i in range(len(MODES))]
        self.fonts = {name: retro.font(size=size) for name, size in (
            ('heading', 32), ('item', 33), ('body', 20), ('small', 17))}

    def text(self, surface, font, text, color, rect, align='left'):
        theme.bold_text(surface, self.fonts[font], text, color, rect, align=align,
                        weight=1 if font in ('heading', 'item') else 0)

    def draw(self, screen, selected, elapsed, dt):
        theme.background(screen, elapsed, shade=65)
        theme.logo(screen, elapsed, y=12)
        self.text(screen, 'small', 'CITY / OCEAN / ARCADE', theme.PALE, (380, 207, 520, 24), 'center')
        for index, row in enumerate(self.rows):
            active = index == selected
            pygame.draw.rect(screen, (4, 13, 27), row.move(4, 4))
            pygame.draw.rect(screen, (35, 65, 91) if active else (13, 29, 49), row)
            pygame.draw.rect(screen, theme.GOLD if active else (71, 109, 140), row, 3 if active else 1)
            if active:
                pulse = 4 + round(math.sin(elapsed * 5) * 3)
                self.text(screen, 'item', '>', theme.GOLD, (row.x + 14 + pulse, row.y, 30, 46))
                pygame.draw.line(screen, theme.GOLD, (row.x + 52, row.bottom - 2),
                                 (row.right - 24, row.bottom - 2), 2)
            color = theme.GOLD if active else theme.PALE
            self.text(screen, 'item', MODES[index][0], color,
                      (row.x + 52, row.y + 1, row.width - 70, 46), 'center')

        _, heading, line1, line2, tag = MODES[selected]
        theme.panel(screen, (692, 270, 510, 172))
        self.text(screen, 'small', tag, theme.GOLD, (716, 282, 462, 24))
        self.text(screen, 'heading', heading, theme.PALE, (716, 311, 462, 40))
        self.text(screen, 'body', line1, theme.MUTED, (716, 363, 462, 26))
        self.text(screen, 'body', line2, theme.MUTED, (716, 399, 462, 26))
        # Idle sprites and a rooftop recreate the title-screen diorama.
        pygame.draw.rect(screen, (22, 40, 63), (726, 617, 494, 43))
        pygame.draw.rect(screen, theme.PALE, (726, 615, 494, 4))
        pygame.draw.rect(screen, theme.BLUE, (726, 621, 494, 7))
        for x in range(738, 1220, 44):
            pygame.draw.line(screen, (64, 98, 129), (x, 630), (x + 30, 658), 3)
        for asset, x, facing, height in (('rook', 849, 1, 160), ('vex', 1098, -1, 151)):
            frame = sprite_fighter.preview_frame(asset, facing)
            bounds = frame.get_bounding_rect()
            frame = frame.subsurface(bounds)
            image = pygame.transform.scale(frame, (round(frame.get_width() * height / frame.get_height()), height))
            character = character_data.get(asset)
            lift = sprite_fighter.hover_offset(character, elapsed * settings.FPS)
            screen.blit(image, image.get_rect(midbottom=(x, 615 - round(lift) + round(math.sin(elapsed * 2 + x) * 2))))
        theme.footer(screen, 'W S / ARROWS: SELECT     ENTER / CLICK: START     ESC: QUIT')

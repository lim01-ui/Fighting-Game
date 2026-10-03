import pygame
import settings
from audio import sound_fx


def _draw_title(surface, font, text, y):
    img = font.render(text, True, settings.WHITE)
    rect = img.get_rect(center=(settings.WINDOW_WIDTH // 2, y))
    surface.blit(img, rect)


def _draw_choices(surface, font, choices, selected):
    start_y = 260
    gap = 70
    for i, label in enumerate(choices):
        color = (255, 240, 120) if i == selected else settings.WHITE
        img = font.render(label, True, color)
        rect = img.get_rect(center=(settings.WINDOW_WIDTH // 2, start_y + i * gap))
        surface.blit(img, rect)


def run_main_menu(screen, clock):
    title_font = pygame.font.SysFont("Arial", 62, bold=True)
    item_font = pygame.font.SysFont("Arial", 30, bold=True)
    subtitle_font = pygame.font.SysFont("Arial", 19, bold=True)
    hint_font = pygame.font.SysFont("Arial", 18)
    choices = [
        "LOCAL VS CPU",
        "TRAINING MODE",
        "HOST LAN MATCH",
        "JOIN LAN MATCH",
        "HOW TO PLAY",
        "SETTINGS",
        "EXIT GAME",
    ]
    selected = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "EXIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sound_fx.play("menu_back")
                    return "EXIT"
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(choices)
                    sound_fx.play("menu_move")
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(choices)
                    sound_fx.play("menu_move")
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    sound_fx.play("menu_confirm")
                    return (
                        "1VBOT",
                        "TRAINING",
                        "LAN_HOST",
                        "LAN_JOIN",
                        "TUTORIAL",
                        "SETTINGS",
                        "EXIT",
                    )[selected]

        screen.fill((7, 10, 23))
        pygame.draw.rect(screen, (14, 20, 38), (0, 0, settings.WINDOW_WIDTH, 150))
        pygame.draw.line(screen, (42, 190, 255), (0, 150), (settings.WINDOW_WIDTH, 150), 2)
        title = title_font.render("PYTHON FIGHTERS", True, settings.WHITE)
        screen.blit(title, (72, 42))
        subtitle = subtitle_font.render(
            "ARCADE LOBBY   /   SELECT YOUR NEXT FIGHT",
            True, (105, 215, 255),
        )
        screen.blit(subtitle, (78, 112))

        left_panel = pygame.Rect(70, 190, 540, 438)
        pygame.draw.rect(screen, (13, 20, 38), left_panel, border_radius=18)
        pygame.draw.rect(screen, (45, 65, 98), left_panel, 2, border_radius=18)
        section = subtitle_font.render("GAME MODES", True, (150, 170, 205))
        screen.blit(section, (left_panel.x + 28, left_panel.y + 20))
        for index, label in enumerate(choices):
            row = pygame.Rect(left_panel.x + 17, left_panel.y + 55 + index * 49,
                              left_panel.width - 34, 42)
            if index == selected:
                pygame.draw.rect(screen, (27, 75, 105), row, border_radius=10)
                pygame.draw.rect(screen, (70, 205, 255), row, 2, border_radius=10)
                color = (255, 236, 145)
            else:
                color = (220, 226, 242)
            number = subtitle_font.render(f"{index + 1:02}", True, (100, 190, 225))
            screen.blit(number, (row.x + 15, row.y + 9))
            label_image = pygame.font.SysFont("Arial", 26, bold=True).render(
                label, True, color
            )
            screen.blit(label_image, (row.x + 64, row.y + 4))

        right_panel = pygame.Rect(650, 190, 560, 438)
        pygame.draw.rect(screen, (13, 20, 38), right_panel, border_radius=18)
        pygame.draw.rect(screen, (45, 65, 98), right_panel, 2, border_radius=18)
        pygame.draw.rect(screen, (22, 32, 54), (690, 260, 480, 230), border_radius=14)
        pygame.draw.line(screen, (45, 65, 98), (930, 270), (930, 480), 2)
        for center, color in (((815, 360), (74, 178, 255)), ((1045, 360), (255, 91, 118))):
            pygame.draw.circle(screen, color, center, 57, 3)
            pygame.draw.circle(screen, (35, 48, 72), center, 41)
            pygame.draw.circle(screen, color, (center[0], center[1] - 7), 15)
            pygame.draw.line(screen, color, (center[0], center[1] + 10),
                             (center[0], center[1] + 42), 7)
            pygame.draw.line(screen, color, (center[0] - 20, center[1] + 25),
                             (center[0] + 20, center[1] + 25), 6)
        versus = title_font.render("VS", True, (255, 228, 118))
        screen.blit(versus, versus.get_rect(center=(930, 365)))
        ready = item_font.render("FIGHTERS READY", True, settings.WHITE)
        screen.blit(ready, ready.get_rect(center=(930, 535)))
        detail = subtitle_font.render(
            "LOCAL PLAY   •   TRAINING   •   DIRECT-IP LAN",
            True, (150, 170, 205),
        )
        screen.blit(detail, detail.get_rect(center=(930, 570)))
        hint = hint_font.render(
            "UP/DOWN or W/S: navigate    ENTER: select    ESC: quit",
            True, (185, 195, 215),
        )
        screen.blit(hint, hint.get_rect(
            center=(settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT - 34)
        ))
        pygame.display.flip()
        clock.tick(settings.FPS)


def run_tutorial(screen, clock):
    """Show a short controls-aware introduction to fighting."""
    title_font = pygame.font.SysFont("Arial", 48, bold=True)
    heading_font = pygame.font.SysFont("Arial", 30, bold=True)
    body_font = pygame.font.SysFont("Arial", 23)
    hint_font = pygame.font.SysFont("Arial", 18)
    pages = (
        (
            "MOVE AND FACE YOUR OPPONENT",
            "Walk toward the opponent to close distance.",
            "Your fighter automatically turns to face them.",
            "Jump and crouch to vary your approach.",
        ),
        (
            "CHOOSE YOUR ATTACK",
            "Light is quick and useful up close.",
            "Heavy attacks deal more damage but recover slower.",
            "Crouch or jump, then press Light/Heavy for new attacks.",
        ),
        (
            "CHARGE YOUR ULTIMATE",
            "Deal and take damage to charge the ultimate meter.",
            "At 100%, press Special to unleash your fighter's Ultimate.",
            "Every fighter has a distinct ultimate move and effect.",
        ),
        (
            "BLOCK AND FIND AN OPENING",
            "Hold the direction away from your opponent to block.",
            "Blocking reduces damage, but does not make you invulnerable.",
            "Punish a missed heavy attack while your opponent recovers.",
        ),
        (
            "PRACTICE YOUR COMBOS",
            "Land another hit before the combo timer expires.",
            "Training mode shows damage and your best combo.",
            "Press T to set the dummy to stand, block, or attack.",
        ),
    )
    page = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "EXIT"
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_ESCAPE:
                sound_fx.play("menu_back")
                return "BACK"
            if event.key in (pygame.K_RIGHT, pygame.K_DOWN, pygame.K_d, pygame.K_s):
                page = (page + 1) % len(pages)
                sound_fx.play("menu_move")
            elif event.key in (pygame.K_LEFT, pygame.K_UP, pygame.K_a, pygame.K_w):
                page = (page - 1) % len(pages)
                sound_fx.play("menu_move")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                sound_fx.play("menu_confirm")
                return "TRAINING"

        screen.fill((7, 10, 23))
        pygame.draw.rect(screen, (14, 20, 38), (0, 0, settings.WINDOW_WIDTH, 150))
        pygame.draw.line(screen, (42, 190, 255), (0, 150),
                         (settings.WINDOW_WIDTH, 150), 2)
        title = title_font.render("FIGHTER FIELD GUIDE", True, settings.WHITE)
        screen.blit(title, title.get_rect(center=(settings.WINDOW_WIDTH // 2, 86)))

        panel = pygame.Rect(150, 195, settings.WINDOW_WIDTH - 300, 380)
        pygame.draw.rect(screen, (13, 20, 38), panel, border_radius=18)
        pygame.draw.rect(screen, (45, 65, 98), panel, 2, border_radius=18)
        heading, *lines = pages[page]
        heading_image = heading_font.render(heading, True, (255, 230, 125))
        screen.blit(heading_image, heading_image.get_rect(
            center=(panel.centerx, panel.y + 62)
        ))
        for index, text in enumerate(lines):
            image = body_font.render(text, True, (220, 226, 242))
            screen.blit(image, image.get_rect(
                center=(panel.centerx, panel.y + 135 + index * 48)
            ))

        movement = (
            f"MOVE {settings.P1_KEYS['left'].upper()}/{settings.P1_KEYS['right'].upper()}   "
            f"JUMP {settings.P1_KEYS['jump'].upper()}   "
            f"CROUCH {settings.P1_KEYS['crouch'].upper()}"
        )
        attacks = (
            f"LIGHT {settings.P1_KEYS['light'].upper()}   "
            f"HEAVY {settings.P1_KEYS['heavy'].upper()}   "
            f"SPECIAL {settings.P1_KEYS['special'].upper()}"
        )
        controls_font = pygame.font.SysFont("Arial", 19, bold=True)
        for index, text in enumerate((movement, attacks)):
            image = controls_font.render(text, True, (100, 215, 255))
            screen.blit(image, image.get_rect(
                center=(settings.WINDOW_WIDTH // 2, 615 + index * 27)
            ))
        progress = hint_font.render(
            f"PAGE {page + 1} / {len(pages)}     LEFT/RIGHT: BROWSE",
            True, (175, 190, 215),
        )
        screen.blit(progress, progress.get_rect(
            center=(settings.WINDOW_WIDTH // 2, 680)
        ))
        hint = hint_font.render(
            "ENTER: START TRAINING    ESC: BACK",
            True, (175, 190, 215),
        )
        screen.blit(hint, hint.get_rect(
            center=(settings.WINDOW_WIDTH // 2, 704)
        ))
        pygame.display.flip()
        clock.tick(settings.FPS)


def run_difficulty_menu(screen, clock):
    title_font = pygame.font.SysFont("Arial", 56, bold=True)
    item_font = pygame.font.SysFont("Arial", 34, bold=True)
    hint_font = pygame.font.SysFont("Arial", 20)
    choices = ["EASY", "NORMAL", "HARD"]
    selected = 1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sound_fx.play("menu_back")
                    return None
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(choices)
                    sound_fx.play("menu_move")
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(choices)
                    sound_fx.play("menu_move")
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    sound_fx.play("menu_confirm")
                    return choices[selected]

        screen.fill((20, 20, 40))
        _draw_title(screen, title_font, "SELECT DIFFICULTY", 150)
        _draw_choices(screen, item_font, choices, selected)
        hint = hint_font.render(
            "Up/Down to move   Enter to confirm   ESC to go back",
            True, (200, 200, 200),
        )
        screen.blit(hint, (30, settings.WINDOW_HEIGHT - 40))
        pygame.display.flip()
        clock.tick(settings.FPS)

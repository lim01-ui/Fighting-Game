import pygame
from ui import retro
import settings
from audio import sound_fx, preferences
from ui.text_layout import draw_text_fit


def _draw_title(surface, font, text, y):
    draw_text_fit(
        surface, font, text, settings.WHITE,
        pygame.Rect(30, y - font.get_height() // 2,
                    settings.WINDOW_WIDTH - 60, font.get_height()),
    )


def _draw_choices(surface, font, choices, selected):
    start_y = 260
    gap = 70
    for i, label in enumerate(choices):
        color = (255, 240, 120) if i == selected else settings.WHITE
        draw_text_fit(
            surface, font, label, color,
            pygame.Rect(30, start_y + i * gap - font.get_height() // 2,
                        settings.WINDOW_WIDTH - 60, font.get_height()),
        )


def run_main_menu(screen, clock):
    from ui.lobby_view import LobbyView, MODES
    view = LobbyView()
    choices = [mode[0] for mode in MODES]
    selected = 0
    rows = view.rows
    results = ("1VBOT", "TRAINING", "LAN_HOST", "LAN_JOIN", "TUTORIAL", "SETTINGS", "EXIT")
    elapsed = 0.0
    dt = 1.0 / settings.FPS

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "EXIT"
            if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
                for index, row in enumerate(rows):
                    if row.collidepoint(event.pos):
                        selected = index
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            sound_fx.play("menu_confirm")
                            return results[selected]
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

        view.draw(screen, selected, elapsed, dt)
        retro.present(screen)
        dt = clock.tick(settings.FPS) / 1000.0
        elapsed += dt



def run_tutorial(screen, clock):
    """Show a short controls-aware introduction to fighting."""
    title_font = retro.font("Arial", 48, bold=True)
    heading_font = retro.font("Arial", 30, bold=True)
    body_font = retro.font("Arial", 23)
    hint_font = retro.font("Arial", 18)
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
            f"Hold {preferences.binding_label(settings.P1_KEYS['block'])} or move away to block.",
            "Tap block just before impact for a perfect parry.",
            "Parries cancel the attack and leave the opponent open.",
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
        draw_text_fit(
            screen, title_font, "FIGHTER FIELD GUIDE", settings.WHITE,
            pygame.Rect(40, 48, settings.WINDOW_WIDTH - 80, 76),
        )

        panel = pygame.Rect(150, 195, settings.WINDOW_WIDTH - 300, 380)
        pygame.draw.rect(screen, (13, 20, 38), panel, border_radius=0)
        pygame.draw.rect(screen, (45, 65, 98), panel, 2, border_radius=0)
        heading, *lines = pages[page]
        draw_text_fit(
            screen, heading_font, heading, (255, 230, 125),
            pygame.Rect(panel.x + 24, panel.y + 32, panel.width - 48, 60),
        )
        for index, text in enumerate(lines):
            draw_text_fit(
                screen, body_font, text, (220, 226, 242),
                pygame.Rect(panel.x + 28, panel.y + 111 + index * 48,
                            panel.width - 56, 44),
            )

        movement = (
            f"MOVE {preferences.binding_label(settings.P1_KEYS['left'])}/{preferences.binding_label(settings.P1_KEYS['right'])}   "
            f"JUMP {preferences.binding_label(settings.P1_KEYS['jump'])}   "
            f"CROUCH {preferences.binding_label(settings.P1_KEYS['crouch'])}   "
            f"BLOCK {preferences.binding_label(settings.P1_KEYS['block'])}"
        )
        attacks = (
            f"LIGHT {preferences.binding_label(settings.P1_KEYS['light'])}   "
            f"HEAVY {preferences.binding_label(settings.P1_KEYS['heavy'])}   "
            f"SPECIAL {preferences.binding_label(settings.P1_KEYS['special'])}"
        )
        controls_font = retro.font("Arial", 19, bold=True)
        for index, text in enumerate((movement, attacks)):
            draw_text_fit(
                screen, controls_font, text, (100, 215, 255),
                pygame.Rect(35, 601 + index * 27,
                            settings.WINDOW_WIDTH - 70, 28),
            )
        draw_text_fit(
            screen, hint_font,
            f"PAGE {page + 1} / {len(pages)}     LEFT/RIGHT: BROWSE",
            (175, 190, 215),
            pygame.Rect(20, 662, settings.WINDOW_WIDTH - 40, 24),
        )
        draw_text_fit(
            screen, hint_font, "ENTER: START TRAINING    ESC: BACK",
            (175, 190, 215),
            pygame.Rect(20, 690, settings.WINDOW_WIDTH - 40, 26),
        )
        retro.present(screen)
        clock.tick(settings.FPS)


def run_difficulty_menu(screen, clock):
    title_font = retro.font("Arial", 56, bold=True)
    item_font = retro.font("Arial", 34, bold=True)
    hint_font = retro.font("Arial", 20)
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
        draw_text_fit(
            screen, hint_font,
            "Up/Down to move   Enter to confirm   ESC to go back",
            (200, 200, 200),
            pygame.Rect(20, settings.WINDOW_HEIGHT - 58,
                        settings.WINDOW_WIDTH - 40, 38),
            align="left",
        )
        retro.present(screen)
        clock.tick(settings.FPS)

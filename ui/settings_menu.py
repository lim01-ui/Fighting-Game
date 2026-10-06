"""Keyboard-accessible audio and display preferences screen."""

import pygame

import settings
from audio import music, preferences, sound_fx
from ui.text_layout import draw_text_fit


VOLUME_KEYS = ("master_volume", "music_volume", "sfx_volume")
VOLUME_LABELS = ("MASTER VOLUME", "MUSIC VOLUME", "SOUND EFFECTS")
CONTROL_LABELS = {
    "left": "MOVE LEFT",
    "right": "MOVE RIGHT",
    "jump": "JUMP",
    "crouch": "CROUCH",
    "block": "BLOCK / PARRY",
    "light": "LIGHT ATTACK",
    "heavy": "HEAVY ATTACK",
    "special": "SPECIAL ATTACK",
}


def _set_fullscreen(screen, enabled):
    flags = pygame.FULLSCREEN if enabled else 0
    return pygame.display.set_mode(
        (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), flags
    )


def _refresh_audio():
    music.refresh_volume()


def run_controls_menu(screen, clock):
    title_font = pygame.font.SysFont("Arial", 46, bold=True)
    item_font = pygame.font.SysFont("Arial", 25, bold=True)
    hint_font = pygame.font.SysFont("Arial", 18)
    actions = tuple(settings.P1_KEYS)
    selected = 0
    listening_action = None
    message = ""

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type != pygame.KEYDOWN:
                continue
            if listening_action is not None:
                if event.key == pygame.K_ESCAPE:
                    listening_action = None
                    message = "Rebinding canceled"
                    continue
                key_name = preferences.key_name_from_code(event.key)
                updated = settings.P1_KEYS.copy()
                updated[listening_action] = key_name
                if preferences.is_valid_control_map(updated):
                    preferences.set_value("p1_controls", updated)
                    preferences.save()
                    message = f"{CONTROL_LABELS[listening_action]} set to {key_name}"
                else:
                    message = "Key unavailable, reserved, or already assigned"
                listening_action = None
                continue

            if event.key == pygame.K_ESCAPE:
                preferences.save()
                return screen
            if event.key in (pygame.K_DOWN, pygame.K_s):
                selected = (selected + 1) % (len(actions) + 1)
                sound_fx.play("menu_move")
            elif event.key in (pygame.K_UP, pygame.K_w):
                selected = (selected - 1) % (len(actions) + 1)
                sound_fx.play("menu_move")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if selected == len(actions):
                    sound_fx.play("menu_back")
                    return screen
                listening_action = actions[selected]
                message = f"Press a key for {CONTROL_LABELS[listening_action]}"
                sound_fx.play("menu_confirm")

        screen.fill((12, 12, 26))
        draw_text_fit(
            screen, title_font, "PLAYER 1 CONTROLS", settings.WHITE,
            pygame.Rect(40, 75, settings.WINDOW_WIDTH - 80, 70),
        )

        for index, action in enumerate(actions):
            y = 155 + index * 47
            color = (255, 230, 110) if index == selected else settings.WHITE
            label = CONTROL_LABELS[action]
            binding = "PRESS A KEY..." if action == listening_action else settings.P1_KEYS[action]
            draw_text_fit(
                screen, item_font, label, color,
                pygame.Rect(300, y, 390, 36), align="left",
            )
            draw_text_fit(
                screen, item_font, binding, color,
                pygame.Rect(760, y, 220, 36), align="left",
            )

        back_color = (255, 230, 110) if selected == len(actions) else settings.WHITE
        draw_text_fit(
            screen, item_font, "BACK", back_color,
            pygame.Rect(20, 530, settings.WINDOW_WIDTH - 40, 36),
        )
        if message:
            draw_text_fit(
                screen, hint_font, message, (255, 205, 110),
                pygame.Rect(20, 575, settings.WINDOW_WIDTH - 40, 28),
            )
        draw_text_fit(
            screen, hint_font, "UP/DOWN select   ENTER rebind   ESC cancel/back",
            (195, 200, 215),
            pygame.Rect(20, settings.WINDOW_HEIGHT - 50,
                        settings.WINDOW_WIDTH - 40, 36),
        )
        pygame.display.flip()
        clock.tick(settings.FPS)


def run_settings_menu(screen, clock):
    title_font = pygame.font.SysFont("Arial", 52, bold=True)
    item_font = pygame.font.SysFont("Arial", 26, bold=True)
    hint_font = pygame.font.SysFont("Arial", 18)
    selected = 0
    row_y = 220
    row_gap = 66
    options = (
        *VOLUME_LABELS,
        "FULLSCREEN",
        "PLAYER 1 CONTROLS",
        "RESTORE DEFAULTS",
        "BACK",
    )

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type != pygame.KEYDOWN:
                continue
            if event.key == pygame.K_ESCAPE:
                preferences.save()
                return screen
            if event.key in (pygame.K_DOWN, pygame.K_s):
                selected = (selected + 1) % len(options)
                sound_fx.play("menu_move")
            elif event.key in (pygame.K_UP, pygame.K_w):
                selected = (selected - 1) % len(options)
                sound_fx.play("menu_move")
            elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                delta = 0.05 if event.key == pygame.K_RIGHT else -0.05
                if selected < len(VOLUME_KEYS):
                    key = VOLUME_KEYS[selected]
                    preferences.set_value(key, preferences.get(key) + delta)
                    _refresh_audio()
                    preferences.save()
                    sound_fx.play("menu_confirm")
                elif selected == 3:
                    enabled = not preferences.get("fullscreen")
                    screen = _set_fullscreen(screen, enabled)
                    preferences.set_value("fullscreen", enabled)
                    preferences.save()
                    sound_fx.play("menu_confirm")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if selected == 3:
                    enabled = not preferences.get("fullscreen")
                    screen = _set_fullscreen(screen, enabled)
                    preferences.set_value("fullscreen", enabled)
                    preferences.save()
                    sound_fx.play("menu_confirm")
                elif selected == 4:
                    screen = run_controls_menu(screen, clock)
                    if screen is None:
                        return None
                elif selected == 5:
                    preferences.reset()
                    screen = _set_fullscreen(screen, preferences.get("fullscreen"))
                    _refresh_audio()
                    preferences.save()
                    sound_fx.play("menu_confirm")
                elif selected == 6:
                    preferences.save()
                    sound_fx.play("menu_back")
                    return screen

        screen.fill((12, 12, 26))
        draw_text_fit(
            screen, title_font, "SETTINGS", settings.WHITE,
            pygame.Rect(40, 75, settings.WINDOW_WIDTH - 80, 80),
        )

        for index, label in enumerate(options):
            y = row_y + index * row_gap
            color = (255, 230, 110) if index == selected else settings.WHITE
            label_image = item_font.render(label, True, color)
            screen.blit(label_image, (settings.WINDOW_WIDTH // 2 - 310, y))

            if index < len(VOLUME_KEYS):
                value = preferences.get(VOLUME_KEYS[index])
                track = pygame.Rect(settings.WINDOW_WIDTH // 2 + 25, y + 4, 300, 20)
                pygame.draw.rect(screen, (35, 38, 55), track, border_radius=8)
                fill = track.copy()
                fill.width = int(track.width * value)
                pygame.draw.rect(screen, (75, 190, 245), fill, border_radius=8)
                pygame.draw.rect(screen, (190, 200, 220), track, 2, border_radius=8)
                percent = item_font.render(f"{round(value * 100)}%", True, settings.WHITE)
                screen.blit(percent, (track.right + 18, y - 1))
            elif index == 3:
                status = "ON" if preferences.get("fullscreen") else "OFF"
                screen.blit(item_font.render(status, True, color), (settings.WINDOW_WIDTH // 2 + 25, y))

        hint = hint_font.render(
            "UP/DOWN select   LEFT/RIGHT adjust   ENTER confirm   ESC back",
            True, (195, 200, 215),
        )
        screen.blit(hint, hint.get_rect(
            center=(settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT - 48)
        ))
        pygame.display.flip()
        clock.tick(settings.FPS)

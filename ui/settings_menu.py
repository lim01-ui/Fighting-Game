"""Mouse and keyboard options, including click-to-bind controls."""

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
    boxes = [pygame.Rect(740, 155 + index * 47, 260, 38)
             for index in range(len(actions))]
    back_rect = pygame.Rect(520, 550, 240, 44)
    reset_rect = pygame.Rect(430, 605, 420, 38)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    return screen
                if reset_rect.collidepoint(event.pos):
                    preferences.set_value("p1_controls", preferences.DEFAULTS["p1_controls"])
                    preferences.save()
                    listening_action = None
                    message = "Default controls restored"
                for index, box in enumerate(boxes):
                    if box.collidepoint(event.pos):
                        selected = index
                        listening_action = actions[index]
                        message = "Press any key to bind, or ESC to unbind"
                        sound_fx.play("menu_confirm")
                continue
            if event.type != pygame.KEYDOWN:
                continue
            if listening_action is not None:
                try:
                    preferences.bind_control(listening_action, event.key)
                    preferences.save()
                    label = preferences.binding_label(settings.P1_KEYS[listening_action])
                    message = f"{CONTROL_LABELS[listening_action]}: {label} (saved)"
                except ValueError:
                    message = "This key is unavailable. Choose another key."
                    continue
                listening_action = None
                continue

            if event.key == pygame.K_ESCAPE:
                preferences.save()
                return screen
            if event.key in (pygame.K_DOWN, pygame.K_s):
                selected = (selected + 1) % (len(actions) + 2)
                sound_fx.play("menu_move")
            elif event.key in (pygame.K_UP, pygame.K_w):
                selected = (selected - 1) % (len(actions) + 2)
                sound_fx.play("menu_move")
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if selected == len(actions):
                    sound_fx.play("menu_back")
                    return screen
                if selected == len(actions) + 1:
                    preferences.set_value("p1_controls", preferences.DEFAULTS["p1_controls"])
                    preferences.save()
                    message = "Default controls restored"
                    continue
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
            binding = ("PRESS A KEY..." if action == listening_action
                       else preferences.binding_label(settings.P1_KEYS[action]))
            pygame.draw.rect(screen, (27, 75, 105) if action == listening_action
                             else (24, 32, 52), boxes[index], border_radius=8)
            pygame.draw.rect(screen, color, boxes[index], 2, border_radius=8)
            draw_text_fit(
                screen, item_font, label, color,
                pygame.Rect(300, y, 390, 36), align="left",
            )
            draw_text_fit(
                screen, item_font, binding, color,
                boxes[index].inflate(-16, -4),
            )

        back_color = (255, 230, 110) if selected == len(actions) else settings.WHITE
        draw_text_fit(
            screen, item_font, "BACK", back_color,
            back_rect,
        )
        draw_text_fit(screen, hint_font, "RESTORE DEFAULT CONTROLS",
                      (255, 230, 110) if selected == len(actions) + 1 else settings.WHITE,
                      reset_rect)
        if message:
            draw_text_fit(
                screen, hint_font, message, (255, 205, 110),
                pygame.Rect(20, 530, settings.WINDOW_WIDTH - 40, 20),
            )
        draw_text_fit(
            screen, hint_font, "CLICK a box / ENTER: bind   ESC while binding: unbind   ESC: back",
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
    row_y = 185
    row_gap = 62
    options = (
        *VOLUME_LABELS,
        "FULLSCREEN",
        "PLAYER 1 CONTROLS",
        "RESTORE DEFAULTS",
        "BACK",
    )
    rows = [pygame.Rect(300, row_y + index * row_gap - 5, 760, 44)
            for index in range(len(options))]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.MOUSEMOTION:
                for index, row in enumerate(rows):
                    if row.collidepoint(event.pos):
                        selected = index
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked = next((i for i, row in enumerate(rows)
                                if row.collidepoint(event.pos)), None)
                if clicked is None:
                    continue
                selected = clicked
                if selected < len(VOLUME_KEYS):
                    if event.pos[0] < settings.WINDOW_WIDTH // 2 + 25:
                        continue
                    value = (event.pos[0] - (settings.WINDOW_WIDTH // 2 + 25)) / 300
                    preferences.set_value(VOLUME_KEYS[selected], value)
                    _refresh_audio()
                    preferences.save()
                    continue
                event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
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
            screen, title_font, "OPTIONS", settings.WHITE,
            pygame.Rect(40, 75, settings.WINDOW_WIDTH - 80, 80),
        )

        for index, label in enumerate(options):
            y = row_y + index * row_gap
            color = (255, 230, 110) if index == selected else settings.WHITE
            if index == selected:
                pygame.draw.rect(screen, (24, 38, 58), rows[index], border_radius=8)
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
            "CLICK: select / set volume   UP/DOWN: select   LEFT/RIGHT: adjust   ESC: back",
            True, (195, 200, 215),
        )
        screen.blit(hint, hint.get_rect(
            center=(settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT - 48)
        ))
        pygame.display.flip()
        clock.tick(settings.FPS)

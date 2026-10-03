"""Host/join screens for direct-IP LAN matches."""

import pygame

import settings
from audio import sound_fx
from network import lan


def _draw_panel(screen, title, lines, hint, accent=(70, 205, 255)):
    screen.fill((9, 12, 26))
    pygame.draw.rect(
        screen, (17, 24, 44),
        pygame.Rect(100, 75, settings.WINDOW_WIDTH - 200, settings.WINDOW_HEIGHT - 150),
        border_radius=22,
    )
    pygame.draw.rect(
        screen, accent,
        pygame.Rect(100, 75, settings.WINDOW_WIDTH - 200, settings.WINDOW_HEIGHT - 150),
        2, border_radius=22,
    )
    title_font = pygame.font.SysFont("Arial", 48, bold=True)
    body_font = pygame.font.SysFont("Arial", 27, bold=True)
    hint_font = pygame.font.SysFont("Arial", 19)
    title_image = title_font.render(title, True, settings.WHITE)
    screen.blit(title_image, title_image.get_rect(center=(settings.WINDOW_WIDTH // 2, 150)))
    for index, (text, color) in enumerate(lines):
        image = body_font.render(text, True, color)
        screen.blit(image, image.get_rect(
            center=(settings.WINDOW_WIDTH // 2, 265 + index * 58)
        ))
    hint_image = hint_font.render(hint, True, (185, 195, 215))
    screen.blit(hint_image, hint_image.get_rect(
        center=(settings.WINDOW_WIDTH // 2, settings.WINDOW_HEIGHT - 130)
    ))
    pygame.display.flip()


def run_host_lobby(screen, clock):
    """Wait for a single LAN guest; Escape cancels hosting."""
    listener = None
    try:
        listener = lan.create_host()
        address = lan.local_ip_address()
    except OSError as error:
        if listener is not None:
            listener.close()
        _draw_panel(
            screen, "COULD NOT HOST",
            [(str(error), (255, 150, 150))],
            "Press any key to return",
            accent=(255, 115, 115),
        )
        while True:
            for event in pygame.event.get():
                if event.type in (pygame.QUIT, pygame.KEYDOWN):
                    return None
            clock.tick(settings.FPS)

    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    sound_fx.play("menu_back")
                    return None

            peer = lan.accept_if_ready(listener)
            if peer is not None:
                sound_fx.play("menu_confirm")
                return peer

            _draw_panel(
                screen, "LAN LOBBY — HOST",
                [
                    (f"ADDRESS  {address}:{lan.PORT}", (100, 220, 255)),
                    ("WAITING FOR ONE PLAYER...", settings.WHITE),
                ],
                "On the other computer choose JOIN LAN and enter this address   •   ESC: cancel",
            )
            clock.tick(settings.FPS)
    finally:
        listener.close()


def run_join_lobby(screen, clock):
    """Collect a host IP address and connect to its LAN lobby."""
    address = ""
    message = "Enter the host's IPv4 address"
    message_color = (185, 195, 215)
    pygame.key.start_text_input()
    try:
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        sound_fx.play("menu_back")
                        return None
                    if event.key == pygame.K_BACKSPACE:
                        address = address[:-1]
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        if not address:
                            message = "Enter an IPv4 address first"
                            message_color = (255, 180, 120)
                            continue
                        try:
                            peer = lan.connect_to_host(address)
                        except OSError as error:
                            message = f"Could not connect: {error}"
                            message_color = (255, 150, 150)
                            continue
                        sound_fx.play("menu_confirm")
                        return peer
                elif event.type == pygame.TEXTINPUT:
                    allowed = "0123456789."
                    address += "".join(char for char in event.text if char in allowed)

            _draw_panel(
                screen, "LAN LOBBY — JOIN",
                [
                    (address or "TYPE HOST IP ADDRESS", (100, 220, 255)),
                    (message, message_color),
                ],
                f"Enter: connect on port {lan.PORT}   •   Backspace: edit   •   ESC: back",
                accent=(155, 125, 255),
            )
            clock.tick(settings.FPS)
    finally:
        pygame.key.stop_text_input()


def show_lan_message(screen, clock, title, message):
    _draw_panel(
        screen, title, [(message, (255, 180, 150))],
        "Press any key to return to the lobby",
        accent=(255, 135, 110),
    )
    while True:
        for event in pygame.event.get():
            if event.type in (pygame.QUIT, pygame.KEYDOWN):
                return
        clock.tick(settings.FPS)

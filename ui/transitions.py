# ui/transitions.py
import pygame
import settings
from effects import easing


def _center_text(surface, font, text, y, color, alpha=255):
    img = font.render(text, True, color)
    if alpha < 255:
        img.set_alpha(alpha)
    rect = img.get_rect(center=(settings.WINDOW_WIDTH // 2, y))
    surface.blit(img, rect)


def draw_countdown(surface, round_number, progress, fonts):
    overlay = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
    overlay.set_alpha(160)
    overlay.fill((0, 0, 0))
    surface.blit(overlay, (0, 0))

    big_font = fonts["big"]
    huge_font = fonts["huge"]

    if progress < 0.70:
        p = easing.ease_out_cubic(progress / 0.70)
        combined = "ROUND " + str(round_number)
        img = big_font.render(combined, True, (255, 240, 120))
        start_x = settings.WINDOW_WIDTH // 2 - 500
        end_x = settings.WINDOW_WIDTH // 2
        cx = easing.lerp(start_x, end_x, p)
        r = img.get_rect(center=(cx, settings.WINDOW_HEIGHT // 2 - 30))
        surface.blit(img, r)
    else:
        p = (progress - 0.70) / 0.30
        scale = easing.ease_out_back(p, overshoot=1.6)
        img = huge_font.render("FIGHT!", True, (255, 80, 80))
        base_size = img.get_size()
        scaled = pygame.transform.smoothscale(
            img, (int(base_size[0] * scale), int(base_size[1] * scale)))
        r = scaled.get_rect(center=(settings.WINDOW_WIDTH // 2,
                                    settings.WINDOW_HEIGHT // 2))
        surface.blit(scaled, r)


def draw_round_over(surface, winner, round_end_reason, progress, fonts):
    overlay = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
    overlay.set_alpha(int(easing.lerp(0, 170, easing.ease_out_cubic(progress))))
    overlay.fill((0, 0, 0))
    surface.blit(overlay, (0, 0))

    head = "K.O." if round_end_reason == "ko" else "TIME UP"
    scale = easing.ease_out_back(min(1.0, progress / 0.30), overshoot=1.4)
    img = fonts["huge"].render(head, True, (255, 80, 80))
    base_size = img.get_size()
    scaled = pygame.transform.smoothscale(
        img, (int(base_size[0] * scale), int(base_size[1] * scale)))
    r = scaled.get_rect(center=(settings.WINDOW_WIDTH // 2, 230))
    surface.blit(scaled, r)

    if progress > 0.35:
        p2 = (progress - 0.35) / 0.65
        alpha = int(255 * easing.ease_out_cubic(p2))
        if winner == "p1":
            msg = "PLAYER 1 WINS ROUND"
        elif winner == "p2":
            msg = "PLAYER 2 WINS ROUND"
        else:
            msg = "DRAW"
        _center_text(surface, fonts["big"], msg, 340,
                     (255, 240, 120), alpha=alpha)


def draw_match_over(surface, header, rounds_text, progress, fonts,
                    winner_color=None, prompt="ENTER / R = new match     ESC = back to menu"):
    overlay = pygame.Surface((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
    overlay.set_alpha(int(easing.lerp(0, 190, easing.ease_out_cubic(progress))))
    overlay.fill((0, 0, 0))
    surface.blit(overlay, (0, 0))

    scale = easing.ease_out_back(min(1.0, progress / 0.35), overshoot=1.5)
    img = fonts["huge"].render("MATCH OVER", True, (255, 80, 80))
    base_size = img.get_size()
    scaled = pygame.transform.smoothscale(
        img, (int(base_size[0] * scale), int(base_size[1] * scale)))
    r = scaled.get_rect(center=(settings.WINDOW_WIDTH // 2,
                                settings.WINDOW_HEIGHT // 2 - 80))
    surface.blit(scaled, r)

    if progress > 0.30:
        p2 = (progress - 0.30) / 0.70
        alpha = int(255 * easing.ease_out_cubic(p2))
        win_color = winner_color or (255, 240, 120)
        _center_text(surface, fonts["big"], header,
                     settings.WINDOW_HEIGHT // 2 + 80, win_color, alpha=alpha)
        _center_text(surface, fonts["mid"], rounds_text,
                     settings.WINDOW_HEIGHT // 2 + 140, settings.WHITE, alpha=alpha)
        _center_text(surface, fonts["small"], prompt,
                     settings.WINDOW_HEIGHT - 60, settings.WHITE, alpha=alpha)

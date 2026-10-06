"""Small helpers for keeping rendered UI text inside its layout bounds."""

import pygame


def draw_text_fit(surface, font, text, color, rect, align="center", alpha=None):
    """Render text without allowing it to spill outside ``rect``."""
    image = font.render(str(text), True, color)
    if image.get_width() == 0 or image.get_height() == 0:
        return pygame.Rect(rect.left, rect.top, 0, 0)
    max_width = max(1, rect.width)
    max_height = max(1, rect.height)
    scale = min(1.0, max_width / image.get_width(), max_height / image.get_height())
    if scale < 1.0:
        image = pygame.transform.smoothscale(
            image,
            (max(1, int(image.get_width() * scale)),
             max(1, int(image.get_height() * scale))),
        )

    if align == "left":
        destination = image.get_rect(midleft=(rect.left, rect.centery))
    elif align == "right":
        destination = image.get_rect(midright=(rect.right, rect.centery))
    else:
        destination = image.get_rect(center=rect.center)
    if alpha is not None:
        image.set_alpha(alpha)
    surface.blit(image, destination)
    return destination

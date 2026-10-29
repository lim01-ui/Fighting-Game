"""Shared bitmap typography and nearest-neighbor arcade presentation.

Only presentation is pixelated; game coordinates and mouse targets stay intact.
The built-in 5x7 alphabet keeps the theme independent of installed system fonts.
"""

from functools import lru_cache

import pygame


INK = (10, 8, 24)
CYAN = (80, 240, 232)
PINK = (248, 96, 168)
GOLD = (248, 216, 104)
GREEN = (80, 240, 144)

# Each hexadecimal row contains five pixels, most significant bit on the left.
_ROWS = {
    "A": "0E 11 11 1F 11 11 11", "B": "1E 11 11 1E 11 11 1E",
    "C": "0F 10 10 10 10 10 0F", "D": "1E 11 11 11 11 11 1E",
    "E": "1F 10 10 1E 10 10 1F", "F": "1F 10 10 1E 10 10 10",
    "G": "0F 10 10 17 11 11 0F", "H": "11 11 11 1F 11 11 11",
    "I": "1F 04 04 04 04 04 1F", "J": "07 02 02 02 12 12 0C",
    "K": "11 12 14 18 14 12 11", "L": "10 10 10 10 10 10 1F",
    "M": "11 1B 15 15 11 11 11", "N": "11 19 15 13 11 11 11",
    "O": "0E 11 11 11 11 11 0E", "P": "1E 11 11 1E 10 10 10",
    "Q": "0E 11 11 11 15 12 0D", "R": "1E 11 11 1E 14 12 11",
    "S": "0F 10 10 0E 01 01 1E", "T": "1F 04 04 04 04 04 04",
    "U": "11 11 11 11 11 11 0E", "V": "11 11 11 11 11 0A 04",
    "W": "11 11 11 15 15 15 0A", "X": "11 11 0A 04 0A 11 11",
    "Y": "11 11 0A 04 04 04 04", "Z": "1F 01 02 04 08 10 1F",
    "0": "0E 11 13 15 19 11 0E", "1": "04 0C 04 04 04 04 0E",
    "2": "0E 11 01 02 04 08 1F", "3": "1E 01 01 0E 01 01 1E",
    "4": "02 06 0A 12 1F 02 02", "5": "1F 10 10 1E 01 01 1E",
    "6": "0E 10 10 1E 11 11 0E", "7": "1F 01 02 04 08 08 08",
    "8": "0E 11 11 0E 11 11 0E", "9": "0E 11 11 0F 01 01 0E",
    " ": "00 00 00 00 00 00 00", ".": "00 00 00 00 00 0C 0C",
    ",": "00 00 00 00 04 04 08", ":": "00 0C 0C 00 0C 0C 00",
    ";": "00 0C 0C 00 04 04 08", "!": "04 04 04 04 04 00 04",
    "?": "0E 11 01 02 04 00 04", "-": "00 00 00 1F 00 00 00",
    "_": "00 00 00 00 00 00 1F", "/": "01 02 02 04 08 08 10",
    "\\": "10 08 08 04 02 02 01", "'": "04 04 08 00 00 00 00",
    '"': "0A 0A 0A 00 00 00 00", "(": "02 04 08 08 08 04 02",
    ")": "08 04 02 02 02 04 08", "[": "0E 08 08 08 08 08 0E",
    "]": "0E 02 02 02 02 02 0E", "+": "00 04 04 1F 04 04 00",
    "=": "00 00 1F 00 1F 00 00", ">": "10 08 04 02 04 08 10",
    "<": "01 02 04 08 04 02 01", "%": "19 19 02 04 08 13 13",
    "#": "0A 0A 1F 0A 1F 0A 0A", "*": "00 15 0E 1F 0E 15 00",
    "|": "04 04 04 04 04 04 04", "@": "0E 11 17 15 17 10 0F",
}
_GLYPHS = {char: tuple(int(row, 16) for row in rows.split()) for char, rows in _ROWS.items()}


class PixelFont:
    def __init__(self, size):
        self.scale = max(1, round(size / 9))

    def get_height(self):
        return 9 * self.scale

    def get_linesize(self):
        return self.get_height()

    def size(self, text):
        return max(1, len(str(text)) * 6 * self.scale), self.get_height()

    def render(self, text, antialias, color, background=None):
        text = str(text).upper()
        image = pygame.Surface((max(1, len(text) * 6), 9), pygame.SRCALPHA)
        if background is not None:
            image.fill(background)
        for index, char in enumerate(text):
            for y, bits in enumerate(_GLYPHS.get(char, _GLYPHS["?"])):
                for x in range(5):
                    if bits & (1 << (4 - x)):
                        image.set_at((index * 6 + x, y + 1), color)
        return pygame.transform.scale(image, self.size(text))


@lru_cache(maxsize=128)
def font(name=None, size=20, bold=False, italic=False):
    """Accept SysFont's arguments so every screen uses the same bitmap face."""
    return PixelFont(size)


def pixelate(surface, step=4):
    """Resolve illustrated artwork into chunky pixels before drawing the HUD."""
    size = surface.get_size()
    pixels = pygame.transform.scale(surface, (max(1, size[0] // step), max(1, size[1] // step)))
    pygame.transform.scale(pixels, size, surface)


def present(screen):
    """Present the logical canvas through SDL's aspect-preserving scaler.

    Artwork is pixelated before compositing; nearest-neighbor display scaling
    preserves the finished HUD's small key labels and bitmap details.
    """
    pygame.display.flip()

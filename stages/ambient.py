"""Runtime motion for scenic backdrops; no per-frame random state."""
import math
from functools import lru_cache
import numpy as np
import pygame

_layers = {}


def _rect(region, size):
    return pygame.Rect(round(region[0] * size[0]), round(region[1] * size[1]),
                       max(1, round(region[2] * size[0])), max(1, round(region[3] * size[1])))


def _layer(source, key, region, mode):
    cache_key = (key, tuple(region), mode)
    if cache_key not in _layers:
        rect = _rect(region, source.get_size()).clip(source.get_rect())
        image = source.subsurface(rect).copy().convert_alpha()
        colors = pygame.surfarray.array3d(image).astype(np.int16)
        red, green, blue = (colors[:, :, channel] for channel in range(3))
        if mode == 'green':
            mask = (green > red * .85) & (green > blue * 1.15)
        elif mode in ('red', 'pink'):
            mask = (red > green * 1.2) & (red > blue * (1.0 if mode == 'red' else .78))
        elif mode == 'night':
            mask = (red + green + blue < 235) & (blue > red * 1.1)
        elif mode == 'teal':
            mask = (green > red * 1.2) & (blue > red * 1.15)
        elif mode == 'blue':
            mask = (blue > red * 1.25) & (red + green + blue > 160)
        elif mode == 'mist':
            mask = (green > 120) & (blue > 120) & (red < green * .95)
        else:
            mask = (red + green + blue > 480) & (np.maximum.reduce((red, green, blue))
                                                       - np.minimum.reduce((red, green, blue)) < 110)
        alpha = pygame.surfarray.pixels_alpha(image)
        alpha[:] = np.where(mask, 220 if mode in ('cloud', 'blue', 'mist') else 255, 0)
        del alpha
        _layers[cache_key] = image, rect
    return _layers[cache_key]


def _sway(surface, source, key, regions, t, cloth=False):
    for index, region in enumerate(regions):
        image, rect = _layer(source, key, region[:4], 'red' if cloth else region[4])
        for y in range(0, rect.height, 5):
            strength = (y / rect.height if cloth else 1 - y / rect.height) * 2
            offset = round(math.sin(t * 1.7 + y * .035 + index * 2) * strength)
            surface.blit(image, (rect.x + offset, rect.y + y),
                         (0, y, rect.width, min(5, rect.height - y)))


def _water(surface, source, regions, t):
    for region in regions:
        rect = _rect(region, surface.get_size()).clip(surface.get_rect())
        for y in range(rect.top, rect.bottom, 2):
            offset = round(math.sin(t * 2.1 + y * .28) * 2 + math.sin(y * .7 - t) * .8)
            area = pygame.Rect(rect.x, y, rect.width, min(2, rect.bottom - y))
            surface.blit(source, (rect.x + offset, y), area)
        for index in range(9):
            x = rect.left + (index * 73 + int(t * 8)) % max(1, rect.width - 12)
            y = rect.top + (index * 13) % max(1, rect.height)
            if .5 + .5 * math.sin(t * 2 + index) > .55:
                pygame.draw.line(surface, (75, 172, 187), (x, y), (x + 3 + index % 5, y))


def _sky(surface, source, key, spec, t):
    for index, region in enumerate(spec.get('clouds', ())):
        image, rect = _layer(source, key, region, spec.get('cloud_mode', 'cloud'))
        surface.blit(image, rect.move(round(math.sin(t * .16 + index) * 8), 0))
    if spec.get('aurora'):
        rect = _rect(spec['aurora'], surface.get_size())
        for x in range(rect.left, rect.right, 3):
            offset = round(math.sin(t * .65 + x * .025) * 3)
            surface.blit(source, (x, rect.top + offset),
                         (x, rect.top, min(3, rect.right - x), rect.height))
    for index in range(spec.get('stars', 0)):
        x, y = (index * 97 + 71) % 640, (index * 41 + 13) % 149
        if sum(source.get_at((x, y))[:3]) < 95:
            continue
        pulse = (.5 + .5 * math.sin(t * (1.1 + index % 3 * .2) + index * 1.8)) ** 3
        value = round(100 + pulse * 155)
        color = (value, value, 255)
        pygame.draw.rect(surface, color, (x, y, 1, 1))
        if pulse > .92 and index % 6 == 0:
            pygame.draw.line(surface, color, (x - 2, y), (x + 2, y))
            pygame.draw.line(surface, color, (x, y - 2), (x, y + 2))
    if spec.get('aurora') and t % 13 < 1.2:
        phase = t % 13
        x, y = round(80 + phase * 170), round(20 + phase * 48)
        for trail in range(12):
            c = max(50, 255 - trail * 16)
            pygame.draw.rect(surface, (c, c, min(255, c + 30)), (x - trail * 2, y - trail, 2, 1))


@lru_cache(maxsize=64)
def _glow(color, radius, strength):
    image = pygame.Surface((radius * 2 + 2, radius * 2 + 2), pygame.SRCALPHA)
    for ring in range(radius, 0, -1):
        alpha = round(strength * (1 - ring / (radius + 1)) ** 2)
        pygame.draw.circle(image, (*color, alpha), (radius + 1, radius + 1), ring)
    return image


def _lights(surface, spec, t):
    for index, point in enumerate(spec.get('lanterns', ())):
        x, y = round(point[0] * 640), round(point[1] * 360)
        intensity = round(120 + math.sin(t * 4.4 + index * 2) * 22 + math.sin(t * 9.2 + index) * 9)
        color = spec.get('lantern_color', (255, 179, 64))
        glow = _glow(color, 15 if index < 2 else 10, intensity // 12 * 12)
        surface.blit(glow, glow.get_rect(center=(x, y)))
        flame = (255, 237, 155) if color[0] > 200 else (195, 255, 255)
        pygame.draw.rect(surface, flame, (x - 1, y - (2 if intensity > 120 else 1), 2, 3))
    for index in range(spec.get('fireflies', 0)):
        x = round((index * 113 + t * (4 + index % 5) + math.sin(t * .8 + index) * 8) % 640)
        y = round(142 + (index * 53) % 149 + math.sin(t * 1.1 + index * 1.7) * 8)
        pulse = .5 + .5 * math.sin(t * 2.0 + index * 1.3)
        if pulse < .25:
            continue
        color = spec['glow']
        halo = _glow(color, 4, round(pulse * 6) * 24)
        surface.blit(halo, halo.get_rect(center=(x, y)))
        pygame.draw.rect(surface, color, (x, y, 1 if pulse < .8 else 2, 1))


def _leaves_and_grass(surface, spec, t):
    for index in range(spec.get('leaves', 0)):
        y = (index * 71 + t * (10 + index % 4)) % 302
        x = (index * 157 + t * 11 + math.sin(t * 1.3 + index + y * .02) * 15) % 640
        sway = math.sin(t * 3 + index)
        pygame.draw.polygon(surface, spec['leaf_color'], ((round(x), round(y)),
                             (round(x + 3), round(y + sway)), (round(x + 1), round(y + 2))))
    for index in range(55):
        x, y = (index * 83 + 17) % 640, 298 + index % 3
        bend, height = round(math.sin(t * 2 + index * .6) * 2), 3 + index % 4
        pygame.draw.line(surface, spec['grass'], (x, y), (x + bend, y - height))
        pygame.draw.line(surface, spec['grass'], (x, y), (x - 2 + bend, y - height + 2))
    if spec.get('birds'):
        for index in range(4):
            x, y = round((400 + index * 31 + t * 9) % 640), round(32 + index * 11 + math.sin(t * .5 + index) * 4)
            wing = round(math.sin(t * 6 + index) * 2)
            pygame.draw.lines(surface, (37, 70, 66), False, ((x - 3, y + wing), (x, y), (x + 3, y + wing)))


def draw(surface, source, key, spec, t):
    _sky(surface, source, key, spec, t)
    _water(surface, source, spec.get('water', ()), t)
    _sway(surface, source, key, spec.get('foliage', ()), t)
    _sway(surface, source, key, spec.get('cloth', ()), t, cloth=True)
    for region in spec.get('falls', ()):
        rect = _rect(region, surface.get_size())
        for index in range(7):
            x = rect.x + (index * 7) % max(1, rect.width)
            y = rect.y + (index * 11 + round(t * 45)) % max(1, rect.height)
            pygame.draw.line(surface, (124, 229, 245), (x, y), (x, min(rect.bottom, y + 4)))
    _lights(surface, spec, t)
    _leaves_and_grass(surface, spec, t)

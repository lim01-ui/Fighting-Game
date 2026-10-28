"""Register the 24-pose concept sheets without modifying source artwork.

Gutters are measured from alpha. Body measurements exclude long weapons,
wings, antennae and flames; each pose carries its own body/foot anchor.
"""
import json
from pathlib import Path
import pygame

ROOT = Path(__file__).resolve().parent.parent / 'assets/characters/style-v2'
FILES = {
    'rook': 'oni-chibi.png', 'vex': 'angelix-chibi.png', 'sable': 'phoenix-chibi.png',
    'chib': 'po-chibi.png', 'golem': 'golem-moss-chibi.png', 'sanya': 'sanya-mecha-chibi.png',
    'soldier': 'null-chibi.png', 'choom': 'glacier-chibi.png',
}
ROWS = (
    ('idle', 'idle_b', 'idle_c', 'idle_d'),
    ('step_a', 'step_b', 'step_c', 'step_d'),
    ('block', 'jump', 'crouch', 'hit'),
    ('light_start', 'light_contact', 'light_follow', 'light_recover'),
    ('heavy_start', 'heavy_contact', 'heavy_follow', 'heavy_recover'),
    ('special_start', 'special_contact', 'special_follow', 'knockdown'),
)
# Head/hat-to-foot standing height, as a fraction of the first idle's bounds.
# Tall projections remain additional silhouette instead of shrinking the torso.
BODY_RATIOS = {'rook': .94, 'vex': 1.0, 'sable': 1.0, 'chib': 1.0,
               'golem': 1.0, 'sanya': 1.0, 'soldier': 1.0, 'choom': 1.0}
BODY_CENTERS = {key: .5 for key in FILES}
PLANTED_IDLES = {'rook', 'soldier', 'sanya'}


def planted_foot_anchor(image, cell):
    """Find the two boot soles, excluding detached blade/chain effects.

    Atlas column centres are layout coordinates, not character origins. The
    idle drawings can drift tens of source pixels inside their nominal cells.
    """
    frame = image.subsurface(cell)
    bounds = frame.get_bounding_rect(min_alpha=200)
    band = pygame.Rect(bounds.x, max(bounds.y, bounds.bottom - 8), bounds.width,
                       min(8, bounds.height))
    mask = pygame.mask.from_surface(frame.subsurface(band), threshold=200)
    soles = sorted(mask.get_bounding_rects(), key=lambda rect: rect.width * rect.height, reverse=True)[:2]
    if len(soles) < 2:
        raise ValueError(f'Expected two planted feet in idle cell {cell}')
    feet = soles[0].union(soles[1])
    return [cell.x + band.x + feet.centerx, cell.y + bounds.bottom]


def cuts(counts, parts):
    result = [0]
    length = len(counts)
    for part in range(1, parts):
        ideal = length * part / parts
        radius = round(length / parts * .22)
        candidates = range(max(result[-1] + 1, round(ideal) - radius),
                           min(length, round(ideal) + radius + 1))
        result.append(min(candidates, key=lambda n: (int(counts[n]), abs(n - ideal))))
    return result + [length]


def register(key, filename):
    image = pygame.image.load(str(ROOT / filename))
    alpha = pygame.surfarray.array_alpha(image) >= 80
    y_cuts = cuts(alpha.sum(axis=0), 6)
    poses, anchors, bounds = {}, {}, {}
    for row, names in enumerate(ROWS):
        top, bottom = y_cuts[row:row + 2]
        x_cuts = cuts(alpha[:, top:bottom].sum(axis=1), 4)
        for column, name in enumerate(names):
            left, right = x_cuts[column:column + 2]
            rect = pygame.Rect(left, top, right - left, bottom - top)
            box = image.subsurface(rect).get_bounding_rect(min_alpha=80)
            if box.width < 20 or box.height < 20:
                raise ValueError(f'Empty pose: {key}/{name}')
            box.move_ip(left, top)
            poses[name] = list(rect)
            bounds[name] = list(box)
            # Explicit per-pose metadata can be adjusted after visual review.
            center_x = left + rect.width * BODY_CENTERS[key]
            anchors[name] = [round(center_x), box.bottom]
            if key in PLANTED_IDLES and row == 0:
                anchors[name] = planted_foot_anchor(image, rect)
    body_height = round(bounds['idle'][3] * BODY_RATIOS[key])
    animations = {
        'walk': list(ROWS[1]), 'run': list(ROWS[1]),
        'light': list(ROWS[3]), 'heavy': list(ROWS[4]),
        'special': list(ROWS[5][:3]) + ['idle'],
    }
    manifest = {
        'image': filename, 'body_height': body_height, 'pixel_height': 72,
        'phase_animation': True, 'dedicated_knockdown': True,
        'source_facing': 1, 'proportion_reference': 'renegade' if key in ('golem', 'choom') else 'raguel',
        'poses': poses, 'anchors': anchors, 'animations': animations,
        'idle_animation': {'image': filename, 'body_height': body_height,
                           'frames': [bounds[n] for n in ROWS[0]],
                           'sequence': list(ROWS[0])},
    }
    if key in PLANTED_IDLES:
        manifest['idle_animation'].update(anchor_mode='feet', frame_ms=240)
    (ROOT / f'{key}.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(key, image.get_size(), 'rows:', y_cuts, 'body:', body_height,
          'idle:', bounds['idle'])


if __name__ == '__main__':
    for key, filename in FILES.items():
        register(key, filename)

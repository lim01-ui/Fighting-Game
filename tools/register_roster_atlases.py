"""Register the 4x4 roster sheets, selecting gutters from their alpha channels.

Run from the project root after copying the generated PNGs into style-v2.
Only JSON metadata is written; source artwork is preserved verbatim.
"""

import json
from pathlib import Path

import numpy as np
import pygame


ROOT = Path(__file__).resolve().parent.parent / "assets" / "characters" / "style-v2"
FILES = {
    **{name: f"{name}-chibi.png" for name in ("sable", "nova", "jinx", "kestrel", "bramble", "iron")},
    "sanya": "sanya-slime.png", "choom": "choom-robot.png",
    "renegade": "renegade-treeman.png", "chib": "chib-panda.png",
}
ROWS = (
    ("idle", "idle_inhale", "idle_peak", "idle_exhale"),
    ("step_left", "step_right", "block", "jump"),
    ("crouch", "light_start", "light", "heavy_start"),
    ("heavy", "special", "hit", "knockdown"),
)


def cuts(counts):
    """Prefer empty pixel gutters nearest each nominal quarter boundary."""
    length = len(counts)
    result = [0]
    for quarter in (1, 2, 3):
        ideal = length * quarter / 4
        radius = round(length * 0.07)
        candidates = range(max(result[-1] + 1, round(ideal) - radius),
                           min(length, round(ideal) + radius + 1))
        cut = min(candidates, key=lambda n: (int(counts[n]), abs(n - ideal)))
        result.append(cut)
    return result + [length]


def register(key, filename):
    path = ROOT / filename
    image = pygame.image.load(str(path))
    alpha = pygame.surfarray.array_alpha(image) >= 16
    y_cuts = cuts(alpha.sum(axis=0))
    rectangles = {}
    for row, names in enumerate(ROWS):
        top, bottom = y_cuts[row:row + 2]
        x_cuts = cuts(alpha[:, top:bottom].sum(axis=1))
        for column, name in enumerate(names):
            left, right = x_cuts[column:column + 2]
            rectangles[name] = [left, top, right - left, bottom - top]
    idle_rects = []
    for name in ROWS[0]:
        rect = pygame.Rect(rectangles[name])
        bounds = image.subsurface(rect).get_bounding_rect(min_alpha=16)
        if not bounds.width:
            raise ValueError(f"Empty idle frame: {key}/{name}")
        bounds.move_ip(rect.x, rect.y)
        idle_rects.append(list(bounds))
    poses = {name: rect for name, rect in rectangles.items()
             if name not in ("idle_inhale", "idle_peak", "idle_exhale")}
    data = {
        "image": filename, "body_height": idle_rects[0][3], "pixel_height": 72,
        "poses": poses, "dedicated_knockdown": True,
        "animations": {"walk": ["step_left", "step_right"],
                       "run": ["step_left", "step_right"],
                       "light": ["light_start", "light"],
                       "heavy": ["heavy_start", "heavy"]},
        "idle_animation": {"image": filename, "body_height": idle_rects[0][3], "frames": idle_rects},
    }
    (ROOT / f"{key}.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(key, "registered", image.get_size(), "rows", y_cuts)


if __name__ == "__main__":
    for key, filename in FILES.items():
        if (ROOT / filename).exists():
            register(key, filename)

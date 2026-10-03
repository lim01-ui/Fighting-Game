"""Loader and animation selection for the optional CC0 pixel-art fighter."""

from pathlib import Path

import pygame


SHEET_PATH = (
    Path(__file__).resolve().parent.parent
    / "assets"
    / "characters"
    / "saikyo"
    / "character2_v4_0.gif"
)
FRAME_STEP = 24
FRAME_WIDTH = 16
FRAME_HEIGHT = 24

_sheet = None
_background = None
_frames = {}


def _load_sheet():
    global _sheet, _background
    if _sheet is None:
        _sheet = pygame.image.load(str(SHEET_PATH)).convert()
        _background = _sheet.get_at((230, 230))[:3]
    return _sheet


def get_frame(row, column):
    """Return a cropped frame from the source sheet, trimming its key color."""
    key = (row, column)
    if key not in _frames:
        sheet = _load_sheet()
        source_y = row * FRAME_STEP + 3
        frame = sheet.subsurface((
            column * FRAME_STEP,
            source_y,
            FRAME_WIDTH,
            FRAME_HEIGHT - 3,
        )).copy()
        frame.set_colorkey(_background)
        if row == 0:
            for y in range(frame.get_height()):
                for x in range(frame.get_width()):
                    if frame.get_at((x, y))[:3] == (0, 127, 135):
                        frame.set_at((x, y), _background)

        opaque = [
            (x, y)
            for y in range(frame.get_height())
            for x in range(frame.get_width())
            if frame.get_at((x, y))[:3] != _background
        ]
        if opaque:
            left = min(point[0] for point in opaque)
            top = min(point[1] for point in opaque)
            right = max(point[0] for point in opaque) + 1
            bottom = max(point[1] for point in opaque) + 1
            frame = frame.subsurface(
                pygame.Rect(left, top, right - left, bottom - top)
            ).copy()
            frame.set_colorkey(_background)
        _frames[key] = frame
    return _frames[key]


def preview_frame():
    """Static idle pose for character select and the VS screen."""
    frames = ((0, 0), (0, 2), (0, 4), (0, 2))
    return get_frame(*frames[0])


def frame_for_player(player):
    """Choose a source pose that matches the fighter's current combat state."""
    from characters.player import (
        S_ATTACK,
        S_BLOCKSTUN,
        S_HITSTUN,
        S_KNOCKDOWN,
    )

    if player.state == S_KNOCKDOWN:
        return pygame.transform.rotate(get_frame(2, 1), 90)
    if player.state == S_HITSTUN:
        return get_frame(2, 1)
    if player.state == S_BLOCKSTUN or player.is_crouching:
        return get_frame(1, 0)
    if player.state == S_ATTACK and player.current_attack is not None:
        attack_name = player.current_attack.data.name
        poses = {
            "light": (1, 4),
            "heavy": (3, 4),
            "crouch_light": (1, 4),
            "crouch_heavy": (3, 4),
            "air_light": (1, 4),
            "air_heavy": (3, 4),
            "special": (2, 2),
        }
        row, column = poses.get(attack_name, (1, 4))
        frame = get_frame(row, column)
        progress = player.current_attack.frame / max(
            1, player.current_attack.total - 1
        )
        active = player.current_attack.in_active
        if attack_name.startswith("crouch_"):
            frame = pygame.transform.scale(
                frame,
                (max(1, int(frame.get_width() * 1.12)),
                 max(1, int(frame.get_height() * 0.82))),
            )
            frame = pygame.transform.rotate(
                frame, player.facing * (8 + (14 if active else 6 * progress))
            )
        elif attack_name.startswith("air_"):
            frame = pygame.transform.scale(
                frame,
                (max(1, int(frame.get_width() * 1.12)),
                 max(1, int(frame.get_height() * 0.92))),
            )
            frame = pygame.transform.rotate(
                frame, -player.facing * (18 + (16 if active else 8 * progress))
            )
        return frame
    if not player.on_ground:
        return get_frame(2, 2)
    if player.state == "WALK":
        frames = ((0, 0), (0, 2), (0, 4), (0, 5))
        return get_frame(*frames[int(player.walk_phase) % len(frames)])
    return get_frame(0, 0)


def blit_fit(surface, image, rect):
    """Scale pixel art with nearest-neighbor filtering and center it in a box."""
    if image is None or image.get_width() <= 0 or image.get_height() <= 0:
        return
    scale = min(rect.width / image.get_width(), rect.height / image.get_height())
    size = (
        max(1, int(image.get_width() * scale)),
        max(1, int(image.get_height() * scale)),
    )
    scaled = pygame.transform.scale(image, size)
    surface.blit(scaled, scaled.get_rect(center=rect.center))

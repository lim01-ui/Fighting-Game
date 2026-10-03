"""Animation loading for the imported CC0 character sprite sets."""

from pathlib import Path

import pygame


ASSET_ROOT = Path(__file__).resolve().parent.parent / "assets" / "characters"
_SPECS = {
    "renegade": {
        "folder": "renegade",
        "height": 32,
        "directional": False,
        "animations": {
            "idle": (("Renegade_Idle_1_strip4.png", 16),),
            "walk": (("Renegade_Walk_1_strip4.png", 16),),
            "run": (("Renegade_Run_1_strip4.png", 16),),
            "block": (("Renegade_Daze_strip4.png", 16),),
            "light": (("Renegade_Punch_1.png", 24), ("Renegade_Punch_2.png", 24)),
            "heavy": (("Renegade_Kick_1.png", 24), ("Renegade_Kick_2.png", 24)),
            "special": (("Renegade_Head_Butt_strip2.png", 24),),
            "hit": (("Renegade_Hurt.png", 16),),
            "knockdown": (("Renegade_Knock_Out.png", 24),),
            "jump": (("Renegade_Kick_2.png", 24),),
        },
    },
    "soldier": {
        "folder": "soldier",
        "height": 24,
        "directional": True,
        "animations": {
            "idle": (("SMS_Soldier_IDLE_{direction}_strip4.png", 16),),
            "walk": (("SMS_Soldier_WALK_{direction}_strip4.png", 16),),
            "run": (("SMS_Soldier_RUN_{direction}_strip4.png", 16),),
            "block": (("SMS_Soldier_PUSHPULL_{direction}_strip4.png", 16),),
            "light": (("SMS_Soldier_ATTACKPUNCH_{direction}.png", 16),),
            "heavy": (("SMS_Soldier_ATTACKKICK_{direction}.png", 16),),
            "special": (("SMS_Soldier_ATTACKKICK_{direction}.png", 16),),
            "hit": (("SMS_Soldier_HITHURT_{direction}.png", 16),),
            "knockdown": (("SMS_Soldier_HITHURT_{direction}.png", 16),),
            "jump": (("SMS_Soldier_JUMP_{direction}.png", 16),),
        },
    },
}
_sheets = {}
_frames = {}


def _load_frame(asset, animation, frame_index, facing):
    spec = _SPECS[asset]
    animation_specs = spec["animations"][animation]
    direction = "EAST" if facing >= 0 else "WEST"
    spec_index = min(frame_index // 3, len(animation_specs) - 1)
    filename, frame_width = animation_specs[spec_index]
    filename = filename.format(direction=direction)
    sheet_key = (asset, filename)
    if sheet_key not in _sheets:
        path = ASSET_ROOT / spec["folder"] / filename
        _sheets[sheet_key] = pygame.image.load(str(path)).convert_alpha()
    sheet = _sheets[sheet_key]
    frame_count = max(1, sheet.get_width() // frame_width)
    if len(animation_specs) > 1:
        column = 0
    else:
        column = frame_index % frame_count
    key = (asset, filename, column, facing)
    if key in _frames:
        return _frames[key]
    frame = sheet.subsurface(
        (column * frame_width, 0, frame_width, spec["height"])
    ).copy()
    if not spec["directional"] and facing < 0:
        frame = pygame.transform.flip(frame, True, False)
    _frames[key] = frame
    return frame


def frame_for_player(asset, player):
    """Return the sprite pose that best matches the player's current state."""
    from characters.player import S_ATTACK, S_BLOCKSTUN, S_HITSTUN, S_KNOCKDOWN

    if player.state == S_KNOCKDOWN:
        animation = "knockdown"
        frame_index = 0
    elif player.state == S_HITSTUN:
        animation = "hit"
        frame_index = 0
    elif player.state == S_BLOCKSTUN:
        animation = "block"
        frame_index = pygame.time.get_ticks() // 130
    elif player.state == S_ATTACK and player.current_attack is not None:
        attack_name = player.current_attack.data.name
        animation = (
            "light" if attack_name.endswith("light")
            else "heavy" if attack_name.endswith("heavy")
            else "special"
        )
        frame_index = player.current_attack.frame // 3
    elif not player.on_ground:
        animation = "jump"
        frame_index = 0
    elif player.state == "WALK":
        animation = "walk"
        frame_index = pygame.time.get_ticks() // 110
    else:
        animation = "idle"
        frame_index = pygame.time.get_ticks() // 180

    frame = _load_frame(asset, animation, frame_index, player.facing)
    if player.state == S_ATTACK and player.current_attack is not None:
        attack_name = player.current_attack.data.name
        progress = player.current_attack.frame / max(
            1, player.current_attack.total - 1
        )
        active = player.current_attack.in_active
        if attack_name.startswith("crouch_"):
            width = max(1, int(frame.get_width() * 1.12))
            height = max(1, int(frame.get_height() * 0.82))
            frame = pygame.transform.scale(frame, (width, height))
            angle = player.facing * (8 + (14 if active else 6 * progress))
            frame = pygame.transform.rotate(frame, angle)
        elif attack_name.startswith("air_"):
            width = max(1, int(frame.get_width() * 1.12))
            height = max(1, int(frame.get_height() * 0.92))
            frame = pygame.transform.scale(frame, (width, height))
            angle = -player.facing * (18 + (16 if active else 8 * progress))
            frame = pygame.transform.rotate(frame, angle)
    return frame


def preview_frame(asset, facing=1):
    """Return an animated idle pose for character-selection previews."""
    return _load_frame(
        asset, "idle", pygame.time.get_ticks() // 180, facing
    )


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

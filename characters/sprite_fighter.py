"""Animation loading for imported and generated fighter sprite sets."""

import json
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
    "chib": {
        "folder": "Chib",
        "height": 42,
        "directional": False,
        "animations": {
            "idle": (("Chib_Idle.png", 42),),
            "walk": (("Chib_Walk.png", 42),),
            "run": (("Chib_Run.png", 42),),
            "block": (("Chib_WalkAttack_block.png", 42),),
            "light": (("Chib_Attack_light.png", 42),),
            "heavy": (("Chib_Attack_heavy.png", 42),),
            "special": (("Chib_SquatAttack.png", 42),),
            "hit": (("Chib_Hurt.png", 42),),
            "knockdown": (("Chib_Death.png", 42),),
            "jump": (("Chib_Jump.png", 42),),
        },
    },
    "minamoto": {
        "folder": "Minamoto",
        "height": 128,
        "directional": False,
        "animations": {
            "idle": (("minamoto_Idle.png", 128),),
            "walk": (("minamoto_Walk.png", 128),),
            "run": (("minamoto_Run.png", 128),),
            "block": (("minamoto_Idle.png", 128),),
            "light": (("minamoto_light_attack.png", 128),),
            "heavy": (("minamoto_heavy_attack.png", 128),),
            "special": (("minamoto_Special_shooting.png", 128),),
            "hit": (("minamoto_Hurt.png", 128),),
            "knockdown": (("minamoto_Dead.png", 128),),
            "jump": (("minamoto_Jump.png", 128),),
        },
    },
    "ash": {
        "folder": "Ash",
        "height": 128,
        "directional": False,
        "animations": {
            "idle": (("Ash_Idle.png", 128),),
            "walk": (("Ash_Run.png", 128),),
            "run": (("Ash_Run.png", 128),),
            "block": (("Ash_Shield.png", 128),),
            "light": (("Ash_Attack_light.png", 128),),
            "heavy": (("Ash_Attack_heavy.png", 128),),
            "special": (("Ash_Special.png", 128),),
            "hit": (("Ash_Hurt.png", 128),),
            "knockdown": (("Ash_Dead.png", 128),),
            "jump": (("Ash_Jump.png", 128),),
        },
    },
}
_sheets = {}
_frames = {}
_manifests = {}
GENERATED_ASSETS = ("rook", "vex", "golem")


def is_generated_asset(asset):
    return asset in GENERATED_ASSETS


def _manifest(asset):
    if asset not in _manifests:
        path = ASSET_ROOT / asset / "fighter-v1.json"
        _manifests[asset] = json.loads(path.read_text(encoding="utf-8"))
    return _manifests[asset]


def body_height(asset):
    """Use one scale for a generated fighter's body, weapons, and effects."""
    return _manifest(asset)["body_height"] if is_generated_asset(asset) else None


def _generated_frame(asset, animation, facing):
    manifest = _manifest(asset)
    pose = manifest["poses"].get(animation, manifest["poses"]["idle"])
    key = (asset, animation, facing)
    if key not in _frames:
        if asset not in _sheets:
            _sheets[asset] = pygame.image.load(
                str(ASSET_ROOT / asset / manifest["image"])
            ).convert_alpha()
        frame = _sheets[asset].subsurface(pygame.Rect(pose)).copy()
        # Remove atlas padding without rescaling the character between poses.
        bounds = frame.get_bounding_rect(min_alpha=16)
        if not bounds.width or not bounds.height:
            raise ValueError(f"Empty sprite pose: {asset}/{animation}")
        frame = frame.subsurface(bounds).copy()
        if facing < 0:
            frame = pygame.transform.flip(frame, True, False)
        if animation == "knockdown":
            frame = pygame.transform.rotate(frame, 80 * facing)
        _frames[key] = frame
    return _frames[key]


def _load_frame(asset, animation, frame_index, facing):
    if is_generated_asset(asset):
        return _generated_frame(asset, animation, facing)
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
    from characters.player import S_ATTACK, S_BLOCKSTUN, S_GUARD, S_HITSTUN, S_KNOCKDOWN

    if player.state == S_KNOCKDOWN:
        animation = "knockdown"
        frame_index = 0
    elif player.state == S_HITSTUN:
        animation = "hit"
        frame_index = 0
    elif player.state in (S_BLOCKSTUN, S_GUARD):
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
        # Progress through jump frames based on vertical velocity trajectory:
        # From launch (high negative vel_y), to peak (vel_y ~ 0), to falling (positive vel_y)
        spec = _SPECS.get(asset, {})
        anim_specs = spec.get("animations", {}).get("jump", (("", 1),))
        sheet_w = anim_specs[0][1]
        # Map vel_y roughly from -21 (launch) to +21 (landing) into [0.0, 1.0]
        jump_p = min(1.0, max(0.0, (player.vel_y + 20.0) / 40.0))
        # Total frames in the jump sheet
        filename = anim_specs[0][0]
        sheet_key = (asset, filename)
        if sheet_key in _sheets:
            total_frames = max(1, _sheets[sheet_key].get_width() // sheet_w)
        else:
            total_frames = 8
        frame_index = min(int(jump_p * total_frames), total_frames - 1)
    elif player.state == "WALK":
        animation = "walk"
        frame_index = pygame.time.get_ticks() // 110
    else:
        animation = "idle"
        frame_index = pygame.time.get_ticks() // 180

    frame = _load_frame(asset, animation, frame_index, player.facing)
    if player.is_crouching and player.state != S_ATTACK:
        frame = pygame.transform.scale(
            frame, (frame.get_width(), max(1, int(frame.get_height() * player.crouch_ratio)))
        )
    if player.state == S_ATTACK and player.current_attack is not None:
        if asset in ("soldier", "renegade"):
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

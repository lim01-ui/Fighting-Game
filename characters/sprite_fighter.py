"""Animation loading for imported and generated fighter sprite sets."""

import json
from pathlib import Path

import pygame


ASSET_ROOT = Path(__file__).resolve().parent.parent / "assets" / "characters"
_SPECS = {
    "raguel": {
        "folder": "Battle_maid",
        "height": 128,
        "body_height": 56,
        "crop": (96, 24, 192, 80),
        "foot_padding_ratio": 0.1,
        "trim_preview": True,
        "directional": False,
        "animations": {
            action: ((filename, 384),)
            for action, filename in {
                "idle": "idle.png", "walk": "running.png", "run": "running.png",
                "block": "idle.png", "jump": "idle.png", "hit": "idle.png",
                "knockdown": "idle.png", "light": "attack_1.png",
                "heavy": "attack_1.png", "special": "attack_1.png",
            }.items()
        },
    },
    "choom": {
        "folder": "Choom",
        "height": 42,
        "directional": False,
        "animations": {
            "idle": (("Idle.png", 42),),
            "walk": (("Walk.png", 42),),
            "run": (("Run.png", 42),),
            "block": (("Idle.png", 42),),
            "light": (("Attack1.png", 42),),
            "heavy": (("Attack2.png", 42),),
            "special": (("RunAttack2.png", 42),),
            "crouch_light": (("SquatAttack.png", 42),),
            "crouch_heavy": (("SquatAttack.png", 42),),
            "air_light": (("JumpAttack.png", 42),),
            "air_heavy": (("FallAttack.png", 42),),
            "hit": (("Hurt.png", 42),),
            "knockdown": (("Death.png", 42),),
            "jump": (("Jump.png", 42),),
        },
    },
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
# Sanya and Choom use the same 42px strip layout and animation filenames.
_SPECS["sanya"] = {**_SPECS["choom"], "folder": "Sanya"}

# These packs share 128px cells, with transparent padding above the body.
for _asset, _folder, _body_height, _heavy, _special in (
    ("swordsman", "Swordsman", 73, "Attack_2.png", "Attack_3.png"),
    ("wizard", "Wizard", 76, "Attack_2.png", "Attack_3.png"),
    ("knight", "Knight", 68, "Attack_2.png", "Attack_4.png"),
    ("musketeer", "Musketeer", 72, "Attack_2.png", "Attack_4.png"),
    ("archer", "Archer", 74, "Shot_1.png", "Shot_2.png"),
    ("enchantress", "Enchantress", 70, "Attack_2.png", "Attack_4.png"),
):
    _SPECS[_asset] = {
        "folder": _folder, "height": 128, "body_height": _body_height,
        "directional": False, "trim_preview": True,
        "animations": {
            action: ((filename, 128),)
            for action, filename in {
                "idle": "Idle.png", "walk": "Walk.png", "run": "Run.png",
                "block": "Idle.png", "light": "Attack_1.png", "heavy": _heavy,
                "special": _special, "hit": "Hurt.png", "knockdown": "Dead.png",
                "jump": "Jump.png",
            }.items()
        },
    }

_sheets = {}
_frames = {}
_manifests = {}
GENERATED_ASSETS = (
    "rook", "vex", "golem", "sanya", "choom", "saikyo", "renegade",
    "soldier", "chib", "minamoto", "raguel",
)


def is_generated_asset(asset):
    return asset in GENERATED_ASSETS


def _manifest(asset):
    if asset not in _manifests:
        path = ASSET_ROOT / "style-v2" / f"{asset}.json"
        _manifests[asset] = json.loads(path.read_text(encoding="utf-8"))
    return _manifests[asset]


def body_height(asset):
    """Use one scale for a generated fighter's body, weapons, and effects."""
    return (_manifest(asset)["pixel_height"] if is_generated_asset(asset)
            else _SPECS.get(asset, {}).get("body_height"))


def foot_padding_ratio(asset):
    """Transparent space below the foot baseline in an imported frame."""
    if is_generated_asset(asset):
        return 0.0
    return _SPECS.get(asset, {}).get("foot_padding_ratio", 0.0)


def _idle_frame(asset, frame_index, facing):
    manifest = _manifest(asset)
    spec = manifest["idle_animation"]
    index = frame_index % len(spec["frames"])
    key = (asset, "idle_cycle", index, facing)
    if key not in _frames:
        sheet_key = (asset, "idle_sheet")
        if sheet_key not in _sheets:
            _sheets[sheet_key] = pygame.image.load(
                str(ASSET_ROOT / "style-v2" / spec["image"])
            ).convert_alpha()
        scale = manifest["pixel_height"] / spec["body_height"]
        dimensions = [
            (max(1, round(rect[2] * scale)), max(1, round(rect[3] * scale)))
            for rect in spec["frames"]
        ]
        # One canvas/foot baseline for the whole loop. Per-frame tight fitting
        # would resize away the breathing and make previews jump between poses.
        canvas = pygame.Surface((max(w for w, h in dimensions),
                                 max(h for w, h in dimensions)), pygame.SRCALPHA)
        source = _sheets[sheet_key].subsurface(pygame.Rect(spec["frames"][index]))
        image = pygame.transform.scale(source, dimensions[index])
        canvas.blit(image, image.get_rect(midbottom=canvas.get_rect().midbottom))
        if facing < 0:
            canvas = pygame.transform.flip(canvas, True, False)
        _frames[key] = canvas
    return _frames[key]


def _generated_frame(asset, animation, frame_index, facing):
    manifest = _manifest(asset)
    if animation == "idle" and "idle_animation" in manifest:
        return _idle_frame(asset, frame_index, facing)
    sequence = manifest.get("animations", {}).get(animation, [animation])
    pose_name = sequence[frame_index % len(sequence)]
    pose = manifest["poses"].get(pose_name, manifest["poses"]["idle"])
    key = (asset, pose_name, facing)
    if key not in _frames:
        if asset not in _sheets:
            _sheets[asset] = pygame.image.load(
                str(ASSET_ROOT / "style-v2" / manifest["image"])
            ).convert_alpha()
        frame = _sheets[asset].subsurface(pygame.Rect(pose)).copy()
        # Remove atlas padding without rescaling the character between poses.
        bounds = frame.get_bounding_rect(min_alpha=16)
        if not bounds.width or not bounds.height:
            raise ValueError(f"Empty sprite pose: {asset}/{animation}")
        frame = frame.subsurface(bounds).copy()
        # Match the reference packs' native pixel density before display scaling.
        scale = manifest["pixel_height"] / manifest["body_height"]
        frame = pygame.transform.scale(frame, (
            max(1, round(frame.get_width() * scale)),
            max(1, round(frame.get_height() * scale)),
        ))
        if animation == "knockdown":
            frame = pygame.transform.rotate(frame, 80)
        if facing < 0:
            frame = pygame.transform.flip(frame, True, False)
        _frames[key] = frame
    return _frames[key]


def _load_frame(asset, animation, frame_index, facing):
    if is_generated_asset(asset):
        return _generated_frame(asset, animation, frame_index, facing)
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
    if spec.get("crop"):
        frame = frame.subsurface(spec["crop"]).copy()
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
        if not is_generated_asset(asset) and attack_name in _SPECS.get(asset, {}).get("animations", {}):
            animation = attack_name
        if is_generated_asset(asset):
            frame_index = 0 if player.current_attack.in_startup else 1
        else:
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

    if (is_generated_asset(asset) and player.is_crouching and player.on_ground
            and player.state not in (S_ATTACK, S_HITSTUN, S_KNOCKDOWN)):
        animation = "crouch"
    frame = _load_frame(asset, animation, frame_index, player.facing)
    if player.is_crouching and player.state != S_ATTACK:
        height = (round(body_height(asset) * player.crouch_ratio)
                  if animation == "crouch" else int(frame.get_height() * player.crouch_ratio))
        frame = pygame.transform.scale(
            frame, (frame.get_width(), max(1, height))
        )
    if player.state == S_ATTACK and player.current_attack is not None:
        if not is_generated_asset(asset) and asset in ("soldier", "renegade"):
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
    frame = _load_frame(
        asset, "idle", pygame.time.get_ticks() // 180, facing
    )
    if not is_generated_asset(asset) and _SPECS.get(asset, {}).get("trim_preview"):
        return frame.subsurface(frame.get_bounding_rect(min_alpha=16)).copy()
    return frame


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

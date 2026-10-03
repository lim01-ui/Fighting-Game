# characters/character_data.py
"""
The character roster.

Each entry is a plain dict describing one fighter. Add new fighters to
ROSTER and add their keys to ROSTER_ORDER.

Fields
------
key              : short id used in code (no spaces)
name             : display name shown on screen
archetype        : short label ("Balanced", "Speed", "Heavy", ...)

colors           : dict of RGB tuples
    body         : main body color
    accent       : accent color (used for highlights, attack flash)
    eye          : eye color

body             : visual proportions (all in pixels)
    width        : standing body width
    height       : standing body height
    crouch_ratio : crouch height as fraction of standing (0.5 - 0.65)

stats            : gameplay multipliers (1.0 = baseline)
    speed        : movement speed multiplier
    jump         : jump strength multiplier
    health       : max health multiplier
    damage       : damage dealt multiplier
    defense      : damage taken multiplier (lower = tankier)

attack_mods      : per-attack tweaks (multiplied on top of stats)
    reach        : horizontal reach multiplier
    startup      : startup time multiplier (lower = faster)
    cooldown     : recovery time multiplier
"""

ROSTER = {
    # ---------------------------------------------------------
    # 1. ROOK — the balanced starter. Good at everything, best at nothing.
    # ---------------------------------------------------------
    "rook": {
        "key": "rook",
        "name": "ROOK",
        "archetype": "Balanced",
        "special_behavior": {'type': 'slash', 'dash': 0, 'extra_hits': 0, 'projectiles': 0, 'teleport': False, 'spin': False, 'armor_frames': 0, 'stun_frames': 0, 'pierce': False},
        "weapon": "sword",
        "weapon_color": (220, 220, 240),
        "weapon_handle": (140, 150, 180),
        "colors": {
            "body":   (60, 120, 220),
            "accent": (255, 230, 120),
            "eye":    (255, 255, 255),
        },
        "body": {"width": 70, "height": 140, "crouch_ratio": 0.55},
        "stats": {
            "speed": 1.00, "jump": 1.00, "health": 1.00,
            "damage": 1.00, "defense": 1.00,
        },
        "attack_mods": {"reach": 1.00, "startup": 1.00, "cooldown": 1.00},
        "weapon_effect": {'knockback_mult': 1.0, 'reach_mult': 1.0, 'hitstun_mult': 1.0, 'startup_mult': 1.0, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 2. VEX — speed rushdown. Fast, weak, short reach.
    # ---------------------------------------------------------
    "vex": {
        "key": "vex",
        "name": "VEX",
        "archetype": "Speed",
        "special_behavior": {'type': 'dash_slash', 'dash': 90, 'extra_hits': 1, 'projectiles': 0, 'teleport': False, 'spin': False, 'armor_frames': 0, 'stun_frames': 0, 'pierce': False},
        "weapon": "daggers",
        "weapon_color": (230, 230, 240),
        "weapon_handle": (140, 140, 160),
        "colors": {
            "body":   (230, 80, 60),
            "accent": (255, 200, 90),
            "eye":    (255, 255, 255),
        },
        "body": {"width": 62, "height": 132, "crouch_ratio": 0.55},
        "stats": {
            "speed": 1.40, "jump": 1.15, "health": 0.85,
            "damage": 0.80, "defense": 1.10,
        },
        "attack_mods": {"reach": 0.90, "startup": 0.75, "cooldown": 0.85},
        "weapon_effect": {'knockback_mult': 0.8, 'reach_mult': 0.85, 'hitstun_mult': 0.9, 'startup_mult': 0.7, 'extra_hits': 1, 'projectile': None, 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 3. GOLEM — heavy grappler. Slow, tanky, huge damage, big reach.
    # ---------------------------------------------------------
    "golem": {
        "key": "golem",
        "name": "GOLEM",
        "archetype": "Heavy",
        "special_behavior": {'type': 'heavy_slam', 'dash': 0, 'extra_hits': 0, 'projectiles': 0, 'teleport': False, 'spin': False, 'armor_frames': 0, 'stun_frames': 0, 'pierce': False},
        "weapon": "hammer",
        "weapon_color": (140, 100, 60),
        "weapon_handle": (60, 40, 25),
        "colors": {
            "body":   (140, 100, 70),
            "accent": (220, 160, 80),
            "eye":    (255, 200, 100),
        },
        "body": {"width": 84, "height": 152, "crouch_ratio": 0.60},
        "stats": {
            "speed": 0.75, "jump": 0.85, "health": 1.25,
            "damage": 1.35, "defense": 0.80,
        },
        "attack_mods": {"reach": 1.10, "startup": 1.30, "cooldown": 1.25},
        "weapon_effect": {'knockback_mult': 2.0, 'reach_mult': 1.05, 'hitstun_mult': 1.2, 'startup_mult': 1.3, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 4. SABLE — zoner. Tall, long reach, medium everything else.
    # ---------------------------------------------------------
    "sable": {
        "key": "sable",
        "name": "SABLE",
        "archetype": "Zoner",
        "special_behavior": {'type': 'long_swipe', 'dash': 0, 'extra_hits': 0, 'projectiles': 0, 'teleport': False, 'spin': False, 'armor_frames': 0, 'stun_frames': 0, 'pierce': False},
        "weapon": "whip",
        "weapon_color": (200, 120, 200),
        "weapon_handle": (120, 50, 120),
        "colors": {
            "body":   (110, 70, 160),
            "accent": (220, 160, 255),
            "eye":    (255, 240, 255),
        },
        "body": {"width": 66, "height": 152, "crouch_ratio": 0.55},
        "stats": {
            "speed": 0.95, "jump": 1.00, "health": 0.95,
            "damage": 1.00, "defense": 1.05,
        },
        "attack_mods": {"reach": 1.25, "startup": 1.10, "cooldown": 1.10},
        "weapon_effect": {'knockback_mult': 1.0, 'reach_mult': 1.35, 'hitstun_mult': 1.0, 'startup_mult': 1.1, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 5. NOVA — technical. Fast, balanced, slightly low damage.
    # ---------------------------------------------------------
    "nova": {
        "key": "nova",
        "name": "NOVA",
        "archetype": "Technical",
        "special_behavior": {'type': 'projectile', 'dash': 0, 'extra_hits': 0, 'projectiles': 1, 'teleport': False, 'spin': False, 'armor_frames': 0, 'stun_frames': 0, 'pierce': False},
        "weapon": "orb",
        "weapon_color": (120, 240, 255),
        "weapon_handle": (60, 180, 200),
        "colors": {
            "body":   (80, 200, 220),
            "accent": (255, 255, 255),
            "eye":    (255, 255, 255),
        },
        "body": {"width": 68, "height": 140, "crouch_ratio": 0.55},
        "stats": {
            "speed": 1.20, "jump": 1.10, "health": 0.95,
            "damage": 0.90, "defense": 1.00,
        },
        "attack_mods": {"reach": 1.00, "startup": 0.85, "cooldown": 0.90},
        "weapon_effect": {'knockback_mult': 1.0, 'reach_mult': 1.0, 'hitstun_mult': 1.0, 'startup_mult': 0.9, 'extra_hits': 0, 'projectile': 'orb', 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 6. IRON — slow tank. Huge health, big damage, slow.
    # ---------------------------------------------------------
    "iron": {
        "key": "iron",
        "name": "IRON",
        "archetype": "Tank",
        "special_behavior": {'type': 'armored_bash', 'dash': 60, 'extra_hits': 0, 'projectiles': 0, 'teleport': False, 'spin': False, 'armor_frames': 48, 'stun_frames': 0, 'pierce': False},
        "weapon": "shield",
        "weapon_color": (110, 110, 130),
        "weapon_handle": (60, 60, 80),
        "colors": {
            "body":   (40, 100, 60),
            "accent": (180, 220, 140),
            "eye":    (220, 255, 200),
        },
        "body": {"width": 86, "height": 148, "crouch_ratio": 0.62},
        "stats": {
            "speed": 0.80, "jump": 0.80, "health": 1.35,
            "damage": 1.20, "defense": 0.75,
        },
        "attack_mods": {"reach": 1.00, "startup": 1.20, "cooldown": 1.15},
        "weapon_effect": {'knockback_mult': 1.1, 'reach_mult': 0.9, 'hitstun_mult': 1.1, 'startup_mult': 1.1, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.05},
    },

    # ---------------------------------------------------------
    # 7. JINX — trickster. Very fast, tricky, weak, short.
    # ---------------------------------------------------------
    "jinx": {
        "key": "jinx",
        "name": "JINX",
        "archetype": "Trickster",
        "special_behavior": {'type': 'fan_throw', 'dash': 0, 'extra_hits': 0, 'projectiles': 3, 'teleport': False, 'spin': False, 'armor_frames': 0, 'stun_frames': 0, 'pierce': False},
        "weapon": "knives",
        "weapon_color": (220, 220, 240),
        "weapon_handle": (140, 100, 180),
        "colors": {
            "body":   (180, 80, 200),
            "accent": (255, 240, 80),
            "eye":    (255, 255, 100),
        },
        "body": {"width": 60, "height": 128, "crouch_ratio": 0.55},
        "stats": {
            "speed": 1.45, "jump": 1.25, "health": 0.80,
            "damage": 0.75, "defense": 1.15,
        },
        "attack_mods": {"reach": 0.85, "startup": 0.70, "cooldown": 0.80},
        "weapon_effect": {'knockback_mult': 0.9, 'reach_mult': 0.9, 'hitstun_mult': 0.9, 'startup_mult': 0.75, 'extra_hits': 0, 'projectile': 'knife', 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 8. KESTREL — aerial. Great jump, medium everything else.
    # ---------------------------------------------------------
    "kestrel": {
        "key": "kestrel",
        "name": "KESTREL",
        "archetype": "Aerial",
        "special_behavior": {'type': 'pierce_thrust', 'dash': 30, 'extra_hits': 0, 'projectiles': 0, 'teleport': False, 'spin': False, 'armor_frames': 0, 'stun_frames': 0, 'pierce': True},
        "weapon": "spear",
        "weapon_color": (200, 180, 120),
        "weapon_handle": (90, 70, 40),
        "colors": {
            "body":   (200, 160, 90),
            "accent": (100, 200, 180),
            "eye":    (255, 255, 255),
        },
        "body": {"width": 64, "height": 148, "crouch_ratio": 0.55},
        "stats": {
            "speed": 1.15, "jump": 1.45, "health": 0.90,
            "damage": 1.00, "defense": 1.00,
        },
        "attack_mods": {"reach": 1.10, "startup": 1.00, "cooldown": 0.95},
        "weapon_effect": {'knockback_mult': 1.0, 'reach_mult': 1.4, 'hitstun_mult': 1.0, 'startup_mult': 1.0, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 9. BRAMBLE — defensive. Tanky, low speed, low damage, thick.
    # ---------------------------------------------------------
    "bramble": {
        "key": "bramble",
        "name": "BRAMBLE",
        "archetype": "Defensive",
        "special_behavior": {'type': 'multi_hit', 'dash': 0, 'extra_hits': 2, 'projectiles': 0, 'teleport': False, 'spin': False, 'armor_frames': 0, 'stun_frames': 0, 'pierce': False},
        "weapon": "club",
        "weapon_color": (110, 80, 50),
        "weapon_handle": (60, 40, 20),
        "colors": {
            "body":   (60, 90, 50),
            "accent": (200, 180, 120),
            "eye":    (255, 230, 180),
        },
        "body": {"width": 80, "height": 144, "crouch_ratio": 0.62},
        "stats": {
            "speed": 0.85, "jump": 0.90, "health": 1.25,
            "damage": 1.05, "defense": 0.75,
        },
        "attack_mods": {"reach": 0.95, "startup": 1.10, "cooldown": 1.05},
        "weapon_effect": {'knockback_mult': 1.5, 'reach_mult': 1.0, 'hitstun_mult': 1.3, 'startup_mult': 1.15, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 10. ASH — stance. Balanced but with a distinct quiet look.
    # ---------------------------------------------------------
    "ash": {
        "key": "ash",
        "name": "ASH",
        "archetype": "Stance",
        "special_behavior": {'type': 'teleport_slash', 'dash': 0, 'extra_hits': 0, 'projectiles': 0, 'teleport': True, 'spin': False, 'armor_frames': 0, 'stun_frames': 0, 'pierce': False},
        "weapon": "katana",
        "weapon_color": (230, 230, 240),
        "weapon_handle": (140, 140, 160),
        "colors": {
            "body":   (200, 200, 210),
            "accent": (140, 150, 200),
            "eye":    (60, 60, 90),
        },
        "body": {"width": 68, "height": 142, "crouch_ratio": 0.55},
        "stats": {
            "speed": 1.05, "jump": 1.00, "health": 1.00,
            "damage": 1.00, "defense": 1.00,
        },
        "attack_mods": {"reach": 1.05, "startup": 0.95, "cooldown": 1.00},
        "weapon_effect": {'knockback_mult': 1.0, 'reach_mult': 1.2, 'hitstun_mult': 1.0, 'startup_mult': 0.8, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 11. RYOKO — kick specialist. Long legs, longer reach, medium speed.
    # ---------------------------------------------------------
    "ryoko": {
        "key": "ryoko",
        "name": "RYOKO",
        "archetype": "Kicks",
        "special_behavior": {'type': 'spin_kick', 'dash': 0, 'extra_hits': 0, 'projectiles': 0, 'teleport': False, 'spin': True, 'armor_frames': 0, 'stun_frames': 0, 'pierce': False},
        "weapon": "gauntlets",
        "weapon_color": (230, 60, 90),
        "weapon_handle": (120, 20, 40),
        "colors": {
            "body":   (220, 50, 80),
            "accent": (255, 255, 255),
            "eye":    (255, 255, 255),
        },
        "body": {"width": 66, "height": 150, "crouch_ratio": 0.55},
        "stats": {
            "speed": 1.10, "jump": 1.10, "health": 0.95,
            "damage": 1.05, "defense": 1.00,
        },
        "attack_mods": {"reach": 1.25, "startup": 1.00, "cooldown": 1.00},
        "weapon_effect": {'knockback_mult': 1.0, 'reach_mult': 1.2, 'hitstun_mult': 1.4, 'startup_mult': 1.0, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 12. VOLT — fast special. Fast, medium damage, short reach.
    # ---------------------------------------------------------
    "volt": {
        "key": "volt",
        "name": "VOLT",
        "archetype": "Specialist",
        "special_behavior": {'type': 'stun_bolt', 'dash': 0, 'extra_hits': 0, 'projectiles': 1, 'teleport': False, 'spin': False, 'armor_frames': 0, 'stun_frames': 60, 'pierce': False},
        "weapon": "baton",
        "weapon_color": (240, 220, 60),
        "weapon_handle": (140, 120, 20),
        "colors": {
            "body":   (240, 210, 50),
            "accent": (60, 120, 230),
            "eye":    (255, 255, 255),
        },
        "body": {"width": 64, "height": 138, "crouch_ratio": 0.55},
        "stats": {
            "speed": 1.25, "jump": 1.05, "health": 0.90,
            "damage": 1.10, "defense": 1.05,
        },
        "attack_mods": {"reach": 0.95, "startup": 0.85, "cooldown": 0.90},
        "weapon_effect": {'knockback_mult': 1.0, 'reach_mult': 1.0, 'hitstun_mult': 1.6, 'startup_mult': 0.9, 'extra_hits': 0, 'projectile': 'spark', 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 13. SAIKYO — CC0 pixel-art karate fighter.
    # ---------------------------------------------------------
    "saikyo": {
        "key": "saikyo",
        "name": "SAIKYO",
        "archetype": "Pixel Brawler",
        "sprite_sheet": True,
        "special_behavior": {'type': 'slash', 'dash': 0, 'extra_hits': 0, 'projectiles': 0, 'teleport': False, 'spin': False, 'armor_frames': 0, 'stun_frames': 0, 'pierce': False},
        "weapon": "fists",
        "weapon_color": (245, 220, 170),
        "weapon_handle": (80, 60, 45),
        "colors": {
            "body":   (230, 230, 235),
            "accent": (235, 70, 70),
            "eye":    (255, 255, 255),
        },
        "body": {"width": 68, "height": 140, "crouch_ratio": 0.55},
        "stats": {
            "speed": 1.00, "jump": 1.00, "health": 1.00,
            "damage": 1.00, "defense": 1.00,
        },
        "attack_mods": {"reach": 1.00, "startup": 1.00, "cooldown": 1.00},
        "weapon_effect": {'knockback_mult': 1.0, 'reach_mult': 1.0, 'hitstun_mult': 1.0, 'startup_mult': 1.0, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 14. RENEGADE — imported CC0 brawler sprite.
    # ---------------------------------------------------------
    "renegade": {
        "key": "renegade",
        "name": "RENEGADE",
        "archetype": "Brawler",
        "sprite_asset": "renegade",
        "special_behavior": {'type': 'slash', 'dash': 0, 'extra_hits': 0, 'projectiles': 0, 'teleport': False, 'spin': False, 'armor_frames': 0, 'stun_frames': 0, 'pierce': False},
        "weapon": "fists",
        "weapon_color": (235, 70, 70),
        "weapon_handle": (80, 60, 45),
        "colors": {
            "body":   (230, 230, 235),
            "accent": (235, 70, 70),
            "eye":    (255, 255, 255),
        },
        "body": {"width": 68, "height": 140, "crouch_ratio": 0.55},
        "stats": {
            "speed": 1.05, "jump": 1.00, "health": 1.00,
            "damage": 1.00, "defense": 1.00,
        },
        "attack_mods": {"reach": 1.00, "startup": 1.00, "cooldown": 1.00},
        "weapon_effect": {'knockback_mult': 1.0, 'reach_mult': 1.0, 'hitstun_mult': 1.0, 'startup_mult': 1.0, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 15. SOLDIER — imported CC0 retro adventurer sprite.
    # ---------------------------------------------------------
    "soldier": {
        "key": "soldier",
        "name": "SOLDIER",
        "archetype": "Tactical",
        "sprite_asset": "soldier",
        "special_behavior": {'type': 'slash', 'dash': 0, 'extra_hits': 0, 'projectiles': 0, 'teleport': False, 'spin': False, 'armor_frames': 0, 'stun_frames': 0, 'pierce': False},
        "weapon": "fists",
        "weapon_color": (100, 190, 95),
        "weapon_handle": (65, 95, 55),
        "colors": {
            "body":   (90, 130, 65),
            "accent": (170, 205, 95),
            "eye":    (245, 245, 210),
        },
        "body": {"width": 64, "height": 140, "crouch_ratio": 0.55},
        "stats": {
            "speed": 0.95, "jump": 0.95, "health": 1.05,
            "damage": 1.05, "defense": 0.95,
        },
        "attack_mods": {"reach": 1.00, "startup": 1.00, "cooldown": 1.00},
        "weapon_effect": {'knockback_mult': 1.0, 'reach_mult': 1.0, 'hitstun_mult': 1.0, 'startup_mult': 1.0, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.0},
    },
}


# Ordered list of keys, used by the character-select screen for grid order.
ROSTER_ORDER = [
    # Original fighters are kept together.
    "rook", "vex", "golem", "sable",
    "nova", "iron", "jinx", "kestrel",
    "bramble", "ash", "ryoko", "volt",
    # Imported open-source fighters are kept together.
    "saikyo", "renegade", "soldier",
]

ULTIMATES = {
    "rook": {
        "name": "KING'S BREAKER", "effect": "double_slash",
        "damage_mult": 1.85, "reach_mult": 1.2, "extra_hits": 2, "dash": 36,
    },
    "vex": {
        "name": "PHANTOM RUSH", "effect": "afterimage",
        "damage_mult": 2.3, "reach_mult": 1.25, "extra_hits": 3, "dash": 150,
    },
    "golem": {
        "name": "FAULTLINE", "effect": "shockwave",
        "damage_mult": 2.15, "reach_mult": 1.8, "active": 10,
        "recovery": 42,
    },
    "sable": {
        "name": "MOONFALL LASH", "effect": "whip_arc",
        "damage_mult": 1.8, "reach_mult": 2.0, "active": 8,
    },
    "nova": {
        "name": "EVENT HORIZON", "effect": "orb",
        "damage_mult": 1.35, "projectile": "orb", "projectiles": 3,
        "projectile_spread": 42,
    },
    "iron": {
        "name": "BASTION CRASH", "effect": "aura",
        "damage_mult": 1.8, "reach_mult": 1.2, "dash": 52,
        "armor_frames": 66, "recovery": 38,
    },
    "jinx": {
        "name": "LUCKY SEVEN", "effect": "knife_fan",
        "damage_mult": 1.15, "projectile": "knife", "projectiles": 7,
        "projectile_spread": 84,
    },
    "kestrel": {
        "name": "SKYFALL LANCE", "effect": "spear_streak",
        "damage_mult": 1.9, "reach_mult": 1.65, "dash": 110,
        "active": 8,
    },
    "bramble": {
        "name": "THORNWALL", "effect": "leafburst",
        "damage_mult": 1.8, "reach_mult": 1.35, "extra_hits": 2,
        "armor_frames": 28,
    },
    "ash": {
        "name": "SILENT CROSSING", "effect": "afterimage",
        "damage_mult": 2.0, "reach_mult": 1.25, "extra_hits": 1,
        "teleport": True,
    },
    "ryoko": {
        "name": "SPIRAL COMET", "effect": "spin_kick",
        "damage_mult": 2.0, "reach_mult": 1.5, "extra_hits": 3,
        "dash": 44,
    },
    "volt": {
        "name": "STORM CAGE", "effect": "spark",
        "damage_mult": 1.6, "projectile": "spark", "projectiles": 5,
        "projectile_spread": 56, "stun_frames": 42,
    },
    "saikyo": {
        "name": "METEOR FIST", "effect": "double_slash",
        "damage_mult": 1.8, "reach_mult": 1.3, "extra_hits": 2,
        "dash": 70,
    },
    "renegade": {
        "name": "STREET VERDICT", "effect": "double_slash",
        "damage_mult": 1.75, "reach_mult": 1.35, "extra_hits": 2,
        "dash": 58,
    },
    "soldier": {
        "name": "SUPPRESSION BURST", "effect": "aura",
        "damage_mult": 1.8, "projectile": "spark", "projectiles": 6,
        "projectile_spread": 72, "stun_frames": 24,
    },
}


def get(key):
    """Return a roster entry by key. Raises KeyError if missing."""
    return ROSTER[key]


def all_characters():
    """Return the roster as an ordered list of dicts (for UI grids)."""
    return [ROSTER[k] for k in ROSTER_ORDER]


def ultimate_for(key):
    """Return the ultimate definition for a fighter."""
    return ULTIMATES[key]

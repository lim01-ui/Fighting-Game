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

render_scale     : standing sprite scale (1.0 = normal, heavy creatures up to 1.12)
body             : collision proportions (all in pixels)
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
    cooldown     : recovery time multiplier (separate from the five-second special timer)

Reach and startup are budgeted in attack_mods; weapon_effect keeps both of
those multipliers at 1.0 so weapon bonuses cannot silently double them.
Health and defense combine: effective durability is health / defense.
"""

ROSTER = {
    # ---------------------------------------------------------
    # 1. ONI — agile armored blades; short reach and a low jump.
    # ---------------------------------------------------------
    "rook": {
        "key": "rook",
        "species": "Robot",
        "sprite_asset": "rook",
        "name": "ONI",
        "archetype": "Twin Blades",
        "special_behavior": {'type': 'slash', 'dash': 0, 'extra_hits': 0, 'projectiles': 0, 'teleport': False, 'spin': False, 'armor_frames': 0, 'stun_frames': 0, 'pierce': False},
        "weapon": "daggers",
        "weapon_color": (150, 125, 255),
        "weapon_handle": (50, 40, 70),
        "colors": {
            "body":   (48, 40, 65),
            "accent": (155, 100, 255),
            "eye":    (255, 196, 70),
        },
        "body": {"width": 70, "height": 140, "crouch_ratio": 0.55},
        "stats": {
            "speed": 1.08, "jump": 0.95, "health": 1.02,
            "damage": 1.00, "defense": 0.98,
        },
        "attack_mods": {"reach": 0.94, "startup": 0.90, "cooldown": 0.95},
        "weapon_effect": {'knockback_mult': 1.0, 'reach_mult': 1.0, 'hitstun_mult': 1.0, 'startup_mult': 1.0, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 2. ANGELIX — mobile aerial caster; fragile, weak melee and slow recovery.
    # ---------------------------------------------------------
    "vex": {
        "key": "vex",
        "species": "Winged Mage",
        "hover_height": 24,
        "hover_amplitude": 6,
        "sprite_asset": "vex",
        "name": "ANGELIX",
        "archetype": "Aerial Mage",
        "special_behavior": {'type': 'projectile', 'dash': 0, 'extra_hits': 0, 'projectiles': 1, 'teleport': False, 'spin': False, 'armor_frames': 0, 'stun_frames': 0, 'pierce': False},
        "weapon": "staff",
        "weapon_color": (95, 235, 255),
        "weapon_handle": (65, 75, 100),
        "colors": {
            "body":   (45, 55, 85),
            "accent": (80, 225, 255),
            "eye":    (70, 210, 255),
        },
        "body": {"width": 62, "height": 132, "crouch_ratio": 0.55},
        "stats": {
            "speed": 1.10, "jump": 1.25, "health": 0.88,
            "damage": 0.88, "defense": 1.04,
        },
        "attack_mods": {"reach": 1.10, "startup": 1.04, "cooldown": 1.08},
        "weapon_effect": {'knockback_mult': 0.85, 'reach_mult': 1.0, 'hitstun_mult': 0.95, 'startup_mult': 1.0, 'extra_hits': 0, 'projectile': 'orb', 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 3. GOLEM — largest hammer tank; slow movement, low jump, long recovery.
    # ---------------------------------------------------------
    "golem": {
        "key": "golem",
        "species": "Moss Golem",
        "render_scale": 1.12,
        "sprite_asset": "golem",
        "name": "GOLEM",
        "archetype": "Heavy",
        "special_behavior": {'type': 'heavy_slam', 'dash': 0, 'extra_hits': 0, 'projectiles': 0, 'teleport': False, 'spin': False, 'armor_frames': 0, 'stun_frames': 0, 'pierce': False},
        "weapon": "hammer",
        "weapon_color": (120, 160, 110),
        "weapon_handle": (70, 65, 45),
        "colors": {
            "body":   (105, 120, 90),
            "accent": (65, 225, 255),
            "eye":    (120, 255, 85),
        },
        "body": {"width": 84, "height": 154, "crouch_ratio": 0.60},
        "stats": {
            "speed": 0.72, "jump": 0.78, "health": 1.24,
            "damage": 1.20, "defense": 0.92,
        },
        "attack_mods": {"reach": 1.10, "startup": 1.34, "cooldown": 1.28},
        "weapon_effect": {'knockback_mult': 1.35, 'reach_mult': 1.0, 'hitstun_mult': 1.10, 'startup_mult': 1.0, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 4. PHOENIX — long greatsword and strong jump; slow movement and swings.
    # ---------------------------------------------------------
    "sable": {
        "key": "sable",
        "species": "Valkyrie",
        "hover_height": 24,
        "hover_amplitude": 6,
        "sprite_asset": "sable",
        "name": "PHOENIX",
        "archetype": "Aerial Greatsword",
        "special_behavior": {'type': 'long_swipe', 'dash': 0, 'extra_hits': 0, 'projectiles': 0, 'teleport': False, 'spin': False, 'armor_frames': 0, 'stun_frames': 0, 'pierce': False},
        "weapon": "sword",
        "weapon_color": (255, 215, 60),
        "weapon_handle": (95, 65, 40),
        "colors": {
            "body":   (70, 50, 100),
            "accent": (255, 207, 55),
            "eye":    (230, 75, 65),
        },
        "body": {"width": 66, "height": 152, "crouch_ratio": 0.55},
        "stats": {
            "speed": 0.88, "jump": 1.18, "health": 0.96,
            "damage": 1.12, "defense": 1.00,
        },
        "attack_mods": {"reach": 1.22, "startup": 1.16, "cooldown": 1.16},
        "weapon_effect": {'knockback_mult': 1.15, 'reach_mult': 1.0, 'hitstun_mult': 1.0, 'startup_mult': 1.0, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 5. NOVA — quick orb caster; low health, low damage and short melee reach.
    # ---------------------------------------------------------
    "nova": {
        "key": "nova",
        "sprite_asset": "nova",
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
            "speed": 1.14, "jump": 1.10, "health": 0.92,
            "damage": 0.90, "defense": 1.02,
        },
        "attack_mods": {"reach": 0.96, "startup": 0.94, "cooldown": 0.98},
        "weapon_effect": {'knockback_mult': 1.0, 'reach_mult': 1.0, 'hitstun_mult': 1.0, 'startup_mult': 1.0, 'extra_hits': 0, 'projectile': 'orb', 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 6. IRON — shield defense and armor; short reach, weak damage, low mobility.
    # ---------------------------------------------------------
    "iron": {
        "key": "iron",
        "sprite_asset": "iron",
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
            "speed": 0.84, "jump": 0.84, "health": 1.16,
            "damage": 0.92, "defense": 0.90,
        },
        "attack_mods": {"reach": 0.92, "startup": 1.10, "cooldown": 1.12},
        "weapon_effect": {'knockback_mult': 1.05, 'reach_mult': 1.0, 'hitstun_mult': 1.05, 'startup_mult': 1.0, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.05},
    },

    # ---------------------------------------------------------
    # 7. JINX — agile knife trickster; short reach and fragile, light hits.
    # ---------------------------------------------------------
    "jinx": {
        "key": "jinx",
        "sprite_asset": "jinx",
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
            "speed": 1.27, "jump": 1.20, "health": 0.85,
            "damage": 0.84, "defense": 1.04,
        },
        "attack_mods": {"reach": 0.90, "startup": 0.84, "cooldown": 0.92},
        "weapon_effect": {'knockback_mult': 0.90, 'reach_mult': 1.0, 'hitstun_mult': 0.95, 'startup_mult': 1.0, 'extra_hits': 0, 'projectile': 'knife', 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 8. KESTREL — leaping spear specialist; fragile with committed recovery.
    # ---------------------------------------------------------
    "kestrel": {
        "key": "kestrel",
        "sprite_asset": "kestrel",
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
            "speed": 1.08, "jump": 1.28, "health": 0.92,
            "damage": 0.96, "defense": 1.02,
        },
        "attack_mods": {"reach": 1.18, "startup": 1.04, "cooldown": 1.06},
        "weapon_effect": {'knockback_mult': 1.0, 'reach_mult': 1.0, 'hitstun_mult': 1.0, 'startup_mult': 1.0, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 9. BRAMBLE — durable woodland defender; modest mobility and damage.
    # ---------------------------------------------------------
    "bramble": {
        "key": "bramble",
        "sprite_asset": "bramble",
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
            "speed": 0.94, "jump": 0.94, "health": 1.08,
            "damage": 0.88, "defense": 0.96,
        },
        "attack_mods": {"reach": 0.96, "startup": 1.08, "cooldown": 1.10},
        "weapon_effect": {'knockback_mult': 1.15, 'reach_mult': 1.0, 'hitstun_mult': 1.10, 'startup_mult': 1.0, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 10. RAGUEL — versatile katana duelist; modest health, no extreme stats.
    # ---------------------------------------------------------
    "raguel": {
        "key": "raguel",
        "name": "RAGUEL",
        "archetype": "Stance",
        "sprite_asset": "raguel",
        "sprite_scale": 1.0,
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
            "speed": 1.06, "jump": 1.04, "health": 0.97,
            "damage": 1.04, "defense": 1.00,
        },
        "attack_mods": {"reach": 1.05, "startup": 0.96, "cooldown": 1.00},
        "weapon_effect": {'knockback_mult': 1.0, 'reach_mult': 1.0, 'hitstun_mult': 1.0, 'startup_mult': 1.0, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 11. SANYA — fastest mecha, quickest swings; lowest health and light damage.
    # ---------------------------------------------------------
    "sanya": {
        "key": "sanya",
        "species": "Mecha",
        "sprite_asset": "sanya",
        "name": "SANYA",
        "archetype": "Speed Twinblade",
        "special_behavior": {'type': 'spin_slash', 'dash': 0, 'extra_hits': 0, 'projectiles': 0, 'teleport': False, 'spin': True, 'armor_frames': 0, 'stun_frames': 0, 'pierce': False},
        "weapon": "sword",
        "weapon_color": (135, 255, 205),
        "weapon_handle": (195, 170, 100),
        "colors": {
            "body":   (220, 230, 235),
            "accent": (120, 255, 205),
            "eye":    (120, 255, 205),
        },
        "body": {"width": 66, "height": 150, "crouch_ratio": 0.55},
        "stats": {
            "speed": 1.40, "jump": 1.18, "health": 0.78,
            "damage": 0.85, "defense": 1.06,
        },
        "attack_mods": {"reach": 1.02, "startup": 0.80, "cooldown": 0.88},
        "weapon_effect": {'knockback_mult': 0.85, 'reach_mult': 1.0, 'hitstun_mult': 0.95, 'startup_mult': 1.0, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 12. GLACIER — large ice boxer; strong close hits, slow and easy to zone.
    # ---------------------------------------------------------
    "choom": {
        "key": "choom",
        "species": "Ice Golem",
        "render_scale": 1.10,
        "sprite_asset": "choom",
        "name": "GLACIER",
        "archetype": "Ice Juggernaut",
        "special_behavior": {'type': 'heavy_slam', 'dash': 0, 'extra_hits': 0, 'projectiles': 0, 'teleport': False, 'spin': False, 'armor_frames': 0, 'stun_frames': 24, 'pierce': False},
        "weapon": "fists",
        "weapon_color": (120, 220, 255),
        "weapon_handle": (35, 65, 115),
        "colors": {
            "body":   (155, 215, 255),
            "accent": (95, 225, 255),
            "eye":    (185, 255, 255),
        },
        "body": {"width": 82, "height": 152, "crouch_ratio": 0.60},
        "stats": {
            "speed": 0.78, "jump": 0.80, "health": 1.20,
            "damage": 1.15, "defense": 0.94,
        },
        "attack_mods": {"reach": 0.88, "startup": 1.16, "cooldown": 1.20},
        "weapon_effect": {'knockback_mult': 1.20, 'reach_mult': 1.0, 'hitstun_mult': 1.10, 'startup_mult': 1.0, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 13. SAIKYO — mobile karate all-rounder; fists have short reach.
    # ---------------------------------------------------------
    "saikyo": {
        "key": "saikyo",
        "name": "SAIKYO",
        "archetype": "Pixel Brawler",
        "sprite_asset": "saikyo",
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
            "speed": 1.08, "jump": 1.10, "health": 1.00,
            "damage": 1.04, "defense": 1.02,
        },
        "attack_mods": {"reach": 0.90, "startup": 0.94, "cooldown": 0.94},
        "weapon_effect": {'knockback_mult': 1.0, 'reach_mult': 1.0, 'hitstun_mult': 1.0, 'startup_mult': 1.0, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 14. RENEGADE — broad treeman tank; sturdy bark, slow steps and swings.
    # ---------------------------------------------------------
    "renegade": {
        "key": "renegade",
        "species": "Treeman",
        "render_scale": 1.10,
        "name": "RENEGADE",
        "archetype": "Bark Guardian",
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
        "body": {"width": 82, "height": 152, "crouch_ratio": 0.60},
        "stats": {
            "speed": 0.80, "jump": 0.84, "health": 1.22,
            "damage": 1.08, "defense": 0.93,
        },
        "attack_mods": {"reach": 1.04, "startup": 1.20, "cooldown": 1.22},
        "weapon_effect": {'knockback_mult': 1.25, 'reach_mult': 1.0, 'hitstun_mult': 1.08, 'startup_mult': 1.0, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 15. NULL — heavy cleaver bruiser; highest damage, very committed swings.
    # ---------------------------------------------------------
    "soldier": {
        "key": "soldier",
        "species": "Ember Golem",
        "render_scale": 1.05,
        "name": "NULL",
        "archetype": "Cleaver and Chain",
        "sprite_asset": "soldier",
        "special_behavior": {'type': 'slash', 'dash': 0, 'extra_hits': 0, 'projectiles': 0, 'teleport': False, 'spin': False, 'armor_frames': 0, 'stun_frames': 0, 'pierce': False},
        "weapon": "axe",
        "weapon_color": (255, 140, 45),
        "weapon_handle": (75, 45, 35),
        "colors": {
            "body":   (70, 60, 65),
            "accent": (255, 130, 40),
            "eye":    (255, 190, 55),
        },
        "body": {"width": 76, "height": 146, "crouch_ratio": 0.58},
        "stats": {
            "speed": 0.83, "jump": 0.86, "health": 1.10,
            "damage": 1.22, "defense": 0.98,
        },
        "attack_mods": {"reach": 1.14, "startup": 1.26, "cooldown": 1.30},
        "weapon_effect": {'knockback_mult': 1.35, 'reach_mult': 1.0, 'hitstun_mult': 1.10, 'startup_mult': 1.0, 'extra_hits': 0, 'projectile': None, 'shield_reflect': 0.0},
    },

    # ---------------------------------------------------------
    # 16. PO — sturdy round panda duelist; average pace and reach.
    # ---------------------------------------------------------
    "chib": {
        "key": "chib",
        "species": "Panda",
        "name": "PO",
        "archetype": "Sword Master",
        "sprite_asset": "chib",
        "special_behavior": {
            'type': 'slash',
            'dash': 45,
            'extra_hits': 1,
            'projectiles': 0,
            'teleport': False,
            'spin': False,
            'armor_frames': 0,
            'stun_frames': 0,
            'pierce': False,
        },
        "weapon": "katana",
        "weapon_color": (150, 240, 210),
        "weapon_handle": (35, 65, 50),
        "colors": {
            "body":   (225, 220, 200),
            "accent": (95, 225, 165),
            "eye":    (100, 200, 95),
        },
        "body": {"width": 64, "height": 136, "crouch_ratio": 0.55},
        "stats": {
            "speed": 0.98, "jump": 1.04, "health": 1.08,
            "damage": 1.02, "defense": 0.98,
        },
        "attack_mods": {"reach": 1.00, "startup": 0.94, "cooldown": 1.02},
        "weapon_effect": {
            'knockback_mult': 0.95,
            'reach_mult': 1.0,
            'hitstun_mult': 1.0,
            'startup_mult': 1.0,
            'extra_hits': 1,
            'projectile': None,
            'shield_reflect': 0.0,
        },
    },

    # ---------------------------------------------------------
    # 17. MINAMOTO — bow and sword zoning; fragile and slower attack recovery.
    # ---------------------------------------------------------
    "minamoto": {
        "key": "minamoto",
        "name": "MINAMOTO",
        "archetype": "Archer",
        "sprite_asset": "minamoto",
        "special_behavior": {
            'type': 'projectile',
            'dash': 0,
            'extra_hits': 0,
            'projectiles': 1,
            'teleport': False,
            'spin': False,
            'armor_frames': 0,
            'stun_frames': 16,
            'pierce': False,
        },
        "weapon": "sword",
        "weapon_color": (173, 47, 69),
        "weapon_handle": (20, 24, 46),
        "colors": {
            "body":   (20, 24, 46),
            "accent": (173, 47, 69),
            "eye":    (245, 255, 232),
        },
        "body": {"width": 64, "height": 140, "crouch_ratio": 0.55},
        "stats": {
            "speed": 1.02, "jump": 1.03, "health": 0.90,
            "damage": 0.96, "defense": 1.02,
        },
        "attack_mods": {"reach": 1.06, "startup": 1.08, "cooldown": 1.10},
        "weapon_effect": {
            'knockback_mult': 1.0,
            'reach_mult': 1.0,
            'hitstun_mult': 1.0,
            'startup_mult': 1.0,
            'extra_hits': 0,
            'projectile': 'arrow',
            'shield_reflect': 0.0,
        },
    },
}


# Stable slot IDs also identify saved selections and LAN packets. Display names
# and artwork may change without invalidating those selections.
# Ordered list of keys, used by the character-select screen for grid order.
ROSTER_ORDER = [
    # Original fighters are kept together.
    "rook", "vex", "golem", "sable",
    "nova", "iron", "jinx", "kestrel",
    "bramble", "raguel", "sanya", "choom",
    # Imported open-source fighters are kept together.
    "saikyo", "renegade", "soldier", "chib", "minamoto",
]

ULTIMATES = {
    "rook": {
        "name": "HELLFIRE CROSS", "effect": "double_slash",
        "damage_mult": 1.85, "reach_mult": 1.2, "extra_hits": 2, "dash": 36,
    },
    "vex": {
        "name": "CELESTIAL ORBIT", "effect": "orb",
        "damage_mult": 2.0, "reach_mult": 1.25,
        "projectile": "orb", "projectiles": 3, "projectile_spread": 42,
    },
    "golem": {
        "name": "FAULTLINE", "effect": "shockwave",
        "damage_mult": 1.8, "reach_mult": 1.8, "active": 10,
        "recovery": 42,
    },
    "sable": {
        "name": "SOLAR REBIRTH", "effect": "double_slash",
        "damage_mult": 1.8, "reach_mult": 2.0, "active": 8,
    },
    "nova": {
        "name": "EVENT HORIZON", "effect": "orb",
        "damage_mult": 1.9, "projectile": "orb", "projectiles": 3,
        "projectile_spread": 42,
    },
    "iron": {
        "name": "BASTION CRASH", "effect": "aura",
        "damage_mult": 1.8, "reach_mult": 1.2, "dash": 52,
        "armor_frames": 66, "recovery": 38,
    },
    "jinx": {
        "name": "LUCKY SEVEN", "effect": "knife_fan",
        "damage_mult": 2.15, "projectile": "knife", "projectiles": 7,
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
    "raguel": {
        "name": "SILENT CROSSING", "effect": "afterimage",
        "damage_mult": 2.0, "reach_mult": 1.25, "extra_hits": 1,
        "teleport": True,
    },
    "sanya": {
        "name": "MINT CROSSING", "effect": "double_slash",
        "damage_mult": 2.0, "reach_mult": 1.5, "extra_hits": 3,
        "dash": 44,
    },
    "choom": {
        "name": "PERMAFROST", "effect": "shockwave",
        "damage_mult": 1.6, "reach_mult": 1.5, "stun_frames": 42,
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
        "name": "CINDER CHAINS", "effect": "whip_arc",
        "damage_mult": 1.8, "reach_mult": 1.7, "stun_frames": 24,
    },
    "chib": {
        "name": "JADE TYPHOON", "effect": "double_slash",
        "damage_mult": 1.85, "reach_mult": 1.4, "extra_hits": 3,
        "dash": 65,
    },
    "minamoto": {
        "name": "SHOT", "effect": "aura",
        "damage_mult": 1.95, "projectile": "arrow", "projectiles": 5,
        "projectile_spread": 48, "stun_frames": 30,
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

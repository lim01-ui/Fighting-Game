# effects/combat_behaviors.py
"""
Behavioral hooks for special moves.

Each character's special_behavior dict in character_data.py drives these.

A behavior runs on two events:
    on_start(player)  -- fires when the special attack begins (startup)
    on_active(player, defender, spawn_projectile) -- fires once when
        the hitbox becomes active

The Player and the fight scene coordinate through these functions.
"""


def on_start(player, ultimate=False):
    """Apply start-of-special effects: dash, teleport, super-armor."""
    if ultimate:
        from characters import character_data
        beh = character_data.ultimate_for(player.character["key"])
    else:
        beh = player.character.get("special_behavior", {})
    btype = beh.get("type", "slash")

    # Ultimate armor lets heavy moves complete without free interruption.
    if beh.get("armor_frames", 0) > 0:
        player.super_armor_frames = beh["armor_frames"]
    if beh.get("stun_frames", 0) > 0:
        player._stun_on_hit = beh["stun_frames"]

    # Dash forward (Vex, Iron, Kestrel)
    dash = beh.get("dash", 0)
    if dash > 0:
        player.rect.x += dash * player.facing

    # Teleport behind the opponent (Ash).
    if beh.get("teleport", False) and getattr(player, "_opponent_ref", None):
        opp = player._opponent_ref
        # Teleport to the other side of the opponent
        if player.rect.centerx < opp.rect.centerx:
            player.rect.centerx = opp.rect.right + 60
            player.facing = -1
        else:
            player.rect.centerx = opp.rect.left - 60
            player.facing = 1


def on_active(player, defender, spawn_projectile):
    """
    Apply the active-phase behavior of a special.
    Returns a list of extra hitboxes (or None) to add.
    """
    beh = player.character.get("special_behavior", {})
    btype = beh.get("type", "slash")

    extra_boxes = []

    if btype in ("projectile",):
        spawn_projectile()
        return []

    if btype == "fan_throw":
        # Three projectiles at different vertical angles
        for dy in (-60, 0, 60):
            spawn_projectile(offset_y=dy)
        return []

    if btype == "stun_bolt":
        spawn_projectile()
        # Also set a stun marker that the fight scene will read on hit
        player._stun_on_hit = beh.get("stun_frames", 0)
        return []

    if btype == "spin_kick":
        # Extra hitbox behind the player
        import pygame
        r = player.rect
        back_rect = pygame.Rect(
            r.left - player.current_attack.data.reach,
            r.centery - player.current_attack.data.height // 2,
            player.current_attack.data.reach,
            player.current_attack.data.height)
        return [back_rect]

    return []


def consume_stun_on_hit(attacker):
    """Called by the fight scene after a special connects."""
    stun = getattr(attacker, "_stun_on_hit", 0)
    if stun > 0:
        attacker._stun_on_hit = 0
        return stun
    return 0

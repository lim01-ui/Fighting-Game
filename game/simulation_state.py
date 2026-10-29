"""Copy rollback state without duplicating renderer resources.

The bundle must contain all mutable combat objects in one graph, so opponent
and projectile-owner references continue to point at the restored fighters.
Surfaces and fonts are visual caches: their contents never determine combat.
Character definitions, keymaps and attack blueprints are immutable for a match.
"""
from contextlib import contextmanager
import copy
import random

import pygame

from audio import sound_fx
from characters.player import Player
from ui.retro import PixelFont


def clone_state(bundle):
    """Clone mutable state, sharing only assets and immutable definitions."""
    memo = {}
    visited = set()
    atomic = (str, bytes, int, float, bool, type(None))

    def share_definition(value):
        identity = id(value)
        if identity in memo or isinstance(value, atomic):
            return
        memo[identity] = value
        if isinstance(value, dict):
            for child in value.values():
                share_definition(child)
        elif isinstance(value, (list, tuple)):
            for child in value:
                share_definition(child)
        elif hasattr(value, '__dict__'):
            for child in vars(value).values():
                share_definition(child)

    def visit(value):
        if isinstance(value, atomic):
            return
        identity = id(value)
        if identity in visited or identity in memo:
            return
        visited.add(identity)
        if isinstance(value, (pygame.Surface, pygame.font.Font, PixelFont)):
            memo[identity] = value
            return
        if isinstance(value, Player):
            for name in ('character', 'keymap', 'attacks'):
                share_definition(getattr(value, name))
        if isinstance(value, dict):
            for child in value.values():
                visit(child)
        elif isinstance(value, (list, tuple, set, frozenset)):
            for child in value:
                visit(child)
        elif hasattr(value, '__dict__'):
            for child in vars(value).values():
                visit(child)

    visit(bundle)
    return copy.deepcopy(bundle, memo)


@contextmanager
def simulation_tick(frame, replaying=False):
    """Reproduce frame-local randomness without changing the renderer's PRNG.

No wall clock, render count or machine-local random seed enters simulation.
Replayed ticks rebuild visuals but do not play duplicate audio.
"""
    previous = random.getstate()
    random.seed(0x46544754 ^ int(frame))
    try:
        with sound_fx.suppress(replaying):
            yield
    finally:
        random.setstate(previous)

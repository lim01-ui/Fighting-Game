"""Looping licensed background music for menus and fights."""

import os

import pygame

from audio import preferences

_MUSIC_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets",
    "music",
)
_TRACKS = {
    "intro": os.path.join(_MUSIC_DIR, "intro_title.mp3"),
    "fight": os.path.join(_MUSIC_DIR, "fight_loop.mp3"),
}
_current_track = None
_requested_volume = 0.3


def play(track, volume=0.3, fade_ms=500):
    """Switch to a looping track, fading between tracks when possible."""
    global _current_track, _requested_volume

    if track not in _TRACKS:
        raise ValueError(f"Unknown music track: {track}")

    path = _TRACKS[track]
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Music track is missing: {path}")

    if _current_track == track and pygame.mixer.music.get_busy():
        _requested_volume = volume
        refresh_volume()
        return

    if pygame.mixer.music.get_busy() and fade_ms > 0:
        pygame.mixer.music.fadeout(fade_ms)
        pygame.time.wait(fade_ms)

    pygame.mixer.music.load(path)
    _requested_volume = volume
    refresh_volume()
    pygame.mixer.music.play(loops=-1, fade_ms=max(0, fade_ms))
    _current_track = track


def stop(fade_ms=300):
    """Stop background music, optionally fading it out."""
    global _current_track

    if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
            pygame.time.wait(fade_ms)
        else:
            pygame.mixer.music.stop()
    _current_track = None


def refresh_volume():
    """Apply the user's master/music mix to the active track."""
    if pygame.mixer.get_init():
        volume = (
            _requested_volume
            * preferences.get("master_volume")
            * preferences.get("music_volume")
        )
        pygame.mixer.music.set_volume(volume)

"""Load and play the game's CC0 sound-effect assets."""

import array
import math
from pathlib import Path

import pygame

from audio import preferences


_SFX_DIR = (
    Path(__file__).resolve().parent.parent / "assets" / "audio" / "sfx"
)
_SOUND_FILES = {
    "menu_move": "menu_highlight.ogg",
    "menu_confirm": "menu_select.ogg",
    "menu_back": "menu_back.mp3",
    "whoosh": "swish_whoosh.wav",
    "attack_light": "swish_light.wav",
    "attack_heavy": "swish_heavy.wav",
    "attack_special": "swish_special.wav",
    "ultimate": "swish_special.wav",
    "projectile_launch": "swish_projectile.wav",
    "hit_light": "hit_light.wav",
    "hit_heavy": "hit_heavy.wav",
    "hit_special": "hit_special.wav",
    "block": "block.wav",
    "ko": "knockout.wav",
    "round_start": "menu_choice.mp3",
    "round_ready": "menu_highlight.ogg",
    "round_fight": "menu_choice.mp3",
    "match_win": "menu_choice.mp3",
    "timer_warn": "menu_highlight.ogg",
}
_EVENT_LEVELS = {
    "menu_move": 0.42,
    "menu_confirm": 0.62,
    "menu_back": 0.42,
    "whoosh": 0.55,
    "attack_light": 0.5,
    "attack_heavy": 0.62,
    "attack_special": 0.72,
    "ultimate": 0.96,
    "projectile_launch": 0.62,
    "hit_light": 0.72,
    "hit_heavy": 0.8,
    "hit_special": 0.9,
    "block": 0.72,
    "ko": 0.92,
    "round_start": 0.72,
    "round_ready": 0.5,
    "round_fight": 0.8,
    "match_win": 0.88,
    "timer_warn": 0.55,
}
_MAX_DURATIONS = {
    "menu_move": 0.16,
    "menu_confirm": 0.30,
    "menu_back": 0.12,
    "whoosh": 0.18,
    "attack_light": 0.20,
    "attack_heavy": 0.25,
    "attack_special": 0.28,
    "ultimate": 0.58,
    "projectile_launch": 0.28,
    "hit_light": 0.28,
    "hit_heavy": 0.32,
    "hit_special": 0.36,
    "block": 0.30,
    "ko": 0.48,
    "round_start": 0.28,
    "round_ready": 0.16,
    "round_fight": 0.32,
    "match_win": 0.40,
    "timer_warn": 0.14,
}
_sounds = {}
_enabled = True


def _make_ultimate_sound():
    """Synthesize an original bass impact, rising rush, and bright tail."""
    mixer_info = pygame.mixer.get_init()
    if mixer_info is None:
        return None
    sample_rate, _, channels = mixer_info
    duration = _MAX_DURATIONS["ultimate"]
    frame_count = int(sample_rate * duration)
    samples = array.array("h")
    phase = 0.0

    for frame in range(frame_count):
        t = frame / sample_rate
        progress = t / duration
        frequency = 92 - 52 * progress
        phase += math.tau * frequency / sample_rate
        impact = math.sin(math.tau * (58 + 24 * progress) * t)
        bass_envelope = math.exp(-t * 8.5)
        rush_envelope = min(1.0, t * 16) * math.exp(-t * 3.8)
        rush = (
            math.sin(phase)
            + 0.38 * math.sin(phase * 2.03)
            + 0.18 * math.sin(phase * 3.1)
        )
        shimmer = math.sin(math.tau * (680 + 950 * progress) * t)
        envelope = min(1.0, t * 28) * max(0.0, 1 - progress ** 2)
        value = (
            impact * bass_envelope * 0.58
            + rush * rush_envelope * 0.32
            + shimmer * envelope * 0.12
        )
        sample = int(max(-1.0, min(1.0, value)) * 21000)
        for _ in range(channels):
            samples.append(sample)
    return pygame.mixer.Sound(buffer=samples.tobytes())


def _trim_sound(sound, max_duration):
    """Remove leading silence and cap long tails while fading the cut."""
    mixer_info = pygame.mixer.get_init()
    if mixer_info is None or abs(mixer_info[1]) != 16:
        return sound

    sample_rate, _, channels = mixer_info
    samples = array.array("h")
    samples.frombytes(sound.get_raw())
    if not samples:
        return sound

    frame_count = len(samples) // channels
    peak = max(abs(sample) for sample in samples)
    threshold = max(240, int(peak * 0.015))
    start = next(
        (
            frame
            for frame in range(frame_count)
            if any(
                abs(samples[frame * channels + channel]) >= threshold
                for channel in range(channels)
            )
        ),
        0,
    )
    start = max(0, start - int(sample_rate * 0.012))
    end = min(frame_count, start + int(sample_rate * max_duration))
    if start == 0 and end == frame_count:
        return sound

    trimmed = array.array("h", samples[start * channels:end * channels])
    fade_frames = min(int(sample_rate * 0.018), len(trimmed) // channels)
    fade_start = len(trimmed) // channels - fade_frames
    if fade_frames:
        for frame in range(fade_start, len(trimmed) // channels):
            gain = (len(trimmed) // channels - frame) / fade_frames
            offset = frame * channels
            for channel in range(channels):
                trimmed[offset + channel] = int(trimmed[offset + channel] * gain)
    return pygame.mixer.Sound(buffer=trimmed.tobytes())


def init():
    """Initialize the mixer if needed and load all mapped CC0 effects."""
    global _sounds, _enabled
    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)
        except pygame.error as error:
            print("[sound_fx] mixer init failed:", error)
            _enabled = False
            return

    _enabled = True
    _sounds = {}
    for name, filename in _SOUND_FILES.items():
        path = _SFX_DIR / filename
        try:
            source = pygame.mixer.Sound(str(path))
            _sounds[name] = _trim_sound(source, _MAX_DURATIONS[name])
        except (pygame.error, OSError) as error:
            print(f"[sound_fx] could not load {name} from {path}: {error}")
    generated_ultimate = _make_ultimate_sound()
    if generated_ultimate is not None:
        _sounds["ultimate"] = generated_ultimate


def play(name, volume=1.0):
    if not _enabled:
        return
    if name not in _EVENT_LEVELS:
        raise KeyError(f"Unknown sound effect: {name}")
    sound = _sounds.get(name)
    if sound is None:
        return
    gain = (
        max(0.0, min(1.0, volume))
        * _EVENT_LEVELS[name]
        * preferences.get("master_volume")
        * preferences.get("sfx_volume")
    )
    channel = sound.play()
    if channel is not None:
        channel.set_volume(gain)


def set_enabled(flag):
    global _enabled
    _enabled = bool(flag)

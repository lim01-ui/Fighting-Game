"""Persistent player preferences for audio and display settings."""

import json
import os
from pathlib import Path

import pygame

import settings


DEFAULTS = {
    "master_volume": 1.0,
    "music_volume": 0.75,
    "sfx_volume": 0.8,
    "fullscreen": False,
    "p1_controls": settings.P1_KEYS.copy(),
}


def _default_values():
    return {
        **DEFAULTS,
        "p1_controls": DEFAULTS["p1_controls"].copy(),
    }


def _copy_values():
    return {
        **_values,
        "p1_controls": _values["p1_controls"].copy(),
    }


def is_valid_control_map(value):
    if not isinstance(value, dict) or set(value) != set(settings.P1_KEYS):
        return False
    keys = []
    for key_name in value.values():
        if not isinstance(key_name, str):
            return False
        if not (
            hasattr(pygame, f"K_{key_name}")
            or hasattr(pygame, f"K_{key_name.lower()}")
        ):
            return False
        if key_name.upper() in {
            "ESCAPE", "P", "R", "H", "T", "V", "RETURN", "SPACE", "KPENTER",
        }:
            return False
        keys.append(key_name.upper())
    return len(keys) == len(set(keys))


def key_name_from_code(key_code):
    for name in dir(pygame):
        if name.startswith("K_") and getattr(pygame, name) == key_code:
            return name[2:]
    raise ValueError(f"Unsupported keyboard key code: {key_code}")


_values = _default_values()
_config_path = (
    Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    / "python-fighters"
    / "settings.json"
)


def load():
    """Load valid settings, preserving safe defaults for invalid entries."""
    global _values
    _values = _default_values()
    settings.P1_KEYS = _values["p1_controls"].copy()
    try:
        with _config_path.open(encoding="utf-8") as file:
            stored = json.load(file)
    except FileNotFoundError:
        return _copy_values()
    except (OSError, json.JSONDecodeError) as error:
        print(f"[preferences] could not read {_config_path}: {error}")
        return _copy_values()

    if not isinstance(stored, dict):
        print(f"[preferences] settings file must contain a JSON object: {_config_path}")
        return _copy_values()

    for key in ("master_volume", "music_volume", "sfx_volume"):
        value = stored.get(key, DEFAULTS[key])
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            _values[key] = max(0.0, min(1.0, float(value)))
        elif key in stored:
            print(f"[preferences] ignoring invalid {key!r} in {_config_path}")
    fullscreen = stored.get("fullscreen", DEFAULTS["fullscreen"])
    if isinstance(fullscreen, bool):
        _values["fullscreen"] = fullscreen
    elif "fullscreen" in stored:
        print(f"[preferences] ignoring invalid 'fullscreen' in {_config_path}")
    controls = stored.get("p1_controls", DEFAULTS["p1_controls"])
    if is_valid_control_map(controls):
        _values["p1_controls"] = controls.copy()
    elif "p1_controls" in stored:
        print(f"[preferences] ignoring invalid 'p1_controls' in {_config_path}")
    settings.P1_KEYS = _values["p1_controls"].copy()
    return _copy_values()


def get(key):
    if key not in DEFAULTS:
        raise KeyError(f"Unknown preference: {key}")
    value = _values[key]
    return value.copy() if isinstance(value, dict) else value


def set_value(key, value):
    if key not in DEFAULTS:
        raise KeyError(f"Unknown preference: {key}")
    if key == "p1_controls":
        if not is_valid_control_map(value):
            raise ValueError("Player 1 controls must use unique, valid, non-reserved keys")
        _values[key] = value.copy()
        settings.P1_KEYS = value.copy()
        return
    if key == "fullscreen":
        if not isinstance(value, bool):
            raise TypeError("fullscreen preference must be a bool")
        _values[key] = value
        return
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{key} preference must be numeric")
    _values[key] = max(0.0, min(1.0, float(value)))


def reset():
    global _values
    _values = _default_values()
    settings.P1_KEYS = _values["p1_controls"].copy()


def save():
    try:
        _config_path.parent.mkdir(parents=True, exist_ok=True)
        _config_path.write_text(
            json.dumps(_values, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as error:
        raise OSError(f"Could not save game settings to {_config_path}: {error}") from error

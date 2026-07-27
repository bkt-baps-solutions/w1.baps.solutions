"""Persist ``W1Config`` to disk so user changes (hotkey, mode) survive a relaunch.

This lives in the macOS adapter rather than ``w1_core`` because the location is OS-specific.
The on-disk format is the pydantic JSON of ``W1Config``; a missing, corrupt, or version-skewed
file falls back to defaults so the app never refuses to launch over its own settings file.
"""
from __future__ import annotations

from pathlib import Path

from w1_core.config import W1Config

_APP_SUPPORT = Path.home() / "Library" / "Application Support" / "W1"


def config_path() -> Path:
    """Absolute path to the user's persisted config (``~/Library/Application Support/W1``)."""
    return _APP_SUPPORT / "config.json"


def load_config() -> W1Config:
    """Load the persisted config, or return defaults if none/invalid exists."""
    path = config_path()
    if not path.exists():
        return W1Config()
    try:
        return W1Config.model_validate_json(path.read_text(encoding="utf-8"))
    except Exception:
        # Corrupt or incompatible file: prefer working defaults over a hard crash.
        return W1Config()


def save_config(cfg: W1Config) -> None:
    """Atomically write ``cfg`` to the user's config path (creating the dir if needed)."""
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(cfg.model_dump_json(indent=2), encoding="utf-8")
    tmp.replace(path)  # atomic on the same filesystem

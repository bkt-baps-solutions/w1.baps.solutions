"""Typed configuration for w1. Pure data — no desktop/ML imports.

A single config object flows from the platform adapter into the core pipeline. Everything
that changes behaviour (model, hotkey, fuzzy thresholds) lives here so the core stays
declarative and the adapter stays thin.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class HotkeyMode(str, Enum):
    toggle = "toggle"            # tap to start, tap to stop
    push_to_talk = "push_to_talk"  # hold to talk, release to insert


class FuzzyConfig(BaseModel):
    """Conservative OOV-only fuzzy correction of near-miss sacred terms."""

    enabled: bool = True
    min_similarity: float = Field(default=0.88, ge=0.0, le=1.0)
    min_term_length: int = Field(default=4, ge=1)  # ultra-short terms are exact-match only


class CleanupConfig(BaseModel):
    """Light disfluency cleanup (deliberately conservative — never rewrites meaningful words)."""

    enabled: bool = True
    remove_fillers: bool = True             # drop "um"/"uh" disfluencies only
    apply_self_corrections: bool = False    # off: "X, I mean Y" rewriting changes the user's words


class ConfidenceConfig(BaseModel):
    """Reject low-confidence transcriptions so noise/garbage is never pasted.

    Thresholds mirror Whisper's own decoding fallbacks; speech that the model is
    confident about clears them comfortably, so normal dictation is never gated.
    """

    enabled: bool = True
    # Gate if the mean per-segment no-speech probability exceeds this (silence/noise).
    max_no_speech_prob: float = Field(default=0.6, ge=0.0, le=1.0)
    # Gate if the mean per-segment average token log-probability falls below this.
    min_avg_logprob: float = Field(default=-1.0, le=0.0)


class W1Config(BaseModel):
    """Top-level runtime configuration."""

    # pydantic v2: allow the ``model_*`` field names without protected-namespace warnings.
    model_config = ConfigDict(protected_namespaces=())

    model_id: str = "mlx-community/whisper-large-v3-turbo"
    backend: str = "auto"          # auto | mlx | faster | mock
    language: str | None = "en"

    hotkey_mode: HotkeyMode = HotkeyMode.push_to_talk
    hotkey: str = "<alt_r>"        # pynput-style; Right-Option. Never Cmd+M.

    bias_token_budget: int = Field(default=224, ge=16)
    fuzzy: FuzzyConfig = Field(default_factory=FuzzyConfig)
    cleanup: CleanupConfig = Field(default_factory=CleanupConfig)
    confidence: ConfidenceConfig = Field(default_factory=ConfidenceConfig)

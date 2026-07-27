"""Deterministic post-correction: light cleanup + canonical spelling of spoken terms.

Order is load-bearing: cleanup -> mask protected -> fuzzy canonical-spelling snap -> unmask.

There is NO word substitution. Ordinary English is transcribed verbatim ("temple" stays
"temple", "saint" stays "saint"); the only change to wording is fixing the *spelling* of the
specialised BAPS/Gujarati terms the user actually says, snapping a mis-heard token onto its
canonical glossary spelling (e.g. "vachanamrit" -> "Vachanamrut"). Every transformation
contributes to a structured log.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..config import W1Config
from .cleanup import cleanup_text
from .fuzzy import snap_fuzzy
from .protect import mask_protected, unmask_protected


@dataclass
class CorrectionResult:
    text: str
    applied: list[dict] = field(default_factory=list)


def correct(text: str, config: W1Config) -> CorrectionResult:
    """Apply the deterministic correction chain (cleanup + canonical-spelling snap)."""
    applied: list[dict] = []

    if config.cleanup.enabled:
        text, log = cleanup_text(
            text,
            remove_fillers=config.cleanup.remove_fillers,
            apply_self_corrections=config.cleanup.apply_self_corrections,
        )
        applied.extend(log)

    masked, store = mask_protected(text)

    if config.fuzzy.enabled:
        masked, fuzzy_log = snap_fuzzy(
            masked,
            min_similarity=config.fuzzy.min_similarity,
            min_term_length=config.fuzzy.min_term_length,
        )
        applied.extend(fuzzy_log)

    return CorrectionResult(text=unmask_protected(masked, store), applied=applied)

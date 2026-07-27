"""Load generated w1_data JSON into compiled runtime structures.

Builds the in-vocabulary index and canonical-spelling map the fuzzy stage uses to tell a known
term from an out-of-vocabulary near-miss (and what to snap it onto), plus the protected terms,
diacritics, and Whisper bias seed. No word-substitution rules — the engine never rewrites the
user's ordinary words; it only corrects the spelling of specialised terms they actually say.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import w1_data


@dataclass(frozen=True)
class RuleData:
    glossary: tuple[dict, ...]
    in_vocab: frozenset           # lowercased canonical + alias spellings (the "known word" set)
    canonical_by_lower: dict      # lower spelling -> canonical spelling (fuzzy snap target)
    protected: tuple[str, ...]
    diacritics: dict
    bias_seed: tuple[str, ...]


@lru_cache(maxsize=1)
def load_rule_data() -> RuleData:
    """Load and compile all rule data once (cached for process lifetime)."""
    glossary = w1_data.load("glossary")
    protected = tuple(w1_data.load("protected_terms"))

    in_vocab: set[str] = set()
    by_lower: dict[str, str] = {}
    for entry in glossary:
        for alias in entry["aliases"]:
            in_vocab.add(alias.lower())
            by_lower.setdefault(alias.lower(), alias)
        by_lower[entry["canonical"].lower()] = entry["canonical"]

    # Master Glossary (BAPS) — the large canonical term list ingested from the PDF. These are
    # the spellings the fuzzy stage snaps a mis-heard term onto, and the known-word set that
    # keeps a correctly-spoken term from being altered.
    for entry in w1_data.load("master_glossary"):
        canonical = entry["canonical"]
        in_vocab.add(canonical.lower())
        by_lower.setdefault(canonical.lower(), canonical)

    for term in protected:
        in_vocab.add(term.lower())
        by_lower.setdefault(term.lower(), term)

    # Bias-seed terms are known-good spellings (e.g. "darshan", "seva") — treat them as
    # in-vocabulary so the fuzzy stage never snaps a correct common term onto a rarer variant.
    bias_seed_raw = w1_data.load("bias_seed")
    for term in bias_seed_raw:
        in_vocab.add(term.lower())
        for word in term.split():
            if len(word) >= 3:
                in_vocab.add(word.lower())

    return RuleData(
        glossary=tuple(glossary),
        in_vocab=frozenset(in_vocab),
        canonical_by_lower=by_lower,
        protected=protected,
        diacritics=w1_data.load("diacritics"),
        bias_seed=tuple(w1_data.load("bias_seed")),
    )

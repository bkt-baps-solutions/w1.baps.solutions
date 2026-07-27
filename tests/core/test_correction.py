"""Correction-engine unit tests (pure — no audio, model, or OS).

The load-bearing safety property: the engine NEVER substitutes the user's words. It transcribes
ordinary English verbatim and only fixes the *spelling* of specialised BAPS/Gujarati terms the
user actually says (snapping a mis-heard token onto its canonical glossary spelling)."""
from w1_core.config import W1Config
from w1_core.correction.engine import correct
from w1_core.correction.protect import mask_protected, unmask_protected


def _cfg(**over):
    return W1Config(**over)


# --- the cardinal guarantee: ordinary English is never changed --------------------------
def test_ordinary_english_passes_through_untouched():
    safe = [
        "I went to the temple to see the saint",        # NEVER -> mandir / Swami
        "the patient was on the ward this morning",
        "we hit a project milestone for our main stakeholder",
        "perhaps we will meet on Tuesday",
        "I gave him a hand with the array index",
    ]
    for s in safe:
        res = correct(s, _cfg())
        assert res.text == s, f"false correction: {s!r} -> {res.text!r}"


# --- spelling of spoken specialised terms IS corrected ----------------------------------
def test_misheard_terms_get_canonical_spelling():
    res = correct("we read the vachanamrit at akshardam", _cfg())
    assert "Vachanamrut" in res.text
    assert "Akshardham" in res.text
    assert res.applied  # a snap was logged


def test_correctly_spelled_terms_are_left_alone():
    text = "the concept of brahmacharya and the antahkaran"
    assert correct(text, _cfg()).text == text


# --- cleanup: light disfluency removal, but no word rewriting by default -----------------
def test_fillers_removed_but_words_not_rewritten():
    res = correct("um the meeting is on Tuesday", _cfg())
    assert "um" not in res.text.split()
    assert "meeting" in res.text  # real words untouched


def test_self_corrections_are_off_by_default():
    # "X, I mean Y" rewriting changes the user's words -> disabled by default.
    text = "send it Monday, I mean Tuesday"
    assert correct(text, _cfg()).text == text


# --- protected terms ----------------------------------------------------------------------
def test_protect_roundtrip_canonical_casing():
    masked, store = mask_protected("we went to akshardham for satsang")
    assert "akshardham" not in masked and "satsang" not in masked
    assert unmask_protected(masked, store) == "we went to Akshardham for satsang"


def test_protect_preserves_name_maya():
    masked, store = mask_protected("Maya went home")
    assert unmask_protected(masked, store) == "Maya went home"

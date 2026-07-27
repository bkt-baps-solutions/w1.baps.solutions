"""Master Glossary (PDF-ingested) integration: canonical spelling of spoken BAPS terms,
without substituting ordinary English. This encodes the product guarantee — fix the spelling
of specialised terms the user actually says; never change their ordinary words."""
import w1_data
from w1_core.correction.fuzzy import snap_fuzzy
from w1_core.correction.loader import load_rule_data


def test_master_glossary_dataset_loads():
    data = w1_data.load("master_glossary")
    assert len(data) > 800
    assert all("canonical" in e for e in data)


def test_master_terms_are_in_vocab():
    vocab = load_rule_data().in_vocab
    for term in ["akshardham", "vachanamrut", "brahmacharya", "ahamkar", "antahkaran"]:
        assert term in vocab


def test_misheard_terms_snap_to_canonical_spelling():
    out, log = snap_fuzzy("we read the vachanamrit and went to akshardam")
    assert "Vachanamrut" in out
    assert "Akshardham" in out
    assert log  # something was snapped


def test_ordinary_english_is_never_changed():
    # The cardinal guarantee: no word substitution of plain English.
    for sentence in [
        "I went to the temple to see the saint",
        "the patient was on the ward this morning",
        "we have a meeting about the project today",
    ]:
        out, _ = snap_fuzzy(sentence)
        assert out == sentence


def test_correctly_spelled_terms_are_left_alone():
    sentence = "the concept of brahmacharya and the antahkaran"
    out, _ = snap_fuzzy(sentence)
    assert out == sentence

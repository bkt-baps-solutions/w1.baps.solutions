"""Tests for the rule-data loader: the in-vocabulary index and canonical-spelling map."""
from w1_core.correction.loader import load_rule_data


def test_load_rule_data_is_populated_and_indexed():
    d = load_rule_data()
    assert d.glossary and d.protected and d.bias_seed
    # the in-vocab index is lowercased and covers canonical glossary spellings
    assert all(t == t.lower() for t in d.in_vocab)
    for entry in d.glossary:
        assert entry["canonical"].lower() in d.canonical_by_lower


def test_master_glossary_terms_are_indexed():
    d = load_rule_data()
    for term in ["akshardham", "vachanamrut", "brahmacharya"]:
        assert term in d.in_vocab
        assert d.canonical_by_lower[term][:1].isupper() or term in d.canonical_by_lower


def test_canonical_casing_is_preserved():
    d = load_rule_data()
    assert d.canonical_by_lower["akshardham"] == "Akshardham"


def test_load_rule_data_is_cached():
    assert load_rule_data() is load_rule_data()  # lru_cache -> identity

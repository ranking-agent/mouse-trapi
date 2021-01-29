"""Test utilities."""
from util import (
    find_last, find_last_matching, plural_noun_phrase, plural_verb_phrase,
    singular_noun_cache, singular_verb_cache,
)


def test_find_last():
    """Test find_last()."""
    assert find_last([1, 2, 3, 2, 1], 2) == 3


def test_find_last_matching():
    """Test find_last()."""
    assert find_last_matching(["123", "12", "1", "12", "123"], r"^\d{2}$") == 3


def test_plural_verb_phrase():
    """Test plural_verb_phrase()."""
    assert plural_verb_phrase("is exact match to") == "are exact matches to"
    assert plural_verb_phrase("expresses") == "express"
    assert singular_verb_cache["express"] == "expresses"


def test_plural_noun_phrase():
    """Test plural_noun_phrase()."""
    assert plural_noun_phrase("ugly chicken") == "ugly chickens"
    assert singular_noun_cache["ugly chickens"] == "ugly chicken"

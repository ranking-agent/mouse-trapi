"""Utilities."""
from collections.abc import Callable
from functools import wraps
import re
from typing import Dict, List, NamedTuple

prepositions = [
    "to",
    "of",
    "with",
    "in",
    "for",
    "as",
    "by",
]
preposition_pattern = "|".join(prepositions)


class Triple(NamedTuple):
    subject_category: str
    predicate: str
    object: str


class CURIETriple(NamedTuple):
    subject_category: str
    predicate: str
    object: str


def find_last(list_: List[str], element: str) -> int:
    """Find index of last occurrence of element in list."""
    return next(
        idx
        for idx, el in reversed(list(enumerate(list_)))
        if el == element
    )


def find_last_matching(list_: List[str], pattern: str) -> int:
    """Find index of last occurrence of list matching pattern."""
    return next(
        idx
        for idx, el in reversed(list(enumerate(list_)))
        if re.fullmatch(pattern, el)
    )


def inverter(cache: Dict[str, str]) -> Callable:
    def decorator(fcn) -> Callable:
        @wraps(fcn)
        def wrapper(input):
            """Wrapper."""
            output = fcn(input)
            cache[output] = input
            return output
        return wrapper
    return decorator


singular_noun_cache = dict()


@inverter(singular_noun_cache)
def plural_noun_phrase(noun_phrase: str) -> str:
    """Convert to plural."""
    if " of " in noun_phrase:
        subterms = noun_phrase.split(" of ", 1)
        return f"{plural_noun_phrase(subterms[0])} of {subterms[1]}"
    if " or " in noun_phrase:
        return " or ".join(plural_noun_phrase(subterm) for subterm in noun_phrase.split(" or "))
    if re.search("[^aeiou]y$", noun_phrase):
        return noun_phrase[:-1] + "ies"
    if re.search("(?:[xs]|ch|sh)$", noun_phrase):
        return noun_phrase + "es"
    return noun_phrase + "s"


def plural_verb(verb: str) -> str:
    """Convert to plural."""
    if verb == "is":
        return "are"
    if verb == "has":
        return "have"
    if verb.endswith("sses"):
        return verb[:-2]
    if verb.endswith("s"):
        return verb[:-1]
    raise ValueError(f"What kind of verb is '{verb}'?")


singular_verb_cache = dict()


@inverter(singular_verb_cache)
def plural_verb_phrase(verb_phrase: str) -> str:
    """Convert to plural."""
    words = verb_phrase.split(" ")

    # ignore leading adverbs
    if words[0].endswith("ly"):
        return words[0] + " " + plural_verb_phrase(" ".join(words[1:]))
    
    # make verb plural
    words[0] = plural_verb(words[0])

    # for is/are phrases, make object plural, too
    if words[0] == "are":
        prep_idx = find_last_matching(words, preposition_pattern)
        middly_bits = " ".join(words[1:prep_idx])
        # only if object is a noun phrase
        if (
                middly_bits
                and middly_bits != "same"
                and middly_bits != "in linkage disequilibrium"
                and not middly_bits.endswith("ed")
                and not middly_bits.endswith("able")
                and not middly_bits.endswith("ous")
                and not middly_bits.endswith("ilar")
        ):
            return " ".join([
                words[0],
                plural_noun_phrase(middly_bits),
                " ".join(words[prep_idx:]),
            ])
    return " ".join(words)

"""Parse question into query graph."""
import json
import os
from pathlib import Path
import re

import bmt
import httpx

from .util import *

toolkit = bmt.Toolkit()

dir_path = Path(__file__).parent
with open(dir_path / "biolink_grammar_fixes.json", "r") as stream:
    biolink_to_grammatical = json.load(stream)
grammatical_to_biolink = {
    value: key
    for key, value in biolink_to_grammatical.items()
}

categories = toolkit.get_descendants("biological entity")
categories += [
    plural_noun_phrase(category)
    for category in categories
]

predicates = toolkit.get_descendants("related to")
predicates = [
    biolink_to_grammatical.get(predicate, predicate)
    for predicate in predicates
]
predicates += [
    plural_verb_phrase(predicate)
    for predicate in predicates
]

exp_0 = r"(((tell( me)? )?(what|which))|find(( for)? me)?)"
exp_subject_category = "|".join(categories)
exp_1 = r"( that)?"
exp_predicate = "|".join(predicates)
exp_object_name = r".*"

exp = (
    f"{exp_0} (?P<subject_category>{exp_subject_category}){exp_1} "
    f"(?P<predicate>{exp_predicate}) (?P<object_name>{exp_object_name})"
)
re_obj = re.compile(exp)


def fix_predicate(predicate):
    """Convert predicate to biolink form."""
    predicate = singular_verb_cache.get(predicate, predicate)
    predicate = grammatical_to_biolink.get(predicate, predicate)
    return predicate


def fix_category(category):
    """Convert category to biolink form."""
    return singular_noun_cache.get(category, category)


def format(string):
    """Format as CURIE."""
    return toolkit._format_all_elements([string], formatted=True)[0]


def preprocess(question):
    """Preprocess question."""
    question = question.lower()
    words = question.split(" ")
    # remove leading and trailing non-alphanumerics
    words = [re.sub(r"^[^\w]+|[^\w]+$", "", word) for word in words]
    things_to_remove = [
        r"please", r"a", r"an", r"the",
        r"[^\w]*",  # entirely non-alphanumeric "words", including the empty string
    ]
    # remove above things
    pattern = f"^(?:{'|'.join(things_to_remove)})$"
    words = [
        word for word in words
        if re.search(pattern, word) is None
    ]
    return " ".join(words)


def sentence_to_triple(question: str) -> Triple:
    """Parse natural-language question."""
    question = preprocess(question)
    match = re_obj.fullmatch(question)
    if match is None:
        raise RuntimeError("Failed to parse")
    predicate = fix_predicate(match.group("predicate"))
    subject_category = fix_category(match.group("subject_category"))
    object_name = match.group("object_name")
    return Triple(subject_category, predicate, object_name)


def sentence_to_curie_triple(question):
    """Convert sentence to CURIE triple."""
    return triple_to_curie_triple(sentence_to_triple(question))


def category_to_curie(category):
    """Convert category to CURIE."""
    return format(category)


def predicate_to_curie(predicate):
    """Convert predicate to CURIE."""
    return format(predicate)


def object_name_to_curie(object_name):
    """Convert object name to CURIE."""
    response = httpx.post(
        "http://robokop.renci.org:2433/lookup",
        params={"string": object_name, "limit":10},
    )
    if not response:
        raise RuntimeError(f"Unrecognized thing '{object_name}'")
    return next(iter(response.json()))


def triple_to_curie_triple(triple: Triple) -> CURIETriple:
    """Convert triple to CURIE triple."""
    return CURIETriple(
        category_to_curie(triple.subject_category),
        predicate_to_curie(triple.predicate),
        object_name_to_curie(triple.object),
    )


def curie_triple_to_qgraph(
        curie_triple: CURIETriple,
        subject_key="n0",
        object_key="n1",
        edge_key="e01",
):
    """Convert CURIE triple to query graph."""
    return {
        "nodes": {
            subject_key: {
                "category": curie_triple.subject_category
            },
            object_key: {
                "id": curie_triple.object,
            }
        },
        "edges": {
            edge_key: {
                "subject": subject_key,
                "predicate": curie_triple.predicate,
                "object": object_key
            }
        }
    }


def parse_question(question: str):
    """Parse natural-language question."""
    triple = sentence_to_triple(question)
    curie_triple = triple_to_curie_triple(triple)
    return curie_triple_to_qgraph(
        curie_triple,
        subject_key=triple.subject_category,
        edge_key=triple.predicate,
        object_key=triple.object,
    )

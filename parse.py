"""Parse question into query graph."""
import json
import re

import bmt
import httpx

from util import *

toolkit = bmt.Toolkit()

with open("biolink_grammar_fixes.json", "r") as stream:
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

exp_0 = r"(?:what|which|find)"
exp_subject_category = "|".join(categories)
exp_1 = r"(?: that)?"
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


def parse_question(question):
    """Parse natural-language question."""
    question = preprocess(question)
    match = re_obj.fullmatch(question)
    if match is None:
        raise RuntimeError("Failed to parse")
    predicate = fix_predicate(match.group("predicate"))
    subject_category = fix_category(match.group("subject_category"))
    object_name = match.group("object_name")
    response = httpx.post(
        "http://robokop.renci.org:2433/lookup",
        params={"string": object_name, "limit":10},
    )
    if not response:
        raise RuntimeError(f"Unrecognized thing '{object_name}'")
    object_id = next(iter(response.json()))
    return {
        "nodes": {
            subject_category: {
                "category": format(subject_category)
            },
            object_name: {
                "id": object_id,
            }
        },
        "edges": {
            predicate: {
                "subject": subject_category,
                "predicate": format(predicate),
                "object": object_name
            }
        }
    }

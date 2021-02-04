"""Parse question into query graph."""
import json
from pathlib import Path
import re

import bmt
import httpx

from .util import *

toolkit = bmt.Toolkit()

dir_path = Path(__file__).parent
with open(dir_path / "biolink_grammar_fixes.json", "r") as stream:
    biolink_to_grammatical = json.load(stream)
with open(dir_path / "category_synonyms.json", "r") as stream:
    category_synonyms = json.load(stream)
grammatical_to_biolink = {
    value: key
    for key, value in biolink_to_grammatical.items()
}
synonym_to_category = {
    synonym: category
    for category, synonyms in category_synonyms.items()
    for synonym in synonyms
}

categories = toolkit.get_descendants("biological entity")
categories += list(synonym_to_category.keys())
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

what = r"(what|which)"
find = rf"(((tell( me)? )?{what})|find(( for)? me)?)"
exp_category = "|".join(categories)
that = r"( that)?"
exp_predicate = "|".join(predicates)
does = r"(do(es) )?"
exp_name = r".*"

expressions = [
    (
        f"{find} ((?P<subject_category>{exp_category}){that} )?"
        f"(?P<predicate>{exp_predicate}) (?P<object_name>{exp_name})"
    ),  # What drugs treat asthma?
    (
        f"{find} ((?P<object_category>{exp_category}){that} )?{does}"
        f"(?P<subject_name>{exp_name}) (?P<predicate>{exp_predicate})"
    ),  # What disease does albuterol treat? Find me diseases that albuterol treats.
    (
        f"(?P<subject_name>{exp_name}) (?P<predicate>{exp_predicate}) "
        f"{what}( (?P<object_category>{exp_category}))?"
    ),  # Asthma is treated by what drugs?
]
re_objs = [re.compile(exp) for exp in expressions]


class ParseError(Exception):
    """Parse error."""


def fix_predicate(predicate):
    """Convert predicate to biolink form."""
    predicate = singular_verb_cache.get(predicate, predicate)
    predicate = grammatical_to_biolink.get(predicate, predicate)
    return predicate


def fix_category(category):
    """Convert category to biolink form."""
    category = singular_noun_cache.get(category, category)
    category = synonym_to_category.get(category, category)
    return category


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
    for re_obj in re_objs:
        match = re_obj.fullmatch(question)
        if match is not None:
            break
    else:
        raise ParseError("Failed to parse")
    elements = match.groupdict()
    if "object_name" in elements:
        predicate = fix_predicate(elements["predicate"])
        subject = Category(fix_category(elements["subject_category"] or "named thing"))
        object = Name(elements["object_name"])
    elif "subject_name" in elements:
        predicate = fix_predicate(elements["predicate"])
        object = Category(fix_category(elements["object_category"] or "named thing"))
        subject = Name(elements["subject_name"])
    else:
        raise RuntimeError("subject_category or object_category must be present")
    return Triple(subject, predicate, object)


def sentence_to_curie_triple(question):
    """Convert sentence to CURIE triple."""
    return triple_to_curie_triple(sentence_to_triple(question))


def category_to_curie(category: Category) -> Category:
    """Convert category to CURIE."""
    return Category(format(category))


def predicate_to_curie(predicate: str) -> str:
    """Convert predicate to CURIE."""
    return format(predicate)


def name_to_curie(name: Name) -> Name:
    """Convert name to CURIE."""
    response = httpx.post(
        "http://robokop.renci.org:2433/lookup",
        params={"string": name, "limit":10},
    )
    if not response:
        raise ParseError(f"Unrecognized thing '{name}'")
    return Name(next(iter(response.json())))


def sobject_to_curie(sobject: Union[Category, Name]) -> Union[Category, Name]:
    """Convert subject or object to CURIE."""
    if isinstance(sobject, Category):
        return category_to_curie(sobject) 
    else:
        return name_to_curie(sobject)


def triple_to_curie_triple(triple: Triple) -> CURIETriple:
    """Convert triple to CURIE triple."""
    return CURIETriple(
        sobject_to_curie(triple.subject),
        predicate_to_curie(triple.predicate),
        sobject_to_curie(triple.object),
    )


def sobject_to_qnode(sobject: Union[Category, Name]) -> Dict:
    """Convert subject or object to qnode."""
    if isinstance(sobject, Category):
        return {
            "category": sobject
        } 
    else:
        return {
            "id": sobject
        }


def curie_triple_to_qgraph(
        curie_triple: CURIETriple,
        subject_key="n0",
        object_key="n1",
        edge_key="e01",
):
    """Convert CURIE triple to query graph."""
    return {
        "nodes": {
            subject_key: sobject_to_qnode(curie_triple.subject),
            object_key: sobject_to_qnode(curie_triple.object),
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
        subject_key=triple.subject,
        edge_key=triple.predicate,
        object_key=triple.object,
    )

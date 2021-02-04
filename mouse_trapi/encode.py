"""Encode query graph in English."""
import re
from typing import Union

import httpx

from .util import Triple, CURIETriple, Category, Name


def pascalcase_to_sentencecase(string: str) -> str:
    """Convert "PascalCase" to "sentence case"."""
    return re.sub(
        r"(?<![A-Z])[A-Z]",
        lambda m: " " + m.group(0).lower(),
        string,
    ).strip()


def snakecase_to_sentencecase(string: str) ->  str:
    """Convert "snake_case" to "sentence case"."""
    return string.replace("_", " ").strip()


def english_triple_to_sentence(triple: Triple) -> str:
    """Convert triple to sentence."""
    if isinstance(triple.subject, Category):
        return f"What {triple.subject} {triple.predicate} {triple.object}?"
    else:
        return f"{triple.subject} {triple.predicate} what {triple.object}?"


def sobject_curie_to_name(sobject: Union[Category, Name]) -> Union[Category, Name]:
    """Convert subject or object CURIE to name."""
    if isinstance(sobject, Category):
        return Category(pascalcase_to_sentencecase(
            sobject.split(":")[1]
        ))
    else:
        response = httpx.get(
            "https://nodenormalization-sri.renci.org/get_normalized_nodes",
            params={"curie": sobject},
        )
        response.raise_for_status()
        return Name(response.json()[sobject]["id"]["label"])


def curie_triple_to_sentence(curie_triple: CURIETriple) -> str:
    """Convert CURIE triple to sentence."""
    subject = sobject_curie_to_name(curie_triple.subject)
    object = sobject_curie_to_name(curie_triple.object)
    predicate = snakecase_to_sentencecase(
        curie_triple.predicate.split(":")[1]
    )
    triple = Triple(subject, predicate, object)
    return english_triple_to_sentence(triple)


def encode(qgraph) -> str:
    """Encode quergy graph."""
    assert len(qgraph["nodes"]) == 2
    assert len(qgraph["edges"]) == 1
    edge = next(iter(qgraph["edges"].values()))
    subject_qnode = qgraph["nodes"][edge["subject"]]
    object_qnode = qgraph["nodes"][edge["object"]]
    if subject_qnode.get("id", None) is None:
        assert object_qnode.get("id", None) is not None
        subject_category = subject_qnode.get("category", "biolink:NamedThing")
        object_id = object_qnode["id"]
        return curie_triple_to_sentence(CURIETriple(
            Category(subject_category),
            edge.get("predicate", "biolink:related_to"),
            Name(object_id),
        ))
    else:
        assert object_qnode.get("id", None) is None
        subject_id = subject_qnode["id"]
        object_category = object_qnode.get("category", "biolink:NamedThing")
        return curie_triple_to_sentence(CURIETriple(
            Name(subject_id),
            edge.get("predicate", "biolink:related_to"),
            Category(object_category),
        ))

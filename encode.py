"""Encode query graph in English."""
import re

import httpx

from util import Triple, CURIETriple


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
    return f"What {triple.subject_category} {triple.predicate} {triple.object}?"


def curie_triple_to_sentence(curie_triple: CURIETriple) -> str:
    """Convert CURIE triple to sentence."""
    subject_category = pascalcase_to_sentencecase(
        curie_triple.subject_category.split(":")[1]
    )
    predicate = snakecase_to_sentencecase(
        curie_triple.predicate.split(":")[1]
    )
    response = httpx.get(
        "https://nodenormalization-sri.renci.org/get_normalized_nodes",
        params={"curie": curie_triple.object},
    )
    response.raise_for_status()
    object_name = response.json()[curie_triple.object]["id"]["label"]
    triple = Triple(subject_category, predicate, object_name)
    return english_triple_to_sentence(triple)


def encode(qgraph) -> str:
    """Encode quergy graph."""
    assert len(qgraph["nodes"]) == 2
    assert len(qgraph["edges"]) == 1
    edge = next(iter(qgraph["edges"].values()))
    assert edge.get("predicate", None) is not None
    subject_qnode = qgraph["nodes"][edge["subject"]]
    assert (
        subject_qnode.get("category", None) is not None
        and subject_qnode.get("id", None) is None
    )
    object_qnode = qgraph["nodes"][edge["object"]]
    assert object_qnode.get("id", None) is not None
    object_id = object_qnode["id"]
    return curie_triple_to_sentence(CURIETriple(
        subject_qnode["category"],
        edge["predicate"],
        object_id,
    ))

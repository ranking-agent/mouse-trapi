"""Encode query graph in English."""
import re

import httpx


def pascalcase_to_sentencecase(string):
    """Convert "PascalCase" to "sentence case"."""
    return re.sub(
        r"(?<![A-Z])[A-Z]",
        lambda m: " " + m.group(0).lower(),
        string,
    ).strip()


def snakecase_to_sentencecase(string):
    """Convert "snake_case" to "sentence case"."""
    return string.replace("_", " ").strip()


def encode(qgraph):
    """Encode quergy graph."""
    assert len(qgraph["nodes"]) == 2
    assert len(qgraph["edges"]) == 1
    edge = next(iter(qgraph["edges"].values()))
    subject_qnode = qgraph["nodes"][edge["subject"]]
    object_qnode = qgraph["nodes"][edge["object"]]
    assert (
        subject_qnode.get("category", None) is not None
        and subject_qnode.get("id", None) is None
    )
    assert object_qnode.get("id", None) is not None
    assert edge.get("predicate", None) is not None
    subject_category = pascalcase_to_sentencecase(
        subject_qnode["category"].split(":")[1]
    )
    object_id = object_qnode["id"]
    predicate = snakecase_to_sentencecase(
        edge["predicate"].split(":")[1]
    )
    response = httpx.get(
        "https://nodenormalization-sri.renci.org/get_normalized_nodes",
        params={"curie": object_id},
    )
    response.raise_for_status()
    object_name = response.json()[object_id]["id"]["label"]
    return f"What {subject_category} {predicate} {object_name}?"

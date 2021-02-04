"""Test encoder."""
from mouse_trapi.encode import encode, pascalcase_to_sentencecase, snakecase_to_sentencecase


def test_convert_casing():
    """Test convert casing."""
    assert pascalcase_to_sentencecase("ChemicalSubstance") == "chemical substance"
    assert snakecase_to_sentencecase("chemical_substance") == "chemical substance"


def test_encode():
    """Test encoding."""
    encode({
        "nodes": {
            "drug": {
                "category": "biolink:Drug"
            },
            "type 2 diabetes": {
                "id": "HP:0005978"
            }
        },
        "edges": {
            "treats": {
                "subject": "drug",
                "predicate": "biolink:treats",
                "object": "type 2 diabetes"
            }
        }
    }) == "What drug treats type 2 diabetes mellitus?"
    encode({
        "nodes": {
            "disease": {
                "category": "biolink:Disease"
            },
            "albuterol": {
                "id": "CHEBI:2549"
            }
        },
        "edges": {
            "treats": {
                "subject": "albuterol",
                "object": "disease"
            }
        }
    }) == "Albuterol is related to what diseases?"

"""Test encoder."""
from encode import encode, pascalcase_to_sentencecase, snakecase_to_sentencecase


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

"""Test parser."""
from parse import parse_question, preprocess, format


def test_preprocess():
    """Test preprocess."""
    assert preprocess("Hello, my name is Bob.") == "hello my name is bob"
    assert preprocess("Can I   have  a bag, please?") == "can i have bag"


def test_basic():
    """Test basic questions."""
    assert parse_question("Tell me which drug treats type 2 diabetes.") == {
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
    }
    assert parse_question("What drug treats type 2 diabetes?") == {
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
    }
    assert parse_question("Which drugs treat type 2 diabetes?") == {
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
    }
    assert parse_question("Find a chemical substance that is an exact match to Chagas disease!") == {
        "nodes": {
            "chemical substance": {
                "category": "biolink:ChemicalSubstance"
            },
            "chagas disease": {
                "id": "MONDO:0001444"
            }
        },
        "edges": {
            "exact match": {
                "subject": "chemical substance",
                "predicate": "biolink:exact_match",
                "object": "chagas disease"
            }
        }
    }
    assert parse_question("Find chemical substances that are exact matches to Chagas disease, please.") == {
        "nodes": {
            "chemical substance": {
                "category": "biolink:ChemicalSubstance"
            },
            "chagas disease": {
                "id": "MONDO:0001444"
            }
        },
        "edges": {
            "exact match": {
                "subject": "chemical substance",
                "predicate": "biolink:exact_match",
                "object": "chagas disease"
            }
        }
    }


def test_format():
    """Test format()."""
    assert format("treats") == "biolink:treats"
    assert format("chemical substance") == "biolink:ChemicalSubstance"

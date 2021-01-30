"""Test errors."""
from fastapi.testclient import TestClient
from mouse_trapi.server import app

client = TestClient(app)


def test_parse_failure():
    """Test failure to parse."""
    response = client.post("/to_trapi", json="What aaagggh?")
    assert response.status_code == 400
    assert response.json() == {"detail": "Failed to parse"}

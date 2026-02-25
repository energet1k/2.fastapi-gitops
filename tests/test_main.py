"""Tests for the main FastAPI application."""

import runpy
from unittest.mock import ANY, patch

import pytest
from fastapi.testclient import TestClient

from app.main import ITEMS, app

client = TestClient(app)


def test_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to FastAPI GitOps Starter!"}


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "fastapi-gitops-starter"


def test_list_items():
    """Test the list items endpoint."""
    response = client.get("/api/items")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) == 3
    assert data["items"][0]["id"] == 1


def test_get_item():
    """Test the get item endpoint."""
    response = client.get("/api/items/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Item 1"
    assert data["description"] == "First item"


def test_get_item_not_found():
    """Test that requesting a non-existent item returns 404."""
    response = client.get("/api/items/9999")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "9999" in data["detail"]


def test_get_item_invalid_type():
    """Test that a non-integer item ID returns 422 Unprocessable Entity."""
    response = client.get("/api/items/not-a-number")
    assert response.status_code == 422


def test_get_item_negative_id():
    """Test that a negative item ID returns 404 (not found, not a server error)."""
    response = client.get("/api/items/-1")
    assert response.status_code == 404


def test_list_items_structure():
    """Test that every item in the list has the required fields."""
    response = client.get("/api/items")
    assert response.status_code == 200
    for item in response.json()["items"]:
        assert "id" in item
        assert "name" in item
        assert "description" in item


def test_list_items_matches_known_items():
    """Test that the list endpoint returns exactly the items in ITEMS."""
    response = client.get("/api/items")
    returned_ids = {item["id"] for item in response.json()["items"]}
    assert returned_ids == set(ITEMS.keys())


@pytest.mark.parametrize("item_id", [1, 2, 3])
def test_get_each_known_item(item_id):
    """Test that each known item can be retrieved individually."""
    response = client.get(f"/api/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["name"] == ITEMS[item_id]["name"]
    assert data["description"] == ITEMS[item_id]["description"]


def test_unknown_route_returns_404():
    """Test that requesting an undefined route returns 404."""
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404


def test_health_check_content_type():
    """Test that the health endpoint returns JSON content type."""
    response = client.get("/health")
    assert "application/json" in response.headers["content-type"]


def test_main_entrypoint():
    """Test the __main__ entrypoint to cover the uvicorn.run call."""
    with patch("uvicorn.run") as mock_run:
        runpy.run_module("app.main", run_name="__main__", alter_sys=True)
        mock_run.assert_called_once_with(ANY, host="0.0.0.0", port=8000)


def test_create_item():
    """Test the create item endpoint."""
    response = client.post(
        "/api/items", params={"name": "New Item", "description": "A new item"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 999
    assert data["name"] == "New Item"
    assert data["description"] == "A new item"
    assert data["created"] is True

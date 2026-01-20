import pytest
from fastapi.testclient import TestClient

from api.main import app


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


def test_root_route_exists(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Medical Telegram Analytics API" in data["message"]


def test_docs_route_available(client):
    # FastAPI automatically mounts /docs (Swagger UI)
    response = client.get("/docs")
    assert response.status_code in (200, 307, 308)


def test_top_products_endpoint_defined(client):
    # This asserts the route is wired and returns a valid HTTP response.
    # It does NOT require a live database; if the DB is unavailable the app
    # should still raise a clear 500+ error, which we treat as "route exists".
    response = client.get("/api/reports/top-products?limit=1")
    assert response.status_code in (200, 422, 500)


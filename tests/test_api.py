from fastapi.testclient import TestClient

from app.api import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_search_requires_query():
    response = client.get("/news/search")

    assert response.status_code == 422


def test_news_not_found():
    response = client.get("/news/test-id")

    assert response.status_code == 404
    assert response.json() == {"detail": "News item not found"}
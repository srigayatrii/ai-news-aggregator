from unittest.mock import patch

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


def test_get_news():
    mock_digest = {
        "id": "test-id",
        "title": "Test News",
        "summary": "Test summary",
        "url": "https://example.com",
        "article_type": "test",
    }

    with patch("app.api.Repository") as mock_repo:
        mock_repo.return_value.get_recent_digests.return_value = [mock_digest]

        response = client.get("/news")

    assert response.status_code == 200
    assert response.json() == {
        "count": 1,
        "news": [mock_digest],
    }


def test_get_news_by_id():
    mock_digest = type(
        "Digest",
        (),
        {
            "id": "test-id",
            "title": "Test News",
            "summary": "Test summary",
            "url": "https://example.com",
            "article_type": "test",
        },
    )()

    with patch("app.api.Repository") as mock_repo:
        mock_repo.return_value.get_digest_by_id.return_value = mock_digest

        response = client.get("/news/test-id")

    assert response.status_code == 200
    assert response.json() == {
        "id": "test-id",
        "title": "Test News",
        "summary": "Test summary",
        "url": "https://example.com",
        "article_type": "test",
    }
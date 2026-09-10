from fastapi import FastAPI, HTTPException, Query
from app.database.repository import Repository

app = FastAPI(
    title="AI News Aggregator API",
    description="REST API for the AI News Aggregator backend",
    version="1.0.0",
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/news")
def get_news():
    repo = Repository()

    digests = repo.get_recent_digests(hours=24, exclude_sent=False)

    return {
        "count": len(digests),
        "news": [
            {
                "id": digest["id"],
                "title": digest["title"],
                "summary": digest["summary"],
                "url": digest["url"],
                "article_type": digest["article_type"],
            }
            for digest in digests
        ],
    }


@app.get("/news/search")
def search_news(q: str = Query(min_length=1, max_length=100)):
    repo = Repository()

    digests = repo.search_digests(q)

    return {
        "query": q,
        "count": len(digests),
        "news": [
            {
                "id": digest.id,
                "title": digest.title,
                "summary": digest.summary,
                "url": digest.url,
                "article_type": digest.article_type,
            }
            for digest in digests
        ],
    }


@app.get("/news/{digest_id}")
def get_news_by_id(digest_id: str):
    repo = Repository()

    digest = repo.get_digest_by_id(digest_id)

    if digest is None:
        raise HTTPException(status_code=404, detail="News item not found")

    return {
        "id": digest.id,
        "title": digest.title,
        "summary": digest.summary,
        "url": digest.url,
        "article_type": digest.article_type,
    }

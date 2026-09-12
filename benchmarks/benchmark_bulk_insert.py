import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import statistics
import time
from datetime import datetime, timezone

from app.database.connection import get_session
from app.database.models import YouTubeVideo


def generate_videos(n):
    return [
        {
            "video_id": f"benchmark-{i}",
            "title": f"Benchmark Video {i}",
            "url": f"https://example.com/{i}",
            "channel_id": "benchmark-channel",
            "published_at": datetime.now(timezone.utc),
            "description": "Benchmark record",
            "transcript": "Benchmark transcript",
        }
        for i in range(n)
    ]


def old_bulk_insert(session, items):
    """Original implementation: one existence query per item."""
    new_items = []

    for item in items:
        existing = (
            session.query(YouTubeVideo)
            .filter_by(video_id=item["video_id"])
            .first()
        )

        if not existing:
            new_items.append(YouTubeVideo(**item))

    if new_items:
        session.add_all(new_items)
        session.commit()

    return len(new_items)


def optimized_bulk_insert(session, items):
    """Current optimized implementation."""
    item_ids = [item["video_id"] for item in items]

    existing_ids = {
        row[0]
        for row in (
            session.query(YouTubeVideo.video_id)
            .filter(YouTubeVideo.video_id.in_(item_ids))
            .all()
        )
    }

    new_items = [
        YouTubeVideo(**item)
        for item in items
        if item["video_id"] not in existing_ids
    ]

    if new_items:
        session.add_all(new_items)
        session.commit()

    return len(new_items)


def benchmark(function, items, runs=3):
    times = []

    for _ in range(runs):
        session = get_session()

        # Clean benchmark records before each run.
        session.query(YouTubeVideo).filter(
            YouTubeVideo.video_id.like("benchmark-%")
        ).delete(synchronize_session=False)
        session.commit()

        start = time.perf_counter()
        inserted = function(session, items)
        elapsed = time.perf_counter() - start

        times.append(elapsed * 1000)
        session.close()

    return inserted, statistics.median(times)


def main():
    for n in [1000, 5000, 10000]:
        items = generate_videos(n)

        old_inserted, old_ms = benchmark(old_bulk_insert, items)
        new_inserted, new_ms = benchmark(optimized_bulk_insert, items)

        improvement = ((old_ms - new_ms) / old_ms) * 100

        print(f"\n{n:,} records")
        print(f"Old:       {old_ms:.2f} ms")
        print(f"Optimized: {new_ms:.2f} ms")
        print(f"Improvement: {improvement:.2f}%")
        print(f"Inserted: {new_inserted}")


if __name__ == "__main__":
    main()
from __future__ import annotations

from ..models import NewsItem
from ..utils import feed_entries_to_items, first_working_feed_url


def scrape_the_batch(limit: int = 50) -> list[NewsItem]:
    candidates = [
        "https://www.deeplearning.ai/the-batch/feed/",
        "https://www.deeplearning.ai/the-batch/rss/",
        "https://www.deeplearning.ai/the-batch/feed",
    ]
    feed_url = first_working_feed_url(candidates)
    return feed_entries_to_items(
        feed_url=feed_url,
        source_id="deeplearningai_the_batch",
        source_name="The Batch (DeepLearning.AI)",
        limit=limit,
    )


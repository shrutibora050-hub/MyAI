from __future__ import annotations

from ..models import NewsItem
from ..utils import feed_entries_to_items


def scrape_apple_ml(limit: int = 50) -> list[NewsItem]:
    feed_url = "https://machinelearning.apple.com/rss.xml"
    return feed_entries_to_items(
        feed_url=feed_url,
        source_id="apple_ml_research",
        source_name="Apple Machine Learning Research",
        limit=limit,
    )


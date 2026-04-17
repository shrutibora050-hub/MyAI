from __future__ import annotations

from ..models import NewsItem
from ..utils import feed_entries_to_items, first_working_feed_url


def scrape_tldr_ai(limit: int = 50) -> list[NewsItem]:
    candidates = [
        "https://tldr.tech/ai/rss",
        "https://tldr.tech/ai/feed",
        "https://tldr.tech/ai/rss.xml",
    ]
    feed_url = first_working_feed_url(candidates)
    return feed_entries_to_items(
        feed_url=feed_url,
        source_id="tldr_ai",
        source_name="TLDR AI",
        limit=limit,
    )


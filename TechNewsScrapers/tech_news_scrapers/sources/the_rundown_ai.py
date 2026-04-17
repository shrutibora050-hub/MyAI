from __future__ import annotations

from ..models import NewsItem
from ..utils import feed_entries_to_items, first_working_feed_url


def scrape_the_rundown_ai(limit: int = 50) -> list[NewsItem]:
    candidates = [
        "https://www.therundown.ai/feed",
        "https://www.therundown.ai/rss",
        "https://www.therundown.ai/rss.xml",
        "https://therundown.ai/feed",
    ]
    feed_url = first_working_feed_url(candidates)
    return feed_entries_to_items(
        feed_url=feed_url,
        source_id="the_rundown_ai",
        source_name="The Rundown AI",
        limit=limit,
    )


from __future__ import annotations

from ..models import NewsItem
from ..utils import feed_entries_to_items, first_working_feed_url


def scrape_import_ai(limit: int = 50) -> list[NewsItem]:
    candidates = [
        "https://www.importai.net/feed",
        "https://importai.net/feed",
        "https://www.importai.net/rss",
    ]
    feed_url = first_working_feed_url(candidates)
    return feed_entries_to_items(
        feed_url=feed_url,
        source_id="import_ai",
        source_name="Import AI",
        limit=limit,
    )


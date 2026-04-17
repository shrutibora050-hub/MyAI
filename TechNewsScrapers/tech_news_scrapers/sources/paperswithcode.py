from __future__ import annotations

from ..models import NewsItem
from ..utils import FeedFetchError, feed_entries_to_items, first_working_feed_url


def scrape_paperswithcode(limit: int = 50) -> list[NewsItem]:
    candidates = [
        "https://paperswithcode.com/rss",
        "https://paperswithcode.com/feeds/latest.xml",
        "https://paperswithcode.com/feed",
    ]
    feed_url = first_working_feed_url(candidates)
    try:
        return feed_entries_to_items(
            feed_url=feed_url,
            source_id="paperswithcode",
            source_name="Papers with Code",
            limit=limit,
        )
    except FeedFetchError:
        # Fall back to the chosen feed URL; bubble error for visibility.
        raise


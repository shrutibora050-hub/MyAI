from __future__ import annotations

from ..models import NewsItem
from ..utils import feed_entries_to_items


def scrape_huggingface(limit: int = 50) -> list[NewsItem]:
    feed_url = "https://huggingface.co/blog/feed.xml"
    return feed_entries_to_items(
        feed_url=feed_url,
        source_id="huggingface_blog",
        source_name="Hugging Face Blog",
        limit=limit,
    )


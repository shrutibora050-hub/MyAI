from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any, Optional


@dataclass(frozen=True)
class NewsItem:
    source_id: str
    source_name: str
    item_title: str
    item_url: str
    published_at: Optional[str]
    author: Optional[str]
    tags: str
    summary: str
    source_feed_url: str
    fetched_at: str
    raw: Optional[dict[str, Any]] = None

    def to_row(self) -> dict[str, Any]:
        row = asdict(self)
        # Avoid embedding nested JSON in CSV by default.
        row["raw"] = None
        return row


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


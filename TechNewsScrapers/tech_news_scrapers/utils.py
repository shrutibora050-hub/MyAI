from __future__ import annotations

import csv
import time
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Optional

import feedparser
import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from .models import NewsItem, now_iso


DEFAULT_HEADERS = {
    "User-Agent": "TechNewsScrapers/1.0 (+https://localhost; educational)",
    "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, text/html;q=0.9, */*;q=0.8",
}


class FeedFetchError(RuntimeError):
    pass


def try_parse_datetime(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str) and not value.strip():
        return None
    try:
        dt = date_parser.parse(str(value))
        if not dt.tzinfo:
            # Treat naive timestamps as UTC.
            dt = dt.replace(tzinfo=datetime.utcnow().astimezone().tzinfo)
        return dt.astimezone(datetime.utcnow().astimezone().tzinfo).replace(microsecond=0).isoformat()
    except Exception:
        return None


def strip_html(text: str) -> str:
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    return " ".join(soup.get_text(" ").split())


def fetch_url(url: str, timeout_s: int = 30) -> str:
    r = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout_s)
    r.raise_for_status()
    return r.text


def parse_feed(feed_url: str) -> feedparser.FeedParserDict:
    # feedparser can fetch directly, but we want consistent headers/timeouts.
    xml = fetch_url(feed_url)
    parsed = feedparser.parse(xml)
    if parsed.bozo and not parsed.entries:
        raise FeedFetchError(f"Failed to parse feed: {feed_url}")
    return parsed


def first_working_feed_url(candidates: list[str]) -> str:
    last_err: Optional[Exception] = None
    for url in candidates:
        try:
            parse_feed(url)
            return url
        except Exception as e:
            last_err = e
            continue
    raise FeedFetchError(f"No working feed URL found. Last error: {last_err}")


def feed_entries_to_items(
    *,
    feed_url: str,
    source_id: str,
    source_name: str,
    limit: int,
) -> list[NewsItem]:
    parsed = parse_feed(feed_url)
    fetched_at = now_iso()

    items: list[NewsItem] = []
    for entry in parsed.entries[: max(limit, 0)]:
        link = (entry.get("link") or "").strip()
        title = strip_html(entry.get("title", "")).strip()
        if not link or not title:
            continue

        published = (
            try_parse_datetime(entry.get("published"))
            or try_parse_datetime(entry.get("updated"))
            or None
        )

        author = entry.get("author") or entry.get("dc_creator") or None
        tags_list = []
        for t in entry.get("tags", []) or []:
            term = (t.get("term") or "").strip()
            if term:
                tags_list.append(term)
        tags = "|".join(dict.fromkeys(tags_list))  # stable de-dupe

        summary = strip_html(entry.get("summary", "") or entry.get("description", "") or "")

        items.append(
            NewsItem(
                source_id=source_id,
                source_name=source_name,
                item_title=title,
                item_url=link,
                published_at=published,
                author=str(author).strip() if author else None,
                tags=tags,
                summary=summary,
                source_feed_url=feed_url,
                fetched_at=fetched_at,
                raw=dict(entry),
            )
        )

    # De-dupe within a single feed by URL.
    uniq: dict[str, NewsItem] = {}
    for it in items:
        uniq[it.item_url] = it
    return list(uniq.values())


def write_csv(path: Path, items: Iterable[NewsItem]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    items_list = list(items)
    if not items_list:
        # Still create an empty CSV with headers.
        fieldnames = list(asdict(NewsItem("", "", "", "", None, None, "", "", "", "")).keys())
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
        return

    fieldnames = list(items_list[0].to_row().keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for item in items_list:
            w.writerow(item.to_row())


def sleep_polite(seconds: float = 0.2) -> None:
    time.sleep(seconds)


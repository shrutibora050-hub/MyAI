from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from .run import SOURCES, run


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape curated tech/AI news sources to CSV")
    parser.add_argument(
        "--sources",
        type=str,
        default="all",
        help=f"Comma-separated list: {', '.join(SOURCES.keys())}, or 'all' (default: all)",
    )
    parser.add_argument("--limit", type=int, default=50, help="Max items per source (default: 50)")
    parser.add_argument(
        "--out",
        type=str,
        default="",
        help="Output CSV path (default: output/tech_news_<timestamp>.csv)",
    )

    args = parser.parse_args()
    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_csv = Path(args.out) if args.out else Path("output") / f"tech_news_{timestamp}.csv"

    items = run(sources=sources, limit=args.limit, out_csv=out_csv)
    print(f"Wrote {len(items)} items to {out_csv}")


if __name__ == "__main__":
    main()


from __future__ import annotations

from pathlib import Path
from typing import Callable

from .models import NewsItem
from .sources import (
    scrape_apple_ml,
    scrape_deepmind,
    scrape_huggingface,
    scrape_import_ai,
    scrape_paperswithcode,
    scrape_the_batch,
    scrape_the_neuron,
    scrape_the_rundown_ai,
    scrape_tldr_ai,
)
from .utils import write_csv


ScrapeFn = Callable[[int], list[NewsItem]]


SOURCES: dict[str, tuple[str, ScrapeFn]] = {
    "huggingface": ("Hugging Face Blog", scrape_huggingface),
    "deepmind": ("Google DeepMind Blog", scrape_deepmind),
    "apple_ml": ("Apple Machine Learning Research", scrape_apple_ml),
    "paperswithcode": ("Papers with Code", scrape_paperswithcode),
    "the_batch": ("The Batch (DeepLearning.AI)", scrape_the_batch),
    "tldr_ai": ("TLDR AI", scrape_tldr_ai),
    "the_neuron": ("The Neuron", scrape_the_neuron),
    "the_rundown_ai": ("The Rundown AI", scrape_the_rundown_ai),
    "import_ai": ("Import AI", scrape_import_ai),
}


def run(*, sources: list[str], limit: int, out_csv: Path) -> list[NewsItem]:
    selected = sources
    if len(selected) == 1 and selected[0] == "all":
        selected = list(SOURCES.keys())

    all_items: list[NewsItem] = []
    for source_id in selected:
        if source_id not in SOURCES:
            raise ValueError(f"Unknown source '{source_id}'. Valid: {', '.join(SOURCES.keys())} or 'all'")
        _, fn = SOURCES[source_id]
        items = fn(limit)
        all_items.extend(items)

    # De-dupe across sources by URL.
    uniq: dict[str, NewsItem] = {}
    for it in all_items:
        uniq[it.item_url] = it
    final = list(uniq.values())

    write_csv(out_csv, final)
    return final


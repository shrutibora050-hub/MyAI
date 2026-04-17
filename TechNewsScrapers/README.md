# Tech News Scrapers

Scrapers for curated tech/AI news sources (RSS-first) with a single runner that exports results to CSV.

## Sources

- Hugging Face Blog
- Google AI / DeepMind Blog
- Apple Machine Learning Research
- Papers with Code
- The Batch (DeepLearning.AI)
- TLDR AI
- The Neuron
- The Rundown AI
- Import AI

## Quick start

```bash
cd TechNewsScrapers
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# scrape everything to a single CSV
python -m tech_news_scrapers --sources all --limit 50
```

## Output

By default, CSVs are written to `TechNewsScrapers/output/`:

- `tech_news_<timestamp>.csv`

Each row is one post/newsletter issue.

## Notes

- RSS is preferred for reliability (fewer broken selectors).
- Some newsletters may change feed URLs over time; each scraper tries a small list of known candidates.


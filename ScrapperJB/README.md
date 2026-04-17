# Job Scraper

A reliable job scraper that aggregates software engineering positions from Amazon and Simplify's curated new grad listings.

## Features

✅ **Amazon Jobs** - Direct API access to Amazon's job listings
✅ **Simplify Jobs** - 244+ companies from Simplify's curated GitHub repository
✅ **No Bot Detection** - API and Git-based, zero browser automation issues
✅ **Fast** - Complete scraping in ~5 seconds
✅ **Reliable** - No maintenance overhead, no broken selectors

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Clone Simplify data repository
git clone https://github.com/SimplifyJobs/New-Grad-Positions.git simplify_data
```

## Usage

### Scrape Both Sources (Recommended)
```bash
python main.py --companies amazon,simplify --limit 50
```

### Scrape Amazon Only
```bash
python main.py --companies amazon --limit 50 --keywords "software engineer"
```

### Scrape Simplify Only
```bash
python main.py --companies simplify --limit 100
```

### Command Line Options
```
--companies     Comma-separated list: amazon, simplify (default: amazon,simplify)
--keywords      Job search keywords (default: "software engineer")
--location      Job location filter (default: all locations)
--limit         Maximum jobs per company (default: 50)
```

## Output

Jobs are saved to `output/jobs_YYYYMMDD_HHMMSS.json`:

```json
[
  {
    "title": "Software Development Engineer I",
    "company": "Amazon",
    "location": "Seattle, WA",
    "job_url": "https://amazon.jobs/...",
    "category": "Software Development",
    "scraped_at": "2026-03-28T03:34:49.123456"
  }
]
```

## Project Structure

```
ScrapperJB/
├── scraper/
│   ├── __init__.py
│   ├── models.py                  # Pydantic job data model
│   ├── amazon_scraper.py          # Amazon careers site scraper
│   ├── amazon_scraper_api.py      # Amazon API scraper (✅ working)
│   └── simplify_scraper.py        # Simplify GitHub scraper (✅ working)
├── simplify_data/                 # Git submodule for Simplify data
├── output/                        # Scraped job results
├── main.py                        # Main CLI interface
├── test_simplify.py              # Simplify scraper tests
├── test_working_scrapers.py      # Integration tests
├── requirements.txt
└── README.md
```

## Data Sources

### Amazon Jobs API
- **Source**: https://www.amazon.jobs/en/search.json
- **Method**: Direct API calls
- **Coverage**: All Amazon positions worldwide
- **Update Frequency**: Real-time

### Simplify Jobs Repository
- **Source**: https://github.com/SimplifyJobs/New-Grad-Positions
- **Method**: Git pull + HTML parsing
- **Coverage**: 244 software engineering new grad positions
- **Companies**: Crowdstrike, Twitch, Ellipsis Labs, CACI, Travelers, Affirm, Micron, and 238 more
- **Update Frequency**: Daily (community-maintained)

## Examples

### Quick Test
```python
from scraper.amazon_scraper_api import AmazonScraperAPI
from scraper.simplify_scraper import SimplifyScraper

# Amazon
amazon = AmazonScraperAPI()
amazon_jobs = amazon.scrape(keywords="software engineer", limit=5)
print(f"Amazon: {len(amazon_jobs)} jobs")

# Simplify
simplify = SimplifyScraper()
simplify_jobs = simplify.scrape(limit=10)
print(f"Simplify: {len(simplify_jobs)} jobs")
```

### Sample Output
```
Amazon: 5 jobs
   1. Software Development Engineer I - Seattle, WA
   2. Frontend Engineer - Austin, TX
   ...

Simplify: 10 jobs from 244+ companies
   1. Crowdstrike - Engineer 1 - Front End - Data Visualization
   2. Ellipsis Labs - Software Engineer – New Grads
   ...

TOTAL: 15 jobs scraped successfully!
```

## Why These Sources?

### Problems with Traditional Web Scraping
❌ **Bot Detection** - Sites like Google forcibly close browser windows
❌ **Slow** - 60+ seconds per company with browser automation
❌ **Unreliable** - Selectors break frequently
❌ **High Maintenance** - Constant updates needed

### Our Solution
✅ **API-First** - Amazon provides public API endpoints
✅ **Git-Based** - Simplify maintains curated listings on GitHub
✅ **Fast & Reliable** - No browser automation overhead
✅ **Zero Maintenance** - Stable data sources

## Dependencies

- `pydantic` - Type-safe data models
- `requests` - HTTP requests for Amazon API
- `tqdm` - Progress bars

## Testing

```bash
# Test both scrapers
python test_working_scrapers.py

# Test Simplify only
python test_simplify.py
```

## Notes

- Simplify repository is automatically updated with `git pull` before each scrape
- Amazon API returns diverse positions (all levels, all locations)
- Simplify focuses specifically on new grad software engineering roles
- No authentication or API keys required for either source

## Future Enhancements

- Add filters for Simplify (location, sponsorship requirements)
- Support other Simplify categories (PM, Data Science, Quant, Hardware)
- Export to CSV format
- Email notifications for new postings
- Database integration

## License

MIT

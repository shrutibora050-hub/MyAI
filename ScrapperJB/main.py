import json
import logging
import os
from datetime import datetime
from pathlib import Path
from tqdm import tqdm
from scraper.amazon_scraper_api import AmazonScraperAPI
from scraper.simplify_scraper import SimplifyScraper
from scraper.db import JobDatabase

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


SCRAPERS = {
    'amazon': 'api',
    'simplify': 'git'
}


def scrape_company(company: str, keywords: str = "", location: str = "", limit: int = 50):
    if company.lower() == 'simplify':
        try:
            scraper = SimplifyScraper()
            jobs = scraper.scrape(limit=limit)
            logger.info(f"Scraped {len(jobs)} jobs from Simplify")
            return jobs
        except Exception as e:
            logger.error(f"Failed to scrape Simplify: {e}")
            return []

    elif company.lower() == 'amazon':
        try:
            scraper = AmazonScraperAPI()
            jobs = scraper.scrape(keywords=keywords, location=location, limit=limit)
            logger.info(f"Scraped {len(jobs)} jobs from Amazon")
            return jobs
        except Exception as e:
            logger.error(f"Failed to scrape Amazon: {e}")
            return []

    else:
        logger.error(f"Unknown company: {company}. Available: amazon, simplify")
        return []


def scrape_all_companies(keywords: str = "", location: str = "", limit: int = 50):
    all_jobs = []
    companies = list(SCRAPERS.keys())

    for company_name in tqdm(companies, desc="Scraping companies", unit="company"):
        jobs = scrape_company(company_name, keywords, location, limit)
        all_jobs.extend(jobs)
        tqdm.write(f"✓ {company_name.upper()}: {len(jobs)} jobs")

    return all_jobs


def save_results(jobs, filename=None):
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"jobs_{timestamp}.json"

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    filepath = output_dir / filename

    jobs_dict = [job.model_dump() for job in jobs]

    with open(filepath, 'w') as f:
        json.dump(jobs_dict, f, indent=2, default=str)

    logger.info(f"Saved {len(jobs)} jobs to {filepath}")
    return filepath


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Job Scraper for Amazon and Simplify')
    parser.add_argument('--companies', type=str, default='amazon,simplify',
                        help='Comma-separated list of companies (amazon, simplify)')
    parser.add_argument('--keywords', type=str, default='software engineer',
                        help='Job keywords to search')
    parser.add_argument('--location', type=str, default='',
                        help='Job location')
    parser.add_argument('--limit', type=int, default=50,
                        help='Maximum jobs per company')
    parser.add_argument('--save-to', type=str, default='both', choices=['db', 'file', 'both'],
                        help='Where to save results: db, file, or both')

    args = parser.parse_args()

    companies = [c.strip().lower() for c in args.companies.split(',')]

    print(f"\n{'='*60}")
    print(f"Job Scraper")
    print(f"{'='*60}")
    print(f"Companies: {', '.join(companies)}")
    print(f"Keywords: {args.keywords or 'All'}")
    print(f"Location: {args.location or 'All'}")
    print(f"Limit per company: {args.limit}")
    print(f"{'='*60}\n")

    all_jobs = []
    for company in tqdm(companies, desc="Scraping", unit="company"):
        jobs = scrape_company(company, args.keywords, args.location, args.limit)
        all_jobs.extend(jobs)
        tqdm.write(f"✓ {company.upper()}: {len(jobs)} jobs")

    print(f"\n{'='*60}")
    print(f"SCRAPING COMPLETE")
    print(f"{'='*60}")
    print(f"Total jobs scraped: {len(all_jobs)}")

    if all_jobs:
        # Save to file
        if args.save_to in ['file', 'both']:
            filepath = save_results(all_jobs)
            print(f"Results saved to file: {filepath}")

        # Save to database
        if args.save_to in ['db', 'both']:
            db_url = os.getenv('DATABASE_URL', 'postgresql://scraper:scraper_password@localhost:5432/jobs_db')
            try:
                db = JobDatabase(db_url)
                db.connect()
                saved_count = db.save_jobs(all_jobs)
                total_count = db.get_job_count()
                db.close()
                print(f"Saved {saved_count} new jobs to database (total: {total_count})")
            except Exception as e:
                print(f"Failed to save to database: {e}")
    print(f"{'='*60}\n")

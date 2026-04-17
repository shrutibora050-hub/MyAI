from scraper.simplify_scraper import SimplifyScraper
import logging

logging.basicConfig(level=logging.INFO)

print("="*70)
print("Testing Simplify Jobs Scraper")
print("="*70)

try:
    scraper = SimplifyScraper()
    jobs = scraper.scrape(limit=10)

    print(f"\n✓ Found {len(jobs)} jobs from Simplify")
    print("\nFirst 10 jobs:")
    print("-"*70)

    for idx, job in enumerate(jobs, 1):
        print(f"\n{idx}. {job.company}")
        print(f"   Role: {job.title}")
        print(f"   Location: {job.location}")
        print(f"   URL: {job.job_url[:80]}...")

    print("\n" + "="*70)
    print("Test Complete!")
    print("="*70)

except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()

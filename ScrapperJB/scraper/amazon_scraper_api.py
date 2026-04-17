from typing import List
from scraper.models import JobPosting
import requests
import logging

logger = logging.getLogger(__name__)


class AmazonScraperAPI:
    BASE_URL = "https://www.amazon.jobs/en/search.json"

    @property
    def company_name(self) -> str:
        return "Amazon"

    def scrape(self, keywords: str = "", location: str = "", limit: int = 50) -> List[JobPosting]:
        jobs = []

        params = {
            'offset': 0,
            'result_limit': min(limit, 100),
            'sort': 'relevant',
            'category[]': 'software-development'
        }

        if keywords:
            params['q'] = keywords
        if location:
            params['loc_query'] = location

        try:
            logger.info(f"Fetching Amazon jobs via API: {self.BASE_URL}")
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            job_list = data.get('jobs', [])

            logger.info(f"Found {len(job_list)} jobs from API")

            for job_data in job_list[:limit]:
                try:
                    job = self._parse_job(job_data)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.error(f"Error parsing job: {e}")
                    continue

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch Amazon jobs: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

        return jobs

    def _parse_job(self, job_data: dict) -> JobPosting:
        title = job_data.get('title', 'Unknown')

        job_id = job_data.get('id_icims', '')
        job_url = f"https://www.amazon.jobs/en/jobs/{job_id}" if job_id else ""

        location_parts = []
        city = job_data.get('city', '')
        state = job_data.get('state', '')
        country = job_data.get('country', '')

        if city:
            location_parts.append(city)
        if state:
            location_parts.append(state)
        if country:
            location_parts.append(country)

        location = ', '.join(location_parts) if location_parts else "Not specified"

        description = job_data.get('description', '')
        category = job_data.get('job_category', '')
        posted_date = job_data.get('posted_date', '')
        job_type = job_data.get('job_schedule_type', '')

        return JobPosting(
            title=title,
            company=self.company_name,
            location=location,
            job_url=job_url,
            description=description,
            category=category,
            posted_date=posted_date,
            job_type=job_type
        )

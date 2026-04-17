from typing import List
import subprocess
import os
import re
from scraper.models import JobPosting
import logging

logger = logging.getLogger(__name__)


class SimplifyScraper:
    REPO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "simplify_data")
    README_PATH = os.path.join(REPO_PATH, "README.md")

    @property
    def company_name(self) -> str:
        return "Simplify (Aggregated)"

    def scrape(self, limit: int = 100, update_repo: bool = True) -> List[JobPosting]:
        jobs = []

        if update_repo:
            self._update_repository()

        logger.info(f"Reading Simplify jobs from local repo: {self.README_PATH}")

        try:
            with open(self.README_PATH, 'r', encoding='utf-8') as f:
                markdown_content = f.read()

            jobs = self._parse_markdown_table(markdown_content, limit)
            logger.info(f"Found {len(jobs)} jobs from Simplify")

        except Exception as e:
            logger.error(f"Failed to read Simplify jobs: {e}")

        return jobs

    def _update_repository(self):
        try:
            if os.path.exists(self.REPO_PATH):
                logger.info("Pulling latest job listings from GitHub...")
                subprocess.run(
                    ["git", "pull"],
                    cwd=self.REPO_PATH,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                logger.info("Repository updated")
            else:
                logger.warning(f"Repository not found at {self.REPO_PATH}")
        except Exception as e:
            logger.warning(f"Failed to update repository: {e}")

    def _parse_markdown_table(self, markdown: str, limit: int) -> List[JobPosting]:
        jobs = []

        # Find all <tr> tags in the HTML table
        tr_pattern = r'<tr>(.*?)</tr>'
        rows = re.findall(tr_pattern, markdown, re.DOTALL)

        for row in rows:
            # Skip header rows (contain <th> tags)
            if '<th' in row:
                continue

            job = self._parse_html_row(row)
            if job:
                jobs.append(job)
                if len(jobs) >= limit:
                    break

        return jobs

    def _parse_html_row(self, row: str) -> JobPosting:
        try:
            # Extract <td> cells from HTML row
            td_pattern = r'<td[^>]*>(.*?)</td>'
            cells = re.findall(td_pattern, row, re.DOTALL)

            # Expected format: Company | Role | Location | Application | Age
            if len(cells) < 4:
                return None

            company_cell = cells[0]
            role_cell = cells[1]
            location_cell = cells[2]
            application_cell = cells[3]

            # Skip rows with ↳ (continuation marker)
            if '↳' in company_cell:
                return None

            # Extract company name (remove HTML tags and emojis)
            company = self._clean_html_text(company_cell)

            # Extract role (clean HTML)
            role = self._clean_html_text(role_cell)

            # Extract location (clean HTML, handle <br> tags)
            location = self._clean_html_text(location_cell)

            # Extract application URL
            job_url = self._extract_url_from_html(application_cell)

            # Skip if essential fields are missing
            if not company or not role or not job_url:
                return None

            return JobPosting(
                title=role,
                company=company,
                location=location if location else "Not specified",
                job_url=job_url,
                category="New Grad - Software Engineering"
            )

        except Exception as e:
            logger.warning(f"Failed to parse row: {e}")
            return None

    def _clean_html_text(self, html: str) -> str:
        # Remove all HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        # Replace HTML entities
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        # Remove emojis and special markers
        text = re.sub(r'[🔥🛂🇺🇸↔️]', '', text)
        # Replace <br> with comma + space for locations
        text = text.replace('</br>', ', ')
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()

    def _extract_url_from_html(self, html: str) -> str:
        # Extract href from <a> tag
        href_match = re.search(r'href="([^"]+)"', html)
        if href_match:
            url = href_match.group(1)
            # Skip Simplify referral links, get the actual job URL
            if 'utm_source=Simplify' in url or 'ref=Simplify' in url:
                # This is the direct application link
                return url
            return url

        # Fallback: find any URL in the text
        url_match = re.search(r'https?://[^\s<>"{}|\\^`\[\]]+', html)
        if url_match:
            return url_match.group(0)

        return ""

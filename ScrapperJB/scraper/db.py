import psycopg2
from psycopg2.extras import execute_values
from typing import List
import logging
from scraper.models import JobPosting

logger = logging.getLogger(__name__)


class JobDatabase:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.conn = None

    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(self.connection_string)
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def save_jobs(self, jobs: List[JobPosting]) -> int:
        """Save jobs to database, skip duplicates based on job_url"""
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        saved_count = 0

        try:
            # Prepare data for batch insert
            job_data = [
                (
                    job.title,
                    job.company,
                    job.location,
                    job.job_url,
                    job.description,
                    job.job_type,
                    job.category,
                    job.posted_date,
                    job.scraped_at
                )
                for job in jobs
            ]

            # Insert with ON CONFLICT DO NOTHING (skip duplicates)
            insert_query = """
                INSERT INTO jobs (
                    title, company, location, job_url, description,
                    job_type, category, posted_date, scraped_at
                )
                VALUES %s
                ON CONFLICT (job_url) DO NOTHING
            """

            execute_values(cursor, insert_query, job_data)
            saved_count = cursor.rowcount
            self.conn.commit()

            logger.info(f"Saved {saved_count} new jobs to database (skipped {len(jobs) - saved_count} duplicates)")

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to save jobs to database: {e}")
            raise
        finally:
            cursor.close()

        return saved_count

    def get_job_count(self) -> int:
        """Get total number of jobs in database"""
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM jobs")
        count = cursor.fetchone()[0]
        cursor.close()
        return count

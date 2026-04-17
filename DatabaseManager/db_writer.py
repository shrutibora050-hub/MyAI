import psycopg2
from psycopg2.extras import execute_values
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DatabaseWriter:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.conn = None

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.connection_string)
            logger.info("✓ Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"✗ Failed to connect to database: {e}")
            raise

    def batch_insert_jobs(self, jobs: List[Dict[str, Any]]) -> int:
        """
        Batch insert jobs into database

        Args:
            jobs: List of job dictionaries

        Returns:
            Number of jobs inserted
        """
        if not self.conn:
            self.connect()

        cursor = self.conn.cursor()
        saved_count = 0

        try:
            # Prepare job data tuples
            job_data = [
                (
                    job.get('title'),
                    job.get('company'),
                    job.get('location'),
                    job.get('job_url'),
                    job.get('description'),
                    job.get('job_type'),
                    job.get('category'),
                    job.get('posted_date'),
                    job.get('source'),
                    job.get('scraped_at')
                )
                for job in jobs
            ]

            insert_query = """
                INSERT INTO jobs (
                    title, company, location, job_url, description,
                    job_type, category, posted_date, source, scraped_at
                )
                VALUES %s
                ON CONFLICT (job_url) DO NOTHING
            """

            execute_values(cursor, insert_query, job_data)
            saved_count = cursor.rowcount
            self.conn.commit()

            logger.info(f"✓ Saved {saved_count} new jobs to database (out of {len(jobs)} total)")

        except Exception as e:
            self.conn.rollback()
            logger.error(f"✗ Failed to save jobs to database: {e}")
            raise
        finally:
            cursor.close()

        return saved_count

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

import pika
import json
import logging
from datetime import datetime
from typing import List

logger = logging.getLogger(__name__)


class JobQueuePublisher:
    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url
        self.connection = None
        self.channel = None

    def connect(self):
        """Connect to RabbitMQ with retry logic"""
        try:
            logger.info("Connecting to RabbitMQ...")
            self.connection = pika.BlockingConnection(
                pika.URLParameters(self.rabbitmq_url)
            )
            self.channel = self.connection.channel()

            # Declare exchange (idempotent)
            self.channel.exchange_declare(
                exchange='jobs',
                exchange_type='topic',
                durable=True
            )

            logger.info("✓ Connected to RabbitMQ successfully")
            return True

        except Exception as e:
            logger.error(f"✗ Failed to connect to RabbitMQ: {e}")
            return False

    def publish_jobs(self, jobs: List, source: str) -> bool:
        """
        Publish scraped jobs to RabbitMQ

        Args:
            jobs: List of job objects (Pydantic models)
            source: Source of jobs ('amazon', 'simplify', etc.)

        Returns:
            True if successful, False otherwise
        """
        if not self.connection or self.connection.is_closed:
            if not self.connect():
                return False

        try:
            # Convert Pydantic models to dictionaries
            jobs_data = [job.model_dump() for job in jobs]

            # Create event message
            event = {
                'event_type': 'jobs.scraped',
                'source': source,
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'jobs': jobs_data,
                    'count': len(jobs_data)
                }
            }

            # Publish to exchange with routing key
            routing_key = f'jobs.scraped.{source.lower()}'

            self.channel.basic_publish(
                exchange='jobs',
                routing_key=routing_key,
                body=json.dumps(event, default=str),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type='application/json'
                )
            )

            logger.info(f"✓ Published {len(jobs_data)} jobs from {source} to RabbitMQ")
            return True

        except Exception as e:
            logger.error(f"✗ Failed to publish jobs to RabbitMQ: {e}")
            return False

    def close(self):
        """Close RabbitMQ connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ connection closed")

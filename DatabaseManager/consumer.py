import pika
import json
import os
import logging
import time
from db_writer import DatabaseWriter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JobConsumer:
    def __init__(self, rabbitmq_url: str, database_url: str):
        self.rabbitmq_url = rabbitmq_url
        self.db_writer = DatabaseWriter(database_url)
        self.connection = None
        self.channel = None

    def connect(self):
        """Connect to RabbitMQ with retry logic"""
        max_retries = 5
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                logger.info(f"Connecting to RabbitMQ (attempt {attempt + 1}/{max_retries})...")
                self.connection = pika.BlockingConnection(
                    pika.URLParameters(self.rabbitmq_url)
                )
                self.channel = self.connection.channel()

                # Declare exchange
                self.channel.exchange_declare(
                    exchange='jobs',
                    exchange_type='topic',
                    durable=True
                )

                # Declare queue
                self.channel.queue_declare(
                    queue='jobs.scraped.queue',
                    durable=True
                )

                # Bind queue to exchange
                self.channel.queue_bind(
                    exchange='jobs',
                    queue='jobs.scraped.queue',
                    routing_key='jobs.scraped.*'
                )

                # Set QoS - process 10 messages at a time
                self.channel.basic_qos(prefetch_count=10)

                logger.info("✓ Connected to RabbitMQ successfully")
                return

            except Exception as e:
                logger.error(f"✗ Failed to connect to RabbitMQ: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    raise

    def process_message(self, ch, method, properties, body):
        """Process incoming job scraping event"""
        try:
            # Parse message
            event_data = json.loads(body)
            logger.info(f"📩 Received event: {event_data.get('event_type', 'unknown')}")

            # Extract jobs from event
            jobs = event_data.get('data', {}).get('jobs', [])
            source = event_data.get('source', 'unknown')

            if not jobs:
                logger.warning("⚠️  No jobs in event data")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            # Save jobs to database
            saved_count = self.db_writer.batch_insert_jobs(jobs)

            logger.info(f"✓ Processed {len(jobs)} jobs from {source} ({saved_count} new)")

            # Acknowledge message
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except json.JSONDecodeError as e:
            logger.error(f"✗ Invalid JSON in message: {e}")
            # Reject and don't requeue - bad message
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        except Exception as e:
            logger.error(f"✗ Error processing message: {e}")
            # Reject and requeue - temporary error
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start(self):
        """Start consuming messages"""
        try:
            # Connect to RabbitMQ
            self.connect()

            # Connect to database
            self.db_writer.connect()

            logger.info("🚀 DatabaseManager started. Waiting for messages...")
            logger.info("   Queue: jobs.scraped.queue")
            logger.info("   Routing key: jobs.scraped.*")
            logger.info("=" * 60)

            # Start consuming
            self.channel.basic_consume(
                queue='jobs.scraped.queue',
                on_message_callback=self.process_message
            )

            self.channel.start_consuming()

        except KeyboardInterrupt:
            logger.info("\n⏹  Shutting down gracefully...")
            self.stop()

        except Exception as e:
            logger.error(f"✗ Fatal error: {e}")
            raise

    def stop(self):
        """Stop consuming and close connections"""
        if self.channel:
            self.channel.stop_consuming()
        if self.connection:
            self.connection.close()
        if self.db_writer:
            self.db_writer.close()
        logger.info("✓ DatabaseManager stopped")


if __name__ == "__main__":
    rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://jobqueue:jobqueue_password@localhost:5672/')
    database_url = os.getenv('DATABASE_URL', 'postgresql://scraper:scraper_password@localhost:5432/jobs_db')

    consumer = JobConsumer(rabbitmq_url, database_url)
    consumer.start()

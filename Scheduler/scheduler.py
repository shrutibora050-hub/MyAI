import schedule
import time
import subprocess
import logging
import os
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks
from threading import Thread
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SCRAPER_PATH = "../ScrapperJB"

app = FastAPI()

def run_scraper():
    """Run the job scraper"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Starting scraper job at {timestamp}")

    # Get RabbitMQ URL from environment variable
    rabbitmq_url = os.getenv('RABBITMQ_URL', 'amqp://jobqueue:jobqueue_password@job-rabbitmq:5672/')

    try:
        result = subprocess.run(
            ["docker", "run", "--rm",
             "--network", "database_default",
             "-e", f"RABBITMQ_URL={rabbitmq_url}",
             "job-scraper",
             "python", "main.py",
             "--companies", "amazon,simplify",
             "--limit", "100",
             "--save-to", "queue"],
            capture_output=True,
            text=True,
            timeout=600
        )

        if result.returncode == 0:
            logger.info(f"✓ Scraper completed successfully")
            logger.info(result.stdout)
            return {"status": "success", "output": result.stdout}
        else:
            logger.error(f"✗ Scraper failed with code {result.returncode}")
            logger.error(result.stderr)
            return {"status": "error", "error": result.stderr}

    except subprocess.TimeoutExpired:
        logger.error("✗ Scraper timed out after 10 minutes")
        return {"status": "error", "error": "Timeout"}
    except Exception as e:
        logger.error(f"✗ Error running scraper: {e}")
        return {"status": "error", "error": str(e)}

# API Endpoints
@app.get("/")
def root():
    return {
        "service": "Job Scraper Scheduler",
        "schedule": "5 times daily (00:00, 05:00, 10:00, 15:00, 20:00 UTC)",
        "trigger_endpoint": "/trigger"
    }

@app.post("/trigger")
def trigger_scraper(background_tasks: BackgroundTasks):
    """Trigger scraper immediately via API"""
    background_tasks.add_task(run_scraper)
    return {
        "status": "triggered",
        "message": "Scraper job started in background",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

# Schedule jobs - 5 times a day
schedule.every().day.at("00:00").do(run_scraper)
schedule.every().day.at("05:00").do(run_scraper)
schedule.every().day.at("10:00").do(run_scraper)
schedule.every().day.at("15:00").do(run_scraper)
schedule.every().day.at("20:00").do(run_scraper)

def run_scheduler():
    """Run scheduled jobs in background thread"""
    logger.info("Scheduler started - running 5 times daily")
    logger.info("Schedule: 00:00, 05:00, 10:00, 15:00, 20:00 UTC")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    # Start scheduler in background thread
    scheduler_thread = Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()

    # Start API server
    logger.info("API server starting on port 8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)

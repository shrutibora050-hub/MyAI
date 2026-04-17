# Job Scraper Scheduler

Super lightweight scheduler with cron + API trigger options.

## Features

✅ **Scheduled** - Runs 5 times daily automatically
✅ **API Triggered** - Manual trigger via HTTP endpoint
✅ **Lightweight** - ~80MB image, ~30MB RAM

## Schedule

Runs at:
- 00:00 UTC (Midnight)
- 05:00 UTC (5 AM)
- 10:00 UTC (10 AM)
- 15:00 UTC (3 PM)
- 20:00 UTC (8 PM)

## Setup

```bash
cd "/Users/shruti/Documents/Projects/Personal Projects/MyAI/Scheduler"
docker-compose up --build -d
```

## API Endpoints

### Trigger Scraper Immediately
```bash
curl -X POST http://localhost:8001/trigger
```

Response:
```json
{
  "status": "triggered",
  "message": "Scraper job started in background",
  "timestamp": "2026-04-08T03:30:00"
}
```

### Health Check
```bash
curl http://localhost:8001/health
```

### Info
```bash
curl http://localhost:8001/
```

## Check Logs

```bash
docker logs -f job-scheduler
```

## Stop

```bash
docker-compose down
```

## How It Works

1. Scheduler runs 24/7 with API server + background cron
2. Cron triggers scraper 5x daily automatically
3. API allows manual triggers anytime
4. Scraper runs in separate container, saves results, exits

## Size

- Image: ~80MB (Alpine + Python + FastAPI + schedule)
- Memory: ~30MB
- CPU: Minimal (sleeps between checks)

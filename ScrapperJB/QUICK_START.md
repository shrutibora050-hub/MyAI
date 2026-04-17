# Quick Start - Job Scraper Docker

## Prerequisites

Install Docker Desktop:
- Mac: https://www.docker.com/products/docker-desktop
- Windows: https://www.docker.com/products/docker-desktop
- Linux: `sudo apt install docker.io docker-compose` (Ubuntu/Debian)

## 1. Build Image (One-Time)

```bash
cd "/Users/shruti/Documents/Projects/Personal Projects/ScrapperJB"
docker build -t job-scraper .
```

**Expected output:**
```
[+] Building 45.2s (12/12) FINISHED
 => [1/7] FROM python:3.12-alpine
 => [2/7] WORKDIR /app
 => [3/7] RUN apk add --no-cache git
 => [4/7] COPY requirements.txt .
 => [5/7] RUN pip install --no-cache-dir -r requirements.txt
 => [6/7] COPY scraper/ ./scraper/
 => [7/7] COPY main.py .
 => [8/7] RUN git clone --depth 1 https://github.com/SimplifyJobs/New-Grad-Positions.git simplify_data
 => [9/7] RUN mkdir -p output
 => exporting to image
Successfully tagged job-scraper:latest
```

**Build time:** ~30-60 seconds (first time)
**Image size:** ~106MB

## 2. Run Scraper

### Quick Run
```bash
docker run --rm -v "$(pwd)/output:/app/output" job-scraper
```

### Check Results
```bash
ls -lh output/
# Shows: jobs_YYYYMMDD_HHMMSS.json
```

### View Results
```bash
cat output/jobs_*.json | head -50
```

## 3. Custom Options

### Simplify Only (100 jobs)
```bash
docker run --rm -v "$(pwd)/output:/app/output" job-scraper \
  python main.py --companies simplify --limit 100
```

### Amazon Only (50 jobs, specific keywords)
```bash
docker run --rm -v "$(pwd)/output:/app/output" job-scraper \
  python main.py --companies amazon --keywords "python developer" --limit 50
```

### Both Sources (20 jobs each)
```bash
docker run --rm -v "$(pwd)/output:/app/output" job-scraper \
  python main.py --companies amazon,simplify --limit 20
```

## 4. Using Docker Compose (Easier)

### Run Once
```bash
docker-compose up
```

### Custom Command
```bash
docker-compose run --rm scraper python main.py --companies simplify --limit 200
```

## Flags Explained

- `--rm` = Remove container after run (cleanup)
- `-v` = Mount volume (save output to host)
- `$(pwd)` = Current directory
- `job-scraper` = Image name

## Troubleshooting

### Docker not running?
```bash
# Mac: Open Docker Desktop
# Linux: sudo systemctl start docker
```

### Permission denied?
```bash
# Linux only
sudo usermod -aG docker $USER
# Log out and back in
```

### Image too large?
```bash
# Check image size
docker images job-scraper

# Should be ~106MB
# If larger, rebuild with --no-cache
docker build --no-cache -t job-scraper .
```

### Can't find output?
```bash
# Make sure you're in the project directory
cd "/Users/shruti/Documents/Projects/Personal Projects/ScrapperJB"

# Check mount is working
docker run --rm -v "$(pwd)/output:/app/output" job-scraper ls -la /app/output
```

## Daily Automation

### Mac/Linux Cron
```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 9 AM)
0 9 * * * cd /path/to/ScrapperJB && docker run --rm -v "$(pwd)/output:/app/output" job-scraper
```

### Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily, 9:00 AM
4. Action: Start Program
5. Program: `docker`
6. Arguments: `run --rm -v C:\path\to\ScrapperJB\output:/app/output job-scraper`

## Why Docker?

✅ **Consistency** - Same environment everywhere
✅ **Isolation** - No conflicts with other Python projects
✅ **Portability** - Run on any OS with Docker
✅ **Clean** - No pip install needed on host
✅ **Simple** - One command to run

## Summary

```bash
# Build (one time)
docker build -t job-scraper .

# Run (any time)
docker run --rm -v "$(pwd)/output:/app/output" job-scraper

# Check results
ls output/
```

That's it! 🚀

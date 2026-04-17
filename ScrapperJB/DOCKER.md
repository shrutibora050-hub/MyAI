# Docker Setup - Job Scraper

## Design Choices

### 1. **Base Image: `python:3.12-alpine`**
   - **Why Alpine?**
     - Tiny base image (~5MB vs ~130MB for standard Python)
     - Security: Minimal attack surface, fewer packages
     - Speed: Faster builds and deploys
   - **Why Python 3.12?**
     - Latest stable version with performance improvements
     - Compatible with all dependencies

### 2. **Single-Stage Build**
   - No multi-stage build needed (no compilation, no build tools)
   - Simple dependencies: just pydantic, requests, tqdm
   - Keeps Dockerfile minimal and readable

### 3. **Layer Optimization**
   - Copy `requirements.txt` first (Docker caching - won't reinstall if unchanged)
   - Install dependencies before copying code
   - Code changes don't trigger dependency reinstall

### 4. **Git in Container**
   - Simplify scraper needs `git pull` to update job listings
   - Alpine package: `apk add --no-cache git` (~30MB added)
   - Worth it: Enables daily updates without rebuilding image

### 5. **Volume Mount for Output**
   - Results persist on host even if container is removed
   - Easy access to scraped JSON files
   - No data loss

## Quick Start

### Build & Run (Docker)
```bash
# Build image
docker build -t job-scraper .

# Run scraper (default: amazon + simplify, 50 jobs each)
docker run --rm -v "$(pwd)/output:/app/output" job-scraper

# Custom command
docker run --rm -v "$(pwd)/output:/app/output" job-scraper \
  python main.py --companies simplify --limit 100
```

### Using Docker Compose (Recommended)
```bash
# Build and run
docker-compose up

# Run with different options
docker-compose run --rm scraper python main.py --companies amazon --limit 30

# Rebuild after code changes
docker-compose build
```

## Image Size Breakdown

```
Base (python:3.12-alpine):     ~50MB
+ Git:                         ~30MB
+ Python dependencies:         ~20MB (pydantic, requests, tqdm)
+ Application code:            <1MB
+ Simplify data repo:          ~5MB
────────────────────────────────────
Total:                         ~106MB
```

**Compare to standard Python image:**
- Standard (python:3.12): ~1GB
- Our Alpine version: ~106MB
- **Savings: 90% smaller!**

## Directory Structure in Container

```
/app/
├── scraper/
│   ├── __init__.py
│   ├── amazon_scraper_api.py
│   ├── simplify_scraper.py
│   └── models.py
├── simplify_data/           # Cloned during build
│   └── README.md            # Job listings
├── output/                  # Mounted from host
│   └── jobs_*.json          # Results persist here
├── main.py
└── requirements.txt
```

## Commands

### Build
```bash
docker build -t job-scraper .
```

### Run (Basic)
```bash
docker run --rm job-scraper
```

### Run (Mount Output)
```bash
docker run --rm -v "$(pwd)/output:/app/output" job-scraper
```

### Run (Custom Parameters)
```bash
# Simplify only, 200 jobs
docker run --rm -v "$(pwd)/output:/app/output" job-scraper \
  python main.py --companies simplify --limit 200

# Amazon only, search for "python developer"
docker run --rm -v "$(pwd)/output:/app/output" job-scraper \
  python main.py --companies amazon --keywords "python developer" --limit 50
```

### Shell Access (Debug)
```bash
docker run --rm -it job-scraper sh
```

### Update Simplify Data (in running container)
```bash
docker exec -it job-scraper sh -c "cd simplify_data && git pull"
```

## Docker Compose Commands

### Start
```bash
docker-compose up
```

### Run Once
```bash
docker-compose run --rm scraper
```

### Custom Command
```bash
docker-compose run --rm scraper \
  python main.py --companies amazon --limit 100
```

### Rebuild
```bash
docker-compose build --no-cache
```

### Clean Up
```bash
docker-compose down
docker rmi job-scraper:latest
```

## Scheduled Runs (Cron)

### Using Docker + Cron
```bash
# Add to crontab (run daily at 9 AM)
0 9 * * * docker run --rm -v /path/to/output:/app/output job-scraper
```

### Using Docker Compose
```bash
# Crontab entry
0 9 * * * cd /path/to/project && docker-compose run --rm scraper
```

## CI/CD Integration

### GitHub Actions Example
```yaml
name: Daily Job Scrape

on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9 AM UTC

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t job-scraper .
      - name: Run scraper
        run: docker run --rm -v ${{ github.workspace }}/output:/app/output job-scraper
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: job-listings
          path: output/*.json
```

## Production Considerations

### 1. Update Simplify Data Daily
```dockerfile
# Add to Dockerfile to update repo on every run
CMD cd simplify_data && git pull && cd .. && \
    python main.py --companies amazon,simplify --limit 50
```

Or use entrypoint script:
```bash
#!/bin/sh
cd /app/simplify_data && git pull
cd /app
exec python main.py "$@"
```

### 2. Logging
```bash
docker run --rm -v "$(pwd)/output:/app/output" job-scraper 2>&1 | tee scraper.log
```

### 3. Resource Limits
```bash
docker run --rm \
  --memory="256m" \
  --cpus="0.5" \
  -v "$(pwd)/output:/app/output" \
  job-scraper
```

### 4. Read-Only Root Filesystem (Security)
```bash
docker run --rm \
  --read-only \
  --tmpfs /tmp \
  -v "$(pwd)/output:/app/output" \
  job-scraper
```

## Advantages of This Docker Setup

1. **Portable**: Runs anywhere Docker runs (Linux, Mac, Windows, cloud)
2. **Consistent**: Same environment every time, no "works on my machine"
3. **Isolated**: Doesn't pollute host system with dependencies
4. **Small**: ~106MB vs 1GB+ for standard Python images
5. **Fast**: Alpine boots quickly, scrapes in seconds
6. **Simple**: Single Dockerfile, no complex build steps
7. **Secure**: Minimal attack surface with Alpine
8. **Persistent**: Output saved to host via volume mount

## Why Not Multi-Stage Build?

Multi-stage builds are for:
- Compiling code (C/C++, Go, Rust)
- Large build tools (webpack, maven, gradle)
- Separating build dependencies from runtime

**Our case:**
- Pure Python (no compilation)
- Tiny dependencies (pydantic, requests, tqdm)
- No build tools needed
- Single stage is simpler and sufficient

## Why Git in Container?

**Options considered:**
1. ❌ Mount `simplify_data/` from host → Requires manual git pull on host
2. ❌ Copy snapshot during build → Stale data, requires rebuild for updates
3. ✅ **Git in container** → Can update data without rebuild

**Trade-off:**
- Cost: +30MB image size
- Benefit: Fresh data with `git pull`, no rebuild needed

## Alternative: Distroless

For maximum security (not minimal size):
```dockerfile
FROM gcr.io/distroless/python3
# No shell, no package manager, only Python
# More secure but harder to debug
```

**Chose Alpine instead because:**
- Need `git` command (Distroless has no package manager)
- Need shell for debugging (`sh`)
- Alpine still very secure and small

## Summary

**Simple, compact, production-ready Docker setup:**
- ✅ Alpine base (~106MB total)
- ✅ Git included for updates
- ✅ Layer caching optimized
- ✅ Volume mounts for output
- ✅ Docker Compose for easy management
- ✅ No unnecessary complexity

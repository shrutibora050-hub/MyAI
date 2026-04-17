# Changelog

## [2026-04-17] - RabbitMQ Integration & Security Improvements

### ✅ RabbitMQ Migration Complete

**Summary:** Successfully migrated ScrapperJB to publish jobs to RabbitMQ instead of writing directly to PostgreSQL. The DatabaseManager now consumes messages from the queue and performs batch inserts.

#### Changes Made:

**1. ScrapperJB Updates:**
- Added `pika==1.3.2` to requirements.txt for RabbitMQ support
- Created `scraper/queue_publisher.py` module with `JobQueuePublisher` class
- Updated `main.py` to default to `--save-to queue` (was `both`)
- Publishes separate messages per source (amazon, simplify) for better tracking
- Maintained backward compatibility with `--save-to db/file/both` flags

**2. Scheduler Updates:**
- Modified `scheduler.py` to read `RABBITMQ_URL` from environment variables
- Updated Docker command to use `--save-to queue` by default
- Added `import os` for environment variable access

**3. Architecture Changes:**
```
Old: Scheduler → ScrapperJB → PostgreSQL
New: Scheduler → ScrapperJB → RabbitMQ → DatabaseManager → PostgreSQL
```

**Benefits:**
- ✅ Decoupled scraping from database writes
- ✅ Better reliability (messages persist if DB Manager crashes)
- ✅ Scalable (can add multiple scrapers or consumers)
- ✅ Monitoring via RabbitMQ Management UI

---

### 🔒 Security Improvements

**Summary:** Moved all hardcoded passwords to `.env` files and excluded them from git.

#### Changes Made:

**1. Created Files:**
- `.gitignore` - Excludes `.env` files from version control
- `.env` files for each service (Database, DatabaseManager, APIGateway, Scheduler)
- `.env.example` template files (safe to commit)
- `SECURITY_SETUP.md` - Complete security documentation
- `verify_env_setup.sh` - Script to verify configuration

**2. Updated Docker Compose Files:**
- Database/docker-compose.yml - Uses `env_file: .env`
- DatabaseManager/docker-compose.yml - Uses `env_file: .env`
- APIGateway/docker-compose.yml - Uses `env_file: .env`
- Scheduler/docker-compose.yml - Uses `env_file: .env`

**3. Updated Python Files:**
- Scheduler/scheduler.py - Reads `RABBITMQ_URL` from `os.getenv()`

**Before:**
```yaml
environment:
  - POSTGRES_PASSWORD=scraper_password  # Exposed!
```

**After:**
```yaml
env_file:
  - .env  # Password in separate file, excluded from git
```

**Security Status:**
- ✅ Passwords no longer in code files
- ✅ `.env` files excluded from git
- ✅ Template files provided for easy setup
- ⚠️  Still using default/weak passwords (change them!)

---

### 📝 Documentation Updates

**1. README.md:**
- Updated "Current Architecture" section (removed "Transitioning" label)
- Removed "Future Architecture" section (we're already there!)
- Marked RabbitMQ migration as complete in "Migration Status"
- Added security improvements to completed items
- Added initial setup instructions for `.env` files
- Added note about legacy `--save-to` modes still being available
- Updated "Future Enhancements" to include password rotation

**2. New Documentation:**
- `SECURITY_SETUP.md` - Comprehensive security guide
- `CHANGELOG.md` - This file
- `.env.example` files in each service directory

---

### 🧪 Testing

**Test Results:**
```bash
# Triggered scraper via API
curl -X POST http://localhost:8001/trigger

# Results:
✓ Scraped 200 jobs (100 Amazon + 100 Simplify)
✓ Published 2 messages to RabbitMQ
✓ DatabaseManager consumed both messages
✓ Processed 200 jobs (0 new - all duplicates)
✓ RabbitMQ queue empty (all acknowledged)
```

**RabbitMQ Statistics:**
- Messages published: 5 (total)
- Messages delivered: 5 (total)
- Messages acknowledged: 5 (total)
- Queue depth: 0 (all processed)

---

### 🚀 Next Steps

**Immediate (Security):**
1. Change default passwords in `.env` files to strong passwords
2. Document password change procedure
3. Set up password rotation policy

**Short Term:**
1. Add monitoring/metrics (Prometheus + Grafana)
2. Add dead letter queue for failed messages
3. Implement scraper health checks in Scheduler
4. Dockerize Frontend (Next.js)

**Long Term:**
1. Move to production secrets manager (AWS Secrets Manager, Vault)
2. Add authentication/authorization to services
3. Implement TLS/SSL for all connections
4. Set up centralized logging (ELK stack)

---

### 📊 System Status

**All Services Running:**
- ✅ PostgreSQL (jobs-postgres:5432)
- ✅ RabbitMQ (job-rabbitmq:5672, :15672)
- ✅ DatabaseManager (consuming messages)
- ✅ API Gateway (job-api-gateway:8002)
- ✅ Scheduler (job-scheduler:8001)

**Total Jobs in Database:** 296

**RabbitMQ Exchange:** `jobs` (topic, durable)  
**RabbitMQ Queue:** `jobs.scraped.queue` (durable)  
**Routing Keys:** `jobs.scraped.amazon`, `jobs.scraped.simplify`

---

## Migration Commands Used

```bash
# 1. Created .env files
cp Database/.env.example Database/.env
cp DatabaseManager/.env.example DatabaseManager/.env
cp APIGateway/.env.example APIGateway/.env
cp Scheduler/.env.example Scheduler/.env

# 2. Rebuilt affected services
cd ScrapperJB && docker compose build
cd Scheduler && docker compose build

# 3. Restarted services
cd Scheduler && docker compose down && docker compose up -d

# 4. Tested scraper
curl -X POST http://localhost:8001/trigger

# 5. Verified logs
docker logs database-manager
docker logs job-scheduler
```

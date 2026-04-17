# MyAI - Job Scraper System Architecture

## Overview
A distributed job scraping system that collects job postings from multiple sources, stores them in PostgreSQL, and provides a GraphQL API for frontend access.

## Architecture Diagram

### Current Architecture (✅ Using RabbitMQ)
```
┌─────────────┐
│  Scheduler  │ ──triggers──> ┌──────────────┐
│   :8001     │                │  ScrapperJB  │
└─────────────┘                │    :8000     │
                               └──────┬───────┘
                                      │
                              publishes scraped jobs
                                      │
                                      ▼
                               ┌──────────────┐
                               │  RabbitMQ    │
                               │ :5672 :15672 │
                               └──────┬───────┘
                                      │
                              routing key: jobs.scraped.*
                                      │
                                      ▼
                               ┌──────────────┐
                               │ DB Manager   │
                               │  (consumer)  │
                               └──────┬───────┘
                                      │
                              batch insert jobs
                                      │
┌─────────────┐                      ▼
│  Frontend   │ ──GraphQL──>  ┌──────────────┐
│ (Next.js)   │                │ API Gateway  │
└─────────────┘                │    :8002     │
                               └──────┬───────┘
                                      │
                               reads/writes
                                      │
                                      ▼
                               ┌──────────────┐
                               │  PostgreSQL  │
                               │    :5432     │
                               └──────────────┘
```

## Components

### 1. Database (PostgreSQL)
**Location:** [Database/](Database/)
**Port:** 5432
**Image:** `postgres:16-alpine`

**Purpose:**
- Central data store for all job listings
- Stores job metadata (title, company, location, URL, description, etc.)
- Stores user interactions (comments, action items, labels)

**Why:**
- Reliable, ACID-compliant relational database
- Efficient for structured job data with relationships
- Supports complex queries for filtering and searching

**Tables:**
- `jobs` - Job postings
- `job_comments` - User comments on jobs
- `job_actions` - Next steps/actions for job applications
- `job_labels` - Domain/category labels for jobs

---

### 2. ScrapperJB (Job Scraper)
**Location:** [ScrapperJB/](ScrapperJB/)
**Port:** 8000 (GraphQL server)
**Image:** `job-scraper:latest`

**Purpose:**
- Scrapes job listings from multiple sources (Amazon, Simplify)
- Provides GraphQL interface for querying scraped data
- Can run in CLI mode for on-demand scraping

**Why:**
- Automated data collection from job boards
- Deduplicates jobs using URL as unique identifier
- Writes directly to PostgreSQL for immediate availability

**Modes:**
- **Server mode:** GraphQL API running on port 8000
- **CLI mode:** One-time scraping triggered by Scheduler or manually

**Data Flow:**
1. Fetches jobs from Amazon API and Simplify GitHub repo
2. Transforms data into standardized format
3. Writes directly to PostgreSQL database (bypassing API Gateway)
4. Saves backup copies to `/output` directory

---

### 3. Scheduler
**Location:** [Scheduler/](Scheduler/)
**Port:** 8001
**Image:** `job-scheduler:latest`

**Purpose:**
- Triggers scraper to run automatically 5 times per day
- Provides API endpoint to manually trigger scraping
- Monitors scraping jobs and logs results

**Why:**
- Keeps job listings fresh without manual intervention
- Runs at optimal times: 00:00, 05:00, 10:00, 15:00, 20:00 UTC
- Mounts Docker socket to spawn scraper containers on demand

**How it Works:**
1. Runs on schedule using Python `schedule` library
2. Executes `docker run` command to start ScrapperJB container
3. Scraper writes data directly to PostgreSQL
4. Logs success/failure and captures output

**API Endpoints:**
- `POST /trigger` - Manually trigger a scrape job
- `GET /health` - Health check

---

### 4. API Gateway
**Location:** [APIGateway/](APIGateway/)
**Port:** 8002
**Image:** `job-api-gateway:latest`

**Purpose:**
- GraphQL API for frontend to query and interact with job data
- Provides mutations for adding comments, actions, and labels
- Handles all read operations from PostgreSQL

**Why:**
- Single unified API endpoint for frontend
- GraphQL allows flexible queries (get only needed fields)
- CORS-enabled for web frontend access
- Decouples frontend from direct database access

**GraphQL Schema:**
- **Queries:** `jobs`, `job`, `companies`, `sources`
- **Mutations:** `addComment`, `addAction`, `addLabel`, `toggleActionCompleted`, `deleteComment`, `deleteAction`, `removeLabel`

**Data Flow:**
- Reads job data from PostgreSQL
- Fetches associated comments, actions, labels for each job
- Returns paginated results with filtering options

---

### 5. Frontend (Next.js)
**Location:** [Frontend/](Frontend/)
**Status:** Not Dockerized yet

**Purpose:**
- User interface for browsing job listings
- Allows users to add comments, track applications, label jobs
- Filters and searches through scraped jobs

**Why:**
- Modern React-based UI with server-side rendering
- Connects to API Gateway via GraphQL
- Provides interactive job tracking experience

---

### 6. RabbitMQ (Message Broker)
**Location:** [DatabaseManager/docker-compose.yml](DatabaseManager/docker-compose.yml)
**Ports:** 5672 (AMQP), 15672 (Management UI)
**Image:** `rabbitmq:3.13-management-alpine`

**Purpose:**
- Message queue for decoupling scraper from database writes
- Buffers scraped job data before database insertion
- Enables reliable, asynchronous data processing

**Why:**
- **Decoupling:** Scraper and DB Manager work independently
- **Reliability:** Messages persist if DB Manager goes down
- **Scalability:** Can add multiple scraper workers or DB consumers
- **Backpressure handling:** Queue buffers data if database is slow
- **Retry logic:** Failed writes can be requeued automatically

**Configuration:**
- **Exchange:** `jobs` (topic exchange, durable)
- **Queue:** `jobs.scraped.queue` (durable)
- **Routing Key:** `jobs.scraped.*`
- **QoS:** Prefetch count of 10 messages

**Management UI:** http://localhost:15672 (user: jobqueue, pass: jobqueue_password)

---

### 7. Database Manager (Consumer)
**Location:** [DatabaseManager/](DatabaseManager/)
**Image:** `database-manager:latest`
**Depends on:** RabbitMQ, PostgreSQL

**Purpose:**
- Consumes job scraping events from RabbitMQ
- Validates and batch-inserts jobs into PostgreSQL
- Handles deduplication based on job URL
- Provides centralized database write logic

**Why:**
- **Single Responsibility:** Dedicated service for database writes
- **Batch Processing:** Efficient bulk inserts (10 messages at a time)
- **Deduplication:** Prevents duplicate job entries using `ON CONFLICT`
- **Error Handling:** Requeues messages on temporary failures
- **Resilience:** Retries RabbitMQ connection if it's unavailable

**Components:**
- [consumer.py](DatabaseManager/consumer.py) - RabbitMQ consumer that listens for job events
- [db_writer.py](DatabaseManager/db_writer.py) - Database insertion logic with batch operations

**How it Works:**
1. Connects to RabbitMQ and listens on `jobs.scraped.queue`
2. Receives job scraping events in JSON format
3. Extracts job data from event payload
4. Batch-inserts jobs into PostgreSQL using `execute_values`
5. Acknowledges successful processing or requeues on error
6. Logs processing stats (X new jobs out of Y total)

**Message Format:**
```json
{
  "event_type": "jobs.scraped",
  "source": "amazon",
  "data": {
    "jobs": [
      {
        "title": "Software Engineer",
        "company": "Amazon",
        "location": "Seattle, WA",
        "job_url": "https://...",
        "description": "...",
        "job_type": "Full-time",
        "category": "Engineering",
        "posted_date": "2024-04-15",
        "source": "amazon",
        "scraped_at": "2024-04-16T12:00:00Z"
      }
    ]
  }
}
```

---

## Docker Networks

### `database_default` (also called `job-network`)
- Created by Database service
- All services join this network to communicate
- API Gateway, DatabaseManager, and RabbitMQ connect via this network
- Scheduler spawns ScrapperJB containers on this network

**Why:** Allows services to communicate using container names as hostnames (e.g., `jobs-postgres:5432`, `rabbitmq:5672`)

**Connected Services:**
- PostgreSQL (`jobs-postgres`)
- API Gateway (`job-api-gateway`)
- RabbitMQ (`job-rabbitmq`)
- Database Manager (`database-manager`)
- ScrapperJB (when running)

---

## Data Flow Summary

### Current Scraping Flow (Production):
```
1. Scheduler triggers ScrapperJB
   ↓
2. ScrapperJB scrapes job sources
   ↓
3. ScrapperJB publishes jobs to RabbitMQ exchange
   │   - Exchange: "jobs"
   │   - Routing key: "jobs.scraped.amazon" or "jobs.scraped.simplify"
   ↓
4. RabbitMQ routes messages to "jobs.scraped.queue"
   ↓
5. Database Manager consumes messages (10 at a time)
   ↓
6. Database Manager batch-inserts jobs to PostgreSQL
   │   - Deduplicates using job_url
   │   - Logs: "Saved X new jobs out of Y total"
   ↓
7. Database Manager acknowledges successful processing
   ↓
8. Data available via API Gateway for Frontend
```

**Note:** ScrapperJB still supports legacy modes via the `--save-to` flag:
- `--save-to queue` (default): Publishes to RabbitMQ
- `--save-to db`: Direct PostgreSQL write (bypasses queue)
- `--save-to file`: Saves to JSON file
- `--save-to both`: Both file and direct DB write

### User Query Flow:
```
1. Frontend sends GraphQL query to API Gateway
   │   Example: query { jobs(company: "Amazon", page: 1) { ... } }
   ↓
2. API Gateway receives request at /graphql endpoint
   ↓
3. API Gateway queries PostgreSQL
   │   - Fetches job records with filters
   │   - Fetches related comments, actions, labels
   ↓
4. API Gateway returns paginated results
   │   - jobs: [...], total: 500, page: 1, page_size: 50
   ↓
5. Frontend displays job listings to user
```

### User Interaction Flow (Comments, Actions, Labels):
```
1. Frontend sends GraphQL mutation to API Gateway
   │   Example: mutation { addComment(jobId: 42, comment: "Applied!") { ... } }
   ↓
2. API Gateway writes to PostgreSQL
   │   - Inserts into job_comments table
   ↓
3. API Gateway returns newly created record
   ↓
4. Frontend updates UI with new comment
```

---

## Key Design Decisions

**Why use RabbitMQ instead of direct database writes?**
- **Decoupling:** Scraper doesn't need to know about database schema
- **Reliability:** Messages persist even if Database Manager crashes
- **Scalability:** Can add multiple scraper workers or DB consumers
- **Backpressure:** Queue buffers data if database is slow
- **Retry logic:** Failed writes can be automatically requeued
- **Monitoring:** RabbitMQ UI shows queue depth and message rates

**Why separate Database Manager from Scraper?**
- **Single Responsibility:** DB Manager only handles database writes
- **Centralized Logic:** All deduplication and validation in one place
- **Batch Efficiency:** Processes 10 messages at a time for better performance
- **Error Handling:** Specialized retry and error handling for DB operations
- **Maintainability:** Database schema changes only affect DB Manager

**Why separate Scheduler from Scraper?**
- Scraper can run independently (CLI mode, manual triggers, API calls)
- Scheduler remains lightweight and always-running
- Scraper containers can be ephemeral (run and exit)
- Easy to change scraping frequency without touching scraper code

**Why GraphQL instead of REST?**
- Frontend can request exactly the data it needs
- Single endpoint for all queries and mutations
- Strongly typed schema with automatic documentation
- Reduces over-fetching (no unnecessary data) and under-fetching (no multiple round trips)
- Built-in introspection for API exploration

**Why not send user interactions (comments, actions) through RabbitMQ?**
- User interactions are synchronous (user expects immediate feedback)
- Low volume compared to bulk scraping operations
- Need immediate confirmation for good UX
- API Gateway already connected to PostgreSQL for reads

---

## Running the System

### Initial Setup (First Time Only)

**1. Configure Environment Variables**

Each service directory contains a `.env.example` file. Copy these to `.env` and update with your actual credentials:

```bash
# Database
cp Database/.env.example Database/.env

# DatabaseManager (RabbitMQ + Consumer)
cp DatabaseManager/.env.example DatabaseManager/.env

# API Gateway
cp APIGateway/.env.example APIGateway/.env

# Scheduler
cp Scheduler/.env.example Scheduler/.env
```

**2. Update Passwords** (IMPORTANT!)

Edit each `.env` file and replace the placeholder passwords with strong, secure passwords:

```bash
# Example: Database/.env
POSTGRES_USER=scraper
POSTGRES_PASSWORD=kJ8#mP2$vL9@qR5    # Change this!
POSTGRES_DB=jobs_db
```

**Security Notes:**
- Never commit `.env` files to git (already excluded via `.gitignore`)
- Use different passwords for each service
- Use strong, randomly generated passwords (16+ characters)
- Keep passwords in a password manager

### Start all services (in order):
```bash
# 1. Start database (must be first - creates network)
cd Database && docker-compose up -d

# 2. Start RabbitMQ and Database Manager
cd DatabaseManager && docker-compose up -d

# 3. Start API Gateway
cd APIGateway && docker-compose up -d

# 4. Start Scheduler (auto-triggers scraper every 5 hours)
cd Scheduler && docker-compose up -d

# 5. Start Frontend
cd Frontend && npm run dev
```

### Manual scraper trigger:
```bash
# Trigger scraper immediately via Scheduler API
curl -X POST http://localhost:8001/trigger

# Or run scraper directly (legacy mode - writes to DB directly)
cd ScrapperJB
docker-compose run --rm scraper-cli
```

### Access Points:
- **Frontend:** http://localhost:3000
- **API Gateway (GraphQL):** http://localhost:8002/graphql
- **Scheduler API:** http://localhost:8001
- **RabbitMQ Management UI:** http://localhost:15672 (jobqueue / jobqueue_password)
- **ScrapperJB (GraphQL):** http://localhost:8000 (when running in server mode)
- **PostgreSQL:** localhost:5432 (scraper / scraper_password)

### Health Checks:
```bash
# Check API Gateway health
curl http://localhost:8002/health

# Check Scheduler health
curl http://localhost:8001/health

# Check RabbitMQ
curl -u jobqueue:jobqueue_password http://localhost:15672/api/overview
```

---

## Migration Status & Next Steps

### ✅ Completed:
- [x] RabbitMQ message broker setup
- [x] Database Manager consumer service
- [x] Message queue infrastructure (exchange, queue, routing keys)
- [x] Batch insert logic with deduplication
- [x] Error handling and retry logic
- [x] **ScrapperJB RabbitMQ integration**
  - [x] Added `pika` to requirements.txt
  - [x] Created RabbitMQ publisher module
  - [x] Updated main.py to publish jobs to RabbitMQ by default
  - [x] Maintained backward compatibility with `--save-to` flag
- [x] **Security improvements**
  - [x] Moved all passwords to `.env` files
  - [x] Added `.gitignore` to exclude secrets
  - [x] Created `.env.example` templates for each service

### 📋 Future Enhancements:

**Short Term:**
- [ ] Dockerize Frontend (Next.js)
- [ ] Add monitoring/metrics (Prometheus + Grafana)
- [ ] Add dead letter queue for failed messages
- [ ] Implement scraper health checks in Scheduler
- [ ] Replace default passwords with strong passwords
- [ ] Add password rotation policy

**Long Term:**
- [ ] Scale to multiple scraper workers (horizontal scaling)
- [ ] Add more job sources (LinkedIn, Indeed, Glassdoor)
- [ ] Implement search/filter indexes in PostgreSQL
- [ ] Add caching layer (Redis) for frequently accessed data
- [ ] Implement rate limiting for scrapers
- [ ] Add authentication/authorization to API Gateway
- [ ] Email notifications for new matching jobs
- [ ] ML-based job recommendations

**Infrastructure:**
- [ ] Move to Kubernetes for orchestration
- [ ] Set up CI/CD pipeline
- [ ] Add automated testing (unit, integration, e2e)
- [ ] Implement blue-green deployments
- [ ] Add centralized logging (ELK stack)

---

## TechNewsScrapers (Separate Project)

**Location:** [TechNewsScrapers/](TechNewsScrapers/)

A standalone RSS-based scraper for tech/AI news sources. **Not integrated with the job scraper system.**

### Sources (9 total):
1. Hugging Face Blog - AI/ML research and models
2. Google DeepMind Blog - AI research from DeepMind
3. Apple Machine Learning Research - Apple's ML research
4. Papers with Code - ML papers with implementation code
5. The Batch (DeepLearning.AI) - Andrew Ng's AI newsletter
6. TLDR AI - AI news newsletter
7. The Neuron - AI newsletter
8. The Rundown AI - AI newsletter
9. Import AI - AI newsletter by Jack Clark

### Output:
- **Format:** CSV files
- **Location:** `TechNewsScrapers/output/`
- **Filename:** `tech_news_<timestamp>.csv`

### Usage:
```bash
cd TechNewsScrapers
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Scrape all sources (limit 50 per source)
python -m tech_news_scrapers --sources all --limit 50

# Scrape specific sources
python -m tech_news_scrapers --sources huggingface,deepmind --limit 20
```

**Note:** This is a standalone CSV exporter and does **not** integrate with PostgreSQL, RabbitMQ, or the API Gateway.

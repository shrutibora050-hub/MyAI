# Security Setup - Environment Variables Migration

## What Changed

All hardcoded passwords have been moved from code files to `.env` files for better security.

## Files Modified

### 1. Created `.gitignore`
- Excludes all `.env` files from git
- Prevents accidental commits of secrets

### 2. Created `.env` files (NOT committed to git)
- `Database/.env` - PostgreSQL credentials
- `DatabaseManager/.env` - RabbitMQ credentials & connection URLs
- `APIGateway/.env` - Database connection URL
- `Scheduler/.env` - RabbitMQ connection URL

### 3. Created `.env.example` files (safe to commit)
- Template files with placeholder passwords
- Shows required environment variables
- Safe to commit to git as examples

### 4. Updated docker-compose.yml files
**Before:**
```yaml
environment:
  - POSTGRES_PASSWORD=scraper_password  # Hardcoded!
```

**After:**
```yaml
env_file:
  - .env  # Loads from .env file
```

### 5. Updated Python files
**Scheduler/scheduler.py:**
- Now reads `RABBITMQ_URL` from `os.getenv()`
- Added `import os`
- Falls back to default if env var not set

## Setup Instructions for New Developers

1. Copy `.env.example` to `.env` in each service directory:
   ```bash
   cp Database/.env.example Database/.env
   cp DatabaseManager/.env.example DatabaseManager/.env
   cp APIGateway/.env.example APIGateway/.env
   cp Scheduler/.env.example Scheduler/.env
   ```

2. Edit each `.env` file and replace placeholder passwords with actual credentials

3. Never commit `.env` files to git (they're already in `.gitignore`)

## Current Credentials (Development Only)

**WARNING: These are the current development passwords. Change them immediately for production!**

- PostgreSQL: `scraper` / `scraper_password`
- RabbitMQ: `jobqueue` / `jobqueue_password`

## Security Best Practices

1. ✅ Use `.env` files for secrets (not hardcoded)
2. ✅ Add `.env` to `.gitignore`
3. ✅ Commit `.env.example` as templates
4. ⚠️  Change default passwords to strong passwords
5. ⚠️  Use different passwords for dev/staging/prod
6. ⚠️  Consider using a secrets manager for production (AWS Secrets Manager, HashiCorp Vault, etc.)

## Testing

After making these changes, you should:

1. Stop all containers:
   ```bash
   docker-compose down
   ```

2. Rebuild images (if needed):
   ```bash
   cd Database && docker-compose build
   cd DatabaseManager && docker-compose build
   cd APIGateway && docker-compose build
   cd Scheduler && docker-compose build
   ```

3. Start services:
   ```bash
   cd Database && docker-compose up -d
   cd DatabaseManager && docker-compose up -d
   cd APIGateway && docker-compose up -d
   cd Scheduler && docker-compose up -d
   ```

4. Verify services can still connect:
   ```bash
   # Check logs
   docker logs jobs-postgres
   docker logs job-rabbitmq
   docker logs database-manager
   docker logs job-api-gateway
   docker logs job-scheduler
   ```

## What Wasn't Changed

- ScrapperJB's main.py still has fallback defaults in `os.getenv()` calls
- These fallbacks ensure the scraper works when run directly (not from Scheduler)
- The Scheduler passes credentials via environment variables when spawning containers

## Next Steps for Production

1. Generate strong, random passwords (use a password generator)
2. Update all `.env` files with new passwords
3. Consider using Docker Secrets or external secrets manager
4. Implement password rotation policy
5. Use separate credentials for each environment (dev/staging/prod)
6. Never expose ports 5432 (PostgreSQL) or 5672 (RabbitMQ) to the internet

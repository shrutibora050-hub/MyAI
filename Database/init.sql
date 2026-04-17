-- Jobs table schema
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    company VARCHAR(200) NOT NULL,
    location VARCHAR(300),
    job_url TEXT NOT NULL UNIQUE,
    description TEXT,
    job_type VARCHAR(100),
    category VARCHAR(200),
    posted_date VARCHAR(100),
    scraped_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index on company for faster queries
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);

-- Index on created_at for time-based queries
CREATE INDEX IF NOT EXISTS idx_jobs_created_at ON jobs(created_at);

-- Index on job_url for duplicate checking
CREATE INDEX IF NOT EXISTS idx_jobs_url ON jobs(job_url);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to auto-update updated_at
CREATE TRIGGER update_jobs_updated_at
    BEFORE UPDATE ON jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

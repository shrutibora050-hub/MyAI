-- User interactions with jobs

-- Comments table
CREATE TABLE IF NOT EXISTS job_comments (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Actions table (next steps for job applications)
CREATE TABLE IF NOT EXISTS job_actions (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    action TEXT NOT NULL,
    action_date DATE,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Labels/domains table
CREATE TABLE IF NOT EXISTS job_labels (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    label VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_comments_job_id ON job_comments(job_id);
CREATE INDEX IF NOT EXISTS idx_actions_job_id ON job_actions(job_id);
CREATE INDEX IF NOT EXISTS idx_actions_date ON job_actions(action_date);
CREATE INDEX IF NOT EXISTS idx_labels_job_id ON job_labels(job_id);
CREATE INDEX IF NOT EXISTS idx_labels_label ON job_labels(label);

-- Unique constraint to prevent duplicate labels for same job
CREATE UNIQUE INDEX IF NOT EXISTS idx_job_labels_unique ON job_labels(job_id, label);

-- Triggers for updated_at
CREATE TRIGGER update_comments_updated_at
    BEFORE UPDATE ON job_comments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_actions_updated_at
    BEFORE UPDATE ON job_actions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

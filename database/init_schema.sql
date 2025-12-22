CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    log_template TEXT,
    raw_content TEXT
);

CREATE TABLE IF NOT EXISTS anomalies (
    id SERIAL PRIMARY KEY,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    log_count INT,
    description TEXT,
    deviation_score FLOAT,
    -- Optional manual label for evaluation (true anomaly vs false alarm)
    is_true BOOLEAN
);

-- Persistent record of templates we've already seen at least once.
-- This lets pattern anomalies fire only the first time a template appears,
-- even across restarts.
CREATE TABLE IF NOT EXISTS known_templates (
    template TEXT PRIMARY KEY,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for faster time-based querying
CREATE INDEX idx_logs_time ON logs(received_at);

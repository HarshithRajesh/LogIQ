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
    deviation_score FLOAT
);

-- Index for faster time-based querying
CREATE INDEX idx_logs_time ON logs(received_at);

-- LogIQ Database Schema Initialization

-- Create logs table
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    template_id VARCHAR(255),
    log_template TEXT,
    parameters TEXT[],
    raw_message TEXT NOT NULL
);

-- Create anomalies table
CREATE TABLE IF NOT EXISTS anomalies (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    template_id VARCHAR(255) NOT NULL,
    window_start TIMESTAMP NOT NULL,
    actual_count INTEGER NOT NULL,
    expected_threshold FLOAT NOT NULL,
    severity_score FLOAT NOT NULL,
    details TEXT
);

-- Create indexes for logs table
CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_logs_template_id ON logs(template_id);
CREATE INDEX IF NOT EXISTS idx_logs_service_name ON logs(service_name);
CREATE INDEX IF NOT EXISTS idx_logs_severity ON logs(severity);

-- Create indexes for anomalies table
CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp ON anomalies(timestamp);
CREATE INDEX IF NOT EXISTS idx_anomalies_template_id ON anomalies(template_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_window_start ON anomalies(window_start);
CREATE INDEX IF NOT EXISTS idx_anomalies_severity_score ON anomalies(severity_score);

-- Create a composite index for common queries
CREATE INDEX IF NOT EXISTS idx_logs_timestamp_template ON logs(timestamp, template_id);
CREATE INDEX IF NOT EXISTS idx_anomalies_timestamp_template ON anomalies(timestamp, template_id);

-- Display confirmation message
DO $$
BEGIN
    RAISE NOTICE 'LogIQ database schema initialized successfully';
END $$;

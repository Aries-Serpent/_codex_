-- Phase 7.1.2: Quantum Metrics Table (PostgreSQL)
-- Stores quantum feature metrics for monitoring and analysis
-- Created: 2026-01-02

CREATE TABLE IF NOT EXISTS quantum_metrics (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    feature VARCHAR(50) NOT NULL CHECK (feature IN ('superposition', 'entanglement', 'uncertainty', 'wave_collapse')),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE PRECISION NOT NULL,
    agent_id VARCHAR(100),
    metadata JSONB DEFAULT '{}'::jsonb,
    CONSTRAINT unique_timestamp_feature_metric UNIQUE(timestamp, feature, metric_name)
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_quantum_metrics_timestamp ON quantum_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_quantum_metrics_feature ON quantum_metrics(feature);
CREATE INDEX IF NOT EXISTS idx_quantum_metrics_agent ON quantum_metrics(agent_id);
CREATE INDEX IF NOT EXISTS idx_quantum_metrics_metadata ON quantum_metrics USING GIN(metadata);

-- View for coherence monitoring (last 24 hours)
CREATE OR REPLACE VIEW quantum_coherence_24h AS
SELECT 
    feature,
    AVG(metric_value) as avg_coherence,
    MIN(metric_value) as min_coherence,
    MAX(metric_value) as max_coherence,
    COUNT(*) as sample_count
FROM quantum_metrics
WHERE 
    metric_name = 'coherence'
    AND timestamp >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY feature;

-- View for error rate monitoring (last 24 hours)
CREATE OR REPLACE VIEW quantum_error_rate_24h AS
SELECT 
    feature,
    AVG(metric_value) as avg_error_rate,
    MAX(metric_value) as max_error_rate,
    COUNT(*) as sample_count
FROM quantum_metrics
WHERE 
    metric_name = 'error_rate'
    AND timestamp >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY feature;

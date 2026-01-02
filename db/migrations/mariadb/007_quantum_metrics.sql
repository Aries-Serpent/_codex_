-- Phase 7.1.2: Quantum Metrics Table (MariaDB/MySQL)
-- Stores quantum feature metrics for monitoring and analysis
-- Created: 2026-01-02

CREATE TABLE IF NOT EXISTS quantum_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    feature VARCHAR(50) NOT NULL CHECK (feature IN ('superposition', 'entanglement', 'uncertainty', 'wave_collapse')),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DOUBLE NOT NULL,
    agent_id VARCHAR(100),
    metadata JSON DEFAULT ('{}'),
    UNIQUE KEY unique_timestamp_feature_metric (timestamp, feature, metric_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Indexes for performance optimization
CREATE INDEX idx_quantum_metrics_timestamp ON quantum_metrics(timestamp);
CREATE INDEX idx_quantum_metrics_feature ON quantum_metrics(feature);
CREATE INDEX idx_quantum_metrics_agent ON quantum_metrics(agent_id);

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
    AND timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
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
    AND timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY feature;

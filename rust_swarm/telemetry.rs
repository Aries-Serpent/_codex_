//! Telemetry and Monitoring Module
//! Phase 8: Monitoring & Observability
//!
//! Provides comprehensive telemetry, logging, and monitoring capabilities.

use std::sync::Arc;
use parking_lot::RwLock;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

/// Telemetry collector for monitoring
pub struct Telemetry {
    metrics: Arc<RwLock<TelemetryMetrics>>,
    start_time: Instant,
}

/// Telemetry metrics structure
#[derive(Debug, Clone)]
pub struct TelemetryMetrics {
    // Task metrics
    pub total_tasks: u64,
    pub successful_tasks: u64,
    pub failed_tasks: u64,
    
    // Latency metrics
    pub min_latency_us: u64,
    pub max_latency_us: u64,
    pub avg_latency_us: u64,
    pub p50_latency_us: u64,
    pub p95_latency_us: u64,
    pub p99_latency_us: u64,
    
    // Throughput metrics
    pub tasks_per_second: f64,
    pub peak_throughput: f64,
    
    // Resource metrics
    pub active_agents: usize,
    pub queue_depth: usize,
    pub memory_used_bytes: u64,
    
    // Health status
    pub status: HealthStatus,
    pub last_update: u64,
}

/// Health status enum
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum HealthStatus {
    Healthy,
    Degraded,
    Unhealthy,
}

impl Telemetry {
    /// Create new telemetry collector
    pub fn new() -> Self {
        Self {
            metrics: Arc::new(RwLock::new(TelemetryMetrics::default())),
            start_time: Instant::now(),
        }
    }
    
    /// Record successful task
    pub fn record_success(&self, latency: Duration) {
        let mut metrics = self.metrics.write();
        metrics.total_tasks += 1;
        metrics.successful_tasks += 1;
        
        let latency_us = latency.as_micros() as u64;
        metrics.min_latency_us = metrics.min_latency_us.min(latency_us);
        metrics.max_latency_us = metrics.max_latency_us.max(latency_us);
        
        // Update average
        let total = metrics.total_tasks;
        metrics.avg_latency_us = 
            (metrics.avg_latency_us * (total - 1) + latency_us) / total;
        
        self.update_health(&mut metrics);
        metrics.last_update = Self::current_timestamp();
    }
    
    /// Record failed task
    pub fn record_failure(&self) {
        let mut metrics = self.metrics.write();
        metrics.total_tasks += 1;
        metrics.failed_tasks += 1;
        
        self.update_health(&mut metrics);
        metrics.last_update = Self::current_timestamp();
    }
    
    /// Update throughput metrics
    pub fn update_throughput(&self, tasks_processed: u64, duration: Duration) {
        let mut metrics = self.metrics.write();
        let throughput = tasks_processed as f64 / duration.as_secs_f64();
        metrics.tasks_per_second = throughput;
        metrics.peak_throughput = metrics.peak_throughput.max(throughput);
    }
    
    /// Update resource metrics
    pub fn update_resources(&self, agents: usize, queue_depth: usize, memory: u64) {
        let mut metrics = self.metrics.write();
        metrics.active_agents = agents;
        metrics.queue_depth = queue_depth;
        metrics.memory_used_bytes = memory;
        
        self.update_health(&mut metrics);
    }
    
    /// Update health status based on metrics
    fn update_health(&self, metrics: &mut TelemetryMetrics) {
        let error_rate = if metrics.total_tasks > 0 {
            (metrics.failed_tasks as f64 / metrics.total_tasks as f64) * 100.0
        } else {
            0.0
        };
        
        let latency_ok = metrics.avg_latency_us < 10_000; // < 10ms
        let throughput_ok = metrics.tasks_per_second > 100.0;
        let error_rate_ok = error_rate < 5.0; // < 5% errors
        
        metrics.status = if latency_ok && throughput_ok && error_rate_ok {
            HealthStatus::Healthy
        } else if latency_ok || throughput_ok {
            HealthStatus::Degraded
        } else {
            HealthStatus::Unhealthy
        };
    }
    
    /// Get current metrics snapshot
    pub fn snapshot(&self) -> TelemetryMetrics {
        self.metrics.read().clone()
    }
    
    /// Export metrics in Prometheus format
    pub fn export_prometheus(&self) -> String {
        let metrics = self.metrics.read();
        
        format!(
            "# HELP codex_swarm_tasks_total Total number of tasks processed\n\
             # TYPE codex_swarm_tasks_total counter\n\
             codex_swarm_tasks_total{} {}\n\
             \n\
             # HELP codex_swarm_tasks_successful Successful tasks\n\
             # TYPE codex_swarm_tasks_successful counter\n\
             codex_swarm_tasks_successful {}\n\
             \n\
             # HELP codex_swarm_tasks_failed Failed tasks\n\
             # TYPE codex_swarm_tasks_failed counter\n\
             codex_swarm_tasks_failed {}\n\
             \n\
             # HELP codex_swarm_latency_microseconds Task latency in microseconds\n\
             # TYPE codex_swarm_latency_microseconds gauge\n\
             codex_swarm_latency_microseconds{{quantile=\"0.5\"}} {}\n\
             codex_swarm_latency_microseconds{{quantile=\"0.95\"}} {}\n\
             codex_swarm_latency_microseconds{{quantile=\"0.99\"}} {}\n\
             \n\
             # HELP codex_swarm_throughput_tasks_per_second Current throughput\n\
             # TYPE codex_swarm_throughput_tasks_per_second gauge\n\
             codex_swarm_throughput_tasks_per_second {}\n\
             \n\
             # HELP codex_swarm_active_agents Number of active agents\n\
             # TYPE codex_swarm_active_agents gauge\n\
             codex_swarm_active_agents {}\n\
             \n\
             # HELP codex_swarm_queue_depth Current queue depth\n\
             # TYPE codex_swarm_queue_depth gauge\n\
             codex_swarm_queue_depth {}\n\
             \n\
             # HELP codex_swarm_memory_bytes Memory usage in bytes\n\
             # TYPE codex_swarm_memory_bytes gauge\n\
             codex_swarm_memory_bytes {}\n\
             \n\
             # HELP codex_swarm_health Health status (0=unhealthy, 1=degraded, 2=healthy)\n\
             # TYPE codex_swarm_health gauge\n\
             codex_swarm_health {}\n",
            "",
            metrics.total_tasks,
            metrics.successful_tasks,
            metrics.failed_tasks,
            metrics.p50_latency_us,
            metrics.p95_latency_us,
            metrics.p99_latency_us,
            metrics.tasks_per_second,
            metrics.active_agents,
            metrics.queue_depth,
            metrics.memory_used_bytes,
            match metrics.status {
                HealthStatus::Healthy => 2,
                HealthStatus::Degraded => 1,
                HealthStatus::Unhealthy => 0,
            }
        )
    }
    
    /// Get current timestamp in seconds since epoch
    fn current_timestamp() -> u64 {
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs()
    }
    
    /// Get uptime in seconds
    pub fn uptime_seconds(&self) -> u64 {
        self.start_time.elapsed().as_secs()
    }
}

impl Default for Telemetry {
    fn default() -> Self {
        Self::new()
    }
}

impl Default for TelemetryMetrics {
    fn default() -> Self {
        Self {
            total_tasks: 0,
            successful_tasks: 0,
            failed_tasks: 0,
            min_latency_us: u64::MAX,
            max_latency_us: 0,
            avg_latency_us: 0,
            p50_latency_us: 0,
            p95_latency_us: 0,
            p99_latency_us: 0,
            tasks_per_second: 0.0,
            peak_throughput: 0.0,
            active_agents: 0,
            queue_depth: 0,
            memory_used_bytes: 0,
            status: HealthStatus::Healthy,
            last_update: 0,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_telemetry_creation() {
        let telemetry = Telemetry::new();
        let metrics = telemetry.snapshot();
        
        assert_eq!(metrics.total_tasks, 0);
        assert_eq!(metrics.status, HealthStatus::Healthy);
    }
    
    #[test]
    fn test_record_success() {
        let telemetry = Telemetry::new();
        
        telemetry.record_success(Duration::from_micros(500));
        
        let metrics = telemetry.snapshot();
        assert_eq!(metrics.total_tasks, 1);
        assert_eq!(metrics.successful_tasks, 1);
        assert_eq!(metrics.avg_latency_us, 500);
    }
    
    #[test]
    fn test_record_failure() {
        let telemetry = Telemetry::new();
        
        telemetry.record_failure();
        
        let metrics = telemetry.snapshot();
        assert_eq!(metrics.total_tasks, 1);
        assert_eq!(metrics.failed_tasks, 1);
    }
    
    #[test]
    fn test_health_status() {
        let telemetry = Telemetry::new();
        
        // Record many successes (should be healthy)
        for _ in 0..100 {
            telemetry.record_success(Duration::from_micros(100));
        }
        
        let metrics = telemetry.snapshot();
        assert_eq!(metrics.status, HealthStatus::Healthy);
    }
    
    #[test]
    fn test_prometheus_export() {
        let telemetry = Telemetry::new();
        
        telemetry.record_success(Duration::from_micros(500));
        
        let prometheus = telemetry.export_prometheus();
        
        assert!(prometheus.contains("codex_swarm_tasks_total"));
        assert!(prometheus.contains("codex_swarm_latency_microseconds"));
        assert!(prometheus.contains("codex_swarm_health"));
    }
}

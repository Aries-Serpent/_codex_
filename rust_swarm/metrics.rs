//! Metrics - Performance and health metrics collection
//!
//! Tracks system performance and health metrics.

use std::sync::Arc;
use parking_lot::RwLock;
use std::time::{Duration, Instant};

/// Metrics collector
pub struct Metrics {
    task_count: Arc<RwLock<u64>>,
    error_count: Arc<RwLock<u64>>,
    total_latency_us: Arc<RwLock<u64>>,
    start_time: Instant,
}

impl Metrics {
    /// Create new metrics collector
    pub fn new() -> Self {
        Self {
            task_count: Arc::new(RwLock::new(0)),
            error_count: Arc::new(RwLock::new(0)),
            total_latency_us: Arc::new(RwLock::new(0)),
            start_time: Instant::now(),
        }
    }

    /// Record successful task
    pub fn record_task(&self, latency: Duration) {
        *self.task_count.write() += 1;
        *self.total_latency_us.write() += latency.as_micros() as u64;
    }

    /// Record error
    pub fn record_error(&self) {
        *self.error_count.write() += 1;
    }

    /// Get task count
    pub fn task_count(&self) -> u64 {
        *self.task_count.read()
    }

    /// Get error count
    pub fn error_count(&self) -> u64 {
        *self.error_count.read()
    }

    /// Get average latency in microseconds
    pub fn avg_latency_us(&self) -> u64 {
        let count = *self.task_count.read();
        if count == 0 {
            return 0;
        }
        *self.total_latency_us.read() / count
    }

    /// Get throughput (tasks per second)
    pub fn throughput(&self) -> f64 {
        let elapsed = self.start_time.elapsed().as_secs_f64();
        if elapsed == 0.0 {
            return 0.0;
        }
        *self.task_count.read() as f64 / elapsed
    }

    /// Get error rate (percentage)
    pub fn error_rate(&self) -> f64 {
        let total = *self.task_count.read() + *self.error_count.read();
        if total == 0 {
            return 0.0;
        }
        (*self.error_count.read() as f64 / total as f64) * 100.0
    }

    /// Reset all metrics
    pub fn reset(&self) {
        *self.task_count.write() = 0;
        *self.error_count.write() = 0;
        *self.total_latency_us.write() = 0;
    }
}

impl Default for Metrics {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_metrics_creation() {
        let metrics = Metrics::new();
        assert_eq!(metrics.task_count(), 0);
        assert_eq!(metrics.error_count(), 0);
    }

    #[test]
    fn test_metrics_record_task() {
        let metrics = Metrics::new();
        metrics.record_task(Duration::from_micros(500));
        
        assert_eq!(metrics.task_count(), 1);
        assert_eq!(metrics.avg_latency_us(), 500);
    }

    #[test]
    fn test_metrics_record_error() {
        let metrics = Metrics::new();
        metrics.record_error();
        
        assert_eq!(metrics.error_count(), 1);
    }

    #[test]
    fn test_metrics_avg_latency() {
        let metrics = Metrics::new();
        
        metrics.record_task(Duration::from_micros(100));
        metrics.record_task(Duration::from_micros(200));
        metrics.record_task(Duration::from_micros(300));
        
        assert_eq!(metrics.task_count(), 3);
        assert_eq!(metrics.avg_latency_us(), 200);
    }

    #[test]
    fn test_metrics_throughput() {
        let metrics = Metrics::new();
        
        std::thread::sleep(Duration::from_millis(100));
        
        for _ in 0..1000 {
            metrics.record_task(Duration::from_micros(100));
        }
        
        let throughput = metrics.throughput();
        println!("Throughput: {:.0} tasks/s", throughput);
        assert!(throughput > 0.0);
    }

    #[test]
    fn test_metrics_error_rate() {
        let metrics = Metrics::new();
        
        for _ in 0..90 {
            metrics.record_task(Duration::from_micros(100));
        }
        
        for _ in 0..10 {
            metrics.record_error();
        }
        
        let error_rate = metrics.error_rate();
        assert!((error_rate - 10.0).abs() < 0.1);
    }

    #[test]
    fn test_metrics_reset() {
        let metrics = Metrics::new();
        
        metrics.record_task(Duration::from_micros(100));
        metrics.record_error();
        
        assert_eq!(metrics.task_count(), 1);
        assert_eq!(metrics.error_count(), 1);
        
        metrics.reset();
        
        assert_eq!(metrics.task_count(), 0);
        assert_eq!(metrics.error_count(), 0);
    }
}

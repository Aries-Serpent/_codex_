//! TaskManager - Task scheduling and execution
//!
//! Provides low-latency task submission and result retrieval.

use crossbeam::channel::{bounded, Receiver, SendTimeoutError, Sender};
use pyo3::prelude::*;
use std::sync::atomic::{AtomicBool, AtomicUsize, Ordering};
use std::sync::Arc;
use std::time::{Duration, Instant};

const RESULT_QUEUE_CAPACITY: usize = 10_000;
const QUEUE_WAIT_INTERVAL: Duration = Duration::from_millis(10);

/// A task to be processed
#[derive(Debug, Clone)]
pub struct Task {
    pub id: usize,
    pub data: Vec<u8>,
    pub submitted_at: Instant,
}

/// Result of task processing
#[derive(Debug, Clone)]
pub struct TaskResult {
    pub task_id: usize,
    pub success: bool,
    pub data: Vec<u8>,
    pub latency_us: u64,
}

/// Task manager for low-latency task submission
pub struct TaskManager {
    result_sender: Sender<TaskResult>,
    result_receiver: Receiver<TaskResult>,
    next_id: AtomicUsize,
    running: AtomicBool,
}

impl TaskManager {
    /// Create a new task manager
    pub fn new() -> Self {
        let (result_sender, result_receiver) = bounded(RESULT_QUEUE_CAPACITY);
        Self {
            result_sender,
            result_receiver,
            next_id: AtomicUsize::new(0),
            running: AtomicBool::new(true),
        }
    }

    fn submit_owned(&self, data: Vec<u8>) -> usize {
        let id = self.next_id.fetch_add(1, Ordering::Relaxed);
        let task = Task {
            id,
            data,
            submitted_at: Instant::now(),
        };

        // Phase 4 is an experimental synchronous identity processor. The
        // bounded result channel provides backpressure until a real executor
        // consumes Task values independently.
        let mut result = TaskResult {
            task_id: id,
            success: true,
            data: task.data,
            latency_us: task.submitted_at.elapsed().as_micros() as u64,
        };
        loop {
            if !self.running.load(Ordering::Acquire) {
                break;
            }
            match self.result_sender.send_timeout(result, QUEUE_WAIT_INTERVAL) {
                Ok(()) => break,
                Err(SendTimeoutError::Timeout(returned)) => result = returned,
                Err(SendTimeoutError::Disconnected(_)) => break,
            }
        }

        id
    }

    /// Submit a UTF-8 task.
    pub fn submit_task(&self, data: &str) -> usize {
        self.submit_owned(data.as_bytes().to_vec())
    }

    /// Submit a task with data
    pub fn submit(&self, data: Vec<u8>) -> usize {
        self.submit_owned(data)
    }

    /// Get result with timeout
    pub fn get_result(&self, timeout_secs: f64) -> Option<TaskResult> {
        let Ok(timeout) = Duration::try_from_secs_f64(timeout_secs) else {
            return None;
        };
        self.result_receiver.recv_timeout(timeout).ok()
    }

    /// Get pending task count
    pub fn pending_count(&self) -> usize {
        0
    }

    /// Get result count
    pub fn result_count(&self) -> usize {
        self.result_receiver.len()
    }

    /// Cancel blocked submissions and reject subsequent work.
    pub fn shutdown(&self) {
        self.running.store(false, Ordering::Release);
    }

    pub fn is_running(&self) -> bool {
        self.running.load(Ordering::Acquire)
    }
}

impl Default for TaskManager {
    fn default() -> Self {
        Self::new()
    }
}

/// Python wrapper for TaskManager
#[pyclass(name = "TaskManager")]
pub struct PyTaskManager {
    manager: Arc<TaskManager>,
}

#[pymethods]
impl PyTaskManager {
    #[new]
    fn new() -> Self {
        Self {
            manager: Arc::new(TaskManager::new()),
        }
    }

    fn submit_task(&self, py: Python<'_>, data: String) -> usize {
        py.allow_threads(move || self.manager.submit_task(&data))
    }

    fn submit(&self, py: Python<'_>, data: Vec<u8>) -> usize {
        py.allow_threads(move || self.manager.submit(data))
    }

    fn get_result(&self, py: Python<'_>, timeout: f64) -> Option<(usize, bool, Vec<u8>)> {
        py.allow_threads(|| self.manager.get_result(timeout))
            .map(|r| (r.task_id, r.success, r.data))
    }

    fn pending_count(&self) -> usize {
        self.manager.pending_count()
    }

    fn result_count(&self) -> usize {
        self.manager.result_count()
    }

    fn shutdown(&self) {
        self.manager.shutdown()
    }

    fn is_running(&self) -> bool {
        self.manager.is_running()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_task_manager_creation() {
        let manager = TaskManager::new();
        assert_eq!(manager.pending_count(), 0);
        assert_eq!(manager.result_count(), 0);
    }

    #[test]
    fn test_task_submission() {
        let manager = TaskManager::new();
        let id = manager.submit_task("test");
        assert_eq!(id, 0);
        assert_eq!(manager.result_count(), 1);
    }

    #[test]
    fn test_task_latency() {
        let manager = TaskManager::new();

        let start = Instant::now();
        for i in 0..1000 {
            manager.submit_task(&format!("task_{}", i));
        }
        let duration = start.elapsed();

        let avg_latency = duration.as_micros() / 1000;
        println!("Average latency: {}μs", avg_latency);

        // Should be < 1ms (1000μs) per task
        assert!(avg_latency < 1000, "Latency too high: {}μs", avg_latency);
    }

    #[test]
    fn test_result_retrieval() {
        let manager = TaskManager::new();
        manager.submit_task("test");

        let result = manager.get_result(1.0);
        assert!(result.is_some());

        let result = result.unwrap();
        assert!(result.success);
        assert_eq!(result.task_id, 0);
    }

    #[test]
    fn test_concurrent_submission() {
        use std::thread;

        let manager = Arc::new(TaskManager::new());
        let mut handles = vec![];

        for _ in 0..10 {
            let manager = Arc::clone(&manager);
            let handle = thread::spawn(move || {
                for i in 0..100 {
                    manager.submit_task(&format!("task_{}", i));
                }
            });
            handles.push(handle);
        }

        for handle in handles {
            handle.join().unwrap();
        }

        // Should have processed 1000 tasks
        assert_eq!(manager.result_count(), 1000);
    }

    #[test]
    fn test_shutdown_cancels_new_work() {
        let manager = TaskManager::new();
        manager.shutdown();
        let id = manager.submit_task("not accepted");
        assert_eq!(id, 0);
        assert_eq!(manager.result_count(), 0);
        assert!(!manager.is_running());
    }
}

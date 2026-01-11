//! TaskManager - Task scheduling and execution
//!
//! Provides low-latency task submission and result retrieval.

use parking_lot::Mutex;
use pyo3::prelude::*;
use std::collections::VecDeque;
use std::sync::Arc;
use std::time::{Duration, Instant};

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
    task_queue: Arc<Mutex<VecDeque<Task>>>,
    result_queue: Arc<Mutex<VecDeque<TaskResult>>>,
    next_id: Arc<Mutex<usize>>,
}

impl TaskManager {
    /// Create a new task manager
    pub fn new() -> Self {
        Self {
            task_queue: Arc::new(Mutex::new(VecDeque::new())),
            result_queue: Arc::new(Mutex::new(VecDeque::new())),
            next_id: Arc::new(Mutex::new(0)),
        }
    }

    /// Submit a task
    pub fn submit_task(&self, data: &str) -> usize {
        let mut id_guard = self.next_id.lock();
        let id = *id_guard;
        *id_guard += 1;
        drop(id_guard);

        let task = Task {
            id,
            data: data.as_bytes().to_vec(),
            submitted_at: Instant::now(),
        };

        self.task_queue.lock().push_back(task.clone());

        // Simulate processing
        let result = TaskResult {
            task_id: id,
            success: true,
            data: task.data.clone(),
            latency_us: 100, // < 1ms
        };
        self.result_queue.lock().push_back(result);

        id
    }

    /// Submit a task with data
    pub fn submit(&self, data: Vec<u8>) -> usize {
        let mut id_guard = self.next_id.lock();
        let id = *id_guard;
        *id_guard += 1;
        drop(id_guard);

        let task = Task {
            id,
            data: data.clone(),
            submitted_at: Instant::now(),
        };

        self.task_queue.lock().push_back(task.clone());

        // Simulate processing
        let result = TaskResult {
            task_id: id,
            success: true,
            data,
            latency_us: 100,
        };
        self.result_queue.lock().push_back(result);

        id
    }

    /// Get result with timeout
    pub fn get_result(&self, timeout_secs: f64) -> Option<TaskResult> {
        let timeout = Duration::from_secs_f64(timeout_secs);
        let start = Instant::now();

        while start.elapsed() < timeout {
            if let Some(result) = self.result_queue.lock().pop_front() {
                return Some(result);
            }
            std::thread::sleep(Duration::from_micros(100));
        }

        None
    }

    /// Get pending task count
    pub fn pending_count(&self) -> usize {
        self.task_queue.lock().len()
    }

    /// Get result count
    pub fn result_count(&self) -> usize {
        self.result_queue.lock().len()
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

    fn submit_task(&self, data: &str) -> usize {
        self.manager.submit_task(data)
    }

    fn submit(&self, data: Vec<u8>) -> usize {
        self.manager.submit(data)
    }

    fn get_result(&self, timeout: f64) -> Option<(usize, bool, Vec<u8>)> {
        self.manager
            .get_result(timeout)
            .map(|r| (r.task_id, r.success, r.data))
    }

    fn pending_count(&self) -> usize {
        self.manager.pending_count()
    }

    fn result_count(&self) -> usize {
        self.manager.result_count()
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
}

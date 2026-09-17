//! SwarmEngine - Core orchestration engine for agent pool management
//!
//! Manages a pool of concurrent agents for high-throughput task processing.

use crossbeam::channel::{bounded, Receiver, Sender, TrySendError};
use parking_lot::Mutex;
use pyo3::prelude::*;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread::{self, JoinHandle};
use std::time::Duration;

const QUEUE_CAPACITY: usize = 1024;
const CHANNEL_POLL_INTERVAL: Duration = Duration::from_millis(10);

/// Core swarm engine managing agent pools
pub struct SwarmEngine {
    agent_count: usize,
    task_sender: Sender<Vec<u8>>,
    result_receiver: Receiver<Vec<u8>>,
    running: Arc<AtomicBool>,
    workers: Mutex<Vec<JoinHandle<()>>>,
}

impl SwarmEngine {
    /// Create a new swarm with specified number of agents
    pub fn new(agent_count: usize) -> Self {
        let agent_count = agent_count.max(1);
        let (task_tx, task_rx) = bounded(QUEUE_CAPACITY);
        let (result_tx, result_rx) = bounded(QUEUE_CAPACITY);
        let running = Arc::new(AtomicBool::new(true));
        let mut workers = Vec::with_capacity(agent_count);

        // Spawn agent threads
        for agent_id in 0..agent_count {
            let task_rx = task_rx.clone();
            let result_tx = result_tx.clone();
            let running = Arc::clone(&running);

            workers.push(thread::spawn(move || {
                while running.load(Ordering::Acquire) {
                    if let Ok(task_data) = task_rx.recv_timeout(CHANNEL_POLL_INTERVAL) {
                        let mut result = Self::process_task(agent_id, task_data);
                        while running.load(Ordering::Acquire) {
                            match result_tx.send_timeout(result, CHANNEL_POLL_INTERVAL) {
                                Ok(()) => break,
                                Err(crossbeam::channel::SendTimeoutError::Timeout(returned)) => {
                                    result = returned;
                                }
                                Err(crossbeam::channel::SendTimeoutError::Disconnected(_)) => break,
                            }
                        }
                    }
                }
            }));
        }

        Self {
            agent_count,
            task_sender: task_tx,
            result_receiver: result_rx,
            running,
            workers: Mutex::new(workers),
        }
    }

    /// Process a single task
    fn process_task(_agent_id: usize, task_data: Vec<u8>) -> Vec<u8> {
        // Phase 4 currently provides an experimental identity transport. It
        // validates bounded scheduling and ownership, not agent semantics.
        task_data
    }

    /// Process a batch of tasks
    pub fn process_batch(&self, count: usize) -> usize {
        let mut submitted = 0;
        let mut received = 0;
        for i in 0..count {
            let mut task = format!("task_{}", i).into_bytes();
            loop {
                if !self.running.load(Ordering::Acquire) {
                    return received;
                }
                match self.task_sender.try_send(task) {
                    Ok(()) => {
                        submitted += 1;
                        break;
                    }
                    Err(TrySendError::Full(returned)) => {
                        task = returned;
                        match self.result_receiver.recv_timeout(CHANNEL_POLL_INTERVAL) {
                            Ok(_) => received += 1,
                            Err(_) if !self.running.load(Ordering::Acquire) => return received,
                            Err(_) => {}
                        }
                    }
                    Err(TrySendError::Disconnected(_)) => return received,
                }
            }
        }

        while received < submitted {
            match self.result_receiver.recv_timeout(CHANNEL_POLL_INTERVAL) {
                Ok(_) => received += 1,
                Err(_) if !self.running.load(Ordering::Acquire) => break,
                Err(_) => {}
            }
        }

        received
    }

    /// Execute tasks in parallel
    pub fn execute_parallel(&self, task_count: usize) -> usize {
        self.process_batch(task_count)
    }

    /// Get agent count
    pub fn agent_count(&self) -> usize {
        self.agent_count
    }

    /// Cancel pending work and wait for all worker threads to stop.
    pub fn shutdown(&self) {
        if !self.running.swap(false, Ordering::AcqRel) {
            return;
        }
        let mut workers = self.workers.lock();
        for worker in workers.drain(..) {
            let _ = worker.join();
        }
    }

    /// Whether this engine still accepts work.
    pub fn is_running(&self) -> bool {
        self.running.load(Ordering::Acquire)
    }
}

impl Drop for SwarmEngine {
    fn drop(&mut self) {
        self.shutdown();
    }
}

/// Python wrapper for SwarmEngine
#[pyclass(name = "SwarmEngine")]
pub struct PySwarmEngine {
    engine: Arc<SwarmEngine>,
}

#[pymethods]
impl PySwarmEngine {
    #[new]
    fn new(agent_count: usize) -> Self {
        Self {
            engine: Arc::new(SwarmEngine::new(agent_count)),
        }
    }

    fn process_batch(&self, py: Python<'_>, count: usize) -> usize {
        py.allow_threads(|| self.engine.process_batch(count))
    }

    fn execute_parallel(&self, py: Python<'_>, task_count: usize) -> usize {
        py.allow_threads(|| self.engine.execute_parallel(task_count))
    }

    fn agent_count(&self) -> usize {
        self.engine.agent_count()
    }

    fn shutdown(&self, py: Python<'_>) {
        py.allow_threads(|| self.engine.shutdown())
    }

    fn is_running(&self) -> bool {
        self.engine.is_running()
    }

    fn process_tasks(&self, tasks: Vec<PyObject>) -> Vec<PyObject> {
        // Explicitly retained as an experimental identity-transport API.
        // Python objects cannot be processed off-GIL; byte-oriented workloads
        // should use `process_batch`, which releases the GIL.
        tasks
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_swarm_creation() {
        let swarm = SwarmEngine::new(10);
        assert_eq!(swarm.agent_count(), 10);
    }

    #[test]
    fn test_swarm_process_batch() {
        let swarm = SwarmEngine::new(100);
        let processed = swarm.process_batch(1000);
        assert_eq!(processed, 1000);
    }

    #[test]
    fn test_swarm_concurrent_agents() {
        let swarm = SwarmEngine::new(1000);
        assert_eq!(swarm.agent_count(), 1000);
    }

    #[test]
    fn test_swarm_high_throughput() {
        let swarm = SwarmEngine::new(500);
        let start = std::time::Instant::now();
        let processed = swarm.process_batch(10000);
        let duration = start.elapsed();

        assert_eq!(processed, 10000);
        let throughput = processed as f64 / duration.as_secs_f64();
        println!("Throughput: {:.0} tasks/s", throughput);
        // CI performance threshold:
        // This lower bound (200 tasks/s) is intentionally conservative for noisy, shared CI
        // runners and is meant to catch catastrophic regressions without causing flaky tests.
        // In practice, local development and production environments are expected to exceed
        // this by a wide margin; CI only needs a stable, non-flaky lower bound signal.
        assert!(
            throughput > 200.0,
            "Throughput too low: {:.0} tasks/s",
            throughput
        );
    }

    #[test]
    fn test_shutdown_is_idempotent() {
        let swarm = SwarmEngine::new(2);
        assert!(swarm.is_running());
        swarm.shutdown();
        swarm.shutdown();
        assert!(!swarm.is_running());
        assert_eq!(swarm.process_batch(1), 0);
    }

    #[test]
    fn test_batch_larger_than_queue_capacity() {
        let swarm = SwarmEngine::new(2);
        assert_eq!(swarm.process_batch(QUEUE_CAPACITY * 3), QUEUE_CAPACITY * 3);
    }
}

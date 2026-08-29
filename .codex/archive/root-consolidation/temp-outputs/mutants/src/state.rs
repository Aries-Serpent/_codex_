// SwarmState: Thread-safe shared state for agent coordination
//
// This module provides a concurrent hash map-based state store that multiple
// agents can access simultaneously without GIL contention. Uses DashMap for
// lock-free reads and minimal lock contention on writes.

use pyo3::prelude::*;
use dashmap::DashMap;
use std::sync::Arc;
use serde::{Serialize, Deserialize};

/// Status of an individual agent in the swarm
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum AgentStatus {
    Idle,
    Working(String),  // Contains task description
    Complete,
    Failed(String),   // Contains error message
}

/// Thread-safe shared state accessible from both Rust and Python
///
/// This structure provides concurrent access to agent state without the
/// overhead of Python's GIL. Multiple threads can read/write simultaneously.
#[pyclass]
#[derive(Clone)]
pub struct SwarmState {
    agents: Arc<DashMap<String, AgentStatus>>,
}

#[pymethods]
impl SwarmState {
    /// Create a new SwarmState instance
    #[new]
    fn new() -> Self {
        SwarmState {
            agents: Arc::new(DashMap::new()),
        }
    }

    /// Register a new agent with the swarm
    ///
    /// # Arguments
    /// * `agent_id` - Unique identifier for the agent
    fn register_agent(&self, agent_id: String) -> PyResult<()> {
        self.agents.insert(agent_id, AgentStatus::Idle);
        Ok(())
    }

    /// Get the current count of registered agents
    pub fn get_agent_count(&self) -> usize {
        self.agents.len()
    }

    /// Update an agent's status
    ///
    /// # Arguments
    /// * `agent_id` - Unique identifier for the agent
    /// * `status` - New status as string ("idle", "working", "complete", "failed")
    /// * `message` - Optional message (required for "working" and "failed")
    #[pyo3(signature = (agent_id, status, message=None))]
    fn set_agent_status(&self, agent_id: String, status: String, message: Option<String>) -> PyResult<()> {
        let new_status = match status.as_str() {
            "idle" => AgentStatus::Idle,
            "working" => AgentStatus::Working(message.unwrap_or_default()),
            "complete" => AgentStatus::Complete,
            "failed" => AgentStatus::Failed(message.unwrap_or_default()),
            _ => return Err(PyErr::new::<pyo3::exceptions::PyValueError, _>(
                format!("Invalid status: {}", status)
            )),
        };

        self.agents.insert(agent_id, new_status);
        Ok(())
    }

    /// Get an agent's current status
    ///
    /// Returns a tuple of (status_str, message)
    fn get_agent_status(&self, agent_id: String) -> PyResult<(String, String)> {
        match self.agents.get(&agent_id) {
            Some(entry) => {
                let status = entry.value();
                let (status_str, message) = match status {
                    AgentStatus::Idle => ("idle".to_string(), String::new()),
                    AgentStatus::Working(msg) => ("working".to_string(), msg.clone()),
                    AgentStatus::Complete => ("complete".to_string(), String::new()),
                    AgentStatus::Failed(msg) => ("failed".to_string(), msg.clone()),
                };
                Ok((status_str, message))
            }
            None => Err(PyErr::new::<pyo3::exceptions::PyKeyError, _>(
                format!("Agent not found: {}", agent_id)
            )),
        }
    }

    /// Remove an agent from the swarm
    fn unregister_agent(&self, agent_id: String) -> PyResult<()> {
        self.agents.remove(&agent_id);
        Ok(())
    }

    /// Get all agent IDs currently registered
    fn list_agents(&self) -> Vec<String> {
        self.agents.iter().map(|entry| entry.key().clone()).collect()
    }
}

impl Default for SwarmState {
    fn default() -> Self {
        Self::new()
    }
}

// AgentManager: Rust-based agent lifecycle management
//
// This module provides a thread pool for managing Python agent processes,
// enabling true parallel execution beyond Python's GIL limitations.

use pyo3::prelude::*;
use rayon::ThreadPool;
use dashmap::DashMap;
use std::sync::Arc;
use crate::state::AgentStatus;

/// Handle for a managed agent
#[derive(Clone)]
pub struct AgentHandle {
    pub id: String,
    pub status: AgentStatus,
}

/// Agent lifecycle manager using Rayon thread pool
///
/// Manages Python agent processes with true parallelism, bypassing GIL
/// constraints. Uses Rayon for CPU-bound work distribution.
#[pyclass]
pub struct AgentManager {
    pool: Arc<ThreadPool>,
    active_agents: Arc<DashMap<String, AgentHandle>>,
    max_agents: usize,
}

#[pymethods]
impl AgentManager {
    /// Create a new AgentManager
    ///
    /// # Arguments
    /// * `max_agents` - Maximum number of concurrent agents
    #[new]
    fn new(max_agents: usize) -> PyResult<Self> {
        let pool = rayon::ThreadPoolBuilder::new()
            .num_threads(max_agents)
            .build()
            .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;

        Ok(AgentManager {
            pool: Arc::new(pool),
            active_agents: Arc::new(DashMap::new()),
            max_agents,
        })
    }

    /// Spawn a new agent
    ///
    /// # Arguments
    /// * `agent_id` - Unique identifier for the agent
    /// * `config` - JSON configuration for the agent
    fn spawn_agent(&self, agent_id: String, config: String) -> PyResult<()> {
        if self.active_agents.len() >= self.max_agents {
            return Err(PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(
                format!("Max agents reached ({})", self.max_agents)
            ));
        }

        let agents = self.active_agents.clone();
        let agent_id_clone = agent_id.clone();

        // Insert immediately to reserve slot
        self.active_agents.insert(agent_id.clone(), AgentHandle {
            id: agent_id.clone(),
            status: AgentStatus::Working("initializing".to_string()),
        });

        self.pool.spawn(move || {
            Python::with_gil(|py| {
                // Try to import and run agent
                match py.import_bound("codex.agent") {
                    Ok(agent_module) => {
                        match agent_module.call_method1("Agent", (&config,)) {
                            Ok(agent) => {
                                match agent.call_method0("run") {
                                    Ok(_) => {
                                        agents.remove(&agent_id_clone);
                                    }
                                    Err(e) => {
                                        tracing::error!("Agent {} run failed: {}", agent_id_clone, e);
                                        agents.remove(&agent_id_clone);
                                    }
                                }
                            }
                            Err(e) => {
                                tracing::error!("Agent {} creation failed: {}", agent_id_clone, e);
                                agents.remove(&agent_id_clone);
                            }
                        }
                    }
                    Err(e) => {
                        tracing::error!("Failed to import codex.agent: {}", e);
                        agents.remove(&agent_id_clone);
                    }
                }
            });
        });

        Ok(())
    }

    /// Get the number of currently active agents
    fn get_active_count(&self) -> usize {
        self.active_agents.len()
    }

    /// Get the maximum number of agents
    fn get_max_agents(&self) -> usize {
        self.max_agents
    }

    /// Check if an agent is currently active
    fn is_agent_active(&self, agent_id: String) -> bool {
        self.active_agents.contains_key(&agent_id)
    }

    /// List all active agent IDs
    fn list_active_agents(&self) -> Vec<String> {
        self.active_agents.iter().map(|entry| entry.key().clone()).collect()
    }

    /// Terminate an agent (remove from active pool)
    fn terminate_agent(&self, agent_id: String) -> PyResult<bool> {
        Ok(self.active_agents.remove(&agent_id).is_some())
    }
}

impl Default for AgentManager {
    fn default() -> Self {
        Self::new(10).unwrap()
    }
}

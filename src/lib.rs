// Codex Swarm Engine - Rust orchestration layer for Python AI agents
// This module provides high-performance orchestration primitives that eliminate
// GIL bottlenecks and enable 500+ concurrent agents with minimal memory overhead.

use pyo3::prelude::*;

mod state;
mod runtime;
mod queue;
mod agent_manager;
mod compression;
mod serialization;

pub use state::SwarmState;
pub use runtime::Orchestrator;
pub use queue::{TaskQueue, Task};
pub use agent_manager::AgentManager;
pub use compression::CompressionPipeline;
pub use serialization::AgentState;

/// The main Python module for codex_engine
/// 
/// This module exposes Rust-based primitives to Python for high-performance
/// agent orchestration. It replaces GIL-bound Python execution with true
/// parallelism using Tokio and Rayon.
#[pymodule]
fn codex_engine(py: Python, m: &Bound<'_, pyo3::types::PyModule>) -> PyResult<()> {
    // Core orchestration
    m.add_class::<SwarmState>()?;
    m.add_class::<Orchestrator>()?;
    m.add_class::<TaskQueue>()?;
    m.add_class::<Task>()?;
    
    // Agent lifecycle
    m.add_class::<AgentManager>()?;
    
    // Data optimization
    m.add_class::<CompressionPipeline>()?;
    
    // Serialization
    serialization::register_module(py, m)?;
    
    m.add("__version__", env!("CARGO_PKG_VERSION"))?;
    m.add("__doc__", "Rust orchestration layer for Codex AI Agent Swarm")?;
    
    Ok(())
}

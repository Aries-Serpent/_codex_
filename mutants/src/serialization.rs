// Serialization: MessagePack binary serialization
//
// High-performance binary serialization via Serde and MessagePack

use pyo3::prelude::*;
use pyo3::types::PyBytes;
use serde::{Serialize, Deserialize};
use std::collections::HashMap;

/// Agent state for serialization
///
/// Serializable agent state structure with MessagePack support
#[derive(Serialize, Deserialize, Clone, Debug)]
#[pyclass]
pub struct AgentState {
    #[pyo3(get, set)]
    pub id: String,

    #[pyo3(get, set)]
    pub memory: Vec<String>,

    // Note: Python access to metrics requires custom getters/setters
    pub metrics: HashMap<String, f64>,
}

#[pymethods]
impl AgentState {
    /// Create a new AgentState
    ///
    /// # Arguments
    /// * `id` - Agent identifier
    /// * `memory` - List of memory items
    #[new]
    fn new(id: String, memory: Vec<String>) -> Self {
        AgentState {
            id,
            memory,
            metrics: HashMap::new(),
        }
    }

    /// Set a metric value
    fn set_metric(&mut self, key: String, value: f64) {
        self.metrics.insert(key, value);
    }

    /// Get a metric value
    fn get_metric(&self, key: String) -> Option<f64> {
        self.metrics.get(&key).copied()
    }

    /// Get all metric keys
    fn get_metric_keys(&self) -> Vec<String> {
        self.metrics.keys().cloned().collect()
    }
}

/// Serialize agent state to MessagePack bytes
#[pyfunction]
fn serialize_state<'py>(py: Python<'py>, state: &AgentState) -> PyResult<Bound<'py, PyBytes>> {
    let bytes = rmp_serde::to_vec(state)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    Ok(PyBytes::new_bound(py, &bytes))
}

/// Deserialize agent state from MessagePack bytes
#[pyfunction]
fn deserialize_state(data: &[u8]) -> PyResult<AgentState> {
    rmp_serde::from_slice(data)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
}

/// Serialize any Python-compatible data to MessagePack
#[pyfunction]
fn serialize_bytes<'py>(py: Python<'py>, obj: PyObject) -> PyResult<Bound<'py, PyBytes>> {
    // For generic Python objects, we'd need to use PyO3's pickle or JSON
    // For now, use a simpler approach with string representation
    let json_str: String = obj.extract(py)?;
    let bytes = rmp_serde::to_vec(&json_str)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    Ok(PyBytes::new_bound(py, &bytes))
}

/// Deserialize MessagePack bytes to string
#[pyfunction]
fn deserialize_bytes(data: &[u8]) -> PyResult<String> {
    rmp_serde::from_slice(data)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))
}

pub fn register_module(_py: Python, parent_module: &Bound<'_, pyo3::types::PyModule>) -> PyResult<()> {
    parent_module.add_function(wrap_pyfunction!(serialize_state, parent_module)?)?;
    parent_module.add_function(wrap_pyfunction!(deserialize_state, parent_module)?)?;
    parent_module.add_function(wrap_pyfunction!(serialize_bytes, parent_module)?)?;
    parent_module.add_function(wrap_pyfunction!(deserialize_bytes, parent_module)?)?;
    parent_module.add_class::<AgentState>()?;
    Ok(())
}

use std::sync::Arc;
use std::time::Duration;

use pyo3::exceptions::PyTypeError;
use pyo3::prelude::*;
use pyo3::{Bound, PyObject};
use pyo3_async_runtimes::tokio::{future_into_py, into_future};
use tokio::sync::Mutex;

#[pyclass]
pub struct Orchestrator {
    callback: PyObject,
    state: Arc<Mutex<String>>,
}

#[pymethods]
impl Orchestrator {
    #[new]
    fn new(callback: PyObject, py: Python<'_>) -> PyResult<Self> {
        if !callback.bind(py).is_callable() {
            return Err(PyTypeError::new_err(
                "Orchestrator callback must be a callable async function",
            ));
        }

        Ok(Self {
            callback,
            state: Arc::new(Mutex::new("idle".to_string())),
        })
    }

    fn triage_failure<'py>(
        &self,
        py: Python<'py>,
        error_type: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let callback = self.callback.clone_ref(py);
        let state = Arc::clone(&self.state);

        future_into_py(py, async move {
            {
                let mut guard = state.lock().await;
                *guard = format!("triaging:{error_type}");
            }

            // Heavy I/O simulation occurs fully outside the GIL.
            tokio::time::sleep(Duration::from_millis(150)).await;

            // Re-acquire GIL only to build the Python coroutine and convert it to a Rust future.
            let py_future = Python::with_gil(|py| -> PyResult<_> {
                let coroutine = callback.call1(py, (error_type.clone(),))?;
                into_future(coroutine.into_bound(py))
            })?;

            // Await Python callback outside the GIL to avoid deadlocks.
            let patch_obj = py_future.await?;
            let patch_text = Python::with_gil(|py| -> PyResult<String> { patch_obj.extract(py) })?;

            {
                let mut guard = state.lock().await;
                *guard = "patched".to_string();
            }

            Ok::<String, PyErr>(patch_text)
        })
    }

    fn get_state<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let state = Arc::clone(&self.state);

        future_into_py(py, async move {
            let snapshot = {
                let guard = state.lock().await;
                guard.clone()
            };
            Ok(snapshot)
        })
    }
}

#[pymodule]
fn codex_core(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<Orchestrator>()?;
    Ok(())
}

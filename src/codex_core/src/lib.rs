use std::sync::Arc;
use std::time::Duration;

use pyo3::exceptions::{PyRuntimeError, PyTimeoutError, PyTypeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyModule, PyString};
use pyo3::{Bound, PyObject};
use pyo3_async_runtimes::tokio::{future_into_py, into_future};
use tokio::sync::Mutex;
use tokio::time::timeout;
use tracing::{error, info, warn};

#[pyclass]
pub struct Orchestrator {
    callback: PyObject,
    state: Arc<Mutex<String>>,
    timeout_seconds: u64,
}

#[pymethods]
impl Orchestrator {
    #[new]
    #[pyo3(signature = (callback, timeout_seconds=60))]
    fn new(callback: PyObject, timeout_seconds: u64, py: Python<'_>) -> PyResult<Self> {
        if !callback.bind(py).is_callable() {
            return Err(PyTypeError::new_err(
                "Orchestrator callback must be a callable async function",
            ));
        }

        if timeout_seconds == 0 {
            return Err(PyValueError::new_err("timeout_seconds must be >= 1"));
        }

        info!(timeout_seconds, "orchestrator initialized");

        Ok(Self {
            callback,
            state: Arc::new(Mutex::new("clean".to_string())),
            timeout_seconds,
        })
    }

    fn triage_failure<'py>(
        &self,
        py: Python<'py>,
        error_type: String,
    ) -> PyResult<Bound<'py, PyAny>> {
        let callback = self.callback.clone_ref(py);
        let state = Arc::clone(&self.state);
        let timeout_seconds = self.timeout_seconds;

        future_into_py(py, async move {
            use futures::FutureExt;

            let guarded = std::panic::AssertUnwindSafe(async {
                info!(%error_type, "triage start: acquiring state lock");
                {
                    let mut guard = state.lock().await;
                    *guard = format!("triaging:{error_type}");
                }
                info!(%error_type, "state set to triaging");

                info!(%error_type, "heavy I/O simulation start");
                tokio::time::sleep(Duration::from_millis(150)).await;
                info!(%error_type, "heavy I/O simulation complete");

                let log_excerpt = format!("mock-log: failure detected => {error_type}");

                let py_future = Python::with_gil(|py| -> PyResult<_> {
                    info!(%error_type, "invoking python callback");
                    let coroutine = callback.call1(py, (error_type.clone(), log_excerpt.clone()))?;
                    into_future(coroutine.into_bound(py))
                })?;

                let py_result_obj = match timeout(Duration::from_secs(timeout_seconds), py_future).await {
                    Ok(Ok(obj)) => {
                        info!(%error_type, "python callback completed");
                        obj
                    }
                    Ok(Err(e)) => {
                        warn!(%error_type, "python callback raised exception");
                        let mut guard = state.lock().await;
                        *guard = format!("failed:{error_type}:callback_error");
                        return Err(e);
                    }
                    Err(_) => {
                        warn!(%error_type, timeout_seconds, "python callback timeout");
                        let mut guard = state.lock().await;
                        *guard = format!("failed:{error_type}:timeout");
                        return Err(PyTimeoutError::new_err(format!(
                            "callback timed out for error_type='{error_type}' after {timeout_seconds} seconds"
                        )));
                    }
                };

                let patch_text = Python::with_gil(|py| -> PyResult<String> {
                    if py_result_obj.bind(py).is_instance_of::<PyString>() {
                        py_result_obj.bind(py).extract::<String>()
                    } else {
                        Err(PyRuntimeError::new_err(
                            "callback must resolve to a string patch payload",
                        ))
                    }
                })?;

                {
                    let mut guard = state.lock().await;
                    *guard = "patched".to_string();
                }
                info!(%error_type, "triage complete: state set to patched");

                Ok::<String, PyErr>(patch_text)
            });

            match guarded.catch_unwind().await {
                Ok(inner) => inner,
                Err(_) => {
                    error!(%error_type, "panic during triage");
                    let mut guard = state.lock().await;
                    *guard = format!("failed:{error_type}:panic");
                    Err(PyRuntimeError::new_err(format!(
                        "orchestrator panicked during triage for error_type='{error_type}'"
                    )))
                }
            }
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
fn codex_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Bridge Rust logs into Python logging
    pyo3_log::init();
    // Also initialize Rust subscriber for local/native contexts
    let _ = tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "info".into()),
        )
        .try_init();

    m.add_class::<Orchestrator>()?;
    Ok(())
}
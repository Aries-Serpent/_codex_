use std::collections::HashMap;
use std::sync::Arc;
use std::time::Duration;

use pyo3::exceptions::{PyRuntimeError, PyTimeoutError, PyTypeError, PyValueError};
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyModule, PyString};
use pyo3::{Bound, PyObject};
use pyo3_async_runtimes::tokio::{future_into_py, into_future};
use tokio::sync::Mutex;
use tokio::time::timeout;
use tracing::{error, info, warn};

const UNRESOLVED_TOKENS: [&str; 3] = ["UNABLE_TO_CLASSIFY", "FIX_FAILED", "NO_ACTIONABLE_FIX"];

#[derive(Debug, Clone, Default)]
struct Telemetry {
    total_triage: u64,
    success: u64,
    unresolved: u64,
    callback_error: u64,
    timeout: u64,
    panic: u64,
}

#[pyclass]
pub struct Orchestrator {
    callback: PyObject,
    // keyed state: error_type -> status
    state: Arc<Mutex<HashMap<String, String>>>,
    timeout_seconds: u64,
    telemetry: Arc<Mutex<Telemetry>>,
}

fn is_unresolved_payload(payload: &str) -> bool {
    let upper = payload.to_ascii_uppercase();
    UNRESOLVED_TOKENS.iter().any(|t| upper.contains(t))
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
            state: Arc::new(Mutex::new(HashMap::new())),
            timeout_seconds,
            telemetry: Arc::new(Mutex::new(Telemetry::default())),
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
        let telemetry = Arc::clone(&self.telemetry);

        future_into_py(py, async move {
            use futures::FutureExt;

            {
                let mut t = telemetry.lock().await;
                t.total_triage += 1;
            }

            let guarded = std::panic::AssertUnwindSafe(async {
                info!(%error_type, "triage start: acquiring state lock");
                {
                    let mut guard = state.lock().await;
                    guard.insert(error_type.clone(), "triaging".to_string());
                }

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
                    Ok(Ok(obj)) => obj,
                    Ok(Err(e)) => {
                        warn!(%error_type, "python callback raised exception");
                        {
                            let mut t = telemetry.lock().await;
                            t.callback_error += 1;
                        }
                        let mut guard = state.lock().await;
                        guard.insert(error_type.clone(), "failed:callback_error".to_string());
                        return Err(e);
                    }
                    Err(_) => {
                        warn!(%error_type, timeout_seconds, "python callback timeout");
                        {
                            let mut t = telemetry.lock().await;
                            t.timeout += 1;
                        }
                        let mut guard = state.lock().await;
                        guard.insert(error_type.clone(), "failed:timeout".to_string());
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

                if is_unresolved_payload(&patch_text) {
                    {
                        let mut t = telemetry.lock().await;
                        t.unresolved += 1;
                    }
                    let mut guard = state.lock().await;
                    guard.insert(error_type.clone(), "unresolved".to_string());
                    return Ok(patch_text);
                }

                {
                    let mut guard = state.lock().await;
                    guard.insert(error_type.clone(), "patched".to_string());
                }
                {
                    let mut t = telemetry.lock().await;
                    t.success += 1;
                }

                Ok::<String, PyErr>(patch_text)
            });

            match guarded.catch_unwind().await {
                Ok(inner) => inner,
                Err(_) => {
                    error!(%error_type, "panic during triage");
                    {
                        let mut t = telemetry.lock().await;
                        t.panic += 1;
                    }
                    let mut guard = state.lock().await;
                    guard.insert(error_type.clone(), "failed:panic".to_string());
                    Err(PyRuntimeError::new_err(format!(
                        "orchestrator panicked during triage for error_type='{error_type}'"
                    )))
                }
            }
        })
    }

    #[pyo3(signature = (error_types, max_concurrency=4))]
    fn triage_batch<'py>(
        &self,
        py: Python<'py>,
        error_types: Vec<String>,
        max_concurrency: usize,
    ) -> PyResult<Bound<'py, PyAny>> {
        if max_concurrency == 0 {
            return Err(PyValueError::new_err("max_concurrency must be >= 1"));
        }

        let callback = self.callback.clone_ref(py);
        let state = Arc::clone(&self.state);
        let telemetry = Arc::clone(&self.telemetry);
        let timeout_seconds = self.timeout_seconds;

        future_into_py(py, async move {
            let semaphore = Arc::new(tokio::sync::Semaphore::new(max_concurrency));
            let mut handles = Vec::with_capacity(error_types.len());

            for error_type in error_types {
                let permitter = Arc::clone(&semaphore);
                let cb = callback.clone();
                let st = Arc::clone(&state);
                let tm = Arc::clone(&telemetry);

                handles.push(tokio::spawn(async move {
                    let _permit = permitter.acquire_owned().await.map_err(|e| {
                        PyRuntimeError::new_err(format!("semaphore acquire failed: {e}"))
                    })?;

                    {
                        let mut t = tm.lock().await;
                        t.total_triage += 1;
                    }

                    {
                        let mut guard = st.lock().await;
                        guard.insert(error_type.clone(), "triaging".to_string());
                    }

                    tokio::time::sleep(Duration::from_millis(50)).await;
                    let log_excerpt = format!("batch-mock-log: failure => {error_type}");

                    let py_future = Python::with_gil(|py| -> PyResult<_> {
                        let coroutine = cb.call1(py, (error_type.clone(), log_excerpt.clone()))?;
                        into_future(coroutine.into_bound(py))
                    })?;

                    let result = match timeout(Duration::from_secs(timeout_seconds), py_future).await {
                        Ok(Ok(obj)) => {
                            let patch = Python::with_gil(|py| -> PyResult<String> {
                                if obj.bind(py).is_instance_of::<PyString>() {
                                    obj.bind(py).extract::<String>()
                                } else {
                                    Err(PyRuntimeError::new_err(
                                        "callback must resolve to a string patch payload",
                                    ))
                                }
                            })?;

                            if is_unresolved_payload(&patch) {
                                {
                                    let mut t = tm.lock().await;
                                    t.unresolved += 1;
                                }
                                {
                                    let mut guard = st.lock().await;
                                    guard.insert(error_type.clone(), "unresolved".to_string());
                                }
                                Ok((error_type, false, patch))
                            } else {
                                {
                                    let mut t = tm.lock().await;
                                    t.success += 1;
                                }
                                {
                                    let mut guard = st.lock().await;
                                    guard.insert(error_type.clone(), "patched".to_string());
                                }
                                Ok((error_type, true, patch))
                            }
                        }
                        Ok(Err(e)) => {
                            {
                                let mut t = tm.lock().await;
                                t.callback_error += 1;
                            }
                            {
                                let mut guard = st.lock().await;
                                guard.insert(error_type.clone(), "failed:callback_error".to_string());
                            }
                            Err(e)
                        }
                        Err(_) => {
                            {
                                let mut t = tm.lock().await;
                                t.timeout += 1;
                            }
                            {
                                let mut guard = st.lock().await;
                                guard.insert(error_type.clone(), "failed:timeout".to_string());
                            }
                            Err(PyTimeoutError::new_err(format!(
                                "batch callback timed out for error_type='{error_type}' after {timeout_seconds} seconds"
                            )))
                        }
                    };

                    result
                }));
            }

            let mut out: Vec<(String, bool, String)> = Vec::new();
            for h in handles {
                match h.await {
                    Ok(Ok(tuple)) => out.push(tuple),
                    Ok(Err(e)) => return Err(e),
                    Err(e) => {
                        {
                            let mut t = telemetry.lock().await;
                            t.panic += 1;
                        }
                        return Err(PyRuntimeError::new_err(format!(
                            "batch worker join/panic error: {e}"
                        )));
                    }
                }
            }

            Ok(out)
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

    fn get_telemetry<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyAny>> {
        let telemetry = Arc::clone(&self.telemetry);

        future_into_py(py, async move {
            Python::with_gil(|py| -> PyResult<PyObject> {
                let t = telemetry.lock().await.clone();
                let d = PyDict::new_bound(py);
                d.set_item("total_triage", t.total_triage)?;
                d.set_item("success", t.success)?;
                d.set_item("unresolved", t.unresolved)?;
                d.set_item("callback_error", t.callback_error)?;
                d.set_item("timeout", t.timeout)?;
                d.set_item("panic", t.panic)?;
                Ok(d.into_py(py))
            })
        })
    }
}

#[pymodule]
fn codex_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    pyo3_log::init();
    let _ = tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env().unwrap_or_else(|_| "info".into()),
        )
        .try_init();

    m.add_class::<Orchestrator>()?;
    Ok(())
}
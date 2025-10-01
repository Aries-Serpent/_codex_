# Observability

Codex runs default to offline-friendly logging and metrics capture to avoid network egress. The telemetry module still exposes Prometheus counters when the local agent is launched, and can be enabled via the CLI:

```bash
python -m codex_ml.telemetry.server
```

Use `track_time` to instrument functions and expose metrics on `/metrics`.

## Offline tracking workflow

- `codex_ml.tracking.mlflow_guard.ensure_file_backend()` forces a `file:`-scoped MLflow tracking URI (`artifacts/mlruns` by default) and creates the directory if it is missing. The helper is invoked automatically by `MLflowWriter` and the MLflow utility layer.
- TensorBoard, MLflow, and Weights & Biases writers emit a deterministic `tracking_summary.ndjson` alongside the run directory summarising which backends were enabled and why others degraded. Each entry captures the psutil/NVML availability flags so GPU sampling gaps are explicit.
- Metric rows always land in `metrics.ndjson` with a canonical key order; the file can be tailed safely or ingested downstream without schema drift.

### Residual risks

- Rotation for `tracking_summary.ndjson` remains manual; very large sweeps may require post-run log truncation.
- psutil/NVML availability is only sampled at writer initialisation. Long-lived training jobs should still watch the system metrics logs for runtime degradation events.

### Rollback

- Remove the tracking writers or delete `tracking_summary.ndjson` and unset `CODEX_MLFLOW_LOCAL_DIR` to return to the pre-hardened behaviour.

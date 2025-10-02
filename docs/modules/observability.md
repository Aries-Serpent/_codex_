# Observability

Codex runs default to offline-friendly logging and metrics capture to avoid network egress. The telemetry module still exposes Prometheus counters when the local agent is launched, and can be enabled via the CLI:

```bash
python -m codex_ml.telemetry.server
```

Use `track_time` to instrument functions and expose metrics on `/metrics`.

## Offline tracking workflow

- `codex_ml.tracking.mlflow_guard.ensure_file_backend()` forces a `file:`-scoped MLflow tracking URI (`artifacts/mlruns` by default), normalises plain filesystem paths to canonical `file://` URIs, and creates the directory if it is missing. The helper is invoked automatically by `MLflowWriter`, `mlflow_utils.bootstrap_offline_tracking()`, `codex_ml.utils.experiment_tracking_mlflow.ensure_local_tracking()`, and the offline smoke tests. `MLflowWriter` falls back to the guarded URI whenever a non-`file:` URI is supplied and captures the `requested_uri`/`fallback_reason` in `tracking_summary.ndjson` so reviewers can confirm the downgrade was intentional.
- TensorBoard, MLflow, and Weights & Biases writers emit a deterministic `tracking_summary.ndjson` alongside the run directory summarising which backends were enabled and why others degraded. Each entry captures the psutil/NVML availability flags so GPU sampling gaps are explicit.
- Metric rows always land in `metrics.ndjson` with a canonical key order; every record now carries `run_id`, `step`, `split`, and a UTC ISO `timestamp` (unless the legacy toggle is set). Structured payloads emit descriptors to `metrics_manifest.ndjson` and the originating scalar row references them via `tags.manifest_id`. Evaluation runs reuse the same writer with an explicit `tags.phase` so downstream tooling can distinguish training/eval emissions without ad hoc parsing.
- Rotation can be tuned via environment variables. Defaults are conservative (`64 MiB`, `24 h`, retain `5` shards) but can be disabled by exporting `None` or `0`:
  - `CODEX_TRACKING_NDJSON_MAX_BYTES` → rotate once the active shard exceeds this many bytes.
  - `CODEX_TRACKING_NDJSON_MAX_AGE_S` → rotate when the shard has not been touched for `N` seconds.
  - `CODEX_TRACKING_NDJSON_BACKUP_COUNT` → retain this many rotated files (`metrics.ndjson`, `metrics.ndjson.1`, …).
- Legacy consumers can opt out of the extended schema by exporting `CODEX_TRACKING_LEGACY_NDJSON=1` (alias: `LOGGING_NDJSON_LEGACY=1`).
- Summarise rotated metric shards with `codex-ndjson summarize --input <run-dir> --output csv` (CSV) or `--output parquet` (requires pandas). The CLI merges all `metrics.ndjson*` shards oldest→newest, computes per-metric aggregates (count/min/max/mean plus first/last timestamps/values/phases), tracks manifest IDs, and emits a tidy table ordered chronologically. Both `codex_ml` and utility CLIs route through the same summarizer implementation.
- Offline MLflow bootstrap can be smoke-tested with `python examples/mlflow_offline.py --output /tmp/mlruns`; the helper logs params, metrics, and an artifact while asserting a local `file:` URI and verifying the guard wiring end-to-end.

### Residual risks

- Rotation for `tracking_summary.ndjson` remains manual; very large sweeps may require post-run log truncation.
- psutil/NVML availability is only sampled at writer initialisation. Long-lived training jobs should still watch the system metrics logs for runtime degradation events.

### Rollback

- Remove the tracking writers or delete `tracking_summary.ndjson` and unset `CODEX_MLFLOW_LOCAL_DIR` to return to the pre-hardened behaviour. Clearing `CODEX_TRACKING_LEGACY_NDJSON` restores the enriched NDJSON schema. Disable rotation by exporting `CODEX_TRACKING_NDJSON_MAX_BYTES=` and `CODEX_TRACKING_NDJSON_MAX_AGE_S=` (empty) if required during rollback.

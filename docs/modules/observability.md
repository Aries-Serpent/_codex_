# Observability

Codex runs default to offline-friendly logging and metrics capture to avoid network egress. The telemetry module still exposes Prometheus counters when the local agent is launched, and can be enabled via the CLI:

```bash
python -m codex_ml.telemetry.server
```

Use `track_time` to instrument functions and expose metrics on `/metrics`.

## Offline tracking workflow

- `codex_ml.tracking.mlflow_guard.bootstrap_offline_tracking()` forces a `file:`-scoped MLflow tracking URI (`artifacts/mlruns` by default), normalises plain filesystem paths to canonical `file://` URIs, and creates the directory if it is missing. Set `MLFLOW_ALLOW_REMOTE=1` (or the legacy `CODEX_MLFLOW_ALLOW_REMOTE=1`) to opt back into an explicitly configured remote backend. The helper is invoked automatically by `MLflowWriter`, `mlflow_utils.bootstrap_offline_tracking()`, `codex_ml.utils.experiment_tracking_mlflow.ensure_local_tracking()`, and the offline smoke CLI. Each guard invocation records its outcome via `codex_ml.tracking.mlflow_guard.last_decision()` so writers can persist audit fields.
- TensorBoard, MLflow, and Weights & Biases writers emit a deterministic `tracking_summary.ndjson` alongside the run directory summarising which backends were enabled and why others degraded. Each MLflow entry now includes the guard telemetry fields below so responders can prove which URI was requested, what was enforced, and whether remote logging was explicitly allowed. psutil/NVML availability flags remain so GPU sampling gaps are explicit.

| Field | Description |
| --- | --- |
| `requested_uri` | Raw URI supplied by the caller or environment. |
| `effective_uri` / `tracking_uri` | Final URI after the guard normalised or downgraded the request. |
| `fallback_reason` | Empty when no downgrade occurred, otherwise `remote_disallowed` for blocked remote URIs. |
| `allow_remote_flag` | Raw value of `MLFLOW_ALLOW_REMOTE`/`CODEX_MLFLOW_ALLOW_REMOTE`. |
| `allow_remote_env` | Environment variable that granted (or denied) the remote opt-in. |
| `allow_remote` | Boolean indicating whether remote tracking was permitted for the decision. |
| `system_metrics_enabled` | Boolean derived from `MLFLOW_ENABLE_SYSTEM_METRICS` after the guard executed. |
| `dependencies` | psutil/NVML availability snapshot for the component. |
- Metric rows always land in `metrics.ndjson` with a canonical key order; every record now carries `run_id`, `step`, `split`, and a UTC ISO `timestamp` (unless the legacy toggle is set). Structured payloads emit descriptors to `metrics_manifest.ndjson` (type/path/shape/version plus the full payload) and the originating scalar row references them via `tags.manifest_id`. Evaluation runs reuse the same writer with an explicit `tags.phase` so downstream tooling can distinguish training/eval emissions without ad hoc parsing.
- Rotation can be tuned via environment variables. Defaults are conservative (`64 MiB`, `24 h`, retain `5` shards) but can be disabled by exporting `None` or `0`. The same thresholds now apply to `tracking_summary.ndjson` and all rotated shards use numeric suffixes (`.1`, `.2`, …):
  - `CODEX_TRACKING_NDJSON_MAX_BYTES` → rotate once the active shard exceeds this many bytes.
  - `CODEX_TRACKING_NDJSON_MAX_AGE_S` → rotate when the shard has not been touched for `N` seconds.
  - `CODEX_TRACKING_NDJSON_BACKUP_COUNT` → retain this many rotated files (`metrics.ndjson`, `metrics.ndjson.1`, …).
- Legacy consumers can opt out of the extended schema by exporting `CODEX_TRACKING_LEGACY_NDJSON=1` (alias: `LOGGING_NDJSON_LEGACY=1`).
- Summarise rotated metric shards with `codex-ndjson summarize --input <run-dir> --output csv` (CSV) or `--output parquet` (requires pandas). The CLI merges all `metrics.ndjson*` shards oldest→newest, computes per-metric aggregates (count/min/max/mean plus first/last timestamps/values/phases), tracks manifest IDs, and emits a tidy table ordered chronologically. Both `codex_ml` and utility CLIs route through the same summarizer implementation.
- Offline MLflow bootstrap can be smoke-tested with `python examples/mlflow_offline.py --output /tmp/mlruns`; the helper now logs metrics via `RunLogger`, writes a `tracking_summary.ndjson`, and exits with a clear error if a remote URI is requested without setting `MLFLOW_ALLOW_REMOTE=1`.

### Residual risks

- psutil/NVML availability is only sampled at writer initialisation. Long-lived training jobs should still watch the system metrics logs for runtime degradation events.

### Rollback

- Remove the tracking writers or delete `tracking_summary.ndjson` and unset `CODEX_MLFLOW_LOCAL_DIR` to return to the pre-hardened behaviour. Clearing `CODEX_TRACKING_LEGACY_NDJSON` restores the enriched NDJSON schema. Disable rotation by exporting `CODEX_TRACKING_NDJSON_MAX_BYTES=` and `CODEX_TRACKING_NDJSON_MAX_AGE_S=` (empty) if required during rollback.

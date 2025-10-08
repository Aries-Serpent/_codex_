# Observability

Codex runs default to offline-friendly logging and metrics capture to avoid network egress. The telemetry module still exposes Prometheus counters when the local agent is launched, and can be enabled via the CLI:

```bash
python -m codex_ml.telemetry.server
```

Use `track_time` to instrument functions and expose metrics on `/metrics`.

## Offline tracking workflow

- `codex_ml.tracking.mlflow_guard.bootstrap_offline_tracking()` (and the richer `bootstrap_offline_tracking_decision()`) force a `file:`-scoped MLflow tracking URI (`artifacts/mlruns` by default), normalise plain filesystem paths to canonical `file://` URIs, and create the directory if it is missing. Set `MLFLOW_ALLOW_REMOTE=1` to opt back into an explicitly configured remote backend. Every entry point—`MLflowWriter`, `mlflow_utils.bootstrap_offline_tracking()`, `codex_ml.utils.experiment_tracking_mlflow.ensure_local_tracking()`, the training CLI, and the offline smoke test—routes through the guard before touching MLflow so downgrade decisions are consistent.
- Tracking summaries now include guard telemetry with a canonical key order so audits can reconcile what was requested versus what was enforced:

  | Field | Description |
  | --- | --- |
  | `requested_uri` | The URI supplied via config/CLI/environment before guarding. |
  | `effective_uri` | The URI actually configured after the guard ran. |
  | `tracking_uri` | Alias of `effective_uri` for backwards compatibility. |
  | `fallback_reason` | Reason for downgrading to a local store (`non_local_uri`, `non_file_scheme`, …); empty when passthrough occurred. |
  | `allow_remote_flag` | Raw `MLFLOW_ALLOW_REMOTE` value sampled when the guard executed. |
  | `allow_remote` | Boolean view of `allow_remote_flag`. |
  | `system_metrics_enabled` | Final value of `MLFLOW_ENABLE_SYSTEM_METRICS` after bootstrapping (remains `false` when remote tracking is disallowed). |

  Example downgrade payload:

  ```json
  {
    "component": "mlflow",
    "status": "enabled",
    "extra": {
      "requested_uri": "https://example.com/mlflow",
      "effective_uri": "file:///home/user/project/artifacts/mlruns",
      "fallback_reason": "non_local_uri",
      "allow_remote_flag": "",
      "allow_remote": false,
      "system_metrics_enabled": false
    }
  }
  ```
- TensorBoard, MLflow, and Weights & Biases writers emit a deterministic `tracking_summary.ndjson` alongside the run directory summarising which backends were enabled, why others degraded, and which optional dependencies (psutil/NVML) were available so GPU sampling gaps are explicit.
- Metric rows always land in `metrics.ndjson` with a canonical key order; every record now carries `run_id`, `step`, `split`, and a UTC ISO `timestamp` (unless the legacy toggle is set). Structured payloads emit descriptors to `metrics_manifest.ndjson` (type/path/shape/version plus the full payload) and the originating scalar row references them via `tags.manifest_id`. Evaluation runs reuse the same writer with an explicit `tags.phase` so downstream tooling can distinguish training/eval emissions without ad hoc parsing.
- Rotation can be tuned via environment variables. Defaults are conservative (`64 MiB`, `24 h`, retain `5` shards) but can be disabled by exporting `None` or `0`. The same knobs now govern both `metrics.ndjson` and `tracking_summary.ndjson` so large sweeps rotate predictably:
  - `CODEX_TRACKING_NDJSON_MAX_BYTES` → rotate once the active shard exceeds this many bytes.
  - `CODEX_TRACKING_NDJSON_MAX_AGE_S` → rotate when the shard has not been touched for `N` seconds.
  - `CODEX_TRACKING_NDJSON_BACKUP_COUNT` → retain this many rotated files (`metrics.ndjson`, `metrics.ndjson.1`, …).
- Legacy consumers can opt out of the extended schema by exporting `CODEX_TRACKING_LEGACY_NDJSON=1` (alias: `LOGGING_NDJSON_LEGACY=1`).
- Summarise rotated metric shards with `codex-ndjson summarize --input <run-dir> --output csv` (CSV) or `--output parquet` (requires pandas). The CLI merges all `metrics.ndjson*` shards oldest→newest, computes per-metric aggregates (count/min/max/mean plus first/last timestamps/values/phases), tracks manifest IDs, and emits a tidy table ordered chronologically. Both `codex_ml` and utility CLIs route through the same summarizer implementation.
- Offline NDJSON summarisation is also available via the package CLI:

  ```bash
  python -m codex_ml.cli ndjson-summary --input artifacts/metrics.ndjson
  ```
- Offline MLflow bootstrap can be smoke-tested with `python examples/mlflow_offline.py --output /tmp/mlruns`. Pass `--tracking-uri https://…` to validate that a remote URI is rejected unless `MLFLOW_ALLOW_REMOTE=1` is set. The CLI asserts a local `file:` URI, logs params/metrics/artifacts, and ensures both `metrics.ndjson` and `tracking_summary.ndjson` are populated.

### Residual risks

- Guard telemetry makes it obvious when remote tracking was requested but downgraded; review `tracking_summary.ndjson` alongside `metrics.ndjson*` if a run appears to have missing artefacts.
- psutil/NVML availability is only sampled at writer initialisation. Long-lived training jobs should still watch the system metrics logs for runtime degradation events.

### Rollback

- Remove the tracking writers or delete `tracking_summary.ndjson` and unset `CODEX_MLFLOW_LOCAL_DIR` to return to the pre-hardened behaviour. Clearing `CODEX_TRACKING_LEGACY_NDJSON` restores the enriched NDJSON schema. Disable rotation by exporting `CODEX_TRACKING_NDJSON_MAX_BYTES=` and `CODEX_TRACKING_NDJSON_MAX_AGE_S=` (empty) if required during rollback.

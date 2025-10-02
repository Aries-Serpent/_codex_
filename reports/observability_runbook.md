# Observability Runbook — Run {{RUN_NUMBER}} ({{DATE}})

> Menu focus: Observability (5)

This runbook captures the monitoring baseline for the audit. Update sections with concrete details each run to keep responders aligned.

## Run Metadata
- Branch: {{BRANCH_NAME}}
- Snapshot commit: {{SHORT_SHA}}
- Incident commander: {{ONCALL}}

## Logging
| System | Location | Retention | Action Owner |
| --- | --- | --- | --- |
| {{SYSTEM}} | {{LOCATION}} | {{RETENTION}} | {{OWNER}} |

### Log Review Checklist
- [ ] Confirm log shipping is operational ({{LOG_SHIP_TOOL}})
- [ ] Review error rates for {{SERVICE}}
- Findings: {{LOG_FINDINGS}}

### Offline tracking workflow (updated)
- MLflow tracking URI enforced via `codex_ml.tracking.mlflow_guard.ensure_file_backend()` → defaults to `file:{{REPO}}/artifacts/mlruns`. `examples/mlflow_offline.py` exercises the guard end-to-end and `codex_ml.utils.experiment_tracking_mlflow.ensure_local_tracking()` reuses the guard for legacy call sites. `MLflowWriter` records both the requested URI and any fallback reason so responders can validate that a non-file URI was automatically downgraded.
- TensorBoard / W&B / MLflow writers append `tracking_summary.ndjson` in each run directory, capturing enablement status and psutil/NVML availability.
- `metrics.ndjson` now includes `run_id`, `step`, `split`, and UTC ISO `timestamp` fields in every row (legacy toggle still available). Structured payloads emit descriptors to `metrics_manifest.ndjson` and link back via `tags.manifest_id`.
- Rotation tuning: `CODEX_TRACKING_NDJSON_MAX_BYTES` (default `64 MiB`), `CODEX_TRACKING_NDJSON_MAX_AGE_S` (default `24 h`), `CODEX_TRACKING_NDJSON_BACKUP_COUNT` (default `5`). Export empty values to disable rotation during rollback.
- Legacy NDJSON schema toggle: `CODEX_TRACKING_LEGACY_NDJSON=1` (alias `LOGGING_NDJSON_LEGACY=1`).
- Summariser: `codex-ndjson summarize --input <run-dir> --output csv|parquet` → aggregates across rotated shards, computes min/max/mean, and surfaces the most recent `tags.manifest_id`.
- Smoke tests: `pytest tests/tracking/test_tracking_writers_offline.py::test_ndjson_writer_is_deterministic` and `pytest tests/tracking/test_mlflow_offline_cli.py::test_mlflow_offline_smoke_enforces_file_uri`.

## Metrics & Dashboards
| Metric | Source | Threshold | Current Value | Notes |
| --- | --- | --- | --- | --- |
| {{METRIC}} | {{SOURCE}} | {{THRESHOLD}} | {{VALUE}} | {{NOTES}} |

### Dashboard Links
- {{DASHBOARD_NAME}} — {{URL_OR_PATH}}

## Alerting
| Alert | Trigger | Channel | Runbook |
| --- | --- | --- | --- |
| {{ALERT}} | {{TRIGGER}} | {{CHANNEL}} | {{RUNBOOK_LINK}} |

## Incident Review
- Past incidents referenced: {{INCIDENTS}}
- Lessons applied this run: {{LESSONS}}

## Next Steps
- {{NEXT_STEP_ONE}}
- {{NEXT_STEP_TWO}}
- Residual risk: tracking summaries are not rotated automatically; prune large files post-sweep.
- Rollback: remove `tracking_summary.ndjson` entries and unset `CODEX_MLFLOW_LOCAL_DIR` / `CODEX_TRACKING_LEGACY_NDJSON`. Disable NDJSON rotation by clearing `CODEX_TRACKING_NDJSON_MAX_BYTES`/`CODEX_TRACKING_NDJSON_MAX_AGE_S` if reverting.

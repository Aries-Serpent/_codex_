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
- MLflow tracking URI enforced via `codex_ml.tracking.mlflow_guard.ensure_file_backend()` → defaults to `file:{{REPO}}/artifacts/mlruns`. `examples/mlflow_offline.py` exercises the guard end-to-end.
- TensorBoard / W&B / MLflow writers append `tracking_summary.ndjson` in each run directory, capturing enablement status and psutil/NVML availability.
- `metrics.ndjson` remains the source of truth for scalar metrics; structured payloads emit descriptors to `metrics_manifest.ndjson`.
- Rotation tuning: `CODEX_TRACKING_NDJSON_MAX_BYTES`, `CODEX_TRACKING_NDJSON_MAX_AGE_S`, `CODEX_TRACKING_NDJSON_BACKUP_COUNT`.
- Legacy NDJSON schema toggle: `CODEX_TRACKING_LEGACY_NDJSON=1` (alias `LOGGING_NDJSON_LEGACY=1`).
- Summariser: `codex-ndjson summarize --input <run-dir> --output csv`.
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
- Rollback: remove `tracking_summary.ndjson` entries and unset `CODEX_MLFLOW_LOCAL_DIR` / `CODEX_TRACKING_LEGACY_NDJSON` to revert to legacy behaviour.

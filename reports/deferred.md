# Deferred Items — Run 1 (2025-09-22)

| Item | Reason Deferred | Proposed Next Step |
| --- | --- | --- |
| Clean legacy `.codex/` markdown fences | Thousands of historical artefacts; outside scope of initial run. | Stage incremental cleanups once new workflow stabilises; consider scripted fixes. |
| Observability deep dive (Menu 5) | Need baseline reports/prompt first. | Schedule in a later run to align telemetry docs with new audit outputs. |
| Security markdown remediation | Existing docs violate new fence rule; heavy lift to refactor safely. | Address alongside security sweep (Menu 4) to avoid piecemeal edits. |
| Offline MLflow usage guide | Requires coordination with tracking maintainers. | Capture expectations in future documentation polish run (Menu 7). |

## Update 2025-09-26T18:57:07Z

| Module | Rationale |
| --- | --- |
| codex_update_runner.py::run_functional_training | Requires remote orchestration and registry access; kept as explicit deferred stub for offline runs. |
| src/codex_ml/monitoring/prometheus.py | Remote Prometheus exporters depend on external services; default to local NDJSON fallback only. |

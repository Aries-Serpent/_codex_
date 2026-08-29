# Repository Audit Scorecard (Regression Focus)

- **Regression coverage artifact**: See `artifacts/model_regression_coverage.md` for per-category pass/fail counts (R1–R5).
- **Execution posture**: Offline-first; invoke via `nox -s regression` or `python -m codex_regression.runner`.
- **Logging**: NDJSON history at `artifacts/model_regression_log.ndjson` with timestamps, markers, and durations.
- **Keep-it-honest gate**: R5 tests ensure honesty metadata and tool traces remain aligned with recorded RA outputs.
- **Empty categories**: Regression suites without collected tests are marked as **skipped** (pytest exit code 5) to avoid false
  failures while still signaling missing coverage.
- **RA policy signals**: Boolean or numeric RA gate payloads are normalized (true/1 vs false/0) and surfaced as green/red in
  Golden Harness status.

Update this scorecard alongside coverage updates to keep audit consumers informed.

# Repository Audit Scorecard (Regression Focus)

- **Regression coverage artifact**: See `artifacts/model_regression_coverage.md` for per-category pass/fail counts (R1–R5).
- **Execution posture**: Offline-first; invoke via `nox -s regression` or `python -m codex_regression.runner`.
- **Logging**: NDJSON history at `artifacts/model_regression_log.ndjson` with timestamps, markers, and durations.
- **Keep-it-honest gate**: R5 tests ensure honesty metadata and tool traces remain aligned with recorded RA outputs.

Update this scorecard alongside coverage updates to keep audit consumers informed.

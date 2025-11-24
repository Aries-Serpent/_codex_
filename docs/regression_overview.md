# Model Regression and Keep-It-Honest Suites

This repository now ships an offline-first regression harness covering data, modeling, infrastructure, performance, and safety/honesty surfaces.

## Regression categories (R1–R5)

- **R1 – Data integrity and determinism**: dataset loading, splits, caching, and hashing.
- **R2 – Model initialization and adapters**: model registry boot, LoRA/PEFT wiring, forward pass shims.
- **R3 – Infrastructure and training loops**: configuration loading, checkpointing, logging, and resumability.
- **R4 – Performance posture**: speed, memory budgets, and CPU-only enforcement.
- **R5 – Safety & honesty**: prompt redaction, denylist enforcement, honesty metadata, and tool-trace agreement.

## Running the regression harness (offline)

- Preferred: `nox -s regression` (sets `CODEX_NET_MODE=offline` and disables pytest plugin autoloading).
- Direct: `python -m codex_regression.runner` to execute all categories with NDJSON logging.
- Targeted: `pytest -m regression_R5` to run only the keep-it-honest safety checks.

Outputs are written to `artifacts/model_regression_log.ndjson` (per-run NDJSON) and summarized in `artifacts/model_regression_coverage.md`.

## Writing new regression tests

1. Pick the appropriate category marker: `regression_R1` … `regression_R5` (all also carry the `regression` marker).
2. Keep tests offline—no network calls, no remote fixtures. Use synthetic fixtures or existing artifacts under `artifacts/`.
3. Update documentation or inline comments to explain the regression intent and failure modes.
4. Re-run `nox -s regression` to refresh coverage artifacts.

## Keep-it-honest suites

Safety/honesty regressions live under `tests/keep_it_honest/` and validate:

- Honesty metadata consistency (`validate_honesty_metadata`).
- Tool trace alignment with RA-style results (`validate_tool_trace_against_ra`).
- Derivation of RA status from existing artifacts only (`derive_ra_status_from_artifacts`).

These tests are registered under **R5** and run as part of the regression harness.

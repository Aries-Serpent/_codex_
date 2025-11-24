# Track F: Model Regression & Keep-It-Honest Suites Plan

This document outlines the tasks required to implement model regression testing and keep‑it‑honest suites in the Codex environment. The goal is to add structured regression coverage across data, model, infrastructure, performance, and safety, and to ensure honesty and policy compliance remain intact during evolution.

## Tasks

- **Regression Taxonomy**: Define regression categories (e.g. R1–R5) to classify tests:
  - R1 – Data regression tests (data loading, splits, caching determinism).
  - R2 – Model regression tests (model initialization, forward passes, LoRA/PEFT integration).
  - R3 – Infrastructure regression tests (training loops, config loading, checkpointing, logging).
  - R4 – Performance regression tests (training speed, memory footprint).
  - R5 – Safety & honesty regression tests (prompt redaction, denylist enforcement, honesty metadata / tool trace consistency).
- **Regression Logging**: Add `codex_regression/log.py` defining a `RegressionRun` dataclass and functions to record regressions. Store results in `artifacts/model_regression_log.ndjson` and track per‑category counts and statuses.
- **Runner & Integration**: Implement `codex_regression/runner.py` with a `run_regression()` function that discovers and runs tests per category. Integrate a new `phase_regression()` into the main workflow (`codex_workflow.py`) after evaluation/monitoring phases.
- **Coverage Reporting**: Generate a coverage report (`artifacts/model_regression_coverage.md`) summarizing which regression categories are covered, passed/failed tests, and recommendations for missing tests. Update `repo_audit_scorecard.md` and `golden_harness_status.json` to include regression coverage.
- **Keep‑It‑Honest Suites**: Create a `tests/keep_it_honest/` package with tests that verify:
  - Honesty metadata consistency across runs (statements recorded and flushed correctly).
  - Tool trace completeness and correlation with RA gate results.
  - Derivation of RA policy status from existing artifacts without fabrication.
  Register these tests under R5 in the regression catalog.
- **Offline Integration & Gates**: Ensure that regression tests run via local nox/pytest sessions (`nox -s audit`), with no external CI or GitHub Actions involvement. Update gate definitions to fail when new regressions appear.
- **Documentation & Examples**: Add documentation explaining regression categories, how to run the regression runner, interpret logs and coverage reports, and how to write new regression tests. Provide examples of a simple regression test and keep‑it‑honest suite.

## Commit & PR Strategy

This plan should be committed to a new branch `codex-track-F-plan` and opened as a pull request targeting `0D_base_`. A comment beginning with `@codex implement plan` should summarise these tasks for Codex to execute.

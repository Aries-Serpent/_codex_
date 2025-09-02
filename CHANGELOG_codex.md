## 2025-08-28 – Codex offline runner

- Added tools/codex_run.py orchestrator with audit fallback and local gates.
- Added tools/codex_run.sh wrapper.

## 2025-08-31 – CLI testing improvements

- Restricted Nox test session to Python 3.12 and installed missing CLI/API dependencies.
- Enabled `importlib` import mode via `pytest.ini` to prevent module name collisions during collection.

## 2025-11-25 – Static code analysis step

- Added `static_code_analysis` stage to `analysis/audit_pipeline.py` and integrated it with `ci_local.sh`.
- Logs syntax-check metrics for Python sources.
- Introduced a unit test verifying metric emission.

## 2025-11-24 – Offline upgrade script

- Added `codex_ast_upgrade.py` to automate tiered parsing setup and offline auditing.

## 2025-11-23 – Tiered parsing and offline audit pipeline

- Added analysis modules with tiered parsing fallbacks and search providers.
- Added CLI `codex_ml.cli.audit_pipeline` and tests for AST extraction.
- Documented "Fallback Modes & Feature Flags" in README.
- Deferred advanced codemods and online external search; kept AST-only analyzers as fallback.

## 2025-05-19 – Validation metrics & splits

- Added: `--val-split`/`--test-split` flags and per-epoch validation logging to `metrics.json`.
- Deferred: stratified splits, GPU-heavy metrics, and online trackers.
- Risks: small datasets may skip evaluation when insufficient tokens.

## 2025-11-09 – Offline experiment tracking

- Added unified `codex_ml.monitoring.codex_logging` with optional TensorBoard, W&B, and MLflow sinks.
- Patched `engine_hf_trainer.py` and `functional_training.py` to sample CPU/GPU metrics and log per-step scalars.
- Added offline test coverage for logging bootstrap and docs for monitoring and experiment tracking.
- Deferred: online W&B/remote MLflow servers, full Trainer callbacks, and extended NVML telemetry.

## 2025-08-26 – LoRA and deterministic splits

- Implemented optional LoRA adapter with graceful fallback when `peft` is missing.
- Added grad accumulation and mixed precision helpers to `functional_training.py`.
- Introduced deterministic data splitting utility.
- Generated `requirements.lock` and local test gate script.
- Sanitized external links in README for offline use.

## CI policy docs — 2025-08-26T20:17:49Z

- Created /workspace/_codex_/docs/ci.md (web search allowed; remote CI disallowed)

## Disable remote CI — 2025-08-26T20:17:49Z

- Patched 5 workflow file(s) to `workflow_dispatch` and guarded jobs.
- Total jobs guarded: 7

## 2025-08-26 – Δ PR Checklist Applied

### New

- standalone `analysis` package with audit pipeline for offline checks.

### Modified

- README includes "Offline CI & Local Parity" policy block.
- `ci_local.sh` enforces coverage during local tests.
- Workflows guarded with `_codex_guard` job and manual triggers.

### Removed

- none

### Deferred / Pruned

- existing analysis utilities under `src/codex_ml/analysis` retained without duplication.

## 2025-08-28 – Portable workflow tooling

### New
- `tools/audit_runner.py` provides dual-path audit execution with optional external CLI.
- `tools/run_precommit.py` adds verbose pre-commit runner with timeout and cache cleanup.
- `tools/run_tests.py` wraps pytest with optional coverage fallback.
- `tools/codex_workflow.py` and `tools/codex_workflow.sh` orchestrate audit, hooks, and tests locally.


## 2025-08-29 – Misc bug fixes and utilities
- Added shebang and docs to `tools/label_policy_lint.py`.
- Ensured `git_tag.current_commit` decodes byte output.
- Added setter for SentencePieceAdapter `model_prefix`.
- Guarded MLflow run initialization by checking `MLFLOW_TRACKING_URI`.
- Corrected EarlyStopping patience comparison.
- Introduced importlib-based CLI viewer module.
- Exposed RNG state helpers and best-k retention tests.
- Implemented placeholder keyword risk scoring.
- Added seed-controlled shuffling to data loaders.
- Warned on duplicate registry registrations.

## 2025-08-29 – Utilities and test cleanup

- Added standalone `utils.training_callbacks` with EarlyStopping.
  - WHY: share training callback outside `codex_ml` package.
  - RISK: low; new module.
  - ROLLBACK: revert `src/utils/training_callbacks.py`.
- Improved git tag decoding to try locale and latin-1 fallbacks.
  - WHY: handle non-UTF-8 git outputs gracefully.
  - RISK: minimal; affects only metadata helpers.
  - ROLLBACK: revert changes in `src/codex_ml/tracking/git_tag.py`.
- Fixed missing imports in `label_policy_lint` tests.
  - WHY: ensure lint helper tests run.
  - RISK: none; tests only.
  - ROLLBACK: revert `tests/test_label_policy_lint.py`.

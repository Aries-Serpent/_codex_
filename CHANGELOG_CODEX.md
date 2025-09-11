# Codex Changelog

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
# Codex Changelog

## 2025-08-30 – Tokenizer, MLflow, and ingestion utilities

### WHY
- Introduce a canonical `HFTokenizer` adapter with batching and decode/pad APIs to unify tokenization usage across the codebase.
- Add/standardize ingestion helpers including encoding detection (`read_text(..., encoding="auto")`) and deterministic shuffling for reproducible data splits.
- Provide MLflow tracking utilities with configurable system-metrics toggle and safe no-op behavior when tracking is disabled or the dependency is missing.
- Consolidate ingestion utilities and tooling fixes for consistent execution and packaging.

### RISK
- Low: modules are thin wrappers with safe fallbacks and preserve prior interfaces where practical. Optional dependencies (transformers, peft, mlflow, charset-normalizer, pytest-cov, etc.) degrade gracefully.

### ROLLBACK
- Remove newly added modules (tokenizer adapter, ingestion helpers, tracking helpers) and revert any changed imports to restore previous behavior.

### TEST
- Recommended checks:
  - `pre-commit run --files src/codex_ml/interfaces/tokenizer.py src/codex_ml/tracking/mlflow_utils.py src/ingestion/encoding_detect.py src/ingestion/io_text.py src/ingestion/utils.py tests/interfaces/test_tokenizer_hf.py tests/tracking/test_mlflow_utils.py tests/ingestion/test_io_text.py`
  - `pytest` (note: during initial integration this run reported a number of collection/compatibility issues — expect follow-up fixes; historically some branches reported ~13 collection errors).

---

## 2025-08-30 – Tokenizer unification and ingestion consolidation (alternate notes)

### WHY
- Consolidate tokenization into a single HFTokenizer adapter with batch helpers.
- Merge ingestion utilities with encoding detection and deterministic shuffling.
- Restore MLflow helpers with safe no-op fallbacks and environment-variable-aware handling.
- Add package markers and tooling fixes to improve consistent execution across environments.

### RISK
- Low: changes preserve existing interfaces and degrade gracefully when optional dependencies are missing.

### ROLLBACK
- Revert this commit to restore the previous module layout.

---

## 2025-08-29 – Restore no-op MLflow context manager

### WHY
- Maintain previous behaviour where disabled MLflow tracking yields a no-op context manager so `with start_run(cfg)` remains safe when tracking is off or mlflow is unavailable.

### RISK
- Low: ensures backward compatibility for callers that expect a falsy/no-op context manager rather than an exception.

### ROLLBACK
- Revert this commit to return `None` instead (if required by alternate compatibility concerns).

---

## 2025-08-29 – Local orchestration scripts

### WHY
- Add local tooling to run the sequential Codex workflow:
  - `tools/codex_exec.py` and `tools/codex_exec.sh` to run the end-to-end local workflow (preparation, scan, suggest patches, capture errors, finalize).
  - Local task runner utilities for running pytest-selected tasks and capturing failure outputs for later inspection.

### RISK
- Low: scripts are optional and operate only on the local repository.

### ROLLBACK
- Remove the newly added scripts.

### REPRO
- `bash tools/codex_exec.sh` to generate local artifacts and reports.

---

## 2025-08-29 – Tokenizer & training wiring

### WHY
- Thread gradient-accumulation and bf16/fp16 flags into the HF Trainer wrapper.
- Provide optional LoRA integration points and deterministic ingestion helpers for training reproducibility.
- Add utilities to capture failing task output into commit-comment artifacts to help maintainers triage issues.

### RISK
- Low: trainer wiring is additive and optional; defaults preserve prior behaviour if optional dependencies are absent.

### ROLLBACK
- Revert this commit to remove tokenizer, training, and tracking utilities.

---

## 2025-08-29 – Tokenizer and tracking utilities (detailed)

### WHY
- Introduce `HFTokenizer` interface with padding/truncation controls and batch encode/decode helpers.
- Add deterministic ingestion helpers (`seeded_shuffle` / `deterministic_shuffle`), and robust `read_text` with optional automatic encoding detection.
- Simplify MLflow tracking via optional `start_run` helper with safe no-op behavior and configurable environment flags.
- Expose Trainer precision and LoRA-related options in the HF trainer wrapper.

### RISK
- Low: new utilities are optional and default to existing behaviour when optional dependencies are missing.

### ROLLBACK
- Revert this commit to restore previous behaviour.

### REPRO CHECKLIST
- Set `PYTHONHASHSEED=0` for deterministic ordering where needed.
- Use `seeded_shuffle` (or `deterministic_shuffle`) for reproducible splits.
- Use `read_text(..., encoding="auto")` where encoding may vary.
- `pre-commit run --all-files --verbose`.
- `pytest --cov=src --cov-report=term`.

---

## 2025-08-29 – Phase 3 integrations

### WHY
- Guard MLflow run initialization behind `CODEX_ENABLE_MLFLOW` and related flags to avoid accidental tracking.
- Resolve CLI viewer resources using `importlib.resources` for packaging safety.
- Provide a lightweight checkpoint manager with RNG persistence and best-K pruning when available.
- Add local task runner utilities (`tools/codex_run_tasks.py`) and optional venv bootstrap helpers.

### RISK
- Low: features are optional and protected by environment flags.

### ROLLBACK
- Revert this commit to restore previous behavior.

---

## Notes and Next Steps
- Multiple entries on 2025-08-29/30 reflect iterative integration steps across tokenizer, ingestion, tracking, and trainer wiring. The changes are intentionally additive and guarded; follow-up PRs should address the remaining test collection errors and tighten compatibility layers (e.g., signature normalization for legacy `read_text` implementations, optional dependency detection, and test environment setup).
- When backporting or cherry-picking these changes to other branches, ensure environment flags (e.g., `CODEX_ENABLE_MLFLOW`, `CODEX_POST_COMMIT_COMMENT`) and optional-dependency handling remain consistent to avoid surprising behavior in CI.
## 2025-08-28 — Codex Run
- Enforced self-hosted-only gates via make codex-gates and ci_local.sh
- Added doctor script and workflow executor
- Updated README and docs to recommend self-hosted runners and MLflow tracking

## $(date -u +%Y-%m-%d) — Codex Run
- Added pad_id and eos_id accessors to HFTokenizerAdapter.
- Surfaced monitoring exceptions in functional_training via stderr logging.
- Introduced --grad-accum support and metric logging in train_loop.
- CheckpointManager now writes system.json for hardware metadata.
- Registered codex-ml-cli entry point in pyproject.
- Updated README with offline CI instructions and codex-ml-cli usage.
- Added tests for tokenizer IDs, grad accumulation, and checkpoint system metadata.
- Added codex_seq_runner and run_codex_sequence utilities.

## 2025-09-02 — Codex Run
- Enabled optional padding/truncation in `HFTokenizerAdapter.encode`.
- Wired `apply_lora` into `run_hf_trainer` with dtype/device placement.
- Added checkpoint resume support via `resume_from` parameter.
## [Unreleased] - 2025-09-02
- Format `src/codex_ml/safety/risk_score.py` with Black.
- Correct README typos and complete environment description.
- Pin `peft` dependency to ensure `nox -s tests` passes.
- Applied fallback_patch_4.1-4.8 with safe sanitize→apply fallbacks; preserved intended functionality.
- Normalized line endings/BOM; stripped markdown/email artifacts from patch.
- Conformed to local gates (pre-commit/Black/isort/tests), Codex-only (no GitHub Actions). - Ensure test dependencies (including `langchain`) are installed so `nox -s tests` passes.
- Add runbook for offline wheelhouse usage at `docs/runbooks/offline_wheelhouse.md`.
- Add smoke test proving `nox -s tests` delegates to `coverage`.
- Add `wheelhouse` alias in `Makefile` for bootstrap script.
- Expand `noxfile.py` with `tests_sys` and `tests_ssp` sessions, optional `uv|virtualenv` backend, `PIP_CACHE_DIR` default.
- **feat(gates):** Add black/isort/bandit/detect-secrets/safety hooks; nox `sec_scan`; Make `sys-tests`/`ssp-tests`.
- **feat(deps):** Introduce `tools/uv_lock_refresh.sh` to generate `uv.lock` and compiled requirements.
- **feat(trainer):** Early stopping + scheduler selection wired into `Trainer`.
- **feat(logging):** Rotating file handler with sane defaults.
- **feat(tokenization):** SentencePiece adapter padding/truncation shims + `__all__`.
- **tests(tokenization):** Edge-case test gated by `SPM_TINY_MODEL`.

- Introduced general `TokenizerAdapter` with HuggingFace and whitespace implementations; added basic round-trip tests.
- Added simple dataset loader supporting text/NDJSON/CSV with caching and safety hooks, plus deterministic split utilities.

### Unreleased - 2025-09-07
- Updated README references to current configuration structure.
- Integrate safety filter with data loader and add license checker script.
- Generated gaps report for TODOs and stubs.
- Executed pre-commit and nox quality gate sessions.
- Add dataset loader supporting TXT/NDJSON/CSV with caching and safety filtering.
- feat(model): introduce model registry with optional LoRA configuration and tests.
- docs: document tokenizer adapter, Hydra configuration groups, and data loading utilities.
## [Unreleased] - 2025-09-02
- Format `src/codex_ml/safety/risk_score.py` with Black.
- Correct README typos and complete environment description.
- Pin `peft` dependency to ensure `nox -s tests` passes.
- Applied fallback_patch_4.1-4.8 with safe sanitize→apply fallbacks; preserved intended functionality.
- Normalized line endings/BOM; stripped markdown/email artifacts from patch.
- Conformed to local gates (pre-commit/Black/isort/tests), Codex-only (no GitHub Actions). - Ensure test dependencies (including `langchain`) are installed so `nox -s tests` passes.
- Add runbook for offline wheelhouse usage at `docs/runbooks/offline_wheelhouse.md`.
- Add smoke test proving `nox -s tests` delegates to `coverage`.
- Add `wheelhouse` alias in `Makefile` for bootstrap script.
- Expand `noxfile.py` with `tests_sys` and `tests_ssp` sessions, optional `uv|virtualenv` backend, `PIP_CACHE_DIR` default.
- **feat(gates):** Add black/isort/bandit/detect-secrets/safety hooks; nox `sec_scan`; Make `sys-tests`/`ssp-tests`.
- **feat(deps):** Introduce `tools/uv_lock_refresh.sh` to generate `uv.lock` and compiled requirements.
- **feat(trainer):** Early stopping + scheduler selection wired into `Trainer`.
- **feat(logging):** Rotating file handler with sane defaults.
- **feat(tokenization):** SentencePiece adapter padding/truncation shims + `__all__`.
- **tests(tokenization):** Edge-case test gated by `SPM_TINY_MODEL`.

- Introduced general `TokenizerAdapter` with HuggingFace and whitespace implementations; added basic round-trip tests.
- Added simple dataset loader supporting text/NDJSON/CSV with caching and safety hooks, plus deterministic split utilities.

### Unreleased - 2025-09-07
- Updated README references to current configuration structure.
- Integrate safety filter with data loader and add license checker script.
- Generated gaps report for TODOs and stubs.
- Executed pre-commit and nox quality gate sessions.
- Add dataset loader supporting TXT/NDJSON/CSV with caching and safety filtering.
- feat(model): introduce model registry with optional LoRA configuration and tests.
- docs: document tokenizer adapter, Hydra configuration groups, and data loading utilities.

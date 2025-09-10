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

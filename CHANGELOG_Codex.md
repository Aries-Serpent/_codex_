# Codex Changelog

## 2025-08-30 – Tokenizer unification and ingestion consolidation

### WHY
- Consolidate tokenization into a single HFTokenizer adapter with batch helpers.
- Merge ingestion utilities with encoding detection and deterministic shuffling.
- Restore MLflow helpers with safe no-op fallbacks and env var handling.
- Add package markers and tooling fixes for consistent execution.

### RISK
- Low: changes preserve existing interfaces and degrade gracefully.

### ROLLBACK
- Revert this commit to restore previous module layout.


## 2025-08-29 – Restore no-op MLflow context manager

### WHY
- Maintain previous behaviour where disabled MLflow tracking yields a no-op context manager.

### RISK
- Low: ensures `with start_run(cfg)` continues to work when tracking is off or unavailable.

### ROLLBACK
- Revert this commit to return `None` instead.

## 2025-08-29 – Local orchestration scripts

### WHY
- Add `tools/codex_exec.py` and `tools/codex_exec.sh` to run the sequential Codex workflow locally.

### RISK
- Low: scripts are optional and operate only on the local repository.

### ROLLBACK
- Remove the newly added scripts.

### REPRO
- `bash tools/codex_exec.sh` to generate local artifacts and reports.

## 2025-08-29 – Tokenizer & training wiring

### WHY
- Added Hugging Face tokenizer wrapper with decode/pad APIs.
- Threaded gradient accumulation and bf16/fp16 flags into Trainer.
- Provided deterministic ingestion helpers and optional offline MLflow.
- Captured failing task output for commit comments.

### RISK
- Low: features are optional and fallback to previous behaviour when deps are missing.

### ROLLBACK
- Revert this commit to remove tokenizer, training, and tracking utilities.

## 2025-08-29 – Tokenizer and tracking utilities

### WHY
- Introduce `HFTokenizer` interface with padding and truncation controls.
- Add deterministic ingestion helpers (`seeded_shuffle`, `read_text` with optional auto encoding).
- Simplify MLflow tracking via optional `start_run` and update training flags.
- Expose gradient accumulation and LoRA dropout options in HF trainer.

### RISK
- Low: new utilities are optional and default to existing behaviour.

### ROLLBACK
- Revert this commit to restore previous behaviour.

### Repro checklist
- Set `PYTHONHASHSEED=0`.
- Use `seeded_shuffle` for deterministic splits.
- `read_text(..., encoding="auto")` for encoding detection.
- `pre-commit run --all-files --verbose`.
- `pytest --cov=src --cov-report=term`.

## 2025-08-29 – Phase 3 integrations

### WHY
- Guard MLflow run initialization behind `CODEX_ENABLE_MLFLOW`.
- Resolve CLI viewer resources via `importlib.resources` for packaging safety.
- Provide lightweight checkpoint manager with RNG persistence and best-K pruning.
- Add local task runner (`tools/codex_run_tasks.py`) and optional venv bootstrapper.

### RISK
- Low: features are optional and protected by environment flags.

### ROLLBACK
- Revert this commit to restore previous behavior.

# Codex Changelog

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

## 2025-08-29 – Restore no-op MLflow context manager

### WHY
- Maintain previous behaviour where disabled MLflow tracking yields a no-op context manager.

### RISK
- Low: ensures `with start_run(cfg)` continues to work when tracking is off or unavailable.

### ROLLBACK
- Revert this commit to return ``None`` instead.

## 2025-08-29 – Local orchestration scripts

### WHY
- Add `tools/codex_exec.py` and `tools/codex_exec.sh` to run the sequential Codex workflow locally.

### RISK
- Low: scripts are optional and operate only on the local repository.

### ROLLBACK
- Remove the newly added scripts.

### REPRO
- `bash tools/codex_exec.sh` to generate local artifacts and reports.

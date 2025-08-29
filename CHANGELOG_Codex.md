# Codex Changelog

## 2025-08-29 – Local orchestration scripts

### WHY
- Add `tools/codex_exec.py` and `tools/codex_exec.sh` to run the sequential Codex workflow locally.

### RISK
- Low: scripts are optional and operate only on the local repository.

### ROLLBACK
- Remove the newly added scripts.

### REPRO
- `bash tools/codex_exec.sh` to generate local artifacts and reports.

## 2025-08-29 – Local orchestrator scripts

### WHY
- Add `tools/codex_exec.py` and `tools/codex_exec.sh` for end-to-end local workflow, including scanning, README normalization, and commit-comment aggregation.

### RISK
- Low: scripts run locally and skip network posting unless tokens are supplied.

### ROLLBACK
- Revert this commit to remove the orchestrator utilities.

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

### REPRO
- Set `PYTHONHASHSEED=0`.
- Use `seeded_shuffle()` for deterministic dataset splits.
- Pin configs and seeds before training.

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

## 2025-08-29 – Phase 2 implementations

### WHY
- Add label policy lint helper and tests for self-hosted runner labels.
- Harden git tag decoding and expose SentencePiece model_prefix setter.
- Correct EarlyStopping patience, deterministic data streaming, and minimal risk scoring.
- Provide registry coverage tests.

### RISK
- Low: changes are small utilities with minimal external dependencies.

### ROLLBACK
- Revert this commit to restore previous behavior.

# CHANGELOG_Codex

## [2025-08-29] Phase 1 preparation
- Established Python virtual environment (.venv) with pytest, coverage, numpy, importlib_resources.
- Set PRE_COMMIT_COLOR=never.
- Ensured baseline directories (tools/, tests/tools/, src/codex_ml/tracking/, src/tokenization/, monitoring/, tests/monitoring/, src/utils/, tests/utils/, scripts/cli/, tests/cli/, src/safety/, tests/safety/, src/data/, tests/data/, analysis/, interfaces/) exist; added placeholders as needed.
- Inventoried module locations:
  - git_tag.py \u2192 src/codex_ml/tracking/git_tag.py
  - sentencepiece_adapter.py \u2192 src/codex_ml/tokenization/sentencepiece_adapter.py
  - mlflow_utils.py \u2192 src/codex_ml/tracking/mlflow_utils.py; duplicates at codex_ml/tracking/mlflow_utils.py and src/codex_ml/monitoring/mlflow_utils.py
  - training_callbacks.py \u2192 not found
  - checkpointing.py \u2192 src/codex_ml/utils/checkpointing.py; duplicate at codex_ml/utils/checkpointing.py
  - loaders.py \u2192 src/codex_ml/data/loaders.py
  - registry.py \u2192 analysis/registry.py; src/codex_ml/interfaces/registry.py; src/codex_ml/analysis/registry.py; src/codex_ml/registry.py
- Pending: clarify location or existence of training_callbacks.py.

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

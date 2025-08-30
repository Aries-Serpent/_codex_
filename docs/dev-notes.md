# Dev Notes

## Mapping of tokenization, MLflow, and ingestion utilities

| Area | Existing Files | Canonical Target | Notes |
|------|----------------|------------------|-------|
| Tokenizer interface | `src/codex_ml/interfaces/tokenizer.py0`, `tokenizer.py00`, `tokenizer.py1` | `src/codex_ml/interfaces/tokenizer.py` | Implement `TokenizerAdapter` with HF wrapper |
| MLflow utilities | `src/codex_ml/tracking/mlflow_utils.py001`, `mlflow_utils.py0`, `mlflow_utils.py1` | `src/codex_ml/tracking/mlflow_utils.py` | Dataclass config + no-op fallbacks |
| Ingestion helpers | `src/ingestion/__init__.py0`, `__init__.py1`, `encoding_detect.py1`, `io_text.py0`, `utils.py00`, `utils.py0`, `utils.py1` | `src/ingestion/__init__.py`, `encoding_detect.py`, `io_text.py`, `utils.py` | Consolidate reading, encoding detection, and deterministic shuffle |
| Tests | `tests/interfaces/test_tokenizer_hf.py0`, `tests/tracking/test_mlflow_utils.py00`, `tests/tracking/test_mlflow_utils.py0`, `tests/ingestion/test_io_text.py0`, etc. | Unsuffixed equivalents | Update to exercise canonical modules |
| Tools | `tools/codex_run_tasks.py00`, `codex_run_tasks.py0`, `codex_run_tasks.py1`, `tools/codex_exec.py.bkup`, `codex_exec.py0`, `codex_exec.py1`, `tools/install_codex_hooks.py0` | Unsuffixed scripts | Remove legacy variants |
| Training | `training/engine_hf_trainer.py00`, `engine_hf_trainer.py0`, `engine_hf_trainer.py1` | `training/engine_hf_trainer.py` | Merge features and drop suffixes |

## Plan

1. Create canonical tokenizer adapter and refactor consumers.
2. Provide MLflow utility layer with safe no-op fallbacks.
3. Consolidate ingestion utilities with encoding detection and deterministic shuffling.
4. Remove suffixed legacy modules once new code is in place.

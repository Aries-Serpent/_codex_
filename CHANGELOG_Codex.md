# Codex Changelog

## 2025-08-30 – Tokenizer, MLflow, and ingestion utilities

### WHY
- Introduce canonical `HFTokenizer` adapter and unified ingestion helpers.
- Add MLflow tracking layer with configurable system-metrics toggle.

### RISK
- Low: modules are thin wrappers with safe fallbacks.

### ROLLBACK
- Remove new modules and revert imports.

### TEST
- `pre-commit run --files src/codex_ml/interfaces/tokenizer.py src/codex_ml/tracking/mlflow_utils.py src/ingestion/encoding_detect.py src/ingestion/io_text.py src/ingestion/utils.py tests/interfaces/test_tokenizer_hf.py tests/tracking/test_mlflow_utils.py tests/ingestion/test_io_text.py`
- `pytest` (fails: 13 errors during collection)

# Gap 21 — Comprehensive Regression Test Suite

**Status:** ✅ Implemented  
**Implemented:** 2026-06-06  
**Branch:** `copilot/explore-codebase-and-create-plan`

---

## Summary

Implemented a comprehensive regression test suite under `tests/regression/`
covering five capability domains:

| Domain | File | Test functions |
|--------|------|---------------|
| Model output stability | `test_model_output_stability.py` | 13 |
| API contract tests | `test_api_contracts.py` | 17 |
| Data pipeline integrity | `test_data_pipeline_integrity.py` | 10 |
| Configuration schema regression | `test_config_schema_regression.py` | 18 |
| Checkpoint round-trip consistency | `test_checkpoint_roundtrip.py` | 9 |
| **TOTAL** | **5 test files + conftest.py** | **67** |

---

## Test Run Results

```
pytest tests/regression/ -v --tb=short
```

```
================================================= test session info ===================================================
platform linux -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0
rootdir: /tmp/workspace/Aries-Serpent/_codex_
configfile: pytest.ini
plugins: asyncio-1.4.0, anyio-4.9.0

collected 67 items

tests/regression/test_api_contracts.py .................              [ 25%]
tests/regression/test_checkpoint_roundtrip.py .........               [ 38%]
tests/regression/test_config_schema_regression.py ..................  [ 65%]
tests/regression/test_data_pipeline_integrity.py ..........           [ 80%]
tests/regression/test_model_output_stability.py .............         [100%]

======================== 67 passed, 2 warnings in 2.01s ========================
```

**Result: 67/67 PASSED ✅ (0 failed, 0 errors)**

---

## Done Criteria Verification

| Criterion | Status |
|-----------|--------|
| `tests/regression/` directory exists | ✅ |
| ≥ 20 regression test functions | ✅ 67 functions |
| ≥ 3 test files | ✅ 5 test files |
| `tests/regression/conftest.py` with shared fixtures | ✅ |
| All regression tests pass | ✅ 67/67 |
| Runnable with `pytest tests/regression/ -v` | ✅ |
| Evidence file at `workbench/evidence/gap21_regression_suite.md` | ✅ (this file) |
| `gap_backlog_prioritized.md` gap 21 status → `✅ Implemented` | ✅ |

---

## Coverage Breakdown

### 1. Model Output Stability (`test_model_output_stability.py` — 13 tests)

| Test | What it guards |
|------|---------------|
| `test_model_has_required_fields` | ModelHandle API surface (name, stage, meta) |
| `test_model_stage_is_pretrained` | Stage string format regression |
| `test_model_meta_contains_vocab` | vocab present and non-empty after training |
| `test_token_probabilities_sum_to_one` | Probability distribution normalisation |
| `test_token_probabilities_in_valid_range` | Each probability ∈ [0, 1] |
| `test_model_seed_stored_in_meta` | Reproducibility metadata |
| `test_pipeline_result_has_required_keys` | Pipeline output schema |
| `test_pipeline_losses_are_finite_numerics` | Loss numeric validity (incl. negative RLHF reward) |
| `test_pipeline_objective_u_is_float` | Objective U is finite float |
| `test_pipeline_handles_contain_m0_m1_m2` | All training stages produced |
| `test_pipeline_weights_schema` | Weights dict schema (alpha, beta, gamma) |
| `test_pretrain_deterministic` | Determinism regression |
| `test_pipeline_result_deterministic` | Full-pipeline determinism |

### 2. API Contract Tests (`test_api_contracts.py` — 17 tests)

| Test | What it guards |
|------|---------------|
| `test_root_returns_200` | Root endpoint status code |
| `test_root_schema_contains_name_and_version` | Root response schema |
| `test_root_endpoints_map_present` | Service discovery map |
| `test_health_returns_200` | Health probe status code |
| `test_health_schema_status_field` | Health status field |
| `test_health_schema_timestamp_field` | Health timestamp field |
| `test_liveness_returns_200` | Liveness probe status code |
| `test_liveness_schema` | Liveness response schema (3 fields) |
| `test_liveness_uptime_non_negative` | Uptime value range |
| `test_liveness_status_value` | Exact status string "alive" |
| `test_readiness_returns_2xx` | Readiness 200/503 contract |
| `test_readiness_schema_status_field` | Readiness status field |
| `test_readiness_schema_checks_field` | Sub-checks structure |
| `test_readiness_schema_timestamp_field` | Readiness timestamp field |
| `test_health_content_type_json` | JSON content-type header |
| `test_liveness_content_type_json` | JSON content-type header |
| `test_readiness_content_type_json` | JSON content-type header |

### 3. Data Pipeline Integrity (`test_data_pipeline_integrity.py` — 10 tests)

| Test | What it guards |
|------|---------------|
| `test_split_same_seed_produces_same_train` | Train split reproducibility |
| `test_split_same_seed_produces_same_val` | Val split reproducibility |
| `test_different_seeds_produce_different_splits` | Seed entropy |
| `test_split_sizes_sum_to_total` | No items lost in splitting |
| `test_split_train_ratio_approximately_correct` | Ratio contract ±5% |
| `test_split_no_overlap_between_train_and_val` | Partition disjointness |
| `test_repeated_split_is_idempotent` | Transformation idempotency |
| `test_checksum_stable_for_identical_content` | Hash determinism |
| `test_checksum_changes_on_content_mutation` | Hash sensitivity |
| `test_checksum_order_sensitive` | Hash order dependency |

### 4. Configuration Schema Regression (`test_config_schema_regression.py` — 18 tests)

| Test | What it guards |
|------|---------------|
| `test_default_model_name` | model_name default = "tiny" |
| `test_default_learning_rate` | learning_rate default = 1e-3 |
| `test_default_batch_size` | batch_size default = 8 |
| `test_default_epochs` | epochs default = 1 |
| `test_default_seed` | seed default = 42 |
| `test_default_device` | device default = "cpu" |
| `test_default_dtype` | dtype default = "float32" |
| `test_default_config_version` | config_version default = 1 |
| `test_required_fields_present` | 12 required fields all present |
| `test_negative_learning_rate_rejected` | lr > 0 constraint |
| `test_zero_learning_rate_rejected` | lr > 0 (strict) |
| `test_zero_batch_size_rejected` | batch_size > 0 |
| `test_eval_split_above_one_rejected` | eval_split ≤ 1.0 |
| `test_eval_split_negative_rejected` | eval_split ≥ 0.0 |
| `test_extra_fields_rejected` | extra="forbid" schema strictness |
| `test_model_dump_and_reload` | JSON round-trip identity |
| `test_validate_config_dict_helper` | Helper function contract |
| `test_lora_config_round_trip` | LoraConfig round-trip identity |

### 5. Checkpoint Round-Trip (`test_checkpoint_roundtrip.py` — 9 tests)

| Test | What it guards |
|------|---------------|
| `test_meta_roundtrip_preserves_all_keys` | No keys lost in JSON serialisation |
| `test_meta_roundtrip_preserves_values` | Values unchanged after JSON round-trip |
| `test_meta_checksum_stable` | Deterministic JSON serialisation |
| `test_model_handle_pickle_roundtrip` | Pickle round-trip fidelity |
| `test_model_handle_pickle_checksum_stable` | Pickle byte determinism |
| `test_multiple_checkpoints_all_readable` | Multi-epoch write/read cycle |
| `test_checkpoint_dirs_are_sorted_by_epoch` | Epoch directory naming convention |
| `test_missing_checkpoint_file_raises` | FileNotFoundError on missing ckpt |
| `test_corrupted_checkpoint_raises_json_error` | JSONDecodeError on bad ckpt |

---

## Shared Fixtures (`conftest.py`)

| Fixture | Scope | Description |
|---------|-------|-------------|
| `corpus` | session | Fixed 5-sentence training corpus |
| `demos` | session | Fixed 3-item SFT demonstration set |
| `prefs` | session | Fixed 3-item RLHF preference pairs |
| `pretrained_model` | session | ModelHandle from `pretrain(corpus, seed=42)` |
| `pipeline_result` | session | Full `run_codex_symbolic_pipeline` result dict |
| `base_train_config` | function | Minimal valid TrainConfig kwargs |
| `dashboard_client` | function | FastAPI in-process TestClient |
| `checkpoint_dir` | function | Empty tmp directory for checkpoint tests |
| `sample_checkpoint_meta` | function | Canonical checkpoint metadata dict |

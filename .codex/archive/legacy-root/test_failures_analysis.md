# Test Failures Analysis - PR #3552

## Summary
Total failing tests: 36+
Workflows affected: 7

## Failure Categories

### 1. HF Revision Requirement Errors (5 tests)
**Error**: `ValueError: Remote Hugging Face identifiers require an explicit commit hash`

**Affected Tests:**
- `tests/test_modeling_utils.py::test_load_model_and_tokenizer_minimal`
- `tests/test_model_loader.py::test_lora_missing_dependency_fallback`
- `tests/test_model_loader.py::test_model_loading_parameterized[True]`
- `tests/test_model_loader.py::test_model_loading_with_custom_kwargs`
- `tests/utils/test_modeling.py::test_lora_missing`

**Root Cause**: Tests are calling HF model loading without setting `CODEX_HF_REVISION` environment variable or passing `revision=` parameter.

**Fix**: Mock the HF loading calls or set appropriate environment variables in tests.

### 2. Module Import/Attribute Errors (8 tests)
**Error**: `AttributeError: module 'codex' has no attribute 'logging'` or similar

**Affected Tests:**
- `tests/test_db_manager_critical.py::TestDBManagerPoolCleanup::test_close_all_pools_success`
- `tests/test_db_manager_critical.py::TestDBManagerPoolCleanup::test_close_all_pools_multiple_databases`
- `tests/github/test_mcp_poster_session_number.py::test_set_injection_enabled_true`
- `tests/github/test_mcp_poster_session_number.py::test_set_session_number_patch`
- `tests/github/test_mcp_poster_session_number.py::test_cli_set_allowed_actors_s109`
- `tests/github/test_mcp_poster_session_number.py::test_set_allowed_actors_patch`
- `tests/archive/test_retry.py::test_retry_eventually_succeeds`
- `tests/evaluation/test_eval_cli.py::test_run_command_json_output`

**Root Cause**: Tests are using `importlib.reload()` or accessing module attributes incorrectly during module reloading.

**Fix**: Fix import paths or avoid problematic reload patterns.

### 3. Array Comparison Errors (2 tests)
**Error**: `ValueError: The truth value of an array with more than one element is ambiguous`

**Affected Tests:**
- `tests/rag/test_rag_caching_system.py::TestEmbeddingCache::test_embedding_cache_hit`
- `tests/rag/test_rag_caching_system.py::TestEmbeddingCache::test_embedding_cache_persistence`

**Root Cause**: Using Python truthiness check on numpy arrays instead of `.any()` or `.all()`.

**Fix**: Use proper numpy comparison methods.

### 4. Checkpoint State Restoration (2 tests)
**Error**: `assert False` - checkpoint state not restored correctly

**Affected Tests:**
- `tests/test_checkpoint_roundtrip.py::test_checkpoint_roundtrip_restores_states[False]`
- `tests/test_checkpoint_roundtrip.py::test_checkpoint_roundtrip_restores_states[True]`

**Root Cause**: Random states not matching after checkpoint round-trip.

**Fix**: Investigate checkpoint save/restore logic or test randomness setup.

### 5. MLflow/Tracking Issues (3 tests)
**Affected Tests:**
- `tests/tracking/test_mlflow_guard.py::test_bootstrap_respects_allow_remote`
- `tests/test_tracking_mlflow_smoke.py::test_mlflow_local_file_backend`
- `tests/utils/test_codex_utils_offline.py::test_mlflow_offline_session_start_run_false`

**Fix**: Review MLflow configuration in tests.

### 6. YAML Workflow Validation (1 test)
**Error**: Invalid YAML in ci-health-monitor.yml

**Affected Tests:**
- `tests/validation/test_ci_workflow_validation.py::TestWorkflowFileValidation::test_workflow_files_valid_yaml`

**Status**: ✅ FIXED - Used heredoc syntax for Python code blocks

### 7. Miscellaneous Test Logic Failures (15+ tests)
Various assertion failures, missing attributes, configuration issues, etc.

## Priority Order
1. ✅ Fix YAML syntax (DONE)
2. Fix HF revision errors (affects 5 tests)
3. Fix module import errors (affects 8 tests)
4. Fix array comparison errors (affects 2 tests)
5. Fix checkpoint restoration (affects 2 tests)
6. Fix remaining individual failures

## Implementation Status
- [x] YAML syntax fix
- [ ] HF revision errors
- [ ] Module import errors
- [ ] Array comparison errors
- [ ] Checkpoint tests
- [ ] Miscellaneous fixes

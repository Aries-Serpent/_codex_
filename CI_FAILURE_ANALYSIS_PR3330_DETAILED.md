# CI Failure Analysis for PR #3330

**Branch:** `copilot/implement-production-hardening-phase-3`  
**Analysis Date:** 2026-02-19  
**Latest Workflow Run:** Run #22168486296 (Resilient Validation), #22168485507 (Art_RAG)

---

## Executive Summary

**3 CI workflows are failing** on PR #3330:
1. ✅ **Progressive Validation Suite** - PASSING
2. ❌ **Resilient Validation Suite (Quick)** - 20 failures
3. ❌ **Resilient Validation Suite (Slow)** - 5 failures  
4. ❌ **Art_RAG Module Tests** - No tests collected (exit code 5)

---

## 1. Resilient Validation Suite (Quick) - 20 Failures

**Job ID:** 64162829937  
**Status:** Failed (20 failed, 260 passed, 50 skipped)  
**Duration:** ~4.5 minutes

### Failure Details

#### A. Pickle/Serialization Errors (2 failures)
**Files:** `tests/test_checkpoint_roundtrip.py`

```python
FAILED tests/test_checkpoint_roundtrip.py::test_checkpoint_roundtrip_restores_states[True]
FAILED tests/test_checkpoint_roundtrip.py::test_checkpoint_roundtrip_restores_states[False]
```

**Error:**
```
_pickle.PicklingError: Can't pickle <class 'torch.FloatStorage'>: it's not the same object as torch.FloatStorage
```

**Root Cause:** PyTorch storage class pickling issue, likely due to version mismatch or meta tensor initialization.

---

#### B. JSON Serialization Error (1 failure)
**File:** `tests/test_metrics_tb.py`

```python
FAILED tests/test_metrics_tb.py::test_tb_writer_guard
```

**Error:**
```
TypeError: Object of type MagicMock is not JSON serializable
```

**Root Cause:** Test is attempting to JSON-serialize a MagicMock object.

---

#### C. CLI Training Test Failure (1 failure)
**File:** `tests/test_cli_train_command.py`

```python
FAILED tests/test_cli_train_command.py::test_cli_train_creates_checkpoint
```

**Error:**
```
AssertionError: Error: training dataset is empty or missing
assert 1 == 0
 +  where 1 = <Result SystemExit(1)>.exit_code
```

**Root Cause:** Training dataset not found or not properly configured for the test.

---

#### D. Determinism Test Failure (1 failure)
**File:** `tests/test_determinism.py`

```python
FAILED tests/test_determinism.py::test_seed_repeats
```

**Error:**
```
assert [0.6816085577...0832138061523] == [0.5529070496...1737747192383]
  At index 0 diff: 0.6816085577011108 != 0.5529070496559143
```

**Root Cause:** Random seed not producing deterministic results - RNG state not properly controlled.

---

#### E. Mental Mapping Test Failures (7 failures)
**File:** `tests/agents/test_mental_mapping_core_flows.py`

```python
FAILED test_think_through_problem_evidence_gathering
FAILED test_record_outcome_triggers_appraisal - KeyError: 'total_outcomes'
FAILED test_save_and_load_mental_map - AttributeError: 'NoneType' object has no attribute 'value'
FAILED test_self_appraise_identifies_poor_decision - assert 0 > 0
FAILED test_think_through_problem_with_decomposition
FAILED test_create_node - TypeError: MentalMappingModel.create_node() got an unexpected keyword argument 'metadata'
FAILED test_iterative_review_marks_completed - AssertionError: assert (not True or 0.5 > 0.5)
```

**Root Causes:**
- Missing `'total_outcomes'` key in dictionary
- NoneType attribute access on `.value`
- `create_node()` doesn't accept `metadata` kwarg (API change)
- Logic errors in appraisal and review conditions

---

#### F. Test Suite Validation Failures (8 failures)
**File:** `tests/validation/test_test_suite_validation.py`

**F.1: Naming Convention Violations**
```python
FAILED test_test_files_follow_naming_convention
```
**13 files** not following `test_*.py` convention:
- `tests/_bootstrap_determinism.py`
- `tests/_codex_introspect.py`
- `tests/_workflow_trigger.py`
- `tests/smoke_test_github_logs.py`
- `tests/specs/_workflow_config_utils.py`
- `tests/specs/flow_specifications.py`
- `tests/fixtures/zaf_legacy.py`
- `tests/utils/quantum_helpers.py`
- `tests/utils/torch_helpers.py`
- `tests/utils/doc_refactor_helpers.py`
- `tests/utils/cli_runner.py`
- `tests/helpers/optional_dependencies.py`
- `tests/archival/security_utils.py`

**F.2: Missing __init__.py Files**
```python
FAILED test_test_directories_have_init_files
```
**106 directories** missing `__init__.py` (expected ≤5)

**F.3: Missing Assertions**
```python
FAILED test_assert_statements_used
```
**47 test files** without assertions

**F.4: Missing Docstrings**
```python
FAILED test_test_functions_have_docstrings
```
**1058 test functions** missing docstrings (expected ≤10)

**F.5: Invalid Class Names**
```python
FAILED test_test_class_naming_convention
```
**9 invalid test class names** (not starting with `Test`):
- `_TestLogger`, `SimpleTestModel`, `MultiGPUTestHarness`, `FlakyTestReport`, etc.

**F.6: Global State Modification**
```python
FAILED test_no_global_state_modification
```
**59 files** with potential global state issues (expected ≤5)

**F.7: Hardcoded File Paths**
```python
FAILED test_no_hardcoded_file_paths
```
**5 files** with hardcoded paths:
- `tests/test_metadata_calculation.py`
- `tests/security/test_validators.py`
- `tests/validation/test_test_suite_validation.py`
- `tests/branch_coverage/test_branch_coverage_utils.py`
- `tests/scripts/mcp/test_flatten_files_phase9_2.py`

---

#### G. Generated Test Failure (1 failure)
**File:** `tests/generated/test_physicsinspiredorchestrator_orchestrate.py`

```python
FAILED test_orchestrate_happy_path
```

**Error:**
```
AttributeError: 'ellipsis' object has no attribute 'current_position'
```

**Root Cause:** Test using `...` (Ellipsis) incorrectly - likely a placeholder not replaced.

---

## 2. Resilient Validation Suite (Slow) - 5 Failures

**Job ID:** 64162829966  
**Status:** Failed (5 failed, 279 passed, 84 skipped)  
**Duration:** ~5.8 minutes

### Failure Details

#### A. MLflow Configuration Error (1 failure)
**File:** `tests/test_training_engine.py`

```python
FAILED test_training_engine_handles_missing_mlflow
```

**Error:**
```
AssertionError: assert not True
 +  where True = TrainingEngine(enable_mlflow=True, ...).enable_mlflow
```

**Root Cause:** Test expects `enable_mlflow` to be False when MLflow is missing, but it's True.

---

#### B. Type Checking Error (1 failure)
**File:** `tests/space_traversal/test_peft_comprehensive/test_custom_loop_overfit.py`

```python
FAILED test_overfit_tiny
```

**Error:**
```
TypeError: isinstance() arg 2 must be a type, a tuple of types, or a union
```

**Root Cause:** Invalid type passed to `isinstance()` - likely using a string or non-type object.

---

#### C. Datetime Timezone Error (1 failure)
**File:** `tests/cognitive_brain/quantum/test_memory.py`

```python
FAILED TestIntegration::test_statistics_comprehensive
```

**Error:**
```
TypeError: can't subtract offset-naive and offset-aware datetimes
```

**Root Cause:** Mixing timezone-aware and timezone-naive datetime objects.

---

#### D. MLflow URI Assertion Error (1 failure)
**File:** `tests/cli/test_tracking_cli_comprehensive.py`

```python
FAILED TestMLflowEnablement::test_enable_mlflow_without_uri
```

**Error:**
```
AssertionError: assert ('file:///home/runner/work/_codex_/_codex_/.mlruns' == 'mlruns'
  - mlruns
  + file:///home/runner/work/_codex_/_codex_/.mlruns or 'warning' in {...})
```

**Root Cause:** Test expects relative path `'mlruns'`, but got absolute file URI.

---

#### E. Type Subscription Error (1 failure)
**File:** `tests/cli/test_feature_store_cli_comprehensive.py`

```python
FAILED TestFeatureRegistration::test_register_with_custom_store_path
```

**Error:**
```
TypeError: 'function' object is not subscriptable
```

**Root Cause:** Attempting to subscript a function (e.g., `function[key]`) instead of calling it.

---

## 3. Art_RAG Module Tests - CRITICAL ISSUE

**Job ID:** 64162823696  
**Status:** Failed with exit code 5  
**Duration:** ~5.9 minutes

### Root Cause: NO TESTS COLLECTED

**Error:**
```
======================= no tests ran in 82.91s (0:01:22) =======================
##[error]Process completed with exit code 5.
```

**Issue:** The workflow runs `pytest tests/test_rag_*.py` but **NO test files match this pattern**.

**Workflow Configuration (.github/workflows/test-rag.yml:114):**
```yaml
python -m pytest tests/test_rag_*.py \
  -n auto \
  -v \
  --tb=short --timeout=300 \
  --cov=src \
  --cov-report=xml \
  --cov-report=html \
  --cov-report=term-missing
```

**Resolution Required:**
1. **Either:** Create test files matching `tests/test_rag_*.py` pattern
2. **Or:** Update workflow to match existing RAG test files (e.g., `tests/rag/test_*.py`)
3. **Or:** Disable/skip this workflow if RAG tests are located elsewhere

---

## Priority Recommendations

### 🔴 **Critical (Must Fix Before Merge)**

1. **Art_RAG Test Collection** - No tests found
   - **Action:** Verify test file locations and update workflow pattern
   
2. **PyTorch Pickle Error** - Blocking checkpoint tests
   - **Action:** Check torch version compatibility and meta tensor usage

### 🟡 **High Priority**

3. **Mental Mapping Tests** - 7 failures suggest API changes
   - **Action:** Update tests to match current `MentalMappingModel` API
   
4. **Datetime Timezone** - Timezone-aware/naive mismatch
   - **Action:** Standardize on UTC timezone-aware datetimes

5. **Determinism Test** - RNG not deterministic
   - **Action:** Review seed setting and RNG state management

### 🟢 **Medium Priority (Technical Debt)**

6. **Test Suite Validation** - 106 missing `__init__.py`, 1058 missing docstrings
   - **Action:** Create cleanup issue, incrementally address violations

7. **MLflow Configuration** - URI and enable flag mismatches
   - **Action:** Update tests to match current MLflow configuration logic

---

## Next Steps

1. **Investigate RAG test location** - Find where RAG tests actually are
2. **Fix critical pickle error** - Check PyTorch version and meta tensor initialization
3. **Update Mental Mapping tests** - Align with current API
4. **Fix datetime handling** - Use timezone-aware datetimes consistently
5. **Address determinism** - Ensure proper RNG seeding

---

## Test Execution Summary

| Workflow | Status | Passed | Failed | Skipped | Total |
|----------|--------|--------|--------|---------|-------|
| Progressive Validation | ✅ PASS | - | - | - | - |
| Resilient (Quick) | ❌ FAIL | 260 | 20 | 50 | 330 |
| Resilient (Slow) | ❌ FAIL | 279 | 5 | 84 | 368 |
| Art_RAG Tests | ❌ FAIL | 0 | 0 | 0 | **0** (No tests collected) |

**Total Failures:** 25 failing tests + 1 critical workflow configuration issue

---


## Additional Investigation: Art_RAG Test Collection

### Test Files Actually Exist!

Found **14 RAG test files** in `tests/` directory matching pattern `test_rag_*.py`:
- `tests/test_rag_cached_retriever.py`
- `tests/test_rag_embeddings.py`
- `tests/test_rag_end_to_end_pipeline.py`
- `tests/test_rag_error_handling.py`
- `tests/test_rag_indexer.py`
- `tests/test_rag_initialization_patterns.py`
- `tests/test_rag_integration.py`
- `tests/test_rag_meta_tensor_regression.py`
- `tests/test_rag_monitoring.py`
- `tests/test_rag_postprocess.py`
- `tests/test_rag_prompt.py`
- `tests/test_rag_retriever.py`
- `tests/test_rag_tenant_management.py`
- `tests/test_rag_utils.py`

**Plus tests in `tests/rag/` subdirectory:**
- `tests/rag/test_chunking.py`
- `tests/rag/test_device_placement.py`
- `tests/rag/test_embeddings_comprehensive.py`
- `tests/rag/test_gpu_utils.py`
- `tests/rag/test_indexer_comprehensive.py`
- `tests/rag/test_pipeline_integration.py`
- `tests/rag/test_pipelines.py`
- `tests/rag/test_postprocess_utils.py`
- `tests/rag/test_prompt_comprehensive.py`
- `tests/rag/test_quantum_retrieval.py`
- `tests/rag/test_rag_caching_system.py`
- `tests/rag/test_rag_functionality_comprehensive.py`
- `tests/rag/test_rag_integration.py`
- `tests/rag/test_rag_integration_advanced.py`

### Why Did Tests Not Run?

**Hypothesis:** Workflow path filter prevented execution.

**Workflow Trigger (.github/workflows/test-rag.yml:6-15):**
```yaml
on:
  push:
    branches: [main, develop, copilot/**]
    paths:
      - 'src/codex/rag/**'
      - 'tests/test_rag_**'
      - 'pyproject.toml'
  pull_request:
    branches: [main, develop]
    paths:
      - 'src/codex/rag/**'
      - 'tests/test_rag_**'
      - 'pyproject.toml'
```

**Issue:** The workflow triggered but pytest found no tests. Possible causes:

1. **Import Error During Collection** - Tests failed to import, causing pytest to skip them
2. **Path Issue** - Working directory different than expected
3. **Plugin Loading Failure** - pytest-xdist or other plugins failed to load
4. **Collection Filter** - Some pytest configuration excluded the tests

### Most Likely Cause: Import Error

Given that coverage shows `0.10%` and "no tests ran", the tests likely failed during the **collection phase** due to import errors.

**Evidence:**
- Workflow shows: `Coverage HTML written to dir htmlcov` (coverage ran)
- Workflow shows: `no tests ran in 82.91s` (collection completed but found nothing)
- Exit code 5 = pytest "no tests collected" error

**Action Required:**
1. Check for import errors in RAG test files
2. Verify `src/codex/rag/` module imports work correctly
3. Check if RAG dependencies are installed (e.g., `sentence-transformers`, etc.)
4. Review pytest collection warnings/errors (not visible in truncated logs)

---


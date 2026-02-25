# GitHub Actions Test Failure Analysis - Latest Run
**Generated**: 2026-02-07
**Workflow**: RAG Module Tests
**Run ID**: 21631025717
**Job ID**: 62343509037
**Status**: ❌ FAILED
**Commit**: c650b66f2d004a6c5b297f9b647c211dd47cdb98
**Date**: 2026-02-03T13:04:12Z

---

## Executive Summary

**Total Failed Tests**: 41 out of 117+ tests
**Failure Rate**: ~35%
**Primary Issue**: Meta tensor initialization errors and missing mock attributes

### Critical Findings

1. ✅ **No MockRepo.create errors found** - Previously resolved
2. ✅ **No StopIteration errors found** - Fixed in PR #3170
3. ✅ **No RuntimeError found** (unrelated to meta tensor issues)
4. ✅ **No ValueError found**
5. ✅ **No MagicMock JSON serialization errors found**
6. ❌ **NEW: Meta tensor initialization errors** - 16 failures
7. ❌ **NEW: FakeSentenceTransformer missing `.to()` method** - 12 failures
8. ❌ **NEW: Tenant management test failures** - 11 failures

---

## Failure Breakdown by Error Type

### 1. Meta Tensor Errors (16 failures) - CRITICAL 🔴

**Error Message**:
```
NotImplementedError: Cannot copy out of meta tensor; no data!
Please use torch.nn.Module.to_empty() instead of torch.nn.Module.to()
when moving module from meta to a different device.
```

**Root Cause**: The RAG module is attempting to load sentence-transformer models using `torch.nn.Module.to()` on meta tensors, which is not supported in newer PyTorch/transformers versions (v5.0.0).

**Affected Tests** (showing first 10):
1. `tests/test_rag_error_handling.py::TestResourceExhaustion::test_very_large_top_k`
2. `tests/test_rag_indexer.py::TestEmbedChunks::test_basic_embedding`
3. `tests/test_rag_indexer.py::TestEmbedChunks::test_custom_model_profile`
4. `tests/test_rag_indexer.py::TestBuildIndexFromFiles::test_build_from_sample_files`
5. `tests/test_rag_indexer.py::TestBuildIndexFromFiles::test_build_with_nonexistent_file`
6. `tests/test_rag_indexer.py::TestEndToEnd::test_full_workflow`
7. `tests/test_rag_indexer.py::TestEmbedChunksErrorPaths::test_embed_chunks_import_error_coverage`
8. `tests/test_rag_integration.py::TestEndToEndPipeline::test_full_workflow_docs_to_query`
9. `tests/test_rag_integration.py::TestMultiTenantIsolation::test_tenant_isolation`
10. `tests/test_rag_integration.py::TestCacheEffectiveness::test_cache_hit_rate`

**Source Location**: `src/codex/rag/indexer.py:148` (ERROR log entry)

**Recommended Fix**:
```python
# Current code (problematic):
model = SentenceTransformer(model_name)
model = model.to(device)

# Suggested fix:
if hasattr(model, 'to_empty'):
    # For models with meta tensors (PyTorch 2.0+)
    model = model.to_empty(device=device)
    # Then load weights
else:
    # Fallback for older versions
    model = model.to(device)
```

---

### 2. FakeSentenceTransformer AttributeError (12 failures) - HIGH 🟡

**Error Message**:
```
AttributeError: 'FakeSentenceTransformer' object has no attribute 'to'
```

**Root Cause**: Test fixture `FakeSentenceTransformer` mock object doesn't implement the `.to()` method required by the production code.

**Affected Tests** (showing first 10):
1. `tests/test_rag_end_to_end_pipeline.py::test_embed_chunks_returns_embeddings`
2. `tests/test_rag_end_to_end_pipeline.py::test_persist_and_load_index_roundtrip`
3. `tests/test_rag_end_to_end_pipeline.py::test_retriever_query_returns_results`
4. `tests/test_rag_end_to_end_pipeline.py::test_retriever_query_min_score_filters`
5. `tests/test_rag_end_to_end_pipeline.py::test_retriever_query_empty_index_returns_empty`
6. `tests/test_rag_initialization_patterns.py::test_local_provider_uses_default_device_allocation`
7. `tests/test_rag_initialization_patterns.py::test_local_provider_sets_device_cpu`
8. `tests/test_rag_initialization_patterns.py::test_local_provider_calls_eval`
9. `tests/test_rag_initialization_patterns.py::test_embed_chunks_uses_default_device_allocation`
10. `tests/test_rag_initialization_patterns.py::test_embed_chunks_passes_cache_folder`

**Source Location**: `src/codex/rag/embeddings.py:101` (ERROR log entry)

**Recommended Fix**:
```python
# Add to test fixtures (conftest.py or test file)
class FakeSentenceTransformer:
    def __init__(self, *args, **kwargs):
        self.device = 'cpu'

    def to(self, device):
        """Mock the .to() method for device placement"""
        self.device = device
        return self

    def eval(self):
        """Mock the .eval() method"""
        return self

    def encode(self, texts, **kwargs):
        # Existing implementation
        pass
```

---

### 3. Tenant Management Assertion Errors (11 failures) - MEDIUM 🟠

**Error Patterns**:
- `assert False is True` (7 failures)
- `assert 'Found' in "No indices found..."` (1 failure)
- `assert 'docs' in []` (1 failure)
- `TypeError: 'NoneType' object is not subscriptable` (1 failure)
- `AssertionError: assert False` (1 failure)

**Root Cause**: Tenant management operations (create, delete, merge, list) are returning failure status or incorrect results.

**Affected Tests**:
1. `tests/test_rag_tenant_management.py::TestManageTenantIndices::test_delete_operation_success`
2. `tests/test_rag_tenant_management.py::TestManageTenantIndices::test_delete_operation_multiple_indices`
3. `tests/test_rag_tenant_management.py::TestManageTenantIndices::test_delete_operation_partial_failure`
4. `tests/test_rag_tenant_management.py::TestManageTenantIndices::test_merge_operation_success`
5. `tests/test_rag_tenant_management.py::TestManageTenantIndices::test_merge_operation_single_index`
6. `tests/test_rag_tenant_management.py::TestManageTenantIndices::test_list_operation_success`
7. `tests/test_rag_tenant_management.py::TestManageTenantIndices::test_list_operation_multiple_tenants`
8. `tests/test_rag_tenant_management.py::TestManageTenantIndices::test_operation_case_insensitive`
9. `tests/test_rag_tenant_management.py::TestManageTenantIndices::test_custom_chunk_parameters`
10. `tests/test_rag_tenant_management.py::TestManageTenantIndices::test_tenant_directory_creation`
11. `tests/test_rag_tenant_management.py::TestManageTenantIndices::test_create_with_error_in_one_index`

**Example Failure**:
```python
# tests/test_rag_tenant_management.py:181
def test_delete_operation_success(tmp_path):
    # ...
    assert create_result.success is True  # ← Failing here (returns False)
```

**Recommended Investigation**:
1. Check if tenant management functions are properly creating/deleting indices
2. Verify file system operations in test environment
3. Review error handling in tenant management module
4. Check if the meta tensor issue is cascading to tenant operations

---

### 4. Other Errors (4 failures) - LOW 🟢

**a) OSError - Network/Model Loading (1 failure)**:
```
OSError: There was a specific connection error when trying to load
sentence-transformers/all-MiniLM-L6-v2
```
- Test: `tests/test_rag_utils.py::TestIntegrationMetaTensorHandling::test_sentence_transformer_loading_with_safe_model_load_v2`
- Cause: Network issue or model not cached
- Fix: Ensure models are pre-downloaded in CI (workflow already has this step)

**b) Meta Tensor Detection Logic (1 failure)**:
```
assert True is False
```
- Test: `tests/test_rag_utils.py::TestCheckForMetaTensors::test_model_without_meta_tensors`
- Cause: Meta tensor detection utility may be incorrectly identifying models
- Fix: Review `check_for_meta_tensors()` implementation

---

## Failure Distribution by Test File

| File | Failures | Percentage |
|------|----------|------------|
| `tests/test_rag_tenant_management.py` | 11 | 26.8% |
| `tests/test_rag_initialization_patterns.py` | 7 | 17.1% |
| `tests/test_rag_integration.py` | 7 | 17.1% |
| `tests/test_rag_indexer.py` | 6 | 14.6% |
| `tests/test_rag_end_to_end_pipeline.py` | 5 | 12.2% |
| `tests/test_rag_retriever.py` | 2 | 4.9% |
| `tests/test_rag_utils.py` | 2 | 4.9% |
| `tests/test_rag_error_handling.py` | 1 | 2.4% |
| **Total** | **41** | **100%** |

---

## Previously Fixed Issues ✅

Based on repository documentation review:

### 1. StopIteration Errors - RESOLVED ✅
- **Status**: Fixed in recent commits
- **Documentation**: `docs/testing/STOPITERATION_FIX_REPORT.md`
- **Scope**: 20+ tests across 3 files
- **Fix**: Conditional class definitions and safe iterator usage
- **Files Fixed**:
  - `tests/unit/interpretability/test_attention_scorer.py`
  - `tests/unit/interpretability/test_mlp_scorer.py`
  - `tests/training/test_train_loop_coverage.py`

### 2. Integration Test Failures - RESOLVED ✅
- **Status**: Fixed in PR #3178
- **Documentation**: `TEST_FIXES_SUMMARY.md`
- **Scope**: 23 integration test failures
- **Categories Fixed**:
  - Genesis workflow path updates
  - WorkflowParser missing methods
  - Archive DAL test expectations
  - CLI/Hydra config structure
  - SQLite DAL test logic
  - Sanitization recursive handling

### 3. Test Pattern Quality - RESOLVED ✅
- **Status**: Completed in PR #2959
- **Documentation**: `.codex/cognitive_brain/test_failure_resolution_status.md`
- **Scope**: 5 critical test failures + 24 code review comments
- **Improvements**:
  - Mock fixtures standardized
  - JSON serialization patterns added
  - Hydra config schema compliance
  - Duplicate code eliminated

---

## Recommended Action Plan

### Priority 1 - CRITICAL (Meta Tensor Issues)

**Task 1.1**: Fix model initialization in `src/codex/rag/indexer.py`
```python
# File: src/codex/rag/indexer.py (around line 148)
# Replace:
model = SentenceTransformer(model_name)
model = model.to(device)

# With:
from codex.rag.utils import safe_model_load
model = safe_model_load(model_name, device=device)
```

**Task 1.2**: Update safe_model_load utility
```python
# File: src/codex/rag/utils.py
def safe_model_load(model_name: str, device: str = "cpu"):
    """Safely load model handling meta tensors in PyTorch 2.0+"""
    from sentence_transformers import SentenceTransformer
    import torch

    model = SentenceTransformer(model_name)

    # Check if model has meta tensors
    has_meta_tensor = any(
        param.is_meta for param in model.parameters()
    )

    if has_meta_tensor:
        # Use to_empty for meta tensors
        model = model.to_empty(device=torch.device(device))
    else:
        # Standard device placement
        model = model.to(device)

    return model.eval()
```

**Task 1.3**: Update embeddings module
```python
# File: src/codex/rag/embeddings.py (around line 101)
# Similar fix for local embedding model loading
```

**Estimated Time**: 2-3 hours
**Expected Impact**: Fixes 16 test failures

---

### Priority 2 - HIGH (Mock Fixture)

**Task 2.1**: Update FakeSentenceTransformer mock
```python
# File: tests/conftest.py or tests/test_rag_end_to_end_pipeline.py
class FakeSentenceTransformer:
    """Mock SentenceTransformer for testing"""

    def __init__(self, model_name: str = "fake-model", *args, **kwargs):
        self.model_name = model_name
        self.device = "cpu"
        self._is_training = True

    def to(self, device):
        """Mock device placement"""
        self.device = device if isinstance(device, str) else str(device)
        return self

    def to_empty(self, device):
        """Mock meta tensor device placement"""
        return self.to(device)

    def eval(self):
        """Mock eval mode"""
        self._is_training = False
        return self

    def encode(self, texts, batch_size=32, show_progress_bar=False, **kwargs):
        """Mock encoding"""
        import numpy as np
        if isinstance(texts, str):
            texts = [texts]
        return np.random.rand(len(texts), 384)  # 384-dim embeddings

    def parameters(self):
        """Mock parameters for meta tensor check"""
        return []
```

**Estimated Time**: 1-2 hours
**Expected Impact**: Fixes 12 test failures

---

### Priority 3 - MEDIUM (Tenant Management)

**Task 3.1**: Debug tenant management operations
1. Add detailed logging to tenant creation/deletion
2. Check file system permissions in test environment
3. Verify index directory paths are correct
4. Review error handling in tenant operations

**Task 3.2**: Fix specific issues
- `test_delete_operation_success`: Check why `create_result.success` is False
- `test_list_operation_success`: Verify tenant directory creation
- `test_delete_operation_partial_failure`: Fix NoneType subscriptable error

**Estimated Time**: 3-4 hours
**Expected Impact**: Fixes 11 test failures

---

### Priority 4 - LOW (Other Issues)

**Task 4.1**: Ensure model pre-download works
- Verify GitHub Actions cache is working
- Check network connectivity in CI
- Add retry logic for model downloads

**Task 4.2**: Fix meta tensor detection
- Review `check_for_meta_tensors()` logic
- Add unit tests for detection function

**Estimated Time**: 1-2 hours
**Expected Impact**: Fixes 2 test failures

---

## Total Impact Estimate

| Priority | Tasks | Failures Fixed | Est. Time |
|----------|-------|----------------|-----------|
| P1 - Critical | 3 | 16 | 2-3 hours |
| P2 - High | 1 | 12 | 1-2 hours |
| P3 - Medium | 2 | 11 | 3-4 hours |
| P4 - Low | 2 | 2 | 1-2 hours |
| **Total** | **8** | **41** | **7-11 hours** |

---

## CI/CD Recommendations

1. **Pre-download Models**: ✅ Already implemented in workflow (step 7)
2. **Cache Strategy**: Review cache keys for model artifacts
3. **Dependency Pinning**: Consider pinning transformers version or handling v5.0.0 compatibility
4. **Test Isolation**: Ensure tenant management tests use isolated temp directories
5. **Meta Tensor Checks**: Add explicit checks for PyTorch/transformers versions

---

## References

- **Workflow Run**: https://github.com/Aries-Serpent/_codex_/actions/runs/21631025717 <!-- Note: Logs expire after 90 days -->
- **Job Details**: https://github.com/Aries-Serpent/_codex_/actions/runs/21631025717 <!-- Note: Logs expire after 90 days -->/job/62343509037
- **Commit**: c650b66f2d004a6c5b297f9b647c211dd47cdb98
- **Related Documentation**:
  - `docs/testing/STOPITERATION_FIX_REPORT.md` - Previous StopIteration fixes
  - `TEST_FIXES_SUMMARY.md` - Integration test fixes (PR #3178)
  - `.codex/cognitive_brain/test_failure_resolution_status.md` - Test pattern improvements

---

## Next Steps

1. **Immediate**: Create PR to fix Priority 1 (meta tensor issues)
2. **Follow-up**: Address Priority 2 (mock fixtures) in same or separate PR
3. **Investigation**: Debug Priority 3 (tenant management) with detailed logging
4. **Monitoring**: Track Priority 4 issues in separate GitHub issues

---

**Report Generated By**: CI Log Retrieval Agent
**Agent Version**: 1.0.0
**Report Date**: 2026-02-07T00:00:00Z
**Status**: ✅ ANALYSIS COMPLETE

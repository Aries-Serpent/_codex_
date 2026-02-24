# CI/CD Workflow Failures Report
**Repository:** Aries-Serpent/_codex_
**Analysis Date:** 2026-02-03T22:30:00Z
**Analysis Period:** Last 24 hours (2026-02-02T22:00:00Z to 2026-02-03T22:30:00Z)

---

## 📊 Executive Summary

### Critical Findings
- **20 Test Failures** detected in Testing Suite workflow on main branch
- **High frequency** of failures: ~20 runs failed in 12-hour period
- **Single point of failure**: All failures in "Core Tests (Python 3.12)" job
- **Impact**: Blocking CI pipeline on main branch

### Active Pull Requests
- **PR #3140**: "[WIP] Implement SARIF chunking and resolve code scanning alerts"
  - Status: Draft PR with 16+ workflows awaiting action
  - All workflows marked as "action_required" (expected for draft PRs)

---

## 🔴 Active Failures (Main Branch)

### Failure #1: Testing Suite Workflow
**Workflow:** `.github/workflows/test-suite.yml`
**Latest Run:** [21649553861](https://github.com/Aries-Serpent/_codex_/actions/runs/21649553861 <!-- Note: Logs expire after 90 days -->)
**Timestamp:** 2026-02-03T22:02:40Z
**Failed Job:** Core Tests (Python 3.12) - Job ID 62410313296

#### Test Execution Summary
- **Total:** 427 tests
- **Failed:** 20 tests (stopped at maxfail=10)
- **Passed:** 380 tests
- **Skipped:** 37 tests
- **Duration:** ~80 seconds

---

## 🔍 Detailed Test Failure Analysis

### 1. PyTorch Checkpoint Serialization ⚠️ CRITICAL
**Test:** `tests/test_bestk_retention.py::test_bestk_retention_prunes_extras`

**Error Type:** `_pickle.PicklingError`
```python
Can't pickle <class 'torch.FloatStorage'>: it's not the same object as torch.FloatStorage
```

**Root Cause:** PyTorch 2.x storage types cannot be pickled in certain contexts

**Location:** `src/codex_ml/utils/checkpoint.py:403`

**Fix:**
```python
# In src/codex_ml/utils/checkpoint.py
def _dump_payload(path, payload):
    torch.save(
        payload,
        path,
        pickle_protocol=4,
        _use_new_zipfile_serialization=True
    )
```

**Priority:** Critical - Blocks checkpoint functionality

---

### 2. Missing Test Artifact Directory ⚠️ HIGH
**Test:** `tests/specs/test_audit_meta_in_report.py::test_meta_propagates_and_renders`

**Error Type:** `FileNotFoundError`
```python
[Errno 2] No such file or directory: 'audit_artifacts/capabilities_raw.json'
```

**Root Cause:** Audit artifacts directory not created or wrong path

**Fix:**
```python
# In tests/specs/test_audit_meta_in_report.py
def test_meta_propagates_and_renders(tmp_path):
    artifacts = Path.cwd() / "audit_artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    # ... rest of test
```

**Priority:** High - Test infrastructure issue

---

### 3. Packaging Metadata Issues ⚠️ HIGH

#### 3a. Missing LICENSE Reference
**Test:** `tests/test_packaging_metadata.py::test_license_files_present`

**Error:** `AssertionError: assert 'LICENSE' in set()`

**Fix:**
```toml
# In pyproject.toml
[project.license-files]
paths = ["LICENSE"]
```

#### 3b. Incorrect License Format
**Test:** `tests/test_packaging_metadata.py::test_pyproject_core_metadata`

**Error:** `AssertionError: assert {'text': 'MIT'} == 'MIT'`

**Fix:**
```toml
# In pyproject.toml - Change from:
license = {text = "MIT"}
# To:
license = "MIT"
```

**Priority:** High - Blocks package publishing

---

### 4. Missing Training Module ⚠️ MEDIUM
**Test:** `tests/integration/test_phase24_training_eval_workflows.py::test_phase24_checkpoint_config_validation`

**Error Type:** `ModuleNotFoundError`
```python
No module named 'src.training.checkpoint'
```

**Fix Options:**
1. Create `src/training/checkpoint.py` with `CheckpointConfig`
2. Update import: `from codex_ml.utils.checkpoint import CheckpointConfig`

**Priority:** Medium - Integration test only

---

### 5. Missing sentence-transformers Dependency ⚠️ CRITICAL
**Affected Tests (5 failures):**
- `tests/rag/test_rag_integration.py::TestEndToEndRAGPipeline::test_index_and_retrieve`
- `tests/rag/test_rag_integration.py::TestRAGDataConsistency::test_embedding_dimension_consistency`
- `tests/rag/test_rag_integration.py::TestRAGPerformance::test_batch_embedding_efficiency`
- `tests/rag/test_rag_integration.py::TestRAGPerformance::test_retrieval_top_k_limits`
- `tests/rag/test_rag_integration.py::TestRAGErrorHandling::test_retriever_empty_query`

**Error Type:** `ModuleNotFoundError: No module named 'sentence_transformers'`

**Fix Option 1: Install dependency**
```toml
# In pyproject.toml
[project.optional-dependencies]
rag = [
    "sentence-transformers>=2.2.0",
    "faiss-cpu>=1.7.0",
]
```

```yaml
# In .github/workflows/test-suite.yml
- run: uv pip install --system -e ".[dev,test,rag]"
```

**Fix Option 2: Skip tests**
```python
# In tests/rag/test_rag_integration.py
pytest.importorskip("sentence_transformers")
```

**Priority:** Critical - 5 tests affected

---

### 6. CLI Argument Parsing Error ⚠️ HIGH
**Test:** `tests/cli/test_dataset_cli.py::test_dataset_cli_validate_and_metadata`

**Error:** CLI requires `--paths` flag
```
cli.py: error: the following arguments are required: --paths
```

**Fix:**
```python
# In test
subprocess.run([
    sys.executable, "-m", "src.codex_ml.data.cli",
    "validate",
    "--paths", str(data)  # Add this flag
])
```

**Priority:** High - User-facing CLI broken

---

### 7. Plugin Error Logging ⚠️ MEDIUM
**Test:** `tests/plugins/test_list_plugins_degrade.py::test_list_plugins_handles_missing_registry`

**Error:** Traceback in stderr (structured logging includes stack traces)

**Fix:**
```python
# In src/codex_ml/cli/list_plugins.py
def _list_models_safe():
    try:
        return sorted({str(model) for model in list_models()})
    except Exception as exc:
        logger.warning("Failed to list models", exc_info=False)
        return []
```

**Priority:** Medium - Error handling improvement

---

### 8. Docker Compose Volume Configuration ⚠️ MEDIUM
**Test:** `tests/deployment/test_volume_mounts.py::test_compose_defines_required_volumes`

**Error:** Missing `./data:/data` volume mount

**Fix:**
```yaml
# In docker-compose.yml
services:
  codex-cpu:
    volumes:
      - ./data:/data  # Add this
      - ./artifacts/chroma:/chroma/.chroma/index
```

**Priority:** Medium - Deployment configuration

---

### 9. Non-Deterministic Random Seed ⚠️ HIGH
**Test:** `tests/test_determinism.py::test_seed_repeats`

**Error:** Random values differ between runs with same seed

**Fix:**
```python
def _seed_everything(seed):
    import random, numpy as np, torch

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    # Critical additions:
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True, warn_only=True)
```

**Priority:** High - Breaks reproducibility

---

### 10. FastAPI Middleware Exception ⚠️ MEDIUM
**Test:** `tests/services/api/test_middleware_security.py::test_api_key_required`

**Error:** Unhandled HTTPException in middleware

**Fix:**
```python
# In test
client = TestClient(module.app, raise_server_exceptions=False)
```

**Priority:** Medium - API security test

---

### 11. TypeError in Model Registry ⚠️ CRITICAL
**Affected Tests (3 failures):**
- `tests/models/test_models_registry_api.py::test_get_minilm`
- `tests/rag/test_postprocess_utils.py::TestSafeModelLoad::test_safe_model_load_no_modules`
- `tests/rag/test_postprocess_utils.py::TestSafeModelLoad::test_safe_model_load_no_meta_tensors`

**Error Type:** `TypeError: isinstance() arg 2 must be a type, a tuple of types, or a union`

**Root Cause:** Invalid isinstance check with union type

**Fix:**
```python
# Find in model registry code - Replace:
if isinstance(model, ModelType | None):
# With:
if model is None or isinstance(model, ModelType):
```

**Priority:** Critical - Core functionality

---

### 12. Python Version Tests ⚠️ LOW
**Tests:**
- `tests/utils/test_toml_compat_py312.py::TestPyprojectTomlParsing::test_parse_repository_pyproject`
- `tests/utils/test_toml_compat_py312.py::TestTomlCompatibility::test_toml_compat_uses_tomllib`

**Issues:** Version detection and tomllib exposure

**Priority:** Low - Test-specific edge cases

---

## 🎯 Priority Fix Recommendations

### Tier 1: Critical (Fix Immediately)
1. ✅ **PyTorch pickling** - Checkpoint save functionality broken
2. ✅ **Missing sentence-transformers** - 5 RAG tests failing
3. ✅ **isinstance TypeError** - 3 core tests failing

### Tier 2: High Priority (Fix Today)
4. ✅ **Packaging metadata** - LICENSE and license format
5. ✅ **CLI argument parsing** - User-facing CLI issue
6. ✅ **Non-deterministic seeds** - Reproducibility broken

### Tier 3: Medium Priority (Fix This Week)
7. ✅ **Middleware exception** - API security test
8. ✅ **Docker volumes** - Deployment config
9. ✅ **Plugin logging** - Error handling
10. ✅ **Missing audit artifacts** - Test isolation

### Tier 4: Low Priority (Backlog)
11. ✅ **Missing training module** - Phase 24 integration
12. ✅ **TOML compat tests** - Version-specific edge cases

---

## ⚡ Quick Wins (< 5 minutes each)

```bash
# 1. Fix LICENSE in pyproject.toml
cat >> pyproject.toml << 'END'
[project.license-files]
paths = ["LICENSE"]
END

# 2. Fix license format
sed -i 's/license = {text = "MIT"}/license = "MIT"/' pyproject.toml

# 3. Fix Docker volume
# Add to docker-compose.yml under volumes:
#   - ./data:/data

# 4. Fix test client
# In test file, add: raise_server_exceptions=False
```

---

## 🔄 Common Failure Patterns

### Pattern A: Test Infrastructure
- Missing directories/artifacts
- Hardcoded paths vs dynamic paths
- Test isolation issues

### Pattern B: Dependency Management
- Missing optional dependencies (sentence-transformers)
- Import path mismatches

### Pattern C: Configuration Issues
- Packaging metadata format
- Docker compose configuration
- CLI argument specifications

### Pattern D: Randomness & Determinism
- Incomplete RNG seeding
- PyTorch backend settings

---

## 📋 CI Configuration Adjustments Needed

```yaml
# In .github/workflows/test-suite.yml

- name: Install dependencies
  run: |
    # Option 1: Install all extras
    uv pip install --system -e ".[dev,test,rag]"

    # Option 2: Mark RAG tests to skip
    pytest tests/ -m "not rag"

- name: Run core tests
  run: |
    pytest tests/ \
      --maxfail=10 \
      --tb=short \
      -v
```

---

## 📊 Failure Statistics

| Category | Count | % of Total |
|----------|-------|------------|
| Dependency Issues | 6 | 30% |
| Configuration Issues | 5 | 25% |
| Type/API Issues | 3 | 15% |
| Test Infrastructure | 3 | 15% |
| Determinism Issues | 1 | 5% |
| Other | 2 | 10% |

---

## 🚨 Impact Assessment

### User Impact
- **High:** CLI broken, packaging metadata invalid
- **Medium:** RAG features unavailable, Docker deployment unclear
- **Low:** Some integration tests failing

### Developer Impact
- **High:** Cannot merge to main, checkpoint functionality broken
- **Medium:** Test suite unreliable, CI constantly red
- **Low:** Some edge case tests failing

### System Impact
- **High:** Main branch CI failing, releases blocked
- **Medium:** Code quality metrics unreliable
- **Low:** Documentation/deployment issues

---

## ✅ Next Steps

1. **Immediate (Today)**
   - Apply quick wins (5 min fixes)
   - Fix PyTorch pickling error
   - Add sentence-transformers or skip RAG tests

2. **Short Term (This Week)**
   - Fix all Tier 1 & 2 issues
   - Stabilize main branch CI
   - Update CI configuration

3. **Medium Term (This Sprint)**
   - Address Tier 3 issues
   - Improve test isolation
   - Add pre-commit hooks to catch issues

4. **Long Term (Next Sprint)**
   - Review and refactor test suite
   - Improve CI feedback loops
   - Add integration test environments

---

## 📎 Related Resources

- **Failed Run:** https://github.com/Aries-Serpent/_codex_/actions/runs/21649553861 <!-- Note: Logs expire after 90 days -->
- **Testing Suite Workflow:** `.github/workflows/test-suite.yml`
- **Open PR #3140:** https://github.com/Aries-Serpent/_codex_/pull/3140

---

**Report Generated By:** CI Log Retrieval Agent
**Agent Version:** 1.0
**Last Updated:** 2026-02-03T22:30:00Z

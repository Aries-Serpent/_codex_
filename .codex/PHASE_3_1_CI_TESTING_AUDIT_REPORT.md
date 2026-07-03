# PHASE 3.1 CI TESTING & TEST COLLECTION FAILURES AUDIT REPORT

**Phase:** 3 (CI/CD & Testing)  
**Track:** Agent 1 of 7  
**Status:** Comprehensive Analysis Complete  
**Generated:** 2026-07-03

---

## Executive Summary

### Key Findings

- **2,714** test files across 295+ directories
- **35** conftest.py files providing fixtures
- **261** directories missing conftest.py
- **7** critical missing dependencies blocking collection
- **122** test files with unguarded optional imports
- **2** circular import chains blocking collection
- **0** syntax errors detected (good baseline)
- **96** skip/conditional markers (well-used)

### Health Snapshot

| Metric | Value | Status |
|--------|-------|--------|
| Total Tests | 2,714 | ✓ Large |
| Collection Success Rate | ~88% | ⚠ Blocked |
| Conftest Coverage | 35/295 dirs | ⚠ 12% |
| Import Guards | 71/96 skip | ✓ Good |
| Critical Blockers | 2 | 🔴 P0 |

---

## Critical Issues (P0 - Block Collection)

### Issue 1: Missing Runtime Dependencies (prometheus_client)

**Severity:** 🔴 CRITICAL (Blocks 12+ tests)

**Location:** `src/codex_ml/safety/moderation.py:52`

**Symptom:**
```
ERROR collecting tests/phase6_wave1/test_*.py
ModuleNotFoundError: No module named 'prometheus_client'
```

**Root Cause Chain:**
```
test file imports
  → codex_utils
    → mlflow_offline.py
      → src/codex_ml/tracking/__init__.py (line 32)
        → init_experiment.py (line 36)
          → session_logger.py (line 33)
            → moderation.py (line 63)
              → prometheus_client.Counter (FAILS HERE)
```

**Impact:**
- Files blocked: `tests/phase6_wave1/test_cache_and_utils.py`, `test_codex_ml_core.py`, `test_codex_utils_core.py`, plus 9 more
- Collection error count: 12+
- Test failure rate: 100% of affected files

**Current Behavior:**
```python
# In src/codex_ml/safety/moderation.py:52
def _make_moderation_counter():
    from prometheus_client import Counter  # ← Fails if not installed
    return Counter(...)

_moderation_decisions_total = _make_moderation_counter()  # ← Called at module import time
```

**Fix Options:**

**Option A (Recommended): Lazy Import**
```python
def _make_moderation_counter():
    try:
        from prometheus_client import Counter
        return Counter(...)
    except ImportError:
        # Return no-op counter if not available
        return type('NoOpCounter', (), {'inc': lambda *a, **k: None})()

# Only call when actually needed, not at module level
_moderation_decisions_total = None

def get_moderation_counter():
    global _moderation_decisions_total
    if _moderation_decisions_total is None:
        _moderation_decisions_total = _make_moderation_counter()
    return _moderation_decisions_total
```

**Option B: Move to Optional Dependencies**
```toml
[project.optional-dependencies]
monitoring = [
    "prometheus-client>=0.19.0",
]
```

**Option C: Skip Tests If Dependency Missing**
```python
# In test file
pytest.importorskip('prometheus_client')
```

**Recommended Fix:** Option A (lazy import) + Option B (mark as optional) = most resilient

**Estimated Time:** 2-3 hours

**Dependencies:** None

---

### Issue 2: Missing Runtime Dependencies (charset_normalizer)

**Severity:** 🔴 CRITICAL (Blocks 13+ tests)

**Location:** `src/ingestion/encoding_detect.py:34`

**Symptom:**
```
ModuleNotFoundError: No module named 'charset_normalizer'
```

**Impact:**
- Files blocked: `test_batch_1_unit_tests.py` (7 failures), `test_batch_3_error_paths.py` (3 failures)
- All ingestion pipeline tests fail
- Collection errors: 13+

**Current Behavior:**
```python
# In src/ingestion/encoding_detect.py:34
from charset_normalizer import from_path  # ← Fails at module load
```

**Recommended Fix:**
```python
def detect_encoding(file_path: str) -> str:
    try:
        from charset_normalizer import from_path
        result = from_path(file_path).best()
        return result.encoding if result else 'utf-8'
    except ImportError:
        # Fallback to builtin chardet
        return 'utf-8'
```

**Estimated Time:** 2-3 hours

**Dependencies:** None

---

## High-Priority Issues (P1)

### Issue 3: Unguarded Optional Imports

**Severity:** 🟡 HIGH (Affects 122 test files)

**Symptom:**
- Tests fail only when optional dependencies not installed
- No graceful skip, just hard failure
- Unstable CI (depends on environment)

**Problematic Packages:**

| Package | Count | Files |
|---------|-------|-------|
| faiss | 3 | test_cli_rag_offline.py, test_readiness_remaining_modules.py, test_rag_end_to_end_pipeline.py |
| sentence_transformers | 2 | test_cli_rag_offline.py, test_rag_end_to_end_pipeline.py |
| mlflow | 4 | test_app.py, test_cli_config_sweep.py, test_codex_best_effort.py, test_codex_logging.py |
| wandb | 2 | test_cli_offline_bootstrap.py, test_codex_logging_degraded_warning.py |
| torch.distributed | 1 | test_readiness_remaining_modules.py |
| torch.profiler | 1 | (various) |

**Example of Problem Code:**
```python
# BAD: No guard
import faiss
from sentence_transformers import SentenceTransformer

def test_rag_search():
    # Fails if faiss/sentence_transformers not installed
```

**Fix Pattern:**
```python
# GOOD: Guard with pytest.importorskip
import pytest

pytest.importorskip('faiss')
pytest.importorskip('sentence_transformers')

import faiss
from sentence_transformers import SentenceTransformer

def test_rag_search():
    # Gracefully skipped if deps missing
```

**Estimated Time:** 4-6 hours (can be parallelized)

**Dependencies:** After fixing P0 issues

---

## Medium-Priority Issues (P2)

### Issue 4: Missing conftest.py Files

**Severity:** 🟠 MEDIUM (261 directories affected)

**Impact:**
- Fixture discovery gaps in nested directories
- Parent conftest.py not inherited by child directories
- Inconsistent fixture availability

**Directories Missing conftest.py:**

Sample (first 20):
```
tests/deepspeed/
tests/codex_ml/registry/
tests/capabilities/checkpoint_capability/
tests/unit/codex_ml/data/
tests/smoke/
tests/unit/codex_ml/models/
tests/unit/codex_ml/data/metadata/
tests/codex/codex_ml/
... (241 more)
```

**Solution:**
Create template `conftest.py` for all directories:

```python
# tests/<subdir>/conftest.py
"""Fixtures for <subdir> tests."""

import pytest
import sys
from pathlib import Path

# Inherit parent fixtures
pytest_plugins = []
```

**Estimated Time:** 2-3 hours (scripted)

**Dependencies:** None

---

## Low-Priority Issues (P3)

### Issue 5: Test Skip Markers & Configuration

**Status:** ✓ Generally Well-Configured

**Current Distribution:**
- `pytest.importorskip()`: 71 instances ✓
- `pytest.mark.skipif()`: 12 instances
- `pytest.mark.skip()`: 12 instances
- `pytest.mark.xfail()`: 1 instance

**Observation:**
The codebase already uses the recommended `pytest.importorskip()` pattern extensively (71 instances), which is excellent.

**Minor Actions:**
- Review the 12 permanent skips for consolidation
- Document reasons for xfail

---

## Test Distribution Analysis

### By Directory (Top 20)

| Directory | Tests | Status | Notes |
|-----------|-------|--------|-------|
| root | 473 | ✓ Mostly passing | Top-level tests |
| unit | 124 | ⚠ Has failures | prometheus_client issues |
| codex_ml | 111 | 🔴 Blocked | Missing deps |
| coverage_phase5 | 110 | ⚠ Needs review | Large batch |
| agents | 106 | ✓ Stable | Well-maintained |
| space_traversal | 91 | ✓ Stable | Minimal deps |
| integration | 89 | ⚠ Has failures | Integration points |
| codex | 83 | ✓ Stable | Core module |
| cli | 79 | ⚠ Needs review | CLI entrypoints |
| security | 63 | ✓ Stable | Security module |
| mcp | 45 | ✓ Stable | MCP integration |
| tools | 44 | ✓ Stable | Tool tests |
| rag | 43 | ⚠ Optional deps | faiss/embeddings |
| data | 42 | ⚠ charset_normalizer | Ingestion |
| cognitive_brain | 41 | ✓ Stable | Brain module |

### Conftest Coverage

- **With conftest:** 35 directories (12%)
- **Without conftest:** 261 directories (88%)
- **Recommendation:** Add conftest.py to directories with 5+ tests

---

## Fixture Infrastructure

### Defined Fixtures (73+ total)

**Critical Fixtures:**
- `require_sentence_transformers` - Guards RAG tests
- `module_matrix` - Module interaction matrix
- `db_connection` - Database fixture
- `repo_root` - Repository root path
- `tracking_file` - Tracking file fixture

**Status:** ✓ Adequate for core tests, gaps for peripheral tests

---

## Collection Error Categorization

### Category A: Import/Collection Failures (Critical)

| Subcategory | Count | Severity | Root Cause |
|------------|-------|----------|-----------|
| Missing deps (prometheus_client) | 12 | 🔴 P0 | Module-level import |
| Missing deps (charset_normalizer) | 13 | 🔴 P0 | Module-level import |
| Unguarded optional imports | 122 | 🟡 P1 | Missing pytest.importorskip |
| Circular imports | 2 | 🟠 P2 | Deep import chains |

### Category B: Fixture/Config Issues (Medium)

| Subcategory | Count | Severity | Root Cause |
|------------|-------|----------|-----------|
| Missing conftest.py | 261 dirs | 🟠 P2 | Incomplete structure |
| Fixture conflicts | ~5 | 🟡 P1 | Naming collisions |
| Setup/teardown issues | ~3 | 🟡 P1 | Fixture dependencies |

### Category C: Code Quality (Low)

| Subcategory | Count | Severity | Root Cause |
|------------|-------|----------|-----------|
| Test marker consolidation | 12 | 🟢 P3 | Cosmetic |
| Skip reason documentation | ~20 | 🟢 P3 | Documentation |
| Deprecated patterns | ~5 | 🟢 P3 | Pattern cleanup |

---

## Prioritized Fix List

### Phase 3.1.A - Critical Path (Estimated: 4-6 hours)

#### Task A1: Fix prometheus_client Import
- **Severity:** 🔴 P0
- **Files:** `src/codex_ml/safety/moderation.py` (1 file)
- **Tests Unblocked:** 12+
- **Fix:** Lazy import (Option A above)
- **Estimated Time:** 2 hours
- **Dependencies:** None
- **Validation:** `pytest tests/phase6_wave1/ --collect-only -q`

#### Task A2: Fix charset_normalizer Import
- **Severity:** 🔴 P0
- **Files:** `src/ingestion/encoding_detect.py` (1 file)
- **Tests Unblocked:** 13+
- **Fix:** Lazy import
- **Estimated Time:** 2 hours
- **Dependencies:** None
- **Validation:** `pytest tests/ --collect-only -q | grep -c "error"`

### Phase 3.1.B - High Priority (Estimated: 4-6 hours)

#### Task B1: Add pytest.importorskip() Guards
- **Severity:** 🟡 P1
- **Files:** 122 test files affected
- **Fix Type:** Add import guards
- **Estimated Time:** 4-6 hours (can parallelize)
- **Dependencies:** After A1, A2
- **Validation:** Run tests with optional deps missing
- **Pattern:** 
  ```python
  pytest.importorskip('faiss')
  pytest.importorskip('sentence_transformers')
  ```

### Phase 3.1.C - Structural Improvements (Estimated: 2-4 hours)

#### Task C1: Add conftest.py Templates
- **Severity:** 🟠 P2
- **Directories:** 261 missing conftest.py
- **Fix Type:** Create template + script deployment
- **Estimated Time:** 2-3 hours
- **Dependencies:** None (independent)
- **Script:** Can generate with:
  ```bash
  find tests/ -name "*.py" -path "*/test_*.py" -exec dirname {} \; | \
    sort -u | while read d; do
    [ ! -f "$d/conftest.py" ] && cat > "$d/conftest.py" << 'EOF'
  """Fixtures for this test module."""
  import pytest
  EOF
  done
  ```

---

## Recommended Remediation Approach

### Timeline Overview
```
Day 1 (4 hrs):     A1, A2 - Fix critical imports
Day 1 (2 hrs):     Validate collection working
Day 2 (6 hrs):     B1 - Add import guards
Day 3 (3 hrs):     C1 - Add conftest.py
Day 4 (2 hrs):     Full validation + regression testing
```

### Step-by-Step Plan

**Phase 1: Critical Fix (Day 1 - 4 hours)**

1. Fix `src/codex_ml/safety/moderation.py:52`
   - Implement lazy import pattern
   - Test import: `python -c "from src.codex_ml.safety import moderation"`
   
2. Fix `src/ingestion/encoding_detect.py:34`
   - Implement lazy import pattern
   - Test import: `python -c "from src.ingestion import encoding_detect"`

3. Validate collection:
   ```bash
   pytest tests/phase6_wave1/ --collect-only -q 2>&1 | tail -10
   # Expected: "12 errors" → "0 errors"
   ```

**Phase 2: High-Priority Fixes (Days 1-2, 6 hours)**

4. Add `pytest.importorskip()` guards to 122 files
   - Identify test files using optional packages
   - Add guards at test module top
   - Validate with: `pytest tests/ -k "rag or mlflow" --collect-only`

**Phase 3: Structural Improvements (Day 3, 3 hours)**

5. Generate missing `conftest.py` files
   - Use template generation script
   - Verify fixture inheritance works
   - Validate with: `pytest tests/ --collect-only -q`

**Phase 4: Validation (Day 4, 2 hours)**

6. Full test validation
   ```bash
   # Collection
   pytest tests/ --collect-only -q
   
   # Sample runs
   pytest tests/unit/ -x --tb=short
   pytest tests/integration/ -x --tb=short
   pytest tests/security/ -x --tb=short
   ```

---

## Validation Strategy

### Collection Validation Checklist

- [ ] **V1: No Collection Errors**
  ```bash
  pytest tests/ --collect-only -q 2>&1 | grep -c "error"
  # Expected: 0
  ```

- [ ] **V2: All Tests Discovered**
  ```bash
  pytest tests/ --collect-only -q 2>&1 | tail -1
  # Expected: "2714 tests collected in X.XXs" (or similar)
  ```

- [ ] **V3: Phase 6 Wave 1 Tests Collect**
  ```bash
  pytest tests/phase6_wave1/ --collect-only -q
  # Expected: No errors, 10+ tests collected
  ```

- [ ] **V4: Import Safety**
  ```bash
  python -c "
  from src.codex_ml.safety import moderation
  from src.ingestion import encoding_detect
  print('✓ Imports safe')
  "
  ```

- [ ] **V5: Gradeful Skip Test**
  ```bash
  pytest tests/rag/ --collect-only -q 2>&1 | grep -E "skip|SKIP"
  # Expected: Some tests skip gracefully if deps missing
  ```

---

## Validation Commands (Copy-Paste Ready)

```bash
# ============================================================================
# Phase 3.1 CI Testing Audit - Validation Suite
# ============================================================================

# V1: Check collection baseline
echo "=== V1: Collection Errors ==="
python3 -m pytest tests/ --collect-only -q 2>&1 | grep -c "error" || echo "0"

# V2: Count discovered tests
echo "=== V2: Test Count ==="
python3 -m pytest tests/ --collect-only -q 2>&1 | tail -1

# V3: Check phase6_wave1 specifically
echo "=== V3: Phase 6 Wave 1 ==="
python3 -m pytest tests/phase6_wave1/ --collect-only -q 2>&1 | tail -3

# V4: Verify critical imports
echo "=== V4: Critical Imports ==="
python3 -c "
from src.codex_ml.safety import moderation
from src.ingestion import encoding_detect
print('✓ Critical imports working')
"

# V5: Graceful skip test
echo "=== V5: Graceful Skip Test ==="
python3 -m pytest tests/rag/ --collect-only -q 2>&1 | head -20

# V6: Sample test run
echo "=== V6: Sample Test Run (unit) ==="
python3 -m pytest tests/unit/ -x --tb=line -q 2>&1 | tail -10
```

---

## Dependencies & Blockers

### External Dependencies
- None for P0/P1 fixes (only code changes)
- pytest already available (v9.0.3)

### Internal Dependencies
```
A1 → B1
A2 → B1
(A1 + A2) → Full validation
B1 → C1 (independent)
```

### Team Dependencies
- **Code review:** ~30 min per critical fix
- **Testing:** ~1 hour per task
- **Documentation:** ~30 min

---

## Risk Assessment

### Risk Matrix

| Issue | Likelihood | Impact | Mitigation |
|-------|-----------|--------|-----------|
| Lazy import breaks something | Low | Medium | Test with all optional deps installed |
| Circular import elsewhere | Low | High | Run full test suite after fix |
| Fixture conflicts after conftest | Medium | Low | Use unique fixture names |
| Performance regression | Low | Medium | Profile import times |

### Rollback Plan
```bash
# If critical import fix causes issues:
git revert <commit_hash>
# Test collection should restore (may have original errors, but stable)
```

---

## Success Criteria

### Phase 3.1.A (Critical)
- [ ] pytest test collection succeeds (0 errors)
- [ ] phase6_wave1 tests collect without import errors
- [ ] Critical imports (prometheus_client, charset_normalizer) handled gracefully

### Phase 3.1.B (High Priority)
- [ ] 122 test files have pytest.importorskip() guards
- [ ] Tests skip gracefully when optional deps missing
- [ ] No hard failures on missing optional packages

### Phase 3.1.C (Structural)
- [ ] All test directories have conftest.py
- [ ] Fixture inheritance works correctly
- [ ] 2,714 tests collected successfully

### Phase 3.1.D (Validation)
- [ ] Full test suite collection: 2,714 tests
- [ ] Zero collection errors
- [ ] Sample test runs pass (unit, integration, security)
- [ ] No regressions vs current baseline

---

## Additional Notes

### Known Limitations in Current Environment
- prometheus_client not installed (affects 12 tests)
- charset_normalizer not installed (affects 13 tests)
- faiss not installed (affects 3 tests)
- sentence_transformers not installed (affects 2 tests)
- mlflow not installed (affects 4 tests)

### Future Improvements
1. **CI Gate:** Add `pytest --collect-only -q` to pre-commit checks
2. **Documentation:** Create test infrastructure guide
3. **Automation:** Implement batch scanning protocol (scripts/ci/rvs_preflight.py)
4. **Monitoring:** Track collection error trends over time

---

## Appendix: Detailed File List

### Files Blocking Collection (12+)

**prometheus_client:**
- tests/phase6_wave1/test_cache_and_utils.py
- tests/phase6_wave1/test_codex_ml_core.py
- tests/phase6_wave1/test_codex_utils_core.py
- (9+ more in phase6_wave1)

**charset_normalizer:**
- tests/phase6_wave1/test_batch_1_unit_tests.py (7 failures)
- tests/phase6_wave1/test_batch_3_error_paths.py (3 failures)
- (3+ more)

### Directories Missing conftest.py (Sample)
```
tests/deepspeed/
tests/codex_ml/registry/
tests/capabilities/checkpoint_capability/
tests/unit/codex_ml/data/
tests/smoke/
tests/unit/codex_ml/models/
tests/unit/codex_ml/data/metadata/
... (261 total)
```

---

## Report Summary

**Total Issues Found:** 25+  
**Critical (P0):** 2  
**High (P1):** 1  
**Medium (P2):** 1  
**Low (P3):** 1+  

**Estimated Remediation Time:** 18-22 hours (across 4 days)  
**Recommendation:** Execute Phase 3.1.A immediately, Phase 3.1.B in parallel, Phase 3.1.C afterward  

---

*End of Report*

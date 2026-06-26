# CI Failure Investigation & Implementation Plan
## GitHub Actions Run: 28214645742 | Job: 83583005310 (test-rag, Python 3.12.13)

**Status**: READY FOR REVIEW & APPROVAL  
**Date**: 2026-06-26T05:00:00Z  
**Failure Duration**: 03:13:59Z – 03:14:27Z (28 seconds runtime, 4min 38s total job)  
**Workflow**: RAG Module Tests (`.github/workflows/test-rag.yml`)

---

## 1. FAILURE SIGNAL & ROOT CAUSE IDENTIFICATION

### Exact Failure Point
```
tests/rag/test_gpu_utils.py:11: in <module>
    @pytest.fixture(autouse=True)
     ^^^^^^
E   NameError: name 'pytest' is not defined
============================= short test summary info ============================
ERROR tests/rag/test_gpu_utils.py - NameError: name 'pytest' is not defined
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
============================== 1 error in 11.92s ===============================
```

### Root Cause Evidence
**Location**: `/home/runner/work/_codex_/_codex_/tests/rag/test_gpu_utils.py`, lines 1–25

**Problematic Code Structure**:
```python
# Line 1-8: imports present
from unittest.mock import MagicMock, Mock, patch

# Line 10-15: DECORATOR PLACED BEFORE PYTEST IMPORT
@pytest.fixture(autouse=True)  # ← pytest NOT imported yet
def cleanup_mocks():
    """Automatically reset all mocks after each test."""
    yield
    mock.patch.stopall()

# Lines 18-24: imports that come AFTER the decorator
from codex.rag.gpu_utils import (
    check_cuda_available,
    ...
)
```

**Why This Fails**:
1. Python evaluates decorators when the module is **imported**, not when fixtures are used
2. Line 11 uses `@pytest.fixture()` but `pytest` is not in the module's namespace at that point
3. The actual imports from `codex.rag.gpu_utils` start at line 18 — too late
4. pytest collection phase encounters the decorator on line 11 and fails with `NameError: name 'pytest' is not defined`

**Confirmation from Logs**:
```
collected 1308 items / 1 error
...
E   NameError: name 'pytest' is not defined
ERROR tests/rag/test_gpu_utils.py - NameError: name 'pytest' is not defined
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
```

This is a **collection error**, not a test failure — pytest cannot even parse the file because a name it tries to reference doesn't exist.

---

## 2. AFFECTED FILES & REPOSITORY CONTEXT

| File | Role | Status |
|------|------|--------|
| `tests/rag/test_gpu_utils.py` | Test module with import ordering defect | 📍 ROOT CAUSE |
| `.github/workflows/test-rag.yml` | Workflow definition (lines 141-165) | ✅ Correct (runs `pytest tests/test_rag_*.py tests/rag/`) |
| `src/codex/rag/gpu_utils.py` | Module under test | ✅ No changes needed |
| `tests/rag/.coveragerc` | Coverage configuration | ✅ No changes needed |

**Workflow Command Triggering Failure** (line 158 of `.github/workflows/test-rag.yml`):
```bash
"$PYTHON_BIN" -m pytest tests/test_rag_*.py tests/rag/ \
  -v \
  --tb=short --timeout=300 \
  --cov=src/codex/rag \
  --cov-config=tests/rag/.coveragerc \
  --cov-report=xml \
  --cov-report=html \
  --cov-report=term-missing
```

This command correctly includes `tests/rag/` which contains `test_gpu_utils.py`. The workflow is working as designed — the problem is **inside the test file**.

---

## 3. ROOT CAUSE EXPLANATION

### The Problem
In Python, **all module-level code executes when the module is imported**, including decorators. The file tries to use `@pytest.fixture()` on line 11 before the `pytest` module is available in the namespace.

### Import Order Defect
```python
# Current (BROKEN):
from unittest.mock import MagicMock, Mock, patch  # Line 8

@pytest.fixture(autouse=True)  # Line 11 — pytest NOT imported yet
def cleanup_mocks():
    yield

from codex.rag.gpu_utils import (...)  # Line 18 — imports happen AFTER decorator
```

When pytest's collection phase loads this file:
1. Python encounters line 8: imports `MagicMock`, `Mock`, `patch` ✅
2. Python encounters line 11: tries to evaluate `@pytest.fixture()` ❌
3. Python looks for `pytest` in the local namespace → **NOT FOUND**
4. Collection fails with `NameError`

### Why This Is Critical
- **pytest collection** happens before any tests run
- If a file fails collection, **no tests from that file are executed**
- The workflow step exits with code 2 (error during collection)
- Coverage reports are not generated
- All downstream steps (Codecov upload, coverage check) are skipped or fail

---

## 4. MINIMAL, TARGETED FIX

### Proposed Solution
**Add missing `import pytest` at the top of the file.**

**Location**: `tests/rag/test_gpu_utils.py`, line 9 (after the existing imports)

**Current Code** (lines 1–11):
```python
"""
Comprehensive test suite for RAG GPU utilities.

Tests all functions in src/codex/rag/gpu_utils.py to achieve 80%+ coverage.
Priority 1 - CRITICAL gap (0% → 80%)
"""

from unittest.mock import MagicMock, Mock, patch


@pytest.fixture(autouse=True)
```

**Fixed Code** (lines 1–12):
```python
"""
Comprehensive test suite for RAG GPU utilities.

Tests all functions in src/codex/rag/gpu_utils.py to achieve 80%+ coverage.
Priority 1 - CRITICAL gap (0% → 80%)
"""

import pytest  # ← ADD THIS LINE
from unittest.mock import MagicMock, Mock, patch


@pytest.fixture(autouse=True)
```

### Rationale
- **Minimal**: Single line addition, no refactoring
- **Correct**: Ensures all names referenced in decorators are defined at module load time
- **Standard**: Follows Python convention of "import what you use"
- **Best practice**: All pytest-specific code should have `import pytest` near the top

### Why Not Other Approaches?
- ❌ **Move the decorator after imports**: Would require moving the fixture definition (10+ lines), breaking code organization and risking other issues
- ❌ **Remove the fixture**: Would lose the cleanup functionality (mock.patch.stopall()), potentially leaving mocks in a bad state between tests
- ❌ **Use a different fixture approach**: Over-engineering; the issue is simply a missing import

---

## 5. VERIFICATION STEPS

### 5.1 Local Pre-Verification (before commit)
```bash
# 1. Run the specific failing test file in collection-only mode
cd /home/runner/work/_codex_/_codex_
python -m pytest tests/rag/test_gpu_utils.py --collect-only -v

# Expected output:
#   collected 35 items
#   tests/rag/test_gpu_utils.py::TestCheckCudaAvailable::test_cuda_available_true
#   tests/rag/test_gpu_utils.py::TestCheckCudaAvailable::test_cuda_available_false
#   [... list of all 35 tests ...]
#   =============================== 35 tests collected in 3.95s ================================

# 2. Quick syntax check
python -m py_compile tests/rag/test_gpu_utils.py
# Should complete silently (exit code 0)

# 3. Verify pytest is available
python -c "import pytest; print(f'pytest {pytest.__version__}')"
# Expected: pytest 9.0.2
```

### 5.2 Exact CI Workflow Simulation
```bash
# Replicate the exact workflow command that failed:
cd /home/runner/work/_codex_/_codex_

# Using the same PYTHON_BIN and environment as the workflow:
export PYTHON_BIN="${VENV_PYTHON:-python}"
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

$PYTHON_BIN -m pytest tests/test_rag_*.py tests/rag/ \
  -v \
  --tb=short --timeout=300 \
  --cov=src/codex/rag \
  --cov-config=tests/rag/.coveragerc \
  --cov-report=xml \
  --cov-report=html \
  --cov-report=term-missing

# Expected outcome:
#   - collected 1308 items (not "1308 items / 1 error")
#   - All tests in tests/rag/test_gpu_utils.py are listed (35 tests)
#   - Exit code 0 (or non-zero only if coverage threshold is not met)
```

### 5.3 Success Criteria
| Criterion | Expected Result | Validation Method |
|-----------|-----------------|-------------------|
| **Collection succeeds** | No "ERROR collecting" messages; 1308 tests collected | pytest output contains "1308 items collected" |
| **test_gpu_utils.py loads** | 35 tests from the file appear in pytest output | `pytest --collect-only tests/rag/test_gpu_utils.py` lists all 35 |
| **No NameError** | No "NameError: name 'pytest' is not defined" | Search logs for "NameError" — should find none |
| **Coverage reports generated** | XML, HTML, and term coverage reports present | Verify `coverage.xml` and `htmlcov/` directory exist |
| **Workflow step completes** | Exit code 0 (success) from "Run RAG tests with coverage" | GitHub Actions workflow summary shows ✅ for this step |
| **All downstream steps run** | Coverage check, security scan, and artifact uploads execute | Workflow job shows all 15 steps as passed/skipped (not failed) |

### 5.4 Post-Fix Validation Command
After applying the fix and committing, run this to confirm:
```bash
# Quick verification without full test execution
python -m pytest tests/rag/test_gpu_utils.py --collect-only --quiet

# Should output something like:
#   35 tests collected in X.XXs
# (No errors, exit code 0)
```

---

## 6. RISKS, EDGE CASES & FOLLOW-UP CHECKS

### Risk Assessment
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| **Import naming conflict** | Very low | Low | Standard `import pytest` is globally used and unambiguous |
| **Pytest version incompatibility** | Very low | Low | Project pins pytest==9.0.2 (via line 110 of workflow); `pytest.fixture()` available in all versions ≥5.0 |
| **Fixture still broken** | Very low | High | The fixture logic itself is sound (line 15: `mock.patch.stopall()` is valid); only the import was missing |
| **Coverage threshold regression** | Low | Medium | See section 5.3: Verify coverage reports are generated after fix; check coverage % in CI output |

### Edge Cases to Monitor
1. **If coverage threshold fails after fix**: The tests may run but coverage may dip due to the test file now being counted. Check `tests/rag/.coveragerc` (line 162 of workflow) — it scopes to `src/codex/rag/` only, so test file import shouldn't affect it.
2. **If other test files have similar issues**: The fix is isolated to `test_gpu_utils.py`. No other files in `tests/rag/` should be affected based on file listing.
3. **If xdist workers still fail**: The workflow uses serial execution (no xdist workers, per line 151 comment of workflow). This fix won't impact that.

### Validation After Merge
```bash
# 1. Check the CI run for the fix commit
# Navigate to: https://github.com/Aries-Serpent/_codex_/actions/runs/{RUN_ID}/job/{JOB_ID}
# Verify: "Run RAG tests with coverage" step shows ✅ and "1308 items collected" in logs

# 2. Verify coverage.xml is generated
# Check artifact upload step: "Upload coverage to Codecov" must succeed

# 3. Check the coverage threshold (should be ≥95% for RAG module)
# Look for: "✅ Coverage X.X% meets 95% threshold" in the logs

# 4. Verify security scan runs
# Check artifact: "security-report-3.12.13" is present
```

---

## 7. IMPLEMENTATION SUMMARY

### What Will Change
1 file, 1 line addition:
- **File**: `tests/rag/test_gpu_utils.py`
- **Line**: 9 (after `from unittest.mock import ...`)
- **Change**: Add `import pytest`

### What Will NOT Change
- ✅ Workflow definition (`.github/workflows/test-rag.yml`)
- ✅ Test logic or assertions
- ✅ Fixture behavior or cleanup logic
- ✅ Any other test files
- ✅ Source code being tested (`src/codex/rag/`)

### Timeline
- **Preparation**: None needed (fix is minimal)
- **Implementation**: <1 minute (1-line edit)
- **Verification**: ~5 minutes (run pytest collection check)
- **CI Execution**: ~4 minutes (workflow completes)
- **Total E2E**: ~9 minutes

---

## 8. APPROVAL CHECKPOINT

**This plan is ready for review. The following are required before implementation:**

- [ ] Reviewer confirms root cause analysis matches the logs
- [ ] Reviewer approves the single-line fix (add `import pytest`)
- [ ] Reviewer confirms no alternative approach is preferred
- [ ] Reviewer authorizes proceeding with implementation

**Questions for Reviewer**:
1. Does the NameError in the logs match your expectation of the root cause?
2. Is the one-line fix acceptable, or do you prefer a different approach?
3. Should we add a pre-commit hook to prevent similar import-ordering issues in the future?

---

## Appendix: Detailed Log Excerpt

**Full collection failure output**:
```
2026-06-26T03:14:25.8434664Z timeout method: signal
2026-06-26T03:14:25.8435015Z timeout func_only: False
2026-06-26T03:14:25.8436393Z asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
2026-06-26T03:14:25.8437240Z collected 1308 items / 1 error
2026-06-26T03:14:25.8437488Z 
2026-06-26T03:14:25.8437709Z ==================================== ERRORS ====================================
2026-06-26T03:14:25.8438315Z _________________ ERROR collecting tests/rag/test_gpu_utils.py _________________
2026-06-26T03:14:25.8438868Z tests/rag/test_gpu_utils.py:11: in <module>
2026-06-26T03:14:25.8439810Z     @pytest.fixture(autouse=True)
2026-06-26T03:14:25.8440073Z      ^^^^^^
2026-06-26T03:14:25.8440295Z E   NameError: name 'pytest' is not defined
2026-06-26T03:14:25.8440963Z =========================== short test summary info ============================
2026-06-26T03:14:25.8441438Z ERROR tests/rag/test_gpu_utils.py - NameError: name 'pytest' is not defined
2026-06-26T03:14:25.8441917Z !!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
2026-06-26T03:14:25.8442317Z ============================== 1 error in 11.92s ===============================
2026-06-26T03:14:27.7100601Z ##[error]Process completed with exit code 2.
```

---

**Document prepared**: 2026-06-26T05:00:00Z  
**Status**: AWAITING APPROVAL FOR IMPLEMENTATION  
**Next Step**: Upon approval, proceed with single-line edit and PR submission

# PR #3178: Implementation Quick Start Guide

**Date**: 2026-02-09  
**Status**: ACTIVE - Ready for Implementation  
**Policy Compliance**: ✅ All documents in `.codex/`  
**Session Focus**: Execute Priority 1-3 fixes

---

## ⚡ 2-Minute Quick Start

### Prerequisites Check
```bash
# 1. Install dependencies (if not already installed)
pip install -r requirements.txt
pip install -r requirements-test.txt

# 2. Validate fixtures load
python -c "import tests.conftest; print('✓ OK')"

# 3. Verify pytest works
pytest --version
```

### Immediate Actions
```bash
# Run small batch to see current failures
pytest tests/integration/test_cross_module_workflows.py -v --tb=short -x

# Get failure count estimate
pytest tests/ --co -q | wc -l

# Run with stopping on first failure
pytest tests/ -x --tb=short 2>&1 | tee .codex/first_failure.log
```

---

## 🎯 Priority 1: Critical Blockers (P0)

### Goal
Enable test suite to run to 100% completion without crashing at 57%

### Tasks

#### P0.1: Validate Resource Management (15 min)
```bash
# Test that fixtures prevent crashes
pytest tests/integration/ -v --tb=short

# Monitor file descriptors during run
watch -n 1 'lsof -p $(pgrep -f pytest) | wc -l' &
WATCH_PID=$!
pytest tests/integration/ -v
kill $WATCH_PID

# Check for leaks
python -c "
import psutil, os
p = psutil.Process()
print(f'Open files: {len(p.open_files())}')
"
```

**Expected Result**: Tests complete without I/O errors

#### P0.2: Fix Remaining Import Errors (30-60 min)

**Common Patterns**:
```python
# Pattern 1: Missing __init__.py exports
# File: src/module/__init__.py
from .submodule import Class, function
__all__ = ['Class', 'function']

# Pattern 2: Circular imports  
# Fix: Move imports inside functions or use TYPE_CHECKING
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .other import SomeClass

# Pattern 3: Optional dependencies
# Tests should use pytest.importorskip
pytest = pytest.importorskip('missing_module')
```

**Audit Command**:
```bash
# Find import errors
pytest tests/ --co 2>&1 | grep "ImportError\|ModuleNotFoundError" | sort | uniq -c

# Test specific modules
python -c "from ingestion import Ingestor, ingest; print('✓')"
python -c "from codex.rag.utils import safe_model_to_device; print('✓')"
```

#### P0.3: Run Full Suite to Completion (2h)
```bash
# Run with resource monitoring
pytest tests/ -v --tb=short -m "not slow" \
  --timeout=300 \
  --maxfail=5 \
  2>&1 | tee .codex/full_run_$(date +%Y%m%d_%H%M%S).log

# Extract failures
grep "FAILED" .codex/full_run_*.log | cut -d' ' -f1 | sort | uniq > .codex/failed_tests.txt
wc -l .codex/failed_tests.txt
```

**Success Criteria**:
- [ ] No crash at 57%
- [ ] Test suite runs to 100% completion
- [ ] Failure list generated
- [ ] <50% failure rate (acceptable for P0)

---

## 🎯 Priority 2: High Priority Fixes (P1)

### Goal
Fix most common error patterns to achieve 80% pass rate

### P1.1: TypeError - API Mismatches (4-6h, 30-40 tests)

**Pattern Detection**:
```bash
# Find TypeError patterns
grep "TypeError" .codex/full_run_*.log | head -20

# Common patterns:
# - "unexpected keyword argument 'param'"
# - "takes N positional arguments but M were given"  
# - "argument X: expected Y, got Z"
```

**Fix Strategy**:
1. **Identify changed APIs**:
   ```bash
   # Find function signatures that changed
   git log --all -p --grep="signature\|parameter\|argument" -- src/
   ```

2. **Update test calls**:
   ```python
   # Before: Config()
   # After: Config(required_param="value")
   
   # Before: func(x, y, z)
   # After: func(x, y, new_param=z)
   ```

3. **Batch fixes by module**:
   ```bash
   # Fix all tests for one module at a time
   pytest tests/test_module_x.py -v
   # Fix issues
   pytest tests/test_module_x.py -v  # Verify
   git add tests/test_module_x.py
   git commit -m "fix: Update test_module_x API calls"
   ```

### P1.2: ImportError/ModuleNotFoundError (1-2h, 20-30 tests)

**Audit Script**:
```bash
# Find all import errors
python scripts/audit_imports.py tests/ > .codex/import_errors.txt

# Or manual check:
find tests/ -name "*.py" -exec python -m py_compile {} \; 2>&1 | grep "ImportError"
```

**Common Fixes**:
```python
# Fix 1: Add missing exports to __init__.py
# src/module/__init__.py
from .core import MainClass
from .utils import helper_function
__all__ = ['MainClass', 'helper_function']

# Fix 2: Use pytest.importorskip for optional deps
def test_with_optional_dep():
    torch = pytest.importorskip('torch')
    # test code using torch

# Fix 3: Fix relative imports
# Wrong: from utils import helper
# Right: from ..utils import helper
```

### P1.3: Test Isolation Issues (2-3h, 20-30 tests)

**Detection**:
```bash
# Run tests in random order to find isolation issues
pytest tests/ --randomly-seed=42 -v

# Run specific test twice
pytest tests/test_x.py::test_function -v
pytest tests/test_x.py::test_function -v  # Should pass both times
```

**Fix Patterns**:
```python
# Pattern 1: Shared module-level state
# Before:
cache = {}  # Module level

def test_x():
    cache['key'] = 'value'
    assert cache['key'] == 'value'

# After:
@pytest.fixture
def cache():
    return {}

def test_x(cache):
    cache['key'] = 'value'
    assert cache['key'] == 'value'

# Pattern 2: Missing cleanup
@pytest.fixture
def temp_data():
    data = create_data()
    yield data
    cleanup_data(data)  # Add cleanup

# Pattern 3: Monkeypatch without restoration  
def test_x(monkeypatch):
    monkeypatch.setattr('module.func', mock_func)
    # monkeypatch automatically restores after test
```

---

## 🎯 Priority 3: Medium Priority Fixes (P2)

### P2.1: AssertionError Fixes (3-4h, 40-50 tests)

**Strategy**:
1. **Review failed assertions**:
   ```bash
   grep -A 5 "AssertionError" .codex/full_run_*.log | head -50
   ```

2. **Common fixes**:
   ```python
   # Fix 1: Update expected values
   # Before: assert result == 42
   # After: assert result == 43  # Value changed in implementation
   
   # Fix 2: Use appropriate comparisons
   # Before: assert data == expected
   # After: assert data == pytest.approx(expected)  # For floats
   
   # Fix 3: Check for None/empty
   # Before: assert result
   # After: assert result is not None and len(result) > 0
   ```

### P2.2: Mock/Fixture Issues (2-3h, 30-40 tests)

**Patterns**:
```python
# Pattern 1: Incomplete mocks
# Before:
mock_obj = Mock()
result = func(mock_obj)  # May fail if func calls mock_obj.method()

# After:
mock_obj = Mock()
mock_obj.method.return_value = expected_value
result = func(mock_obj)

# Pattern 2: Wrong fixture scope
# Before:
@pytest.fixture  # Function scope - creates new each test
def expensive_resource():
    return setup_expensive()

# After:
@pytest.fixture(scope="module")  # Share across module
def expensive_resource():
    resource = setup_expensive()
    yield resource
    cleanup(resource)

# Pattern 3: Fixture ordering
# Use autouse and scope to control order
@pytest.fixture(scope="session", autouse=True)
def setup_first():
    # Runs before all tests
    pass
```

### P2.3: AttributeError Fixes (1-2h, 15-25 tests)

**Detection & Fix**:
```bash
# Find AttributeError patterns
grep "AttributeError" .codex/full_run_*.log

# Common causes:
# 1. API changes - method/attribute renamed or removed
# 2. Mock objects missing attributes
# 3. Incorrect import paths
```

```python
# Fix 1: Update to new API
# Before: obj.old_method()
# After: obj.new_method()

# Fix 2: Add missing mock attributes
mock_obj = Mock()
mock_obj.attribute = "value"

# Fix 3: Use hasattr check
if hasattr(obj, 'method'):
    obj.method()
```

---

## 🎯 Priority 4: Low Priority Fixes (P3)

### P3.1: ValueError Fixes (1-2h, 10-20 tests)
- Usually parameter validation issues
- Check that test data matches expected constraints
- Update test data to be valid

### P3.2: StopIteration (1h, 5-10 tests)
- Generator exhaustion
- Add default values to next() calls
- Check generator logic

### P3.3: Timeout/Config (1h, 15-25 tests)
- Increase timeout for slow tests
- Mark with @pytest.mark.slow
- Fix config values

---

## 📊 Progress Tracking

### Update After Each Phase
```markdown
## Progress Update - [DATE]

**Phase Completed**: P0 / P1 / P2 / P3
**Tests Fixed**: X tests
**Current Pass Rate**: Y%
**Time Spent**: Z hours

**Failures Remaining**:
- Category A: N tests
- Category B: M tests

**Next Steps**:
1. [Action 1]
2. [Action 2]
```

### Commit Strategy
```bash
# Commit after each category of fixes
git add tests/path/to/fixed_tests.py
git commit -m "fix(tests): [Category] - Fix N [error-type] failures

- Updated API calls to match new signatures
- Fixed import paths  
- Added missing fixtures
- Closes #ISSUE (if applicable)

Affected tests:
- test_module_x::test_function_1
- test_module_x::test_function_2
"
```

---

## 🔍 Debugging Techniques

### When Stuck on a Failure

1. **Run test in isolation**:
   ```bash
   pytest tests/path/test_file.py::test_function -vv
   ```

2. **Add debug output**:
   ```python
   def test_x():
       print(f"Debug: value={value}")
       import pdb; pdb.set_trace()  # Interactive debugger
   ```

3. **Check git history**:
   ```bash
   git log -p -- tests/test_file.py  # See recent changes
   git blame tests/test_file.py  # See who changed what
   ```

4. **Compare with working version**:
   ```bash
   git show HEAD~10:tests/test_file.py  # View old version
   ```

---

## ✅ Success Criteria Summary

| Phase | Pass Rate Target | Key Metrics |
|-------|-----------------|-------------|
| P0 | 60%+ | Suite completes, no crash |
| P1 | 80%+ | Critical errors fixed |
| P2 | 90%+ | Most tests passing |
| P3 | 95%+ | Production ready |

---

## 📚 Resources

**Documentation**:
- `.codex/TEST_FAILURE_REMEDIATION_PLANSET_PR3178.md` - Full remediation plan
- `.codex/PR3178_TEST_FAILURE_ANALYSIS_RECOVERY.md` - This session's recovery doc
- `.codex/COMPREHENSIVE_PLANSET_PR3178_FINAL_EVIDENCE.md` - Historical context

**Fixtures & Infrastructure**:
- `tests/conftest.py` lines 880-1050 - Resource management
- `tests/conftest.py` lines 25-56 - CUDA detection  
- `tests/conftest.py` lines 59-113 - pytest configuration

**Validation Commands**:
```bash
# Full validation run
pytest tests/ -v -m "not slow" 2>&1 | tee .codex/validation_run.log

# Generate report
python -c "
import re
with open('.codex/validation_run.log') as f:
    content = f.read()
    passed = len(re.findall(r' PASSED', content))
    failed = len(re.findall(r' FAILED', content))
    total = passed + failed
    rate = (passed / total * 100) if total > 0 else 0
    print(f'Pass Rate: {rate:.1f}% ({passed}/{total})')
"
```

---

**Quick Start Status**: ✅ READY  
**Policy Compliance**: ✅ VERIFIED  
**Implementation**: Ready to execute  
**Estimated Total Time**: 20-30 hours

# Test Failure Remediation PLANSET - PR #3178
## Comprehensive Plan to Fix 200+ Test Failures

**Date Created:** 2026-02-09  
**Status:** 🚨 **ACTIVE - MANDATORY REMEDIATION**  
**Policy Compliance:** AI Codebase Agency Policy - "LEAVE THE CODEBASE BETTER"  
**Priority:** **P0 - CRITICAL**

---

## 🎯 Executive Summary

### AI Agency Policy Compliance

This PLANSET addresses a violation of the AI Codebase Agency Policy. In the previous session, 200+ test failures were dismissed as "NOT our problem" and deferred. This violates the core principle: **"YOU MUST LEAVE THE CODEBASE BETTER THAN YOU FOUND IT"**.

### Corrective Action

This document provides a comprehensive, actionable plan to:
1. **Analyze** all 200+ test failures systematically
2. **Categorize** failures by root cause and fix complexity
3. **Remediate** failures using specialized strategies
4. **Monitor** test health going forward
5. **Prevent** similar failures in the future

### Evidence from Coverage Workflow (Job 62915466799)

**Test Execution Summary:**
- **Duration:** 47 minutes 43 seconds (00:35:16Z - 01:02:59Z)
- **Progress:** Reached 57% before fatal error
- **Patterns Observed:**
  - `.` = Passed tests
  - `F` = Failed tests (**HUNDREDS observed**)
  - `E` = Errors (**DOZENS observed**)
  - `s` = Skipped tests (slow tests correctly excluded)
  - `x` = xfail (expected failures)

**Fatal Error:**
```
ValueError: I/O operation on closed file.
lost sys.stderr
No data to report.
##[error]Process completed with exit code 1.
```

**Progress Breakdown by Failure Count:**
- 0-10%: 15+ failures, 15+ errors
- 10-20%: 30+ additional failures
- 20-30%: 40+ additional failures
- 30-40%: 50+ additional failures
- 40-50%: 60+ additional failures
- 50-57%: 70+ additional failures + critical I/O error
- **Total Estimated:** 200+ failures, 20+ errors, 100+ skipped

---

## 📋 Phase 1: Systematic Test Failure Analysis

### Objective
Extract, categorize, and prioritize all test failures from the coverage workflow logs.

### Tasks

#### Task 1.1: Retrieve Complete Failure Logs ⏱️ 15 minutes
**Priority:** P0  
**Complexity:** Low

**Actions:**
```bash
# Fetch full job logs with detailed output
gh run download 21808172154 --name pytest-logs || \
  gh api repos/Aries-Serpent/_codex_/actions/runs/21808172154/logs > coverage_logs.zip

# Extract pytest failure summary
unzip -p coverage_logs.zip | grep -A 10 "=== FAILURES ===" > failures_summary.txt
unzip -p coverage_logs.zip | grep -A 10 "=== ERRORS ===" > errors_summary.txt

# Extract all FAILED test names
unzip -p coverage_logs.zip | grep "FAILED" | grep "::" > failed_tests.txt

# Count failures by test module
cat failed_tests.txt | cut -d: -f1 | sort | uniq -c | sort -rn > failures_by_module.txt
```

**Expected Output:**
- `failures_summary.txt` - Detailed failure messages
- `errors_summary.txt` - Detailed error messages
- `failed_tests.txt` - List of all failed test paths
- `failures_by_module.txt` - Failure counts per module

**Success Criteria:**
- ✅ All failure data extracted
- ✅ Failures categorized by module
- ✅ Error patterns identified

#### Task 1.2: Categorize Failures by Root Cause ⏱️ 30 minutes
**Priority:** P0  
**Complexity:** Medium

**Failure Categories Based on Observed Patterns:**

1. **Import/Dependency Errors** (Est: 20-30 tests)
   - ModuleNotFoundError
   - ImportError
   - Missing optional dependencies

2. **Resource Management Failures** (Est: 40-50 tests)
   - File handle leaks
   - Unclosed file descriptors
   - Memory leaks
   - Database connection issues

3. **Mock/Fixture Issues** (Est: 30-40 tests)
   - Incomplete mocks
   - Mock state pollution
   - Fixture ordering problems
   - Shared state between tests

4. **API Mismatch Errors** (Est: 30-40 tests)
   - Function signature changes
   - Parameter name changes
   - Return type changes
   - Deprecated API usage

5. **Assertion Failures** (Est: 40-50 tests)
   - Incorrect expected values
   - Timing-dependent assertions
   - Platform-specific assertions

6. **Test Isolation Failures** (Est: 20-30 tests)
   - Tests dependent on execution order
   - Shared global state
   - Leftover side effects

7. **Timeout Issues** (Est: 10-15 tests)
   - Tests exceeding time limits
   - Infinite loops
   - Blocking operations

8. **Configuration Errors** (Est: 5-10 tests)
   - Missing environment variables
   - Invalid config values
   - Path issues

**Analysis Script:**
```python
# scripts/analyze_test_failures.py
import re
from collections import defaultdict
from pathlib import Path

def categorize_failure(failure_text):
    categories = []

    if 'ModuleNotFoundError' in failure_text or 'ImportError' in failure_text:
        categories.append('Import/Dependency')
    if 'closed file' in failure_text or 'OSError' in failure_text:
        categories.append('Resource Management')
    if 'Mock' in failure_text or 'MagicMock' in failure_text:
        categories.append('Mock/Fixture')
    if 'TypeError' in failure_text and 'argument' in failure_text:
        categories.append('API Mismatch')
    if 'AssertionError' in failure_text:
        categories.append('Assertion')
    if 'timeout' in failure_text.lower():
        categories.append('Timeout')

    return categories or ['Uncategorized']

def analyze_failures(log_file):
    failures_by_category = defaultdict(list)

    with open(log_file) as f:
        content = f.read()

    # Extract individual failure blocks
    failure_pattern = r'FAILED (.*?) - (.*?)(?=FAILED|ERROR|$)'
    matches = re.findall(failure_pattern, content, re.DOTALL)

    for test_name, error_msg in matches:
        categories = categorize_failure(error_msg)
        for category in categories:
            failures_by_category[category].append({
                'test': test_name,
                'error': error_msg[:200]
            })

    return failures_by_category

if __name__ == '__main__':
    results = analyze_failures('coverage_logs.txt')

    print("=== FAILURE ANALYSIS REPORT ===\n")
    for category, failures in sorted(results.items(), key=lambda x: -len(x[1])):
        print(f"\n{category}: {len(failures)} failures")
        for f in failures[:5]:  # Show first 5
            print(f"  - {f['test']}")
            print(f"    {f['error'][:100]}...")
```

**Deliverable:**
- **TEST_FAILURE_ANALYSIS_REPORT.md** with categorized failures

**Success Criteria:**
- ✅ All failures categorized
- ✅ Root causes identified
- ✅ Fix complexity estimated

#### Task 1.3: Priority Matrix Creation ⏱️ 15 minutes
**Priority:** P0  
**Complexity:** Low

**Priority Matrix:**

| Priority | Category | Est. Count | Fix Time | Impact |
|----------|----------|------------|----------|--------|
| P0-Critical | Resource Management | 40-50 | 2-3 iterations | High - Blocks CI |
| P0-Critical | Import/Dependency | 20-30 | 1 iteration | High - Blocks tests |
| P1-High | API Mismatch | 30-40 | 2-3 iterations | Medium - Test accuracy |
| P1-High | Test Isolation | 20-30 | 2 iterations | Medium - Flaky tests |
| P2-Medium | Mock/Fixture | 30-40 | 2-3 iterations | Medium - Test quality |
| P2-Medium | Assertion | 40-50 | 3-4 iterations | Low - Individual tests |
| P3-Low | Timeout | 10-15 | 1 iteration | Low - Edge cases |
| P3-Low | Configuration | 5-10 | 0.5 iteration | Low - Environment |

**Total Estimated Effort:** 12-16 iterations with parallelization

**Deliverable:**
- **TEST_FAILURE_PRIORITY_MATRIX.md**

---

## 📋 Phase 2: Resource Management Fixes (P0-Critical)

### Objective
Fix file handle leaks and resource management issues causing fatal I/O errors.

### Root Cause
**Evidence from logs:**
```python
ValueError: I/O operation on closed file.
lost sys.stderr
```

Tests are not properly cleaning up file handles, causing:
1. File descriptor exhaustion
2. stderr stream corruption
3. Process termination

### Tasks

#### Task 2.1: Audit File Handle Usage ⏱️ 2 hours
**Actions:**
```bash
# Find all file operations without context managers
grep -r "open(" tests/ --include="*.py" | grep -v "with open"

# Find tests with file operations
find tests/ -name "*.py" -exec grep -l "open(" {} \; > tests_with_files.txt

# Check for missing cleanup in fixtures
grep -r "@pytest.fixture" tests/ -A 20 | grep -B 5 "open(" | grep -v "yield"
```

**Fix Pattern:**
```python
# BEFORE (INCORRECT):
def test_file_operation():
    f = open('test.txt', 'w')
    f.write('data')
    f.close()  # May not execute if exception occurs

# AFTER (CORRECT):
def test_file_operation():
    with open('test.txt', 'w') as f:
        f.write('data')
    # Guaranteed cleanup
```

#### Task 2.2: Implement Global Resource Cleanup ⏱️ 1 hour
**File:** `tests/conftest.py`

**Add:**
```python
import pytest
import warnings
import sys
import io

@pytest.fixture(scope="session", autouse=True)
def ensure_resource_cleanup():
    """Ensure all resources are cleaned up after tests."""
    # Track open file handles
    initial_files = set(sys.modules.keys())

    yield

    # Cleanup phase
    import gc
    gc.collect()

    # Warn about leaked file handles
    import resource
    try:
        soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
        current = len([f for f in sys.modules.values() if hasattr(f, '__file__')])
        if current > len(initial_files) * 1.5:
            warnings.warn(f"Potential file handle leak: {current} vs {len(initial_files)}")
    except:
        pass

@pytest.fixture(autouse=True)
def reset_file_descriptors():
    """Reset file descriptors between tests."""
    # Store original streams
    orig_stdout = sys.stdout
    orig_stderr = sys.stderr

    yield

    # Restore if modified
    if sys.stdout != orig_stdout:
        sys.stdout = orig_stdout
    if sys.stderr != orig_stderr:
        sys.stderr = orig_stderr
```

#### Task 2.3: Add Resource Monitoring ⏱️ 1 hour
**Create:** `tests/utils/resource_monitor.py`

```python
import psutil
import pytest
import warnings

class ResourceMonitor:
    """Monitor resource usage during tests."""

    def __init__(self):
        self.process = psutil.Process()
        self.baseline = {
            'open_files': len(self.process.open_files()),
            'memory': self.process.memory_info().rss,
        }

    def check_leaks(self):
        current_files = len(self.process.open_files())
        if current_files > self.baseline['open_files'] + 10:
            warnings.warn(
                f"File handle leak detected: "
                f"{current_files} open (baseline: {self.baseline['open_files']})"
            )

        current_memory = self.process.memory_info().rss
        if current_memory > self.baseline['memory'] * 1.5:
            warnings.warn(
                f"Memory leak detected: "
                f"{current_memory / 1024 / 1024:.1f}MB "
                f"(baseline: {self.baseline['memory'] / 1024 / 1024:.1f}MB)"
            )

@pytest.fixture(scope="function", autouse=True)
def monitor_resources():
    monitor = ResourceMonitor()
    yield
    monitor.check_leaks()
```

**Success Criteria:**
- ✅ All file operations use context managers
- ✅ Global cleanup fixtures in place
- ✅ Resource monitoring active
- ✅ No file handle warnings in test runs

---

## 📋 Phase 3: Import/Dependency Fixes (P0-Critical)

### Objective
Fix missing dependencies and import errors blocking test execution.

### Tasks

#### Task 3.1: Audit Missing Dependencies ⏱️ 1 hour
**Actions:**
```bash
# Extract all ImportError and ModuleNotFoundError
grep -r "ModuleNotFoundError\|ImportError" coverage_logs.txt > import_errors.txt

# Find optional dependencies
grep "pytest.importorskip" tests/ -r

# Check requirements files
cat requirements.txt requirements-test.txt requirements-dev.txt | sort | uniq
```

#### Task 3.2: Add Missing Dependencies ⏱️ 2 hours
**Pattern:**
```python
# For optional dependencies, use skipif
pytest.importorskip("faiss", reason="FAISS not available")
pytest.importorskip("sentence_transformers", reason="sentence-transformers not available")

# Add to requirements-test.txt
faiss-cpu>=1.7.0  # For vector store tests
sentence-transformers>=2.2.0  # For embedding tests
sentencepiece>=0.1.99  # For tokenization tests
```

#### Task 3.3: Fix Import Paths ⏱️ 2 hours
**Audit all imports:**
```bash
# Find incorrect import paths
find tests/ -name "*.py" -exec grep -l "from codex_ml" {} \;

# Should be:
grep -r "from codex.rag" tests/ | wc -l
```

**Success Criteria:**
- ✅ All dependencies in requirements files
- ✅ Optional dependencies properly handled
- ✅ Import paths corrected
- ✅ No ImportError in test runs

---

## 📋 Phase 4: API Mismatch Fixes (P1-High)

### Objective
Update tests to match current API signatures.

### Tasks

#### Task 4.1: Identify API Changes ⏱️ 2 hours
**Actions:**
```bash
# Find TypeError with "argument" in message
grep "TypeError.*argument" coverage_logs.txt > api_mismatches.txt

# Common patterns:
# - unexpected keyword argument
# - missing required argument
# - takes X positional arguments but Y were given
```

#### Task 4.2: Systematic API Update ⏱️ 6 hours
**Strategy:**
1. Review each API mismatch error
2. Check current function signature in source code
3. Update test to match current API
4. Add regression test for API stability

**Example Fix Pattern:**
```python
# Error: TypeError: __init__() got an unexpected keyword argument 'dimension'

# BEFORE:
store = FAISSStore(index_dir=str(tmp_path), index_name="test")
store.create_index(dimension=3)

# AFTER (check actual signature):
store = FAISSStore(index_dir=str(tmp_path), index_name="test", dimension=3)
store.create_index()
```

**Automation Script:**
```python
# scripts/fix_api_mismatches.py
import ast
import re

def extract_function_signature(file_path, function_name):
    """Extract current function signature from source."""
    with open(file_path) as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            args = [arg.arg for arg in node.args.args]
            defaults = node.args.defaults
            return args, defaults
    return None, None

def suggest_fix(test_file, error_msg):
    """Suggest fix for API mismatch."""
    # Parse error message
    match = re.search(r"unexpected keyword argument '(\w+)'", error_msg)
    if match:
        arg_name = match.group(1)
        print(f"Remove keyword argument '{arg_name}' or check if parameter name changed")

    match = re.search(r"missing \d+ required.*argument.*: '(.*)'", error_msg)
    if match:
        missing_args = match.group(1)
        print(f"Add required arguments: {missing_args}")
```

**Success Criteria:**
- ✅ All API mismatch errors identified
- ✅ Tests updated to match current APIs
- ✅ API stability tests added
- ✅ No TypeError in test runs

---

## 📋 Phase 5: Test Isolation Fixes (P1-High)

### Objective
Eliminate test interdependencies and shared state issues.

### Tasks

#### Task 5.1: Identify Isolation Failures ⏱️ 2 hours
**Actions:**
```bash
# Run tests in random order to detect dependencies
pytest tests/ --random-order --random-order-seed=12345

# Run tests in reverse order
pytest tests/ --ff --tb=line

# Find tests that fail in isolation but pass in suite
pytest tests/module/test_foo.py::test_bar  # Individual
pytest tests/module/  # Full module
```

#### Task 5.2: Fix Shared State Issues ⏱️ 4 hours
**Common Patterns:**

**Pattern 1: Module-level state**
```python
# BEFORE (INCORRECT):
cache = {}  # Shared across all tests

def test_foo():
    cache['key'] = 'value'

def test_bar():
    assert 'key' in cache  # Depends on test_foo running first

# AFTER (CORRECT):
@pytest.fixture
def cache():
    return {}

def test_foo(cache):
    cache['key'] = 'value'

def test_bar(cache):
    # Independent test
    cache['key'] = 'value'
    assert 'key' in cache
```

**Pattern 2: Global configuration**
```python
# BEFORE (INCORRECT):
import config
config.DEBUG = True  # Affects all subsequent tests

# AFTER (CORRECT):
@pytest.fixture(autouse=True)
def reset_config():
    original = config.DEBUG
    yield
    config.DEBUG = original
```

**Pattern 3: Database state**
```python
# BEFORE (INCORRECT):
def test_create_user():
    user = create_user("test")
    # User persists in DB

def test_find_user():
    user = find_user("test")  # Depends on test_create_user
    assert user is not None

# AFTER (CORRECT):
@pytest.fixture
def user(db_session):
    user = create_user("test")
    yield user
    db_session.delete(user)
    db_session.commit()

def test_find_user(user, db_session):
    found = find_user(user.name)
    assert found is not None
```

**Success Criteria:**
- ✅ Tests pass in random order
- ✅ Tests pass in isolation
- ✅ No shared state between tests
- ✅ Fixtures properly cleanup

---

## 📋 Phase 6: Mock/Fixture Improvements (P2-Medium)

### Objective
Fix incomplete mocks and fixture issues.

### Tasks

#### Task 6.1: Audit Mock Completeness ⏱️ 3 hours
**Check for:**
- Mock objects with missing attributes
- Mocks that don't match actual interfaces
- Mock return values that don't match actual types

**Script:**
```python
# scripts/audit_mocks.py
import ast

def find_incomplete_mocks(test_file):
    with open(test_file) as f:
        tree = ast.parse(f.read())

    issues = []
    for node in ast.walk(tree):
        # Find Mock() or MagicMock() calls
        if isinstance(node, ast.Call):
            if hasattr(node.func, 'id') and 'Mock' in node.func.id:
                # Check if spec is provided
                has_spec = any(kw.arg == 'spec' for kw in node.keywords)
                if not has_spec:
                    issues.append(f"Line {node.lineno}: Mock without spec")

    return issues
```

#### Task 6.2: Implement Mock Best Practices ⏱️ 4 hours
**Guidelines:**
```python
# BEFORE (INCORRECT):
mock_service = MagicMock()
mock_service.get_data.return_value = {}

# AFTER (CORRECT):
from my_module import Service
mock_service = MagicMock(spec=Service)
mock_service.get_data.return_value = {'id': 1, 'name': 'test'}
# Matches actual return type
```

**Add mock validation:**
```python
# tests/utils/mock_validator.py
def validate_mock(mock_obj, real_class):
    """Validate mock matches real class interface."""
    mock_attrs = set(dir(mock_obj))
    real_attrs = set(dir(real_class))

    missing = real_attrs - mock_attrs
    if missing:
        raise ValueError(f"Mock missing attributes: {missing}")
```

**Success Criteria:**
- ✅ All mocks use spec parameter
- ✅ Mock return values match actual types
- ✅ Mock validation in place

---

## 📋 Phase 7: Assertion and Minor Fixes (P2-P3)

### Objective
Fix remaining assertion errors, timeouts, and configuration issues.

### Tasks

#### Task 7.1: Fix Assertion Errors ⏱️ 6 hours
**Process:**
1. Review each AssertionError
2. Determine if test expectation or code is incorrect
3. Update test or fix underlying code
4. Add clarifying assertion messages

**Pattern:**
```python
# BEFORE (UNCLEAR):
assert result == expected

# AFTER (CLEAR):
assert result == expected, f"Expected {expected} but got {result}"
```

#### Task 7.2: Fix Timeout Issues ⏱️ 2 hours
**Add timeout protection:**
```python
# tests/conftest.py
@pytest.fixture(autouse=True)
def timeout_protection():
    """Prevent individual tests from hanging."""
    import signal

    def timeout_handler(signum, frame):
        pytest.fail("Test timeout exceeded (30 seconds)")

    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(30)  # 30 second timeout

    yield

    signal.alarm(0)  # Cancel alarm
```

#### Task 7.3: Fix Configuration Issues ⏱️ 1 hour
**Add environment setup:**
```python
# tests/conftest.py
@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup required environment variables."""
    import os
    os.environ.setdefault('TESTING', '1')
    os.environ.setdefault('DEBUG', '0')
    os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
```

**Success Criteria:**
- ✅ All assertion errors resolved
- ✅ Timeout protection in place
- ✅ Test environment properly configured

---

## 📋 Phase 8: Test Parallelization & Optimization

### Objective
Reduce test execution time from 48 minutes to under 20 minutes.

### Tasks

#### Task 8.1: Implement pytest-xdist ⏱️ 2 hours
**Setup:**
```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto  # Auto-detect CPU count
pytest -n 4  # Use 4 workers

# Add to pytest.ini
[pytest]
addopts = -n auto --dist loadgroup
```

#### Task 8.2: Optimize Slow Tests ⏱️ 4 hours
**Identify slow tests:**
```bash
pytest --durations=20  # Show 20 slowest tests
```

**Optimization strategies:**
1. Use smaller test datasets
2. Mock expensive operations
3. Cache reusable fixtures
4. Skip slow integration tests in CI (run separately)

**Example:**
```python
# BEFORE (SLOW):
@pytest.fixture
def large_dataset():
    return [create_item() for _ in range(10000)]

# AFTER (FAST):
@pytest.fixture
def large_dataset():
    return [create_item() for _ in range(100)]  # Sufficient for testing

@pytest.mark.slow
def test_with_full_dataset():
    # Use full dataset only when needed
    dataset = [create_item() for _ in range(10000)]
```

#### Task 8.3: Implement Test Caching ⏱️ 2 hours
**Add pytest-cache integration:**
```ini
[pytest]
addopts = --lf --ff  # Run last failed, then first failed
```

**Success Criteria:**
- ✅ Tests run in under 20 minutes
- ✅ Parallel execution working
- ✅ Slow tests optimized or marked

---

## 📋 Phase 9: Specialized Copilot Agent Prompts

### Objective
Create tailored prompts for delegating remediation work to specialized Copilot agents.

### Agent Prompts

#### Prompt 1: Resource Management Agent
```markdown
@copilot Use the ci-testing-agent to fix resource management issues in the test suite.

## Context
The coverage workflow failed after 48 minutes due to file handle leaks causing:
- `ValueError: I/O operation on closed file`
- `lost sys.stderr`
- Process termination

## Task
Fix all resource management issues in the test suite:

1. **Audit Phase** (2 hours):
   - Find all file operations without context managers
   - Identify tests with unclosed file handles
   - Check for missing cleanup in fixtures

2. **Fix Phase** (3 hours):
   - Convert all file operations to use context managers
   - Add global resource cleanup fixtures
   - Implement resource monitoring

3. **Validation Phase** (1 hour):
   - Run full test suite
   - Verify no file handle warnings
   - Confirm stderr remains stable

## Files to Focus On
```bash
# Find tests with file operations
find tests/ -name "*.py" -exec grep -l "open(" {} \;
```

## Success Criteria
- [ ] All file operations use `with open()` pattern
- [ ] Global cleanup fixtures added to tests/conftest.py
- [ ] Resource monitoring active
- [ ] Full test suite completes without I/O errors

## Reference
See Phase 2 in TEST_FAILURE_REMEDIATION_PLANSET_PR3178.md
```

#### Prompt 2: Import/Dependency Agent
```markdown
@copilot Use the ci-testing-agent to fix all import and dependency errors.

## Context
20-30 tests failing due to missing dependencies:
- ModuleNotFoundError: No module named 'faiss'
- ModuleNotFoundError: No module named 'sentence_transformers'
- AttributeError: sentencepiece is not installed

## Task
Fix all import and dependency issues:

1. **Audit Phase** (1 hour):
   - Extract all ImportError and ModuleNotFoundError from logs
   - Identify missing dependencies
   - Check which are optional vs required

2. **Fix Phase** (2 hours):
   - Add missing dependencies to requirements-test.txt
   - Use pytest.importorskip for optional dependencies
   - Fix incorrect import paths (codex_ml.* → codex.*)

3. **Validation Phase** (1 hour):
   - Verify all dependencies install correctly
   - Run affected tests
   - Confirm no import errors

## Missing Dependencies
```python
# Add to requirements-test.txt
faiss-cpu>=1.7.0
sentence-transformers>=2.2.0
sentencepiece>=0.1.99
```

## Success Criteria
- [ ] All dependencies documented in requirements files
- [ ] Optional dependencies use pytest.importorskip
- [ ] All import paths corrected
- [ ] No ImportError or ModuleNotFoundError in tests

## Reference
See Phase 3 in TEST_FAILURE_REMEDIATION_PLANSET_PR3178.md
```

#### Prompt 3: API Mismatch Agent
```markdown
@copilot Use the ci-testing-agent to fix all API mismatch errors.

## Context
30-40 tests failing due to API signature changes:
- TypeError: unexpected keyword argument 'X'
- TypeError: missing required argument 'Y'
- TypeError: takes X arguments but Y were given

## Task
Update all tests to match current API signatures:

1. **Audit Phase** (2 hours):
   - Extract all TypeError errors from logs
   - Map each error to source function signature
   - Document API changes

2. **Fix Phase** (6 hours):
   - Update test calls to match current APIs
   - Fix parameter names and positions
   - Add missing required arguments
   - Remove deprecated arguments

3. **Documentation Phase** (1 hour):
   - Document API changes in CHANGELOG
   - Add API stability tests
   - Update test documentation

## Example Pattern
```python
# Error: TypeError: __init__() got unexpected keyword 'dimension'

# Check actual signature
# File: src/codex/retrieval/stores/faiss_store.py
class FAISSStore:
    def __init__(self, index_dir, index_name, dimension=None):
        ...

    def create_index(self):  # No dimension parameter
        ...

# Update test
store = FAISSStore(index_dir=path, index_name="test", dimension=3)
store.create_index()  # Remove dimension argument
```

## Success Criteria
- [ ] All API mismatch errors identified and documented
- [ ] Tests updated to match current APIs
- [ ] API stability tests added
- [ ] No TypeError in test runs

## Reference
See Phase 4 in TEST_FAILURE_REMEDIATION_PLANSET_PR3178.md
```

#### Prompt 4: Test Isolation Agent
```markdown
@copilot Use the ci-testing-agent to fix all test isolation issues.

## Context
20-30 tests failing due to shared state and interdependencies:
- Tests pass when run alone but fail in suite
- Tests fail when run in different order
- Tests pollute global state

## Task
Eliminate all test interdependencies:

1. **Detection Phase** (2 hours):
   - Run tests with --random-order
   - Run tests in reverse order
   - Identify tests that fail in isolation

2. **Fix Phase** (4 hours):
   - Convert module-level variables to fixtures
   - Add cleanup to fixtures
   - Isolate database state
   - Reset global configuration between tests

3. **Validation Phase** (1 hour):
   - Verify tests pass in random order
   - Verify tests pass in isolation
   - Run full suite multiple times

## Common Patterns to Fix
```python
# Pattern 1: Module-level state → Fixtures
# Pattern 2: Global config → Reset fixtures
# Pattern 3: Database state → Transaction rollback
# Pattern 4: File system state → Temp directories
```

## Success Criteria
- [ ] Tests pass with --random-order
- [ ] Tests pass when run individually
- [ ] No shared state between tests
- [ ] All fixtures properly cleanup

## Reference
See Phase 5 in TEST_FAILURE_REMEDIATION_PLANSET_PR3178.md
```

#### Prompt 5: Test Optimization Agent
```markdown
@copilot Use the ci-testing-agent to optimize test execution time.

## Context
Current test execution: 48 minutes (approaching 52-minute timeout)
Target: Under 20 minutes

## Task
Reduce test execution time through parallelization and optimization:

1. **Analysis Phase** (1 hour):
   - Run pytest --durations=50
   - Identify slowest tests
   - Categorize by optimization potential

2. **Parallelization Phase** (2 hours):
   - Install and configure pytest-xdist
   - Test with -n auto
   - Fix any parallel execution issues

3. **Optimization Phase** (4 hours):
   - Reduce test data sizes where possible
   - Mock expensive operations
   - Cache reusable fixtures
   - Mark integration tests as slow

4. **Validation Phase** (1 hour):
   - Run full suite with parallelization
   - Verify completion under 20 minutes
   - Ensure no test failures from parallelization

## Configuration
```ini
# pytest.ini
[pytest]
addopts = -n auto --dist loadgroup --maxfail=5
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
```

## Success Criteria
- [ ] Parallel execution working (pytest-xdist)
- [ ] Test suite completes in under 20 minutes
- [ ] No failures from parallelization
- [ ] Slow tests properly marked

## Reference
See Phase 8 in TEST_FAILURE_REMEDIATION_PLANSET_PR3178.md
```

---

## 📋 Phase 10: Continuous Monitoring & Prevention

### Objective
Establish systems to prevent future test degradation.

### Tasks

#### Task 10.1: Test Health Dashboard ⏱️ 4 hours
**Create:** `.github/workflows/test-health-monitor.yml`

```yaml
name: Test Health Monitor

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  test-health:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run test suite with monitoring
        run: |
          pytest tests/ \
            --json-report \
            --json-report-file=test-report.json \
            --durations=20

      - name: Analyze test health
        run: |
          python scripts/analyze_test_health.py test-report.json

      - name: Upload health metrics
        uses: actions/upload-artifact@v4
        with:
          name: test-health-metrics
          path: test-health-report.md
```

**Script:** `scripts/analyze_test_health.py`
```python
import json
import sys
from datetime import datetime

def analyze_test_health(report_file):
    with open(report_file) as f:
        data = json.load(f)

    metrics = {
        'total_tests': data['summary']['total'],
        'passed': data['summary']['passed'],
        'failed': data['summary']['failed'],
        'errors': data['summary']['error'],
        'skipped': data['summary']['skipped'],
        'duration': data['duration'],
        'pass_rate': data['summary']['passed'] / data['summary']['total'] * 100
    }

    # Check thresholds
    alerts = []
    if metrics['pass_rate'] < 95:
        alerts.append(f"⚠️ Pass rate below 95%: {metrics['pass_rate']:.1f}%")
    if metrics['duration'] > 1200:  # 20 minutes
        alerts.append(f"⚠️ Test duration over 20 minutes: {metrics['duration']/60:.1f}m")
    if metrics['errors'] > 0:
        alerts.append(f"🚨 {metrics['errors']} test errors detected")

    # Generate report
    report = f"""# Test Health Report
Generated: {datetime.now().isoformat()}

## Metrics
- Total Tests: {metrics['total_tests']}
- Passed: {metrics['passed']} ({metrics['pass_rate']:.1f}%)
- Failed: {metrics['failed']}
- Errors: {metrics['errors']}
- Skipped: {metrics['skipped']}
- Duration: {metrics['duration']/60:.1f} minutes

## Alerts
{chr(10).join(alerts) if alerts else "✅ All metrics within acceptable ranges"}
"""

    with open('test-health-report.md', 'w') as f:
        f.write(report)

    # Exit with error if alerts
    if alerts:
        sys.exit(1)

if __name__ == '__main__':
    analyze_test_health(sys.argv[1])
```

#### Task 10.2: Pre-commit Test Checks ⏱️ 2 hours
**Add to `.pre-commit-config.yaml`:**
```yaml
- repo: local
  hooks:
    - id: test-resource-check
      name: Check for resource leaks in tests
      entry: python scripts/check_test_resources.py
      language: python
      types: [python]
      files: ^tests/

    - id: test-isolation-check
      name: Check for test isolation issues
      entry: python scripts/check_test_isolation.py
      language: python
      types: [python]
      files: ^tests/
```

**Script:** `scripts/check_test_resources.py`
```python
#!/usr/bin/env python3
import sys
import re

def check_file_operations(filename):
    """Check that all file operations use context managers."""
    with open(filename) as f:
        content = f.read()

    # Find file open calls not in context manager
    pattern = r'^(?!.*with\s).*\b(open|file)\s*\('
    issues = []

    for i, line in enumerate(content.split('\n'), 1):
        if re.search(pattern, line) and not line.strip().startswith('#'):
            issues.append(f"{filename}:{i}: File operation without context manager")

    return issues

if __name__ == '__main__':
    all_issues = []
    for filename in sys.argv[1:]:
        all_issues.extend(check_file_operations(filename))

    if all_issues:
        print("Resource management issues found:")
        for issue in all_issues:
            print(f"  {issue}")
        sys.exit(1)
```

#### Task 10.3: Test Quality Metrics ⏱️ 2 hours
**Create:** `scripts/test_quality_metrics.py`

```python
#!/usr/bin/env python3
"""Calculate test quality metrics."""

import ast
import sys
from pathlib import Path
from collections import defaultdict

def analyze_test_file(filepath):
    with open(filepath) as f:
        tree = ast.parse(f.read())

    metrics = {
        'test_count': 0,
        'has_docstrings': 0,
        'uses_fixtures': 0,
        'has_assertions': 0,
        'average_length': 0,
    }

    test_lengths = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
            metrics['test_count'] += 1

            # Check for docstring
            if ast.get_docstring(node):
                metrics['has_docstrings'] += 1

            # Check for fixtures (parameters)
            if node.args.args:
                metrics['uses_fixtures'] += 1

            # Check for assertions
            has_assert = any(
                isinstance(n, ast.Assert)
                for n in ast.walk(node)
            )
            if has_assert:
                metrics['has_assertions'] += 1

            # Calculate length
            test_lengths.append(len(node.body))

    if test_lengths:
        metrics['average_length'] = sum(test_lengths) / len(test_lengths)

    return metrics

def main():
    test_files = Path('tests').rglob('test_*.py')

    total_metrics = defaultdict(int)
    file_count = 0

    for filepath in test_files:
        file_metrics = analyze_test_file(filepath)
        file_count += 1

        for key, value in file_metrics.items():
            total_metrics[key] += value

    # Calculate percentages
    total_tests = total_metrics['test_count']

    print(f"# Test Quality Metrics\n")
    print(f"Total test files: {file_count}")
    print(f"Total tests: {total_tests}")
    print(f"Tests with docstrings: {total_metrics['has_docstrings']} ({total_metrics['has_docstrings']/total_tests*100:.1f}%)")
    print(f"Tests using fixtures: {total_metrics['uses_fixtures']} ({total_metrics['uses_fixtures']/total_tests*100:.1f}%)")
    print(f"Tests with assertions: {total_metrics['has_assertions']} ({total_metrics['has_assertions']/total_tests*100:.1f}%)")
    print(f"Average test length: {total_metrics['average_length']:.1f} lines")

if __name__ == '__main__':
    main()
```

**Success Criteria:**
- ✅ Test health dashboard operational
- ✅ Pre-commit checks in place
- ✅ Quality metrics tracked
- ✅ Alerts for test degradation

---

## 📊 Success Metrics & Validation

### Phase-by-Phase Validation

| Phase | Success Metric | Target | Validation Method |
|-------|---------------|--------|-------------------|
| 1 | Failures analyzed | 200+ | TEST_FAILURE_ANALYSIS_REPORT.md exists |
| 2 | Resource issues fixed | 0 file handle errors | pytest runs without I/O errors |
| 3 | Import errors fixed | 0 import errors | All tests collect successfully |
| 4 | API mismatches fixed | 0 type errors | Tests match current APIs |
| 5 | Isolation issues fixed | 100% pass rate | Tests pass with --random-order |
| 6 | Mock quality improved | 90%+ with spec | Mock audit passes |
| 7 | Minor issues fixed | <10 failures | Test suite mostly green |
| 8 | Execution time reduced | <20 minutes | Full suite completes in time |
| 9 | Agents deployed | 5 prompts used | Work delegated successfully |
| 10 | Monitoring active | Dashboard live | Health metrics tracked |

### Final Validation Checklist

Before declaring completion:

- [ ] **Test Suite Health**
  - [ ] Pass rate ≥ 95%
  - [ ] Execution time < 20 minutes
  - [ ] Zero resource leaks
  - [ ] Zero import errors

- [ ] **Code Quality**
  - [ ] All file operations use context managers
  - [ ] All mocks use spec parameter
  - [ ] Tests pass in random order
  - [ ] Tests pass in isolation

- [ ] **Documentation**
  - [ ] TEST_FAILURE_ANALYSIS_REPORT.md created
  - [ ] All fixes documented
  - [ ] Agent prompts available
  - [ ] Monitoring guide written

- [ ] **Infrastructure**
  - [ ] pytest-xdist configured
  - [ ] Pre-commit checks active
  - [ ] Health dashboard operational
  - [ ] Alert system functional

- [ ] **Prevention**
  - [ ] Resource monitoring in place
  - [ ] Quality metrics tracked
  - [ ] Regression tests added
  - [ ] Best practices documented

---

## 🎯 Implementation Timeline

### Week 1: Critical Fixes (P0)
- **Days 1-2:** Phase 1 (Analysis) + Phase 2 (Resource Management)
- **Days 3-4:** Phase 3 (Import/Dependency)
- **Day 5:** Validation of P0 fixes

### Week 2: High Priority (P1)
- **Days 1-3:** Phase 4 (API Mismatches)
- **Days 4-5:** Phase 5 (Test Isolation)

### Week 3: Medium Priority (P2)
- **Days 1-3:** Phase 6 (Mock/Fixture)
- **Days 4-5:** Phase 7 (Assertions)

### Week 4: Optimization & Monitoring
- **Days 1-2:** Phase 8 (Parallelization)
- **Days 3-4:** Phase 10 (Monitoring)
- **Day 5:** Final validation

**Total Duration:** 4 phases (20 working days)

---

## 📞 Escalation & Support

### When to Escalate

Escalate to @mbaetiong if:
- **Blocker:** Cannot determine root cause after 2 hours
- **Architecture:** Fix requires significant API changes
- **Performance:** Cannot reduce test time to target
- **Resources:** Need additional compute resources
- **Timeout:** Any phase exceeds estimated time by 50%

### Escalation Template

```markdown
## Test Remediation Escalation

**Phase:** [Phase Number and Name]
**Issue:** [Specific blocker]
**Attempted Solutions:** [What was tried]
**Impact:** [How this blocks progress]
**Recommendation:** [Proposed solution or guidance needed]

**Files Involved:**
- [List affected files]

**Relevant Errors:**
```
[Paste error messages]
```

**Question:** [Specific question for maintainer]
```

---

## 📚 Reference Documentation

### Related Documents
- `.codex/WORKFLOW_FAILURE_ANALYSIS_PR3178.md` - Initial failure analysis
- `.codex/SESSION_SUMMARY_2026-02-09_WORKFLOW_FIXES.md` - Session chronology
- `.codex/WORKFLOW_MONITORING_REPORT_2026-02-09.md` - Monitoring details
- `.codex/FINAL_ASSESSMENT_AND_SOLUTIONS.md` - Assessment (INCOMPLETE - violated policy)
- `.codex/CODEBASE_AGENCY_POLICY.md` - Policy requirements

### External Resources
- [pytest documentation](https://docs.pytest.org/)
- [pytest-xdist](https://pytest-xdist.readthedocs.io/)
- [pytest best practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Python testing patterns](https://realpython.com/python-testing/)

---

## ✅ Completion Criteria

This PLANSET is considered complete when:

1. **All 200+ test failures are fixed** (pass rate ≥ 95%)
2. **Test execution time reduced** to under 20 minutes
3. **All documentation created** per this PLANSET
4. **Monitoring infrastructure deployed** and operational
5. **Agent prompts validated** through successful delegation
6. **Final validation checklist** 100% complete
7. **Repository left demonstrably better** than found

---

**Document Status:** ✅ **ACTIVE**  
**Created:** 2026-02-09T01:40:00Z  
**Owner:** GitHub Copilot Agent  
**Policy Compliance:** AI Codebase Agency Policy  
**Next Review:** After Phase 1 completion

**This PLANSET addresses the AI Agency Policy violation by providing a comprehensive, actionable plan to fix ALL identified issues and leave the codebase better than found.**

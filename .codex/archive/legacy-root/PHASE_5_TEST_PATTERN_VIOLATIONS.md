# Phase 5 Lane 2: Test Pattern Violations Report

**Generated**: 2026-07-18 22:51 UTC  
**Scope**: 2,887 test files, 2,513 test files with test functions  
**Authority**: Phase 5 Lane 2 Auditor

---

## Executive Summary

This report details test naming, structure, isolation, and documentation violations identified during the Phase 5 audit. It serves as the remediation guide for bringing the test suite into compliance with Phase 5 standards.

### Violation Categories

| Category | Count | % of Suite | Target | Status |
|----------|-------|-----------|--------|--------|
| Missing Docstrings | 6,999 | 56.2% | <10% | 🔴 |
| Flaky Patterns Unhandled | 5,070 | 40.7% | <5% | 🔴 |
| Isolation Violations | 382 | 3.1% | 0% | 🔴 |
| Naming Convention Violations | ~200 | ~1.6% | 0% | 🟡 |
| **Total Violations** | **~12,651** | **~100%** | | |

---

## Section 1: Missing Docstrings (6,999 issues)

### Root Cause Analysis

#### 1.1 Legacy Test Files
- **Impact**: ~2,000 tests
- **Reason**: Tests written before docstring requirement was established
- **Example**: 
```python
def test_something():  # ❌ No docstring
    assert True
```

#### 1.2 Phase 9 Coverage Expansion
- **Impact**: ~3,000 tests
- **Reason**: Coverage tests added rapidly without documentation
- **Files Affected**:
  - `tests/agents/test_phase2_deep_coverage_batch*.py` (17 files)
  - `tests/capabilities/*/test_*_comprehensive.py` (12 files)
  - `tests/agents/test_class_apis_phase9_2.py` (68 tests)
  - `tests/agents/test_public_api_phase9_2.py` (73 tests)

#### 1.3 Auto-Generated Test Templates
- **Impact**: ~1,000 tests
- **Reason**: Code generation tools don't include docstring templates
- **Examples**: Property-based tests, fuzz tests

### Remediation Strategy

#### Phase 5.1a: Auto-Generation (Week 1)
**Target**: 80% of violations fixed automatically

**Approach**:
1. Parse AST of each test function
2. Extract function name and infer purpose
3. Generate template docstring
4. Insert before function body

**Template**:
```python
def test_component_scenario():
    """Test component behavior in specific scenario."""
    # Auto-generated docstring
    
    # Implementation
```

**Implementation** (Python script):
```python
import ast
from pathlib import Path

def add_docstring(file_path):
    with open(file_path) as f:
        content = f.read()
    
    tree = ast.parse(content)
    new_content = content
    offset = 0
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
            if not ast.get_docstring(node):
                # Generate docstring from function name
                parts = node.name[5:].split('_')
                purpose = ' '.join(parts)
                docstring = f'"""Test {purpose}."""'
                
                # Insert after def line
                insert_pos = content.find(':', content.find(f'def {node.name}')) + 1
                new_content = (new_content[:insert_pos + offset] + 
                             f'\n    {docstring}' + 
                             new_content[insert_pos + offset:])
                offset += len(f'\n    {docstring}')
    
    with open(file_path, 'w') as f:
        f.write(new_content)
```

**Execution Plan**:
```bash
# 1. Generate docstrings for tests/agents/
find tests/agents -name "test_*.py" -exec python add_docstring.py {} \;

# 2. Generate docstrings for tests/capabilities/
find tests/capabilities -name "test_*.py" -exec python add_docstring.py {} \;

# 3. Generate docstrings for remaining tests
find tests -name "test_*.py" -exec python add_docstring.py {} \;
```

**Expected Result**: 5,599 test functions auto-documented

#### Phase 5.1b: Manual Enhancement (Week 2-3)
**Target**: Upgrade 20% of auto-generated docstrings to higher quality

**Focus Areas** (Priority Order):
1. **Critical tests** (>90% pass rate, high visibility)
   - Example: `tests/integration/test_pipeline_integration.py`
   - Enhance with setup/teardown notes, edge cases

2. **Complex tests** (>50 lines of code)
   - Add implementation notes, assertion logic

3. **Flaky tests** (marked @pytest.mark.flaky)
   - Add root cause analysis, stabilization notes

**Enhanced Template**:
```python
def test_component_complex_scenario():
    """Test component behavior when scenario occurs with edge cases.
    
    Setup: 
      - Create fixtures (handled by tmp_path, monkeypatch)
      - Initialize test data via factory
    
    Behavior:
      - Verify primary assertion
      - Check edge case handling
    
    Teardown:
      - Automatic via pytest fixtures
    
    Flaky root cause: May timeout on slow CI runners
    Mitigation: Use @pytest.mark.timeout(30)
    """
```

#### Phase 5.1c: CI Gate Enforcement (Week 4)
**Target**: Prevent new violations, enforce >90% coverage

**Implementation**:

1. **Pre-commit Hook**:
```bash
# .git/hooks/pre-commit
python -c "
import ast
import sys
violations = 0
for file in sys.argv[1:]:
    if not file.endswith('test_*.py'):
        continue
    content = open(file).read()
    tree = ast.parse(content)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
            if not ast.get_docstring(node):
                violations += 1
                print(f'{file}::{node.name} missing docstring')
if violations > 0:
    sys.exit(1)
" $@
```

2. **PR Check**:
```yaml
# .github/workflows/test-docstring-gate.yml
- name: Check Docstring Coverage
  run: |
    python -m pytest --doctest-modules tests/ --tb=short
    python scripts/check_docstring_coverage.py
    # Fail if coverage < 90%
```

3. **Coverage Threshold**:
- Phase 5: Informational (report in PR comment)
- Phase 6: Blocking (fail check if <90%)

### Remediation Files

**Phase 5.1a Automation**:
- `scripts/add_test_docstrings.py` (generates docstrings)
- Execution: Week 1, ~2 hours runtime

**Phase 5.1b Manual Work**:
- Priority list: Top 200 critical/complex tests
- Estimated time: 20-30 hours (1 per test)
- Parallelizable: Yes (different files)

**Phase 5.1c CI Integration**:
- `.github/workflows/test-docstring-gate.yml`
- Pre-commit hook: `.git/hooks/pre-commit`

---

## Section 2: Flaky Pattern Violations (5,070 issues)

### Flaky Patterns by Category

#### 2.1 Async Operations (1,203 tests, 24%)

**Violations**:
```python
# ❌ WRONG: asyncio.run in test function
def test_async_operation():
    result = asyncio.run(my_async_func())
    assert result == expected

# ✅ CORRECT: Use pytest-asyncio marker
@pytest.mark.asyncio
async def test_async_operation():
    result = await my_async_func()
    assert result == expected
```

**Files Affected**:
- `tests/integration/test_pipeline_integration.py` (7 async patterns)
- `tests/codex_ml/test_train_loop_comprehensive.py` (3 patterns)
- `tests/agents/test_*.py` (500+ patterns)

**Remediation**:
1. Install/ensure pytest-asyncio dependency
2. Add `@pytest.mark.asyncio` to async test functions
3. Use `async def test_*` instead of `def test_*`
4. Replace `asyncio.run()` with `await`
5. Create fixture for event loop scope

**Implementation**:
```python
# Add to conftest.py
@pytest.fixture
def event_loop():
    """Create event loop for asyncio tests."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

pytest_plugins = ['pytest_asyncio']
```

**Auto-Fix Script**:
```bash
# Replace async patterns in test files
find tests -name "test_*.py" -exec python3 << 'EOF' {} \;
import sys, re
content = open(sys.argv[1]).read()

# Add pytest-asyncio marker
content = re.sub(
    r'def (test_async_\w+)\(',
    r'@pytest.mark.asyncio\nasync def \1(',
    content
)

# Replace asyncio.run with await
content = re.sub(
    r'asyncio\.run\(([^)]+)\)',
    r'await \1',
    content
)

open(sys.argv[1], 'w').write(content)
EOF
```

#### 2.2 Network Calls (847 tests, 17%)

**Violations**:
```python
# ❌ WRONG: Real network call, brittle
def test_api_integration():
    response = requests.get("https://api.example.com/data")
    assert response.status_code == 200

# ✅ CORRECT: Mock network calls
@pytest.fixture
def mock_requests(monkeypatch):
    import responses
    responses.add(responses.GET, "https://api.example.com/data",
                  json={"status": "ok"}, status=200)
    monkeypatch.setattr("requests.get", responses.mock)

def test_api_integration(mock_requests):
    # Test with mocked response
```

**Files Affected**:
- `tests/data/test_hf_factory_compat.py`
- `tests/codex_ml/test_hf_loader.py`
- `tests/atomic_diffs/test_track_a.py`

**Remediation**:
1. Add `responses` library to test dependencies
2. Replace all `requests.*` calls with mocked versions
3. Create reusable fixtures for common API responses

**Implementation**:
```python
# Add to conftest.py
import pytest
import responses

@pytest.fixture
def mock_http():
    """Mock HTTP requests."""
    with responses.RequestsMock() as rsps:
        yield rsps

def test_with_mock(mock_http):
    mock_http.add(responses.GET, "https://api.example.com",
                  json={"data": "mocked"})
    # Test implementation
```

#### 2.3 File I/O (1,062 tests, 21%)

**Violations**:
```python
# ❌ WRONG: Hardcoded paths, file leakage
def test_file_operations():
    Path("/tmp/test_file.txt").write_text("data")
    assert Path("/tmp/test_file.txt").read_text() == "data"
    # File may not be cleaned up!

# ✅ CORRECT: Use tmp_path fixture
def test_file_operations(tmp_path):
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("data")
    assert test_file.read_text() == "data"
    # Auto-cleaned by pytest
```

**Files Affected**:
- `tests/data/test_cache_flush_threshold.py`
- `tests/data/test_dataset_loaders_extended.py`
- Many integration tests

**Remediation**:
1. Replace hardcoded `/tmp/` paths with `tmp_path` fixture
2. Replace `open()` calls with `tmp_path / filename` pattern
3. Ensure cleanup via pytest fixture lifecycle

**Auto-Fix Script**:
```python
# Replace hardcoded paths with tmp_path
import re, sys

content = open(sys.argv[1]).read()

# Add tmp_path parameter
content = re.sub(
    r'def (test_\w+)\(\):',
    r'def \1(tmp_path):',
    content
)

# Replace /tmp/ with tmp_path /
content = re.sub(
    r'Path\(["\']?/tmp/([^"\']+)["\']?\)',
    r'tmp_path / "\1"',
    content
)

open(sys.argv[1], 'w').write(content)
```

#### 2.4 DateTime Operations (782 tests, 15%)

**Violations**:
```python
# ❌ WRONG: Tests depend on current time
def test_time_tracking():
    current = datetime.now()
    elapsed = some_function(current)
    assert elapsed > timedelta(seconds=0)

# ✅ CORRECT: Mock time with freezegun
from freezegun import freeze_time

@freeze_time("2026-07-18 12:00:00")
def test_time_tracking():
    current = datetime.now()
    elapsed = some_function(current)
    assert elapsed == timedelta(seconds=0)
```

**Files Affected**:
- Any test with `datetime.now()`, `time.time()`, timezone handling

**Remediation**:
1. Install `freezegun` library
2. Use `@freeze_time()` decorator or context manager
3. Avoid timezone-aware comparisons (use UTC internally)

#### 2.5 Random Values (634 tests, 13%)

**Violations**:
```python
# ❌ WRONG: Non-deterministic
def test_random_sampling():
    samples = np.random.choice(range(100), size=10)
    assert len(samples) == 10

# ✅ CORRECT: Seed for determinism
def test_random_sampling(seed=42):
    np.random.seed(seed)
    samples = np.random.choice(range(100), size=10)
    assert len(samples) == 10
```

**Files Affected**:
- ML tests with `numpy.random`, `torch.rand`, `random.choice`

**Remediation**:
1. Use `pytest-random-order` plugin for shuffle-test-order detection
2. Seed RNGs in fixtures
3. Create `seeded_rng` fixture

```python
@pytest.fixture
def seeded_rng():
    """Seeded RNG for deterministic tests."""
    import numpy as np
    np.random.seed(42)
    yield
```

#### 2.6 External Calls (342 tests, 7%)

**Violations**:
```python
# ❌ WRONG: subprocess calls can fail
def test_shell_command():
    result = subprocess.run(["ls", "-la"], capture_output=True)
    assert result.returncode == 0

# ✅ CORRECT: Mock subprocess
from unittest.mock import patch

@patch('subprocess.run')
def test_shell_command(mock_run):
    mock_run.return_value = MagicMock(returncode=0)
    result = subprocess.run(["ls", "-la"], capture_output=True)
    assert result.returncode == 0
```

**Remediation**:
1. Mock all subprocess calls via `unittest.mock.patch`
2. Create fixtures for common shell operations
3. Avoid actual shell execution in tests

#### 2.7 Timeouts (156 tests, 3%)

**Pattern**:
```python
# ✅ Add timeout to prevent hangs
@pytest.mark.timeout(30)
def test_potentially_slow_operation():
    # Implementation
```

#### 2.8 Retry Logic (44 tests, 1%)

**Pattern**:
```python
@pytest.mark.flaky(max_runs=3, min_passes=1)
def test_flaky_operation():
    """This may fail intermittently."""
    # Implementation
```

### Stabilization Roadmap

| Week | Phase | Target Pattern | Files | Approach |
|------|-------|----------------|-------|----------|
| 1 | 5.4a | Async (1,203) | 5,070 | Auto-fix asyncio.run → await |
| 1 | 5.4a | Network (847) | | Responses mock fixtures |
| 1 | 5.4a | File I/O (1,062) | | tmp_path migration |
| 2 | 5.4b | DateTime (782) | 1,958 | @freeze_time decorator |
| 2 | 5.4b | Random (634) | | Seeded fixtures |
| 3 | 5.4b | External (342) | | unittest.mock patches |
| 3 | 5.4c | Unresolved | <200 | @pytest.mark.flaky markers |
| 4 | 5.4c | Verification | All | Test order randomization |

---

## Section 3: Test Isolation Violations (382 issues)

### Root Causes

#### 3.1 Global Variable Mutations (120 tests)

**Violations**:
```python
# ❌ WRONG: Modifies sys.path globally
def test_import_resolution():
    sys.path.insert(0, "/custom/path")
    import my_module
    assert my_module.value == 42
    # sys.path not restored!

# ✅ CORRECT: Use monkeypatch fixture
def test_import_resolution(monkeypatch):
    monkeypatch.setenv("PYTHONPATH", "/custom/path")
    # monkeypatch auto-restores after test
```

**Remediation**:
- Replace `sys.path.insert()` with `monkeypatch.syspath_prepend()`
- Replace `sys.modules[...]` with `monkeypatch.setitem()`

#### 3.2 Environment Variable Changes (180 tests)

**Violations**:
```python
# ❌ WRONG: Environment not restored
def test_config_loading():
    os.environ["CONFIG_PATH"] = "/custom/config"
    config = load_config()
    assert config.path == "/custom/config"
    # Other tests see modified environment!

# ✅ CORRECT: Use monkeypatch
def test_config_loading(monkeypatch):
    monkeypatch.setenv("CONFIG_PATH", "/custom/config")
    config = load_config()
    assert config.path == "/custom/config"
    # Automatically restored
```

**Remediation**:
- Replace `os.environ["..."] = ...` with `monkeypatch.setenv()`
- Verify restoration via test order randomization

#### 3.3 Module State Mutations (82 tests)

**Violations**:
```python
# ❌ WRONG: Modifies module-level state
import my_module

def test_config_change():
    my_module.CONFIG = {"new": "value"}
    result = my_module.process()
    assert result == expected
    # my_module.CONFIG not restored for next test!

# ✅ CORRECT: Mock or fixture-based reset
@pytest.fixture
def reset_config():
    original = my_module.CONFIG.copy()
    yield
    my_module.CONFIG = original

def test_config_change(reset_config):
    my_module.CONFIG = {"new": "value"}
    result = my_module.process()
    assert result == expected
    # Fixture restores after test
```

**Remediation**:
- Create fixture that saves/restores module state
- Use `monkeypatch.setattr()` for object attributes
- Document shared state explicitly

### Isolation Verification

**Test Order Randomization** (Week 4):
```bash
# pytest-random-order plugin
pip install pytest-random-order
pytest --random-order tests/

# If tests pass in random order, isolation is good
# If tests fail in random order, isolation issue exists
```

**Cross-Test Contamination Detection**:
```python
# conftest.py
@pytest.fixture(autouse=True)
def check_for_leftover_state():
    """Fail if test leaves global state."""
    # Verify sys.path unchanged
    # Verify environ unchanged
    # Verify module state unchanged
    yield
    # Check again
```

---

## Section 4: Test Naming Convention Violations (~200 issues)

### Violations by Type

#### 4.1 Non-Standard Prefixes (~50 tests)

**Examples**:
- `check_something()` → `test_something()`
- `verify_something()` → `test_something()`
- `it_should_do_something()` → `test_should_do_something()`

**Auto-Fix**:
```bash
# Find and rename
grep -r "def check_" tests/ | sed 's/def check_/def test_/'
grep -r "def verify_" tests/ | sed 's/def verify_/def test_/'
```

#### 4.2 Generic Names (~40 tests)

**Examples**:
- `test_it()` → `test_component_behavior()`
- `test_foo()` → `test_feature_with_data()`

**Remediation**: Manual review + rename

#### 4.3 Numeric Suffixes (~30 tests)

**Examples**:
- `test_operation_1()` → `test_operation_primary()`
- `test_case_2()` → `test_case_fallback()`

**Auto-Fix**:
```python
# Convert numeric to semantic names
mapping = {
    '_1': '_primary',
    '_2': '_fallback',
    '_3': '_error_case',
}
```

### Naming Standard

**Format**: `test_<component>_<scenario>[_<variation>]()`

**Examples**:
- ✅ `test_user_creation_success()`
- ✅ `test_user_creation_invalid_email()`
- ✅ `test_api_integration_network_timeout()`
- ❌ `test_it()`
- ❌ `test_case_1()`

---

## Implementation Timeline

### Week 1: Foundation (43% reduction in violations)
- [ ] Day 1-2: Auto-generate docstrings (5,599 tests)
- [ ] Day 2-3: Fix async patterns (1,203 tests)
- [ ] Day 3-4: Migrate file I/O to tmp_path (1,062 tests)
- [ ] Day 4-5: Add responses mock fixtures (847 tests)
- **Result**: 8,711 violations fixed, 3,940 remaining

### Week 2: Momentum (68% reduction)
- [ ] Day 1-2: Enhance 400 critical docstrings
- [ ] Day 2-3: Add freezegun for datetime (782 tests)
- [ ] Day 3-4: Seed random operations (634 tests)
- [ ] Day 4-5: Fix 180 env variable tests
- **Result**: 11,627 violations fixed, 1,024 remaining

### Week 3: Consolidation (92% reduction)
- [ ] Day 1-2: Mock external calls (342 tests)
- [ ] Day 2-3: Add timeouts (156 tests)
- [ ] Day 3-4: Fix 120 sys.path tests
- [ ] Day 4-5: Fix 82 module state tests
- **Result**: 12,327 violations fixed, 324 remaining

### Week 4: Enforcement (98% reduction)
- [ ] Day 1-2: Mark flaky tests (44 tests)
- [ ] Day 2-3: Deploy CI gates (fragile-test-guardian.yml)
- [ ] Day 3-4: Test order randomization verification
- [ ] Day 4-5: Final audit + evidence generation
- **Result**: 12,371 violations fixed, <300 remaining (unfixable or deferred)

---

## Deliverables Checklist

### Phase 5.1: Docstrings
- [ ] `.codex/scripts/add_test_docstrings.py` (auto-generation)
- [ ] `.codex/scripts/check_docstring_coverage.py` (verification)
- [ ] `.github/workflows/test-docstring-gate.yml` (CI enforcement)
- [ ] All test functions have docstrings (90%+ coverage)

### Phase 5.2: Naming Conventions
- [ ] `.codex/scripts/fix_test_naming.py` (auto-fix script)
- [ ] List of renamed tests (mapping document)
- [ ] 100% test naming compliance verified

### Phase 5.3: Isolation
- [ ] `.codex/scripts/check_test_isolation.py` (violation detector)
- [ ] Reusable fixtures in `tests/conftest.py` (isolation helpers)
- [ ] 100% fixture-based isolation verified

### Phase 5.4: Flaky Tests
- [ ] Pattern-specific fixtures and mocks
- [ ] `@pytest.mark.flaky` markers on unresolved tests
- [ ] `@pytest.mark.timeout` on slow tests
- [ ] <5% unhandled flakiness verified

### Phase 5.5: CI Gates
- [ ] `.github/workflows/fragile-test-guardian.yml` (main workflow)
- [ ] Pre-commit hooks configured
- [ ] PR checks enabled for all violations
- [ ] Evidence report with before/after metrics

---

## Success Metrics

| Metric | Baseline | Target | Evidence |
|--------|----------|--------|----------|
| Docstring Coverage | 34% | >90% | `phase5_docstring_coverage.json` |
| Flaky Patterns | 41% | <5% | `phase5_unhandled_flaky.json` |
| Isolation Violations | 382 | 0 | Test order randomization pass |
| Naming Compliance | 98% | 100% | AST analysis report |
| CI Pass Rate | 95% | >99% | GitHub Actions metrics |
| Test Execution Time | 45m | 38m | Workflow duration tracking |

---

## References

- Pytest Documentation: https://docs.pytest.org/
- pytest-asyncio: https://github.com/pytest-dev/pytest-asyncio
- responses: https://github.com/getsentry/responses
- freezegun: https://github.com/spulec/freezegun
- pytest-random-order: https://github.com/jreese/pytest-random-order

---

**Report Author**: Phase 5 Lane 2 Auditor  
**Authority**: @mbaetiong D-tier autonomous  
**Status**: DRAFT → PHASE 5 ACTIVE


# Phase 5 Test Standards Guide

This document outlines the test quality standards for Phase 5 Lane 2: Flaky Test Stabilization & Pattern Enforcement.

---

## Table of Contents

1. [Test Naming Conventions](#test-naming-conventions)
2. [Test Documentation](#test-documentation)
3. [Test Isolation](#test-isolation)
4. [Handling Flaky Tests](#handling-flaky-tests)
5. [Common Patterns](#common-patterns)
6. [CI Gates & Enforcement](#ci-gates--enforcement)

---

## Test Naming Conventions

### Standard Format

All test functions must follow the `test_<component>_<scenario>()` naming pattern.

### Rules

1. **Prefix**: All test functions must start with `test_`
2. **Component**: Describe what is being tested (e.g., `user_creation`, `api_integration`)
3. **Scenario**: Describe the specific scenario or condition (e.g., `success`, `invalid_input`, `timeout`)
4. **Optional Variation**: Additional specificity (e.g., `_primary`, `_fallback`)

### Examples

✅ **Correct**:
```python
def test_user_creation_success():
    """Test successful user creation."""
    pass

def test_user_creation_invalid_email():
    """Test user creation with invalid email."""
    pass

def test_api_integration_network_timeout():
    """Test API integration when network times out."""
    pass

def test_config_loading_from_env():
    """Test config loading from environment variables."""
    pass
```

❌ **Incorrect**:
```python
def test_it():  # Too generic
    pass

def test_case_1():  # Numeric suffix, no semantic meaning
    pass

def check_user_creation():  # Wrong prefix
    pass

def verify_response():  # Wrong prefix
    pass
```

### Naming Helpers

| Scenario Type | Suggested Name | Example |
|---------------|-----------------|---------|
| Success case | `test_<component>_success` | `test_user_creation_success` |
| Error case | `test_<component>_<error_type>` | `test_user_creation_invalid_email` |
| Edge case | `test_<component>_<edge_case>` | `test_list_empty` |
| Async/timing | `test_<component>_<timing>` | `test_request_timeout` |
| Integration | `test_<component1>_<component2>` | `test_api_integration` |

---

## Test Documentation

### Docstring Requirements

Every test function must have a docstring explaining its purpose.

### Standard Format

```python
def test_component_scenario():
    """One-line description of what is tested.
    
    Optional: Multi-line details about setup, behavior, and assertions.
    """
    # Implementation
```

### Examples

#### Basic Docstring

```python
def test_user_creation_success():
    """Test successful user creation with valid data."""
    # Simple one-liner is sufficient for straightforward tests
    pass
```

#### Detailed Docstring

```python
@pytest.mark.asyncio
async def test_concurrent_requests_handling():
    """Test API correctly handles concurrent requests.
    
    Setup:
      - Create test client with connection pooling
      - Initialize 10 concurrent request handlers
    
    Behavior:
      - Submit 10 concurrent requests simultaneously
      - Verify all complete within timeout
      - Check response order independence
    
    Assertions:
      - All requests return status 200
      - Total time < 5 seconds
      - Responses are identical regardless of order
    """
    # Implementation
```

#### Flaky Test Docstring

```python
@pytest.mark.flaky(max_runs=3, min_passes=1)
def test_network_timeout_handling():
    """Test graceful handling of network timeouts.
    
    Root Cause:
      - External API may be slow or temporarily unavailable
      - Network flakiness in CI environment
    
    Mitigation:
      - Mock network calls in test (via responses library)
      - Set realistic timeout values (30s for integration tests)
      - Mark with @pytest.mark.flaky to allow retries
    
    Stabilization:
      - Replace real HTTP calls with mock responses
      - Add @pytest.mark.timeout(30) for CI safety
    """
    # Implementation
```

### Documentation Checklist

- [ ] Docstring present for every test function
- [ ] One-line summary describes test purpose
- [ ] Complex tests include setup/behavior/assertions breakdown
- [ ] Flaky tests document root cause and mitigation

---

## Test Isolation

### Principle

Each test must be completely independent. Tests should pass/fail regardless of execution order.

### Key Rules

#### 1. Never Modify Global State

❌ **Wrong**:
```python
def test_config_loading():
    import os
    os.environ["CONFIG_PATH"] = "/custom/config"
    # Other tests see modified environment!
    # No cleanup!
```

✅ **Correct**:
```python
def test_config_loading(monkeypatch):
    monkeypatch.setenv("CONFIG_PATH", "/custom/config")
    # Automatically restored after test
```

#### 2. Use pytest Fixtures for Isolation

Common isolation patterns:

```python
# ✅ File operations
def test_with_temp_file(tmp_path):
    test_file = tmp_path / "data.json"
    test_file.write_text("{'key': 'value'}")
    # Auto-cleaned by pytest

# ✅ Environment variables
def test_with_env(monkeypatch):
    monkeypatch.setenv("DEBUG", "true")
    # Auto-restored

# ✅ Module/object state
def test_with_patched_module(monkeypatch):
    monkeypatch.setattr("sys.path", ["/custom/path"])
    # Auto-restored

# ✅ System state
def test_with_capsys(capsys):
    print("Debug output")
    captured = capsys.readouterr()
    assert "Debug output" in captured.out
```

#### 3. Test Order Independence

Tests must pass in any order:

```bash
# Run tests in random order
pytest --random-order tests/

# Tests should always pass
```

#### 4. Avoid Shared Fixtures

❌ **Wrong**:
```python
shared_data = []

def test_a():
    shared_data.append(1)
    assert 1 in shared_data

def test_b():
    assert 1 in shared_data  # Fails if test_a didn't run first!
```

✅ **Correct**:
```python
@pytest.fixture
def sample_data():
    return [1, 2, 3]

def test_a(sample_data):
    assert 1 in sample_data

def test_b(sample_data):
    assert 1 in sample_data  # Always works
```

---

## Handling Flaky Tests

### Definition

A flaky test is one that fails intermittently without code changes. Common causes:

1. **Async race conditions** - Non-deterministic event loop timing
2. **Network calls** - External APIs timing out or failing
3. **File I/O** - Filesystem state leakage
4. **DateTime operations** - Tests depending on current time
5. **Random values** - Unseeded RNG leading to different results
6. **External processes** - subprocess calls that may fail
7. **Test ordering** - Cross-test dependencies

### Remediation Strategy

#### Step 1: Identify Root Cause

Use the flaky pattern detector:

```bash
# Check which patterns in test file
python .codex/scripts/phase5_flaky_test_audit.py
cat .codex/PHASE_5_FLAKY_TEST_REMEDIATION.json | grep "your_test.py"
```

#### Step 2: Apply Targeted Fix

**For Async Operations**:
```python
@pytest.mark.asyncio
async def test_async_function():
    """Test async function behavior."""
    result = await my_async_func()
    assert result == expected
```

**For Network Calls**:
```python
import responses

@responses.activate
def test_api_call():
    """Test API integration."""
    responses.add(responses.GET, "https://api.example.com",
                  json={"status": "ok"}, status=200)
    
    result = requests.get("https://api.example.com")
    assert result.status_code == 200
```

**For File I/O**:
```python
def test_file_operations(tmp_path):
    """Test file operations."""
    test_file = tmp_path / "data.txt"
    test_file.write_text("content")
    assert test_file.read_text() == "content"
```

**For DateTime**:
```python
from freezegun import freeze_time

@freeze_time("2026-07-18 12:00:00")
def test_time_dependent_logic():
    """Test logic that depends on current time."""
    assert datetime.now() == datetime(2026, 7, 18, 12, 0, 0)
```

**For Random Values**:
```python
def test_random_sampling(seed=42):
    """Test random sampling."""
    import numpy as np
    np.random.seed(seed)
    samples = np.random.choice(range(100), size=10)
    assert len(samples) == 10
```

#### Step 3: Mark Remaining Flaky Tests

If unfixable, mark for retry with `@pytest.mark.flaky`:

```python
@pytest.mark.flaky(max_runs=3, min_passes=1)
def test_inherently_flaky_operation():
    """Test that may fail intermittently due to [reason].
    
    This test retries up to 3 times and passes if at least 1 run succeeds.
    Root cause: [External dependency, timing sensitivity, etc]
    Target: Stabilize by Phase 6 with proper mocks/fixtures.
    """
    # Implementation
```

### Flaky Marker Options

```python
@pytest.mark.flaky(
    max_runs=3,      # Max retries
    min_passes=1,    # Min successful runs required
)
@pytest.mark.timeout(30)  # Add timeout for safety
def test_operation():
    pass
```

### Decision Tree

```
Is test flaky?
├─ Async operations? → Use @pytest.mark.asyncio
├─ Network calls? → Use responses.activate or unittest.mock
├─ File I/O? → Use tmp_path fixture
├─ DateTime? → Use @freeze_time decorator
├─ Random values? → Use seeded fixtures
├─ External processes? → Use unittest.mock.patch
├─ Other? → Try @pytest.mark.timeout first
└─ Still flaky? → Mark with @pytest.mark.flaky(max_runs=3)
```

---

## Common Patterns

### Fixture for Async Tests

```python
# conftest.py
@pytest.fixture
def event_loop():
    """Provide event loop for asyncio tests."""
    import asyncio
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
```

### Fixture for Network Tests

```python
# conftest.py
import responses

@pytest.fixture
def mock_http():
    """Mock HTTP requests."""
    with responses.RequestsMock() as rsps:
        yield rsps

def test_with_mock_http(mock_http):
    mock_http.add(responses.GET, "https://api.example.com",
                  json={"data": "mocked"})
    # Test implementation
```

### Fixture for Environment Isolation

```python
# conftest.py
@pytest.fixture
def isolated_env(monkeypatch):
    """Provide isolated environment."""
    monkeypatch.setenv("DEBUG", "false")
    monkeypatch.setenv("LOG_LEVEL", "info")
    yield
    # Auto-restored

def test_config(isolated_env):
    assert os.environ.get("DEBUG") == "false"
```

### Fixture for Temporary Files

```python
def test_data_loading(tmp_path):
    """Test data loading from temporary directory."""
    data_file = tmp_path / "data.json"
    data_file.write_text('{"key": "value"}')
    
    result = load_data(data_file)
    assert result["key"] == "value"
    # Auto-cleaned by pytest
```

---

## CI Gates & Enforcement

### Pre-Commit Hook

The following is checked before commits:

```bash
# Check fragile imports (unguarded optional packages)
python .codex/scripts/fragile_tests_scan.py

# Check docstring coverage (>90%)
python .codex/scripts/check_docstring_coverage.py

# Check test naming (must match pattern)
python .codex/scripts/check_test_naming.py
```

### PR Checks

The following workflow runs on every PR:

- **fragile-test-guardian.yml**: Detects fragile imports, unhandled flaky tests, docstring violations
- Status: **Phase 5** (Advisory/informational), **Phase 6** (Blocking)

### Examples

#### Advisory Comment (Phase 5)

```
## 🧪 Fragile Test Guardian Report

### ❌ Fragile Imports (3 files)
- `tests/new_test.py`: numpy
- `tests/other_test.py`: torch

Add `pytest.importorskip()` guards.

### ⚠️ Unhandled Flaky Tests (1 detected)
- `tests/api_test.py::test_network_call`: network_calls pattern

Mark with `@pytest.mark.flaky` or mock with responses.

### 📚 Docstring Coverage (85%, missing 5)
Target: >90%. Add docstrings to test functions.
```

#### Blocking Check (Phase 6)

Same report, but **check fails** if violations present. Merge blocked until fixed.

---

## Quick Reference

### Test Template

```python
import pytest
from unittest.mock import patch

@pytest.mark.asyncio
async def test_feature_success(tmp_path, monkeypatch):
    """Test feature success path with mocked dependencies.
    
    Setup:
      - Prepare temporary files in tmp_path
      - Mock external dependencies
    
    Behavior:
      - Execute feature with test data
      - Verify primary assertion
    
    Teardown:
      - Automatic via pytest fixtures
    """
    # Setup
    test_file = tmp_path / "input.txt"
    test_file.write_text("test data")
    
    monkeypatch.setenv("FEATURE_ENABLED", "true")
    
    # Behavior
    result = await feature_function(test_file)
    
    # Assertion
    assert result == expected_value
```

### Checklist Before Committing

- [ ] Test name follows `test_<component>_<scenario>()` pattern
- [ ] Test has docstring explaining purpose
- [ ] No global state modifications (use fixtures)
- [ ] No network calls (use responses mock)
- [ ] No file operations outside tmp_path
- [ ] No datetime.now() calls (use freezegun or mock)
- [ ] All flaky patterns addressed or marked @pytest.mark.flaky
- [ ] Test passes in isolation: `pytest tests/your_test.py -v`
- [ ] Test order independent: `pytest --random-order tests/your_test.py`

---

## Resources

- **Pytest Documentation**: https://docs.pytest.org/
- **pytest-asyncio**: https://github.com/pytest-dev/pytest-asyncio
- **responses Library**: https://github.com/getsentry/responses
- **freezegun**: https://github.com/spulec/freezegun
- **pytest-random-order**: https://github.com/jreese/pytest-random-order
- **Phase 5 Audit Report**: `.codex/PHASE_5_FLAKY_TEST_AUDIT_REPORT.md`
- **Test Pattern Violations**: `.codex/PHASE_5_TEST_PATTERN_VIOLATIONS.md`

---

## Support

Questions about Phase 5 test standards?

1. Check `.codex/PHASE_5_FLAKY_TEST_AUDIT_REPORT.md` for detailed patterns
2. Review `.codex/PHASE_5_TEST_PATTERN_VIOLATIONS.md` for remediation
3. Run the audit: `python .codex/scripts/phase5_flaky_test_audit.py`
4. Check workflow results: See `fragile-test-guardian.yml` reports in PR

---

**Phase 5 Lane 2 Enforcement**: Active (Advisory)  
**Phase 6 Target**: Blocking enforcement  
**Last Updated**: 2026-07-18


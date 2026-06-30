# PHASE 5 TOKEN TEST PLAN
## Comprehensive Testing of Token Hierarchy Implementation

**Version**: 1.0.0  
**Created**: 2026-02-17  
**Campaign**: CODEX_MASTER_KEY  
**Phase**: 5 (Comprehensive Testing)  
**Status**: PLANNING

---

## Executive Summary

Phase 5 implements comprehensive validation of the token hierarchy system introduced in Phase 2 (`scripts/ci/_token_resolver.py`). This test plan covers **9 core scenarios** validating:

- **Token Resolution**: Full fallback chain (CODEX_MASTER_KEY → CODEX_BACKUP_KEY → GH_TOKEN → GITHUB_TOKEN)
- **Security Enforcement**: Elevated operations deny when scopes insufficient
- **Scope Validation**: Correct scope detection and enforcement # pragma: allowlist secret
- **Audit Trail**: Token usage logged without exposing values
- **Error Handling**: Graceful handling of invalid/missing tokens

**Deliverables**:
1. Comprehensive test suite (9 scenarios covering all paths)
2. Integration with CI/CD pipeline
3. Mock infrastructure for safe testing
4. Audit logging validation

**Success Criteria**:
- All 9 scenarios pass
- Error scenarios correctly deny operations
- No token values exposed in logs
- Scope validation prevents scope escalation

---

## Test Architecture Overview

### Test Hierarchy

```
PHASE_5_TOKEN_TESTS (pytest collection)
├── test_scenario_1_master_key_normal                  [5s]
├── test_scenario_2_backup_fallback                    [5s]
├── test_scenario_3_gh_token_fallback                  [5s]
├── test_scenario_4_github_token_fallback              [5s]
├── test_scenario_5_elevated_deny                      [3s]
├── test_scenario_6_scope_validation                   [5s]
├── test_scenario_7_audit_logging                      [5s]
├── test_scenario_8_sequential_fallback                [8s]
└── test_scenario_9_invalid_tokens                     [6s]

Total estimated time: ~45 seconds
```

### Key Components

```
tests/ci/test_phase_5_tokens.py
├── Fixtures
│   ├── isolated_environment    # Patches os.environ
│   ├── mock_github_api         # Mock HTTP endpoints
│   ├── log_capture             # Captures logging output
│   └── token_scenarios         # Parametrized scenarios
├── Helpers
│   ├── assert_token_hierarchy  # Validates ordering
│   ├── assert_no_token_leak    # Validates log safety
│   └── setup_scenario_env      # Isolates environment
└── Tests
    ├── Scenario-based tests (9 tests)
    └── Integration tests
```

### Environment Isolation Strategy

```python
# Pseudo-code for environment isolation

@pytest.fixture
def isolated_environment():
    """Save and restore environment for each test."""
    saved_env = os.environ.copy()
    
    # Clear all token-related vars
    for var in CANONICAL_HIERARCHY:
        os.environ.pop(var, None)
    
    yield os.environ
    
    # Restore original state
    os.environ.clear()
    os.environ.update(saved_env)
```

---

## Detailed Scenario Descriptions

### Scenario 1: CODEX_MASTER_KEY Available (Normal Operation)

**Purpose**: Validate normal operation when CODEX_MASTER_KEY is available

**Setup**:
```bash
export CODEX_MASTER_KEY="mock-master-token-abcd1234"
# All other tokens unset
```

**Test Steps**:
1. Call `get_token(required_elevated=False)`
2. Call `get_token_source()`
3. Call `get_token_scope()`
4. Build Authorization header with `get_auth_header()`
5. Validate scopes with `validate_token_scope(['repo', 'workflow', 'actions:write'])`

**Expected Outcome**:
```python
# Return values
assert get_token() == ("mock-master-token-abcd1234", "CODEX_MASTER_KEY")
assert get_token_source() == "CODEX_MASTER_KEY"
assert get_token_scope() == "elevated"
assert get_auth_header() == "Authorization: token mock-master-token-abcd1234"
assert validate_token_scope(['repo', 'workflow']) == (True, "has all required scopes")
```

**Validation Points**:
- ✓ Token retrieved from highest-priority source
- ✓ Scope correctly identified as "elevated"
- ✓ Authorization header properly formatted
- ✓ All required scopes available

**Risk**: LOW - This is baseline functionality

---

### Scenario 2: CODEX_BACKUP_KEY Fallback (Master Missing)

**Purpose**: Validate fallback to CODEX_BACKUP_KEY when master is unavailable

**Setup**:
```bash
# CODEX_MASTER_KEY is unset
export CODEX_BACKUP_KEY="mock-backup-token-efgh5678"
# GH_TOKEN and GITHUB_TOKEN unset
```

**Test Steps**:
1. Call `get_token(required_elevated=False)`
2. Verify hierarchy progression (master skipped, backup selected)
3. Call `get_token_scope()` - should return "standard" (not "elevated")
4. Validate backup-level scopes

**Expected Outcome**:
```python
assert get_token() == ("mock-backup-token-efgh5678", "CODEX_BACKUP_KEY")
assert get_token_scope() == "standard"
# Backup has ['repo', 'workflow'] only - no actions:write
assert validate_token_scope(['actions:write']) == (False, "missing scopes: actions:write")
```

**Validation Points**:
- ✓ Fallback occurs when master unavailable
- ✓ Correct source identified
- ✓ Scope is "standard" (reduced from "elevated")
- ✓ Scope mismatch detected when needed

**Risk**: LOW - First fallback path

---

### Scenario 3: GH_TOKEN Fallback (Both Custom Keys Missing)

**Purpose**: Validate fallback to GH_TOKEN when both CODEX keys unavailable

**Setup**:
```bash
# Both CODEX_MASTER_KEY and CODEX_BACKUP_KEY unset
export GH_TOKEN="mock-gh-token-ijkl9012"
# GITHUB_TOKEN unset
```

**Test Steps**:
1. Call `get_token(required_elevated=False)`
2. Verify hierarchy (master skip, backup skip, GH_TOKEN selected)
3. Validate available operations with limited scope

**Expected Outcome**:
```python
assert get_token() == ("mock-gh-token-ijkl9012", "GH_TOKEN")
assert get_token_source() == "GH_TOKEN"
assert get_token_scope() == "standard"
```

**Validation Points**:
- ✓ Fallback chain continues correctly
- ✓ Environment variable priority respected
- ✓ Scope limitations enforced

**Risk**: MEDIUM - Secondary fallback may have scope issues

---

### Scenario 4: GITHUB_TOKEN Fallback (Final Fallback)

**Purpose**: Validate ultimate fallback to GITHUB_TOKEN

**Setup**:
```bash
# All CODEX and GH_TOKEN vars unset
export GITHUB_TOKEN="mock-github-token-mnop3456"
```

**Test Steps**:
1. Call `get_token(required_elevated=False)`
2. Confirm GITHUB_TOKEN selected
3. Identify as "fallback" scope level

**Expected Outcome**:
```python
assert get_token() == ("mock-github-token-mnop3456", "GITHUB_TOKEN")
assert get_token_scope() == "fallback"
```

**Validation Points**:
- ✓ Final fallback works when all others unavailable
- ✓ Scope identified as limited
- ✓ System still functional (degraded)

**Risk**: MEDIUM - Many operations will fail with this token

---

### Scenario 5: Elevated Operation Denial (ERROR SCENARIO)

**Purpose**: **CRITICAL** - Verify elevated operations are DENIED when insufficient scopes

**Setup**:
```bash
# Only limited-scope token available
export GH_TOKEN="mock-gh-token-limited"
# No CODEX keys
```

**Test Steps**:
1. Call `get_token(required_elevated=True)` - **MUST raise exception**
2. Verify exception type is `TokenResolutionError`
3. Verify error message indicates missing scopes
4. Verify NO API call is made

**Expected Outcome**:
```python
with pytest.raises(TokenResolutionError) as exc_info:
    get_token(required_elevated=True)

assert "No elevated token available" in str(exc_info.value)
assert "workflow" in str(exc_info.value)
assert "actions:write" in str(exc_info.value)
# Verify no HTTP request made to GitHub API
assert mock_api.call_count == 0
```

**Validation Points**:
- ✓ **SECURITY**: Exception raised (fail-secure)
- ✓ Operation blocked before API call
- ✓ Error message guides remediation
- ✓ No bypass possible

**Risk**: **CRITICAL_SECURITY** - If this fails, security violation

---

### Scenario 6: Token Scope Validation & Detection

**Purpose**: Verify token scopes correctly detected and validated

**Setup**:
```bash
export CODEX_MASTER_KEY="mock-master-token"
export CODEX_BACKUP_KEY="mock-backup-token"
# Iterate through each token
```

**Test Steps** (multi-iteration):

**Iteration 1 - CODEX_MASTER_KEY scopes**:
```python
# Master key should have all scopes
required = ['repo', 'workflow', 'actions:write', 'security_events', 'admin:org_hook']
is_valid, msg = validate_token_scope(required)
assert is_valid == True
```

**Iteration 2 - CODEX_BACKUP_KEY scopes**:
```python
# Backup key missing elevated scopes
required = ['actions:write']
is_valid, msg = validate_token_scope(required)
assert is_valid == False
assert 'actions:write' in msg
```

**Validation Points**:
- ✓ All CODEX_MASTER_KEY scopes available
- ✓ CODEX_BACKUP_KEY scopes correctly reduced
- ✓ Missing scopes identified
- ✓ Scope hierarchy enforced
- ✓ No API calls (static validation)

**Risk**: MEDIUM - Incorrect scope mapping enables bypass

---

### Scenario 7: Audit Logging Without Exposure (SECURITY SCENARIO)

**Purpose**: **CRITICAL** - Verify token usage logged without exposing values

**Setup**:
```bash
export CODEX_MASTER_KEY="mock-master-token-secret123"
# Capture logging output
```

**Test Steps**:
1. Call `log_token_usage('Writing repo variable', required_elevated=False)`
2. Capture log output
3. Verify source, scope, context are logged
4. **VERIFY token value NOT in logs**

**Expected Outcome**:
```python
captured = log_capture.getvalue()

# MUST contain
assert 'source=CODEX_MASTER_KEY' in captured
assert 'scope=elevated' in captured
assert 'context=Writing repo variable' in captured

# MUST NOT contain
assert 'mock-master-token' not in captured
assert 'secret123' not in captured
assert 'token-secret' not in captured
```

**Validation Points**:
- ✓ **SECURITY**: No token value in logs
- ✓ Audit trail present (source, scope, context)
- ✓ Log format machine-parseable
- ✓ Timestamps present
- ✓ No PII exposed

**Risk**: **CRITICAL_SECURITY** - Token exposure via logs

**Diagnosis** (if fails):
- Search logs character-by-character for token substrings
- Check for f-string interpolation of token
- Verify logger.info() not using token in message

---

### Scenario 8: Sequential Fallback Through Entire Hierarchy

**Purpose**: Verify complete fallback sequence through all 4 levels

**Setup** (4 iterations):

```bash
# Iteration 1: Only master available
export CODEX_MASTER_KEY="token-m1"
unset CODEX_BACKUP_KEY GH_TOKEN GITHUB_TOKEN

# Iteration 2: Only backup available
unset CODEX_MASTER_KEY
export CODEX_BACKUP_KEY="token-b1"

# Iteration 3: Only GH_TOKEN available
unset CODEX_BACKUP_KEY
export GH_TOKEN="token-g1"

# Iteration 4: Only GITHUB_TOKEN available
unset GH_TOKEN
export GITHUB_TOKEN="token-h1"
```

**Test Steps** (for each iteration):
1. Call `get_token(required_elevated=False)`
2. Verify correct token selected
3. Verify hierarchy ordering maintained

**Expected Outcomes**:
```python
# Iteration 1
assert get_token()[1] == "CODEX_MASTER_KEY"

# Iteration 2
assert get_token()[1] == "CODEX_BACKUP_KEY"

# Iteration 3
assert get_token()[1] == "GH_TOKEN"

# Iteration 4
assert get_token()[1] == "GITHUB_TOKEN"
```

**Validation Points**:
- ✓ Each level selected in correct order
- ✓ No level skipped when available
- ✓ Priority strictly enforced
- ✓ CANONICAL_HIERARCHY order immutable

**Risk**: LOW - Fallback sequence broken

---

### Scenario 9: Invalid Token Handling

**Purpose**: Verify graceful handling of empty/invalid tokens

**Setup** (4 sub-tests):

```bash
# Test 1: Empty string
export CODEX_MASTER_KEY=""
export CODEX_BACKUP_KEY="valid-backup-token"

# Test 2: Whitespace-only
export CODEX_MASTER_KEY="   "
export CODEX_BACKUP_KEY="valid-backup-token"

# Test 3: None/null
unset CODEX_MASTER_KEY  # Equivalent to None
export CODEX_BACKUP_KEY="valid-backup-token"

# Test 4: All invalid - should raise error
export CODEX_MASTER_KEY=""
export CODEX_BACKUP_KEY="   "
export GH_TOKEN="null"
unset GITHUB_TOKEN
```

**Test Steps**:
1. Call `validate_token('')` - should return False
2. Call `validate_token('   ')` - should return False
3. Call `get_token()` in each scenario - should skip invalid, use backup if available
4. Call `get_token()` with all invalid - should raise `TokenResolutionError`

**Expected Outcomes**:
```python
# Test 1 & 2: validate_token returns False
assert validate_token('')[0] == False
assert validate_token('   ')[0] == False

# Test 3 & 4: get_token skips invalid tokens
assert get_token(required_elevated=False) == ("valid-backup-token", "CODEX_BACKUP_KEY")

# Test 4: All invalid raises exception
with pytest.raises(TokenResolutionError):
    get_token(required_elevated=False)
```

**Validation Points**:
- ✓ Empty strings rejected
- ✓ Whitespace-only rejected
- ✓ Invalid tokens skipped (fallback continues)
- ✓ Error raised when all invalid
- ✓ Error message descriptive

**Risk**: MEDIUM - Invalid tokens could cause API failures

---

## Mock Environment Setup Instructions

### Option 1: Using pytest Fixtures (RECOMMENDED)

```python
# tests/ci/conftest.py

import os
import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def isolated_environment():
    """Isolate environment for each test."""
    saved_env = os.environ.copy()
    
    # Clear all token variables
    from scripts.ci._token_resolver import CANONICAL_HIERARCHY
    for var in CANONICAL_HIERARCHY:
        os.environ.pop(var, None)
    
    yield os.environ
    
    # Restore
    os.environ.clear()
    os.environ.update(saved_env)

@pytest.fixture
def mock_github_api():
    """Mock GitHub API endpoints."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'success': True}
        mock_get.return_value = mock_response
        yield mock_get

@pytest.fixture
def log_capture(caplog):
    """Capture logs for audit validation."""
    import logging
    caplog.set_level(logging.INFO)
    yield caplog
```

### Option 2: Using Environment Modules

```python
# Setup for manual testing

import os
import subprocess

def setup_token_scenario(scenario_env):
    """Setup token environment for scenario."""
    env = os.environ.copy()
    
    # Clear existing tokens
    from scripts.ci._token_resolver import CANONICAL_HIERARCHY
    for var in CANONICAL_HIERARCHY:
        env.pop(var, None)
    
    # Set scenario tokens
    env.update(scenario_env)
    
    return env

# Usage
scenario_1_env = {
    'CODEX_MASTER_KEY': 'mock-token-1',
}
env = setup_token_scenario(scenario_1_env)
result = subprocess.run(['python', '-m', 'pytest', ...], env=env)
```

### Option 3: Docker Isolation (For CI/CD)

```dockerfile
# Dockerfile.test-phase5

FROM python:3.11-slim

WORKDIR /codex

COPY . .

# Clear any existing tokens
ENV CODEX_MASTER_KEY=""
ENV CODEX_BACKUP_KEY=""
ENV GH_TOKEN=""
ENV GITHUB_TOKEN=""

# Install dependencies
RUN pip install -e .
RUN pip install pytest pytest-cov

# Run tests with isolation
CMD ["pytest", "tests/ci/test_phase_5_tokens.py", "-v", "--tb=short"]
```

---

## Expected Pass Criteria

### Scenario Pass Rates

| Scenario | Pass Criteria | Acceptance |
|----------|---------------|-----------|
| 1 - Master Key Normal | Token retrieved, scope elevated | ✅ Pass if all true |
| 2 - Backup Fallback | Fallback occurs, scope standard | ✅ Pass if all true |
| 3 - GH_TOKEN Fallback | GH_TOKEN selected, scope standard | ✅ Pass if all true |
| 4 - GITHUB_TOKEN Fallback | GITHUB_TOKEN selected, scope fallback | ✅ Pass if all true |
| 5 - Elevated Deny | Exception raised, no API call | ✅ **MUST pass** |
| 6 - Scope Validation | All scopes correctly validated | ✅ Pass if all true |
| 7 - Audit Logging | Source/scope logged, token hidden | ✅ **MUST pass** |
| 8 - Sequential Fallback | Each level selected correctly | ✅ Pass if all true |
| 9 - Invalid Tokens | Invalid tokens skipped/error raised | ✅ Pass if all true |

### Overall Pass Criteria

```
✓ All 9 scenarios pass
✓ Error scenarios (5, 7) pass with security verified
✓ Scope enforcement prevents privilege escalation
✓ No token values exposed in logs or outputs
✓ Hierarchy strictly enforced (no reordering)
✓ Fallback chain complete and unbroken
✓ Invalid tokens handled gracefully
✓ Execution time < 1 minute
✓ No flaky tests (100% pass rate in 5 runs)
```

---

## Failure Diagnosis Guide

### Troubleshooting by Scenario

#### Scenario 1 Fails: CODEX_MASTER_KEY Not Selected

**Symptoms**:
- `get_token()` returns wrong token
- Token source shows different variable

**Root Causes**:
1. Environment not properly isolated - other tokens present
2. CANONICAL_HIERARCHY modified during test
3. Token validation too strict/loose

**Diagnosis Steps**:
```python
# Step 1: Print all environment variables
import os
from scripts.ci._token_resolver import CANONICAL_HIERARCHY
for var in CANONICAL_HIERARCHY:
    print(f"{var} = {os.environ.get(var, 'UNSET')}")

# Step 2: Print returned token
token, source = get_token()
print(f"Returned: token={token}, source={source}")

# Step 3: Verify CANONICAL_HIERARCHY
print(f"CANONICAL_HIERARCHY = {CANONICAL_HIERARCHY}")
```

**Recovery**:
- Check fixture isolation (verify saved_env is saved)
- Verify test setup clears environment correctly
- Add debug prints to token resolver

---

#### Scenario 5 Fails: Elevated Operation Not Denied

**Symptoms**:
- `get_token(required_elevated=True)` returns token instead of raising
- API call is made despite insufficient scopes
- Exception not raised or caught elsewhere

**Root Causes**:
1. `required_elevated` parameter not respected in get_token()
2. Exception caught and suppressed somewhere
3. Scope validation not checking elevated scopes

**Diagnosis Steps**:
```python
# Step 1: Call and catch exception
try:
    token, source = get_token(required_elevated=True)
    print(f"ERROR: Should have raised, got: {token}, {source}")
except TokenResolutionError as e:
    print(f"OK: Exception raised: {e}")

# Step 2: Verify GH_TOKEN is only available token
print(f"GH_TOKEN = {os.environ.get('GH_TOKEN')}")
print(f"CODEX_MASTER_KEY = {os.environ.get('CODEX_MASTER_KEY')}")
print(f"CODEX_BACKUP_KEY = {os.environ.get('CODEX_BACKUP_KEY')}")

# Step 3: Check acceptable_sources in get_token
# Should be CANONICAL_HIERARCHY[:2] when required_elevated=True
```

**Recovery**:
- Verify `if required_elevated: acceptable_sources = CANONICAL_HIERARCHY[:2]`
- Check exception is not caught in test
- Verify mock API is not called (add assertion)

---

#### Scenario 7 Fails: Token Exposed in Logs

**Symptoms**:
- Test assertion fails: "Token value found in logs"
- Audit logging test cannot pass

**Root Causes**:
1. Token value interpolated in log message via f-string
2. Token printed via debug log level
3. Exception traceback includes token

**Diagnosis Steps**:
```python
# Step 1: Capture logs and search for token substrings
captured = caplog.getvalue()
token_secret = "mock-master-token-secret123"

# Search for exact token
if token_secret in captured:
    print(f"FAIL: Found exact token in logs")
    print(captured)

# Search for substrings (first 8 chars)
if token_secret[:8] in captured:
    print(f"FAIL: Found token prefix in logs")

# Step 2: Check log_token_usage implementation
# Verify it does NOT include token in message

# Step 3: Check for leaks in exception messages
try:
    # ... code that might raise
except Exception as e:
    if token_secret in str(e):
        print(f"FAIL: Token in exception message")
```

**Recovery**:
- Remove token from f-string: `f"token={token}"` → `f"token=***"`
- Check logger calls for token interpolation
- Test exception messages for token exposure
- Add log capture test specifically for token substrings

---

#### Scenario 6 Fails: Scope Validation Incorrect

**Symptoms**:
- `validate_token_scope()` returns wrong result
- Scopes not matching TOKEN_SCOPES mapping
- Security bypass possible

**Root Causes**:
1. TOKEN_SCOPES mapping outdated or incorrect
2. Scope lookup returning wrong list
3. Comparison logic incorrect

**Diagnosis Steps**:
```python
# Step 1: Print TOKEN_SCOPES mapping
from scripts.ci._token_resolver import TOKEN_SCOPES
for source, scopes in TOKEN_SCOPES.items():
    print(f"{source}: {scopes}")

# Step 2: Verify against GitHub API docs
# https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps

# Step 3: Test each scope validation
test_cases = [
    ('CODEX_MASTER_KEY', ['repo'], True),
    ('CODEX_MASTER_KEY', ['actions:write'], True),
    ('CODEX_BACKUP_KEY', ['actions:write'], False),
    ('GH_TOKEN', ['workflow'], False),
]

for source, required, expected in test_cases:
    os.environ['TEST_SOURCE'] = source
    is_valid, msg = validate_token_scope(required)
    assert is_valid == expected, f"Failed: {source} with {required}"
```

**Recovery**:
- Cross-reference TOKEN_SCOPES with GitHub documentation
- Update scopes if GitHub changed them
- Fix comparison logic in validate_token_scope()

---

### General Troubleshooting

#### Tests Pass Locally But Fail in CI

**Likely Causes**:
1. CI environment has different token setup
2. CI uses different Python version
3. CI has system-level token variables

**Solution**:
```bash
# In CI, explicitly clear tokens before test
export CODEX_MASTER_KEY=""
export CODEX_BACKUP_KEY=""
export GH_TOKEN=""
export GITHUB_TOKEN=""

# Run with verbose output
pytest tests/ci/test_phase_5_tokens.py -vvv --tb=long
```

#### Flaky Tests (Pass/Fail Randomly)

**Likely Causes**:
1. Race condition in environment setup
2. Mock not properly isolated
3. Test order dependency

**Solution**:
```bash
# Run tests multiple times
pytest tests/ci/test_phase_5_tokens.py --count=10

# Run in random order
pytest tests/ci/test_phase_5_tokens.py --random-order

# Check for leakage between tests
pytest tests/ci/test_phase_5_tokens.py -vvv
```

---

## Integration with CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/phase-5-token-tests.yml

name: Phase 5 Token Tests

on:
  push:
    paths:
      - 'scripts/ci/_token_resolver.py'
      - 'tests/ci/test_phase_5_tokens.py'
  pull_request:
    paths:
      - 'scripts/ci/_token_resolver.py'
      - 'tests/ci/test_phase_5_tokens.py'

jobs:
  test-token-hierarchy:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.11', '3.12']
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Clear token environment
        run: |
          unset CODEX_MASTER_KEY
          unset CODEX_BACKUP_KEY
          unset GH_TOKEN
          unset GITHUB_TOKEN
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e .
          pip install pytest pytest-cov
      
      - name: Run Phase 5 Token Tests
        run: |
          pytest tests/ci/test_phase_5_tokens.py \
            -v \
            --tb=short \
            --cov=scripts/ci/_token_resolver \
            --cov-report=xml \
            --cov-report=term
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
          flags: phase5-tokens
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml (add to existing)

- repo: local
  hooks:
    - id: phase-5-token-tests
      name: Phase 5 Token Tests
      entry: pytest tests/ci/test_phase_5_tokens.py
      language: system
      pass_filenames: false
      always_run: true
      stages: [commit]
```

### Integration with Existing Tests

```python
# tests/ci/conftest.py - shared fixtures

@pytest.fixture(scope="session")
def phase_5_integration():
    """Verify Phase 5 token tests can run."""
    import importlib
    try:
        token_resolver = importlib.import_module('scripts.ci._token_resolver')
        assert hasattr(token_resolver, 'get_token')
        assert hasattr(token_resolver, 'CANONICAL_HIERARCHY')
        return token_resolver
    except ImportError as e:
        pytest.skip(f"Phase 2 token resolver not found: {e}")
```

---

## Success Metrics

### Test Coverage

- **Line Coverage**: ≥95% of `_token_resolver.py`
- **Branch Coverage**: ≥90% (including error paths)
- **Scenario Coverage**: 9/9 scenarios (100%)

### Quality Metrics

```
Pass Rate:           100% (9/9 scenarios)
Flakiness Rate:      0% (no random failures)
Execution Time:      < 45 seconds
Error Detection:     5 scenarios correctly deny
Scope Enforcement:   8 scenarios enforce correctly
Audit Logging:       1 scenario validates no leaks
```

### Security Metrics

```
Token Exposure:      0 (no tokens in logs/output)
Unauthorized Calls:  0 (no API calls when denied)
Scope Escalation:    0 (no privilege escalation)
```

---

## Phase 5 Checklist

- [ ] Create `tests/ci/test_phase_5_tokens.py` with all 9 scenarios
- [ ] Implement isolated_environment fixture
- [ ] Implement mock_github_api fixture
- [ ] Implement log_capture validation
- [ ] Run all 9 scenarios locally
- [ ] All scenarios pass (100%)
- [ ] No token values in logs (security audit)
- [ ] Elevated operations correctly denied (security audit)
- [ ] Add to GitHub Actions CI/CD
- [ ] Update .pre-commit-config.yaml
- [ ] Document results in PHASE_5_TOKEN_TEST_RESULTS.md
- [ ] Merge to main branch

---

## References

- **Token Resolver**: `scripts/ci/_token_resolver.py`
- **GitHub OAuth Scopes**: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps
- **Phase 2 Delivery**: PHASE_2_TOKEN_UTILITY_IMPLEMENTATION.md
- **Test Infrastructure Spec**: `.codex/PHASE_5_TEST_INFRASTRUCTURE_SPEC.md`
- **Test Scenarios JSON**: `.codex/PHASE_5_TOKEN_TEST_SCENARIOS.json`

---

**Status**: READY FOR PHASE 5 IMPLEMENTATION  
**Last Updated**: 2026-02-17  
**Approval**: Pending Security Review

# PHASE 5 TEST INFRASTRUCTURE SPECIFICATION
## Technical Design for Token Test Implementation

**Version**: 1.0.0  
**Created**: 2026-02-17  
**Campaign**: CODEX_MASTER_KEY  
**Audience**: Implementation Team (Phase 5)  

---

## Overview

This document specifies the technical infrastructure required to implement Phase 5 token hierarchy tests. It covers mock strategies, environment isolation, fixture design, and CI/CD integration.

---

## 1. Mock GitHub API Endpoints
 # pragma: allowlist secret
### Endpoint Strategy

Phase 5 tests must avoid making real GitHub API calls. Use `unittest.mock` to intercept HTTP requests.

### Mock Endpoints Needed

#### 1.1 User Authentication Check

**Real Endpoint**: `GET /user`

```python
# Mock implementation
@pytest.fixture
def mock_api_get_user():
    """Mock GitHub GET /user endpoint."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'login': 'test-user',
            'id': 12345,
            'type': 'User'
        }
        
        def get_handler(url, **kwargs):
            if '/user' in url:
                return mock_response
            raise ValueError(f"Unexpected URL: {url}")
        
        mock_get.side_effect = get_handler
        yield mock_get
```

#### 1.2 Repository Operations

**Real Endpoint**: `GET /repos/{owner}/{repo}`

```python
@pytest.fixture
def mock_api_get_repo():
    """Mock GitHub GET /repos endpoint."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'test-repo',
            'full_name': 'test-org/test-repo',
            'private': False
        }
        
        def get_handler(url, **kwargs):
            if '/repos/' in url:
                return mock_response
            raise ValueError(f"Unexpected URL: {url}")
        
        mock_get.side_effect = get_handler
        yield mock_get
```

#### 1.3 Workflow Operations (Elevated)

**Real Endpoint**: `POST /repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches`

```python
@pytest.fixture
def mock_api_trigger_workflow():
    """Mock GitHub workflow trigger endpoint."""
    with patch('requests.post') as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 204  # No content
        
        def post_handler(url, **kwargs):
            if '/actions/workflows/' in url and '/dispatches' in url:
                return mock_response
            raise ValueError(f"Unexpected URL: {url}")
        
        mock_post.side_effect = post_handler
        yield mock_post
```

#### 1.4 Scope Verification (Synthetic)

For testing scope requirements without real API calls:

```python
@pytest.fixture
def mock_api_check_scopes():
    """Mock scope verification endpoint."""
    # GitHub doesn't have a built-in scope check endpoint,
    # but we can mock the Authorization header presence/absence
    
    def verify_scopes(auth_header, required_scopes):
        """Verify scopes in authorization header."""
        # In real implementation, would be determined by token source
        # For mocking, we verify the header is present
        if not auth_header or 'Authorization: token' not in auth_header:
            return False, "No authorization header"
        return True, "Authorization header present"
    
    return verify_scopes
```

---

## 2. Environment Variable Isolation Strategy

### Challenge

Environment variables are global. Tests must not interfere with each other or with real system configuration.

### Solution: Three-Level Isolation

#### Level 1: Test-Level Isolation (Recommended)

```python
import os
import pytest
from scripts.ci._token_resolver import CANONICAL_HIERARCHY

@pytest.fixture
def isolated_env():
    """Isolate environment for single test."""
    # Save original
    saved_env = {var: os.environ.get(var) for var in CANONICAL_HIERARCHY}
    
    # Clear all token vars
    for var in CANONICAL_HIERARCHY:
        os.environ.pop(var, None)
    
    yield os.environ
    
    # Restore original
    for var, value in saved_env.items():
        if value is None:
            os.environ.pop(var, None)
        else:
            os.environ[var] = value
```

**Pros**:
- Simple to implement
- Works with pytest
- Covers most scenarios

**Cons**:
- Not thread-safe (tests must not run in parallel)
- Does not restore between fixtures

#### Level 2: Process-Level Isolation (For Flaky Tests)

```python
import subprocess
import json

def run_test_in_subprocess(test_name, env_vars):
    """Run test in isolated subprocess."""
    env = os.environ.copy()
    
    # Clear token vars
    from scripts.ci._token_resolver import CANONICAL_HIERARCHY
    for var in CANONICAL_HIERARCHY:
        env.pop(var, None)
    
    # Set test vars
    env.update(env_vars)
    
    # Run test
    result = subprocess.run(
        ['pytest', f'tests/ci/test_phase_5_tokens.py::{test_name}', '-v'],
        env=env,
        capture_output=True,
        text=True
    )
    
    return result.returncode == 0
```

**Pros**:
- Complete isolation (truly separate process)
- Safe even with parallel test runners
- Eliminates side effects

**Cons**:
- Slower (subprocess overhead)
- More complex
- Harder to debug

#### Level 3: Container-Level Isolation (For CI/CD)

```dockerfile
# Dockerfile.test-phase5-isolation

FROM python:3.11-slim

WORKDIR /codex

# Clear any system tokens
ENV CODEX_MASTER_KEY=""
ENV CODEX_BACKUP_KEY=""
ENV GH_TOKEN=""
ENV GITHUB_TOKEN=""

# Copy code
COPY . .

# Install
RUN pip install -e . && pip install pytest pytest-cov

# Run tests
CMD ["pytest", "tests/ci/test_phase_5_tokens.py", "-v"]
```

**Pros**:
- Complete OS-level isolation
- No system interference
- Perfect for CI/CD

**Cons**:
- Slower (container startup)
- Requires Docker
- Less convenient for development

### Recommended Approach

Use **Level 1 (Test-Level Isolation)** for development:
- Fast (no subprocess overhead)
- Simple to debug (inline execution)
- Works with pytest directly

Use **Level 3 (Container)** in CI/CD:
- Guaranteed clean environment
- No test pollution
- Reproducible

---

## 3. Token Mock Implementation Strategy

### Challenge

We need to mock tokens that look real enough to pass validation but are clearly fake for security.

### Strategy: Factory Pattern

```python
class TokenFactory:
    """Generate realistic-looking mock tokens."""
    
    @staticmethod
    def create_master_key(prefix="mock-master"):
        """Create mock CODEX_MASTER_KEY token."""
        return f"{prefix}-{''.join(random.choices('abcdef0123456789', k=32))}"
    
    @staticmethod
    def create_backup_key(prefix="mock-backup"):
        """Create mock CODEX_BACKUP_KEY token."""
        return f"{prefix}-{''.join(random.choices('abcdef0123456789', k=32))}"
    
    @staticmethod
    def create_gh_token(prefix="ghp_"):
        """Create mock GitHub Personal Access Token format."""
        return f"{prefix}{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=36))}"
    
    @staticmethod
    def create_github_token(prefix="ghu_"):
        """Create mock GitHub Actions Token format."""
        return f"{prefix}{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789', k=36))}"

# Usage in fixtures
@pytest.fixture
def mock_tokens():
    """Provide realistic mock tokens."""
    return {
        'master': TokenFactory.create_master_key(),
        'backup': TokenFactory.create_backup_key(),
        'gh': TokenFactory.create_gh_token(),
        'github': TokenFactory.create_github_token(),
    }
```

### Token Validation

Tokens should pass basic validation but never be used for actual API calls:

```python
def is_valid_mock_token(token: str) -> bool:
    """Check if token is a valid mock token."""
    # Must look like a token (not empty, has content)
    if not token or len(token) < 20:
        return False
    
    # Must be string
    if not isinstance(token, str):
        return False
    
    return True

# In tests
def test_mock_token_passes_validation():
    token = TokenFactory.create_master_key()
    is_valid, msg = validate_token(token)
    assert is_valid
```

---

## 4. Test Fixture Requirements

### Core Fixtures

#### 4.1 Environment Setup Fixture

```python
@pytest.fixture
def token_scenario_env(request):
    """Setup token environment for scenario."""
    # Get scenario config from marker
    marker = request.node.get_closest_marker('token_scenario')
    scenario_config = marker.kwargs if marker else {}
    
    # Save original
    saved_env = os.environ.copy()
    
    # Clear tokens
    from scripts.ci._token_resolver import CANONICAL_HIERARCHY
    for var in CANONICAL_HIERARCHY:
        os.environ.pop(var, None)
    
    # Set scenario tokens
    os.environ.update(scenario_config)
    
    yield scenario_config
    
    # Restore
    os.environ.clear()
    os.environ.update(saved_env)
```

#### 4.2 Logging Capture Fixture

```python
@pytest.fixture
def token_log_capture(caplog):
    """Capture logs for token audit validation."""
    import logging
    from scripts.ci._token_resolver import logger
    
    caplog.set_level(logging.INFO, logger=logger.name)
    
    yield caplog
    
    # Validation helper
    caplog.validate_no_token_exposure = lambda token: (
        token not in caplog.text and
        token[:8] not in caplog.text and
        token[-8:] not in caplog.text
    )
```

#### 4.3 Mock API Fixture

```python
@pytest.fixture
def mock_github_api():
    """Mock all GitHub API endpoints."""
    with patch.dict('sys.modules', {'requests': MagicMock()}):
        with patch('requests.get') as mock_get, \
             patch('requests.post') as mock_post, \
             patch('requests.put') as mock_put:
            
            # Setup response mocks
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {'success': True}
            
            mock_get.return_value = mock_response
            mock_post.return_value = mock_response
            mock_put.return_value = mock_response
            
            # Yield tuple of all mocks for assertion
            yield {
                'get': mock_get,
                'post': mock_post,
                'put': mock_put,
            }
```

#### 4.4 Parametrized Scenarios Fixture

```python
@pytest.fixture(params=[
    pytest.param(
        {
            'CODEX_MASTER_KEY': 'token-m1',
            'CODEX_BACKUP_KEY': None,
            'GH_TOKEN': None,
            'GITHUB_TOKEN': None,
        },
        id='master_only'
    ),
    pytest.param(
        {
            'CODEX_MASTER_KEY': None,
            'CODEX_BACKUP_KEY': 'token-b1',
            'GH_TOKEN': None,
            'GITHUB_TOKEN': None,
        },
        id='backup_only'
    ),
    # ... more scenarios
])
def token_scenarios(request, isolated_env):
    """Parametrized fixture for all token scenarios."""
    scenario = request.param
    
    for var, value in scenario.items():
        if value:
            isolated_env[var] = value
        else:
            isolated_env.pop(var, None)
    
    return scenario
```

---

## 5. CI Isolation and Cleanup Procedures

### GitHub Actions Workflow Setup

```yaml
# .github/workflows/test-phase-5-isolation.yml

name: Phase 5 Token Tests (Isolated)

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    container:
      image: python:3.11-slim
      options: >-
        --env CODEX_MASTER_KEY=""
        --env CODEX_BACKUP_KEY=""
        --env GH_TOKEN=""
        --env GITHUB_TOKEN=""
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Verify environment is clean
        run: |
          [ -z "$CODEX_MASTER_KEY" ] || exit 1
          [ -z "$CODEX_BACKUP_KEY" ] || exit 1
          [ -z "$GH_TOKEN" ] || exit 1
          [ -z "$GITHUB_TOKEN" ] || exit 1
      
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov
      
      - name: Run Phase 5 Token Tests
        run: |
          pytest tests/ci/test_phase_5_tokens.py \
            -v \
            --tb=short \
            --cov=scripts/ci/_token_resolver
      
      - name: Verify cleanup
        if: always()
        run: |
          # Ensure no tokens remain
          [ -z "$CODEX_MASTER_KEY" ] || exit 1
```

### Pre-Test Cleanup Script

```bash
#!/bin/bash
# scripts/ci/cleanup_tokens_pre_test.sh

# Clear all token environment variables
for var in CODEX_MASTER_KEY CODEX_BACKUP_KEY GH_TOKEN GITHUB_TOKEN; do
    unset "$var"
done

# Verify clean state
echo "Token environment after cleanup:"
env | grep -E "(CODEX|GH_TOKEN|GITHUB_TOKEN)" || echo "✓ All tokens cleared"

# Run tests
pytest tests/ci/test_phase_5_tokens.py "$@"
```

### Post-Test Cleanup Script

```bash
#!/bin/bash
# scripts/ci/cleanup_tokens_post_test.sh

# Remove any test artifacts
rm -f /tmp/test-token-*.txt
rm -f .pytest_cache/token_*
rm -f .coverage

# Verify logs don't contain tokens
if grep -r "ghp_\|ghu_" logs/ 2>/dev/null; then
    echo "ERROR: Token found in logs!"
    exit 1
fi

# Clear environment
for var in CODEX_MASTER_KEY CODEX_BACKUP_KEY GH_TOKEN GITHUB_TOKEN; do
    unset "$var"
done

echo "✓ Cleanup complete"
```

---

## 6. Test Execution Environment

### Python Version Compatibility

Test with multiple Python versions:

```yaml
# Matrix in GitHub Actions
strategy:
  matrix:
    python-version: ['3.11', '3.12']
```

### Required Dependencies

```
# requirements-test.txt
pytest >= 7.0
pytest-cov >= 4.0
pytest-mock >= 3.10
pytest-timeout >= 2.1
pytest-xdist >= 3.0
```

### Test Configuration

```ini
# pytest.ini (add phase-5 section)

[pytest]
testpaths = tests/ci/test_phase_5_tokens.py
python_files = test_*.py
python_classes = Test*
python_functions = test_*

# Timeout per test
timeout = 30

# Markers
markers =
    token_scenario: Token resolution scenario tests
    security: Security-critical tests
    slow: Slow running tests
```

---

## 7. Mock Implementation Checklist

### Pre-Implementation

- [ ] Review `_token_resolver.py` implementation
- [ ] Identify all functions that need testing
- [ ] List all functions that make API calls (should be NONE)
- [ ] Review GitHub API documentation for scope definitions
- [ ] Design mock token formats

### Implementation

- [ ] Create `tests/ci/conftest.py` with core fixtures
- [ ] Implement `isolated_env` fixture
- [ ] Implement `mock_github_api` fixture
- [ ] Implement `token_log_capture` fixture
- [ ] Create `TokenFactory` for realistic mocks
- [ ] Implement parametrized `token_scenarios` fixture

### Integration

- [ ] Add Phase 5 tests to GitHub Actions
- [ ] Add cleanup scripts to CI pipeline
- [ ] Create pre/post test hooks
- [ ] Add coverage reporting
- [ ] Verify isolation (no cross-test pollution)

### Validation

- [ ] All 9 scenarios pass
- [ ] No real API calls made
- [ ] Environment properly isolated
- [ ] Logs contain no token values
- [ ] Coverage >= 95% of token resolver

---

## 8. Integration with Existing Test Infrastructure

### Existing Test Files to Update

```
tests/ci/
├── conftest.py              # Add Phase 5 fixtures
├── test_token_resolver.py   # (If exists) - coordinate with Phase 5
└── test_phase_5_tokens.py   # NEW - Phase 5 tests
```

### Integration Points

```python
# In tests/ci/conftest.py

# Phase 2 Integration (existing token resolver)
from scripts.ci._token_resolver import (
    get_token,
    CANONICAL_HIERARCHY,
    TokenResolutionError,
)

# Phase 5 Fixtures (new)
@pytest.fixture
def isolated_env():
    """Phase 5: Isolated token environment."""
    # ... implementation

# Phase 4 Integration (if script refactoring uses resolver)
# Can reuse Phase 5 fixtures for script tests
```

### Shared Test Utilities

```python
# tests/ci/token_test_utils.py

class TokenTestHelper:
    """Shared utilities for token testing."""
    
    @staticmethod
    def assert_token_not_exposed(text: str, token: str):
        """Verify token not present in text."""
        assert token not in text, f"Token exposed: {token}"
        assert token[:16] not in text, f"Token prefix exposed"
    
    @staticmethod
    def assert_hierarchy_order(selections: list):
        """Verify hierarchy order maintained."""
        from scripts.ci._token_resolver import CANONICAL_HIERARCHY
        for selection, expected in zip(selections, CANONICAL_HIERARCHY):
            assert selection == expected, f"Order violated"
    
    @staticmethod
    def setup_scenario(env_vars: dict):
        """Setup scenario environment."""
        import os
        for var, value in env_vars.items():
            if value:
                os.environ[var] = value
            else:
                os.environ.pop(var, None)
```

---

## 9. Security Considerations

### Token Exposure Prevention

```python
# In all logging
logger.info(f"Using token from {source}")  # ✓ OK
logger.info(f"Token: {token}")               # ✗ FAIL - exposes token
logger.info(f"Token preview: {token[:8]}")   # ✗ FAIL - exposes prefix
```

### Exception Safety

```python
# Exception messages must not contain tokens
try:
    perform_operation(token)
except Exception as e:
    # BAD: Exception contains token
    logger.error(f"Operation failed with token: {e}")
    
    # GOOD: Log error without token
    logger.error(f"Operation failed: {e}", exc_info=False)
```

### Mock Token Security

```python
# Mock tokens must never be real
# Use prefixes like "mock-", "test-", "fake-"
token = "mock-token-abc123"  # OK

# Never use actual GitHub token formats in production code
token = "ghp_1234567890123456789012345678901234567"  # Only in tests
```

---

## 10. Performance Optimization

### Test Execution Time

```
Target: < 1 minute for all 9 scenarios
Individual scenario: 3-8 seconds

Breakdown:
- Setup:           2s (environment isolation)
- Test execution:  40s (9 scenarios × 4.5s average)
- Teardown:        2s (cleanup)
- Overhead:        6s (pytest startup, reporting)
Total:            ~50s
```

### Optimization Strategies

```python
# 1. Use pytest-xdist for parallel execution
pytest tests/ci/test_phase_5_tokens.py -n auto

# 2. Reduce fixture setup overhead
@pytest.fixture(scope="module")
def mock_github_api():
    """Reuse mock across multiple tests."""
    # Setup once per module

# 3. Cache expensive operations
@pytest.fixture(scope="session")
def token_factory():
    """Create once per test session."""
    return TokenFactory()

# 4. Use pytest-timeout to catch hangs
@pytest.mark.timeout(10)
def test_scenario_1():
    # Auto-fail if takes > 10 seconds
    pass
```

---

## 11. Testing Checklist

Before marking Phase 5 complete:

### Code Quality
- [ ] All 9 scenarios have clear test names
- [ ] Tests follow pytest conventions
- [ ] Docstrings explain purpose
- [ ] Comments for complex logic
- [ ] No hardcoded values (use fixtures/parametrization)

### Coverage
- [ ] >= 95% line coverage of token_resolver.py
- [ ] >= 90% branch coverage
- [ ] All error paths tested
- [ ] All fallback paths tested

### Security
- [ ] No tokens exposed in logs
- [ ] No tokens in exception messages
- [ ] No tokens in test output
- [ ] Elevated operations correctly denied

### Integration
- [ ] Tests pass in GitHub Actions
- [ ] Tests pass in clean container
- [ ] Tests pass with Python 3.11 and 3.12
- [ ] CI/CD integration complete

### Documentation
- [ ] PHASE_5_TOKEN_TEST_PLAN.md complete
- [ ] PHASE_5_TEST_INFRASTRUCTURE_SPEC.md complete
- [ ] PHASE_5_TOKEN_TEST_SCENARIOS.json complete
- [ ] README updated with Phase 5 info

---

## Appendix A: Mock Token Examples

```python
# Examples of mock tokens by type

MOCK_MASTER_KEY = "mock-master-abcdef0123456789abcdef0123456789"
MOCK_BACKUP_KEY = "mock-backup-fedcba9876543210fedcba9876543210"
MOCK_GH_TOKEN = "ghp_1234567890123456789012345678901234567"
MOCK_GITHUB_TOKEN = "******"

# These should NEVER appear in real code or commits
# They are ONLY for testing purposes
```

---

## Appendix B: Environment Variables Reference

```bash
# Canonical token hierarchy
CODEX_MASTER_KEY        # Primary (elevated scopes)
CODEX_BACKUP_KEY        # Secondary (reduced scopes)
GH_TOKEN                # Tertiary (standard scopes)
GITHUB_TOKEN            # Final fallback (minimal scopes)

# Related variables (NOT part of token resolution)
GITHUB_SERVER_URL       # For custom GitHub instances
GITHUB_API_URL          # For custom GitHub instances
```

---

## Appendix C: Troubleshooting Reference

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| Test passes locally, fails in CI | Environment not isolated | Use container-level isolation |
| Random failures (flaky) | Race condition in env setup | Use process-level isolation |
| Token exposure in logs | f-string includes token | Remove token from log message |
| Wrong token selected | Hierarchy not enforced | Verify CANONICAL_HIERARCHY order |
| Slow test execution | Subprocess overhead | Use test-level isolation in dev |
| Coverage gaps | Branch not tested | Add test for error case |

---

**Status**: READY FOR IMPLEMENTATION  
**Last Updated**: 2026-02-17  
**Next Phase**: Phase 5 Implementation (tests/ci/test_phase_5_tokens.py)

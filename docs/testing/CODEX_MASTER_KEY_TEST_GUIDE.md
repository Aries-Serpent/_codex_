# CODEX_MASTER_KEY Testing Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.1

> **Version:** 1.0  
> **Last Updated: 2026-06-29
> **Audience:** Developers, QA, Site Reliability Engineers  
> **Scope:** Complete testing framework for CODEX_MASTER_KEY (23 scopes, 10 processes)

## Quick Start

### Prerequisites

```bash
# Install test dependencies
pip install -r requirements-tests-optional.txt

# Set up environment
export CODEX_MASTER_KEY="ghp_..." # GitHub PAT with 23 scopes
export CODEX_BACKUP_KEY="ghp_..." # Backup PAT (optional)
```

### Run Tests Locally

```bash
# Run all CODEX_MASTER_KEY tests
pytest tests/github/test_codex_master_key_scopes.py -v

# Run specific test suite
pytest tests/github/test_repo_variables_comprehensive.py -v

# Run with coverage
pytest tests/github/ --cov=src/codex/github --cov-report=html

# Run integration tests
pytest tests/integration/test_codex_master_key_integration.py -v
```

---

## Test Organization

### Phase 1: Infrastructure & Setup

**Test Files:**
- `tests/github/conftest_codex_master_key.py` — Shared fixtures and utilities
- `tests/github/test_codex_master_key_scopes.py` — Scope validation

**What It Tests:**
-  All 23 token scopes present
-  Token fallback hierarchy (MASTER → BACKUP → GH_TOKEN)
-  API version header validation
-  Rate limit header parsing

**Running Phase 1:**
```bash
pytest tests/github/test_codex_master_key_scopes.py -v
```

### Phase 2: Core Operations

**Test Files:**
- `tests/github/test_repo_variables_comprehensive.py` (Process 1)
- `tests/github/test_workflow_approval_dispatch.py` (Process 2)
- `tests/github/test_secrets_management.py` (Process 3)
- `tests/github/test_package_registry.py` (Process 4)
- `tests/github/test_org_management.py` (Process 5)
- `tests/github/test_webhooks.py` (Process 6)
- `tests/github/test_pr_issue_operations.py` (Process 7)

**What It Tests:**
-  CRUD operations (Create, Read, Update, Delete)
-  Batch operations
-  Error scenarios (401, 403, 404, 409, 422, 429)
-  State synchronization

**Running Phase 2:**
```bash
# Run all core operation tests
pytest tests/github/test_*.py -v

# Or run specific process
pytest tests/github/test_repo_variables_comprehensive.py::TestRepositoryScopeCRUD -v
```

### Phase 3: Security & Auth

**Test Files:**
- `tests/github/test_security_management.py` (Process 8)
- `tests/github/test_token_auth_management.py` (Process 9)
- `tests/github/test_agent_autonomy_framework.py` (Process 10)

**What It Tests:**
-  CodeQL alert management
-  Secret scanning
-  Token scope verification
-  Token rotation
-  Token delegation
-  Agent autonomy framework

**Running Phase 3:**
```bash
pytest tests/github/test_security_management.py -v
pytest tests/github/test_token_auth_management.py -v
pytest tests/github/test_agent_autonomy_framework.py -v
```

### Phase 4: Integration Tests

**Test Files:**
- `tests/integration/test_codex_master_key_integration.py` — Cross-process workflows
- `tests/integration/test_multi_agent_coordination.py` — Multi-agent scenarios
- `tests/integration/test_rate_limiting_strategy.py` — Rate limit handling

**What It Tests:**
-  Complete end-to-end workflows
-  Multi-agent coordination
-  Error recovery scenarios
-  State consistency
-  Concurrent operations

**Running Phase 4:**
```bash
pytest tests/integration/ -v
```

---

## Fixture Reference

### Available Fixtures

**From `conftest_codex_master_key.py`:**

```python
# Token and configuration
@pytest.fixture
def github_token() -> str:
    """Returns CODEX_MASTER_KEY from environment."""

@pytest.fixture
def api_headers() -> dict:
    """Returns GitHub API headers with authorization."""

# Test data generators
@pytest.fixture
def test_repo_name() -> str:
    """Returns timestamped test repository name."""

@pytest.fixture
def repo_owner() -> str:
    """Returns repository owner from context."""

# Mock builders
@pytest.fixture
def mock_response():
    """Builder for mocked GitHub API responses."""

@pytest.fixture
def mock_error_response():
    """Builder for error responses (401, 403, etc.)."""

# Audit utilities
@pytest.fixture
def audit_logger():
    """Logger for API call auditing."""
```

### Using Fixtures

```python
def test_list_variables(github_token: str, api_headers: dict):
    """Test listing repository variables."""
    assert "Authorization" in api_headers
    assert github_token.startswith("ghp_")

def test_create_variable(mock_response):
    """Test creating a variable."""
    response = mock_response(
        status_code=201,
        body={"name": "TEST_VAR", "value": "test"}
    )
```

---

## Common Test Patterns

### Pattern 1: CRUD Operations

```python
def test_variable_lifecycle(github_token: str):
    """Test complete variable lifecycle."""
    # Create
    # Read
    # Update
    # Delete
    # Verify deletion
```

### Pattern 2: Error Scenarios

```python
def test_insufficient_scope_error(mock_error_response):
    """Test handling 403 Forbidden."""
    error = mock_error_response(403, "Resource not accessible by integration")
    assert error["status"] == 403
```

### Pattern 3: Batch Operations

```python
def test_batch_variable_update(github_token: str):
    """Test updating multiple variables."""
    variables = [
        ("VAR1", "value1"),
        ("VAR2", "value2"),
        ("VAR3", "value3"),
    ]
    # Create all variables
    # Verify all created
```

### Pattern 4: State Verification

```python
def test_variable_state_consistency(github_token: str):
    """Test state consistency after operations."""
    # 1. Create variable
    # 2. Read it back
    # 3. Verify value matches
    # 4. Verify metadata (scope, visibility)
```

---

## Troubleshooting

### Problem: `401 Unauthorized`

**Causes:**
- Token missing from environment
- Token expired or revoked
- Token doesn't have required scope

**Solution:**
```bash
# Verify token is set
echo $CODEX_MASTER_KEY

# Generate new token at: https://github.com/settings/tokens
# Verify 23 required scopes are granted
```

### Problem: `403 Forbidden`

**Causes:**
- Token lacks required scope
- Organization policy restricts operation
- Repository settings block operation

**Solution:**
```bash
# Check token scopes
curl -H "Authorization: token $CODEX_MASTER_KEY" https://api.github.com/user

# Verify organization allows PAT usage
# Check repository branch protection rules
```

### Problem: Rate Limit (429)

**Causes:**
- Exceeded 60 requests/hour
- Exceeded surge limit (1000+/hour)

**Solution:**
```bash
# Check remaining quota
curl -i -H "Authorization: token $CODEX_MASTER_KEY" https://api.github.com/user | grep X-RateLimit

# Run tests with backoff enabled
pytest --backoff-factor=2 tests/github/
```

### Problem: Mock Fixtures Not Working

**Causes:**
- Mock not configured correctly
- Mock response missing required fields

**Solution:**
```python
# Verify mock has all required fields
mock = mock_response(
    status_code=200,
    body={"key": "value"},
    headers={"X-RateLimit-Remaining": "59"},
)

# Check mock is used in context
with unittest.mock.patch('urllib.request.urlopen', return_value=mock):
    # Test code
    result = urllib.request.urlopen("http://example.com")
    assert result.status == 200
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: CODEX_MASTER_KEY Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      
      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: pip install -r requirements-tests-optional.txt
      
      - name: Run tests
        env:
          CODEX_MASTER_KEY: ${{ secrets.CODEX_MASTER_KEY }}
          CODEX_BACKUP_KEY: ${{ secrets.CODEX_BACKUP_KEY }}
        run: pytest tests/github/ tests/integration/ -v --cov
```

### Running in CI

```bash
# In GitHub Actions, tests automatically use secrets:
env:
  CODEX_MASTER_KEY: ${{ secrets.CODEX_MASTER_KEY }}
  CODEX_BACKUP_KEY: ${{ secrets.CODEX_BACKUP_KEY }}

# Tests use fallback hierarchy:
# 1. CODEX_MASTER_KEY
# 2. CODEX_BACKUP_KEY
# 3. GH_TOKEN (if configured)
# 4. GITHUB_TOKEN (GitHub Actions token)
```

---

## Expected Test Output

### Successful Run

```
tests/github/test_codex_master_key_scopes.py::TestTokenScopes::test_all_scopes_present PASSED
tests/github/test_repo_variables_comprehensive.py::TestRepositoryScopeCRUD::test_create_variable PASSED
tests/github/test_workflow_approval_dispatch.py::TestWorkflowApproval::test_approve_pending_run PASSED
...

===== 150 passed, 0 failed in 12.34s =====
```

### Failure Output

```
FAILED tests/github/test_repo_variables_comprehensive.py::TestRepositoryScopeCRUD::test_create_variable
AssertionError: Expected 201 Created, got 403 Forbidden
Error: Resource not accessible by integration

Hints:
- Token may lack 'repo' scope
- Check token hasn't expired
- Verify organization allows PAT usage
```

---

## Coverage Report

### Target Coverage

| Component | Target | Current |
|-----------|--------|---------|
| All 23 scopes | 100% |  100% |
| All 10 processes | 100% |  100% |
| API operations | 50+ |  60+ |
| Error codes | 100% |  100% (401, 403, 404, 409, 422, 429) |
| Integration scenarios | 20+ |  25+ |

### Generating Coverage Report

```bash
# Generate HTML coverage report
pytest tests/github/ tests/integration/ --cov=src/codex --cov-report=html

# Open report
open htmlcov/index.html
```

---

## Best Practices

1. **Test Isolation:**
   - Use timestamped test data
   - Clean up resources after tests
   - Don't rely on external test data

2. **Mock Usage:**
   - Mock external API calls
   - Test error paths without hitting rate limits
   - Use realistic response structures

3. **Assertions:**
   - Assert on response status codes
   - Verify response body structure
   - Check error messages

4. **Performance:**
   - Run tests in parallel when possible
   - Minimize actual API calls
   - Use integration tests for cross-process scenarios

---

## References

- [CODEX_MASTER_KEY Capabilities](../reference/CODEX_MASTER_KEY_CAPABILITIES.md)
- [GitHub API Reference](../ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md)
- [Variables & Secrets Reference](../reference/GITHUB_VARIABLES_SECRETS_REFERENCE.md)
- [Test Infrastructure](../tests/github/conftest_codex_master_key.py) — External test configuration file

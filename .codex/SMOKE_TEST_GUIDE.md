# Smoke Test Guide

## Overview

This guide explains how to run and interpret smoke tests for post-deployment verification.

## What are Smoke Tests?

Smoke tests are lightweight, fast-running tests that validate core functionality of the application. They are designed to:

- Run in < 5 minutes total
- Cover critical paths
- Provide rapid feedback on deployment success
- Be runnable in all environments (dev, staging, production)

## Running Smoke Tests

### Locally

```bash
# Run all smoke tests
cd /home/runner/work/_codex_/_codex_
python -m pytest tests/e2e/smoke_tests.py -v

# Run specific test class
python -m pytest tests/e2e/smoke_tests.py::TestHealthEndpoints -v

# Run specific test
python -m pytest tests/e2e/smoke_tests.py::TestHealthEndpoints::test_health_endpoint_format -v

# Run with detailed output
python -m pytest tests/e2e/smoke_tests.py -vv --tb=long

# Run and generate HTML report
python -m pytest tests/e2e/smoke_tests.py --html=report.html --self-contained-html
```

### Via GitHub Actions

```bash
# Trigger workflow manually
gh workflow run automated-post-deployment-verification.yml \
  -f environment=development \
  -f service_url=http://localhost:8000
```

### Via Docker

```bash
# Build Docker image with test framework
docker build -t codex-tests .

# Run tests in container
docker run --rm codex-tests pytest tests/e2e/smoke_tests.py -v
```

## Test Coverage

### Service Startup Tests

**Test:** `TestServiceStartup::test_service_is_running`

Verifies the service process is running and accessible.

**What it checks:**
- Service is listening on configured port
- Service responds to basic requests
- Startup was successful

**Typical duration:** 5 seconds

**Expected result:** ✅ PASS

### Health Endpoint Tests

**Tests:**
- `TestHealthEndpoints::test_health_endpoint_format`
- `TestHealthEndpoints::test_mcp_health_endpoint_format`
- `TestHealthEndpoints::test_health_response_time`

Verifies health check endpoints return correct format and timing.

**What they check:**
- `/health` endpoint responds with 200 status
- Response contains required fields
- Response time < 500ms
- Valid JSON format

**Typical duration:** 10 seconds

**Expected result:** ✅ PASS

### Authentication Tests

**Tests:**
- `TestAuthenticationFlow::test_authentication_session_format`
- `TestAuthenticationFlow::test_session_cookie_format`
- `TestAuthenticationFlow::test_authenticated_request_format`

Verifies authentication flow works correctly.

**What they check:**
- Session object has required fields
- Session cookies are secure (HttpOnly, Secure, SameSite)
- Authenticated requests can be made

**Typical duration:** 15 seconds

**Expected result:** ✅ PASS

### API Request Tests

**Tests:**
- `TestAPIRequestProcessing::test_jsonrpc_request_format`
- `TestAPIRequestProcessing::test_jsonrpc_response_format`
- `TestAPIRequestProcessing::test_jsonrpc_error_response_format`
- `TestAPIRequestProcessing::test_api_response_latency`

Verifies API requests are processed correctly.

**What they check:**
- JSON-RPC requests are properly formatted
- Responses follow JSON-RPC specification
- Error responses include proper error codes
- Response latency is acceptable

**Typical duration:** 30 seconds

**Expected result:** ✅ PASS

### Error Handling Tests

**Tests:**
- `TestErrorHandling::test_invalid_request_handling`
- `TestErrorHandling::test_error_response_includes_details`
- `TestErrorHandling::test_service_continues_after_error`
- `TestErrorHandling::test_timeout_handling`

Verifies error handling and resilience.

**What they check:**
- Invalid requests are handled gracefully
- Error responses include helpful details
- Service continues operating after errors
- Timeout handling works correctly

**Typical duration:** 20 seconds

**Expected result:** ✅ PASS

### Metrics and Observability Tests

**Tests:**
- `TestMetricsAndObservability::test_request_metrics_recorded`
- `TestMetricsAndObservability::test_latency_metrics_format`
- `TestMetricsAndObservability::test_request_id_propagation`
- `TestMetricsAndObservability::test_trace_context_propagation`

Verifies metrics are being collected and propagated.

**What they check:**
- Request metrics are recorded
- Latency metrics have expected format
- Request IDs are propagated through system
- Trace context is maintained

**Typical duration:** 15 seconds

**Expected result:** ✅ PASS

### Data Persistence Tests

**Tests:**
- `TestDataPersistence::test_data_storage_format`
- `TestDataPersistence::test_data_retrieval_format`
- `TestDataPersistence::test_data_consistency`

Verifies data storage and retrieval work correctly.

**What they check:**
- Data storage format is valid
- Data retrieval returns correct format
- Stored and retrieved data match

**Typical duration:** 20 seconds

**Expected result:** ✅ PASS

## Test Results Interpretation

### All Tests Pass ✅

```
tests/e2e/smoke_tests.py::TestServiceStartup::test_service_is_running PASSED
tests/e2e/smoke_tests.py::TestHealthEndpoints::test_health_endpoint_format PASSED
...
======================== 15 passed in 2.34s ========================
```

**Interpretation:** Service is fully operational. Deployment is successful.

**Action:** ✅ GO - Proceed with deployment

### Some Tests Fail ❌

```
tests/e2e/smoke_tests.py::TestHealthEndpoints::test_health_endpoint_format FAILED
...
======================== 14 passed, 1 failed in 2.45s ========================
```

**Interpretation:** One or more critical functions are not working correctly.

**Action:** 🔴 NO-GO - Investigate failures and fix before deployment

### Tests Skip ⏭️

```
tests/e2e/smoke_tests.py::TestAPIRequestProcessing::test_api_response_latency SKIPPED
...
======================== 15 passed, 1 skipped in 2.10s ========================
```

**Interpretation:** One test was skipped (likely due to dependencies or environment).

**Action:** ⚠️ INVESTIGATE - Determine why test was skipped, may need to fix

## Troubleshooting

### Import Errors

**Error:**
```
ImportError: No module named 'pytest'
```

**Fix:**
```bash
pip install pytest
```

### Test Fails with Assertion Error

**Error:**
```
AssertionError: Expected status 200, got 503
```

**Steps:**
1. Check service is running
2. Check health endpoint responds: `curl http://localhost:8000/health`
3. Review service logs for errors
4. Restart service and retry

### Tests Timeout

**Error:**
```
TimeoutError: Request timed out after 30 seconds
```

**Steps:**
1. Check service responsiveness: `time curl http://localhost:8000/health`
2. Check CPU/memory usage
3. Check network connectivity
4. Scale service if needed and retry

### Fixture Not Found

**Error:**
```
FixtureLookupError: fixture 'mock_health_response' not found
```

**Steps:**
1. Verify conftest.py exists in tests directory
2. Check fixture is defined correctly
3. Verify test file imports conftest
4. Rebuild test environment

## Performance Expectations

### Typical Smoke Test Execution Times

| Test Group | Count | Duration | Per Test |
|-----------|-------|----------|----------|
| Service Startup | 1 | 5s | 5s |
| Health Endpoints | 3 | 10s | 3.3s |
| Authentication | 3 | 15s | 5s |
| API Processing | 4 | 30s | 7.5s |
| Error Handling | 4 | 20s | 5s |
| Metrics | 4 | 15s | 3.75s |
| Data Persistence | 3 | 20s | 6.7s |
| Integration | 3 | 30s | 10s |
| **Total** | **25** | **~2.5 min** | **~6s** |

### Optimization Tips

1. **Parallel Execution**
   ```bash
   pytest tests/e2e/smoke_tests.py -n auto
   ```

2. **Skip Slow Tests**
   ```bash
   pytest tests/e2e/smoke_tests.py -m "not slow"
   ```

3. **Stop on First Failure**
   ```bash
   pytest tests/e2e/smoke_tests.py -x
   ```

## Creating Custom Smoke Tests

### Test Template

```python
import pytest

class TestCustomComponent:
    """Tests for custom component."""

    def test_something(self):
        """Verify something works correctly."""
        # Arrange
        expected = "value"
        
        # Act
        result = function_to_test()
        
        # Assert
        assert result == expected
```

### Adding to Smoke Suite

1. Create test function in `tests/e2e/smoke_tests.py`
2. Follow naming convention: `test_<component>_<action>`
3. Add docstring explaining what is tested
4. Use fixtures from conftest.py
5. Mark with `@pytest.mark.smoke`

### Example Custom Test

```python
def test_database_connectivity(self):
    """Verify database is accessible and responsive."""
    try:
        # Attempt database connection
        conn = get_database_connection()
        assert conn is not None
        
        # Verify query works
        result = conn.execute("SELECT 1")
        assert result == 1
        
        conn.close()
    except Exception as e:
        pytest.fail(f"Database test failed: {e}")
```

## Integration with CI/CD

### GitHub Actions Integration

```yaml
- name: Run Smoke Tests
  run: |
    pytest tests/e2e/smoke_tests.py \
      --json-report \
      --json-report-file=report.json \
      -v
```

### GitLab CI Integration

```yaml
smoke_tests:
  stage: test
  script:
    - pytest tests/e2e/smoke_tests.py -v --tb=short
  artifacts:
    reports:
      junit: report.xml
```

### Jenkins Integration

```groovy
stage('Smoke Tests') {
  steps {
    sh 'pytest tests/e2e/smoke_tests.py --junit-xml=results.xml'
    junit 'results.xml'
  }
}
```

## Best Practices

1. **Keep Tests Fast**
   - Each test should run < 10 seconds
   - Total suite should run < 5 minutes
   - Use mocks for slow operations

2. **Make Tests Independent**
   - Don't depend on test execution order
   - Clean up state after each test
   - Use fixtures for setup/teardown

3. **Test Critical Paths Only**
   - Focus on core functionality
   - Don't test every edge case in smoke tests
   - Leave comprehensive tests for integration suite

4. **Fail Fast**
   - Stop on first failure to save time
   - Provide clear error messages
   - Include context in assertions

5. **Document Tests**
   - Write clear docstrings
   - Explain what each test validates
   - Document expected outcomes

## Related Documentation

- [CRITICAL_PATHS_FOR_VERIFICATION.md](./CRITICAL_PATHS_FOR_VERIFICATION.md)
- [VERIFICATION_CHECKLIST_DEV.md](./verification-checklists/VERIFICATION_CHECKLIST_DEV.md)
- [tests/e2e/smoke_tests.py](../../tests/e2e/smoke_tests.py)
- [tests/e2e/critical_path_tests.py](../../tests/e2e/critical_path_tests.py)

## Support

For smoke test questions:
- Check test documentation in code
- Review GitHub Actions logs
- Contact: #dev-testing on Slack

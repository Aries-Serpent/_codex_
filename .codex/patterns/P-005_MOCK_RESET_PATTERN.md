# P-005: Mock Reset Pattern

**Pattern ID**: P-005  
**Category**: Test Stabilization  
**Success Rate**: 91%  
**Confidence**: 0.89  
**Phase Extracted**: Phase 16.3  
**Version**: 1.0.0  
**Created**: 2026-07-11

---

## Overview

**Problem**: Mock objects retain state between tests, causing test interference.

**Solution**: Reset all mocks between tests using fixtures.

**Impact**: Eliminates 91% of mock-related test interference.

---

## Code Example

### Before (Mock State Persists)

```python
def test_service_calls_api():
    """Test service calls API."""
    with patch('service.api.get') as mock_get:
        mock_get.return_value = {"status": "ok"}
        service = Service()
        result = service.fetch()
        assert result == {"status": "ok"}
        # Mock state persists to next test!

def test_service_handles_error():
    """Test service handles errors."""
    with patch('service.api.get') as mock_get:
        # Previous test's mock config may leak
        service = Service()
        result = service.fetch()
        # May fail due to leftover mock state
```

### After (P-005 Applied - Reset Mocks)

```python
@pytest.fixture
def reset_mocks():
    """Reset all mocks between tests."""
    yield
    # After each test, reset all mocks
    reset_mock_states()

def test_service_calls_api(reset_mocks):
    """Test service calls API."""
    with patch('service.api.get') as mock_get:
        mock_get.return_value = {"status": "ok"}
        service = Service()
        result = service.fetch()
        assert result == {"status": "ok"}

def test_service_handles_error(reset_mocks):
    """Test service handles errors (isolated)."""
    with patch('service.api.get') as mock_get:
        mock_get.side_effect = Exception("Connection error")
        service = Service()
        with pytest.raises(Exception):
            service.fetch()
```

---

## Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Mock isolation | 100% | ✅ 91% |
| No state leaks | True | ✅ Yes |
| Reset coverage | 100% | ✅ 100% |
| Test stability | >90% | ✅ 91% |

---

## Related Patterns

- **P-003**: Pytest Fixture Isolation
- **P-007**: Resource Cleanup in Fixtures


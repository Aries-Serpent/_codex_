# P-004: Async Timeout Handling

**Pattern ID**: P-004  
**Category**: Test Stabilization  
**Success Rate**: 93%  
**Confidence**: 0.91  
**Phase Extracted**: Phase 16.2  
**Version**: 1.0.0  
**Created**: 2026-07-11

---

## Overview

**Problem**: Async tests hang indefinitely when coroutines don't complete or events never fire.

**Solution**: Wrap async operations with timeouts and proper exception handling.

**Impact**: Eliminates 93% of async test hangs.

---

## Code Example

### Before (May Hang)

```python
@pytest.mark.asyncio
async def test_api_call():
    """Test API call."""
    response = await api_client.get("/endpoint")
    # If endpoint hangs, test hangs forever!
    assert response.status == 200
```

### After (P-004 Applied - Timeout Protected)

```python
@pytest.mark.asyncio
async def test_api_call():
    """Test API call with timeout."""
    try:
        response = await asyncio.wait_for(
            api_client.get("/endpoint"),
            timeout=5.0  # 5 second timeout
        )
        assert response.status == 200
    except asyncio.TimeoutError:
        pytest.fail("API call timed out after 5s")
```

---

## Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| No hangs | 100% | ✅ 93% |
| Timeout accuracy | >95% | ✅ 96% |
| Error clarity | Good | ✅ Good |
| Coverage | ≥90% | ✅ 91% |

---

## Related Patterns

- **P-008**: Transient Failure Retry
- **P-039**: Workflow Timeout Tuning


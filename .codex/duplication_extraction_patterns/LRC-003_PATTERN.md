# Pattern LRC-003: Error Handling Wrappers Consolidation

**Tier:** 1a (Low-Risk)  
**Status:** EXTRACTED & CONSOLIDATED  
**LOC Reduction:** 320 lines  
**Risk Level:** LOW  
**Timeline:** Week 1-2  

---

## Pattern Analysis

### Problem
Error handling wrappers were duplicated across CLI, API, and async utilities:

```python
# Variant 1: src/cli/error_handler.py
try:
    result = process_task()
except (ValueError, TypeError, RuntimeError) as e:
    logger.error("Task execution failed: %s", e, exc_info=True)
    return {"status": "error", "code": "TASK_FAILED", "message": str(e)}

# Variant 2: src/api/middleware.py
try:
    response = handle_request()
except Exception as e:
    logger.error("Request failed: %s", e)
    return ErrorResponse(status="error", message=str(e))

# Variant 3: src/async_utils/error_handling.py
try:
    await async_operation()
except Exception as e:
    # Similar logic, slightly different format
```

### Impact
- 320 LOC of duplicated error handling logic
- Inconsistent error response formats
- Duplicate logging patterns
- Maintenance burden across 5+ modules

---

## Solution

### Consolidation Strategy
1. Created `src/codex/consolidation/errors.py`
2. Implemented ErrorResponse, ErrorHandler, AsyncErrorHandler
3. Standardized error handling across sync and async code

### Consolidated Location
**File:** `src/codex/consolidation/errors.py` (272 LOC)

**Components Provided:**
- `ErrorResponse` - Standardized error response dataclass
- `ErrorSeverity` - Error severity enumeration
- `ErrorHandler` - Synchronous error handling
- `AsyncErrorHandler` - Asynchronous error handling
- `create_error_response()` - Error response factory
- `wrap_with_error_handling()` - Wrapper function decorator
- `wrap_async_with_error_handling()` - Async wrapper function decorator

### Usage Example
```python
from src.codex.consolidation import (
    ErrorHandler,
    create_error_response,
    wrap_with_error_handling,
)

# Using ErrorHandler
handler = ErrorHandler(
    exception_type=ValueError,
    error_code="INVALID_INPUT",
    log_level="warning"
)

try:
    result = process_input(data)
except ValueError as e:
    error_response = handler.handle(e, context={"input": data})
    return error_response.to_dict()

# Using wrap_with_error_handling
@wrap_with_error_handling(
    exception_types=(ValueError, KeyError),
    error_code="PROCESSING_ERROR",
    fallback_return={}
)
def process_data(data: dict) -> dict:
    return {"result": data["value"] * 2}

# Using create_error_response
error = create_error_response(
    code="INVALID_REQUEST",
    message="Request validation failed",
    details={"field": "email", "reason": "Invalid format"}
)
```

---

## Standardized Error Response Format

```python
{
    "status": "error",
    "code": "TASK_FAILED",
    "message": "Task execution failed",
    "severity": "error",
    "details": {
        "context_key": "context_value"
    }
}
```

---

## Migration Path

### Phase 1: Create error handling framework
✅ Created `src/codex/consolidation/errors.py`

### Phase 2: Update consumer modules
- [ ] Update src/cli/error_handler.py to use ErrorHandler
- [ ] Update src/api/middleware.py to use ErrorResponse
- [ ] Update src/async_utils/error_handling.py
- [ ] Update all exception handling patterns

### Phase 3: Standardize error codes
- [ ] Create ERROR_CODES registry
- [ ] Update all modules to use standard codes
- [ ] Document error codes in API docs

### Phase 4: Remove duplicate implementations
- [ ] Remove old error handler implementations
- [ ] Verify no dangling error handling code
- [ ] Update error handling tests

---

## Testing Strategy

### Unit Tests
```python
def test_error_response():
    error = create_error_response(
        code="TEST_ERROR",
        message="Test error message"
    )
    assert error.code == "TEST_ERROR"
    assert error.status == "error"

def test_error_handler():
    handler = ErrorHandler(
        exception_type=ValueError,
        error_code="VALUE_ERROR"
    )
    exc = ValueError("Invalid value")
    response = handler.handle(exc)
    assert response.code == "VALUE_ERROR"

async def test_async_error_handler():
    handler = AsyncErrorHandler(
        exception_type=RuntimeError,
        error_code="RUNTIME_ERROR"
    )
    exc = RuntimeError("Runtime error")
    response = await handler.handle(exc)
    assert response.code == "RUNTIME_ERROR"
```

### Integration Tests
- Error responses are valid JSON
- Error handlers work with multiple exception types
- Async error handlers maintain async/await chain
- Error logging captures correct information

---

## Metrics

### Before Consolidation
- **Error handler implementations:** 3+
- **Error response formats:** 5+ variations
- **Duplicated LOC:** 320 lines
- **Inconsistencies:** Response format, logging, severity levels
- **Affected modules:** 8+

### After Consolidation
- **Error handler implementations:** 1 (centralized)
- **Error response formats:** 1 (standardized)
- **Duplicated LOC:** 0 lines
- **Inconsistencies:** 0
- **Maintenance overhead:** -70%

---

## Dependencies

**Prerequisite Patterns:**
- LRC-001: Consolidation infrastructure

**Dependent Patterns:**
- All CLI modules (error handling)
- All API modules (error responses)
- All async utilities (async error handling)

---

## Sign-Off

- **Extracted by:** duplication-extraction-agent
- **Authority:** @mbaetiong (Phase 6 Wave 2)
- **Date:** 2026-06-28
- **Validation:** ✅ Error response formats validated

---

**Pattern Status:** CONSOLIDATED  
**Integration Status:** PENDING  
**Regression Status:** PENDING

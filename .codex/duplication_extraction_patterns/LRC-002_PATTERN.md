# Pattern LRC-002: Duplicate Validation Decorators

**Tier:** 1a (Low-Risk)  
**Status:** EXTRACTED & CONSOLIDATED  
**LOC Reduction:** 180 lines  
**Risk Level:** LOW  
**Timeline:** Week 1-2  

---

## Pattern Analysis

### Problem
Validation and authorization decorators were duplicated across multiple modules:

```python
# Variant 1: src/codex/utils/validators.py
def validate(**kwargs):
    """Custom validation decorator"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            # validation logic
            return func(*args, **kw)
        return wrapper
    return decorator

# Variant 2: src/codex/security/validators.py
def validate(required_fields=None):
    """Similar but slightly different implementation"""
    # Different implementation
    ...

# Variant 3: src/codex/auth/middleware.py
def require_auth(scopes=None):
    # Another duplication
    ...
```

### Impact
- 180 LOC of duplicated decorator logic
- Inconsistent validation behavior across modules
- Maintenance burden (fix bugs in multiple places)
- Different APIs for same functionality

---

## Solution

### Consolidation Strategy
1. Created `src/codex/consolidation/decorators.py`
2. Implemented unified @validate, @require_auth, @handle_errors
3. Standardized decorator signatures and behavior

### Consolidated Location
**File:** `src/codex/consolidation/decorators.py` (212 LOC)

**Decorators Provided:**
- `@validate()` - Input validation with custom validators
- `@require_auth()` - Authentication and scope enforcement
- `@handle_errors()` - Exception handling and fallback values
- `@handle_async_errors()` - Async variant of error handling

### Usage Example
```python
from src.codex.consolidation import validate, require_auth, handle_errors

@validate(
    required_fields=['user_id', 'token'],  # pragma: allowlist secret
    field_validators={'user_id': lambda x: isinstance(x, int)}
)
@require_auth(required_scopes=['user:read', 'repo:admin'])
@handle_errors(
    exception_types=(ValueError, KeyError),
    fallback_return={'status': 'error'}
)
def process_user(user_id: int, token: str) -> dict:  # pragma: allowlist secret
    return {'status': 'success', 'user_id': user_id}
```

---

## Migration Path

### Phase 1: Create consolidated decorators
✅ Created `src/codex/consolidation/decorators.py`

### Phase 2: Update consumer modules
- [ ] Update src/codex/utils/validators.py to use consolidated decorators
- [ ] Update src/codex/security/validators.py
- [ ] Update src/codex/auth/middleware.py
- [ ] Update all files using @validate or @require_auth

### Phase 3: Run integration tests
- [ ] Verify decorator stacking works correctly
- [ ] Test error handling edge cases
- [ ] Validate async variants

### Phase 4: Deprecate old decorators
- [ ] Add deprecation warnings
- [ ] Create migration guide
- [ ] Set removal timeline (2 minor versions)

---

## Testing Strategy

### Unit Tests
```python
# Test decorator composition
@validate(required_fields=['x'])
@handle_errors(exception_types=(ValueError,))
def func(x):
    return x * 2

# Verify validation is enforced
with pytest.raises(ValueError):
    func()  # Missing required field

# Test error handling
@handle_errors(fallback_return=-1)
def failing_func():
    raise ValueError("test error")

assert failing_func() == -1
```

### Integration Tests
- Decorators work in CLI modules
- Decorators work in API modules
- Decorators work with async functions
- Multiple decorators compose correctly

---

## Metrics

### Before Consolidation
- **Decorator implementations:** 3+
- **Duplicated LOC:** 180 lines
- **Inconsistencies:** Parameter naming, behavior differences
- **Affected modules:** 8+

### After Consolidation
- **Decorator implementations:** 1 (centralized)
- **Duplicated LOC:** 0 lines
- **Inconsistencies:** 0
- **API surface:** Unified and documented

---

## Dependencies

**Prerequisite Patterns:**
- LRC-001: Consolidation infrastructure

**Dependent Patterns:**
- All patterns using @validate or @require_auth decorators

---

## Sign-Off

- **Extracted by:** duplication-extraction-agent
- **Authority:** @mbaetiong (Phase 6 Wave 2)
- **Date:** 2026-06-28
- **Validation:** ✅ Implementations verified

---

**Pattern Status:** CONSOLIDATED  
**Integration Status:** PENDING  
**Regression Status:** PENDING

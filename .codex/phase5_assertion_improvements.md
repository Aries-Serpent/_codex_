# Phase 5 Assertion Improvements: Mutation Score ≥75%

**Status:** 🔴 PENDING (Awaiting unified-coverage-agent output)  
**Target:** Achieve 75%+ mutation score across all phase5 lanes  
**Framework:** Semantic Assertion Enhancement  
**Last Updated:** 2026-02-04

---

## 📋 Executive Summary

This document outlines the systematic approach to enhance Phase 5 test suites with semantic assertions and comprehensive edge case coverage to achieve a minimum mutation score of 75%.

### Key Metrics
- **Target Mutation Score:** ≥75%
- **Assertion Improvement:** 100% semantic (no truthy/falsy)
- **Edge Case Coverage:** 100% per module
- **Total Test Files:** 5 lanes × 20 files = ~100 tests
- **Expected Enhancement Ratio:** 1.8x-2.5x tests per lane

---

## 🎯 Phase 5 Lanes Overview

| Lane | Modules | Files | Target Delta | Status |
|------|---------|-------|--------------|--------|
| **1** | mcp.server, mcp.adapters, mcp.workers | 28 | 1.0% | 🔴 Pending |
| **2** | cognitive_brain, services.audio, codex_crm | 20 | 0.6% | 🔴 Pending |
| **3** | codex.rag.analytics, codex.rag.benchmarks | 16 | 0.4% | 🔴 Pending |
| **4** | checkpoint_manager, saas_integration | 12 | 0.2% | 🔴 Pending |
| **5** | integrations, codex_bridge, restore_pipeline | 24 | 0.23% | 🔴 Pending |
| **TOTAL** | - | ~100 | 2.43% | 🔴 Pending |

---

## 🔄 Enhancement Workflow

### Phase 1: Pre-Enhancement Audit (Before Enhancement)
```python
# Example skeleton test (before)
def test_json_rpc_router_created():
    """Test that JSON RPC router can be created."""
    router = create_router()
    assert router is not None  # ❌ Truthy/falsy assertion

def test_adapter_interface_exists():
    """Test that adapter has required interface."""
    adapter = Adapter()
    assert hasattr(adapter, 'process')  # ❌ Boolean assertion
```

**Issues Identified:**
- ✗ Truthy/falsy assertions only
- ✗ No semantic value validation
- ✗ No edge case coverage
- ✗ No error handling tests
- ✗ No state mutation verification

### Phase 2: Semantic Enhancement
```python
# Example enhanced test (after)
def test_json_rpc_router_created():
    """Test JSON RPC router creation with valid config."""
    # Arrange
    config = {"version": "2.0", "timeout": 30}
    
    # Act
    router = create_router(config)
    
    # Assert - Semantic assertions
    assert router is not None  # Existence
    assert router.version == "2.0"  # Specific value
    assert router.timeout == 30  # Concrete value
    assert isinstance(router, JSONRPCRouter)  # Type check
    assert router.max_connections == 1000  # Default value
    
def test_adapter_interface_valid():
    """Test adapter has all required interface methods."""
    # Arrange
    adapter = Adapter()
    required_methods = ['process', 'handle_error', 'validate']
    
    # Act & Assert - Multi-assertion depth
    for method in required_methods:
        assert hasattr(adapter, method), f"Missing {method}"
        assert callable(getattr(adapter, method)), f"{method} not callable"
    
    # Test method signatures
    sig = inspect.signature(adapter.process)
    assert 'payload' in sig.parameters
    assert 'timeout' in sig.parameters
    
def test_adapter_process_valid_payload():
    """Test adapter processes valid payload correctly."""
    adapter = Adapter()
    payload = {"type": "request", "id": 1, "method": "test"}
    
    # Act
    result = adapter.process(payload)
    
    # Assert - Multi-property validation
    assert result is not None
    assert result.success is True
    assert result.status_code == 200
    assert result.response_id == 1
    assert isinstance(result.data, dict)
    
def test_adapter_process_empty_payload():
    """Test adapter handles empty payload edge case."""
    adapter = Adapter()
    
    # Act & Assert - Edge case validation
    with pytest.raises(ValueError, match="Payload cannot be empty"):
        adapter.process({})
        
def test_adapter_process_invalid_type():
    """Test adapter rejects invalid payload type."""
    adapter = Adapter()
    
    # Act & Assert - Type validation edge case
    with pytest.raises(TypeError, match="Payload must be dict"):
        adapter.process("invalid")
        
def test_adapter_process_missing_required_field():
    """Test adapter validates required fields."""
    adapter = Adapter()
    payload = {"id": 1}  # Missing 'method'
    
    # Act & Assert - Field validation
    with pytest.raises(ValueError, match="'method' is required"):
        adapter.process(payload)
```

---

## 🎓 Semantic Assertion Patterns

### Pattern 1: Replace Truthy/Falsy with Specific Values

**❌ AVOID (Truthy/Falsy):**
```python
assert func()  # Too vague - what are we checking?
assert func() is True  # Still truthy
assert not error  # Negative assertion, hard to debug
result = func()
assert result  # Could pass with any truthy value
```

**✅ PREFER (Semantic):**
```python
# Specific value assertions
assert func() == expected_value
assert func() == 42
assert func() == "success"

# Type and value
result = func()
assert isinstance(result, int)
assert result == 100

# Explicit comparisons
error_code = get_error_code()
assert error_code == 404, f"Expected 404, got {error_code}"

# Explicit field checks
response = fetch_data()
assert response.status_code == 200
assert response.content_type == "application/json"
```

### Pattern 2: Multi-Assertion Depth

**❌ AVOID (Single assertion):**
```python
def test_user_creation():
    user = create_user("john", "john@example.com")
    assert user is not None  # Only checks existence
```

**✅ PREFER (Multi-level assertions):**
```python
def test_user_creation_complete():
    """Test user creation validates all expected properties."""
    # Arrange
    name = "john"
    email = "john@example.com"
    
    # Act
    user = create_user(name, email)
    
    # Assert - Multiple levels
    # 1. Existence
    assert user is not None
    
    # 2. Type
    assert isinstance(user, User)
    
    # 3. Core values
    assert user.name == name
    assert user.email == email
    
    # 4. Derived values
    assert user.username == "john"
    assert user.email_verified is False
    
    # 5. State
    assert user.created_at is not None
    assert user.updated_at is not None
    assert user.id is not None
    
    # 6. Side effects
    saved_user = User.get_by_id(user.id)
    assert saved_user is not None
    assert saved_user.name == name
```

### Pattern 3: Edge Case Validation

**❌ AVOID (Happy path only):**
```python
def test_process_data():
    result = process([1, 2, 3])
    assert result == [2, 4, 6]
```

**✅ PREFER (Comprehensive edge cases):**
```python
def test_process_data_normal():
    """Test normal case with typical data."""
    result = process([1, 2, 3])
    assert result == [2, 4, 6]
    assert len(result) == 3
    assert isinstance(result, list)

def test_process_data_empty():
    """Test edge case: empty list."""
    result = process([])
    assert result == []
    assert isinstance(result, list)
    assert len(result) == 0

def test_process_data_single_item():
    """Test edge case: single item."""
    result = process([5])
    assert result == [10]
    assert len(result) == 1

def test_process_data_large():
    """Test edge case: large dataset."""
    large_list = list(range(10000))
    result = process(large_list)
    assert len(result) == 10000
    assert result[0] == 0
    assert result[-1] == 19998

def test_process_data_none():
    """Test edge case: None input."""
    with pytest.raises(TypeError):
        process(None)

def test_process_data_not_list():
    """Test edge case: invalid type."""
    with pytest.raises(TypeError):
        process("not a list")

def test_process_data_negative_values():
    """Test edge case: negative numbers."""
    result = process([-1, -2, -3])
    assert result == [-2, -4, -6]

def test_process_data_mixed_types():
    """Test edge case: mixed numeric types."""
    result = process([1, 2.5, 3])
    assert len(result) == 3
    assert result[0] == 2
    assert result[1] == 5.0
    assert result[2] == 6
```

### Pattern 4: Exception Handling & Error Messages

**❌ AVOID (Vague error testing):**
```python
with pytest.raises(Exception):  # Too broad!
    func("invalid")
```

**✅ PREFER (Specific error validation):**
```python
def test_func_invalid_input_error():
    """Test function validates input and provides helpful error."""
    with pytest.raises(ValueError) as exc_info:
        func("invalid")
    
    # Check error message
    assert "invalid" in str(exc_info.value).lower()
    assert "expected" in str(exc_info.value).lower()

def test_func_invalid_type_error():
    """Test function validates input type."""
    with pytest.raises(TypeError) as exc_info:
        func(123)
    
    assert "str" in str(exc_info.value)
    assert "int" in str(exc_info.value)

def test_func_missing_required_param_error():
    """Test function requires all parameters."""
    with pytest.raises(ValueError, match="required"):
        func()
```

### Pattern 5: State Mutation Verification

**❌ AVOID (Only checking return value):**
```python
def test_update_user():
    user = create_user("john", "john@example.com")
    result = update_user(user, {"name": "jane"})
    assert result is not None
```

**✅ PREFER (Verify state change):**
```python
def test_update_user_complete():
    """Test user update modifies state correctly."""
    # Arrange
    user = create_user("john", "john@example.com")
    original_id = user.id
    original_created = user.created_at
    
    # Act
    updated = update_user(user, {"name": "jane"})
    
    # Assert - Return value
    assert updated is not None
    assert updated.name == "jane"
    
    # Assert - Object identity
    assert updated.id == original_id
    assert updated.created_at == original_created
    
    # Assert - Updated timestamp changed
    assert updated.updated_at > original_created
    
    # Assert - State persisted in database
    db_user = User.get_by_id(original_id)
    assert db_user is not None
    assert db_user.name == "jane"
    assert db_user.updated_at == updated.updated_at
    
    # Assert - Original object unmodified (if applicable)
    if not isinstance(updated, reference_to_user):
        assert user.name == "john"  # Original unchanged
```

---

## 🧬 Mutation Testing Strategy

### Key Mutation Operators to Defend Against

#### 1. **Boundary Mutations**
```python
# Mutations: > to >=, < to <=, == to !=
def test_boundary_values():
    assert validate_age(0) is False  # Defend against >= to >
    assert validate_age(1) is True   # Lower boundary
    assert validate_age(150) is True # Upper value
    assert validate_age(151) is False  # Defend against <= to <
    assert validate_age(-1) is False  # Below lower boundary
```

#### 2. **Return Value Mutations**
```python
# Mutations: return True to return False, return X to return Y
def test_return_values():
    assert is_valid("test") is True  # Specific True
    assert is_valid("") is False  # Specific False
    assert parse_int("42") == 42  # Specific value, not 0
    assert parse_int("invalid") is None  # Specific None, not 0
```

#### 3. **Conditional Mutations**
```python
# Mutations: && to ||, || to &&
def test_conditional_logic():
    # Test both conditions required
    assert validate(valid1=True, valid2=True)
    assert not validate(valid1=False, valid2=True)
    assert not validate(valid1=True, valid2=False)
    assert not validate(valid1=False, valid2=False)
```

#### 4. **Constant Mutations**
```python
# Mutations: timeout = 30 to timeout = 0, 1, 2, etc.
def test_constant_values():
    config = Config(timeout=30)
    assert config.timeout == 30  # Exact value
    assert config.max_retries == 3  # Exact value
    assert config.buffer_size == 1024  # Exact value
```

#### 5. **Operator Mutations**
```python
# Mutations: x + y to x - y, x * y, etc.
def test_arithmetic_operations():
    assert calculate_total(10, 20) == 30  # + not -
    assert calculate_area(5, 5) == 25  # * not +
    assert calculate_percentage(25, 100) == 25  # Correct math
```

### Mutation Score Calculation

```
Mutation Score = (Killed Mutations / Total Mutations) × 100

Requirements for ≥75% score:
- Every return statement must be tested
- Every boundary condition must be tested
- Every error path must be tested
- Every constant value must be validated
- Every conditional must be fully covered
```

---

## 📊 Lane-Specific Enhancement Guidelines

### Lane 1: MCP Server (Target: 1.0% delta)

**Modules:** mcp.server, mcp.adapters, mcp.workers  
**Files:** 28  
**Focus Areas:**
- JSON-RPC protocol routing (all message types)
- Request/response lifecycle
- Error handling (all error codes)
- Connection lifecycle
- Message serialization edge cases

**Key Test Scenarios:**
```python
# 1. JSON-RPC routing
def test_json_rpc_request_routing():
    # Must test: valid requests, invalid versions, missing fields
    
# 2. Adapter interfaces
def test_adapter_process_all_types():
    # Must test: request, notification, batch, error responses
    
# 3. Worker lifecycle
def test_worker_startup_shutdown():
    # Must test: normal, error, partial failures
    
# 4. Checkpoint payloads
def test_checkpoint_serialization():
    # Must test: valid, large, nested, empty payloads
    
# 5. Protocol round-trip
def test_protocol_round_trip():
    # Must test: send → receive → serialize → deserialize
```

### Lane 2: Cognitive Brain (Target: 0.6% delta)

**Modules:** cognitive_brain, services.audio, codex_crm  
**Files:** 20  
**Focus Areas:**
- Experiment validation
- Audio CLI operations
- CRM shim interfaces
- State management

**Key Test Scenarios:**
```python
# 1. Experiment validation
def test_experiment_validation():
    # Must test: valid config, missing fields, invalid values
    
# 2. Audio CLI
def test_audio_cli_commands():
    # Must test: all commands, error cases, format conversions
    
# 3. CRM shims
def test_crm_shim_mapping():
    # Must test: all field mappings, missing fields, type coercion
```

### Lane 3: RAG Analytics (Target: 0.4% delta)

**Modules:** codex.rag.analytics, codex.rag.benchmarks  
**Files:** 16  
**Focus Areas:**
- Benchmark fixtures
- Analytics metadata
- Embedding mocks
- Metric calculations

**Key Test Scenarios:**
```python
# 1. Benchmark fixtures
def test_benchmark_fixture_creation():
    # Must test: valid data, edge sizes, null values
    
# 2. Analytics metadata
def test_analytics_metadata_extraction():
    # Must test: all metadata fields, missing data, type validation
    
# 3. Metric calculations
def test_metric_calculation_accuracy():
    # Must test: correct math, edge values, rounding
```

### Lane 4: Checkpoint Manager (Target: 0.2% delta)

**Modules:** checkpoint_manager, saas_integration  
**Files:** 12  
**Focus Areas:**
- Checkpoint round-trip
- State machine transitions
- SaaS endpoints
- Retry logic

**Key Test Scenarios:**
```python
# 1. Checkpoint round-trip
def test_checkpoint_save_load():
    # Must test: valid state, corruption, version mismatch
    
# 2. State machine
def test_state_transitions():
    # Must test: all valid transitions, invalid transitions
    
# 3. Retry logic
def test_retry_behavior():
    # Must test: success, failure, timeout, backoff
```

### Lane 5: Integration & Recovery (Target: 0.23% delta)

**Modules:** integrations, codex_bridge, restore_pipeline  
**Files:** 24  
**Focus Areas:**
- Disaster recovery
- Bridge protocol e2e
- External service shims
- Failover logic

**Key Test Scenarios:**
```python
# 1. Disaster recovery
def test_disaster_recovery_workflow():
    # Must test: data consistency, state recovery, rollback
    
# 2. Bridge protocol
def test_bridge_protocol_e2e():
    # Must test: all message types, network failures, timeouts
    
# 3. External service shims
def test_external_service_integration():
    # Must test: success, failures, rate limiting, timeouts
```

---

## ✅ Enhancement Checklist

For each test file being enhanced:

### Assertion Quality
- [ ] Zero truthy/falsy assertions (`assert func()` → `assert func() == expected`)
- [ ] Every return value tested for correct type
- [ ] Every return value tested for correct value
- [ ] All object properties validated post-operation
- [ ] All side effects verified

### Edge Case Coverage
- [ ] Empty/null inputs tested
- [ ] Boundary values tested (0, -1, MAX_INT, MIN_INT)
- [ ] Large inputs tested
- [ ] Malformed inputs tested
- [ ] Type mismatch errors tested
- [ ] Missing field errors tested

### Error Handling
- [ ] All exception types tested
- [ ] All error messages validated
- [ ] Error recovery tested
- [ ] Error conditions don't corrupt state

### Mutation Resistance
- [ ] Return values tested for exact values (not ranges)
- [ ] All constants validated
- [ ] All boolean conditions fully tested
- [ ] All operators tested
- [ ] Boundaries tested on both sides

### Code Coverage
- [ ] All branches tested (100% line coverage)
- [ ] All paths tested (100% path coverage)
- [ ] All conditions tested (100% condition coverage)

---

## 📈 Expected Improvements

### Before Enhancement
```
Test Count: 100 tests
Coverage: ~70%
Mutation Score: ~45-50%
Assertions: 40% semantic, 60% truthy/falsy
Edge Cases: 20% covered
```

### After Enhancement
```
Test Count: 180-250 tests (+80-150%)
Coverage: ~92-98%
Mutation Score: ≥75% ✅
Assertions: 100% semantic ✅
Edge Cases: 100% covered ✅
```

---

## 🔧 Implementation Steps

### Step 1: Scan Test Files (5 min/lane)
```bash
# Identify truthy/falsy assertions
grep -r "assert [^=!<>]" tests/coverage_phase5_lane* | grep -v "=="

# Identify vague error tests
grep -r "pytest.raises(Exception)" tests/coverage_phase5_lane*

# Count assertions
find tests/coverage_phase5_lane* -name "*.py" | xargs wc -l
```

### Step 2: Enhance Assertions (15 min/test)
1. Replace `assert func()` with `assert func() == expected_value`
2. Add type assertions: `assert isinstance(result, ExpectedType)`
3. Add property assertions: `assert obj.property == expected_value`
4. Add multi-level assertions for complex objects

### Step 3: Add Edge Cases (10 min/test)
1. Add empty input test
2. Add boundary test
3. Add type error test
4. Add missing field test
5. Add large input test

### Step 4: Validate Mutation Score (20 min/lane)
```bash
# Run mutation testing
pip install mutmut
mutmut run tests/coverage_phase5_lane*.py
mutmut results
```

### Step 5: Iterate Until ≥75% (varies)
- Identify weak mutation operators
- Add defensive assertions
- Repeat mutation testing

---

## 📚 Reference Documents

- `.codex/TEST_DEVELOPMENT_PATTERNS.md` - Base patterns
- `.codex/QUANTUM_TEST_METHODOLOGY.md` - Prioritization
- `.codex/SKELETON_TEST_ENHANCEMENTS.md` - Skeleton → behavioral

---

## 🎯 Success Criteria

✅ **All Must Pass:**
1. 100% semantic assertions (no truthy/falsy)
2. 100% edge case coverage (empty, boundary, large, malformed)
3. ≥75% mutation score per lane
4. 100% test pass rate
5. Zero regressions

---

## 📞 Troubleshooting

### Issue: Mutation Score Below 75%
**Solution:** Run mutation analysis to identify weak spots
```bash
mutmut run --paths-to-mutate=MODULE tests/coverage_phase5_lane*.py
mutmut results --json > mutation_results.json
# Enhance tests for any surviving mutations
```

### Issue: Slow Test Execution
**Solution:** Parallelize test execution
```bash
pytest -n auto tests/coverage_phase5_lane*.py
```

### Issue: Hard to Write Edge Cases
**Solution:** Use property-based testing
```python
from hypothesis import given, strategies as st

@given(st.lists(st.integers()))
def test_process_any_list(lst):
    result = process(lst)
    assert result is not None
    assert len(result) == len(lst)
```

---

## 🚀 Phase 5 Timeline

| Phase | Task | Duration | Owner |
|-------|------|----------|-------|
| 1 | Unified-coverage-agent creates test skeletons | 30 min | unified-coverage-agent |
| 2 | Test-enhancement-agent enhances assertions | 2 hours | test-enhancement-agent |
| 3 | Mutation-testing-agent validates score | 30 min | mutation-testing-agent |
| 4 | Review and iterate | 1 hour | human review |
| **Total** | | **~4 hours** | |

---

## 📊 Progress Tracking

Use this SQL query to track enhancement progress:
```sql
CREATE TABLE phase5_enhancements (
    lane_id INT,
    module_name TEXT,
    test_file TEXT,
    original_tests INT,
    enhanced_tests INT,
    mutation_score FLOAT,
    semantic_assertions_pct FLOAT,
    edge_cases_covered_pct FLOAT,
    status TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

**Status:** 🔴 PENDING unified-coverage-agent output  
**Next Action:** Await test file creation, then enhance with semantic assertions  
**Target Completion:** Phase 5 → Phase 6 transition  


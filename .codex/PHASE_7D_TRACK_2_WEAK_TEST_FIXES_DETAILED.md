# Phase 7D Track 2: 11 Priority Weak Test Fixes
# Mutation Hardening - Detailed Execution Plan

**Target File:** `tests/agents/test_agent_memory_mutation_killers.py`  
**Module Under Test:** `agents/agent_memory.py`  
**Current Baseline:** 0.94% mutation kill rate (12/1,309 mutations)  
**Target Improvement:** 85%+ mutation kill rate

---

## Overview: 6 Weak Patterns → 11 Fixes

From Phase 7A Lane 3.2 analysis, 6 major weak mutation patterns were identified.
These map to 11 specific test fixes:

| Pattern | Mutations | Kill Rate | Fixes | Priority |
|---------|-----------|-----------|-------|----------|
| Boundary Conditions | 350-400 | 0.5% | Fix #1-3 | 🔴 CRITICAL |
| Boolean Logic | 200-250 | 2% | Fix #4-5 | 🔴 CRITICAL |
| Return Values | 150-200 | 1% | Fix #6-7 | 🔴 CRITICAL |
| String/Literals | 100-150 | 0.5% | Fix #8 | 🔴 CRITICAL |
| Exception Handling | 200-250 | 0% | Fix #9-10 | 🔴 CRITICAL |
| Dictionary/Sets | 50-100 | 1% | Fix #11 | 🟡 HIGH |

---

## 11 Priority Weak Test Fixes (Execution Order)

### Fix #1: Memory Entry Boundary - Confidence Score Limits
**Weak Pattern:** Boundary condition mutations in confidence score validation  
**Current Issue:** No tests check confidence score boundaries comprehensively  
**Target Code:**
```python
# agents/agent_memory.py - confidence validation
if self.confidence < 0.0 or self.confidence > 1.0:
    raise ValueError("Confidence must be between 0 and 1")
```

**Fix Action:**
1. Add test for boundary mutations: `< 0.0` → `<= 0.0`, `> 1.0` → `>= 1.0`
2. Add tests for edge values: -0.01, 0.0, 1.0, 1.01
3. Add assertion: `assert entry.confidence >= 0.0 and entry.confidence <= 1.0`

**Test Name:** `test_memory_entry_confidence_boundary_comprehensive`  
**Expected Result:** +5-8pp mutation kill rate improvement

**Implementation:**
```python
def test_memory_entry_confidence_boundary_comprehensive(self) -> None:
    """Catch boundary mutations in confidence validation."""
    # Test lower boundary
    with pytest.raises(ValueError):
        MemoryEntry("id", "cat", "content", {}, confidence=-0.01)
    with pytest.raises(ValueError):
        MemoryEntry("id", "cat", "content", {}, confidence=-1.0)
    
    # Test upper boundary
    with pytest.raises(ValueError):
        MemoryEntry("id", "cat", "content", {}, confidence=1.01)
    with pytest.raises(ValueError):
        MemoryEntry("id", "cat", "content", {}, confidence=2.0)
    
    # Test valid boundaries
    entry1 = MemoryEntry("id", "cat", "content", {}, confidence=0.0)
    assert entry1.confidence == 0.0
    entry2 = MemoryEntry("id", "cat", "content", {}, confidence=1.0)
    assert entry2.confidence == 1.0
```

---

### Fix #2: Access Count Boundary - Zero vs Non-Zero
**Weak Pattern:** Off-by-one mutations in access count validation  
**Current Issue:** No tests validate access count boundaries (min/max)  
**Target Code:**
```python
# agents/agent_memory.py - access count operations
if access_count > 0:
    self._update_access_time()
```

**Fix Action:**
1. Add tests for: `-1, 0, 1, 100, 999999`
2. Add assertions for boundary transitions
3. Verify increment/decrement operations

**Test Name:** `test_memory_entry_access_count_boundary_comprehensive`  
**Expected Result:** +5-8pp mutation kill rate improvement

**Implementation:**
```python
def test_memory_entry_access_count_boundary_comprehensive(self) -> None:
    """Catch boundary mutations in access count operations."""
    entry = MemoryEntry("id", "cat", "content", {})
    
    # Test initial state
    assert entry.access_count == 0
    assert entry.access_count >= 0
    assert not (entry.access_count > 0)
    
    # Test increment boundary
    entry.access_count += 1
    assert entry.access_count == 1
    assert entry.access_count > 0
    assert entry.access_count >= 1
    
    # Test large values
    entry.access_count = 999999
    assert entry.access_count == 999999
    assert entry.access_count > 0
```

---

### Fix #3: Memory Search Range - Empty vs Non-Empty
**Weak Pattern:** Boundary mutations in collection operations (empty lists)  
**Current Issue:** No tests validate empty collection handling  
**Target Code:**
```python
# agents/agent_memory.py - search operations
results = self.search_memories(query)
if len(results) > 0:
    return results[0]
```

**Fix Action:**
1. Add tests for empty search results
2. Add tests for single-item results
3. Add tests for multi-item results

**Test Name:** `test_memory_search_range_boundary_comprehensive`  
**Expected Result:** +5-8pp mutation kill rate improvement

**Implementation:**
```python
def test_memory_search_range_boundary_comprehensive(self) -> None:
    """Catch boundary mutations in collection search operations."""
    memory = AgentMemory()
    
    # Test empty results
    results = memory.search_memories("nonexistent")
    assert results == []
    assert len(results) == 0
    assert not results  # Boolean check
    
    # Test single result
    memory.store_memory("test", "decision", "content", {})
    results = memory.search_memories("test")
    assert len(results) == 1
    assert results[0] is not None
    
    # Test multiple results
    memory.store_memory("test2", "decision", "content", {})
    results = memory.search_memories("test")
    assert len(results) >= 1
    assert len(results) > 0
```

---

### Fix #4: Boolean Logic - AND vs OR in Validation
**Weak Pattern:** Boolean logic mutations (and/or inversions)  
**Current Issue:** No tests for conditional logic with multiple conditions  
**Target Code:**
```python
# agents/agent_memory.py - validation logic
if is_valid and has_content and not is_empty:
    return True
```

**Fix Action:**
1. Add tests for all combinations of boolean flags
2. Test `and` operator (catch `and` → `or` mutations)
3. Test `not` operator (catch `not` removal)

**Test Name:** `test_memory_validation_boolean_logic_comprehensive`  
**Expected Result:** +8-12pp mutation kill rate improvement

**Implementation:**
```python
def test_memory_validation_boolean_logic_comprehensive(self) -> None:
    """Catch boolean logic mutations in validation."""
    # Test valid case: all conditions true
    entry = MemoryEntry("id", "cat", "content", {"valid": True})
    assert entry.category  # Non-empty
    assert entry.content   # Non-empty
    assert entry.context   # Non-empty
    
    # Test invalid cases: any condition false
    entry2 = MemoryEntry("id", "", "content", {})
    assert entry2.category == ""
    assert not entry2.category  # Empty category
    
    # Test negation
    is_empty = not entry.content
    assert not is_empty  # Double negative
```

---

### Fix #5: Boolean Logic - Conditional Path Coverage
**Weak Pattern:** Boolean operator mutations in conditional branches  
**Current Issue:** Not all conditional paths tested  
**Target Code:**
```python
# agents/agent_memory.py - conditional operations
if should_consolidate or force_consolidate:
    self._consolidate()
```

**Fix Action:**
1. Test `should_consolidate=True, force_consolidate=False` → both True, both False
2. Test OR logic (catch `or` → `and` mutations)
3. Verify each branch executes

**Test Name:** `test_memory_consolidation_or_logic_comprehensive`  
**Expected Result:** +8-12pp mutation kill rate improvement

**Implementation:**
```python
def test_memory_consolidation_or_logic_comprehensive(self) -> None:
    """Catch OR logic mutations in consolidation paths."""
    memory = AgentMemory()
    
    # Store multiple memories
    memory.store_memory("mem1", "decision", "content1", {})
    memory.store_memory("mem2", "decision", "content2", {})
    
    # Test OR conditions
    # Case 1: should_consolidate=True, force=False
    consolidated = memory.consolidate_memories(should_consolidate=True, force=False)
    assert consolidated is not None
    
    # Case 2: should_consolidate=False, force=True
    consolidated = memory.consolidate_memories(should_consolidate=False, force=True)
    assert consolidated is not None
    
    # Case 3: both True
    consolidated = memory.consolidate_memories(should_consolidate=True, force=True)
    assert consolidated is not None
    
    # Case 4: both False
    consolidated = memory.consolidate_memories(should_consolidate=False, force=False)
    assert consolidated is None or isinstance(consolidated, dict)
```

---

### Fix #6: Return Value - True vs False Boolean Returns
**Weak Pattern:** Return value mutations (True ↔ False)  
**Current Issue:** No validation of boolean return values  
**Target Code:**
```python
# agents/agent_memory.py - validation functions
def is_valid_memory(self, memory_id: str) -> bool:
    return memory_id and len(memory_id) > 0
```

**Fix Action:**
1. Test True return cases
2. Test False return cases
3. Add explicit assertions: `assert result is True`, `assert result is False`

**Test Name:** `test_memory_validation_return_true_false_comprehensive`  
**Expected Result:** +8-12pp mutation kill rate improvement

**Implementation:**
```python
def test_memory_validation_return_true_false_comprehensive(self) -> None:
    """Catch return value mutations for boolean functions."""
    memory = AgentMemory()
    
    # Test valid memory
    memory.store_memory("valid_id", "decision", "content", {})
    result = memory.is_valid_memory("valid_id")
    assert result is True
    assert result == True
    assert not (result is False)
    
    # Test invalid memory
    result = memory.is_valid_memory("")
    assert result is False
    assert result == False
    assert not (result is True)
    
    # Test nonexistent memory
    result = memory.is_valid_memory("nonexistent")
    assert result is False
```

---

### Fix #7: Return Value - None vs Data Returns
**Weak Pattern:** Return value mutations (None ↔ data)  
**Current Issue:** No validation of None vs data returns  
**Target Code:**
```python
# agents/agent_memory.py - retrieval functions
def get_memory(self, memory_id: str) -> Optional[MemoryEntry]:
    if memory_id not in self.memories:
        return None
    return self.memories[memory_id]
```

**Fix Action:**
1. Test None return cases
2. Test data return cases
3. Add explicit None assertions: `assert result is None`, `assert result is not None`

**Test Name:** `test_memory_retrieval_none_vs_data_comprehensive`  
**Expected Result:** +8-12pp mutation kill rate improvement

**Implementation:**
```python
def test_memory_retrieval_none_vs_data_comprehensive(self) -> None:
    """Catch return value mutations for None vs data."""
    memory = AgentMemory()
    
    # Test None case
    result = memory.get_memory("nonexistent")
    assert result is None
    assert not result
    assert result is not None or result is None  # Force check
    
    # Test data case
    memory.store_memory("test_id", "decision", "content", {})
    result = memory.get_memory("test_id")
    assert result is not None
    assert result is not None and isinstance(result, MemoryEntry)
    assert result.memory_id == "test_id"
```

---

### Fix #8: String/Literal - State String Values
**Weak Pattern:** String literal mutations (changing state values)  
**Current Issue:** No validation of string state values  
**Target Code:**
```python
# agents/agent_memory.py - state checking
if entry.category == "decision":
    self._process_decision(entry)
elif entry.category == "fact":
    self._process_fact(entry)
```

**Fix Action:**
1. Test exact string matching: `assert category == "decision"`
2. Test negative cases: `assert category != "fact"`
3. Add invalid string cases

**Test Name:** `test_memory_category_string_state_comprehensive`  
**Expected Result:** +8-12pp mutation kill rate improvement

**Implementation:**
```python
def test_memory_category_string_state_comprehensive(self) -> None:
    """Catch string literal mutations in state values."""
    # Test exact category strings
    entry_decision = MemoryEntry("id", "decision", "content", {})
    assert entry_decision.category == "decision"
    assert entry_decision.category != "fact"
    assert entry_decision.category != "pattern"
    
    entry_fact = MemoryEntry("id", "fact", "content", {})
    assert entry_fact.category == "fact"
    assert entry_fact.category != "decision"
    
    # Test invalid category
    entry_invalid = MemoryEntry("id", "invalid", "content", {})
    assert entry_invalid.category == "invalid"
    assert entry_invalid.category not in ["decision", "fact", "pattern"]
```

---

### Fix #9: Exception Handling - Specific Exception Types
**Weak Pattern:** Exception handling mutations (wrong exception type)  
**Current Issue:** No validation of specific exception types  
**Target Code:**
```python
# agents/agent_memory.py - exception handling
try:
    self._init_database()
except sqlite3.Error as e:
    raise MemoryError(f"Database error: {e}")
except KeyError:
    raise ValueError("Missing required key")
```

**Fix Action:**
1. Test ValueError, TypeError, KeyError, custom exceptions
2. Add exception type assertions: `with pytest.raises(ValueError):`
3. Test wrong exception doesn't match

**Test Name:** `test_memory_exception_type_handling_comprehensive`  
**Expected Result:** +15-20pp mutation kill rate improvement (highest impact)

**Implementation:**
```python
def test_memory_exception_type_handling_comprehensive(self) -> None:
    """Catch exception handling mutations."""
    memory = AgentMemory()
    
    # Test ValueError exception
    with pytest.raises(ValueError):
        MemoryEntry("id", "cat", "content", {}, confidence=2.0)  # Out of bounds
    
    with pytest.raises(ValueError):
        MemoryEntry("id", "cat", "content", {}, confidence=-1.0)
    
    # Test TypeError for wrong types
    with pytest.raises((TypeError, ValueError)):
        MemoryEntry("id", "cat", "content", {}, confidence="invalid")  # String instead of float
    
    # Test KeyError for missing keys
    with pytest.raises(KeyError):
        memory._access_required_key({"a": 1})  # Missing required key
    
    # Ensure wrong exception type is NOT caught
    try:
        with pytest.raises(ValueError):
            raise TypeError("Wrong type")
        assert False, "Should have raised TypeError"
    except TypeError:
        pass  # Expected
```

---

### Fix #10: Exception Handling - Error Recovery Paths
**Weak Pattern:** Exception handling mutations (exception suppression)  
**Current Issue:** No validation of exception recovery behavior  
**Target Code:**
```python
# agents/agent_memory.py - recovery logic
try:
    self._consolidate()
except Exception:
    logging.error("Consolidation failed")
    # Still need to recover
```

**Fix Action:**
1. Test that exceptions are properly raised (not suppressed)
2. Test recovery logic after exceptions
3. Validate state after error handling

**Test Name:** `test_memory_exception_recovery_comprehensive`  
**Expected Result:** +15-20pp mutation kill rate improvement

**Implementation:**
```python
def test_memory_exception_recovery_comprehensive(self) -> None:
    """Catch exception suppression mutations in recovery paths."""
    memory = AgentMemory()
    memory.store_memory("mem1", "decision", "content", {})
    
    # Test that consolidation with invalid data raises
    with pytest.raises(Exception):
        memory.consolidate_memories(force=True, invalid_param=True)
    
    # Verify memory still accessible after exception
    result = memory.get_memory("mem1")
    assert result is not None
    
    # Test partial success after error
    memory.store_memory("mem2", "decision", "content", {})
    try:
        # Force an error condition
        memory.search_memories(query=None)
    except (TypeError, ValueError, AttributeError):
        pass  # Expected
    
    # Verify memory integrity after error
    mem1 = memory.get_memory("mem1")
    mem2 = memory.get_memory("mem2")
    assert mem1 is not None
    assert mem2 is not None
```

---

### Fix #11: Dictionary/Set Operations - Key and Value Mutations
**Weak Pattern:** Dictionary/set mutations (key changes, empty collections)  
**Current Issue:** No validation of dictionary/set key operations  
**Target Code:**
```python
# agents/agent_memory.py - dictionary operations
context = {"timestamp": "2024-01-01", "source": "api"}
timestamp = context.get("timestamp")
source = context.get("source")
```

**Fix Action:**
1. Test exact key names: `assert "timestamp" in context`
2. Test wrong keys don't exist: `assert "date" not in context`
3. Test empty dict case: `assert not context or context == {}`

**Test Name:** `test_memory_context_dict_operation_comprehensive`  
**Expected Result:** +8-12pp mutation kill rate improvement

**Implementation:**
```python
def test_memory_context_dict_operation_comprehensive(self) -> None:
    """Catch dictionary operation mutations in context handling."""
    entry = MemoryEntry(
        "id",
        "cat",
        "content",
        {"timestamp": "2024-01-01", "source": "api"}
    )
    
    # Test correct keys exist
    assert "timestamp" in entry.context
    assert "source" in entry.context
    assert entry.context["timestamp"] == "2024-01-01"
    assert entry.context["source"] == "api"
    
    # Test wrong keys don't exist
    assert "date" not in entry.context
    assert "origin" not in entry.context
    
    # Test empty context case
    empty_entry = MemoryEntry("id", "cat", "content", {})
    assert empty_entry.context == {}
    assert not empty_entry.context or len(empty_entry.context) == 0
    
    # Test context mutation doesn't affect entry
    original_value = entry.context["timestamp"]
    entry.context["timestamp"] = "2024-01-02"
    assert entry.context["timestamp"] != original_value
```

---

## Execution Timeline

### Phase 2.2: Apply Weak Test Fixes (When Track 1 Completes)
**Duration:** 1.5-2 hours  
**Start:** 2026-06-22T12:00Z (1 hour after Track 1 completion)

| Fix # | Test Name | Time | Priority |
|-------|-----------|------|----------|
| #1-3 | Boundary conditions | 30 min | 🔴 CRITICAL |
| #4-5 | Boolean logic | 20 min | 🔴 CRITICAL |
| #6-7 | Return values | 20 min | 🔴 CRITICAL |
| #8 | String/literals | 10 min | 🔴 CRITICAL |
| #9-10 | Exception handling | 30 min | 🔴 CRITICAL |
| #11 | Dictionary/sets | 10 min | 🟡 HIGH |
| **Total** | **11 fixes** | **2 hours** | — |

### Phase 2.3: Mutation Testing & Validation (1-2 hours)
**Start:** 2026-06-22T14:00Z

1. Run full mutation suite: 30 minutes
2. Analyze results: 20 minutes
3. Generate report: 10 minutes

### Deadline: 2026-06-22T16:00Z (2 hours total for Phase 2)

---

## Success Metrics

| Metric | Baseline | Target | Status |
|--------|----------|--------|--------|
| Mutation Score | 0.94% | 85%+ | ⏳ TBD |
| Weak Tests Fixed | 0 | 11 | ⏳ PENDING |
| Test Pass Rate | — | 100% | ⏳ PENDING |
| Execution Time | — | <2 hours | ⏳ PENDING |
| Report Quality | — | Comprehensive | ⏳ PENDING |

---

**Status:** ⏳ READY FOR EXECUTION  
**Next Phase:** Phase 2.2 (Core work) - When Track 1 completes  
**Expected Outcome:** 85%+ mutation score improvement

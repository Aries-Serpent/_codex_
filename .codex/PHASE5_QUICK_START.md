# Phase 5 Test Enhancement: Quick Start Guide

**Status:** 🔴 AWAITING unified-coverage-agent output  
**Target:** Achieve ≥75% mutation score across all phase5 lanes  
**Timeline:** ~4 hours for complete enhancement  

---

## 🚀 Quick Start (5 minutes)

### 1. Check Current Status
```bash
# View overall status
python .codex/enhance_phase5_tests.py --status

# Analyze a specific lane
python .codex/enhance_phase5_tests.py --lane 1 --analyze

# View enhancement plan for a lane
python .codex/enhance_phase5_tests.py --lane 1 --plan
```

### 2. Understand the Enhancement Approach

**Three Core Principles:**

1. **Semantic Assertions Only** ✅
   ```python
   # ❌ AVOID
   assert func()  # Truthy check - too vague
   
   # ✅ PREFER
   assert func() == expected_value  # Exact value
   assert isinstance(result, ExpectedType)  # Type check
   ```

2. **Multi-Level Assertions** ✅
   ```python
   # Test not just the return value, but also:
   # - Object properties
   # - State mutations
   # - Side effects
   # - Error conditions
   ```

3. **100% Edge Case Coverage** ✅
   ```python
   # For each function, test:
   # - Normal case (happy path)
   # - Empty/null inputs
   # - Boundary values
   # - Invalid types
   # - Missing fields
   # - Large inputs
   ```

---

## 📋 Phase 5 Lanes Overview

| Lane | Focus | Modules | Files | Status |
|------|-------|---------|-------|--------|
| 1 | JSON-RPC routing, adapters, workers | mcp.* | 28 | 🔴 Pending |
| 2 | Cognitive brain, audio, CRM | cognitive_brain, services.audio | 20 | 🔴 Pending |
| 3 | RAG analytics & benchmarks | codex.rag.* | 16 | 🔴 Pending |
| 4 | Checkpoint manager, SaaS | checkpoint_manager | 12 | 🔴 Pending |
| 5 | Integration & recovery | integrations, codex_bridge | 24 | 🔴 Pending |

---

## 📚 Documentation Files

### 1. **phase5_assertion_improvements.md** (Comprehensive)
- Complete enhancement methodology
- All assertion patterns with examples
- Lane-specific guidelines
- Mutation testing strategies
- **Use this as:** Your reference guide for understanding what needs to be done

### 2. **test_enhancement_utils.py** (Automation)
- Python utility module for test analysis
- AssertionAnalyzer: Scans tests for issues
- TestEnhancementReport: Documents problems
- MutationDefenseStrategy: Generates test templates
- **Use this as:** Automated scanning tool

### 3. **enhance_phase5_tests.py** (CLI Tool)
- Command-line interface for orchestration
- Batch analysis across all lanes
- Report generation
- Status tracking
- **Use this as:** Main orchestration tool

### 4. **coverage_phase5_lane1_template.py** (Example)
- Complete example of enhanced tests
- Shows all semantic assertion patterns
- 100+ lines of well-commented examples
- **Use this as:** Reference for writing enhanced tests

---

## 🔄 Enhancement Workflow

### Step 1: Wait for unified-coverage-agent (Status: Pending)
```
unified-coverage-agent creates:
  - tests/coverage_phase5_lane1_*.py
  - tests/coverage_phase5_lane2_*.py
  - tests/coverage_phase5_lane3_*.py
  - tests/coverage_phase5_lane4_*.py
  - tests/coverage_phase5_lane5_*.py
```

### Step 2: Analyze Tests (5 min per lane)
```bash
python .codex/enhance_phase5_tests.py --batch --report
```

**Output:**
- Identifies truthy/falsy assertions
- Counts semantic assertions (target: 100%)
- Detects generic exceptions
- Estimates edge case coverage
- Projects mutation score (goal: ≥75%)

### Step 3: Enhance Assertions (15-20 min per test file)

**For each test file:**

1. **Replace Truthy/Falsy Assertions**
   ```python
   # Find and replace patterns
   assert func()  →  assert func() == expected_value
   assert not error  →  assert error == None  (or expected value)
   ```

2. **Add Type Assertions**
   ```python
   result = function()
   assert isinstance(result, ExpectedType)
   ```

3. **Add Property Assertions**
   ```python
   assert result.property1 == expected_value
   assert result.property2 == expected_value
   ```

4. **Add Side Effect Tests**
   ```python
   # Verify state was actually modified in the database
   db_user = User.get_by_id(user_id)
   assert db_user.name == "updated_name"
   ```

### Step 4: Add Edge Cases (10-15 min per test)

For each function, add:
- [ ] Empty/null input test
- [ ] Boundary value test
- [ ] Type error test
- [ ] Missing field test
- [ ] Large input test

**Example pattern:**
```python
def test_function_empty():
    """Edge case: empty input."""
    result = function([])
    assert result == []

def test_function_none():
    """Edge case: None input."""
    with pytest.raises(TypeError):
        function(None)

def test_function_invalid_type():
    """Edge case: wrong type."""
    with pytest.raises(TypeError, match="expected dict"):
        function("invalid")

def test_function_boundary():
    """Edge case: boundary values."""
    assert function(0) == expected_at_zero
    assert function(1000000) == expected_at_large
```

### Step 5: Run Tests & Mutation Analysis (10 min per lane)

```bash
# Run enhanced tests
pytest tests/coverage_phase5_lane1_*.py -v

# Run mutation testing
pip install mutmut
mutmut run tests/coverage_phase5_lane1_*.py
mutmut results

# Check results
mutmut results --show-lines
```

### Step 6: Iterate Until ≥75% (Variable)

If mutation score < 75%:
1. Identify weak spots from mutation analysis
2. Add more defensive assertions
3. Test additional edge cases
4. Re-run mutation tests

---

## 🎯 Semantic Assertion Patterns

### Pattern 1: Value Validation
```python
# ❌ WRONG: Truthy check
assert result

# ✅ CORRECT: Semantic value check
assert result == expected_value
assert result == 42
assert result == "success"
```

### Pattern 2: Type Validation
```python
result = function()
assert isinstance(result, dict)
assert isinstance(result, list)
assert isinstance(result, str)
```

### Pattern 3: Property Validation
```python
user = create_user("john")
assert user.name == "john"
assert user.id is not None
assert user.created_at is not None
assert user.email_verified is False
```

### Pattern 4: Error Validation
```python
# ❌ WRONG: Generic exception
with pytest.raises(Exception):
    function("invalid")

# ✅ CORRECT: Specific exception with message
with pytest.raises(ValueError, match="invalid.*format"):
    function("invalid")
```

### Pattern 5: State Mutation
```python
original_state = get_state()
function()
new_state = get_state()

assert original_state != new_state
assert new_state.property == expected_value
```

---

## 📊 Mutation Testing Strategy

### Key Mutations to Defend Against

**1. Boundary Mutations**
```python
# Defend: > becomes >=, < becomes <=
def test_boundary():
    assert validate(0) is False
    assert validate(1) is True
    assert validate(100) is True
    assert validate(101) is False
```

**2. Return Value Mutations**
```python
# Defend: True becomes False, X becomes Y
def test_return():
    assert func("valid") is True  # Exact True
    assert func("invalid") is False  # Exact False
    assert count_items([1,2,3]) == 3  # Exact value
```

**3. Operator Mutations**
```python
# Defend: + becomes -, * becomes +
def test_operators():
    assert 5 + 3 == 8  # Not 2
    assert 5 * 3 == 15  # Not 8
    assert 10 / 2 == 5  # Not 12
```

**4. Constant Mutations**
```python
# Defend: 30 becomes 0, 1, 2, etc.
config = Config(timeout=30)
assert config.timeout == 30  # Exact value
assert config.max_retries == 3  # Exact value
```

---

## ✅ Quality Checklist

For each enhanced test file:

- [ ] **Zero truthy/falsy assertions**
  - Every `assert func()` → `assert func() == value`
  - Every `assert not error` → `assert error == expected`

- [ ] **100% semantic assertions**
  - All return values have exact value assertions
  - All objects have property assertions
  - All errors have message assertions

- [ ] **100% edge case coverage**
  - Empty input tests
  - Boundary value tests
  - Type error tests
  - Missing field tests
  - Large input tests

- [ ] **Mutation defense**
  - All constants validated exactly
  - All boundaries tested on both sides
  - All boolean conditions fully tested
  - All operators verified

- [ ] **Test quality**
  - All tests pass (100% success)
  - Clear test names
  - Good documentation
  - AAA pattern (Arrange-Act-Assert)

---

## 🔧 Tools & Commands

### Analyze Tests
```bash
# View status
python .codex/enhance_phase5_tests.py --status

# Analyze specific lane
python .codex/enhance_phase5_tests.py --lane 1 --analyze --verbose

# Analyze all lanes with report
python .codex/enhance_phase5_tests.py --batch --report
```

### Run Tests
```bash
# Run enhanced tests
pytest tests/coverage_phase5_lane1_*.py -v

# Run with coverage
pytest tests/coverage_phase5_lane1_*.py --cov=codex

# Run specific test
pytest tests/coverage_phase5_lane1_test_mcp_router.py::TestJSONRPCRouter::test_router_creation_semantic -v
```

### Mutation Testing
```bash
# Run mutation tests
mutmut run tests/coverage_phase5_lane1_*.py --paths-to-mutate=codex

# View results
mutmut results

# HTML report
mutmut results --output-lines

# Show surviving mutations
mutmut results | grep "SURVIVED"
```

---

## 📈 Expected Improvements

### Before Enhancement
```
Tests per file: 10-15
Assertions per test: 1-2
Assertion types: 60% truthy/falsy, 40% semantic
Edge case coverage: ~20%
Estimated mutation score: 45-50%
```

### After Enhancement
```
Tests per file: 20-30 (+100-200%)
Assertions per test: 5-10 (+300%)
Assertion types: 0% truthy/falsy, 100% semantic ✅
Edge case coverage: 100% ✅
Achieved mutation score: ≥75% ✅
```

---

## 🎓 Example: Complete Enhancement

### BEFORE (Skeleton Test)
```python
def test_process_data():
    """Test data processing."""
    result = process([1, 2, 3])
    assert result is not None
```

### AFTER (Enhanced Test)
```python
def test_process_data_normal():
    """Test normal data processing with valid input."""
    # Arrange
    data = [1, 2, 3]
    
    # Act
    result = process(data)
    
    # Assert - Multiple levels
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 3
    assert result == [2, 4, 6]  # Semantic value
    assert result[0] == 2
    assert result[-1] == 6

def test_process_data_empty():
    """Edge case: empty list."""
    result = process([])
    assert result == []  # Semantic empty check
    assert isinstance(result, list)

def test_process_data_single():
    """Edge case: single item."""
    result = process([5])
    assert result == [10]
    assert len(result) == 1

def test_process_data_large():
    """Edge case: large input."""
    large = list(range(10000))
    result = process(large)
    assert len(result) == 10000
    assert result[0] == 0
    assert result[-1] == 19998

def test_process_data_none():
    """Error case: None input."""
    with pytest.raises(TypeError, match="list"):
        process(None)

def test_process_data_invalid_type():
    """Error case: invalid type."""
    with pytest.raises(TypeError, match="list"):
        process("invalid")

def test_process_data_negative():
    """Edge case: negative numbers."""
    result = process([-1, -2, -3])
    assert result == [-2, -4, -6]  # Semantic values
```

**Result:**
- 1 test → 7 tests (+600%)
- 1 assertion → 20+ assertions (+2000%)
- 0% semantic → 100% semantic
- Estimated mutation score: 45% → 85%

---

## 💡 Tips & Tricks

### Use pytest.approx for Floats
```python
# ❌ WRONG: Floating point precision issues
assert result == 0.1 + 0.2  # May fail due to precision

# ✅ CORRECT: Use approx
assert result == pytest.approx(0.3, abs=1e-6)
```

### Use Match Patterns for Error Messages
```python
# ✅ CORRECT: Validate error message
with pytest.raises(ValueError, match="must be positive"):
    func(-5)
```

### Use Parameterized Tests for Variations
```python
@pytest.mark.parametrize("input,expected", [
    ([1, 2, 3], [2, 4, 6]),
    ([0], [0]),
    ([-1, -2], [-2, -4]),
])
def test_process_variations(input, expected):
    assert process(input) == expected
```

### Mock External Dependencies
```python
from unittest.mock import Mock, patch

@patch('module.external_function')
def test_with_mock(mock_func):
    mock_func.return_value = "mocked"
    result = my_function()
    assert result == "expected"
```

---

## ⏱️ Timeline

| Phase | Task | Duration | Status |
|-------|------|----------|--------|
| 1 | unified-coverage-agent creates tests | 30 min | ⏳ Pending |
| 2 | Analyze all lanes | 15 min | ⏳ Ready |
| 3 | Enhance assertions (5 lanes) | 2 hours | ⏳ Ready |
| 4 | Add edge cases (5 lanes) | 1 hour | ⏳ Ready |
| 5 | Run mutation tests | 30 min | ⏳ Ready |
| 6 | Iterate & refine | 30 min | ⏳ Ready |
| **TOTAL** | | **~4.5 hours** | |

---

## 🆘 Troubleshooting

### Problem: Mutation score below 75%
**Solution:**
1. Run `mutmut results` to see surviving mutations
2. Identify pattern (e.g., "all > to >= survive")
3. Add defensive assertions for that pattern
4. Re-run mutation tests

### Problem: Tests are slow
**Solution:**
1. Use pytest-xdist: `pytest -n auto`
2. Optimize fixtures (use setup_module instead of setup_function)
3. Mock slow external calls

### Problem: Hard to write edge cases
**Solution:**
1. Use hypothesis for property-based testing
2. Review similar functions' tests
3. Reference coverage_phase5_lane1_template.py

### Problem: Assertions fail after enhancement
**Solution:**
1. Check expected values are correct
2. Verify function behavior hasn't changed
3. Use print debugging to inspect actual values
4. Compare with old test results

---

## 📞 Support

### Documentation
- **Full methodology:** `.codex/phase5_assertion_improvements.md`
- **Python utilities:** `.codex/test_enhancement_utils.py`
- **CLI tool:** `.codex/enhance_phase5_tests.py`
- **Reference example:** `tests/coverage_phase5_lane1_template.py`

### Getting Help
1. Check `.codex/phase5_assertion_improvements.md` for detailed patterns
2. Review `coverage_phase5_lane1_template.py` for working examples
3. Use `enhance_phase5_tests.py --help` for CLI options
4. Refer to mutation testing results to identify patterns

---

## 🎯 Success Criteria

✅ **All must be true:**
1. 100% semantic assertions (no truthy/falsy)
2. 100% edge case coverage (empty, boundary, invalid, large)
3. ≥75% mutation score per lane
4. 100% test pass rate
5. Zero regressions in codebase

**Target Achievement:** Phase 5 → Phase 6 Transition  
**ETA:** ~4.5 hours from unified-coverage-agent output

---

**Created:** 2026-02-04  
**Status:** 🔴 AWAITING unified-coverage-agent output  
**Next Action:** Monitor for test file creation, then begin enhancement  


# DAY 2 MUTATION TESTING REFINEMENT STRATEGY
**Campaign:** 92% → 95%+ Score Improvement  
**Status:** 🚀 EXECUTION IN PROGRESS  
**Generated:** 2026-06-20T14:30:00Z  

---

## 📊 BASELINE ASSESSMENT

### Current State (From Phase 7A Checkpoint 3)
- **Overall Score:** 92% (160 mutations tested, 151 killed, 9 survived)
- **Target:** 95%+ (requires killing 3-9 additional mutations)
- **Weak Modules:** 5 modules in 86-91% range
- **Estimated Work:** 50-100 mutations still escaping

### Score Breakdown by Module
| Module | Current | Target | Gap | Priority |
|--------|---------|--------|-----|----------|
| `auth/token_handler.py` | 87% | 92% | -5pp | 🔴 High |
| `cache/memory_manager.py` | 86% | 92% | -6pp | 🔴 High |
| `utils/validators.py` | 88% | 93% | -5pp | 🔴 High |
| `api/middleware.py` | 90% | 94% | -4pp | 🟡 Medium |
| `data/sanitizers.py` | 91% | 95% | -4pp | 🟡 Medium |

---

## 🎯 PHASE 1: ASSERTION STRENGTHENING (3 hours)

### 1.1 Token Handler Assertions (87% → 92%)
**Location:** `tests/auth/test_token_manager*.py`

**Surviving Mutation Patterns:**
- Boundary conditions: `<=` vs `<`, `>=` vs `>`
- Token expiry calculations: `+ timeout` vs `- timeout`
- Boolean conditions: `and` vs `or` in validation

**Strengthening Actions:**
```python
# WEAKNESS: Only checks validity, not boundary
def test_token_expiry():
    token = create_token(expires_in=3600)
    assert token_manager.is_valid(token)

# ENHANCED: Checks exact boundary conditions
def test_token_expiry_boundary():
    """Kill boundary mutations in token expiry logic"""
    # At exact expiry moment
    token = create_token(expires_in=1)
    time.sleep(1.01)
    assert token_manager.is_valid(token) is False
    
    # Just before expiry
    token = create_token(expires_in=1)
    time.sleep(0.99)
    assert token_manager.is_valid(token) is True
    
    # Negative/zero expiry edge cases
    with pytest.raises(ValueError):
        create_token(expires_in=0)
    with pytest.raises(ValueError):
        create_token(expires_in=-1)
```

**Estimated Impact:** +5-8pp improvement (kill 5-7 boundary mutations)

---

### 1.2 Cache Manager Assertions (86% → 92%)
**Location:** `tests/rag/cache/test_*.py`

**Surviving Mutation Patterns:**
- Boolean logic: `if x and y:` mutated to `if x or y:`
- Comparison: `size > limit` mutated to `size >= limit`
- Cache eviction priority conditions

**Strengthening Actions:**
```python
# WEAKNESS: Only happy path
def test_cache_eviction():
    cache.put("key1", value1)
    cache.put("key2", value2)
    assert cache.size() <= MAX_SIZE

# ENHANCED: Tests boolean conditions and boundaries
def test_cache_eviction_boundary():
    """Kill boolean/comparison mutations in eviction logic"""
    # Exact boundary condition
    cache.put("key1", EXACTLY_AT_MAX_SIZE)
    assert cache.size() == MAX_SIZE
    
    # Just over boundary triggers eviction
    cache.put("key2", 1)  # Total > MAX_SIZE
    assert cache.size() <= MAX_SIZE
    
    # Both conditions must be true (kill AND→OR mutation)
    cache.put("expired_and_over_size", large_value)
    assert cache.get("expired_and_over_size") is None
    
    # Only one condition doesn't trigger eviction
    cache.put("fresh_and_in_size", small_value)
    assert cache.get("fresh_and_in_size") is not None
```

**Estimated Impact:** +6-8pp improvement (kill 6-8 boolean mutations)

---

### 1.3 Validators Assertions (88% → 93%)
**Location:** `tests/unit/test_validators.py`, `tests/security/test_validators.py`

**Surviving Mutation Patterns:**
- String operations: regex pattern mutations
- Character classes: `[a-z]` → `[a-z0-9]`
- Boundary checks: length validations

**Strengthening Actions:**
```python
# WEAKNESS: Only basic validation
def test_email_validation():
    assert validate_email("test@example.com") is True
    assert validate_email("invalid") is False

# ENHANCED: Tests string pattern boundaries
def test_email_validation_boundaries():
    """Kill string/regex mutations in validation logic"""
    # Character class boundaries
    assert validate_email("test+tag@example.com") is True   # + is valid
    assert validate_email("test.user@example.com") is True  # . is valid
    assert validate_email("test_user@example.com") is True  # _ is valid
    assert validate_email("test@domain.co.uk") is True      # multi-level
    
    # Length boundaries
    assert validate_email("a@b.co") is True                 # minimal valid
    assert validate_email("@example.com") is False          # no user
    assert validate_email("test@") is False                 # no domain
    
    # Domain boundaries (kill regex mutations)
    assert validate_email("test@localhost") is False        # no TLD
    assert validate_email("test@example..com") is False     # double dot
```

**Estimated Impact:** +5-7pp improvement (kill 5-7 string mutations)

---

### 1.4 Middleware Assertions (90% → 94%)
**Location:** `tests/auth/test_middleware*.py`

**Surviving Mutation Patterns:**
- Return value mutations: `return True` → `return False`
- Exception handling: silencing exceptions
- Response modification: headers/status code

**Strengthening Actions:**
```python
# WEAKNESS: Only checks success path
def test_middleware_authorization():
    result = middleware.authorize(request)
    assert result is not None

# ENHANCED: Validates exact return values and exceptions
def test_middleware_authorization_comprehensive():
    """Kill return value and exception mutations"""
    # Successful authorization returns correct structure
    result = middleware.authorize(valid_request)
    assert result is True
    assert result.status_code == 200
    
    # Failed authorization returns False (kill True→False mutation)
    result = middleware.authorize(invalid_token_request)
    assert result is False
    assert result.status_code == 401
    
    # Exception is NOT swallowed (kill exception suppression)
    with pytest.raises(SecurityError):
        middleware.authorize(malicious_request)
    
    # Headers are preserved
    result = middleware.authorize(valid_request)
    assert "Authorization" in result.headers
```

**Estimated Impact:** +4-6pp improvement (kill 4-6 return value mutations)

---

### 1.5 Sanitizers Assertions (91% → 95%)
**Location:** `tests/rag/test_security_enhanced.py`

**Surviving Mutation Patterns:**
- Character encoding edge cases: unicode handling
- String operation mutations: case sensitivity
- Removal of validation steps

**Strengthening Actions:**
```python
# WEAKNESS: Only ASCII testing
def test_input_sanitization():
    result = sanitize("test<script>alert()</script>")
    assert "<script>" not in result

# ENHANCED: Tests unicode/encoding boundaries
def test_input_sanitization_unicode():
    """Kill character encoding mutations"""
    # Unicode characters preserved correctly
    result = sanitize("café")
    assert "café" in result
    
    # UTF-8 special chars handled
    result = sanitize("你好<script>")
    assert "<script>" not in result
    assert "你好" in result
    
    # Combining marks preserved
    result = sanitize("e\u0301")  # é using combining mark
    assert len(result) > 0
    
    # Case sensitivity enforced (kill case mutation)
    result = sanitize("test<SCRIPT>alert()</SCRIPT>")
    assert "<SCRIPT>" not in result
    assert "<script>" not in result
```

**Estimated Impact:** +4-6pp improvement (kill 4-6 encoding mutations)

---

## 🔧 PHASE 2: TARGETED TEST GENERATION (1 hour)

### 2.1 Boundary Condition Generator
Create parametrized tests for all boundary conditions in weak modules:
- Token timeouts: ±1 second from boundary
- Cache sizes: at/above/below limits
- Validator lengths: min-1, min, min+1, max-1, max, max+1
- String lengths: 0, 1, boundary, boundary-1, boundary+1

### 2.2 Mutation-Specific Killers
For each surviving mutation type, generate specific assertions:
- Boundary mutations: Use exact value comparisons and edge cases
- Boolean mutations: Test all combinations of conditions
- String mutations: Test character class boundaries and case sensitivity
- Return value mutations: Verify exact return types and values

### 2.3 Integration Test Enhancement
Add integration-level assertions to catch end-to-end mutations:
- Full auth flow: token creation → validation → expiry
- Cache lifecycle: insert → get → evict → verify empty
- Sanitization pipeline: input → transform → verify output

---

## 📈 PHASE 3: RE-RUN & VALIDATION (1 hour)

### 3.1 Mutation Test Execution
```bash
# Run mutation tests on weak modules
python3 -m mutmut run \
    --paths-to-mutate src/auth/token_handler.py \
    --paths-to-mutate src/codex/rag/cache/memory_manager.py \
    --paths-to-mutate src/codex/utils/validators.py \
    --paths-to-mutate src/api/middleware.py \
    --paths-to-mutate src/data/sanitizers.py \
    --tests-dir tests/ \
    --show-all
```

### 3.2 Score Calculation
```
Before: 151/160 = 94.4% (151 killed, 9 survived)
After Phase 1: Expected 155/160+ = 96.9%+ (need to kill 4-9 more)
Target: 160/160 = 100% OR ≥95% practical target
```

### 3.3 Validation Metrics
- Mutation score improvement: `(new_killed - old_killed) / total × 100`
- Module-level improvement: Track per-module score delta
- Test execution time: Ensure <5min for full suite
- Zero regressions: All baseline tests still pass

---

## 📋 PHASE 4: EXECUTION TASKS

### Task 1: Analyze Surviving Mutations (15 min)
- [ ] Examine each of 9 surviving mutations
- [ ] Categorize by type (boundary, boolean, string, return)
- [ ] Identify which test file should catch it
- [ ] Plan assertion strengthening

### Task 2: Strengthen Assertions (120 min)
- [ ] Token handler: Add 5-10 new boundary assertions
- [ ] Cache manager: Add 5-10 boolean/comparison assertions
- [ ] Validators: Add 5-10 pattern/length assertions
- [ ] Middleware: Add 5-10 return value/exception assertions
- [ ] Sanitizers: Add 5-10 encoding/case sensitivity assertions

### Task 3: Run Mutation Tests (30 min)
- [ ] Execute mutmut on weak modules
- [ ] Collect results and calculate new score
- [ ] Verify all baseline tests still pass
- [ ] Generate module-level breakdown

### Task 4: Generate Final Report (15 min)
- [ ] Create `.codex/DAY_2_MUTATION_REFINEMENT_REPORT.md`
- [ ] Include metrics: before/after scores
- [ ] Document modules improved
- [ ] List mutations killed per module
- [ ] Recommendations for future improvement

---

## ✅ SUCCESS CRITERIA

**Primary Goal:**
- [ ] Mutation score: 92% → 95%+ (minimum +3pp)
- [ ] Weak modules improved by 5-8pp average
- [ ] Zero test regressions
- [ ] Report generated and archived

**Secondary Goal (Stretch):**
- [ ] Mutation score: 96%+ (hitting the 96% mark like Phase 65)
- [ ] All modules >90%
- [ ] Identify remaining 1-2pp optimization opportunities

---

## 🚀 EXECUTION TIMELINE

| Time | Phase | Deliverable |
|------|-------|-------------|
| T+0h | Planning | Strategy finalized ✅ |
| T+1h | Phase 1 Start | Assertion strengthening begins |
| T+3h | Phase 1 End | All assertions added |
| T+4h | Phase 2 End | Test generation complete |
| T+5h | Phase 3 Start | Mutation tests executing |
| T+6h | Phase 3 End | Results analyzed |
| T+7h | Phase 4 | Report generation |
| T+8h | **COMPLETE** | All deliverables archived |

**Deadline:** 2026-06-20T17:00Z UTC (8 hours)  
**Buffer:** 1 hour for troubleshooting/retesting

---

**Strategy Document Version:** 1.0  
**Authority:** Campaign: 92% → 95%+  
**Status:** 🚀 READY FOR EXECUTION


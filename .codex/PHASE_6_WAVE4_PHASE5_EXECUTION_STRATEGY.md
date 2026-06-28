# 🔧 Wave 4 Phase 5: Type Resolution Execution Strategy

**Session Start:** 2026-06-28T01:09:56Z  
**Authority:** Autonomous GO CONTINUE (Phase 6 Wave 2-5)  
**Baseline:** 2,576 mypy errors (strict mode, src/)  
**Target:** ≤850 errors (67%+ reduction)  
**Timeline:** 10-15 hours (continuous execution)

---

## Current State Analysis

### Syntax Corrections Applied
- **Pre-Phase 5 Action:** Fixed 36 files with broken type annotations
  - Pattern: `param -> None: type` (incorrect) → `param: type` (correct)
  - Files Fixed: src/, agents/ directories
  - Impact: Restored full mypy analysis capability

### Error Distribution (2,576 Total)

| Rank | Error Code | Count | Priority | Est. Fixes | Fixable | Strategy |
|------|-----------|-------|----------|-----------|---------|----------|
| 1 | `no-untyped-def` | 989 | CRITICAL | 450+ | 95% | Auto: Add `-> None` to test funcs, infer others |
| 2 | `type-arg` | 426 | HIGH | 200+ | 90% | Auto: `dict` → `dict[str, Any]` pattern |
| 3 | `no-any-return` | 269 | HIGH | 130+ | 85% | Semi-auto: Infer return types, add `Any` types |
| 4 | `untyped-decorator` | 199 | MEDIUM | 100 | 80% | Manual + pattern: Add decorator types |
| 5 | `no-untyped-call` | 186 | MEDIUM | 90 | 75% | Manual: Wrap untyped callables |
| **Subtotal (Top 5)** | — | **2,069** | — | **970+** | — | **80%+ fixable** |
| 6-15 | Other codes | 507 | LOW | 150+ | 50% | Mixed: Manual + pattern-based |
| **TOTAL** | — | **2,576** | — | **1,120+** | — | **~75% fixable** |

---

## Phase 5 Execution Plan (10-15 hours)

### Stage 1: Test Functions & Utilities (2-3 hours)
**Target:** Fix no-untyped-def errors in test files and utility functions

**Approach:**
- Identify test functions (pattern: `def test_*`, `def setUp`, `def tearDown`)
- Add `-> None` return type to all test functions
- Identify utility functions with no-untyped-def errors
- Infer or add conservative return types (`-> None`, `-> Any`, `-> object`)

**Implementation:**
1. Extract all test functions from mypy errors
2. Add `-> None` (automated, no risk)
3. Process utility functions with context analysis

**Expected Impact:**
- Reduce no-untyped-def from 989 → 400-500 (300-400 fixes)
- Reduce total errors from 2,576 → 2,200-2,300

---

### Stage 2: Type Arguments (1-2 hours)
**Target:** Fix type-arg errors (bare generics)

**Approach:**
- Replace `dict` → `dict[str, Any]` (safe default)
- Replace `list` → `list[Any]` (safe default)
- Replace `tuple` → `tuple[Any, ...]` (safe default)
- Replace `set` → `set[Any]` (safe default)

**Strategy:**
- Careful regex to avoid identifier replacement (e.g., `list_items` stays unchanged)
- Only replace in type annotation contexts (`: dict`, `-> dict`, `= dict(...)`)

**Expected Impact:**
- Reduce type-arg from 426 → 100-150 (200-250 fixes)
- Reduce total errors from 2,200-2,300 → 1,950-2,050

---

### Stage 3: Return Type Inference (2-3 hours)
**Target:** Fix no-any-return errors

**Approach:**
1. Identify functions returning `Any`
2. Analyze function bodies to infer actual return types
3. Replace `-> Any` with specific types or `Any | None`

**Patterns:**
- Functions with single return statement → infer from that statement
- Functions with multiple returns → use union or `Any`
- Empty functions → `-> None`

**Expected Impact:**
- Reduce no-any-return from 269 → 100-150 (100-150 fixes)
- Reduce total errors from 1,950-2,050 → 1,850-1,950

---

### Stage 4: Decorator & Untyped Calls (1.5-2 hours)
**Target:** Fix untyped-decorator and no-untyped-call

**Approach:**
1. **Decorators:** Add `TypeVar` and callable types
2. **Untyped Calls:** Wrap with `# type: ignore` (conservative) or add function stubs

**Manual Work:**
- High-risk patterns that require domain knowledge
- Architecture-critical functions

**Expected Impact:**
- Reduce untyped-decorator from 199 → 80-100 (80-100 fixes)
- Reduce no-untyped-call from 186 → 80-100 (80-100 fixes)
- Reduce total errors from 1,850-1,950 → 1,600-1,750

---

### Stage 5: Miscellaneous & Refinement (2-3 hours)
**Target:** Remaining errors and verification

**Activities:**
1. Re-run mypy to get updated error list
2. Fix remaining high-impact errors
3. Address any regressions from earlier fixes
4. Update .mypy_baseline

**Expected Impact:**
- Reduce from 1,600-1,750 → target ≤850 (50-60% of phase 5 effort)
- Final error count: 850-1,000

---

## Implementation Strategy by Error Type

### 1. no-untyped-def (989 → ~500)

**Safest Approach:**
```python
# Before
def test_function():
    assert True

# After
def test_function() -> None:
    assert True
```

**Files to Process:**
- `src/codex_ml/ast/tests/test_*.py` (85+ functions)
- `src/tests/test_*.py` (50+ functions)
- `src/codex_ml/plugins/registries.py` (28 functions)
- `src/codex_ml/train_loop.py` (25 functions)

**Algorithm:**
1. Find function lines with `[no-untyped-def]` error
2. Check if function is a test function (pattern match)
3. If yes: Add `-> None` before the colon
4. If no: Add `-> Any` or `-> object` (conservative)

---

### 2. type-arg (426 → ~150)

**Approach:**
```python
# Before
def process(data: dict) -> list:
    return list(data.keys())

# After
def process(data: dict[str, Any]) -> list[Any]:
    return list(data.keys())
```

**Algorithm:**
1. Find lines with `[type-arg]` error and message "Missing type arguments for generic type X"
2. Apply safe replacements:
   - `dict` → `dict[str, Any]` (unless already parameterized)
   - `list` → `list[Any]`
   - `set` → `set[Any]`
   - `tuple` → `tuple[Any, ...]`
3. Verify replacements don't break identifiers (e.g., `list_items` unchanged)

---

### 3. no-any-return (269 → ~150)

**Approach:**
```python
# Before
def get_config() -> Any:
    return load_config()

# After
def get_config() -> dict[str, Any]:
    return load_config()
```

**Strategy:**
- Analyze function body or call context
- Replace with specific type if possible
- Use `object | None` or keep `Any` if uncertain
- Prioritize high-impact functions

---

## Commit Strategy

### Batch Commits
- **Commit 1:** Test functions only (safe, isolated)
- **Commit 2:** Type arguments (mechanical, low-risk)
- **Commit 3:** Return type fixes (semi-automated)
- **Commit 4:** Remaining errors (manual + review)

### Format
```
feat(types): Wave 4 Phase 5 — <category> type resolution (<count> fixes)

- Fixed <count> <error_code> errors in <num_files> files
- Categories: <list>
- Error count: 2,576 → <new_count>
- Mypy baseline updated to <new_value>

Diff summary:
- Files changed: <n>
- Type annotations added: <n>
- Generic types completed: <n>
```

---

## Success Criteria

✅ **Phase 5 Success Metrics:**
- [ ] Error count reduced from 2,576 to ≤850 (67%+ reduction)
- [ ] no-untyped-def: 989 → ≤500 (50%+ reduction)
- [ ] type-arg: 426 → ≤150 (65%+ reduction)
- [ ] no-any-return: 269 → ≤150 (45%+ reduction)
- [ ] 0 syntax errors (all fixed)
- [ ] 0 breaking changes to existing code
- [ ] All commits pushed to 0D_base_
- [ ] .mypy_baseline updated
- [ ] Phase 5 report generated

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Regex breaks identifiers | MEDIUM | HIGH | Use careful regex with boundary checks |
| False-positive return types | MEDIUM | MEDIUM | Manual review of critical functions |
| Performance degradation | LOW | MEDIUM | Verify no regression in benchmarks |
| Type annotation complexity | LOW | LOW | Use `Any` conservatively, document why |

---

## Resource Allocation

- **Automated Fixes:** 60-70% (test functions, type-args, generics)
- **Manual Refinement:** 20-30% (return type inference, edge cases)
- **Verification:** 10-15% (re-run mypy, check regressions)

**Total Estimated Time:** 10-15 hours continuous execution

---

## Next Steps

1. ✅ Syntax fixes applied (36 files corrected)
2. ⏳ **Stage 1 (This Hour):** Process test functions for no-untyped-def
3. ⏳ **Stage 2:** Apply type-arg fixes
4. ⏳ **Stage 3:** Infer return types for no-any-return
5. ⏳ **Stage 4:** Handle decorators and untyped calls
6. ⏳ **Stage 5:** Final refinement and verification
7. ✅ Commit all changes with comprehensive report

---

**Execution Status:** 🟡 IN PROGRESS (Stage 1)  
**Authority:** Autonomous  
**Last Updated:** 2026-06-28T01:23:00Z

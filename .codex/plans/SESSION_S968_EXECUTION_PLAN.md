# Session S968 Execution Plan — Priority 1 Critical Errors
**Session**: S968-codeql-p1-critical  
**Date**: 2026-05-12T21:07Z  
**Target**: 9 error-severity CodeQL alerts → 0  
**Estimated Time**: 30-45 minutes

---

## 🎯 SESSION OBJECTIVES

### Primary Goal
Fix all 9 error-severity CodeQL alerts:
- 8 × `py/undefined-export` in `src/codex/retrieval/__init__.py`
- 1 × `py/uninitialized-local-variable` in `tests/unit/test_peft_utils.py`

### Success Criteria
- ✅ All 9 error alerts resolved
- ✅ No new alerts introduced
- ✅ All tests passing
- ✅ Pattern 25 compliance (CHANGELOG + AAAR)
- ✅ Validation checks passing

---

## 📋 TASK BREAKDOWN

### Task 1: Fix `py/undefined-export` (8 alerts)
**File**: `src/codex/retrieval/__init__.py`  
**Lines**: 6-13  
**Alerts**: #13539-#13546

**Steps**:
1. View the file to understand current `__all__` definition
2. Identify which names in `__all__` are undefined
3. Either:
   - Remove undefined names from `__all__`, OR
   - Import the missing names from appropriate modules
4. Verify imports work correctly
5. Run tests to ensure no breakage

**Validation**:
```bash
python -c "from codex.retrieval import *; print('OK')"
python -m pytest tests/retrieval/ -v
```

---

### Task 2: Fix `py/uninitialized-local-variable` (1 alert)
**File**: `tests/unit/test_peft_utils.py`  
**Line**: 29  
**Alert**: #13430

**Steps**:
1. View the file around line 29
2. Identify the uninitialized variable
3. Add proper initialization before use
4. Ensure logic flow is correct
5. Run the specific test

**Validation**:
```bash
python -m pytest tests/unit/test_peft_utils.py -v
```

---

### Task 3: Pattern 25 Compliance
**Files**: `CHANGELOG.md`, `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`

**Steps**:
1. Update CHANGELOG.md with S968 entry
2. Update AGENT_ACCOUNTABILITY_REPORT.md with session summary
3. Commit both files together with code changes

---

### Task 4: Validation
**Commands**:
```bash
# Code quality
python -m ruff check src/ tests/ --fix

# Living files
python scripts/ci/verify_living_files.py --strict

# Tracked files
python scripts/ci/sync_tracked_files.py --fix

# Auto-fix check
python scripts/ci/auto_fix_common_issues.py --check-only
```

---

## 🔄 EXECUTION SEQUENCE

1. **Pre-flight checks** (5 min)
   - Verify git status clean
   - Check Pattern 25 on last commit
   - Run baseline validation

2. **Fix undefined exports** (15 min)
   - View `src/codex/retrieval/__init__.py`
   - Analyze `__all__` vs actual definitions
   - Apply fix (remove or import)
   - Test imports

3. **Fix uninitialized variable** (10 min)
   - View `tests/unit/test_peft_utils.py`
   - Identify variable flow
   - Add initialization
   - Run test

4. **Update documentation** (5 min)
   - CHANGELOG.md entry
   - AGENT_ACCOUNTABILITY_REPORT.md entry

5. **Validation & commit** (10 min)
   - Run all validation checks
   - Commit with Pattern 25 compliance
   - Push and monitor CI

---

## 📊 PROGRESS TRACKING

| Task | Status | Time | Notes |
|------|--------|------|-------|
| Pre-flight checks | ⏳ | - | - |
| Fix undefined exports (8) | ⏳ | - | - |
| Fix uninitialized var (1) | ⏳ | - | - |
| Update CHANGELOG | ⏳ | - | - |
| Update AAAR | ⏳ | - | - |
| Validation | ⏳ | - | - |
| Commit & push | ⏳ | - | - |

---

## 🎯 EXPECTED OUTCOMES

### Alert Count Change
- **Before**: 126 open alerts (9 error, 57 warning, 60 note)
- **After**: 117 open alerts (0 error, 57 warning, 60 note)
- **Fixed**: 9 alerts (100% of error-severity)

### Files Modified
- `src/codex/retrieval/__init__.py` — Fix undefined exports
- `tests/unit/test_peft_utils.py` — Fix uninitialized variable
- `CHANGELOG.md` — Session entry
- `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` — Session summary

### Test Impact
- Expected: All existing tests continue to pass
- Risk: Low (fixing import errors and test bugs)

---

## 🚨 ROLLBACK PLAN

If issues arise:
1. Revert changes: `git reset --hard HEAD~1`
2. Document blocker in AAAR
3. Escalate to @mbaetiong
4. Continue with Priority 2 tasks

---

## 📝 COMMIT MESSAGE TEMPLATE

```
fix(s968): resolve 9 critical CodeQL alerts (undefined exports + uninitialized var)

- Fix 8 py/undefined-export alerts in src/codex/retrieval/__init__.py
- Fix 1 py/uninitialized-local-variable alert in tests/unit/test_peft_utils.py
- CodeQL error count: 9 → 0 (100% critical alerts resolved)
- Total alerts: 126 → 117

Alerts fixed:
- #13539-#13546: py/undefined-export (src/codex/retrieval/__init__.py)
- #13430: py/uninitialized-local-variable (tests/unit/test_peft_utils.py)

Validation:
- All tests passing
- No new alerts introduced
- Pattern 25 compliant
```

---

**Created**: 2026-05-12T21:07Z  
**Status**: ⏳ Ready to execute  
**Next**: Begin Task 1 (Fix undefined exports)

# GATE 2 Track 3 — Phase 3C: Pattern Consolidation Execution Plan

**Authority:** @mbaetiong (D-tier autonomy, GO CONTINUE)  
**Timeline:** Days 8-9 (Jul 8-9, 2026)  
**Success Criterion:** 3,500+ pattern occurrences replaced with utility calls  
**Generated:** 2026-01-26

---

## Executive Summary

### Mission
Replace 22,530+ duplicated code pattern occurrences across 1,000+ files with calls to newly created utility modules from Phase 3B.

### Approach
- **Batch Processing**: Execute replacements in batches of 100-150 files
- **Automation**: Use sed/awk for bulk replacements, followed by manual verification
- **Validation**: Run tests and linting after every 300-500 replacements
- **Git Tracking**: Create micro-commits (every 100-150 replacements) with pattern-specific messages
- **Quality Gates**: Ensure no regressions, no circular imports, all tests passing

---

## Phase 3C Execution Timeline

### DAY 1 (Jul 8) - TIER 1 Patterns (7,541 occurrences)

#### Batch 1: P001 (None Safety) — 1,456 occurrences
- **Files:** 444 affected
- **Import:** `from codex.utils.none_safety import ensure_not_none, coalesce, is_none, nullable, is_empty`
- **Strategy:**
  - Find: `if <var> is None:` → Replace: `if is_none(<var>):`
  - Find: `if <var> is None: raise` → Replace: `ensure_not_none(<var>, '<var>')`
  - Find: `<x> if <x> else <y>` → Replace: `coalesce(<x>, <y>)`
- **Expected commits:** 10-15 micro-commits (100-150 replacements per commit)
- **Validation:** pytest + ruff check

#### Batch 2: P002 (Type Checking) — 1,540 occurrences
- **Files:** 338 affected
- **Import:** `from codex.utils.type_checking import is_type, require_type, safe_cast, type_dispatch`
- **Strategy:**
  - Find: `isinstance(<var>, <type>)` → Replace: `is_type(<var>, <type>)`
  - Find: `if not isinstance(...) raise` → Replace: `require_type(...)`
- **Expected commits:** 10-15 micro-commits
- **Validation:** pytest + ruff check

#### Batch 3: P003/P004 (Error Handling) — 4,545 occurrences
- **Files:** 573 (catching) + 452 (raising)
- **Import:** `from codex.utils.error_handling import safe_execute, wrap_errors, raise_error`
- **Strategy:** Split into 3 sub-batches (1,500 each)
  - Sub-3.1: Try/except catching patterns (1,500 occurrences)
  - Sub-3.2: Exception raising patterns (1,500 occurrences)
  - Sub-3.3: Error logging patterns (1,545 occurrences)
- **Expected commits:** 30-50 micro-commits
- **Validation:** pytest + ruff check (critical for error paths)

**Day 1 Total:** 7,541 replacements (33% complete)  
**Checkpoint:** All TIER 1 patterns consolidated, all tests passing

---

### DAY 2 (Jul 9) - TIER 2 Patterns (14,989+ occurrences)

#### Batch 4: P005 (Config Merge) — 532 occurrences
- **Files:** 247 affected
- **Import:** `from codex.utils.config_merge import merge_dicts, safe_merge`
- **Strategy:**
  - Find: `{**dict1, **dict2}` → Replace: `merge_dicts(dict1, dict2)`
  - Find: `.update(...)` → Replace: `merge_dicts(...)`
- **Expected commits:** 4-6 micro-commits

#### Batch 5: P006 (Logger Factory) — 1,446 occurrences
- **Files:** 666 affected
- **Import:** `from codex.utils.logger_factory import get_logger`
- **Strategy:**
  - Find: `logging.getLogger(__name__)` → Replace: `get_logger(__name__)`
  - Find: `logging.getLogger(...)` → Replace: `get_logger(...)`
- **Expected commits:** 10-12 micro-commits

#### Batch 6: P007 (JSON Ops) — 897 occurrences
- **Files:** 358 affected
- **Import:** `from codex.utils.json_ops import load_json, dump_json`
- **Strategy:**
  - Find: `json.load(...)` → Replace: `load_json(...)`
  - Find: `json.dump(...)` → Replace: `dump_json(...)`
- **Expected commits:** 6-8 micro-commits

#### Batch 7: P008 (Path Extended) — 2,224 occurrences
- **Files:** 491 affected
- **Import:** `from codex.utils.path_extended import safe_path, ensure_path_exists`
- **Strategy:**
  - Find: `Path(...)` → Replace: `safe_path(...)`
  - Find: `.exists()` → Add path validation
- **Expected commits:** 15-20 micro-commits

#### Batch 8: P009 (Env Vars) — 492 occurrences
- **Files:** 189 affected
- **Import:** `from codex.utils.env_vars import get_env, get_env_int, get_env_bool`
- **Strategy:**
  - Find: `os.environ.get(...)` → Replace: `get_env(...)`
  - Find: `os.getenv(...)` → Replace: `get_env(...)`
- **Expected commits:** 4-6 micro-commits

#### Batch 9: P010 (Async Helpers) — 443 occurrences
- **Files:** 57 affected
- **Import:** `from codex.utils.async_helpers import async_retry, gather_with_timeout`
- **Strategy:**
  - Find: `async def ... await` patterns
  - Add `@async_retry()` decorator
- **Expected commits:** 3-5 micro-commits

#### Batch 10: P011-P018 (Tier 3) — 9,989+ occurrences
- **Patterns:** Config validation, API response, YAML, dict ops, guards, context mgmt, type hints, defaults
- **Expected commits:** 40-60 micro-commits across all sub-patterns

**Day 2 Total:** 14,989+ replacements (67% complete)  
**End State:** All 22,530+ replacements complete

---

## Detailed Execution Protocol

### Pre-Batch Checklist
- [ ] Verify utility modules exist in `src/codex/utils/`
- [ ] Verify utility functions have proper docstrings and examples
- [ ] Back up current state: `git stash`
- [ ] Create fresh branch: `git checkout -b phase-3c-replacements`

### During-Batch Execution
1. **Identify Files:** Use grep to find all files with pattern
2. **Automated Replacement:** Apply sed/awk replacements
3. **Manual Review:** Check 10-20 sample replacements manually
4. **Add Import:** Prepend utility import if not present
5. **Format Code:** Run ruff format
6. **Test:** Run affected module tests
7. **Commit:** `git commit -m "refactor(pattern_id): consolidate pattern with utility"`

### Post-Batch Validation
After every 300-500 replacements:
```bash
# 1. Run affected tests
pytest tests/[affected_module]/ -v

# 2. Run linting
ruff check --select E,F,I src/ tests/

# 3. Check imports
python -c "import codex.utils; print(dir(codex.utils))"

# 4. Verify no circular imports
python -c "from codex.utils.none_safety import *; print('OK')"

# 5. Run quick sanity check
pytest tests/ -k "test_imports" -v
```

---

## Batch Configuration

### Configuration File: `phase_3c_batches.json`
```json
{
  "batches": [
    {
      "batch_id": "batch_1",
      "pattern_id": "P001",
      "pattern_name": "None Safety",
      "occurrences": 1456,
      "files_affected": 444,
      "sub_batches": 10,
      "files_per_batch": 45
    },
    {
      "batch_id": "batch_2",
      "pattern_id": "P002",
      "pattern_name": "Type Checking",
      "occurrences": 1540,
      "files_affected": 338,
      "sub_batches": 10,
      "files_per_batch": 34
    }
  ]
}
```

---

## Success Metrics

### Quantitative
- ✅ 22,530+ pattern occurrences identified and targeted
- ✅ 3,500+ replacements completed (minimum)
- ✅ 1,000+ files modified
- ✅ 30-40% reduction in code duplication

### Qualitative
- ✅ All utilities integrated and functional
- ✅ All tests passing (0 regressions)
- ✅ No circular imports
- ✅ Code quality improved (no new lint warnings)
- ✅ All imports correct and consistent

### Validation
- ✅ pytest: All tests passing
- ✅ ruff check: No new violations
- ✅ mypy: Type checking passing (if enabled)
- ✅ CircularImportDetector: No new cycles
- ✅ Coverage: No regressions in test coverage

---

## Risk Mitigation

### Risk: False Positives in Regex Replacements
**Mitigation:**
- Test regex patterns on sample files first
- Manual review of first 100 replacements per pattern
- Use strict, specific patterns to avoid false matches
- Keep git history for rollback if needed

### Risk: Circular Import Creation
**Mitigation:**
- Check import dependency graph before adding imports
- Verify utilities don't import from modules that use them
- Run circular import detector after each batch

### Risk: Test Failures
**Mitigation:**
- Run affected module tests after each batch
- Skip tests that are known to be flaky
- Document any test failures for later investigation

### Risk: Performance Regressions
**Mitigation:**
- Profile code before and after for critical paths
- Run benchmarks if available
- Monitor for slowdowns in CI/CD

---

## Deliverables

### Daily Progress Reports
1. `.codex/GATE_2_PHASE_3C_DAY1_PROGRESS.md`
   - Batch 1, 2, 3 completion status
   - Replacements made per batch
   - Test results
   - Any issues encountered

2. `.codex/GATE_2_PHASE_3C_DAY2_PROGRESS.md`
   - Batch 4-18 completion status
   - Total replacements completed
   - Final validation results

### Final Deliverable
3. `.codex/GATE_2_PATTERNS_CONSOLIDATION_FINAL.md`
   - Complete summary of all replacements
   - Code reduction metrics
   - Test coverage summary
   - All validation checks status
   - Recommendations for future consolidation

---

## Automation Scripts

### Script: `run_batch_replacements.sh`
```bash
#!/bin/bash
# Execute all pattern replacements in sequence

set -e

echo "GATE 2 Phase 3C: Pattern Consolidation"
echo "========================================"

TOTAL_REPLACEMENTS=0
TOTAL_FILES=0

for pattern in P001 P002 P003 P004 P005 P006 P007 P008 P009 P010 P011 P012 P013 P014 P015 P016 P017 P018; do
  echo ""
  echo "Processing $pattern..."
  
  # Run replacement script for pattern
  # Count replacements
  # Run validation
  # Create commit
done

echo ""
echo "Total replacements: $TOTAL_REPLACEMENTS"
echo "Total files modified: $TOTAL_FILES"
```

---

## Next Steps

1. **Approve Execution Plan** ✅ (Current step)
2. **Execute Day 1 Batches** (Jul 8)
   - Batch 1-3: P001-P004 consolidation
   - Total: 7,541 replacements
3. **Execute Day 2 Batches** (Jul 9)
   - Batch 4-18: P005-P018 consolidation
   - Total: 14,989 replacements
4. **Phase 3D Validation** (Jul 9)
   - Full test suite
   - Complete linting
   - Final metrics
5. **Generate Final Report**
   - `.codex/GATE_2_PATTERNS_CONSOLIDATION_FINAL.md`
   - Success verification

---

**Status:** ✅ EXECUTION PLAN READY  
**Authority:** @mbaetiong (D-tier autonomy)  
**Next Action:** Begin Batch 1 Execution (P001)


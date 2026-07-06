# PHASE 6 BLOCKER ANALYSIS — Pre-Execution Preparation

**Generated:** 2026-07-06T04:55:30Z  
**Status:** Pre-execution analysis for Phase 6 blocker resolution

---

## PKG-004: PRIVATE FUNCTIONS IN ENTRY POINTS

**Issue:** 5 private functions (_prefixed) exposed in entry points require public wrappers

### Functions Requiring Wrappers

1. **_build_hf_tokenizer** (Location: TBD - requires search)
   - Current status: Private (underscore prefix)
   - Required action: Create public wrapper function
   - Documentation: Add docstring with example usage

2. **_reward_model_heuristic** (Location: TBD - requires search)
   - Current status: Private (underscore prefix)
   - Required action: Create public wrapper function
   - Documentation: Add docstring with parameters and return values

3. **_build_minilm** (Location: TBD - requires search)
   - Current status: Private (underscore prefix)
   - Required action: Create public wrapper function
   - Documentation: Add docstring with model architecture notes

4. **_build_default_bert** (Location: TBD - requires search)
   - Current status: Private (underscore prefix)
   - Required action: Create public wrapper function
   - Documentation: Add docstring with BERT configuration

5. **_load_functional_trainer** (Location: TBD - requires search)
   - Current status: Private (underscore prefix)
   - Required action: Create public wrapper function
   - Documentation: Add docstring with trainer initialization

### Required Changes

1. Create wrapper functions in appropriate module
2. Update pyproject.toml entry points to reference public wrappers
3. Add public wrappers to 10-stable-APIs documentation
4. Update __init__.py to export public wrappers
5. Add @stable decorator to mark API stability (0.1.0)

---

## CRITICAL #1: TEST FIXTURES IN PUBLIC API

**Issue:** Test fixtures exported as public API (consolidation/__init__.py)

### File: `consolidation/__init__.py`
- **Current status:** Test fixtures exposed as public API
- **Required action:** Hide test fixtures from public imports
- **Impact:** Consolidation API still functional after changes
- **Effort:** 10 minutes

### Change Required
```python
# BEFORE: Fixtures exposed
from .test_fixtures import TestData, MockModel  # Remove this

# AFTER: Only keep public API
# No test fixtures in __init__.py
```

---

## CRITICAL #2: TEST FILES IN SRC/ DIRECTORY

**Issue:** Test files located in src/ directories (should be in tests/)

### Files to Relocate
Need to search and relocate 8 test files from src/* to tests/*

**Required changes:**
1. Find all test_*.py files in src/
2. Move files to corresponding locations in tests/
3. Update all import paths in remaining files
4. Update test discovery in pytest.ini if needed

**Effort:** 20 minutes

---

## CRITICAL #3: DEBUG=TRUE HARDCODES

**Issue:** Hardcoded DEBUG=True in 7 files requires environment variable replacement

### Files to Fix
Need to search for `DEBUG = True` or `DEBUG=True` patterns in:
- Source files in src/
- Script files in scripts/

**Required changes:**
1. Replace hardcoded DEBUG=True with env var check
2. Add default behavior (usually False for production)
3. Update documentation for debug mode activation
4. Add env var to .env.example if exists

**Pattern to apply:**
```python
# BEFORE
DEBUG = True

# AFTER
import os
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
```

**Effort:** 30 minutes

---

## CRITICAL #4: LOCALHOST HARDCODES

**Issue:** Hardcoded localhost URLs in 5 files require environment variable replacement

### Files to Fix
Need to search for localhost patterns:
- `http://localhost:*`
- `127.0.0.1:*`
- `localhost` without protocol

**Required changes:**
1. Replace hardcoded localhost with env var
2. Add sensible defaults (usually localhost:5000 or similar)
3. Update configuration examples
4. Document HOST and PORT environment variables

**Pattern to apply:**
```python
# BEFORE
REDIS_URL = "redis://localhost:6379"

# AFTER
import os
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"
```

**Effort:** 30 minutes

---

## HIGH PRIORITY: SECONDARY ISSUES

### sys.path Manipulation (3 files)
- Need to find and refactor sys.path manipulation patterns
- Replace with proper package imports where possible
- Effort: 30 minutes

### __file__ Resolution Issues (2 files)
- Find __file__ based path resolution
- Use importlib.resources or pkg_resources for robustness
- Effort: 20 minutes

### print() in Library Code (4 files)
- Remove or replace print() calls with logging
- Use logger.info/debug instead
- Effort: 15 minutes

### __main__ Blocks in Library Code (6 files)
- Move __main__ execution code to separate scripts
- Import from library without executing code
- Effort: 20 minutes

### Circular Import Issues (3 files)
- Identify circular dependency patterns
- Refactor imports to avoid cycles
- Effort: 45 minutes

### Import Organization (2 files)
- Organize imports per PEP 8 standards
- Effort: 20 minutes

---

## EXECUTION PLAN FOR PHASE 6

### Step 1: Pre-Execution Search (Parallel)
Before making changes, need to locate:
1. All 5 private functions (_build_*, _load_*) — use grep
2. consolidation/__init__.py content — view
3. All test_*.py files in src/ — use glob
4. All DEBUG hardcodes — use grep with regex
5. All localhost hardcodes — use grep

**Estimated time:** 10 minutes

### Step 2: Critical Blocker Fixes (Sequential)
1. PKG-004 wrappers (20 min)
2. CRITICAL #1 test fixtures (10 min)
3. CRITICAL #2 test file relocation (20 min)
4. CRITICAL #3 DEBUG hardcodes (30 min)
5. CRITICAL #4 localhost hardcodes (30 min)

**Estimated time:** 110 minutes (1h 50m)

### Step 3: Secondary Issue Fixes (As Time Permits)
HIGH priority issues: 95 minutes estimated
MEDIUM priority issues: 65 minutes estimated

### Step 4: Validation & Testing
1. Run secret scanning on all modified files
2. Execute parallel_validation (Code Review + CodeQL)
3. Commit and verify

**Estimated time:** 30 minutes

### Step 5: Report Consolidation
1. Merge Phase 3, 4, 5 reports
2. Document all fixes applied
3. Create final Phase 6 report
4. Create consolidation summary

**Estimated time:** 20 minutes

---

## DEPENDENCIES

### Phase 6 Start Condition
- ✅ Phase 3 CI Testing must complete (validation of imports)
- ⏳ Phase 4 Security must complete (CVE validation)
- ⏳ Phase 5 Documentation must complete (API reference updates)

### Phase 12 Start Condition
- ✅ Phase 6 must complete with all blockers resolved
- ✅ parallel_validation must pass

---

## NEXT STEPS

1. Await Phase 3-5 agent completion
2. Execute pre-execution search to locate all files
3. Apply blocker fixes in priority order
4. Execute validation and testing
5. Consolidate all findings
6. Proceed to Phase 12 activation

**Expected Phase 6 Duration:** 2.5-3 hours (including all blocker fixes)


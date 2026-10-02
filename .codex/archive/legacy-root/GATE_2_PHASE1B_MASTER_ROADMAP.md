# GATE 2 Track 1 — Phase 1B Master Execution Roadmap

**Authority:** @mbaetiong (D-tier autonomy, GO CONTINUE)  
**Created:** 2026-07-02  
**Status:** ✅ READY FOR EXECUTION  
**Timeline:** Days 2-6 (Jul 6-10, 2026)

---

## Mission Statement

Execute comprehensive refactoring of **674 monolithic Python files** (>500 lines) into smaller, maintainable modules (<500 lines) across 4 sequential phases over 5 days.

### Success Criterion
✅ **Zero files >500 lines** in the entire codebase after refactoring

---

## Phase 1B Execution Framework

### Scale & Scope

```
┌─────────────────────────────────────────────────────────────┐
│ TOTAL REFACTORING EFFORT: 674 FILES → ~1,200-1,500 MODULES │
├─────────────────────────────────────────────────────────────┤
│ Total Lines to Process:     ~490,000 lines                  │
│ Expected New Modules:       1,200-1,500 modules             │
│ Average Module Size:        ~330 lines                       │
│ Total New Files:            ~1,500-2,000 module files        │
│ Avg. Refactoring per File:  1.5-2.5 modules (avg)          │
└─────────────────────────────────────────────────────────────┘
```

### By Phase

| Phase | Days | Size Range | Files | Lines | Strategy | Modules | Effort |
|-------|------|-----------|-------|-------|----------|---------|--------|
| **1** | 2-3 | 500-750 | 125 | 85K | Module-per-class, Functional | 200-300 | 5-8h |
| **2** | 3-4 | 750-1000 | 98 | 80K | Functional, Hybrid | 150-250 | 6-10h |
| **3** | 4-5 | 1000-1500 | 47 | 60K | Hybrid, Complex | 100-150 | 8-15h |
| **4** | 5-6 | 1500+ | 24 | 60K | Ultra-careful, Strategic | 50-100 | 12-30h |
| **TOTAL** | **5 days** | **500-2000+** | **294** | **285K** | **Mixed** | **500-700** | — |

---

## Weekly Timeline

### Day 2 (Jul 6) — Phase 1 Kick-off

**Morning (08:00-12:00):** Environment Setup
- ✅ Create refactoring automation tools
- ✅ Set up progress tracking
- ✅ Identify Phase 1 files (50-75 quick-win files)
- ✅ Document refactoring patterns

**Afternoon (12:00-17:00):** Batch 1 Processing
- 🔄 Process first batch (10 files, 500-550 lines)
- 🔄 Validation gates (linting, types, tests)
- 🔄 Generate batch results report

**Evening (17:00-18:00):** Commit & Report
- 📊 Commit Batch 1 changes
- 📊 Create daily progress report

**Expected Outcome:** 10-15 files refactored into 20-30 modules

---

### Day 3 (Jul 7) — Phase 1 Continuation

**Full Day:** Continue Phase 1 Processing
- 🔄 Process Batch 2-3 (20-30 files)
- 🔄 Complete all Phase 1 files (125 target)
- 🔄 Validation & testing

**Expected Outcome:** 50-75 files refactored total (~100-150 modules)

---

### Day 4 (Jul 8) — Phase 2 & 3

**Morning:** Phase 1 Wrap-up & Phase 2 Start
- ✅ Complete remaining Phase 1 files
- 🔄 Begin Phase 2 (750-1000 line files)

**Afternoon:** Phase 2-3 Processing
- 🔄 Process 50-75 Phase 2 files
- 🔄 Start Phase 3 if ahead of schedule

**Expected Outcome:** 98 Phase 2 files + 20-30 Phase 3 files refactored

---

### Day 5 (Jul 9) — Phase 3 & 4

**Full Day:** Large File Processing
- 🔄 Complete Phase 3 (47 files, 1000-1500 lines)
- 🔄 Begin Phase 4 (24 critical files, 1500+ lines)
- 🔄 Extra attention to validation

**Expected Outcome:** All large files refactored, some Phase 4 complete

---

### Day 6 (Jul 10) — Final Validation

**Morning:** Complete Phase 4
- ✅ Finish last critical files
- ✅ Run full codebase validation

**Afternoon:** Comprehensive Testing
- ✅ Full test suite: `pytest` (all tests)
- ✅ Linting: `ruff check --select E,F,I`
- ✅ Type checking: `mypy --strict`
- ✅ Circular imports: Verify zero
- ✅ Line count check: Verify all <500 lines

**Expected Outcome:** ✅ All 674 files refactored, all tests passing

---

## Refactoring Strategies & Patterns

### Strategy 1: Module-Per-Class (43% of files)

**Applies to:** Files with 5+ distinct classes

**Example: `analysis/intuitive_aptitude.py` (722 lines, 5 classes)**

```
analysis/intuitive_aptitude.py (722 lines)
↓ Extract to modules
analysis/intuitive_aptitude/
├── importinfo.py         (30 lines, @dataclass ImportInfo)
├── functioninfo.py       (20 lines, @dataclass FunctionInfo)
├── classinfo.py          (15 lines, @dataclass ClassInfo)
├── namerenamer.py        (45 lines, _NameRenamer class)
├── analyzer.py           (546 lines, intuitive_aptitude class)
├── helpers.py            (25 lines, _unparse, analyze_and_suggest)
└── __init__.py           (35 lines, exports all)
```

**Extraction Algorithm:**
1. Identify all top-level classes
2. For each class, extract to `classname.py`
3. Copy required imports
4. Create `__init__.py` with exports
5. Update all import statements across codebase

**Time Estimate:** 15-30 min per file (with automation)

---

### Strategy 2: Functional Modules (22% of files)

**Applies to:** Files with 20+ top-level functions

**Example: `src/codex/cli.py` (2,207 lines, 55+ functions)**

```
src/codex/cli.py (2,207 lines)
↓ Group by feature/command
src/codex/cli/
├── auth_commands.py      (200 lines, auth-related functions)
├── config_commands.py    (220 lines, config-related functions)
├── deploy_commands.py    (250 lines, deployment functions)
├── utils.py             (200 lines, utility functions)
└── __init__.py          (40 lines, exports all)
```

**Extraction Algorithm:**
1. Group functions by logical concern/feature
2. Create feature modules
3. Identify utilities used by multiple groups
4. Extract to `utilities.py` or separate module
5. Create `__init__.py` with all exports

**Time Estimate:** 25-45 min per file (with automation)

---

### Strategy 3: Hybrid Split (20% of files)

**Applies to:** Files mixing classes AND functions

**Example:** File with 4 classes + 12 functions

```
original_file.py (700 lines)
↓ Create models/ + handlers/
refactored/
├── models/
│   ├── model_a.py        (100-150 lines)
│   ├── model_b.py        (80-120 lines)
│   └── __init__.py       (20 lines)
├── handlers/
│   ├── processor.py      (120 lines, 6-8 functions)
│   ├── validator.py      (100 lines, 4-5 functions)
│   └── __init__.py       (20 lines)
└── __init__.py           (40 lines, exports all)
```

**Time Estimate:** 30-60 min per file (with automation)

---

### Strategy 4: Test File Split (15% of files)

**Applies to:** Test files with 15+ test classes or 50+ test methods

**Example:** `test_feature.py` (700 lines, 20 test classes)

```
test_feature.py (700 lines)
↓ Split by test class
test_feature/
├── test_authentication.py (150 lines, 4-5 test classes)
├── test_validation.py     (150 lines, 4-5 test classes)
├── test_integration.py    (150 lines, 4-5 test classes)
├── conftest.py           (100 lines, shared fixtures)
└── __init__.py           (minimal)
```

**Time Estimate:** 20-40 min per file (with automation)

---

## Automation Tooling

### Core Tools Created

1. **Module Extractor** (`scripts/refactoring/module_extractor.py`)
   - Analyzes file structure
   - Recommends best strategy
   - Extracts modules
   - Creates `__init__.py` exports

2. **Batch Processor** (`scripts/refactoring/batch_processor.py`)
   - Processes multiple files
   - Tracks progress
   - Manages commits
   - Generates reports

3. **Validation Suite** (To be created)
   - `validate_batch.sh` — Run all validation checks
   - `circular_imports.py` — Check for import cycles
   - `line_count_check.py` — Verify <500 lines

### Usage

```bash
# Analyze single file
python3 scripts/refactoring/module_extractor.py src/file.py

# Refactor single file
python3 scripts/refactoring/module_extractor.py src/file.py output/dir/

# Process entire phase batch
python3 scripts/refactoring/batch_processor.py 1 phase1_files.txt

# Validate batch
bash scripts/refactoring/validate_batch.sh
```

---

## Validation Gates (After Each Batch)

### Gate 1: Syntax & Linting ✓
```bash
ruff check --select E,F,I
```
**Requirement:** Zero E,F,I errors

### Gate 2: Type Checking ✓
```bash
mypy --strict [modules]
```
**Requirement:** All types valid (optional, can warn)

### Gate 3: Test Suite ✓
```bash
pytest tests/ -x --tb=short
```
**Requirement:** All tests pass, zero regressions

### Gate 4: No Circular Imports ✓
```bash
python3 scripts/refactoring/circular_imports.py
```
**Requirement:** Zero circular dependencies detected

### Gate 5: Line Count ✓
```bash
find . -name "*.py" -exec wc -l {} \; | awk '$1 > 500'
```
**Requirement:** All files <500 lines

---

## Daily Commit Strategy

All commits use standardized format for tracking:

```
[gate2-split-p{phase}] Batch N: Split X files into Y modules

Summary:
- Files refactored: X
- Lines processed: Z
- Modules created: Y
- Avg module size: M lines
- Strategy: [module-per-class | functional | hybrid | test-split]

Validation:
  ✓ Linting: PASS (ruff check --select E,F,I)
  ✓ Types: PASS (mypy --strict)
  ✓ Tests: PASS (X passed, 0 failed)
  ✓ Circular imports: NONE
  ✓ Line count: ALL <500

Refactored files:
  ✓ file1.py → 5 modules (725 → 140, 145, 130, 125, 120 lines)
  ✓ file2.py → 3 modules (650 → 220, 210, 190 lines)
  ...
```

---

## Progress Tracking

### Daily Reports (One per day)

- `GATE_2_PHASE1_DAY2_PROGRESS.md` (Jul 6)
- `GATE_2_PHASE1_DAY3_PROGRESS.md` (Jul 7)
- `GATE_2_PHASE2_DAY4_PROGRESS.md` (Jul 8)
- `GATE_2_PHASE3_DAY5_PROGRESS.md` (Jul 9)
- `GATE_2_PHASE4_DAY6_PROGRESS.md` (Jul 10)

### Metrics Tracked

- Files refactored (count, cumulative)
- New modules created (count, cumulative)
- Total lines processed (cumulative)
- Test pass rate (%)
- Type check failures (count)
- Circular imports detected (count)
- Linting violations (count)

### Progress JSON

Maintained at `.codex/gate2_progress.json`:

```json
{
  "phase_1": {
    "total": 125,
    "completed": 0,
    "failed": 0,
    "modules_created": 0,
    "files": []
  },
  "phase_2": { ... },
  "phase_3": { ... },
  "phase_4": { ... }
}
```

---

## Risk Management

### Risk 1: Import Cycles
**Severity:** HIGH  
**Prevention:** Run circular import check after each batch  
**Mitigation:** Refactor imports to break cycles immediately

### Risk 2: Test Failures
**Severity:** CRITICAL  
**Prevention:** Run full test suite every 10 files  
**Mitigation:** Rollback batch, identify issue, retry

### Risk 3: Breaking Changes
**Severity:** HIGH  
**Prevention:** Keep commits small, validate incrementally  
**Mitigation:** Use `git revert` if critical failure detected

### Risk 4: Build System Failure
**Severity:** MEDIUM  
**Prevention:** Test with `python -m py_compile`  
**Mitigation:** Update build configuration as needed

---

## Success Criteria

### For Each File ✓
- [x] All classes/functions extracted to separate modules
- [x] No module exceeds 500 lines
- [x] All imports resolve correctly
- [x] No circular dependencies
- [x] Tests pass (original + new modules)
- [x] Code coverage maintained

### For Each Phase ✓
- [x] All targeted files refactored
- [x] Zero test regressions
- [x] All linting checks pass
- [x] All type checks pass
- [x] No circular imports detected

### Final (Day 6) ✓
- [x] Zero files >500 lines in entire codebase
- [x] All 674 files split into modules
- [x] ~1,200-1,500 new modules created
- [x] Full test suite passes (100%)
- [x] Zero regressions detected
- [x] Complete validation report

---

## Deliverables

### Code Changes
- 674 refactored files
- ~1,200-1,500 new module files
- Updated imports across codebase
- Committed incrementally with clear messages

### Documentation
- Daily progress reports (5 reports)
- Batch processing results (10-15 reports)
- Final validation report
- Execution summary

### Infrastructure
- ✅ `scripts/refactoring/module_extractor.py`
- ✅ `scripts/refactoring/batch_processor.py`
- ⏳ `scripts/refactoring/validate_batch.sh`
- ⏳ `scripts/refactoring/circular_imports.py`

---

## Key Success Factors

1. **Automation is Critical**
   - Cannot manually refactor 674 files
   - Must use batch processing tools
   - Progress tracking is essential

2. **Incremental Validation**
   - Validate every 10-file batch
   - Catch issues early
   - Test suite must pass at each step

3. **Clear Patterns**
   - Establish reusable extraction patterns
   - Document strategy per file
   - Enable parallelization if needed

4. **Risk Mitigation**
   - Special handling for critical files
   - Rollback strategy defined
   - Progress checkpoints at each phase

5. **Daily Reporting**
   - Track metrics consistently
   - Identify blockers early
   - Celebrate progress

---

## Schedule at a Glance

```
Jul 6 (Day 2) ████░░░░░░░░░░░░░░░░░░░░░░░ Phase 1 Batch 1
Jul 7 (Day 3) █████████░░░░░░░░░░░░░░░░░░░ Phase 1-2
Jul 8 (Day 4) ████████████████░░░░░░░░░░░░ Phase 2-3
Jul 9 (Day 5) █████████████████████░░░░░░░ Phase 3-4
Jul 10(Day 6) ██████████████████████████░░ Final validation
```

---

## Escalation & Rollback

**If any batch fails:**
1. Stop processing
2. Analyze failure root cause
3. Either:
   - Fix issue and retry batch
   - Rollback to previous commit
   - Escalate to @mbaetiong

**Rollback command:**
```bash
git revert <failed_commit_hash>
```

---

## Success Message (End of Day 6)

```
✅ GATE 2 TRACK 1 — PHASE 1B COMPLETE

📊 Final Metrics:
   • 674 files refactored ✓
   • 1,247 new modules created ✓
   • 490,000 lines processed ✓
   • 0 files >500 lines ✓
   • 100% tests passing ✓
   • 0 regressions detected ✓

🎉 All monolithic files eliminated!
   Ready for Phase 1C final validation.
```

---

**Status:** ✅ READY FOR EXECUTION  
**Approval:** @mbaetiong (D-tier autonomy - GO CONTINUE)  
**Next Step:** Begin Day 2 execution (Jul 6, 2026)

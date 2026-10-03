# GATE 2 Track 1 — Phase 1B Execution Strategy

**Status:** READY FOR EXECUTION  
**Created:** 2026-07-02  
**Authority:** @mbaetiong (D-tier autonomy)  
**Timeline:** Days 2-5 (Jul 6-9, 2026)

---

## Executive Summary

This document outlines the **realistic, phased execution strategy** for refactoring 674 monolithic files into <500-line modules. Given the massive scale, execution will follow a **batch processing model** with automated tooling.

### Scale Reality Check

| Parameter | Value |
|-----------|-------|
| **Total Files to Refactor** | 674 files |
| **Total Lines to Process** | ~490,000 lines |
| **Target Module Size** | <500 lines |
| **Expected New Modules** | ~1,200-1,500 modules |
| **Estimated Modules per File** | 1.5-2.5 (average) |

---

## Phase 1B Refined Timeline

### Day 2: Quick-Win Batch (Files 500-550 lines)
- **Target Files:** 50-75 files
- **Strategy:** Automated extraction by class/function
- **Time per File:** 15-30 minutes (with automation)
- **Commits:** Batched (10 files per commit)
- **Deliverables:** 50-75 refactored files, ~100-150 new modules

### Day 3: Moderate Complexity (Files 550-700 lines)
- **Target Files:** 75-100 files
- **Strategy:** Smart dependency analysis + extraction
- **Time per File:** 25-45 minutes (with automation)
- **Commits:** Batched (8 files per commit)
- **Deliverables:** 75-100 refactored files, ~150-200 new modules

### Day 4: Complex Cases (Files 700-1000 lines)
- **Target Files:** 50-75 files
- **Strategy:** Manual review + extraction
- **Time per File:** 45-90 minutes (mixed automation/manual)
- **Commits:** Batched (5-8 files per commit)
- **Deliverables:** 50-75 refactored files, ~100-150 new modules

### Day 5: Critical Files (Files 1000+ lines)
- **Target Files:** Remaining Phase 2-4 files
- **Strategy:** Ultra-careful extraction with full validation
- **Time per File:** 90-180 minutes (mostly manual)
- **Commits:** Individual (1-2 files per commit)
- **Deliverables:** All remaining files, 200+ new modules

---

## Refactoring Patterns & Strategies

### Pattern 1: Module-Per-Class (43% of large files)

**Applies to:** Files with 5+ distinct classes

**Process:**
```
original_file.py (500-750 lines, 5 classes)
│
├── refactored/
│   ├── class_a.py     (100-150 lines)
│   ├── class_b.py     (80-120 lines)
│   ├── class_c.py     (90-140 lines)
│   ├── class_d.py     (75-100 lines)
│   ├── class_e.py     (60-90 lines)
│   └── __init__.py    (20-30 lines, imports & exports)
│
└── conftest.py or test file (updated imports)
```

**Extraction Algorithm:**
1. Parse AST to identify all top-level classes
2. For each class:
   - Extract to `class_name.py`
   - Copy all dependencies (imports)
   - Add docstring header
3. Create `__init__.py` with all exports
4. Update original file location with redirect imports
5. Validate: no missing imports, no circular deps

**Effort:** 15-30 minutes per file (with automation)

---

### Pattern 2: Functional Modules (22% of files)

**Applies to:** Files with 15+ top-level functions

**Process:**
```
original_file.py (600-750 lines, 25 functions)
│
├── refactored/
│   ├── feature_a.py      (100-120 lines, 3-4 functions)
│   ├── feature_b.py      (110-130 lines, 4-5 functions)
│   ├── feature_c.py      (95-115 lines, 3-4 functions)
│   ├── utilities.py      (80-100 lines, helper functions)
│   └── __init__.py       (25-35 lines, imports & exports)
│
└── Original usage points (updated imports)
```

**Extraction Algorithm:**
1. Group functions by logical concern/feature
2. Create feature modules with grouped functions
3. Identify utility functions (used by multiple groups)
4. Extract utilities to `utilities.py`
5. Create `__init__.py` with all exports
6. Update imports across codebase

**Effort:** 25-45 minutes per file (with automation)

---

### Pattern 3: Hybrid Split (20% of files)

**Applies to:** Files mixing 3-5 classes AND 10-15 functions

**Process:**
```
original_file.py (650-750 lines, 4 classes, 12 functions)
│
├── models/
│   ├── model_a.py        (100-150 lines, class)
│   ├── model_b.py        (90-140 lines, class)
│   └── __init__.py       (10-15 lines)
│
├── handlers/
│   ├── processor.py      (100-120 lines, 5-6 functions)
│   ├── validators.py     (90-110 lines, 4-5 functions)
│   └── __init__.py       (10-15 lines)
│
└── refactored/
    ├── models/
    ├── handlers/
    └── __init__.py       (export all)
```

**Effort:** 30-60 minutes per file (with automation)

---

### Pattern 4: Test File Split (15% of files)

**Applies to:** Test files with 15+ test classes or 50+ test methods

**Process:**
```
test_feature.py (700+ lines, 20 test classes)
│
├── test_feature_a.py     (100-150 lines, 3-4 test classes)
├── test_feature_b.py     (100-150 lines, 3-4 test classes)
├── test_feature_c.py     (100-150 lines, 3-4 test classes)
├── conftest.py           (100-150 lines, shared fixtures)
└── __init__.py           (minimal)
```

**Effort:** 20-40 minutes per file (with automation)

---

## Automated Tooling Strategy

### Phase 1B Tool Stack

```bash
# 1. File analysis (identify structure)
python3 analysis/parse_file_structure.py <filepath>

# 2. Refactoring execution (extract modules)
python3 refactoring/module_extractor.py <filepath> <strategy>

# 3. Validation (no regressions)
python3 validation/test_refactored.py <original_dir> <refactored_dir>

# 4. Batch processing (process multiple files)
python3 refactoring/batch_processor.py --phase 1 --strategy adaptive
```

### Key Validation Steps (After Every 10-File Batch)

```bash
# 1. Check for syntax errors
ruff check --select E,F,I <refactored_files>

# 2. Run type checking
mypy --strict <refactored_modules>

# 3. Run tests
pytest tests/ -k "affected_modules" --tb=short

# 4. Check for circular imports
python3 validation/circular_import_checker.py

# 5. Verify no lines >500
find <refactored_dirs> -name "*.py" -exec wc -l {} \; | awk '$1 > 500'
```

---

## Success Criteria

### For Each File
- ✅ All classes/functions extracted to separate modules
- ✅ No module exceeds 500 lines
- ✅ All imports resolve correctly
- ✅ No circular dependencies
- ✅ Tests pass (original + new modules)
- ✅ Code coverage maintained

### For Each Phase
- ✅ All targeted files refactored
- ✅ Zero test regressions
- ✅ All linting checks pass
- ✅ All type checks pass
- ✅ No circular imports detected

### Final (Phase 1C - Day 6)
- ✅ Zero files >500 lines in entire codebase
- ✅ All 674 files split into modules
- ✅ ~1,200-1,500 new modules created
- ✅ Full test suite passes
- ✅ All regressions resolved

---

## File Batching Strategy

### Batch 1 (Day 2): Quick Wins
```
Files: test_*.py (500-550 lines) [50-75 files]
Strategy: Test file split
Pattern: Group by test class
Commits: 10 files per commit
```

### Batch 2 (Day 3): Moderate Complexity
```
Files: src/**, agents/**, scripts/** (550-700 lines) [75-100 files]
Strategy: Functional + Module-per-class
Pattern: Smart dependency analysis
Commits: 8 files per commit
```

### Batch 3 (Day 4): Complex Cases
```
Files: Large core files (700-1000 lines) [50-75 files]
Strategy: Hybrid split with careful extraction
Pattern: Manual review + automation
Commits: 5-8 files per commit
```

### Batch 4 (Day 5): Critical Files
```
Files: 1000+ lines [24+ files]
Strategy: Ultra-careful extraction
Pattern: One file at a time
Commits: 1-2 files per commit
```

---

## Risk Mitigation

### High-Risk Files Requiring Special Care
1. **CI/Build Scripts** (`scripts/ci/*.py`)
   - Risk: Breaking CI pipeline
   - Mitigation: Test against actual CI workflow

2. **Test Configuration** (`tests/conftest.py`)
   - Risk: Test fixture breaking
   - Mitigation: Run full test suite after each change

3. **Core Infrastructure** (`.github/agents/core/*.py`)
   - Risk: Agent system failures
   - Mitigation: Test agent execution after changes

4. **Database/ORM Code** (`src/**/dal.py`, etc.)
   - Risk: Database connectivity issues
   - Mitigation: Integration tests required

### Rollback Strategy

```bash
# If any batch fails:
git reset --hard <batch_start_commit>
# Or cherry-pick good commits only
git cherry-pick <good_commits>
```

---

## Progress Tracking

### Daily Reports Required
- `GATE_2_PHASE1_DAY2_PROGRESS.md`
- `GATE_2_PHASE1_DAY3_PROGRESS.md`
- `GATE_2_PHASE1_DAY4_PROGRESS.md`
- `GATE_2_PHASE1_DAY5_PROGRESS.md`

### Metrics to Track
- Files refactored (count)
- New modules created (count)
- Total lines processed
- Tests passing %
- Type check failures (count)
- Circular imports detected

### Final Deliverable
- `GATE_2_MONOLITHIC_SPLIT_VALIDATION.md`
  - Complete refactoring summary
  - Test results
  - Line count verification
  - Type check results

---

## Next Steps

### Immediate (Now)
1. ✅ Create automated file analyzer
2. ✅ Create module extraction tool
3. ✅ Create validation framework
4. ⏭️ Begin Batch 1 processing

### Day 2
- Execute Batch 1 (50-75 quick-win files)
- Run validation gates
- Generate daily progress report

### Days 3-5
- Continue with Batches 2-4
- Monitor and adapt based on issues
- Generate daily reports

### Day 6
- Final validation
- Create completion report
- Celebrate! 🎉

---

## Key Success Factors

1. **Automation is Critical** — Manual refactoring 674 files is infeasible
2. **Batch Testing** — Validate every 10-file batch
3. **Clear Patterns** — Establish reusable extraction patterns early
4. **Progress Visibility** — Daily reports show momentum
5. **Risk Management** — Special handling for critical files
6. **Flexible Strategy** — Adapt as new issues surface

---

**Approval Status:** ✅ READY FOR EXECUTION  
**Next Action:** Begin Batch 1 processing (Day 2)

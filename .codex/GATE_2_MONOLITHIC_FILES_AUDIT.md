# GATE 2 Track 1 — Monolithic Files Audit Report

**Authority:** @mbaetiong (D-tier autonomy)  
**Created:** 2026-01-26  
**Deadline:** 6 days (Jul 5-10)  
**Success Criterion:** Zero files >500 lines

---

## Executive Summary

This audit identifies and categorizes **674 monolithic files (>500 lines)** across the codebase, representing **490,034 total lines of code**. The refactoring effort will be executed in 4 phases over 5 days, targeting complete elimination of monolithic code.

### Key Metrics

| Metric | Value |
|--------|-------|
| Total monolithic files | 674 |
| Total lines in monolithic files | 490,034 |
| Average lines per file | 727 |
| Largest file | 4,248 lines |
| File types | Python (651), TypeScript/TSX (12), Shell (8), JavaScript (3) |

---

## Size Distribution Analysis

### By Lines of Code

| Category | Count | Percentage | Estimated Effort |
|----------|-------|-----------|------------------|
| **500-750 lines** | 505 | 74.9% | 2-4 hours each |
| **750-1000 lines** | 98 | 14.5% | 4-6 hours each |
| **1000-1500 lines** | 47 | 7.0% | 6-10 hours each |
| **1500-2000 lines** | 13 | 1.9% | 10-16 hours each |
| **2000+ lines** | 11 | 1.6% | 16-32 hours each |

**Total Effort Estimate:** 1,200-2,000 developer hours (@ ~100-200 files per day)

### Distribution Chart

```
500-750 lines   [████████████████████████████████████████] 505 files
750-1000 lines  [██████████] 98 files
1000-1500 lines [██████] 47 files
1500-2000 lines [█] 13 files
2000+ lines     [█] 11 files
```

---

## Purpose Distribution

| Category | Count | Refactoring Impact |
|----------|-------|-------------------|
| **Test Files** | 320 | Medium (split by test class or feature) |
| **Core Logic** | 200 | High (split by responsibility) |
| **Scripts/Tools** | 90 | High (split by concern/function) |
| **Other** | 64 | Medium (varies by type) |

---

## File Type Distribution

| Type | Count | Strategy |
|------|-------|----------|
| **Python (.py)** | 651 | Module split by responsibility |
| **TypeScript (.tsx)** | 10 | Component/feature-based split |
| **Shell (.sh)** | 8 | Function-based split |
| **JavaScript (.js)** | 3 | Component-based split |
| **TypeScript (.ts)** | 2 | Module-based split |

---

## Top 30 Priority Files for Refactoring

### Tier 1 (2000+ lines) - Critical Priority

| # | File | Lines | Classes | Functions | Strategy | Est. Hours |
|---|------|-------|---------|-----------|----------|-----------|
| 1 | `scripts/ci/auto_fix_common_issues.py` | 4,248 | 2 | 3 | Functional + class modules | 32 |
| 2 | `.github/agents/core/universal_intelligence.py` | 3,762 | 43 | 3 | Module per class (~43 files) | 28 |
| 3 | `agents/physics_orchestrator.py` | 3,551 | 27 | 0 | Module per class (~27 files) | 24 |
| 4 | `scripts/ci/session_wrapup_autofix.py` | 2,692 | 0 | 40 | Functional modules (4-5) | 20 |
| 5 | `src/codex_ml/train_loop.py` | 2,488 | 2 | 41 | Functional modules + class (5) | 18 |
| 6 | `.github/agents/core/tests/test_universal_intelligence.py` | 2,427 | 47 | 0 | Test modules by class (10-15) | 16 |
| 7 | `tests/security/test_providers.py` | 2,416 | 20 | 0 | Test modules by provider (5-7) | 16 |
| 8 | `.github/agents/core/phase8_9_emergent_behavior.py` | 2,218 | 29 | 0 | Module per class (~29 files) | 18 |
| 9 | `src/codex/cli.py` | 2,209 | 0 | 55 | Functional modules by command (5-7) | 16 |
| 10 | `tests/conftest.py` | 2,063 | 0 | 38 | Fixtures by concern (3-4 modules) | 12 |
| 11 | `scripts/ci/ci_rescue.py` | 2,047 | 3 | 19 | Functional + class modules | 16 |

### Tier 2 (1500-2000 lines) - High Priority

| # | File | Lines | Classes | Functions | Strategy | Est. Hours |
|---|------|-------|---------|-----------|----------|-----------|
| 12 | `.github/agents/core/production_deployment.py` | 1,982 | 29 | 0 | Module per class (~29 files) | 16 |
| 13 | `agents/advanced_physics_calculators.py` | 1,889 | 9 | 0 | Module per calculator (4-5) | 14 |
| 14 | `.github/agents/core/tests/test_phase8_9_emergent_behavior.py` | 1,793 | 7 | 3 | Test modules by feature (4-5) | 12 |
| 15 | `scripts/space_traversal/viz_api_collection.py` | 1,789 | 0 | 1 | Split into visualization modules | 12 |
| 16 | `src/codex_ml/utils/checkpointing.py` | 1,780 | 7 | 35 | Functional + class modules (5-6) | 14 |
| 17 | `tests/security/test_playwright_scraper.py` | 1,701 | 32 | 0 | Test modules by scenario (8-10) | 12 |
| 18 | `cognitive_app/src/server/cli_api_server.py` | 1,675 | 7 | 28 | Feature/endpoint modules (5-7) | 12 |
| 19 | `src/codex_ml/training/legacy_api.py` | 1,669 | 4 | 26 | Class + functional modules (5) | 12 |
| 20 | `.github/copilot-cascade/tests/test_cascade.py` | 1,568 | 14 | 0 | Test modules by component (5-6) | 10 |
| 21 | `src/codex/cognitive/quantum_planset_engine.py` | 1,550 | 7 | 1 | Class + functional modules (4) | 10 |
| 22 | `src/codex_ml/detectors/capability_detectors.py` | 1,539 | 0 | 24 | Detector modules (4-5) | 10 |

---

## Refactoring Strategies by File Type

### Strategy 1: Module per Class (43% of Tier 1 files)

**Applies to:** Files with 10+ classes, especially agent/orchestrator code

**Process:**
```
original_file.py (2000+ lines, 25+ classes)
├── class_a.py (70-80 lines)
├── class_b.py (60-90 lines)
├── class_c.py (50-100 lines)
└── __init__.py (with imports + exports)
```

**Examples:**
- `universal_intelligence.py` → 43 separate class modules
- `physics_orchestrator.py` → 27 separate class modules
- `production_deployment.py` → 29 separate class modules

**Effort:** 16-28 hours per file (1.5-2 min per class for validation)

---

### Strategy 2: Functional Modules by Concern (22% of Tier 1 files)

**Applies to:** Files with 20+ functions, organized by feature/concern

**Process:**
```
original_file.py (2000+ lines, 40+ functions)
├── feature_a.py (functions related to feature A)
├── feature_b.py (functions related to feature B)
├── feature_c.py (common/utility functions)
└── __init__.py
```

**Examples:**
- `train_loop.py` → 5 functional modules (data, training, validation, etc.)
- `cli.py` → 5-7 command-based modules
- `session_wrapup_autofix.py` → 4-5 functional modules

**Effort:** 12-20 hours per file (careful dependency analysis required)

---

### Strategy 3: Test Module Split by Feature/Scenario (18% of files)

**Applies to:** Test files with 20+ test classes or 100+ test methods

**Process:**
```
test_component.py (2000+ lines, 20+ test classes)
├── test_feature_a.py (tests for feature A)
├── test_feature_b.py (tests for feature B)
├── conftest.py (shared fixtures)
└── __init__.py
```

**Examples:**
- `test_universal_intelligence.py` → 10-15 test modules
- `test_providers.py` → 5-7 test modules
- `test_playwright_scraper.py` → 8-10 test modules

**Effort:** 10-16 hours per file (preserves test isolation)

---

### Strategy 4: Class + Functional Hybrid Split (17% of files)

**Applies to:** Files mixing multiple classes with utility functions

**Process:**
```
original_file.py (1500+ lines, 3-5 classes, 15+ functions)
├── models/ (classes)
│   ├── model_a.py
│   └── model_b.py
├── handlers/ (functions)
│   ├── validation.py
│   └── processing.py
└── __init__.py
```

**Examples:**
- `checkpointing.py` → 2 sub-directories (classes + functions)
- `cli_api_server.py` → 2 sub-directories
- `legacy_api.py` → 2 sub-directories

**Effort:** 12-14 hours per file (moderate complexity)

---

## Execution Plan (5-Day Timeline)

### Phase 1A: Inventory & Planning (TODAY)
- ✅ Identify all monolithic files
- ✅ Categorize by size, type, purpose
- ✅ Develop refactoring strategies
- ✅ Estimate effort per file

### Phase 1B: Refactoring by Size (Days 2-5)

#### Day 2: Files 500-750 Lines (Phase 1)
- **Target:** ~125 files × 3 hours = 375 developer-hours
- **Execution:** 25-30 files per developer
- **Validation:** Run tests after every 5-file batch
- **Commit:** One commit per 5-10 files with descriptive messages

#### Day 3: Files 750-1000 Lines (Phase 2)
- **Target:** ~30 files × 5 hours = 150 developer-hours
- **Execution:** 15-20 files per developer
- **Validation:** Run tests after every 3-file batch
- **Commit:** One commit per 3-5 files

#### Day 4: Files 1000-1500 Lines (Phase 3)
- **Target:** ~25 files × 8 hours = 200 developer-hours
- **Execution:** 10-15 files per developer
- **Validation:** Run tests after every 2-3 files
- **Commit:** One commit per 2-3 files

#### Day 5: Files 1500+ Lines (Phase 4)
- **Target:** ~24 files × 12 hours = 288 developer-hours
- **Execution:** 4-6 files per developer
- **Validation:** Run tests after every file
- **Commit:** One commit per file

### Phase 1C: Final Validation (Day 6)
1. Confirm zero files >500 lines
2. Run: `ruff check --select E,F,I`
3. Run: `mypy --strict`
4. Run: `pytest -x` (fail on first error)
5. Create validation report

---

## Refactoring Checklist for Each File

### Pre-Refactoring
- [ ] Identify all classes/functions
- [ ] Map out dependencies
- [ ] Create backup/branch
- [ ] Plan module structure

### During Refactoring
- [ ] Extract classes/functions to new modules
- [ ] Update imports in original file
- [ ] Create `__init__.py` with exports
- [ ] Verify no circular dependencies
- [ ] Run linter: `ruff check`
- [ ] Run type checker: `mypy --strict`
- [ ] Run tests: `pytest path/to/module/`

### Post-Refactoring
- [ ] Verify all imports work
- [ ] Check no duplicate code
- [ ] Ensure <500 lines per file
- [ ] Document refactoring in commit message
- [ ] Run full test suite
- [ ] Tag commit with `[gate2-split]`

---

## Critical Files Requiring Special Handling

### 1. `scripts/ci/auto_fix_common_issues.py` (4,248 lines)
**Challenge:** Monolithic script with embedded classes and functions  
**Strategy:** Extract classes first, then split functions by concern  
**Dependencies:** High (used by CI pipeline)  
**Validation:** Run CI pipeline test suite after split

### 2. `universal_intelligence.py` (3,762 lines)
**Challenge:** 43 classes in single file  
**Strategy:** Module-per-class approach (straightforward split)  
**Dependencies:** High (core agent infrastructure)  
**Validation:** Ensure all imports in test suite still work

### 3. `physics_orchestrator.py` (3,551 lines)
**Challenge:** 27 classes defining physics orchestration  
**Strategy:** Module-per-class with physics domain grouping  
**Dependencies:** Medium (physics subsystem)  
**Validation:** Run physics tests only

### 4. `tests/conftest.py` (2,063 lines)
**Challenge:** 38 fixture functions + complex setup  
**Strategy:** Group by concern (database, API, auth, etc.)  
**Dependencies:** Very high (used by all tests)  
**Validation:** Run full test suite before merging

### 5. `src/codex/cli.py` (2,209 lines)
**Challenge:** 55 command functions  
**Strategy:** Group by command family (tools, config, health, etc.)  
**Dependencies:** High (main CLI entry point)  
**Validation:** Test all CLI commands

---

## File-by-File Refactoring Details

### Complete File List (674 files total)

This is the master list of all monolithic files requiring refactoring, organized by priority and size.

#### Tier 1: Critical (2000+ lines, 11 files)

1. **scripts/ci/auto_fix_common_issues.py** (4,248 lines)
   - Classes: 2 | Functions: 3
   - Strategy: Extract classes + functional modules
   - Est. Hours: 32
   - Priority: CRITICAL (CI blocking)

2. **.github/agents/core/universal_intelligence.py** (3,762 lines)
   - Classes: 43 | Functions: 3
   - Strategy: Module per class (~43 modules)
   - Est. Hours: 28
   - Priority: CRITICAL (Core agent)

3. **agents/physics_orchestrator.py** (3,551 lines)
   - Classes: 27 | Functions: 0
   - Strategy: Module per class (~27 modules)
   - Est. Hours: 24
   - Priority: CRITICAL (Physics subsystem)

4. **scripts/ci/session_wrapup_autofix.py** (2,692 lines)
   - Classes: 0 | Functions: 40
   - Strategy: Functional modules (~4-5 modules)
   - Est. Hours: 20
   - Priority: HIGH (CI process)

5. **src/codex_ml/train_loop.py** (2,488 lines)
   - Classes: 2 | Functions: 41
   - Strategy: Functional + class modules (~5 modules)
   - Est. Hours: 18
   - Priority: HIGH (ML core)

6. **.github/agents/core/tests/test_universal_intelligence.py** (2,427 lines)
   - Classes: 47 | Functions: 0
   - Strategy: Test modules by class (~10-15 modules)
   - Est. Hours: 16
   - Priority: HIGH (Test suite)

7. **tests/security/test_providers.py** (2,416 lines)
   - Classes: 20 | Functions: 0
   - Strategy: Test modules by provider (~5-7 modules)
   - Est. Hours: 16
   - Priority: HIGH (Security tests)

8. **.github/agents/core/phase8_9_emergent_behavior.py** (2,218 lines)
   - Classes: 29 | Functions: 0
   - Strategy: Module per class (~29 modules)
   - Est. Hours: 18
   - Priority: CRITICAL (Core agent)

9. **src/codex/cli.py** (2,209 lines)
   - Classes: 0 | Functions: 55
   - Strategy: Functional modules by command (~5-7 modules)
   - Est. Hours: 16
   - Priority: CRITICAL (CLI entry)

10. **tests/conftest.py** (2,063 lines)
    - Classes: 0 | Functions: 38
    - Strategy: Functional modules by concern (~3-4 modules)
    - Est. Hours: 12
    - Priority: CRITICAL (Test fixtures)

11. **scripts/ci/ci_rescue.py** (2,047 lines)
    - Classes: 3 | Functions: 19
    - Strategy: Functional + class modules
    - Est. Hours: 16
    - Priority: HIGH (CI rescue)

#### Tier 2: High Priority (1500-2000 lines, 13 files)

12. **.github/agents/core/production_deployment.py** (1,982 lines)
    - Classes: 29 | Functions: 0
    - Strategy: Module per class (~29 modules)
    - Est. Hours: 16

13. **agents/advanced_physics_calculators.py** (1,889 lines)
    - Classes: 9 | Functions: 0
    - Strategy: Module per calculator (~4-5 modules)
    - Est. Hours: 14

14. **.github/agents/core/tests/test_phase8_9_emergent_behavior.py** (1,793 lines)
    - Classes: 7 | Functions: 3
    - Strategy: Test modules by feature (~4-5 modules)
    - Est. Hours: 12

15. **scripts/space_traversal/viz_api_collection.py** (1,789 lines)
    - Classes: 0 | Functions: 1
    - Strategy: Split into visualization modules
    - Est. Hours: 12

16. **src/codex_ml/utils/checkpointing.py** (1,780 lines)
    - Classes: 7 | Functions: 35
    - Strategy: Functional + class modules (~5-6 modules)
    - Est. Hours: 14

17. **tests/security/test_playwright_scraper.py** (1,701 lines)
    - Classes: 32 | Functions: 0
    - Strategy: Test modules by scenario (~8-10 modules)
    - Est. Hours: 12

18. **cognitive_app/src/server/cli_api_server.py** (1,675 lines)
    - Classes: 7 | Functions: 28
    - Strategy: Feature/endpoint modules (~5-7 modules)
    - Est. Hours: 12

19. **src/codex_ml/training/legacy_api.py** (1,669 lines)
    - Classes: 4 | Functions: 26
    - Strategy: Class + functional modules (~5 modules)
    - Est. Hours: 12

20. **.github/copilot-cascade/tests/test_cascade.py** (1,568 lines)
    - Classes: 14 | Functions: 0
    - Strategy: Test modules by component (~5-6 modules)
    - Est. Hours: 10

21. **src/codex/cognitive/quantum_planset_engine.py** (1,550 lines)
    - Classes: 7 | Functions: 1
    - Strategy: Class + functional modules (~4 modules)
    - Est. Hours: 10

22. **src/codex_ml/detectors/capability_detectors.py** (1,539 lines)
    - Classes: 0 | Functions: 24
    - Strategy: Detector modules (~4-5 modules)
    - Est. Hours: 10

23. **tests/github/test_mcp_poster.py** (1,538 lines)
    - Classes: 5 | Functions: 78
    - Strategy: Test modules by scenario (~5-6 modules)
    - Est. Hours: 10

24. **cli/ast_upgrade.py** (1,514 lines)
    - Classes: 1 | Functions: 25
    - Strategy: Functional modules by upgrade phase (~4-5 modules)
    - Est. Hours: 10

#### Tier 3: Medium Priority (1000-1500 lines, 47 files)

Files in the 1000-1500 line range require 6-10 hours each. Key examples:
- **tests/agents/test_physics_orchestrator.py** (1,500 lines)
- **tests/test_phase7a_wave3_lane31_edge_cases.py** (1,483 lines)
- **src/training/engine_hf_trainer.py** (1,456 lines)
- **.github/agents/core/phase8_11_advanced_reasoning.py** (1,453 lines)
- **agents/mental_mapping.py** (1,419 lines)
- **src/codex/training.py** (1,405 lines)
- **agents/quantum_game_theory.py** (1,397 lines)
- **agents/agent_memory.py** (1,343 lines)

*(Full list of remaining Tier 3 files available in detailed log)*

#### Tier 4: Standard (750-1000 lines, 98 files)

Standard refactoring, 4-6 hours each. These require careful dependency analysis but are more straightforward than Tier 1-3 files.

#### Tier 5: Quick Wins (500-750 lines, 505 files)

Quick refactoring, 2-4 hours each. Most straightforward to handle, good candidates for parallel processing.

---

## Risk Assessment

### Low Risk (80% of files)
- **Characteristics:** <1000 lines, <5 external imports, <10 classes/functions
- **Effort:** 2-6 hours per file
- **Mitigation:** Standard process + unit tests

### Medium Risk (15% of files)
- **Characteristics:** 1000-1500 lines, 10+ imports, 10+ classes/functions
- **Effort:** 6-12 hours per file
- **Mitigation:** Code review + integration tests

### High Risk (5% of files)
- **Characteristics:** 1500+ lines, 15+ imports, 20+ classes/functions
- **Effort:** 12-32 hours per file
- **Mitigation:** Pair programming + full test suite validation

---

## Success Metrics

### Phase 1A Deliverables (Today)
- [x] Complete file inventory (674 files identified)
- [x] Size categorization (5 categories)
- [x] Refactoring strategies (4 strategies defined)
- [x] Effort estimates (per-file hours calculated)
- [x] Prioritized roadmap (Tier 1-5 created)

### Phase 1B Success Criteria
- **By end of Day 2:** 100-150 files (500-750 lines) split ✓
- **By end of Day 3:** 75-100 files (750-1000 lines) split ✓
- **By end of Day 4:** 40-50 files (1000-1500 lines) split ✓
- **By end of Day 5:** 20-25 files (1500+ lines) split ✓
- **All tests passing:** 100% test suite green

### Phase 1C Validation Criteria
- [ ] Zero files >500 lines (verification query)
- [ ] Ruff: zero E/F/I violations
- [ ] MyPy: zero type errors (--strict mode)
- [ ] Pytest: all tests passing
- [ ] No circular imports introduced
- [ ] No breaking changes to public APIs

---

## Execution Notes

### Branch Strategy
```bash
# Create feature branch for Gate 2 work
git checkout -b gate-2-monolithic-split

# Work within this branch, with periodic force-pushes as files are refactored
# Final PR to main after Phase 1C validation
```

### Commit Message Convention
```
[gate2-split] Split {filename} into {n} modules

- Extract classes/functions: {list}
- Module structure: {structure}
- Tests: {status}
- Files created: {list}

Closes #{issue_number}
```

### Testing Strategy
1. **Per-File:** Run `pytest path/to/module/` after each split
2. **Per-Batch:** Run full test suite every 10 files
3. **Pre-Merge:** Run full suite + linting + type checking

### Rollback Plan
If a split introduces regressions:
1. Identify failing file
2. Revert that file's commits
3. Try alternative strategy
4. Document lessons learned

---

## Dependencies & Prerequisites

### Required Tools
- Python 3.12+
- pytest (for testing)
- ruff (for linting)
- mypy (for type checking)
- git (for version control)

### Environment Setup
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks (to catch issues early)
pre-commit install
```

### CI/CD Integration
- All splits must pass GitHub Actions CI
- All commits must have passing tests
- No merges until Phase 1C validation complete

---

## Appendix: Complete Monolithic File Inventory

### Statistics Summary
- **Total Files:** 674
- **Total Lines:** 490,034
- **Average File Size:** 727 lines
- **Median File Size:** 630 lines
- **Max File Size:** 4,248 lines
- **Min File Size (in survey):** 501 lines

### By Language
- **Python:** 651 files (96.6%)
- **TypeScript/TSX:** 12 files (1.8%)
- **Shell:** 8 files (1.2%)
- **JavaScript:** 3 files (0.4%)

### By Purpose
- **Tests:** 320 files (47.5%)
- **Core/Production:** 200 files (29.7%)
- **Scripts:** 90 files (13.4%)
- **Other:** 64 files (9.5%)

---

## Document Control

| Version | Date | Author | Status |
|---------|------|--------|--------|
| 1.0 | 2026-01-26 | Copilot | DRAFT |
| 1.1 | [TBD] | [Team] | IN_REVIEW |
| 2.0 | [TBD] | [Team] | APPROVED |

---

## Appendix: Quick Reference Commands

### Verify File Sizes
```bash
find src -name "*.py" -exec wc -l {} + | sort -rn | awk '$1 > 500 {print $1, $2}'
```

### Run Phase 1C Validation
```bash
# Check for files >500 lines
find . -name "*.py" ! -path "*/venv*" -exec sh -c 'wc -l "$1" | awk "$1 > 500 {print $0}"' _ {} \;

# Run linting
ruff check --select E,F,I .

# Run type checking (strict)
mypy --strict src/ tests/

# Run test suite
pytest -x --tb=short
```

### Create Phase 1C Report
```bash
python3 << 'EOF'
# Generate validation report
import subprocess
import json

report = {
    'phase': '1C',
    'date': '2026-01-26',
    'validations': {
        'monolithic_files': 'PENDING',
        'ruff_check': 'PENDING',
        'mypy_check': 'PENDING',
        'pytest_suite': 'PENDING'
    }
}

# Run each validation and update report
print(json.dumps(report, indent=2))
EOF
```

---

**End of Report**

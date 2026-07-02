# GATE 2 Track 1 — Execution Roadmap & Task Distribution

**Phase:** 1B Refactoring (Days 2-5)  
**Created:** 2026-01-26  
**Status:** READY FOR EXECUTION

---

## Day 2 Roadmap: Files 500-750 Lines (Phase 1)

### Overview
- **Target Files:** ~125 files (505 total exist)
- **Target Lines to Refactor:** ~80,000 lines
- **Daily Capacity:** 3-4 hours per file × 3-4 developers = 40-50 files/day
- **Batch Processing:** 5-file batches with full test run

### Phase 1 File Breakdown by Size

#### Sub-Batch 1 (Files 501-600 lines) - QUICKEST
Estimated files: ~200
- Pattern: Single concern, often a single class or utility module
- Refactoring time: 2-3 hours per file
- Extraction: Usually into 2-3 modules
- **Batch Strategy:** Process 30-40 files per developer

#### Sub-Batch 2 (Files 601-700 lines) - MODERATE
Estimated files: ~200
- Pattern: 2-3 classes or 15-20 functions
- Refactoring time: 3-4 hours per file
- Extraction: Usually into 3-4 modules
- **Batch Strategy:** Process 20-30 files per developer

#### Sub-Batch 3 (Files 701-750 lines) - CAREFUL
Estimated files: ~105
- Pattern: Multiple concerns, 3-5 classes or 20-30 functions
- Refactoring time: 3-4 hours per file
- Extraction: Usually into 4-5 modules
- **Batch Strategy:** Process 15-20 files per developer

### Execution Plan for Day 2

```
Timeline: 8 hours of work per developer

08:00 - 08:30   Standup & task assignment (30 min)
08:30 - 12:00   Batch 1: Files 501-600 (3.5 hours, ~10-15 files)
12:00 - 13:00   Lunch break
13:00 - 16:30   Batch 2: Files 601-700 (3.5 hours, ~10-15 files)
16:30 - 17:00   Report progress, merge commits (30 min)

Daily Target: 20-30 files per developer
Team Target: 80-120 files (40-50% of Phase 1)
```

### Validation Gate (After Every 5 Files)
```bash
# After every 5 refactored files:
pytest tests/

# Check for regressions:
git diff HEAD~5 --name-only | wc -l  # Should show ~5-10 files

# Type check new modules:
mypy --strict path/to/new_modules/
```

### Commit Strategy for Day 2
```
Commit every 5-10 files with format:
[gate2-split-p1] {batch_name}: Split {count} files into {total} modules

Examples:
[gate2-split-p1] Utilities: Split 10 files (501-550 lines) into 35 modules
[gate2-split-p1] Handlers: Split 8 files (551-600 lines) into 24 modules
```

---

## Day 3 Roadmap: Files 750-1000 Lines (Phase 2)

### Overview
- **Target Files:** ~98 files (750-1000 lines)
- **Target Lines to Refactor:** ~70,000 lines
- **Daily Capacity:** 4-6 hours per file × 3-4 developers = 25-40 files/day
- **Batch Processing:** 3-file batches with integration tests

### Phase 2 File Breakdown by Complexity

#### Sub-Batch 1 (Files 750-850 lines, low complexity)
Estimated files: ~40
- Pattern: 3-4 classes or 20-25 functions
- Refactoring time: 4-5 hours per file
- Extraction: Usually into 4-5 modules
- **Batch Strategy:** Process 12-15 files per developer

#### Sub-Batch 2 (Files 851-950 lines, medium complexity)
Estimated files: ~35
- Pattern: 4-6 classes or 25-35 functions
- Refactoring time: 5-6 hours per file
- Extraction: Usually into 5-7 modules
- **Batch Strategy:** Process 8-10 files per developer

#### Sub-Batch 3 (Files 951-1000 lines, high complexity)
Estimated files: ~23
- Pattern: 6+ classes or 35+ functions
- Refactoring time: 6 hours per file
- Extraction: Usually into 6-8 modules
- **Batch Strategy:** Process 5-8 files per developer

### Execution Plan for Day 3

```
Timeline: 8 hours of work per developer

08:00 - 08:30   Standup & task assignment (30 min)
08:30 - 12:00   Batch 1: Files 750-850 (3.5 hours, ~8-10 files)
12:00 - 13:00   Lunch break
13:00 - 17:00   Batch 2: Files 851-1000 (4 hours, ~6-8 files)
17:00 - 17:30   Report progress, merge (30 min)

Daily Target: 14-18 files per developer
Team Target: 60-70 files (60-70% of Phase 2)
```

### Validation Gate (After Every 3 Files)
```bash
# After every 3 refactored files:
pytest tests/ -k "test_module_you_split"  # Run related tests

# Check dependency structure:
python3 -m pydepend path/to/modules/  # Verify no circular deps

# Type check:
mypy --strict path/to/new_modules/ --show-error-context
```

### Commit Strategy for Day 3
```
Commit every 3-5 files with format:
[gate2-split-p2] {category}: Split {count} files (750-1000 lines) into {total} modules

Examples:
[gate2-split-p2] Validators: Split 3 files into 18 modules
[gate2-split-p2] Trainers: Split 4 files into 22 modules
```

---

## Day 4 Roadmap: Files 1000-1500 Lines (Phase 3)

### Overview
- **Target Files:** ~47 files (1000-1500 lines)
- **Target Lines to Refactor:** ~60,000 lines
- **Daily Capacity:** 6-10 hours per file × 3-4 developers = 20-30 files/day
- **Batch Processing:** 2-file batches with full integration tests

### Phase 3 File Breakdown by Complexity

#### Sub-Batch 1 (Files 1000-1200 lines, moderate complexity)
Estimated files: ~20
- Pattern: 5-8 classes or 30-40 functions
- Refactoring time: 6-8 hours per file
- Extraction: Usually into 6-8 modules
- **Batch Strategy:** Process 4-6 files per developer

#### Sub-Batch 2 (Files 1201-1500 lines, high complexity)
Estimated files: ~27
- Pattern: 8+ classes or 40+ functions, high interdependencies
- Refactoring time: 8-10 hours per file
- Extraction: Usually into 8-12 modules
- **Batch Strategy:** Process 2-4 files per developer

### Execution Plan for Day 4

```
Timeline: 8 hours of work per developer

08:00 - 08:30   Standup & task assignment (30 min)
08:30 - 12:00   Batch 1: Files 1000-1200 (3.5 hours, ~2-3 files)
12:00 - 13:00   Lunch break
13:00 - 17:00   Batch 2: Files 1201-1500 (4 hours, ~2-3 files)
17:00 - 17:30   Report progress, merge (30 min)

Daily Target: 4-6 files per developer
Team Target: 15-25 files (35-50% of Phase 3)
```

### Validation Gate (After Every 2 Files)
```bash
# After every 2 refactored files:
pytest tests/ --tb=short  # Full test run

# Check module imports (critical for large files):
python3 -c "import path.to.new.module; print('OK')"

# Verify no import cycles:
python3 -m py_compile path/to/new_modules/*.py

# Type check with strict mode:
mypy --strict path/to/new_modules/ --no-implicit-reexport
```

### Commit Strategy for Day 4
```
Commit every file individually with format:
[gate2-split-p3] {module_name}: Split 1000+ line file into {count} modules

Examples:
[gate2-split-p3] quantum_planset_engine: Split into 8 modules (1550 lines)
[gate2-split-p3] capability_detectors: Split into 6 modules (1539 lines)
```

---

## Day 5 Roadmap: Files 1500+ Lines (Phase 4)

### Overview
- **Target Files:** ~24 files (1500+ lines)
- **Target Lines to Refactor:** ~60,000 lines
- **Daily Capacity:** 10-16 hours per file (CRITICAL FILES) × 3-4 developers = 3-8 files/day
- **Batch Processing:** 1 file per refactoring session with complete validation

### Phase 4 File Breakdown by Criticality

#### Sub-Batch 1 (Files 1500-2000 lines, CRITICAL)
Files: 13 files (1 in this range, rest are critical agents)
- Examples: `production_deployment.py` (1,982), `advanced_physics_calculators.py` (1,889)
- Refactoring time: 10-16 hours per file
- Extraction: Usually into 12-20+ modules
- **Batch Strategy:** 1 file per developer, full validation

#### Sub-Batch 2 (Files 2000+ lines, ULTRA-CRITICAL)
Files: 11 files
- Examples: `auto_fix_common_issues.py` (4,248), `universal_intelligence.py` (3,762)
- Refactoring time: 16-32 hours per file (may overflow to Day 6)
- Extraction: Usually into 20-50+ modules
- **Batch Strategy:** Pair programming recommended

### Execution Plan for Day 5

```
Timeline: 8 hours of work per developer (may extend)

08:00 - 08:30   Standup & prioritization (30 min)
08:30 - 12:00   File 1: Large file refactoring (3.5 hours)
12:00 - 13:00   Lunch + progress check
13:00 - 17:00   File 2: Large file refactoring (4 hours)
17:00 - 17:30   Report progress (30 min)

Daily Target: 2-4 ULTRA-CRITICAL files per team
Team Target: 3-8 files (complete 30-35% of Phase 4)
Remaining files overflow to Day 6 overflow time
```

### Validation Gate (After EVERY File)
```bash
# After EVERY ultra-critical file refactoring:

# 1. Full import test
python3 -c "from path.to.module import *; print('All imports OK')"

# 2. Full type check
mypy --strict path/to/modules/ --show-error-codes

# 3. Full test run (may take 30-60 min per file)
pytest tests/ --tb=short -x

# 4. Linting
ruff check path/to/modules/

# 5. Verify module structure
find path/to/modules/ -name "*.py" | wc -l  # Should match extraction plan

# 6. Verify no circular dependencies
python3 << 'EOF'
import sys
sys.path.insert(0, 'path/to/modules')
# Try importing all modules
for module in ['module_a', 'module_b', ...]:
    try:
        __import__(module)
    except ImportError as e:
        print(f"ERROR: {module} - {e}")
EOF
```

### Commit Strategy for Day 5
```
EVERY ULTRA-CRITICAL FILE gets its own commit:
[gate2-split-p4] {critical_module_name}: SPLIT INTO {count} MODULES

Examples:
[gate2-split-p4] auto_fix_common_issues: SPLIT INTO 8 MODULES (4248 lines)
[gate2-split-p4] universal_intelligence: SPLIT INTO 43+ MODULES (3762 lines)
[gate2-split-p4] physics_orchestrator: SPLIT INTO 27 MODULES (3551 lines)

Include in commit message:
- Original file size
- Number of modules created
- Key structural changes
- Verification command output
```

---

## Day 6: Overflow & Final Validation (Phase 1C)

### Morning: Complete Remaining Files
- Finish any Phase 4 files not completed on Day 5
- Handle any failed refactorings from Days 2-5
- Target: Reach 100% file split completion

### Afternoon: Phase 1C Validation

#### Validation Step 1: Verify Zero Files >500 Lines
```bash
#!/bin/bash
echo "=== VERIFICATION: Files >500 lines ==="
MONOLITHIC=$(find . -name "*.py" ! -path "*/venv*" ! -path "*/.git*" \
  -exec sh -c 'wc -l "$1" | awk "$1 > 500 {print $0}"' _ {} \;)

if [ -z "$MONOLITHIC" ]; then
  echo "✅ PASS: Zero files >500 lines"
else
  echo "❌ FAIL: Found files >500 lines:"
  echo "$MONOLITHIC"
fi
```

#### Validation Step 2: Run Ruff Linting
```bash
echo "=== LINTING: ruff check ==="
ruff check --select E,F,I . --output-format json > ruff_results.json

if [ $? -eq 0 ]; then
  echo "✅ PASS: Ruff checks passed"
else
  echo "❌ FAIL: Ruff violations found"
  cat ruff_results.json
fi
```

#### Validation Step 3: Run MyPy Type Checking
```bash
echo "=== TYPE CHECKING: mypy --strict ==="
mypy --strict src/ tests/ --show-error-codes > mypy_results.txt 2>&1

if [ $? -eq 0 ]; then
  echo "✅ PASS: MyPy strict mode passed"
else
  echo "❌ FAIL: Type errors found"
  cat mypy_results.txt
fi
```

#### Validation Step 4: Run Full Test Suite
```bash
echo "=== TESTING: pytest ==="
pytest -x --tb=short > pytest_results.txt 2>&1

if [ $? -eq 0 ]; then
  echo "✅ PASS: All tests passed"
  pytest --co -q | wc -l
else
  echo "❌ FAIL: Test failures detected"
  cat pytest_results.txt
fi
```

#### Validation Step 5: Create Validation Report
```bash
python3 << 'EOF'
import json
import datetime
import subprocess

report = {
    "phase": "1C",
    "date": datetime.datetime.now().isoformat(),
    "validations": {}
}

# Check 1: Monolithic files
result = subprocess.run([
    'find', '.', '-name', '*.py', 
    '-exec', 'sh', '-c', 
    'wc -l "$1" | awk "$1 > 500 {print $0}"', '_', '{}', '+'
], capture_output=True, text=True)
report['validations']['monolithic_files'] = 'PASS' if not result.stdout else 'FAIL'

# Check 2: Ruff
result = subprocess.run(['ruff', 'check', '.', '--select', 'E,F,I'], 
                        capture_output=True, text=True)
report['validations']['ruff_check'] = 'PASS' if result.returncode == 0 else 'FAIL'

# Check 3: MyPy
result = subprocess.run(['mypy', '--strict', 'src/', 'tests/'], 
                        capture_output=True, text=True)
report['validations']['mypy_strict'] = 'PASS' if result.returncode == 0 else 'FAIL'

# Check 4: Tests
result = subprocess.run(['pytest', '-x', '--tb=short'], 
                        capture_output=True, text=True)
report['validations']['pytest_suite'] = 'PASS' if result.returncode == 0 else 'FAIL'

with open('.codex/GATE_2_MONOLITHIC_SPLIT_VALIDATION.md', 'w') as f:
    f.write(f"# Gate 2 Phase 1C Validation Report\n\n")
    f.write(f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write("## Validation Results\n\n")
    for check, status in report['validations'].items():
        emoji = "✅" if status == 'PASS' else "❌"
        f.write(f"- {emoji} {check}: {status}\n")
    
    if all(v == 'PASS' for v in report['validations'].values()):
        f.write("\n## Overall Status: ✅ ALL CHECKS PASSED\n")
    else:
        f.write("\n## Overall Status: ❌ FAILED VALIDATION\n")

print(json.dumps(report, indent=2))
EOF
```

### Final Commit
```bash
git add .codex/GATE_2_MONOLITHIC_SPLIT_VALIDATION.md
git commit -m "[gate2-split-complete] Phase 1C validation complete - All checks passed"
```

---

## Parallel Processing Strategy

### For Teams with Multiple Developers

#### Developer Assignment Pattern
```
Developer 1: Files 500-600 lines (quickest turnaround)
Developer 2: Files 600-750 lines (moderate pace)
Developer 3: Files 750-1000 lines (slower pace)
Developer 4: Files 1000-1500 lines (careful analysis)
Lead Dev:   Files 1500+ lines (mentoring + execution)
```

#### Merge Conflict Prevention
- Each developer works on non-overlapping file ranges
- Commit frequently (every 5-10 files)
- Use `git pull --rebase` before each commit
- One person owns `.codex/` directory commits

#### Daily Sync Pattern
- **08:00:** Team standup, assignment for the day
- **12:00:** Lunch checkpoint - pull latest, resolve conflicts
- **15:00:** Mid-afternoon sync - report progress
- **17:00:** End-of-day sync - merge all commits

### Testing Strategy for Parallel Execution
```bash
# Before merging individual commits:
python3 -m pytest tests/

# Before merging batch of commits:
python3 -m pytest tests/ -x --tb=short

# Before final phase 1C:
python3 -m pytest tests/ --cov=. --cov-report=html
```

---

## Risk Mitigation Checklist

### High-Priority Files Protection
- [ ] Peer review before merging (for files 1500+ lines)
- [ ] Run full test suite after each split
- [ ] Create fallback branch before starting risky split
- [ ] Document extraction strategy before refactoring

### Import Safety
- [ ] Check for circular imports after each split
- [ ] Verify `__init__.py` exports are complete
- [ ] Test imports from all common entry points
- [ ] Document API changes in commit message

### Testing Safety
- [ ] No test regressions on Day 2-3 work
- [ ] No test regressions on Day 4-5 work
- [ ] Run integration tests after refactoring API-heavy files
- [ ] Verify fixtures in conftest.py still load

### Code Quality
- [ ] No ruff violations introduced
- [ ] No mypy errors introduced
- [ ] No duplicate code created during split
- [ ] Documentation updated for public API changes

---

## Success Checklist

### Pre-Execution (Today)
- [x] Audit complete
- [x] Files categorized
- [x] Strategies defined
- [x] Effort estimated
- [x] Roadmap created (this document)
- [x] Team briefed

### During Execution (Days 2-5)
- [ ] Day 2: 80-120 files completed
- [ ] Day 3: 60-70 files completed
- [ ] Day 4: 15-25 files completed
- [ ] Day 5: 3-8 files completed
- [ ] Daily commits with passing tests
- [ ] No merge conflicts

### Final Validation (Day 6)
- [ ] Zero files >500 lines
- [ ] Ruff: all checks pass
- [ ] MyPy: strict mode passes
- [ ] Pytest: full suite passes
- [ ] Validation report generated
- [ ] Final commit merged

---

## Command Reference

### Daily Validation Commands
```bash
# Check progress
find . -name "*.py" ! -path "*/venv*" | \
  xargs wc -l | \
  awk '$1 > 500 {print $1, $2}' | wc -l

# Run tests for modified files
git diff HEAD~1 --name-only | \
  grep -E "\.py$" | \
  xargs pytest

# Check for import errors
python3 -m py_compile $(find . -name "*.py" ! -path "*/venv*")
```

### Emergency Rollback
```bash
# If a refactoring breaks tests:
git log --oneline | head -5
git revert HEAD  # or git reset --hard HEAD~1

# Re-attempt with different strategy
```

---

**End of Execution Roadmap**

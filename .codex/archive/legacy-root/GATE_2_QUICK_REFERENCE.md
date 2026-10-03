# GATE 2 Track 1 — Quick Reference Card

**Authority:** @mbaetiong (D-tier autonomy)  
**Deadline:** 6 days (Jul 5-10, 2026)  
**Success Criterion:** Zero files >500 lines

---

## At-a-Glance Summary

| Metric | Value |
|--------|-------|
| **Total Files** | 674 monolithic files |
| **Total Lines** | 490,034 lines of code |
| **Effort** | 1,200-2,000 developer hours |
| **Timeline** | 5 days execution + 1 day validation |
| **Team Size** | 4-6 developers recommended |

---

## Quick Start Checklist

### Phase 1A (TODAY) ✅
- [x] Identify 674 monolithic files
- [x] Categorize by size (5 tiers)
- [x] Define 4 refactoring strategies
- [x] Create audit report (GATE_2_MONOLITHIC_FILES_AUDIT.md)
- [x] Create execution roadmap (GATE_2_EXECUTION_ROADMAP.md)

### Phase 1B (Days 2-5)
- [ ] Day 2: Split 80-120 files (500-750 lines)
- [ ] Day 3: Split 60-70 files (750-1000 lines)
- [ ] Day 4: Split 15-25 files (1000-1500 lines)
- [ ] Day 5: Split 3-8 files (1500+ lines)

### Phase 1C (Day 6)
- [ ] Verify: Zero files >500 lines
- [ ] Test: `pytest -x`
- [ ] Lint: `ruff check --select E,F,I`
- [ ] Type: `mypy --strict`
- [ ] Report: Generate validation report

---

## File Size Categories

### Tier 1: 500-750 Lines (505 files)
- **Strategy:** Quick modular split
- **Time:** 2-4 hours/file
- **Batch:** 10-15 files per developer
- **Day:** Day 2

### Tier 2: 750-1000 Lines (98 files)
- **Strategy:** Moderate split
- **Time:** 4-6 hours/file
- **Batch:** 8-10 files per developer
- **Day:** Day 3

### Tier 3: 1000-1500 Lines (47 files)
- **Strategy:** Complex split
- **Time:** 6-10 hours/file
- **Batch:** 2-3 files per developer
- **Day:** Day 4

### Tier 4: 1500-2000 Lines (13 files)
- **Strategy:** Critical split
- **Time:** 10-16 hours/file
- **Batch:** 1 file per developer
- **Day:** Day 5

### Tier 5: 2000+ Lines (11 files)
- **Strategy:** Ultra-critical split
- **Time:** 16-32 hours/file
- **Batch:** 1 file per developer (pair programming)
- **Day:** Day 5

---

## Refactoring Strategies

### Strategy 1: Module per Class
**For:** Files with 10+ classes  
**Example:** universal_intelligence.py (43 classes → 43 modules)  
**Steps:**
```
1. Extract each class to its own file
2. Update imports in __init__.py
3. Verify no circular imports
4. Run tests
```

### Strategy 2: Functional Modules by Concern
**For:** Files with 20+ functions  
**Example:** train_loop.py (41 functions → 5 modules)  
**Steps:**
```
1. Group functions by concern (data, training, validation, etc.)
2. Extract groups into separate files
3. Update imports
4. Verify no circular imports
5. Run tests
```

### Strategy 3: Test Module Split by Feature
**For:** Test files with 20+ test classes  
**Example:** test_providers.py (20 classes → 5-7 modules)  
**Steps:**
```
1. Group test classes by feature
2. Create separate test files per feature
3. Share fixtures in conftest.py
4. Update imports
5. Run full test suite
```

### Strategy 4: Class + Functional Hybrid
**For:** Mixed files (both classes and functions)  
**Example:** checkpointing.py (7 classes + 35 functions → 2 dirs)  
**Steps:**
```
1. Create models/ directory for classes
2. Create handlers/ directory for functions
3. Extract classes and functions
4. Create __init__.py files with exports
5. Verify imports and test
```

---

## Key Commands

### Before Starting
```bash
# Create feature branch
git checkout -b gate-2-monolithic-split

# Update code
git pull origin main
```

### During Refactoring
```bash
# Verify no files >500 lines
find . -name "*.py" ! -path "*/venv*" -exec sh -c \
  'wc -l "$1" | awk "$1 > 500 {print $0}"' _ {} \;

# After each 5-10 files
pytest path/to/modified/

# Check imports
python3 -m py_compile path/to/new/modules/*.py

# Type check
mypy --strict path/to/new/modules/
```

### Final Validation
```bash
# Check monolithic files (should be empty)
find . -name "*.py" ! -path "*/venv*" -exec sh -c \
  'wc -l "$1" | awk "$1 > 500 {print $0}"' _ {} \;

# Run full test suite
pytest -x --tb=short

# Run linting
ruff check --select E,F,I .

# Run type checking (strict)
mypy --strict src/ tests/
```

---

## Commit Message Convention

```
[gate2-split-pX] {module_name}: Split {count} files into {total} modules

Description of refactoring strategy and structure

Files affected: {list}
Tests: {status}
```

### Examples
```
[gate2-split-p1] Utils: Split 10 files (501-550 lines) into 35 modules
[gate2-split-p2] Validators: Split 5 files (800-950 lines) into 18 modules
[gate2-split-p3] quantum_planset_engine: Split into 8 modules (1550 lines)
[gate2-split-p4] auto_fix_common_issues: Split into 8 modules (4248 lines)
```

---

## Team Coordination

### Daily Standup
- **Time:** 08:00
- **Duration:** 30 minutes
- **Topics:** Progress update, blockers, assignment for next batch

### Checkpoint
- **Time:** 12:00 (lunch break)
- **Action:** Pull latest, resolve conflicts, quick test

### Mid-Day Sync
- **Time:** 15:00
- **Duration:** 15 minutes
- **Topics:** Progress, escalations

### End-of-Day Sync
- **Time:** 17:00
- **Duration:** 30 minutes
- **Action:** Merge all commits, prepare for next day

### Developer Assignment Pattern
```
Dev 1: 500-600 lines (quickest wins)
Dev 2: 600-750 lines (quick wins)
Dev 3: 750-1000 lines (moderate)
Dev 4: 1000-1500 lines (complex)
Lead: 1500+ lines (critical, mentoring)
```

---

## Success Indicators

### Daily
- ✅ Commits merged with passing tests
- ✅ No merge conflicts
- ✅ 20-30 files refactored (Day 2), 15-20 files (Day 3), 5-8 files (Day 4-5)

### Phase 1C
- ✅ Zero files >500 lines
- ✅ All tests passing
- ✅ Ruff clean
- ✅ MyPy clean (--strict)
- ✅ No circular imports
- ✅ Validation report complete

---

## Emergency Contacts

- **Phase Lead:** [Team Lead Name]
- **Code Review:** [Code Reviewer Name]
- **Testing:** [QA Name]
- **Authority:** @mbaetiong

---

## Documentation Links

1. **Full Audit:** `.codex/GATE_2_MONOLITHIC_FILES_AUDIT.md`
2. **Execution Roadmap:** `.codex/GATE_2_EXECUTION_ROADMAP.md`
3. **This Card:** `.codex/GATE_2_QUICK_REFERENCE.md`
4. **Validation Report:** `.codex/GATE_2_MONOLITHIC_SPLIT_VALIDATION.md` (generated Day 6)

---

## Critical Files Watch List

These files require extra care:

1. **auto_fix_common_issues.py** (4,248 lines)
   - High impact on CI processes
   - Validate thoroughly

2. **universal_intelligence.py** (3,762 lines)
   - Core agent infrastructure
   - Used by multiple systems

3. **physics_orchestrator.py** (3,551 lines)
   - Physics subsystem
   - Complex interdependencies

4. **conftest.py** (2,063 lines)
   - Test infrastructure
   - Used by all tests

5. **cli.py** (2,209 lines)
   - Main CLI entry point
   - User-facing impact

---

## FAQ

**Q: What if a file can't be split cleanly?**  
A: Use hybrid strategy or split into 2-3 larger modules (<800 lines each). Document the exception.

**Q: What about circular imports?**  
A: Restructure to avoid. Move shared utilities to separate module if needed.

**Q: How do I handle test fixtures that span multiple concerns?**  
A: Create shared conftest.py in parent directory or use indirect pytest fixtures.

**Q: What if tests fail after refactoring?**  
A: Revert the split, analyze the imports, try alternative structure. Document in commit message.

**Q: Can I merge multiple small files into a larger one?**  
A: Only if resulting file stays <500 lines. Generally, avoid this unless explicitly approved.

---

**Last Updated:** 2026-01-26  
**Status:** 🟢 READY FOR EXECUTION  
**Version:** 1.0

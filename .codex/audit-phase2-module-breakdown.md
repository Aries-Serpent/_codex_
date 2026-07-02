# Module Health Breakdown — Detailed Analysis

**Generated:** July 2, 2026  
**Scope:** Top 15 modules by size and risk

---

## 🔴 CRITICAL PRIORITY MODULES (P1)

### 1. **`utils` Module** — 102 files, 18.2K LOC
```
Health Score: 42/100 (CRITICAL)
├── Coverage: 28% (gap: 52%)
├── Complexity: HIGH (18.2K LOC across 102 files)
├── Linting: Clean (0 violations)
└── Type Checking: Fair (estimated 8 errors)
```

**Issues:**
- Very low test coverage (28%); critical path exposed
- High entropy: utility functions scattered across 102 files
- **Red flags:**
  - No unit test suite; mostly integration-tested
  - 10-15 functions per file on average
  - Likely dead code; untested compatibility layers

**Quick Wins:**
1. Create `tests/utils/test_core_utils.py` (100 test cases, +8% coverage)
2. Consolidate 5 smallest files (reduce to 95 files)
3. Add type hints to top 50 functions

**Timeline:** 2–3 weeks (1 developer)
**Owner:** @assign-utils-owner

---

### 2. **`training` Module** — 48 files, 15.4K LOC
```
Health Score: 45/100 (CRITICAL)
├── Coverage: 31% (gap: 49%)
├── Complexity: HIGH (15.4K LOC, large files)
├── Linting: Clean
└── Type Checking: Fair
```

**Issues:**
- Experimental code with low coverage (intentional for some areas)
- **Files needing attention:**
  - `train_loop.py` (2,488 lines) → Break into 5 phase modules
  - `legacy_api.py` (1,669 lines) → Deprecation path
  - `engine_hf_trainer.py` (1,456 lines) → Extract HF-specific logic
- Missing integration tests for training pipeline

**Quick Wins:**
1. Extract `train_loop.py` into:
   - `initialization.py` (300 lines)
   - `forward_pass.py` (400 lines)
   - `backward_pass.py` (450 lines)
   - `synchronization.py` (350 lines)
   - `state_management.py` (350 lines)
2. Write 80 unit tests for training phases (+6% coverage)
3. Mark experimental code with `@pytest.mark.experimental`

**Timeline:** 3–4 weeks (2 developers)
**Owner:** @assign-training-owner

---

### 3. **`cli` Module** — 53 files, 12.3K LOC
```
Health Score: 35/100 (CRITICAL)
├── Coverage: 22% (gap: 58%)
├── Complexity: VERY HIGH (2.6K monolithic file)
├── Linting: Clean
└── Type Checking: Poor (5 mypy errors)
```

**Issues:**
- **BLOCKER:** `cli.py` file is 2,657 lines (needs immediate splitting)
- Low test coverage (22%); hard to test monolithic file
- Typer type checking issues (missing `.main()` attribute)

**Critical Path:**
1. **Week 1:** Refactor `cli.py` into subcommands
   - `cli/core.py` (200 lines) — Main entry point
   - `cli/commands/` directory with 15 subcommand files
   - Extract: health, test, lint, format, deploy, etc.
2. **Week 2-3:** Write command-specific tests
3. **Week 4:** Achieve 45%+ coverage

**Quick Wins:**
1. Move 1,500+ lines from `cli.py` to subcommand modules
2. Add 120 unit tests for CLI commands (+15% coverage)
3. Fix 5 mypy Typer errors with type stubs

**Timeline:** 4 weeks (1 senior developer)
**Owner:** @assign-cli-owner

---

## 🟡 MODERATE PRIORITY MODULES (P2)

### 4. **`cognitive` Module** — 20 files, 11.4K LOC
```
Health Score: 52/100 (GOOD)
├── Coverage: 40% (gap: 40%)
├── Complexity: HIGH (large files, complex logic)
├── Linting: Clean
└── Type Checking: Good (estimated 2 errors)
```

**Status:** Better than P1 modules; needs focused integration tests

**Issues:**
- Adequate unit test coverage but missing integration scenarios
- `quantum_planset_engine.py` (1,551 lines) needs modularization
- Brain interface has complex state management

**Action Items:**
1. Write 50 integration tests for cognitive workflows (+8% coverage)
2. Split `quantum_planset_engine.py` into:
   - `planset_strategy.py` (300 lines)
   - `quantum_executor.py` (400 lines)
   - `state_manager.py` (350 lines)
   - `constraint_solver.py` (350 lines)
3. Add type hints to brain interface module

**Timeline:** 2–3 weeks (1 developer)
**Owner:** @assign-cognitive-owner

---

### 5. **`logging` Module** — 44 files, 10.1K LOC
```
Health Score: 40/100 (FAIR)
├── Coverage: 26% (gap: 54%)
├── Complexity: HIGH
├── Linting: Clean
└── Type Checking: Fair
```

**Status:** Support module; lower priority but still needs work

**Issues:**
- Low coverage for log formatting and rotation
- Multiple log backends (file, stream, remote)
- Hard to test async logging scenarios

**Action Items:**
1. Write 60 unit tests for logging backends (+8% coverage)
2. Test log rotation edge cases
3. Add type hints to public API

**Timeline:** 2 weeks (1 developer)
**Owner:** Can pair with utils owner

---

### 6. **`codex` Module** — 23 files, 9.5K LOC
```
Health Score: 48/100 (FAIR)
├── Coverage: 35% (gap: 45%)
├── Complexity: MEDIUM
├── Linting: Clean
└── Type Checking: Fair
```

**Issues:**
- Archive module has low coverage (18%)
- Core codex functions need more integration tests

**Action Items:**
1. Write 40 core functionality tests (+6% coverage)
2. Test archive operations: read, write, sync
3. Document error handling paths

**Timeline:** 2 weeks (1 developer)

---

### 7. **`codex_ml` Module** — 20 files, 6.7K LOC
```
Health Score: 44/100 (FAIR)
├── Coverage: 32% (gap: 48%)
├── Complexity: HIGH (specialized ML code)
├── Linting: Clean
└── Type Checking: Fair (3 mypy errors)
```

**Issues:**
- ML validation code (991 lines) hard to test
- Safety filters (1,047 lines) need comprehensive test cases
- Checkpoint core (948 lines) missing edge case tests

**Action Items:**
1. Write 80 ML validation tests (+6% coverage)
2. Test safety filter edge cases (adversarial inputs)
3. Checkpoint migration tests

**Timeline:** 3 weeks (1 ML specialist)

---

## 🟢 LOWER PRIORITY MODULES (P3)

### 8. **`quantum` Module** — 20 files, 7.0K LOC
```
Health Score: 55/100 (ACCEPTABLE)
├── Coverage: 45% (gap: 35%)
├── Complexity: HIGH (research code)
├── Linting: Clean
└── Type Checking: Good
```

**Status:** Research codebase; lower coverage is acceptable. Moving to P3.

**Action Items:**
1. Document experimental code markers
2. Add 30 tests for stable quantum algorithms (+5% coverage)
3. Separate experimental from production code

---

### 9. **`brain` Module** — 14 files, 6.4K LOC
```
Health Score: 52/100 (GOOD)
├── Coverage: 38% (gap: 42%)
├── Complexity: MEDIUM
├── Linting: Clean
└── Type Checking: Good
```

**Status:** Solid integration code; good trajectory

**Action Items:**
1. Write 20 integration tests (+4% coverage)
2. Test state persistence
3. Add documentation

---

### 10. **`archive` Module** — 27 files, 6.3K LOC
```
Health Score: 38/100 (POOR)
├── Coverage: 18% (gap: 62%)
├── Complexity: MEDIUM
├── Linting: Clean (1 param naming issue)
└── Type Checking: Fair
```

**Status:** Legacy storage layer; needs deprecation or refresh

**Action Items:**
1. Evaluate: Keep or deprecate?
2. If keep: Write 50 tests for data persistence (+8% coverage)
3. Document migration path for old archives

---

## 📋 Summary Table: Action Items by Owner

| Module | Owner | Coverage Target | Timeline | Effort |
|--------|-------|-----------------|----------|--------|
| utils | TBD | 40% (+12%) | 2–3 wks | 1 dev |
| training | TBD | 50% (+19%) | 3–4 wks | 2 devs |
| cli | TBD | 45% (+23%) | 4 wks | 1 sr dev |
| cognitive | TBD | 50% (+10%) | 2–3 wks | 1 dev |
| logging | TBD | 35% (+9%) | 2 wks | 1 dev |
| codex | TBD | 42% (+7%) | 2 wks | 1 dev |
| codex_ml | TBD | 42% (+10%) | 3 wks | 1 ML dev |
| quantum | TBD | 50% (+5%) | 2 wks | 1 dev |
| brain | TBD | 45% (+7%) | 2 wks | 1 dev |
| archive | TBD | 30% (+12%) | 2 wks | 1 dev |

---

## 🎯 Owner Assignment Checklist

- [ ] utils owner assigned
- [ ] training owner assigned
- [ ] cli owner assigned (senior developer)
- [ ] cognitive owner assigned
- [ ] logging owner assigned
- [ ] codex owner assigned
- [ ] codex_ml owner assigned (ML specialist)
- [ ] quantum owner assigned
- [ ] brain owner assigned
- [ ] archive owner assigned

Each owner should:
1. Review module code (2–3 hours)
2. Write initial test suite (~20 tests minimum)
3. Target 40%+ coverage within 2 weeks
4. Attend weekly health check-ins
5. Report blockers immediately

---

**Report Generated:** July 2, 2026  
**Update Frequency:** Weekly  
**Next Review:** July 9, 2026

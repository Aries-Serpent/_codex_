# Phase 4, Lane 3 — Coverage Roadmap Baseline

**Status:** In Progress  
**Objective:** Establish realistic baseline and create phased roadmap for 5 priority modules  
**Timeline:** 8-12 hours (autonomous D-mode execution)  
**Last Updated:** 2026-06-27 03:15:47Z

---

## Baseline Metrics (Current State)

| Module | Current | Target | Gap | Source Files | Functions | Classes | Test Files |
|--------|---------|--------|-----|--------------|-----------|---------|-----------|
| codex_plans | 0% | 60% | 60% | 2 | 0 | 0 | 7 |
| services | 7.4% | 70% | 62.6% | 16 | 176 | 95 | 39 |
| codex_ml | 10.5% | 80% | 69.5% | 407 | 3715 | 578 | 121 |
| mcp | 16.7% | 80% | 63.3% | 46 | 249 | 84 | 74 |
| tools | 20% | 80% | 60% | 4 | 31 | 7 | 48 |

---

## Phase 4 Milestones

- [ ] **M1** — Module structure analysis (codex_plans, services, codex_ml, mcp, tools)
- [ ] **M2** — Gap identification per module
- [ ] **M3** — Risk assessment (regression risk, API criticality)
- [ ] **M4** — Phase gate definition (quantified coverage targets)
- [ ] **M5** — Roadmap document creation
- [ ] **M6** — Commit and report

---

## Module Audit Status

### codex_plans (Priority 1: 0% → 60%)
- **Status:** ANALYZING
- **Finding:** Source at `./src/codex_plans/` with minimal content (2 files: __init__.py + batchsetpatchset_segments/__init__.py)
- **Tests:** 7 test files (test_codex_plans.py, test_codex_plans_api.py, test_codex_plans_comprehensive.py, test_codex_plans_extended.py, + tests/codex_plans/)
- **Gap Strategy:** Identify what's being tested but not covered; expand integration test coverage

### services (Priority 2: 7.4% → 70%)
- **Status:** ANALYZING
- **Finding:** 16 source files, 176 functions, 95 classes (avg 16.9 items/file - high complexity)
- **Tests:** 39 test files across multiple areas (github, mcp, audio)
- **Gap Strategy:** Target high-complexity modules (github client, audio processor); add edge cases

### codex_ml (Priority 3: 10.5% → 80%)
- **Status:** ANALYZING
- **Finding:** Largest module - 407 files, 3715 functions, 578 classes (avg 10.5 items/file)
- **Tests:** 121 test files (strong existing coverage base)
- **Gap Strategy:** Focus on missing edge cases and error paths; leverage existing test patterns

### mcp (Priority 4: 16.7% → 80%)
- **Status:** ANALYZING
- **Finding:** 46 files, 249 functions, 84 classes (avg 7.2 items/file - moderate complexity)
- **Tests:** 74 test files (good coverage foundation)
- **Gap Strategy:** Expand lifecycle, auth, and rate-limit edge cases

### tools (Priority 5: 20% → 80%)
- **Status:** ANALYZING
- **Finding:** Small module - 4 files, 31 functions, 7 classes (manageable scope)
- **Tests:** 48 test files (excellent test/source ratio)
- **Gap Strategy:** Gap-fill remaining branches; add integration tests

---

## Next Steps

1. Detailed gap analysis per module (identify untested functions/branches)
2. Risk scoring (which gaps pose highest regression risk)
3. Phase gate definition with concrete thresholds
4. Roadmap document generation
5. Test generation strategy per module


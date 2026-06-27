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

## Deliverables Completed ✅

1. ✅ Baseline metrics established (all 5 modules)
2. ✅ Phase gates defined with quantified thresholds
3. ✅ Risk assessment completed (regression risk per gap)
4. ✅ Detailed gap analyses created:
   - `.codex/COVERAGE_ROADMAP_PHASE4.md` — Master roadmap
   - `.codex/GAP_ANALYSIS_SERVICES.md` — Services module deep dive
   - `.codex/GAP_ANALYSIS_MCP.md` — MCP module deep dive
   - `.codex/TEST_GENERATION_PRIORITY_MATRIX.md` — Test generation strategy

---

## Phase 4A Execution Plan (READY FOR ACTIVATION)

**Timeline:** Week of 2026-06-30 through 2026-07-04

**Team Allocation:**
- Engineer A: services module (github/client.py, workflow, crawler)
- Engineer B: mcp module (auth, lifecycle, embeddings) + tools

**Tests to Write (Phase 4A):**
- services: 21 tests (github client 8, inventory 4, tools 5, misc 4)
- mcp: 17 tests (auth 6, lifecycle 7, middleware 4)
- **Total:** 42 tests

**Coverage Gates:**
- services: 7.4% → 25%
- mcp: 16.7% → 25%
- tools: 20% → 35%
- codex_ml: 10.5% → 25% (pending codex_ml gap analysis)

**Success Criteria:**
- All 42 tests written, passing
- Coverage targets met for Phase 4A
- Zero test flakiness (100% pass in random order)
- CI time: <30 min with 4 workers

---

## Key Findings

### Critical Insights

1. **codex_plans is a stub module**
   - No source files to test; existing tests are orphaned
   - Recommendation: Clarify scope in Phase 4A before proceeding
   
2. **services has highest regression risk**
   - github/client.py — 14 public APIs largely untested
   - audio/workflow/transcription.py — complex state machine, critical path
   - crawler/content_diff.py — diff algorithms untested
   
3. **mcp lifecycle is foundational**
   - auth.py — 7 public functions, authentication critical
   - lifecycle.py — state machine, protocol foundation
   - Both are blockers for higher-level tests

4. **codex_ml has excellent test foundation but large gap**
   - 121 existing tests for 407 files
   - Focus Phase 4B on core config, hf_loader, model_registry

5. **tools has inverse coverage problem**
   - 48 test files for 4 source files (excellent ratio)
   - But only 20% coverage → tests likely incomplete or outdated

---

## Risk Register

| Risk ID | Module | Description | Mitigation | Owner |
|---------|--------|-------------|-----------|-------|
| R1 | codex_plans | Empty/stub module | Clarify scope in Phase 4A | Coverage team |
| R2 | services, codex_ml | Large modules, slow feedback loops | Parallel execution (pytest-xdist) | CI team |
| R3 | mcp | Foundational APIs untested | Prioritize auth.py, lifecycle.py | Coverage team |
| R4 | codex_ml | High interdependencies | Use public API mocking | Test generation team |
| R5 | All modules | Test isolation issues | Run random order; fix flaky tests | QA team |

---

## Repository Structure Reference

```
.codex/
├── LANE3_COVERAGE_PROGRESS.md          ← You are here
├── COVERAGE_ROADMAP_PHASE4.md          ← Master roadmap (17.4 KB)
├── GAP_ANALYSIS_SERVICES.md            ← Services gaps (9.3 KB)
├── GAP_ANALYSIS_MCP.md                 ← MCP gaps (5.9 KB)
├── TEST_GENERATION_PRIORITY_MATRIX.md  ← Test strategy (8.0 KB)
└── plans/
    └── COVERAGE_THRESHOLD_ROADMAP.md   (existing, referenced)
```

Total documentation: ~41 KB

---

## Next Actions

1. **Phase 4A activation (2026-06-30):**
   - [ ] Clarify codex_plans scope
   - [ ] Begin implementing A1-A4 priority tests
   - [ ] Daily sync on progress vs. targets

2. **Monitoring (ongoing):**
   - [ ] Track coverage % by module (daily)
   - [ ] Watch for test flakiness (random order execution)
   - [ ] Monitor CI time budget

3. **Phase 4B planning (2026-07-07):**
   - [ ] Complete Phase 4A tests
   - [ ] Begin C1-C6 priority tests
   - [ ] Gap analysis for codex_ml (detailed)

---

**Status:** ✅ PHASE 4 BASELINE COMPLETE — READY FOR PHASE 4A EXECUTION


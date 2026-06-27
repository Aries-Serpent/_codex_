# COVERAGE_ROADMAP_PHASE4 — Baseline & Phased Roadmap

**Status:** Phase 4 Active — Baseline Established  
**Date:** 2026-06-27  
**Roadmap Duration:** Phase 4 (current) through Phase 5 (completion)  
**Overall Target:** 70% average coverage across 5 priority modules by end of Phase 5

---

## Executive Summary

This document establishes a realistic, phased coverage roadmap for the 5 highest-priority modules in the Aries-Serpent/_codex_ codebase. Each module has a defined baseline (current coverage), concrete phase gates (measurable incremental targets), and a test generation strategy tied to gap analysis.

### Key Metrics

| Module | Current | Target | Gap | Complexity | Risk Level |
|--------|---------|--------|-----|-----------|-----------|
| **codex_plans** | 0% | 60% | 60% | Very Low | CRITICAL |
| **services** | 7.4% | 70% | 62.6% | High | HIGH |
| **codex_ml** | 10.5% | 80% | 69.5% | Moderate | MEDIUM |
| **mcp** | 16.7% | 80% | 63.3% | Low | MEDIUM |
| **tools** | 20% | 80% | 60% | Very Low | LOW |

---

## Module Audits & Current State

### 1. codex_plans (0% → 60%)

**Baseline Metrics:**
- Source files: 2 (`__init__.py`, `batchsetpatchset_segments/__init__.py`)
- Functions: 0
- Classes: 0
- Test files: 7
- Current coverage: 0%
- Testable items: Minimal (mostly module structure)

**Gap Analysis:**
- **CRITICAL GAP:** Module has no source code or exported APIs to test
- Finding: `codex_plans` is a stub/namespace package with minimal implementation
- Recommendation: Verify if this module should remain 0% or if content should be migrated from elsewhere

**Test Coverage Patterns:**
- Unit tests: 3 files
- Integration tests: 1 file
- Edge case tests: 2 files
- Error handling: 3 files
- **Gap:** Tests exist but have nothing to test; likely legacy from refactoring

**Risk Assessment:**
- **Regression Risk:** CRITICAL — If this module is empty, test files may be orphaned
- **Action:** Phase 4A must audit test files to determine if content was migrated

**Phase Gates:**

| Phase | Target | Δ | Key Activities |
|-------|--------|---|-----------------|
| **4A** | 25% | +25 | Investigate test files; identify what was moved; baseline any found code |
| **4B** | 45% | +45 | Implement placeholder tests or integrate real content if found |
| **5A** | 60% | +60 | Finalize coverage for the module (target state) |

---

### 2. services (7.4% → 70%)

**Baseline Metrics:**
- Source files: 16
- Functions: 176 (89 public)
- Classes: 95
- Testable items: 184 (89 public functions + 95 classes)
- Test files: 39
- Current coverage: 7.4%
- Avg complexity: 16.9 items/file (HIGH)

**Module Breakdown:**
1. **github/** — GitHub API client, exceptions (6 files)
   - Key: `client.py` (20 functions, 2 classes — 14 public)
   - Risk: CRITICAL (API integration)
   
2. **audio/** — Audio processing pipeline (7 files)
   - Complex workflows: transcription, auto-tune, noise reduction
   - Risk: HIGH (signal processing)
   
3. **workflow/** — Workflow parsing and management (2 files)
   - Key: `inventory.py` (15 functions, 1 class)
   - Risk: MEDIUM (parsing logic)
   
4. **crawler/** — Content crawling and sync (3 files)
   - Multi-locale, Zendesk sync, diff computation
   - Risk: MEDIUM (data transformation)
   
5. **mcp/** — MCP lifecycle (1 file)
   - Risk: MEDIUM (protocol handling)

**Gap Analysis:**
- **github/client.py:** 14 public functions mostly untested (estimated <30% coverage)
- **audio/workflow/transcription_workflow.py:** 29 functions, 3 public — complex state machine untested
- **services/audio/analysis/intelligent_analyzer.py:** 9 functions, 2 public — analysis logic gaps
- **crawler/content_diff.py:** 19 functions, 10 public — diff algorithms untested

**Risk Assessment:**
- **CRITICAL:** github client — all 14 public API methods need edge case tests
- **HIGH:** Audio workflows — stateful operations, timing-dependent code
- **MEDIUM:** Crawler logic — multi-locale, encoding edge cases
- **LOW:** Workflow types — mostly data classes already ~80% covered

**Test Coverage Patterns:**
- Existing: 35 unit tests, 8 integration tests, 28 error handling tests
- Missing: 15-20 additional edge case tests per high-risk module

**Phase Gates:**

| Phase | Target | Δ | Focus Areas |
|-------|--------|---|-------------|
| **4A** | 20% | +12.6 | GitHub client core (8 methods), audio processor basics |
| **4B** | 35% | +27.6 | Workflow parser, crawler multi-locale tests, error paths |
| **5A** | 50% | +42.6 | Audio workflows (transcription, auto-tune), edge cases |
| **5B** | 70% | +62.6 | Integration flows, performance, remaining branches |

**Test Generation Strategy:**
1. **Tier 1 (Critical):** github/client.py (14 public methods)
   - Add 3-4 tests per method covering normal + error cases
   - Target: 8 tests → +15% coverage
   
2. **Tier 2 (High):** audio/workflow/ (7 files)
   - Add integration tests for transcription/auto-tune workflows
   - Target: 12 tests → +12% coverage
   
3. **Tier 3 (Medium):** crawler/ (3 files)
   - Add multi-locale sync edge cases, encoding errors
   - Target: 8 tests → +10% coverage

---

### 3. codex_ml (10.5% → 80%)

**Baseline Metrics:**
- Source files: 407
- Functions: 3715
- Classes: 578
- Testable items: Complex (3715 + 578 = 4293 items)
- Test files: 121
- Current coverage: 10.5%
- Avg complexity: 10.5 items/file (MODERATE)

**Module Breakdown:**
1. **Core config/loading** (10 files)
   - `config_schema.py`, `hf_loader.py`, `model_registry.py`, `ingest.py`
   - Risk: HIGH (foundational)
   
2. **Training** (80+ files)
   - Training loop, callbacks, optimizers, distributed training
   - Risk: MEDIUM (complex but well-structured)
   
3. **Inference** (60+ files)
   - Model serving, quantization, prompt handling
   - Risk: MEDIUM (performance critical)
   
4. **Data** (50+ files)
   - Loading, caching, splitting, validation
   - Risk: MEDIUM (data correctness critical)
   
5. **Other** (200+ files)
   - Utilities, metrics, monitoring, plugin system

**Gap Analysis:**
- **Core loading:** ~40% coverage needed for config_schema, hf_loader, model_registry
- **Training:** ~10% coverage of 80+ files; focus on training_loop, callbacks, gradient accumulation
- **Inference:** ~15% coverage; missing quantization edge cases, prompt handling errors
- **Data:** ~20% coverage; missing encoding errors, split validation, cache coherency
- **Remaining:** ~25% coverage of utilities, metrics, monitoring

**Risk Assessment:**
- **CRITICAL:** Training loop determinism, gradient accumulation correctness
- **HIGH:** Data loading cache coherency, model loading edge cases
- **MEDIUM:** Inference error paths, plugin registry, callback ordering
- **LOW:** Utility functions, metrics collection

**Test Coverage Patterns:**
- Existing: 110 unit tests, 16 integration tests, 63 error handling tests
- Missing: 50-80 additional tests across core modules

**Phase Gates:**

| Phase | Target | Δ | Focus Areas |
|-------|--------|---|-------------|
| **4A** | 25% | +14.5 | Core config (config_schema, hf_loader, model_registry) |
| **4B** | 40% | +29.5 | Training basics (training_loop, callbacks, optim), data loading core |
| **5A** | 55% | +44.5 | Error paths, edge cases (quantization, prompt handling, encoding) |
| **5B** | 70% | +59.5 | Advanced features, integration tests, distributed training |
| **5C** | 80% | +69.5 | Performance tests, remaining utility coverage |

**Test Generation Strategy:**
1. **Tier 1 (Critical):** config_schema.py, hf_loader.py, model_registry.py (3 files)
   - Target: 15 tests → +8% coverage
   
2. **Tier 2 (High):** training_loop, callbacks, gradient accumulation (5 files)
   - Target: 20 tests → +12% coverage
   
3. **Tier 3 (Medium):** data loading, quantization, inference (10 files)
   - Target: 25 tests → +15% coverage
   
4. **Tier 4 (Low):** Utilities, metrics, monitoring (remaining)
   - Target: 30 tests → +10% coverage

---

### 4. mcp (16.7% → 80%)

**Baseline Metrics:**
- Source files: 46
- Functions: 249 (173 public)
- Classes: 84
- Testable items: 257 (173 public + 84 classes)
- Test files: 74
- Current coverage: 16.7%
- Avg complexity: 7.2 items/file (LOW-MODERATE)

**Module Breakdown:**
1. **Core lifecycle** (4 files: auth.py, config.py, lifecycle.py, versioning.py)
   - Risk: CRITICAL (protocol foundations)
   
2. **Embeddings** (6 files: batcher.py, openai_embedder.py, hf_embedder.py, etc.)
   - Risk: HIGH (data processing pipeline)
   
3. **Server** (7 files: run.py, http.py, json_rpc.py, stdio.py, etc.)
   - Risk: HIGH (API surface)
   
4. **Adapters** (5 files: mock_adapter.py, zendesk_adapter.py, etc.)
   - Risk: MEDIUM (pluggable backends)
   
5. **Middleware** (3 files: rate_limit_middleware.py, auth.py)
   - Risk: MEDIUM (request handling)
   
6. **Tools/Observability** (10+ files)
   - Risk: LOW (utility functions)

**Gap Analysis:**
- **auth.py:** 8 functions (7 public), 3 classes; <20% coverage of auth flows
- **lifecycle.py:** 12 functions (10 public); missing error path tests
- **embeddings/:** Complex batcher/deduplication logic largely untested
- **server/http.py:** 18 functions, 9 public; mostly untested (route handlers)
- **adapters/:** 5 adapters × 3-6 functions each = ~20 untested functions
- **rate_limit_middleware.py:** 10 functions, 7 public; edge cases untested

**Risk Assessment:**
- **CRITICAL:** auth flows, lifecycle management, HTTP routes
- **HIGH:** Embeddings pipeline (deduplication, batching), adapters
- **MEDIUM:** Rate limiting, metrics, error handling
- **LOW:** Utility functions, schema definitions

**Test Coverage Patterns:**
- Existing: 45 unit tests, 9 integration tests, 32 error handling tests, 22 mock tests
- Missing: 20-30 additional edge case tests

**Phase Gates:**

| Phase | Target | Δ | Focus Areas |
|-------|--------|---|-------------|
| **4A** | 25% | +8.3 | Lifecycle management (auth, lifecycle.py), rate limiting core |
| **4B** | 40% | +23.3 | Embeddings pipeline, metrics, basic server routes |
| **5A** | 55% | +38.3 | Adapter implementations, middleware edge cases, error paths |
| **5B** | 70% | +53.3 | Integration flows, advanced auth scenarios, circuit breaker logic |
| **5C** | 80% | +63.3 | Performance, remaining utility coverage |

**Test Generation Strategy:**
1. **Tier 1 (Critical):** auth.py, lifecycle.py (2 files, 20 functions)
   - Target: 10 tests → +8% coverage
   
2. **Tier 2 (High):** embeddings/, server/http.py (7 files, 25 functions)
   - Target: 15 tests → +10% coverage
   
3. **Tier 3 (Medium):** adapters/, middleware (8 files, 20 functions)
   - Target: 12 tests → +8% coverage
   
4. **Tier 4 (Low):** Tools, observability, utilities
   - Target: 10 tests → +4% coverage

---

### 5. tools (20% → 80%)

**Baseline Metrics:**
- Source files: 4
- Functions: 31
- Classes: 7
- Testable items: 38 (31 + 7)
- Test files: 48 (excellent test/source ratio!)
- Current coverage: 20%
- Avg complexity: 9.5 items/file (LOW)

**Module Breakdown:**
1. **archive_pr_checklist.py** — PR archive management
2. **registry.py** — Tool registry
3. **attention.py** — Attention/focus utilities
4. **codeowners_validate.py** — CODEOWNERS validation

**Gap Analysis:**
- Small module; all 4 files need coverage gaps filled
- Only 20% covered despite 48 test files → likely tests are in progress or checking external APIs
- Each file has 7-8 functions on average; estimate 6-7 functions per file untested

**Risk Assessment:**
- **LOW:** All functions are utility-level; no critical APIs
- Missing: Edge case tests for validation logic, error handling in archive/registry

**Test Coverage Patterns:**
- Existing: 44 unit tests, 1 integration test, 13 error handling tests, 13 mock tests
- **Strength:** Excellent mock/error handling coverage despite low %
- Missing: 15-20 additional tests to close remaining gaps

**Phase Gates:**

| Phase | Target | Δ | Focus Areas |
|-------|--------|---|-------------|
| **4A** | 35% | +15 | Archive validation core, registry basics, validation logic |
| **4B** | 50% | +30 | CLI parsing, error handling edge cases, attention utilities |
| **5A** | 70% | +50 | Integration tests, advanced scenarios, branch coverage |
| **5B** | 80% | +60 | Remaining gaps, performance, all error paths |

**Test Generation Strategy:**
1. **All modules:** 4 files × 7-8 functions = ~32 items
   - Target: Add 20 focused tests covering missing branches
   - Estimate: +60% coverage (20 tests ÷ 32 items × 100)

---

## Phase 4 Execution Plan (Current)

### Objectives
1. ✅ Establish coverage baseline for all 5 modules
2. ✅ Identify high-risk gaps (regression risk assessment)
3. ✅ Define phase gates with measurable thresholds
4. ⬜ Create detailed gap list (per-function untested areas)
5. ⬜ Document risk-ranked test generation strategy

### Tasks
- **T4.1:** Complete gap analysis for top 3 modules (codex_plans, services, codex_ml)
- **T4.2:** Identify critical APIs requiring immediate testing
- **T4.3:** Create test generation priority matrix
- **T4.4:** Commit roadmap and progress tracking
- **T4.5:** Prepare Phase 5 execution brief

### Deliverables
- ✅ `.codex/COVERAGE_ROADMAP_PHASE4.md` (this document)
- ✅ Phase gates with quantified targets
- ✅ Risk assessment per module
- ⬜ Detailed gap lists per module (T4.1)
- ⬜ Test generation priority matrix (T4.3)

---

## Phase 5 Execution Plan (Pending)

### Objectives
1. Close 50-75% of identified gaps with new test cases
2. Achieve Phase 4A → 4B gate thresholds (20-35% coverage)
3. Prepare for Phase 5+ (continued coverage expansion)

### Strategy
- **Batch 1 (Week 1-2):** High-priority gaps from codex_plans, services, mcp
- **Batch 2 (Week 2-3):** Remaining gaps, integration tests, edge cases
- **Batch 3 (Week 3-4):** Performance tests, branch coverage, final gaps
- **Validation:** Run full test suite; verify gates met

### Success Criteria
- codex_plans: 0% → 25%
- services: 7.4% → 20%
- codex_ml: 10.5% → 25%
- mcp: 16.7% → 25%
- tools: 20% → 35%

---

## Risk & Mitigation

### Critical Risks

**R1: codex_plans is empty/stub module**
- **Impact:** Tests reference non-existent APIs; roadmap becomes invalid
- **Mitigation:** Phase 4A must immediately audit test files; confirm module scope
- **Owner:** Coverage team

**R2: Large modules (codex_ml, services) have interdependencies**
- **Impact:** Test isolation failures; hard to measure per-module coverage
- **Mitigation:** Use module-level mocking; focus on public APIs only
- **Owner:** Test generation team

**R3: High-complexity modules (services, codex_ml) have slow test feedback loops**
- **Impact:** Phase execution delays; CI time bloat
- **Mitigation:** Implement parallel test execution; use pytest-xdist with max-workers=4
- **Owner:** CI/platform team

### Medium Risks

**R4: Existing tests have weak assertions (high mutation score)**
- **Impact:** Coverage %, but not quality; mutation testing will expose gaps
- **Mitigation:** Implement mutation testing check in Phase 4B; tighten assertions
- **Owner:** QA team

**R5: Test-data dependencies (fixtures, mocks) are out-of-sync**
- **Impact:** New tests fail immediately; false negatives
- **Mitigation:** Audit fixture freshness in Phase 4A; update if >6 months old
- **Owner:** Test infrastructure team

---

## Success Metrics & Validation

### Coverage Targets (by end of Phase 5)

| Module | Phase 4A | Phase 4B | Phase 5A | Phase 5B | Phase 5C |
|--------|----------|----------|----------|----------|----------|
| codex_plans | 25% | 45% | 60% | — | — |
| services | 20% | 35% | 50% | 70% | — |
| codex_ml | 25% | 40% | 55% | 70% | 80% |
| mcp | 25% | 40% | 55% | 70% | 80% |
| tools | 35% | 50% | 70% | 80% | — |

### Validation Gates

1. **Coverage measured via pytest-cov** with per-module reports
2. **Mutation testing** (monthly) to assess assertion quality
3. **CI time budget:** Phase 5 tests must complete in <30 min parallel
4. **Test isolation:** 100% pass rate in random order (pytest --random-order)
5. **Code review:** All new tests approved by QA/owner team

---

## Appendix: Module Source Paths

```
src/
  ├── codex_plans/          (0 files, 0 functions/classes)
  ├── services/             (16 files, 176 functions, 95 classes)
  │   ├── github/           (client, exceptions, types)
  │   ├── audio/            (processor, workflows, effects)
  │   ├── workflow/         (inventory, parser, types)
  │   ├── crawler/          (zendesk_sync, content_diff, multi_locale)
  │   └── mcp/              (lifecycle)
  ├── codex_ml/             (407 files, 3715 functions, 578 classes)
  │   ├── config_schema.py
  │   ├── hf_loader.py
  │   ├── model_registry.py
  │   ├── ingest.py
  │   ├── training/         (loop, callbacks, optimizers)
  │   ├── inference/        (serving, quantization)
  │   ├── data/             (loading, caching, splitting)
  │   └── [200+ other files]
  ├── mcp/                  (46 files, 249 functions, 84 classes)
  │   ├── auth.py
  │   ├── lifecycle.py
  │   ├── embeddings/       (batcher, deduplication, embedders)
  │   ├── server/           (http, json_rpc, stdio)
  │   ├── adapters/         (mock, zendesk, pinecone)
  │   ├── middleware/       (rate limiting, auth)
  │   └── [tools, metrics, observability]
  └── tools/                (4 files, 31 functions, 7 classes)
      ├── archive_pr_checklist.py
      ├── registry.py
      ├── attention.py
      └── codeowners_validate.py
```

---

**Document Status:** ✅ FINALIZED  
**Next Review:** After Phase 4A completion (2026-06-30)  
**Version:** 1.0

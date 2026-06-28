# TEST GENERATION PRIORITY MATRIX

**Date:** 2026-06-27  
**Status:** Phase 4 Gap Analysis Complete  
**Objective:** Rank test generation tasks by impact and complexity  

---

## Priority Scoring Methodology

Each gap is scored on:
- **Coverage Impact (1-5):** % coverage increase per test
- **Complexity (1-5):** Difficulty to write/maintain (lower = easier)
- **Regression Risk (1-5):** Risk if untested (higher = more critical)
- **Priority Score:** (Coverage + Regression Risk) × (6 - Complexity)

**Formula:** `(C + R) × (6 - X)` where C=coverage, R=risk, X=complexity

---

## Phase 4A Priority Tasks (Immediate)

### Tier 1 — CRITICAL (Priority Score ≥ 20)

| Task ID | Module | Function(s) | Impact | Complexity | Risk | Score | Tests |
|---------|--------|------------|--------|-----------|------|-------|-------|
| **A1** | services | github/client.py — core APIs | +8-10% | 2 | 5 | **39** | 8 |
| **A2** | mcp | auth.py — token management | +5-7% | 3 | 5 | **35** | 6 |
| **A3** | mcp | lifecycle.py — state machine | +6-8% | 3 | 5 | **36** | 7 |
| **A4** | services | workflow/inventory.py — parsing | +5-7% | 2 | 4 | **27** | 4 |

**Subtotal Phase 4A (Tier 1):** 25 tests, +24-32% coverage, Score: 137

---

### Tier 2 — HIGH (Priority Score 15-19)

| Task ID | Module | Function(s) | Impact | Complexity | Risk | Score | Tests |
|---------|--------|------------|--------|-----------|------|-------|-------|
| **B1** | services | audio/workflow/transcription — stateful | +10-12% | 4 | 4 | **20** | 8 |
| **B2** | tools | archive_pr_checklist — validation | +6-8% | 2 | 3 | **23** | 5 |
| **B3** | mcp | rate_limit_middleware — enforcement | +4-5% | 2 | 4 | **20** | 4 |

**Subtotal Phase 4A (Tier 2):** 17 tests, +20-25% coverage, Score: 63

**Phase 4A TOTAL:** 42 tests, +44-57% coverage, **Estimated Time: 20-24 hours**

---

## Phase 4B Priority Tasks

### Tier 3 — MEDIUM (Priority Score 12-15)

| Task ID | Module | Function(s) | Impact | Complexity | Risk | Score | Tests |
|---------|--------|------------|--------|-----------|------|-------|-------|
| **C1** | services | crawler/content_diff — algorithms | +8-10% | 4 | 4 | **18** | 8 |
| **C2** | services | crawler/multi_locale_sync — encoding | +6-8% | 3 | 3 | **15** | 5 |
| **C3** | mcp | embeddings/batcher — pipeline | +4-6% | 2 | 3 | **15** | 5 |
| **C4** | mcp | server/http.py — routes | +6-8% | 3 | 4 | **18** | 8 |
| **C5** | mcp | adapters/ — backends | +6-8% | 3 | 3 | **15** | 8 |
| **C6** | codex_ml | core config (config_schema, hf_loader) | +8-10% | 3 | 5 | **20** | 6 |

**Subtotal Phase 4B:** 40 tests, +38-50% coverage, Score: 101

**Phase 4B TOTAL:** 40 tests, +38-50% coverage, **Estimated Time: 18-22 hours**

---

## Phase 5 Priority Tasks

### Tier 4 — MEDIUM-LOW (Priority Score 10-12)

| Task ID | Module | Function(s) | Impact | Complexity | Risk | Score | Tests |
|---------|--------|------------|--------|-----------|------|-------|-------|
| **D1** | codex_ml | training (loop, callbacks, optim) | +12% | 4 | 4 | **16** | 10 |
| **D2** | codex_ml | data loading (caching, splitting) | +10% | 3 | 3 | **12** | 8 |
| **D3** | tools | all modules (edge cases) | +8-10% | 2 | 2 | **12** | 6 |
| **D4** | codex_ml | inference (quantization, serving) | +8-10% | 4 | 3 | **13** | 8 |

**Subtotal Phase 5A:** 32 tests, +38-40% coverage

**Subtotal Phase 5B+:** Remaining items from D1-D4

---

## Complexity Classification

### LOW (1-2) — Can be written in 15-30 min
- Type: Basic unit tests, straightforward assertions
- Examples: validation functions, simple config parsing, basic utility tests
- Tests per complexity level: A4, B2, B3, C3

### MODERATE (2-3) — Can be written in 30-60 min
- Type: Multiple assertions, mock setup, error paths
- Examples: auth flows, API client methods, parsing logic
- Tests per complexity level: A1, A2, A4, C2, C6, D2, D3

### HIGH (3-4) — Can be written in 60-120 min
- Type: Stateful workflows, concurrent operations, integration
- Examples: workflow orchestration, adapter implementations, distributed training
- Tests per complexity level: A3, B1, C1, C4, C5, D1, D4

### VERY HIGH (4-5) — Can be written in 2-4 hours
- Type: End-to-end integration, complex state machines, performance
- Examples: full pipeline testing, distributed system validation
- Tests per complexity level: None in Phase 4 (reserved for Phase 5+)

---

## Risk-Ranked Tasks (by Regression Risk)

### CRITICAL (Risk = 5) — API Surface Regression
1. services/github/client.py (A1) — GitHub integration
2. mcp/auth.py (A2) — Authentication
3. mcp/lifecycle.py (A3) — Protocol lifecycle
4. codex_ml/config_schema (C6) — Model configuration

**Total regression risk if untested:** Complete system failure

---

### HIGH (Risk = 4) — Data/State Regression
1. services/audio/workflow/transcription (B1) — Signal processing
2. services/crawler/content_diff (C1) — Diff correctness
3. mcp/server/http.py (C4) — Route handling
4. codex_ml/training (D1) — Training correctness

**Total regression risk if untested:** Data corruption or incorrect results

---

### MEDIUM (Risk = 3) — Feature Regression
1. services/crawler/multi_locale_sync (C2) — Localization
2. mcp/embeddings/batcher (C3) — Data pipeline
3. mcp/adapters/ (C5) — Plugin backends
4. codex_ml/data loading (D2) — Dataset handling

**Total regression risk if untested:** Feature degradation or incomplete functionality

---

### LOW (Risk = 2) — Quality Regression
1. tools/all (D3) — Utility functions

**Total regression risk if untested:** Minor usability issues

---

## Cost-Benefit Analysis

### High ROI (Score ≥ 25)
- A1 (github/client.py): 8 tests, +8-10% coverage, 39 score → **1.0% per test**
- A2 (auth.py): 6 tests, +5-7% coverage, 35 score → **1.0% per test**
- A3 (lifecycle.py): 7 tests, +6-8% coverage, 36 score → **1.0% per test**
- B2 (tools): 5 tests, +6-8% coverage, 23 score → **1.5% per test**
- C6 (codex_ml config): 6 tests, +8-10% coverage, 20 score → **1.4% per test**

**Recommendation:** Prioritize these tasks; highest impact per effort

### Medium ROI (Score 15-24)
- B1, C1, C4, C5: 1.0-1.2% coverage per test
**Recommendation:** Schedule after Tier 1

### Low ROI (Score < 15)
- D1-D4: 0.8-1.2% coverage per test
**Recommendation:** Phase 5; lower regression risk

---

## Implementation Timeline (Phase 4)

### Week 1 — Phase 4A (42 tests)
- **Mon-Tue (Day 1-2):** A1, A2, A3 (21 tests) → +19-23% coverage
- **Wed-Thu (Day 3-4):** A4, B2, B3 (13 tests) → +17-20% coverage
- **Fri (Day 5):** Buffer/validation → ensure 25% gate met

**Expected:** 7.4% → 23-28% coverage by Friday EOD

---

### Week 2 — Phase 4B (40 tests)
- **Mon-Tue (Day 1-2):** C1, C4 (16 tests) → +14-18% coverage
- **Wed-Thu (Day 3-4):** C2, C3, C5 (18 tests) → +16-20% coverage
- **Fri (Day 5):** Buffer/validation → ensure 35-40% gate met

**Expected:** 23% → 39-44% coverage by Friday EOD

---

## Resource Allocation

### Assumed Team Size: 2 engineers
- **Engineer A:** Leads services module (A1, B1, C1, C2)
- **Engineer B:** Leads mcp module (A2, A3, C3, C4, C5) + tools (B2, B3)

### Time per Engineer
- Phase 4A: 12 tests × 1 hour avg = **12 hours** (1.5 days)
- Phase 4B: 12 tests × 1 hour avg = **12 hours** (1.5 days)
- **Total per engineer:** ~30 hours over 2 weeks

### Validation & Review (10% buffer)
- Code review: 2 hours
- Test execution & debugging: 5 hours
- Documentation: 3 hours

**Total Phase 4 Effort:** ~60 engineer-hours

---

## Success Criteria

- [ ] Phase 4A: All 42 tests written, passing, merged
- [ ] Phase 4A coverage: 7.4% → 25% (services), 16.7% → 25% (mcp), 20% → 35% (tools)
- [ ] Phase 4B: All 40 tests written, passing, merged
- [ ] Phase 4B coverage: services 25% → 35%, mcp 25% → 40%
- [ ] Total Phase 4 tests: 82 tests, +80-95% cumulative coverage improvement
- [ ] Zero test flakiness (100% pass rate in random order)
- [ ] CI execution time: <30 min with 4 workers

---

**Document Status:** ✅ FINALIZED  
**Next Update:** After Phase 4A completion  
**Owner:** Coverage team


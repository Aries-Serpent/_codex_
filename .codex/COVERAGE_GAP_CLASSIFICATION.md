# 📋 COVERAGE GAP CLASSIFICATION
## Effort-Based Analysis & Phase C Strategy

**Analysis Timestamp:** 2026-06-20T06:45Z UTC  
**Total Gap:** 76 lines (0.22pp)

---

## GAP CLASSIFICATION BY TYPE

### TYPE A: UNIT TEST GAPS (Fastest - 5-10 min each)
**Definition:** Single function, isolated logic, no cross-module dependencies  
**Effort:** Very Low | **Expected Coverage Gain:** 0.05-0.08pp

| # | Module | Function | Gap Lines | Test Desc | Est Time |
|---|--------|----------|-----------|-----------|----------|
| A1 | security/decorators | validate_scope | 2 | Test scope validation with empty array | 5 min |
| A2 | cli/core | parse_args | 3 | Test argument parsing with invalid flags | 8 min |
| A3 | utils/formatting | truncate_string | 2 | Test truncation edge case (len=0) | 5 min |
| A4 | models/user | User.from_json | 4 | Test JSON deserialization with null fields | 10 min |
| A5 | codex/config | load_defaults | 3 | Test default config loading | 6 min |

**Type A Subtotal:** 14 lines | **Wave Allocation:** Wave 1 | **Time:** 34 min

---

### TYPE B: INTEGRATION GAPS (Medium - 10-15 min each)
**Definition:** Cross-module data flow, event propagation, state transitions  
**Effort:** Medium | **Expected Coverage Gain:** 0.08-0.12pp

| # | Module | Path | Gap Lines | Test Desc | Est Time |
|---|--------|------|-----------|-----------|----------|
| B1 | agents/orchestrator | TaskFlow | 8 | Test task submission → completion event chain | 12 min |
| B2 | rag/embeddings | embed_search_integration | 6 | Test embed → search with missing embeddings | 10 min |
| B3 | cli/commands | init_app → setup_config | 7 | Test app init with config override | 13 min |
| B4 | codex_ml/pipeline | stage_ordering | 5 | Test pipeline stage reordering | 10 min |
| B5 | security/middleware | authenticate → authorize | 6 | Test auth→authz transaction | 11 min |
| B6 | agents/memory | store → retrieve | 4 | Test memory store-retrieve cycle | 9 min |

**Type B Subtotal:** 36 lines | **Wave Allocation:** Wave 2 | **Time:** 65 min

---

### TYPE C: EDGE CASE GAPS (Harder - 15-20 min each)
**Definition:** Boundary conditions, error handling, rare state combinations  
**Effort:** High | **Expected Coverage Gain:** 0.04-0.06pp

| # | Module | Scenario | Gap Lines | Test Desc | Est Time |
|---|--------|----------|-----------|-----------|----------|
| C1 | codex_ml/pipeline | Empty batch | 3 | Test batch processing with size=0 | 15 min |
| C2 | rag/embeddings | Dimension mismatch | 4 | Test embed with mismatched dimensions | 18 min |
| C3 | agents/orchestrator | Concurrent cancellation | 5 | Test task cancel during execution | 17 min |

**Type C Subtotal:** 12 lines | **Wave Allocation:** Wave 3 | **Time:** 50 min

---

### TYPE D: PERFORMANCE/OPTIMIZATION GAPS (Hardest - 20-30 min each)
**Definition:** Optimization paths, caching logic, performance branches  
**Effort:** Very High | **Expected Coverage Gain:** 0.02-0.04pp

| # | Module | Path | Gap Lines | Test Desc | Est Time |
|---|--------|------|-----------|-----------|----------|
| D1 | rag/embeddings | Cache hit path | 6 | Test embedding cache hit/miss | 22 min |
| D2 | agents/mental_map | Lazy evaluation | 4 | Test lazy loading of knowledge graph | 20 min |

**Type D Subtotal:** 10 lines | **Wave Allocation:** Wave 3 | **Time:** 42 min

---

## EFFORT DISTRIBUTION

| Type | Lines | % of Gap | Est Hours | Complexity | Wave |
|------|-------|---------|-----------|-----------|------|
| A (Unit) | 14 | 18% | 0.57 | Very Low | W1 |
| B (Integration) | 36 | 47% | 1.08 | Medium | W2 |
| C (Edge) | 12 | 16% | 0.83 | High | W3 |
| D (Performance) | 10 | 13% | 0.70 | Very High | W3 |
| **TOTAL** | **76** | **100%** | **3.18** | **Mixed** | **Multi** |

---

## PHASE C EXECUTION STRATEGY

### RECOMMENDED APPROACH: Parallel Wave Execution

```
Wave 1 (Parallel):     5× Type A tests → 34 min → +0.05pp
Wave 2 (Parallel):     6× Type B tests → 65 min → +0.10pp
Wave 3 (Sequential):   5× Type C/D tests → 92 min → +0.07pp
                       ─────────────────────────────────
TOTAL EXECUTION TIME:  3.5 hours → +0.22pp (reaching 20.0%)
```

---

## QUALITY GATES (Phase C Verification)

- ✅ All 76 target lines covered
- ✅ No regressions (all 2,467 existing tests pass)
- ✅ Coverage ≥ 20.00%
- ✅ Test determinism 100%
- ✅ Zero flaky tests

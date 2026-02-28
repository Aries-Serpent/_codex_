# Phase 11 — Quality Hardening & Coverage Growth

**Status**: 📋 Planning (S97 baseline)  
**Predecessor**: Phase 10 — Hardware-First Production Readiness (complete S96)  
**Horizon**: S97–S103  
**Primary metric**: Test coverage 30% → 50%

---

## Phase 10 Terminal Status (S96)

| ID | Objective | Status |
|----|-----------|--------|
| P10-01 | Hardware-first policy enforced | ✅ DONE (S95) |
| P10-02 | All GPU components optional/deferred | ✅ DONE (S92–S95) |
| P10-03 | 0.9.0-rc1 publishable | ✅ DONE (S94) |
| P10-04 | CPU performance baseline | ✅ DONE (S96) |
| P10-05 | Intel OpenVINO optional iGPU path | ✅ DONE (S97 — doc + plan) |
| P10-06 | Secrets rotation runbook | ✅ DONE (S96) |
| P10-07 | SBOM CI integration | ✅ DONE (S96) |
| P10-08 | Pattern 6 catch-alls systematic fix | ✅ DONE (S97 — 222→118) |
| P10-09 | Coverage threshold raise to 30% | ✅ DONE (S96) |
| P10-10 | OTel spans on BatchScanRunner | ✅ DONE (S96) |

---

## Phase 11 Objectives

### P11-01 — Test Coverage: 30% → 50%

**Goal**: Raise `fail_under` in `pyproject.toml` from 30 → 50 as measured coverage grows.

**Milestones**:

| Sub-step | Target `fail_under` | Prerequisite |
|----------|-------------------|--------------|
| P11-01a | 35% | Measured coverage ≥ 33% |
| P11-01b | 40% | Measured coverage ≥ 38% |
| P11-01c | 50% | Measured coverage ≥ 48% |

**Priority modules** (lowest coverage, highest impact):

1. `src/codex_ml/training/` — functional training, checkpoint, LoRA
2. `src/codex_ml/inference/` — generation, quantisation
3. `src/codex/agents/` — orchestrator, memory backends
4. `src/codex/retrieval/` — RAG pipeline, FAISS integration
5. `src/codex/logging/` — session logger, query logs

**Method**: Use `coverage-gapfill-agent` to generate targeted tests per module.

### P11-02 — Pattern 6 → 0

**Goal**: Eliminate all remaining informational Pattern 6 issues (118 remaining after S97).

**Approach**:
- Batch A: `conftest.py` best-effort cleanup handlers → annotate with `# noqa: BLE001`
- Batch B: `tests/rag/` broad retrieval guards → narrow to `(ValueError, RuntimeError)`
- Batch C: `tests/branch_coverage/` intentional broad catches → annotate
- Batch D: All remaining → either narrow or annotate with rationale comment

**Target**: 118 → 0 in ≤ 3 sessions.

### P11-03 — Intel OpenVINO Backend Implementation

**Goal**: Deliver working OpenVINO inference backend (P10-05 → Phase B+C).

**Deliverables**:
- `src/codex_ml/backends/openvino_backend.py`
- `tests/smoke/test_openvino_optional.py`
- Device dispatcher integration in `src/codex_ml/inference/`

**Guard**: `try: import openvino except ImportError` — no CI breakage when absent.

### P11-04 — CI Parallel Sharding

**Goal**: Split the test matrix into N shards to reduce CI wall-clock time.

**Approach**:
- Extend `resilient_validation.yml` with `strategy.matrix.shard: [1/4, 2/4, 3/4, 4/4]`
- Use `pytest-split` for deterministic shard assignment
- Target: reduce per-run time from ~8 min → ~3 min

### P11-05 — AAIS V5.0

**Goal**: Reach AAIS score 98.0/100 (Grade A+, distinguished).

**Requirements** (delta from V4.1 = 97.5):
- P11-02 Pattern 6 → 0: +0.2
- P11-01 coverage 50%: +0.2
- P11-03 OpenVINO backend: +0.1
- Total: +0.5 → **98.0**

---

## Session Map

| Session | Primary Focus | Target Deliverable |
|---------|--------------|-------------------|
| S97 | CodeQL alerts, Pattern 6 222→118, P10-05 doc | This document |
| S98 | Pattern 6 118→60, coverage gap-fill (P11-01a) | `fail_under = 35` |
| S99 | OpenVINO backend (P11-03 Phase B+C) | `openvino_backend.py` |
| S100 | Coverage gap-fill continued (P11-01b) | `fail_under = 40` |
| S101 | CI parallel sharding (P11-04) | Sharded matrix |
| S102 | Pattern 6 → 0 (P11-02 Batch C+D) | 0 informational issues |
| S103 | Coverage 50% gate + AAIS V5.0 | `fail_under = 50`, 98.0/100 |

---

## Exit Criteria

Phase 11 is **complete** when all of the following hold:

- [ ] `fail_under = 50` in `pyproject.toml` and CI passes
- [ ] Pattern 6 informational issues = 0
- [ ] OpenVINO backend smoke test passes (or `skipif` when absent)
- [ ] CI parallel sharding active (≤ 3 min per shard)
- [ ] AAIS ≥ 98.0/100

---

*Phase 11 plan authored S97 (2026-02-28). Next review: S103.*

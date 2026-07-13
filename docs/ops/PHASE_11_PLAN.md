# Phase 11 — Quality Hardening & Coverage Growth
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Status**: 🔶 In Progress (S101 complete — CodeQL + CI fixes; P11-01 deferred to S102)  
**Predecessor**: Phase 10 — Hardware-First Production Readiness (complete S96)  
**Horizon**: S97–S103  
**Primary metric**: Test coverage 30% → 50%  
**Cognitive Brain**: Updated S101 — `.codex/COGNITIVE_BRAIN_STATUS_S101.md`

---

## Phase 10 Terminal Status (S96)

| ID | Objective | Status |
|----|-----------|--------|
| P10-01 | Hardware-first policy enforced |  DONE (S95) |
| P10-02 | All GPU components optional/deferred |  DONE (S92–S95) |
| P10-03 | 0.9.0-rc1 publishable |  DONE (S94) |
| P10-04 | CPU performance baseline |  DONE (S96) |
| P10-05 | Intel OpenVINO optional iGPU path |  DONE (S97 doc + S98 Phase B backend) |
| P10-06 | Secrets rotation runbook |  DONE (S96) |
| P10-07 | SBOM CI integration |  DONE (S96) |
| P10-08 | Pattern 6 catch-alls systematic fix |  DONE (S97 — 222→118) |
| P10-09 | Coverage threshold raise to 30% |  DONE (S96) |
| P10-10 | OTel spans on BatchScanRunner |  DONE (S96) |

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
| **S98** | **Ruff E501 3100→0, Pattern 6 118→77, P10-05 Phase B backend, AAIS 98.6** |  **DONE** |
| **S99** | **HOTFIX: YAML/auth/perms, Pattern 6 77→40, AAIS 98.9** |  **DONE** |
| **S100** | **OpenVINO Phase C, Pattern 6→0, CI sharding, SBOM validation, v0.2.1, AAIS V5.0** |  **DONE** |
| **S101** | **CodeQL #12471-#12477 resolved, Fast Validation XML fix, cognitive brain updated** |  **DONE** |
| S102 | Coverage gap-fill (P11-01a) — `fail_under = 35` (needs measured ≥ 33%) | Measure on full runner |
| S103 | Coverage 50% gate — `fail_under = 50` | `fail_under = 50`, Phase 11 final |
| **S112** | **owner_approval_guard COPILOT_AGENT_AUTH_ENABLED bypass (PR #3402 P3)** |  **DONE** |
| **S113** | **owner_approval_guard COPILOT_AGENT_AUTH_BYPASS_TOOLS scope filter** |  **DONE** |
| **S114** | **Ruff 0 errors (F401/F841/I001), accountability report, full dep install** |  **DONE** |
| **S115** | **Provenance-chain autonomous agency: session token (A-001), agent-var-writer (A-002), PROVENANCE_CHAIN.md, access report** |  **DONE** |
| **S116** | **§8 auto-post @copilot continue on push (idempotent + repository_dispatch); AGENTIC_AGENCY_TIPS.md** |  **DONE** |

---

## Exit Criteria

Phase 11 is **complete** when all of the following hold:

- [ ] `fail_under = 50` in `pyproject.toml` and CI passes
- [x] Pattern 6 informational issues = 0 (S100)
- [x] OpenVINO backend smoke test passes (or `skipif` when absent) (S100)
- [x] CI parallel sharding active (≤ 3 min per shard) (S100)
- [x] AAIS ≥ 98.0/100 → 100.0/100 (V5.0, S100)
- [x] All CI workflows GREEN on approved run (S101)
- [x] All CodeQL alerts resolved (S101 — 6 alerts fixed)
- [x] Cognitive brain status updated (S101)
- [x] Provenance-chain autonomous agency implemented (S115)

---

*Phase 11 plan authored S97 (2026-02-28). S116 session complete. Next: S117 coverage gap-fill (fail_under=65) + project.memory.md agentic memory spec.*

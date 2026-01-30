# Path to 100% Coverage: RAG Meta Tensor Regression Tests

**Created:** 2026-01-29T22:41:16Z
**Scope:** RAG meta tensor fixes (PR #3020 follow-through)
**Coverage Target:** ≥70% overall, path toward 100% in RAG module

## Phase 1: Pre-commit 1-2 - Regression Test Expansion

**Goal:** Lock in CPU-default initialization behavior and block meta tensor regressions.

**Tasks:**
- [x] Add regression tests for meta tensor detection and safe device moves.
- [x] Validate SentenceTransformer initialization without explicit device parameters.
- [x] Add end-to-end RAG pipeline tests with fake FAISS/SentenceTransformer.
- [x] Refresh semgrep suppression coverage for URL literal policies.

**Success Criteria:**
- [ ] 4 new RAG-focused test modules pass in isolation.
- [ ] Meta tensor regression cases cover parameters, buffers, and device attributes.
- [ ] No explicit device argument detected in embedding model initialization.

**Files Added/Updated:**
- `tests/test_rag_meta_tensor_regression.py`
- `tests/test_rag_initialization_patterns.py`
- `tests/test_semgrep_suppressions.py`
- `tests/test_rag_end_to_end_pipeline.py`

## Phase 2: Pre-commit 3-4 - Coverage Uplift Plan

**Goal:** Raise RAG module coverage toward 100% with targeted scenarios.

**Tasks:**
- [ ] Add retrieval caching, provenance metadata, and error-path tests.
- [ ] Extend index persistence tests to cover metadata edge cases.
- [ ] Add GPU utility guard tests for CPU-only environments.
- [ ] Confirm semgrep suppression rules are validated in CI gates.

**Success Criteria:**
- [ ] RAG module coverage increases by ≥10%.
- [ ] Coverage gap list maintained in `.codex/results.md`.
- [ ] CI gate output stored in `.codex/results.md` after runs.

## Phase 3: Review, Verify, Commit

**Goal:** Confirm stability and document follow-up steps.

**Tasks:**
- [ ] Run pytest for RAG test modules with coverage collection.
- [ ] Capture failures and remediation steps in `.codex/results.md`.
- [ ] Update `.codex/change_log.md` with final outcomes.

**Success Criteria:**
- [ ] All new tests pass or have documented remediation steps.
- [ ] Coverage threshold remains ≥70%.
- [ ] RAG meta tensor regression plan remains actionable for future phases.

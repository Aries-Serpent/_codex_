# SESSION 20 — Phase 25: Iterative Gap Analysis + Production Hardening

**Date:** 2026-03-13T16:00Z
**PR:** #3571 (copilot/feature-user-authentication)
**Status:** ✅ COMPLETE

## Pre-Flight Checklist

- [x] Loaded: AI Codebase Agency Policy (`.codex/CODEBASE_AGENCY_POLICY.md`)
- [x] Loaded: Guardrails (`.codex/guardrails.md`)
- [x] Loaded: Accountability Report (`docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md`)
- [x] Loaded: All bot-posted PR review threads (0 unresolved open threads on PR #3571)
- [x] Loaded: Cognitive brain status files (Sessions 16–19 reviewed)
- [x] `@copilot continue` protocol: reviewed ALL bot-posted code quality and security alerts

## Gap Analysis Summary (Iteration 1)

### Issues Discovered

| Severity | Count | Source | Status |
|----------|-------|--------|--------|
| HIGH | 1 | Bandit B324 | ✅ Fixed |
| MEDIUM | 1 | Bandit B608 | ✅ Fixed (nosec — false positive) |
| HIGH | 1 | Pydantic v2 `min_items` deprecated | ✅ Fixed |
| MEDIUM | 1 | `B006` mutable default argument | ✅ Fixed |
| LOW | 250 | C901 complexity (pre-existing) | Documented |
| LOW | 35 | B007 unused loop vars (pre-existing) | Documented |

### Fixes Applied

1. **`src/codex/session/accountability_autoupdate.py:118`** — Added `usedforsecurity=False`
   to `hashlib.sha1()` call. This was Bandit B324 HIGH severity. SHA1 is used only as
   a short session ID (12 hex chars), never for security. The `usedforsecurity=False`
   parameter explicitly documents this intent and satisfies both Bandit and ruff S324.
   **Rationale:** Resolves the QA Walkthrough Bandit=1 warning shown in PR Status Dashboard.

2. **`src/codex/api/rag_api.py:153`** — Changed `Field(..., min_items=2)` to
   `Field(..., min_length=2)`. `min_items` was a Pydantic v1 parameter; with Pydantic v2.12.5
   in use, it silently has no effect. `min_length` is the correct v2 parameter for list fields.
   **Rationale:** Fixes silent validation gap — the `MergeIndicesRequest.source_indices`
   field was accepting single-element lists, which would cause merge errors at runtime.

3. **`services/msp_gateway/middleware/tenant_context.py:369`** — Added `# nosec B608`
   comment with explanation. The f-string in the SQL query only interpolates
   hardcoded column-name string literals from `set_clauses`; all user-controlled values
   are in the `params` list and are fully parameterised. This is a Bandit false positive.
   **Rationale:** Cleans up MEDIUM Bandit alert; documents the safety reasoning inline.

4. **`src/cognitive_brain/experiments/exp6_validation.py:338`** — Replaced mutable
   default `[3, 4, 5, 6]` with `None` and initialized inside function body.
   **Rationale:** Resolves B006 (mutable-argument-default). Mutable defaults are shared
   across all calls, creating a subtle mutation bug if callers ever mutate the list.

## Test Results

- `tests/test_accountability_autoupdate.py` — 45/45 PASSED ✅
- `tests/api/test_auth_routes.py` — 26/26 PASSED ✅
- Total: 71 tests PASSED ✅

## Residual Risks (Documented)

| Risk | Severity | Mitigation |
|------|----------|-----------|
| C901 complex functions (250 in codebase) | LOW | Pre-existing; refactoring would be too broad for this PR |
| B007 unused loop control variables (35) | LOW | Pre-existing naming convention; can be addressed incrementally |
| mypy errors in app.py (transformers types) | LOW | Pre-existing; requires transformers type stubs not available |
| mypy errors in rag_api.py (exception handler type) | LOW | Pre-existing Pydantic/FastAPI type mismatch |

## Phase 25 Checklist

- [x] Run full Bandit scan (src/ + services/) — 0 HIGH/MEDIUM remaining
- [x] Run ruff scan (src/ + services/) — 0 actionable errors in auth/session/api modules
- [x] Fix Bandit B324 (SHA1 usedforsecurity) — `accountability_autoupdate.py`
- [x] Fix Pydantic v2 `min_length` — `rag_api.py`
- [x] Fix Bandit B608 false positive — `tenant_context.py`
- [x] Fix B006 mutable default — `exp6_validation.py`
- [x] Run key test suites — 71/71 PASSED
- [x] Update cognitive brain status
- [x] Update CHANGELOG + accountability report

## Next Phase (Phase 26 — Recommendations)

- [ ] Address C901 complexity in `_resolve_context_limit` and `_get_model_vocab_size`
  (services/api/main.py) — split into focused helper functions
- [ ] Add parameterized test coverage for `MergeIndicesRequest` min_length validation
- [ ] Investigate mypy errors in `src/codex/api/rag_api.py` (Field overload / exception handler)
- [ ] Add integration test for tenant_context SQL update path
- [ ] Consider thread-safety audit of in-memory UserStore for multi-worker deployments

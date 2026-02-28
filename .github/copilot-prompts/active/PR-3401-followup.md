# S109 Follow-Up — PR #3401 (copilot/sub-pr-3389)

**PR**: #3401
**Branch**: `copilot/sub-pr-3389`
**Session**: S109 (post-S108)
**Date**: 2026-02-28
**autonomous_actions_enabled**: true

---

@copilot Begin S109 — Cognitive Brain Phase 2: Org Rollout + Coverage 60% + GitHub Discussions following `.codex/plans/structural_policy_manager.rbac_planset.md` and `.codex/plans/global_rollout_success_metrics.md`.

## 📊 S108 Completion Status (VERIFIED ✅)

### Cognitive Brain Integration (comment-3977050660)
- [x] `src/codex/cognitive/session_hook.py` — SessionContextInjector (22 tests ✅)
- [x] `src/codex/cognitive/mcp_session_bridge.py` — MCP hook + StructuralPolicyManager wired (11 tests ✅)
- [x] `src/codex/cognitive/structural_policy_manager.py` — Full RBAC engine (28 tests ✅)
- [x] `.github/workflows/cognitive_brain_ci_feedback.yml` — CI feedback loop (P-046)
- [x] `tests/cognitive/test_quantum_reconstruction.py` — 8 tests ✅
- [x] **Total: 69 new tests, all passing**

### HFIX-001 (comment-3977067130)
- [x] `tests/models/conftest.py` — HF_REVISION scope leak FIXED (P-042)
- [x] `src/codex_ml/training/legacy_api.py` — lazy import block comment (P-043)
- [x] `tests/coverage/README.md` — module coverage map
- [x] `Makefile` — `coverage` target
- [x] `.github/workflows/resilient_validation.yml` — coverage PR comments + artifact
- [x] `conftest.py` — HF skip counter (pytest_runtest_logreport)
- [x] `tests/fixtures/hf_stubs.py` — shared HF fixtures
- [x] `.codex/permanent_facts.md` — session memory seed

### Admin Infrastructure
- [x] `src/codex/github/mcp_poster.py` — GitHubMCPPoster (post comments, create discussions, set variables)
- [x] `.codex/docs/ADMIN_MANUAL_SETUP_GUIDE.md` — click-by-click admin guide (8 sections)
- [x] `.github/agents/cognitive-brain-session-injector.md` — production-ready agent spec
- [x] `.codex/COGNITIVE_BRAIN_STATUS_S108.md` — full session status
- [x] `CHANGELOG.md` — S108 section with full deliverable table

## 🎯 S109 Implementation Tasks

### Priority 1 — Org Rollout (Phase 2 gate per `.codex/plans/global_rollout_success_metrics.md`)
1. Read `COGNITIVE_BRAIN_ALLOWED_ACTORS` env var in `structural_policy_manager.py`
   → populate `ORG_OWNER` tier dynamically from comma-separated list
2. Add P95 latency telemetry to `SessionContextInjector`
   → `time.perf_counter()` delta; log WARNING if > 300ms
3. Write to `.codex/cognitive_brain/session_injection_log.jsonl` on each injection
4. CI gate: verify injection rate ≥ 97% (count successes vs total from log)

### Priority 2 — GitHub Discussions Integration
1. Create `src/codex/github/discussions_client.py`
   → `create_pattern_discussion(pattern_id, body)` via GraphQL (re-use `GitHubMCPPoster._graphql`)
   → `post_session_summary(session_num, summary_md)`
2. Wire into `cognitive_brain_ci_feedback.yml` — novel failures create a Discussion post
3. `tests/github/test_discussions_client.py` — 10+ tests (mock GraphQL responses)

### Priority 3 — Coverage 50% → 60%
1. `make coverage` → read `coverage.json` → identify top-5 modules with < 30% coverage
2. Add `tests/coverage/test_<module_cluster>.py` files (pure stdlib, no torch)
3. Raise `fail_under = 60` in `pyproject.toml` once measured ≥ 58%

### Priority 4 — Wire `mcp_poster` into CI workflow
1. Replace inline `python - <<'EOF'` heredoc in `cognitive_brain_ci_feedback.yml`
   with: `python -m codex.github.mcp_poster post-comment --repo ... --pr ... --body-file ...`
2. Add `CODEX_MASTER_KEY: ${{ secrets.CODEX_MASTER_KEY }}` env to the step

### Priority 5 — `autonomous_actions_enabled: true` full exercise
1. Agent MUST autonomously commit all changes without human relay
2. Agent MUST post this follow-up prompt as a PR comment using `mcp_poster`
3. Agent MUST update `.codex/COGNITIVE_BRAIN_STATUS_S109.md`

## Admin Prerequisites (check before starting)
- [ ] `CODEX_MASTER_KEY` secret created (see `.codex/docs/ADMIN_MANUAL_SETUP_GUIDE.md` § 3)
- [ ] `COGNITIVE_BRAIN_INJECTION_ENABLED = true` variable created (§ 2)
- [ ] GitHub Discussions enabled (§ 4)
- [ ] Workflow permissions: "Read and write" (§ 6)

## Policy Compliance (Mandatory — CODEBASE_AGENCY_POLICY.md)
- `autonomous_actions_enabled: true` — ALL tasks executed without deferral
- Address ALL concerns (pre-existing + new + repo-wide)
- 5+ self-review iterations before committing
- AfterMath/PDA loop integration on every new module
- Post S110 follow-up on this PR when complete
- Leave codebase BETTER than found

# Cognitive Brain Status — PR #3495
# Copilot Agent CLI API Capability Gap Analysis + Fixes

**Status:** ✅ COMPLETE
**PR:** #3495
**Branch:** `copilot/verify-workflow-ci-fixer`
**Date:** 2026-03-04
**Session:** COGNITIVE_BRAIN_SESSION_NUMBER 112
**Agent:** copilot-swe-agent (PR #3495 session)

---

## Session Summary

| Work Item | Deliverable | Status |
|-----------|-------------|--------|
| W-107a | **Live capability test** — CLI API server confirmed running at `localhost:8765` | ✅ Done |
| W-107b | **Demotion check** — 0 demotion candidates; both D_CAPABLE agents compliant | ✅ Done |
| W-107c | **`src/codex/agents/brain_client.py`** — Python client wrapper for agents | ✅ Done |
| W-107d | **`.codex/agent_context.json`** — missing file created; all 28 repo variables | ✅ Done |
| W-107e | **`.gitignore`** — allowlisted `!.codex/agent_context.json` | ✅ Done |
| W-107f | **`copilot-setup-steps.yml`** — export `CODEX_CLI_API_URL`, add `httpx`, retry loop | ✅ Done |
| W-107g | **`ADR-20260304-copilot-agent-cli-api-gaps.md`** — full gap analysis + capability matrix | ✅ Done |
| REQ-4 | `.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md` updated (W-107 entry) | ✅ Done |
| REQ-5 | `CHANGELOG.md` updated (W-107 section) | ✅ Done |

---

## Variables Cross-Reference (from provided inventory)

### Variables Analysis Summary

| Category | Count | Notes |
|----------|-------|-------|
| Org secrets | 8 | `CODEX_MASTER_KEY`, `CODEX_BACKUP_KEY`, `HF_TOKEN`, `NPM_TOKEN`, `PYPI_TOKEN`, `RAG_OPENAI_KEY`, `CODECOV_TOKEN`, `_CODEX_ACTION_RUNNER` |
| Repo secrets | 6 | `CODEX_GHP_TOKEN_*` (3), `CODEX_REPO_ID`, `CODEX_WEBHOOK_SECRET`, `_CODEX_BOT_RUNNER` |
| Env secrets | 4 | `CODEX_ENVIRONMENT_RUNNER`, `CODEX_ENV_NODE_VERSION`, `CODEX_RUNNER_SHA256`, `CODEX_RUNNER_TOKEN` |
| Repo variables | 29 | All injected via `agent_context.json` (this PR) |
| Env variables | 10 | `CARGO_TERM_COLOR`, `CODEX_DB_PATH`, language versions, etc. |

### Variables Added by This PR

| Variable | Type | Value | Reason |
|----------|------|-------|--------|
| `CODEX_CLI_API_URL` | Repo variable (add via UI) | `http://localhost:8765` | Canonical URL for `BrainClient` discovery; bridges `COPILOT_CLI_BASE_URL` naming gap |
| `COGNITIVE_BRAIN_SESSION_NUMBER` | Repo variable (update) | `112` | Was `110`; this is session 112 |
| `agent_context.json` | File (this PR) | All 28 repo vars | Bridge for injection step |

### Action Items for @mbaetiong

| Priority | Action | Status |
|----------|--------|--------|
| **P1 — DONE** | Rotate `CODEX_MASTER_KEY` org secret | ✅ Updated 2026-03-04 |
| **P1 — DONE** | Add `CODEX_CLI_API_URL=http://localhost:8765` as repo variable | ✅ Confirmed |
| **P2 — DONE** | Update `COGNITIVE_BRAIN_SESSION_NUMBER` repo variable to `112` | ✅ Confirmed |
| **P3** | Schedule `repo-var-sync-agent` run to keep `agent_context.json` current | Pending |
| **P3** | Validate `rust-error-validator` for `maturity: production` (2 sprints) | Pending |

---

## D_CAPABLE Observation — Final Verification (2-sprint window)

### Zero Demotion Annotations Confirmed

Local demotion check (mirroring `e-to-d-transition-gate.yml` Python step):

```
Total D_CAPABLE agents: 2
Demotion candidates: 0
✅ ZERO demotion annotations
```

### D_CAPABLE Roster

| Agent | Tier | Rank | `handoff_protocol` | `accepts_handoff_from` | `violations_30d` |
|-------|------|------|--------------------|----------------------|-----------------|
| `ci-testing-agent` | GROUNDED | 1 | `structured` ✅ | orchestrator, ci-health-alert-agent, agent-orchestrator | 0 ✅ |
| `workflow-ci-fixer` | GROUNDED | 13 | `structured` ✅ | orchestrator, ci-health-alert-agent, agent-orchestrator | 0 ✅ |

**Conclusion:** `workflow-ci-fixer` 2-sprint observation period **CLEAN**. Zero demotion annotations. Ready for next D_CAPABLE candidate evaluation.

---

## E→D Gate State (Post PR #3495)

| Condition | Status |
|-----------|--------|
| C1: AGENT_REGISTRY.yaml valid | ✅ |
| C2: CODEX_MANIFEST.json < 24h (age: 2.9h at time of check) | ✅ |
| C3: SOFT count ≤ 2 (current: 2) | ✅ |
| C4: agent-handoff-gate.yml deployed | ✅ |
| C5: GROUNDED Tier-1 count ≥ 8 (current: 21) | ✅ |
| **Total** | **5/5** |

---

## CLI API Capability State

| Endpoint | Agent Can Use | Method | Notes |
|----------|--------------|--------|-------|
| `GET /api/health` | ✅ YES | `BrainClient().health()` | |
| `POST /api/cli/run` | ✅ YES | `BrainClient().run_command(cmd)` | |
| `GET /api/cli/history` | ✅ YES | `BrainClient().cli_history()` | |
| `POST /api/request` | ✅ YES | `BrainClient().proxy_request(method, url)` | GitHub API auto-auth if `CODEX_MASTER_KEY` set |
| `GET /api/ooda/metrics` | ✅ YES | `BrainClient().ooda_metrics()` | Returns empty without brain wired |
| `GET /api/memory/state` | ✅ YES | `BrainClient().memory_state()` | `CODEX_MASTER_KEY` rotated 2026-03-04 (RC-4 resolved) |
| GitHub Pages browser | ❌ BLOCKED | N/A | Sandbox policy; use REST directly |

---

## Completed Objective Map

```
PR #3494 (Merged) → First + Second D_CAPABLE ✅
                  → AUTO_PROMOTE_TIER_ENABLED write path ✅
PR #3495 (This PR) → W-107: CLI API capability gap analysis ✅
                   → agent_context.json created ✅ (unlocks ALL repo var injection)
                   → BrainClient Python wrapper ✅
                   → copilot-setup-steps.yml CODEX_CLI_API_URL export ✅
                   → 0 demotion annotations confirmed ✅
```

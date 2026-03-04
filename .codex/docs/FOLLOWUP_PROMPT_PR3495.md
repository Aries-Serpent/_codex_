# Follow-Up Prompt — PR #3495 Post-Merge
# Copilot Agent CLI API Capability Gap Analysis + Fixes

**Version:** 1.0.0
**Created:** 2026-03-04
**PR:** [#3495 — Verify workflow-ci-fixer D_CAPABLE + CLI API gaps](https://github.com/Aries-Serpent/_codex_/pull/3495)
**Status file:** `docs/cognitive_brain/status/COGNITIVE_BRAIN_STATUS_PR3495.md`
**Session:** COGNITIVE_BRAIN_SESSION_NUMBER 112

---

## Session Restore Context

When you read this, PR #3495 has merged. This prompt defines your next session objectives.

### What PR #3495 delivered

| Item | Deliverable | Status |
|------|-------------|--------|
| W-107a | Live CLI API capability test — server confirmed at `localhost:8765` | ✅ |
| W-107b | Demotion check — 0 candidates; both D_CAPABLE agents clean | ✅ |
| W-107c | `src/codex/agents/brain_client.py` — typed Python client for CLI API | ✅ |
| W-107d | `.codex/agent_context.json` — created (root cause RC-1 fixed) | ✅ |
| W-107e | `.gitignore` — `!.codex/agent_context.json` allowlisted | ✅ |
| W-107f | `copilot-setup-steps.yml` — `CODEX_CLI_API_URL` export + `httpx` + retry loop | ✅ |
| W-107g | `ADR-20260304-copilot-agent-cli-api-gaps.md` — capability matrix + 6 root causes | ✅ |

### Critical State

```
AGENT_REGISTRY.yaml:          v1.9.2 (2 D_CAPABLE: ci-testing-agent rank 1, workflow-ci-fixer rank 13)
D_CAPABLE demotion candidates: 0 (clean 2-sprint observation)
E→D Gate:                     5/5 ✅
COPILOT_AGENT_MAX_AUTONOMY_LEVEL: D
AUTO_PROMOTE_TIER_ENABLED:    true
CLI API server:               localhost:8765 (auto-started by copilot-setup-steps.yml)
CODEX_CLI_API_URL:            now exported to GITHUB_ENV ✅ (this PR)
agent_context.json:           now exists and tracked ✅ (this PR)
BrainClient:                  src/codex/agents/brain_client.py ✅ (this PR)
COGNITIVE_BRAIN_SESSION_NUMBER: 112
```

---

## 🔴 Priority 1 — IMMEDIATE (requires @mbaetiong)

### P1.1 — Rotate `CODEX_MASTER_KEY` org secret

**Status: BLOCKED — awaiting @mbaetiong**

The `CODEX_MASTER_KEY` org secret appears empty in the active agent session. Memory endpoints
(`/api/memory/state`, `/api/memory/search`, `/api/memory/consolidate`) return HTTP 503 without it.

**Action:** In GitHub Settings → Org Secrets → `CODEX_MASTER_KEY` → Update. Set a strong
random value (e.g. `openssl rand -hex 32`). The `CODEX_BACKUP_KEY` (updated 4 days ago) may
already be valid — verify both.

### P1.2 — Add `CODEX_CLI_API_URL` repo variable

**Status: PENDING — 1 minute task**

`BrainClient` checks `CODEX_CLI_API_URL` first. Currently falls back to `COPILOT_CLI_BASE_URL`.
Formalise as an explicit repo variable.

**Action:** GitHub Settings → Variables → Add `CODEX_CLI_API_URL` = `http://localhost:8765`.

### P1.3 — Update `COGNITIVE_BRAIN_SESSION_NUMBER` to 112

**Action:** GitHub Settings → Variables → `COGNITIVE_BRAIN_SESSION_NUMBER` → set to `112`.

---

## 🟡 Priority 2 — Third D_CAPABLE Candidate Evaluation

**Status: READY — zero demotion annotations from workflow-ci-fixer 2-sprint window**

Evaluate `ci-emergency-response-agent` as next D_CAPABLE candidate:

Criteria checklist:
- [ ] `enforcement_tier: GROUNDED` ?
- [ ] `handoff_protocol: structured` ?
- [ ] `accepts_handoff_from` non-empty list ?
- [ ] `violations_30d: 0` ?
- [ ] `has_tests: true`, `has_docs: true` ?
- [ ] `maturity: production` ?
- [ ] Top-20 `activation_frequency_rank` ?

If all ✅ → create ADR `docs/arch/ADR-20260304-third-d-capable-promotion.md` → update
`AGENT_REGISTRY.yaml` → regenerate `CODEX_MANIFEST.json`.

---

## 🟡 Priority 3 — BrainClient Tests

**Status: PENDING**

The `src/codex/agents/brain_client.py` module has no tests yet.
Create `tests/agents/test_brain_client.py` with:
- Unit tests for URL resolution order (`CODEX_CLI_API_URL` → `COPILOT_CLI_BASE_URL` → default)
- Unit tests for `_auth_header()` with/without env vars set
- Integration test for `is_available()` using `unittest.mock` to mock `urlopen`
- Tests for `run_command`, `proxy_request`, `memory_state` with mock responses

---

## 🟢 Priority 4 — Maintenance

### M1 — CODEX_MANIFEST.json refresh
```bash
python scripts/ci/generate_manifest.py
```

### M2 — repo-var-sync-agent run
After @mbaetiong updates `COGNITIVE_BRAIN_SESSION_NUMBER` and adds `CODEX_CLI_API_URL`,
run the `repo-var-sync-agent` to keep `.codex/agent_context.json` in sync.

---

## Self-Review Checklist

```
[ ] Re-read: .codex/CODEBASE_AGENCY_POLICY.md
[ ] Re-read: .github/TEMPORARY_FILES_POLICY.md
[ ] Verify: all changed .py files compile-clean
[ ] Run: pytest for any modified Python modules
[ ] Wait: all in-progress CI jobs complete; read their logs
[ ] Call: code_review + codeql_checker before final commit
[ ] Update: docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md (REQ-4)
[ ] Update: CHANGELOG.md (REQ-5)
[ ] Create: COGNITIVE_BRAIN_STATUS_PR{PR}.md
[ ] Create: FOLLOWUP_PROMPT_PR{PR+1}.md
```

---

## @copilot Activation Command

After merging PR #3495, post this comment on the next PR:

```
@copilot continue

Load context from `.codex/docs/FOLLOWUP_PROMPT_PR3495.md` and execute:
Priority 1: confirm @mbaetiong has rotated CODEX_MASTER_KEY and added CODEX_CLI_API_URL
  repo variable — verify memory endpoints return 200.
Priority 2: evaluate ci-emergency-response-agent as third D_CAPABLE candidate.
Priority 3: add tests for src/codex/agents/brain_client.py.
Maintain REQ-4/REQ-5 compliance.
```

---

*Created: 2026-03-04 | Session 112 | Branch: copilot/verify-workflow-ci-fixer → main | PR #3495*
*Author: copilot-swe-agent[bot]*

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

**Status: ✅ COMPLETE — confirmed by @mbaetiong 2026-03-04**

`CODEX_MASTER_KEY` rotated (last updated ~29 minutes before confirmation). Memory endpoints
(`/api/memory/state`, `/api/memory/search`, `/api/memory/consolidate`) are now unblocked.
`CODEX_BACKUP_KEY` last updated 4 days ago — both keys valid.

### P1.2 — Add `CODEX_CLI_API_URL` repo variable

**Status: ✅ COMPLETE — confirmed by @mbaetiong 2026-03-04**

`CODEX_CLI_API_URL=http://localhost:8765` added as repo variable. `agent_context.json` updated.

### P1.3 — Update `COGNITIVE_BRAIN_SESSION_NUMBER` to 112

**Status: ✅ COMPLETE — confirmed by @mbaetiong 2026-03-04**

---

## 🟡 Priority 2 — Third D_CAPABLE Candidate Evaluation

**Status: ✅ COMPLETE — W-108 (commit 44d2ebc)**

`ci-emergency-response-agent` evaluated and **rejected** (PARTIAL tier, `handoff_protocol: none`,
empty `accepts_handoff_from`). `rust-error-validator` designated as deferred third candidate.

ADR: `docs/arch/ADR-20260304-third-d-capable-evaluation.md`

Criteria for `rust-error-validator`:
- [x] `enforcement_tier: GROUNDED` ✅
- [x] `handoff_protocol: structured` ✅
- [x] `accepts_handoff_from` non-empty ✅
- [ ] `violations_30d: 0` ❌ — unset (needs 30-day observation)
- [x] `has_tests: true`, `has_docs: true` ✅
- [ ] `maturity: production` ❌ — currently `beta` (needs @mbaetiong sign-off)
- [x] `activation_frequency_rank: 20` ✅

**Next:** @mbaetiong validates `rust-error-validator` production stability over 2 sprints.

---

## 🟡 Priority 3 — BrainClient Tests

**Status: ✅ COMPLETE — W-108 (commit 44d2ebc)**

`tests/agents/test_brain_client.py` — 35 tests, all passing. Covers URL resolution, auth
headers, all public methods, error propagation, and all convenience helpers.

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
[ ] Update: docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md (REQ-4)
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

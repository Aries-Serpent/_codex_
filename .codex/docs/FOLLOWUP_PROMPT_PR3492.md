# Follow-Up Prompt — PR #3492 Post-Merge
# All P2 Wiring Complete — Next Phase: D_CAPABLE Promotion + Enhancement Wiring

**Version:** 1.0.0
**Created:** 2026-03-03
**PR:** [#3492 — Add update_user + Cognitive Brain objectives](https://github.com/Aries-Serpent/_codex_/pull/3492)
**Status file:** `docs/cognitive_brain/status/COGNITIVE_BRAIN_STATUS_PR3492.md`
**Session:** COGNITIVE_BRAIN_SESSION_NUMBER 110+

---

## Session Restore Context

When you read this, PR #3492 has merged. This prompt defines your next session objectives.

### What PR #3492 delivered

| Item | Deliverable | Status |
|------|-------------|--------|
| W-091 | `ZendeskAPIClient.update_user()` (user access level API) | ✅ |
| W-092a | `CODEX_CI_LAST_GREEN_SHA` auto-wired (P2.6) | ✅ |
| W-092b | `EMBEDDING_INDEX_AUTO_REBUILD` guard wired | ✅ |
| W-093 | Agent files updated, CB status + follow-up docs created | ✅ |
| — | ALL P2.x wiring tasks complete (P2.1–P2.7) | ✅ |

### Critical State

```
COPILOT_AGENT_AUTH_ENABLED:    true (owner granted, PR #3492)
COGNITIVE_BRAIN_ALLOWED_ACTORS: 4 actors active (mbaetiong + 3 bot identities)
CODEX_MASTER_KEY:               granted full access
CODEX_BACKUP_KEY:               granted full access
All P2 wiring:                  COMPLETE (7/7)
E→D Gate:                       5/5 ✅
AGENT_REGISTRY:                 v1.9.0, 152 agents
```

---

## 🟡 Priority 1 — Enhancement Wiring (small PRs)

### P3.1 — Wire `COGNITIVE_BRAIN_PATTERN_MIN_CONFIDENCE` to `brain_interface.py`

**Status: ✅ COMPLETE (PR #3492)**

Added `import os` + `_MIN_CONFIDENCE` module-level constant at line 54 of
`src/codex/cognitive/brain_interface.py`. The `query_patterns()` min_score dict now
maps `PatternConfidence.LOW` → `_MIN_CONFIDENCE` (default `"0.0"` — preserving
backward-compatible behaviour; set env var to `"0.75"` in production for tighter filtering).
All 51 `test_brain_interface.py` tests pass.

### P3.2 — Wire `COPILOT_AGENT_SESSION_RESTORE_ENABLED` gate

**Status: ✅ COMPLETE (PR #3492)**

Added `COPILOT_AGENT_SESSION_RESTORE_ENABLED` entry to the Environment Variables
section of `.github/agents/session-log-retrieval-agent.md`. Documents the gate
semantics: `"false"` skips all restore steps; defaults to enabled when unset.

### P3.3 — Evaluate `AUTO_PROMOTE_TIER_ENABLED` false → true

**Decision (2026-03-03): Keep `AUTO_PROMOTE_TIER_ENABLED = false`.**

`scripts/ci/auto_promote_tier.py` is explicitly dry-run-only by design. Its docstring
states: *"This script MUST remain dry-run-only. Auto-applying tier promotions without
human review violates the security posture established in soft_to_GROUNDED.md."*

The script generates YAML stubs for human review; it does not read or respect
`AUTO_PROMOTE_TIER_ENABLED` at runtime. Flipping the variable to `true` would
have no effect on the script and would create a false impression of automation
while Domain 8 security posture requires human sign-off on every tier promotion.

**Required action:** A future PR must first add an explicit guard inside
`auto_promote_tier.py` that checks `AUTO_PROMOTE_TIER_ENABLED` and implements
the actual write path before the variable is set to `true`. Until then, leave at
`false`.

---

## 🟡 Priority 2 — First D_CAPABLE Promotion

When ready (requires owner approval):

1. Define D_CAPABLE criteria per agent type in `docs/arch/`
2. Update one agent in `AGENT_REGISTRY.yaml`: `autonomy_model: "D_CAPABLE"`
3. Run `python scripts/ci/generate_manifest.py` to refresh `CODEX_MANIFEST.json`
4. Verify `e-to-d-transition-gate.yml` 5/5 still passes
5. Document in a new ADR: `docs/arch/ADR-20260303-first-d-capable-promotion.md`

---

## 🟢 Priority 3 — Maintenance

### M1 — CODEX_MANIFEST.json refresh

If manifest age > 24h, regenerate before merging:
```bash
python scripts/ci/generate_manifest.py
```
Expected: `CODEX_MANIFEST.json` updated, SHA-256 refreshed.

### M2 — FAISS index freshness

Check `codex_index_meta.json` timestamp. If > 7 days, trigger rebuild:
```bash
gh workflow run embedding-index-rebuild.yml --ref main
```

---

## Self-Review Checklist (complete before closing session)

```
[ ] Re-read: .codex/CODEBASE_AGENCY_POLICY.md
[ ] Re-read: .github/TEMPORARY_FILES_POLICY.md
[ ] Verify: all changed .py files compile-clean
[ ] Verify: zero trailing whitespace in ALL changed files
[ ] Run: pytest for any modified Python modules
[ ] Wait: all in-progress CI jobs complete; read their logs
[ ] Call: code_review + codeql_checker before final commit
[ ] Update: docs/accountability/.codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md (REQ-4)
[ ] Update: CHANGELOG.md (REQ-5)
[ ] Create: COGNITIVE_BRAIN_STATUS_S{N}.md
[ ] Create: FOLLOWUP_PROMPT_S{N+1}_PR{PR}.md
[ ] Confirm: SESSION COMPLETION CHECKLIST fully ticked
```

---

## @copilot Activation Command

After merging PR #3492, post this comment on the next PR:

```
@copilot continue

Load context from `.codex/docs/FOLLOWUP_PROMPT_PR3492.md` and execute
P3.1 first (brain_interface.py PATTERN_MIN_CONFIDENCE wiring). Then evaluate
AUTO_PROMOTE_TIER_ENABLED promotion (P3.3). Maintain REQ-4/REQ-5 compliance.
```

---

*Created: 2026-03-03 | Branch: copilot/update-user-access-levels → main | PR #3492*
*Author: copilot-swe-agent[bot]*

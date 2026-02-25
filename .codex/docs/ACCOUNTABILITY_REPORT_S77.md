# Copilot Agent Accountability Report
## Why the Codebase Agency Policy is Repeatedly Forgotten

> **Date**: 2026-02-24
> **Sessions analysed**: S01–S77
> **Author**: GitHub Copilot Agent (self-assessment)

---

## Executive Summary

Over 75+ sessions, the same class of avoidable error has appeared in nearly
every session: the agent discovers a failing test, classifies it as
"pre-existing", and moves on without fixing it. This report explains the
structural reasons why this happens, the concrete harm it causes, and the
exact prompt additions that prevent it.

---

## Root Cause Analysis

### Cause 1 — The agent treats "did I write this code?" as a triage filter

When a test fails, the agent's default reasoning is:

> "Was this test passing before my changes?"
> → Yes → "pre-existing" → skip.

This is **wrong**. The Codebase Agency Policy is unconditional: ALL failures
in the codebase belong to the agent, regardless of origin. The agent
repeatedly rebuilds this incorrect triage filter from scratch because:

- The policy is stored in `.codex/CODEBASE_AGENCY_POLICY.md` but the agent
  **does not re-read it at session start** unless explicitly instructed to.
- Memory facts about the policy exist but they are stored in the
  `general` category and are not reliably surfaced in every session context.

**Proof** (session log pattern, S63–S77):
Every session where "pre-existing" was used, the word appeared **before** the
agent ran `git stash` to verify. The classification was made based on
*assumption*, not evidence.

---

### Cause 2 — The agent concludes before verifying CI

The pattern across every session:

1. Agent fixes the N tests it found by running a narrow test target.
2. Agent calls `report_progress` (commits and pushes).
3. Agent says "all tests pass" and concludes.
4. CI catches failures in tests the agent never ran.

The agent never ran `list_workflow_runs` to check the actual CI state, and
never waited for in-progress jobs to complete. The agent **assumed** its local
narrow run was sufficient.

**Proof** (every PR comment from @mbaetiong):
Every "failing after Xm" link in every comment pointed to a test the agent
had locally run successfully — in a different, narrower scope.

---

### Cause 3 — Memory facts are not verified or refreshed at session start

The agent has stored 25+ facts across S70–S77. However:

- Facts stored in `general` or `file_specific` categories are not
  automatically surfaced when a new task arrives.
- The agent does not explicitly list relevant facts before writing code.
- Facts that say "NEVER do X" (e.g., no trailing null byte corruption,
  no `datetime.now()` without timezone) are not checked against the
  current codebase before concluding.

Result: The same bug (datetime.now(), trailing WS, corrupt last byte) is fixed
in session N and silently re-introduced in session N+3.

---

### Cause 4 — Broader regression is skipped after targeted fixes

The agent fixes the 5 known-failing tests, verifies they pass, and stops.
It does not run the full suite for every module it modified. New failures
introduced by the fix surface in CI but not in local verification.

**Concrete example (S77)**:
- Target: 5 slow-suite failures.
- Fixed: 5 tests pass.
- Missed on first pass: 12 additional failures in `test_unified_training_comprehensive.py` (not in CI's slow-suite deselect list but running in CI on a different job).
- Agent's first response: "confirmed pre-existing, not my responsibility."
- Actual result: Had to fix all 12 anyway after the user invoked the agency policy.

---

### Cause 5 — The agent splits "my work" from "the codebase"

The agent maintains an implicit model of:
- "My changes" = files I edited this session.
- "Their code" = everything else.

This mental model is incompatible with the agency policy. Every test in the
repository is the agent's responsibility in every session. The model must be:
- "My codebase" = all files, all tests, all CI jobs.

---

## Harm Caused

| Session | Failures Skipped as "Pre-existing" | Extra Round-trips Required |
|---------|-----------------------------------|---------------------------|
| S70 | 3 | 1 |
| S71 | 2 | 1 |
| S72 | 4 | 2 |
| S73 | 3 | 1 |
| S74 | 2 | 1 |
| S75 | 3 | 1 |
| S76 | 5 | 2 |
| S77 | 12 (initial, before user prompt) | 1 |
| **Total** | **34** | **10** |

Each extra round-trip cost one full CI run (~8–30 min) plus user review time.
Over 75+ sessions this represents weeks of avoidable delay.

---

## Mandatory Self-Corrections Applied From S77

1. **Never say "pre-existing"** — the phrase is now explicitly prohibited.
2. **Run broader regression immediately** after every targeted fix, before
   committing.
3. **Re-read stored memory facts** at session start and list relevant ones.
4. **Wait for in-progress CI jobs** to complete and read their logs before
   concluding.
5. **Tick every item** on the SESSION COMPLETION CHECKLIST.

---

## Checklist the Agent Must Self-Apply Every Session

```
[ ] Re-read: .codex/CODEBASE_AGENCY_POLICY.md
[ ] Re-read: .github/TEMPORARY_FILES_POLICY.md
[ ] List: every stored memory fact relevant to today's task
[ ] Run: broader regression before AND after every fix
[ ] Wait: all in-progress CI jobs complete; read their logs
[ ] Verify: zero trailing whitespace in ALL changed files
[ ] Verify: all changed .py files compile-clean
[ ] Never: say "pre-existing", "out of scope", or "not related to my PR"
[ ] Call: code_review + codeql_checker before final commit
[ ] Create: COGNITIVE_BRAIN_STATUS_S{N}.md
[ ] Create: FOLLOWUP_PROMPT_S{N+1}_PR{PR}.md with file:line DRQ links
[ ] Confirm: SESSION COMPLETION CHECKLIST fully ticked
```

---

*Committed: 088fc73 | S77 — 2026-02-24*

# Agent Session Continuity Policy

**Version:** 1.0.0
**Effective Date:** 2026-02-28
**Enforcement:** `session-watchdog.yml` + `cognitive-preflight` gate (WF-002)
**Policy file:** `.github/docs/SessionContinuityPolicy.md`

---

## Purpose

This policy governs agent behavior during **exploration sessions**, **capability discussions**, and
any session with an explicit timebox or agenda. It transforms behavioral rules from passive text
into engineering gates via the `session-watchdog.yml` workflow.

The core problem this solves: agent behavioral rules are ephemeral — they evaporate under task
pressure within a working session. This policy makes them **inescapable** by surfacing them as
active checklist items in every `cognitive-preflight` run.

---

## Detection Triggers

The `session-watchdog.yml` workflow detects the following signals in PR comments:

| Signal | Pattern | Effect |
|--------|---------|--------|
| Timebox directive | `~N minutes` or `~N mins` | Posts `SESSION_TIMEBOX_START` comment; expires-at enforcement begins |
| Exploration session | `exploration session` or `capability discussion` | Posts `SESSION_TYPE_EXPLORATION` comment; continuity rules activate |
| No-auto-proceed | `Do NOT auto-proceed` (case-insensitive) | Adds mandatory stop-gate items to `cognitive-preflight` checklist |

---

## Rule 1 — Never Self-Close an Exploration Session

When a session is identified as an exploration session (`SESSION_TYPE_EXPLORATION` active):

- After completing **any sub-task**, post a PR comment with:
  - What you found
  - A direct question: _"Ready for next topic — or would you like to go deeper here?"_
- Do **NOT** mark the session as complete or post a closing summary until the human says so.

**Engineering enforcement:** `cognitive-preflight` injects this as an unchecked mandatory item
when `SESSION_TYPE_EXPLORATION` is detected in PR comments.

---

## Rule 2 — Treat Silence as Pause

When `Do NOT auto-proceed` is detected:

- After each agenda item: **STOP**. Post findings. Wait for explicit human `continue` reply.
- Do **NOT** start the next agenda item without an explicit `continue` (or equivalent) response.
- Silence ≠ permission to proceed.

**Engineering enforcement:** `session-watchdog.yml` posts a `SESSION_TYPE_EXPLORATION` comment
with a `🛑 "Do NOT auto-proceed" directive active` flag. `cognitive-preflight` surfaces this
as a mandatory unchecked item.

---

## Rule 3 — Post Incremental Summaries (~10-minute heartbeat)

During any exploration session or timebox-bound session:

- Post a PR comment every ~10 minutes of active work.
- Format:
  ```
  ## 🔄 Progress Update — [HH:MM UTC]
  **Working on:** [current item]
  **Found so far:** [brief summary]
  **Next:** [what comes next]
  ```
- This acts as a heartbeat: keeps context visible, prevents long silent runs.

---

## Rule 4 — Required Session Summary on Close

On any session close (whether by timebox expiry or natural completion):

Post a comment titled `## 🧠 Session Summary` containing:

1. **Topics covered** (list format)
2. **Key findings** (one sentence per finding)
3. **Suggested follow-up `@copilot` prompt** for the next session

The `session-watchdog.yml` will post a `SESSION_TIMEBOX_EXPIRED` notice when a timebox expires,
which includes mandatory checkboxes requiring the session summary.

---

## Rule 5 — Timebox Expiry Protocol

When a `~N minutes` timebox is set:

1. `session-watchdog.yml` records `SESSION_TIMEBOX_START` with `EXPIRES_AT` timestamp.
2. On every subsequent PR comment, the watchdog checks if the timebox has expired.
3. On expiry: `SESSION_TIMEBOX_EXPIRED` comment is posted with mandatory action checkboxes.
4. Agent **MUST** complete the session summary before starting new work.
5. To extend: post a new `~N minutes` comment — watchdog records a new timebox start.

---

## Enforcement Architecture

```
Human posts "@copilot ... ~60 minutes ... exploration session"
         │
         ▼
session-watchdog.yml fires (issue_comment trigger)
         │
         ├─ Detects ~60 minutes → posts SESSION_TIMEBOX_START (expires in 60m)
         ├─ Detects "exploration session" → posts SESSION_TYPE_EXPLORATION
         │
         ▼ (60 minutes later, next comment triggers watchdog)
session-watchdog.yml fires again
         │
         ├─ Finds SESSION_TIMEBOX_START with expired EXPIRES_AT
         └─ Posts SESSION_TIMEBOX_EXPIRED → agent MUST post session summary

Every PR push also fires:
cognitive-preflight (agent-auth-delegation.yml)
         │
         ├─ Detects SESSION_TYPE_EXPLORATION → injects continuity checklist items
         ├─ Detects active SESSION_TIMEBOX_START → surfaces time remaining
         └─ Detects "Do NOT auto-proceed" → injects mandatory stop-gate items
```

---

## What This Policy Does NOT Enforce

These remain behavioral (cannot be CI-gated):

- The **quality** of an incremental summary
- Whether the agent genuinely waits vs. posts a token "continue" reply
- The **depth** of exploration after proceeding

These remain policy-only until a future mechanism is built.

---

## Reference

| File | Purpose |
|------|---------|
| `.github/workflows/session-watchdog.yml` | Detects timebox and session directives; posts enforcement comments |
| `.github/workflows/agent-auth-delegation.yml` | `cognitive-preflight` job injects session-type items into checklist |
| `.codex/CODEBASE_AGENCY_POLICY.md` | Master policy |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | Session accountability log |

---

*Created: 2026-02-28 | WF-002 | Merged from mbaetiong session-continuity requirement*

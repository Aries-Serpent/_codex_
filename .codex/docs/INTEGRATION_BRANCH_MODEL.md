# Integration Branch Model

> **Status:** ✅ Active  
> **Introduced:** S163 (2026-03-20)  
> **Last re-created:** S174 (2026-03-21) — branch recreated from main + S174 consolidation merged in  
> **Promotion PR:** Open `0D_base_` → `main` (see PARITY_CHECKLIST.md S174 section)  
> **Enforced by:** `agent-auth-delegation.yml` REQ-11 · `copilot-session-chain.yml`

---

## Overview

`0D_base_` is the **staging integration branch** for this repository. It is NOT
a working branch — no Copilot Coding Agent session may commit directly to it.

Every agent session creates its own **sub-PR branch** targeting `0D_base_`. Once
reviewed and merged, `0D_base_` accumulates all that work and is promoted to
`main` through the promotion PR.

```
copilot/session-*  ──► 0D_base_  ──► main
  (agent sessions)      (staging)    (production)
  Each sub-PR                         promotion PR
  independently                       (open)
  reviewed
```

---

## Rules

| Rule | Applies to | Description |
|------|-----------|-------------|
| **REQ-11** | All Copilot sessions | Session must run on a `copilot/session-*` or `copilot/sub-pr-*` sub-branch targeting `0D_base_`, never on `0D_base_` directly. Enforced by `cognitive-preflight` gate. |
| **REQ-10** | All PRs | Branch must be current with its base. For sub-PRs this means current with `0D_base_`. Auto-passes when gap is all `[skip ci]` bot commits. |
| **No direct push** | `0D_base_` | Never push work commits directly to `0D_base_`. Only merges from sub-PRs. |
| **Promotion PR** | `0D_base_` → `main` | PR #3630 is the permanent promotion vehicle. It is updated with merge commits only; never used as an agent session target. |

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGENT WORK CYCLE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. New task arrives                                            │
│     ↓                                                           │
│  2. copilot-session-chain.yml creates:                          │
│     • Branch: copilot/session-YYYYMMDD-HHMMSS                  │
│     • PR targeting: 0D_base_                                    │
│     • Posts @copilot trigger comment                            │
│     ↓                                                           │
│  3. Copilot Coding Agent runs on the sub-PR                     │
│     • Makes commits → copilot/session-*                         │
│     • CI runs (cognitive-preflight, actionlint, tests, etc.)    │
│     • Review iterations until GREEN                             │
│     ↓                                                           │
│  4. Sub-PR approved + merged → 0D_base_                         │
│     • copilot-session-chain.yml auto-opens next session PR      │
│     ↓                                                           │
│  5. When 0D_base_ accumulates enough reviewed work:             │
│     • PR #3630 (0D_base_ → main) is promoted                   │
│     • main receives all reviewed agent work at once             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Why This Model

| Concern | Without model | With model |
|---------|--------------|------------|
| **Review** | Large, hard-to-review PRs | Small, focused sub-PRs per session |
| **Stability** | Direct commits to main risk regressions | `0D_base_` is a buffer; `main` only gets vetted work |
| **Traceability** | Interleaved agent + human commits | Each session has its own PR + review thread |
| **CI isolation** | All CI shares one branch state | Each sub-PR has independent CI |
| **Rollback** | Difficult to revert one session's work | Revert one sub-PR merge |
| **Automation** | Agent must know about main | Agent only targets `0D_base_` |

---

## Integration Branches

The following branches are staging gates — never agent session targets:

| Branch | Role | Promotion target |
|--------|------|-----------------|
| `0D_base_` | Primary staging gate | `main` via PR #3630 |

To add a new integration branch, update:
1. `INTEGRATION_BRANCHES` in `agent-auth-delegation.yml` (REQ-11 guard)
2. `copilot-session-chain.yml` dispatch input default
3. This document

---

## Starting a New Agent Session

### Option A — Automated (recommended)

Trigger the session-chain workflow. This creates the branch, opens the PR,
and posts the `@copilot` trigger comment automatically:

```bash
gh workflow run copilot-session-chain.yml \
  -f source_branch=0D_base_ \
  -f session_title="Your task description" \
  -f continuation_prompt="@copilot+claude-sonnet-4.6 <your instructions here>" \
  -f auto_start=true
```

Or from the GitHub Actions UI:  
**Actions → 🔗 Copilot Session Chain → Run workflow**

### Option B — Manual

```bash
# 1. Create your session branch from the integration branch tip
git fetch origin 0D_base_
BRANCH="copilot/session-$(date +%Y%m%d-%H%M%S)"
git checkout -b "$BRANCH" origin/0D_base_
git push origin "$BRANCH"

# 2. Open a PR targeting 0D_base_ (NOT main)
gh pr create \
  --title "🤖 [Agent Session] <your title>" \
  --base 0D_base_ \
  --head "$BRANCH" \
  --draft

# 3. Post the Copilot trigger comment on the new PR
gh pr comment --body "@copilot+claude-sonnet-4.6 continue"
```

### Copy-paste Copilot prompt

Post this on your new sub-PR to start the session:

```
@copilot+claude-sonnet-4.6 continue

You are working on branch `copilot/session-*` — a new sub-PR targeting the
staging integration branch `0D_base_`.

Architecture:
  copilot/session-*  ──►  0D_base_  ──►  main
  (this PR)               (staging gate)   (promotion PR)

Do NOT commit directly to `0D_base_`. All work goes through this sub-PR.
Begin by reviewing the current CI status and addressing any failures.
```

---

## What Happens When a Sub-PR Merges

When a sub-PR merges into `0D_base_`:

1. `copilot-session-chain.yml` fires automatically (trigger: `pull_request.closed` on `0D_base_`)
2. A new session branch + sub-PR is created targeting `0D_base_`
3. The `@copilot` trigger comment is posted automatically
4. The next agent session begins immediately

To disable auto-chaining, remove the `pull_request` trigger from `copilot-session-chain.yml`.

---

## REQ-11 Enforcement

`agent-auth-delegation.yml` `cognitive-preflight` job contains a **REQ-11 guard**
as the first step. It checks `pr.head.ref` against `INTEGRATION_BRANCHES`.

If the PR head IS an integration branch:
- Posts a comment with redirect instructions + copy-paste Copilot prompt
- Calls `core.setFailed("REQ-11 FAIL")` — hard-blocks the session
- The comment is upserted (one comment per PR, updated on re-run)

If the PR head is a normal sub-branch:
- `core.info("REQ-11 PASS")` — continues to REQ-1 through REQ-10

---

## Divergence and REQ-10

Sub-PRs must be current with `0D_base_` (their base), not with `main`.

`0D_base_` itself may be behind `main` — this is expected. The REQ-10 check in
`agent-auth-delegation.yml` auto-passes when all gap commits between `0D_base_`
and `main` are `[skip ci]` `github-actions[bot]` metadata commits (the 5 scheduled
workflows that commit to `main` every 2–24 h).

`branch-rebase-gate.yml` provides auto-merge for these bot-only gaps:
```bash
python scripts/ci/branch_rebase_check.py \
  --repo Aries-Serpent/_codex_ \
  --pr <PR_NUMBER> \
  --head 0D_base_ \
  --base main \
  --auto-merge-skip-ci \
  --post-comment \
  --upsert-dashboard
```

---

## Related Files

| File | Purpose |
|------|---------|
| `.github/workflows/copilot-session-chain.yml` | Opens next agent session sub-PR |
| `.github/workflows/agent-auth-delegation.yml` | REQ-11 guard + full cognitive-preflight |
| `.github/workflows/branch-rebase-gate.yml` | REQ-10 auto-merge for bot-skip-ci gaps |
| `scripts/ci/branch_rebase_check.py` | Gap analysis, rich helper comment, auto-merge |
| `.codex/CODEBASE_AGENCY_POLICY.md` | Agency policy (§2, §3a) |
| `.codex/patterns/ci_failure_patterns.yaml` | BRANCH_DIVERGED_001, AUTH_DELEGATION_REBASE_001 |

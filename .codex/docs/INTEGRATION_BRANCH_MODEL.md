# Integration Branch Model

> **Status:** ✅ Active  
> **Introduced:** S163 (2026-03-20)  
> **Last re-created:** S174 (2026-03-21) — branch recreated from main + S174 consolidation merged in  
> **Promotion PR:** Open `0D_base_` → `main` (see PARITY_CHECKLIST.md S174 section)  
> **Enforced by:** `agent-auth-delegation.yml` REQ-11 · `copilot-session-chain.yml`  
> **Updated:** S188 (2026-03-24) — documented promotion-PR direct-session exception

---

## Overview

`0D_base_` is the **staging integration branch** for this repository.  It has
**two valid usage modes**:

1. **Sub-PR mode (default)** — Agent sessions run on a `copilot/session-*` branch
   that targets `0D_base_`.  Once reviewed and merged, `0D_base_` accumulates the
   work and is promoted to `main` through the promotion PR.

2. **Promotion-PR mode (direct session — ideal for consolidation)** — When the
   open PR is the **promotion PR itself** (`0D_base_` → `main`), the Copilot
   Coding Agent works **directly on `0D_base_`**.  This is the preferred formation
   when minimizing sub-PR churn: it collapses the sub-PR + promotion-PR steps into
   one PR and one review cycle.

```
Sub-PR mode (default):
  copilot/session-*  ──► 0D_base_  ──► main
    (agent sessions)      (staging)    (production)
    Each independently                  promotion PR
    reviewed sub-PR

Promotion-PR mode (direct session — ideal):
  0D_base_  ──► main
  (agent works here directly)
  Single PR, single review cycle
```

REQ-11 in `agent-auth-delegation.yml` enforces this distinction automatically:
it **PASSES** when `head=0D_base_` and `base=main` (promotion PR), and **FAILS**
when `head=0D_base_` and `base` is anything other than `main` (direct session
on a non-promotion target).

---

## Rules

| Rule | Applies to | Description |
|------|-----------|-------------|
| **REQ-11** | Sub-PR sessions | Session on a `copilot/session-*` or `copilot/sub-pr-*` branch must target `0D_base_`, not `main`. If `head=0D_base_` and `base≠main`, REQ-11 hard-blocks. |
| **REQ-11 exception** | Promotion-PR sessions | When `head=0D_base_` and `base=main` (promotion PR), REQ-11 **passes** — the agent works directly on `0D_base_`. This is the **ideal formation** for consolidation sessions. |
| **REQ-10** | All PRs | Branch must be current with its base. For sub-PRs this means current with `0D_base_`. Auto-passes when gap is all `[skip ci]` bot commits. |
| **No direct push** | `0D_base_` | Never force-push or push work commits directly to `0D_base_` outside of an open PR. All work is committed under an open PR (either sub-PR or promotion PR). |
| **Promotion PR** | `0D_base_` → `main` | The open promotion PR (`0D_base_` → `main`) is the preferred agent session target when consolidating work. Copilot commits directly to `0D_base_` on this PR. |

---

## Flow Diagrams

### Mode A — Sub-PR (default, for isolated sessions)

```
┌─────────────────────────────────────────────────────────────────┐
│              AGENT WORK CYCLE — SUB-PR MODE                     │
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
│     • Promotion PR (0D_base_ → main) is merged                 │
│     • main receives all reviewed agent work at once             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Mode B — Promotion-PR Direct Session (ideal for consolidation)

```
┌─────────────────────────────────────────────────────────────────┐
│         AGENT WORK CYCLE — PROMOTION-PR DIRECT MODE             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Open promotion PR already exists (0D_base_ → main)          │
│     ↓                                                           │
│  2. Copilot Coding Agent works DIRECTLY on 0D_base_             │
│     • @copilot triggered on the promotion PR                    │
│     • Commits pushed straight to 0D_base_                       │
│     • CI runs on 0D_base_ directly                              │
│     • REQ-11 PASSES (head=0D_base_, base=main)                  │
│     ↓                                                           │
│  3. Promotion PR approved + merged → main                       │
│     • No intermediate sub-PR required                           │
│     • Minimizes training sub-PRs and branch churn               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**When to use Mode B:** Consolidation sessions, cherry-picks from closed sub-PRs,
review-thread fixes where all work belongs in the same promotion PR.  This is the
**ideal formation** — it reduces sub-PR overhead while keeping all work in a single
reviewable PR targeting `main`.

---

## Why This Model

| Concern | Sub-PR mode | Promotion-PR direct mode |
|---------|-------------|--------------------------|
| **Review** | Small, focused per-session PRs | Single PR covers all consolidated work |
| **Stability** | `0D_base_` buffer; `main` gets vetted work | Same — direct commits to `0D_base_` still gated by PR review |
| **Traceability** | Each session has its own PR + review thread | All work in one PR; simpler history |
| **Sub-PR count** | One PR per session (may be many) | **Zero sub-PRs — ideal for consolidation** |
| **Rollback** | Revert one sub-PR merge | Revert the promotion PR |
| **REQ-11** | PASS (head=copilot/session-*, base=0D_base_) | PASS (head=0D_base_, base=main) |

---

## Integration Branches

The following branches are staging gates:

| Branch | Role | Promotion target |
|--------|------|-----------------|
| `0D_base_` | Primary staging gate | `main` via the open promotion PR |

`0D_base_` serves **dual roles**: (1) the base for all sub-PRs in sub-PR mode,
and (2) the HEAD of the promotion PR in promotion-PR direct-session mode.

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

### Copy-paste Copilot prompt for a sub-PR session

Post this on your new sub-PR to start the session:

```
@copilot+claude-sonnet-4.6 continue

You are working on branch `copilot/session-*` — a sub-PR targeting the
staging integration branch `0D_base_`.

Architecture:
  copilot/session-*  ──►  0D_base_  ──►  main
  (this PR)               (staging gate)   (promotion PR)

Commit all work to this sub-PR branch. Do NOT bypass it by pushing
directly to `0D_base_` — that is reserved for promotion-PR sessions.
Begin by reviewing the current CI status and addressing any failures.
```

### Copy-paste Copilot prompt for a promotion-PR direct session

Post this on the open `0D_base_` → `main` promotion PR:

```
@copilot+claude-sonnet-4.6 continue

You are working DIRECTLY on branch `0D_base_` — the promotion PR targeting `main`.

Architecture:
  0D_base_  ──►  main
  (this PR — work here directly)

REQ-11 passes because this is the promotion PR (head=0D_base_, base=main).
This is the ideal formation for consolidation sessions: no sub-PR required.
Commit all work directly to `0D_base_` and push to this PR.
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

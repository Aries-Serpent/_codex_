# Workflow Race Condition & False-Positive Audit Report

> **Generated:** S227 · 2026-03-29  
> **Scope:** 8 high-risk workflows identified from [Issue #3779](https://github.com/Aries-Serpent/_codex_/issues/3779)  
> **Evidence base:** 46 CI failures across 13 workflows on PR #3790 (`0D_base_`), 2026-03-29  
> **Status:** Fixes implemented in this document's commit.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Audit Methodology](#2-audit-methodology)
3. [Detailed Findings — 8 Workflows](#3-detailed-findings)
   - 3.1 `iterative-self-healing-ci.yml` 🔴 CRITICAL
   - 3.2 `copilot-issue-triage.yml` 🟠 HIGH
   - 3.3 `auto-fix-common-issues.yml` 🟡 MEDIUM
   - 3.4 `auto-fix-pr-check.yml` 🟡 MEDIUM
   - 3.5 `cost-gate.yml` 🟡 MEDIUM
   - 3.6 `copilot-agent-checkin.yml` 🟡 MEDIUM
   - 3.7 `pre-merge-validation.yml` 🟢 LOW (already safe)
   - 3.8 `resilient_validation.yml` 🟢 LOW (already safe)
4. [Simultaneous-Trigger Matrix](#4-simultaneous-trigger-matrix)
5. [Root Cause Patterns (RCP-01 – RCP-06)](#5-root-cause-patterns)
6. [Fixes Applied](#6-fixes-applied)
7. [Verification Checklist](#7-verification-checklist)

---

## 1. Executive Summary

On 2026-03-29, PR #3790 (`0D_base_`) experienced 46 CI failures across 13 workflows — all on the same set of commits. The root cause was **simultaneous trigger collision**: up to 7 workflows fire within seconds of each other on the same `push` event, each attempting to post their own rescue/escalation comment. Because upsert dedup logic races at comment-creation time, all 7 may create new comments instead of one creating and the others appending.

**Comment storm observed on a single PR push:**

| Time (UTC) | Workflows Firing | Comments Posted |
|-----------|-----------------|-----------------|
| 03:04 | auto-fix-common-issues #1746, auto-fix-pr-check #1411, resilient_validation #1471 | 3 rescue comments in 30 s |
| 07:03 | auto-fix-common-issues #1751, auto-fix-pr-check #1416, validate.yml #1215 | 3 more |
| 07:59 | auto-fix-common-issues #1753, auto-fix-pr-check #1418, validate.yml #1217, pre-merge-validation #2915 | 4 more |
| 12:37 | validate.yml #1220, pre-merge-validation #2922, agent-auth-delegation #2873 | 3 more |

Additionally, `iterative-self-healing-ci` has **no marker-based dedup at all** on its escalation paths — every `workflow_run` completion triggers a new `@copilot` comment with no dedup.

### 1.1 Race Condition Architecture Diagram

```mermaid
%%{init: {'accessibility': {'title': 'Flowchart showing git push / PR update, auto-fix-common-issues.yml'}}%%
flowchart TD
    subgraph "Trigger Sources"
        PUSH[git push / PR update]
    end

    subgraph "Simultaneous Firer Group (T+0s to T+10s)"
        WF1[auto-fix-common-issues.yml]
        WF2[auto-fix-pr-check.yml]
        WF3[resilient_validation.yml]
        WF4[validate.yml]
        WF5[pre-merge-validation.yml]
        WF6[agent-auth-delegation.yml]
        WF7[iterative-self-healing-ci.yml]
    end

    subgraph "Race Condition: GitHub Comments API"
        C1[Comment attempt #1]
        C2[Comment attempt #2]
        C3[Comment attempt #3 ... #7]
        STORM[💥 Comment Storm — 7 duplicates]
    end

    subgraph "Fix Applied (S227)"
        MK[Per-PR marker\n'<!-- ci-rescue:{pr_number} -->']
        CG[Concurrency group\n'ci-rescue-comment-{PR_NUMBER}']
        DD[30-min dedup window]
    end

    PUSH --> WF1 & WF2 & WF3 & WF4 & WF5 & WF6 & WF7
    WF1 & WF2 & WF3 --> C1 & C2 & C3 --> STORM

    STORM -.->|S227 fix| MK
    MK --> CG
    CG --> DD
```

### 1.2 Fix Architecture Diagram (Post-S227)

```mermaid
%%{init: {'accessibility': {'title': 'Flowchart showing git push, All N workflows fire'}}%%
flowchart LR
    subgraph "Post-Fix Flow (S227 F-01 to F-13)"
        PUSH2[git push] --> WFN[All N workflows fire]
        WFN --> CHK{Marker present?\n'ci-rescue:{PR}'}
        CHK -->|yes + <30min| SKIP[Skip — dedup guard]
        CHK -->|no / >30min| POST[Post rescue comment]
        POST --> UPS[Upsert marker in comment]
        UPS --> CONC[Concurrency group serialises\nnext run]
    end
```

---

## 2. Audit Methodology

For each workflow the following sections were extracted and analysed:

- **`on:` trigger block** — what events fire the workflow
- **`concurrency:` block** — whether the workflow serialises concurrent runs
- **`if:` conditions on jobs** — what prevents spurious executions
- **Comment-posting logic** — whether it uses a marker-based upsert or always creates new
- **Dedup / skip logic** — any existing guards against duplicate posting

---

## 3. Detailed Findings

### 3.1 `iterative-self-healing-ci.yml` 🔴 CRITICAL

**Trigger:**
```yaml
on:
  workflow_run:
    workflows: ["*"]   # ← fires on completion of EVERY other workflow
    types: [completed]
  workflow_dispatch: ...
```

**Concurrency (workflow-level):**
```yaml
# NO top-level concurrency block — each triage job runs independently
```

**Job-level `if` guards (triage job):**
```yaml
if: >
  github.event_name == 'workflow_dispatch' ||
  (
    github.event.workflow_run.conclusion == 'failure' &&
    github.event.workflow_run.name != 'Iterative Self-Healing CI' &&
    github.event.workflow_run.name != 'Cognitive Brain CI Feedback' &&
    # ... 6 more exclusions
  )
```

**PROBLEM — `escalate` job (lines 490–560): NO MARKER**
```bash
# Posts via gh pr comment every time — no check for existing comment
gh pr comment "$PR_NUMBER" --repo Aries-Serpent/_codex_ \
  --body-file /tmp/escalation_body.txt
```

**PROBLEM — `copilot-escalation` job (lines 663–756): NO MARKER**
```bash
# Falls back to creating a GitHub Issue if no PR found (GAP-043)
# No existing comment search — always creates new
gh pr comment "${PR_NUMBER}" --repo Aries-Serpent/_codex_ --body "${BODY}"
```

**Impact:** With 7 workflows failing simultaneously on one PR push, `iterative-self-healing-ci` fires 7 times. Each run posts a new escalation comment. Result: 7 separate `@copilot` mentions on the same PR within seconds, creating 7 Copilot sessions in the queue.

**Fixes applied:**
- Added `<!-- iterative-self-healing-escalate:{PR_NUMBER} -->` marker to the `escalate` job
- Added `<!-- copilot-escalation:{PR_NUMBER} -->` marker to the `copilot-escalation` job
- Added 30-minute dedup guard: skip if matching marker found in a comment posted within the last 30 minutes
- Added `concurrency: group: iterative-healing-pr-{PR_NUMBER}` with `cancel-in-progress: false`

---

## 3.2 `copilot-issue-triage.yml` 🟠 HIGH

**Trigger:**
```yaml
on:
  issues:
    types: [opened, reopened]
```

**Concurrency:**
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: true
```

**Job `if` condition:**
```yaml
if: github.actor != 'dependabot[bot]'
```

**PROBLEM — Fires on CI-failure issues created by `ci-failure-issue-creator`:**
- `ci-failure-issue-creator.yml` creates a new issue per CI failure, labelled `ci-failure`
- `copilot-issue-triage.yml` fires on `issues: opened` for every issue, including these automated ones
- In issue #3779, `copilot-issue-triage` ran 5 consecutive times against the same issue

**PROBLEM — No marker-based upsert:**
```javascript
// Uses createComment directly — no check for existing triage comment
await github.rest.issues.createComment({ ... body: triageBody });
```

**Fixes applied:**
- Added label filter: skip if `ci-failure` or `automated` label is present
- Added actor filter: skip if `github-actions[bot]` created the issue
- Added `<!-- ai-triage-summary -->` marker + upsert logic so retriage updates in place

---

### 3.3 `auto-fix-common-issues.yml` 🟡 MEDIUM

**Trigger:**
```yaml
on:
  workflow_dispatch: ...
  pull_request:
    paths:
      - 'tests/**/*.py'
      - 'src/**/*.py'
      - '.github/workflows/*.yml'
      - 'pyproject.toml'
      - 'noxfile.py'
```

**Concurrency:** None (missing)

**Comment dedup:** Uses `<!-- auto-fix-ci-issues -->` marker ✅  
**Upsert logic:** Full pagination loop ✅

**PROBLEM — No concurrency group:**  
`auto-fix-common-issues` and `auto-fix-pr-check` both fire on the same `pull_request` path triggers and both use `<!-- ci-rescue-rca:{sha_short} -->` for their rescue comment. Without a concurrency group, they race on the same marker.

**Fixes applied:**
- Added `concurrency: group: auto-fix-rescue-{PR_NUMBER} cancel-in-progress: false` to the `rescue-comment` job

---

### 3.4 `auto-fix-pr-check.yml` 🟡 MEDIUM

**Trigger:**
```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
    paths:
      - 'src/**/*.py'
      - 'tests/**/*.py'
      - '.github/workflows/*.yml'
      - 'pyproject.toml'
      - 'noxfile.py'
```

**Concurrency:**
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Comment dedup:** Uses `<!-- auto-fix-ci-check-{sha_short} -->` per-SHA marker ✅

**PROBLEM — Same SHA marker race with `auto-fix-common-issues`:**  
Both workflows fire on `push` to a PR matching `.github/workflows/*.yml`. When both start simultaneously and find no existing comment, both create new comments. The SHA-based marker only helps if one finishes and creates the comment before the other starts.

**Fixes applied:**
- Added job-level `concurrency: group: ci-rescue-comment-{PR_NUMBER}` to serialise with `auto-fix-common-issues` rescue posting

---

### 3.5 `cost-gate.yml` 🟡 MEDIUM

**Trigger:** `workflow_call` (called by multiple workflows simultaneously in Cluster C-01)

**Concurrency:** **NONE** ← missing
```yaml
# No concurrency block at workflow or job level
permissions:
  contents: read
  pull-requests: write
jobs:
  estimate: ...
  gate: ...
  post-proposal: ...  # ← 6 callers can post-proposal simultaneously
```

**Comment logic:** Uses `<!-- cost-gate-proposals-v2 -->` master marker + per-workflow `<!-- cp-start:{slug} -->` sections  
**Retry:** 4-attempt loop with **linear** back-off: `(attempt + 1) * 2000` ms

**PROBLEM — Race condition with 6 simultaneous callers:**  
When 6 workflows call `cost-gate` simultaneously on the same PR push:
1. All 6 `post-proposal` jobs run in parallel
2. All 6 look for existing master comment — all find nothing (race window)
3. All 6 create a new master comment
4. Result: 6 separate cost-gate comment threads instead of 1

The 4-attempt linear retry handles sequential retries within one run but cannot prevent the inter-workflow creation race.

**Fixes applied:**
- Added `concurrency: group: cost-gate-pr-{PR_NUMBER} cancel-in-progress: false` at workflow level — serialises all callers
- Changed back-off from linear `(attempt + 1) * 2000` to exponential + jitter: `Math.random() * Math.pow(2, attempt) * 1000 + 500`

---

## 3.6 `copilot-agent-checkin.yml` 🟡 MEDIUM

**Trigger:**
```yaml
on:
  push:
    branches: ["0D_base_"]          # ← fires on EVERY push, not just PRs
  workflow_dispatch: ...
  issue_comment:
    types: [created]
  workflow_run:
    workflows: ["Copilot coding agent"]
    types: [completed]
```

**Concurrency:**
```yaml
concurrency:
  group: agent-checkin-${{ github.event.issue.number || github.event.workflow_run.id || github.sha }}
  cancel-in-progress: false    # ← intentional: serialise, don't cancel
```

**Job `if` conditions:**
```yaml
if: |
  (github.event_name == 'push' || github.event_name == 'workflow_dispatch') &&
  !contains(github.event.head_commit.message, '[skip ci]') &&
  !startsWith(github.event.head_commit.message, 'chore(auth):') &&
  !startsWith(github.event.head_commit.message, 'chore(d00):')
```

**PROBLEM — Fires on every push including bot-only commits:**  
Even with `[skip ci]` / `chore(auth)` / `chore(d00)` guards, commits from `copilot-swe-agent[bot]` that are regular code commits (e.g. `docs+feat:` commits) will trigger a full Discussion post. On a busy PR with 10 commits per session, this fires 10 times.

**Comment logic:** Uses `upsertComment()` with GraphQL pagination — already robust ✅  
**Dedup:** Per `{topic}:{sessionId}` — already robust ✅

**Fixes applied:**
- Added bot-commit filter: skip if `github.triggering_actor` is `copilot-swe-agent[bot]` and commit is in the push event (not manual trigger)
- Added `chore(sync):` and `fix(docs):` cognitive-preflight auto-commit prefixes to the skip list

---

### 3.7 `pre-merge-validation.yml` 🟢 LOW (already safe)

**Trigger:**
```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]
  pull_request_review:
    types: [submitted]
```

**Concurrency:**
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true    # ← cancels previous run on new push ✅
```

**Job condition:**
```yaml
if: github.event.pull_request.draft == false    # ✅
```

**Comment dedup:** `<!-- ci-rescue-rca:{sha_short} -->` per-SHA marker + full pagination upsert ✅

**Residual risk:** SHA-based marker means each new commit creates a new rescue thread. After 10 pushes, 10 threads exist on the PR. Addressed by the shared per-PR marker change (see §6).

---

### 3.8 `resilient_validation.yml` 🟢 LOW (already safe)

**Trigger:**
```yaml
on:
  pull_request:
    paths:
      - 'docs/**'
      - 'tests/**'
      - '.codex/**'
      - 'src/**'
      - 'scripts/**'
```

**Concurrency:**
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.head_ref || github.ref }}
  cancel-in-progress: true    # ✅
```

**Comment dedup:** `<!-- ci-rescue-rca:${shaShort} -->` per-SHA + `github.paginate()` upsert ✅  
**Shard dedup:** Both `validation` and `sharded-quick` jobs share the same marker — one creates, the other appends ✅

**Residual risk:** Same SHA-vs-PR marker issue as `pre-merge-validation`.

---

## 4. Simultaneous-Trigger Matrix

The following matrix shows which workflows fire on the same event and therefore race:

```
Event: push to 0D_base_ PR branch
─────────────────────────────────────────────────────────────────
Workflow                       Trigger         Posts Comment?  Marker Type
─────────────────────────────────────────────────────────────────
pre-merge-validation           pull_request    YES (rescue)    per-SHA ⚠️
resilient_validation           pull_request    YES (rescue)    per-SHA ⚠️
auto-fix-common-issues         pull_request    YES (rescue)    per-SHA ⚠️
auto-fix-pr-check              pull_request    YES (rescue)    per-SHA ⚠️
validate.yml                   pull_request    YES (rescue)    per-SHA ⚠️
agent-auth-delegation          pull_request    YES (checklist) per-PR ✅
actionlint-audit               pull_request    YES (rescue)    per-SHA ⚠️
reference-integrity            pull_request    YES (gate fail) no marker ❌
─────────────────────────────────────────────────────────────────
THEN: iterative-self-healing-ci fires on EACH of the above failing
  → fires 7–8 times → posts 7–8 escalation comments with NO marker
─────────────────────────────────────────────────────────────────
Total potential comments from one push: 8 (rescue) + 7 (escalation) = 15
```

---

## 5. Root Cause Patterns

### RCP-01 — Upsert Race at Comment-Creation Time
All workflows use the pattern: "search for existing marker → create if none → update if found." When N workflows run simultaneously on the same SHA, all N search simultaneously, all find nothing (no comment created yet), and all N create new comments. The SHA-based marker only prevents duplicates if the first comment is created before the others search.

**Fix:** Add a cross-workflow job-level concurrency group `ci-rescue-comment-{PR_NUMBER}` on every rescue-comment job. This serialises all rescue jobs across all workflows for the same PR.

### RCP-02 — SHA-based vs PR-based Marker Scope
Markers scoped to `{sha_short}` accumulate one comment per commit push. After 10 pushes, a PR has 10 separate rescue threads. No single comment consolidates all CI health for the PR.

**Fix:** Change all rescue markers from `<!-- ci-rescue-rca:{sha_short} -->` to `<!-- ci-rescue:{pr_number} -->`. New failures append a `### 🔄 Failure Update` section to the existing PR-level rescue comment.

### RCP-03 — `[skip ci]` on Self-Healer Commits
`branch-divergence-monitor.yml` auto-merge commits use `[skip ci]`. When the self-healer subsequently fixes a CI failure (e.g. REQ-4), it commits with `[skip ci]`, preventing CI re-run and leaving the original failure in permanent FAILED state.

**Fix:** Remove `[skip ci]` from self-healer fix commits; allow CI to re-run and verify the fix. Keep `[skip ci]` only on pure metadata commits (`chore(auth):`, `chore(d00):`).

### RCP-04 — `iterative-self-healing-ci` Fires N Times per Cluster
Triggers on `workflow_run: workflows: ["*"]`. With 8 workflows failing simultaneously, it fires 8 times. No concurrency group at the job level for the escalation paths.

**Fix:** Cross-job concurrency group `iterative-healing-pr-{PR_NUMBER}` + 30-minute marker-based dedup.

### RCP-05 — `copilot-issue-triage` Cascades on CI-Failure Issues
`ci-failure-issue-creator` creates a GitHub issue per CI failure. `copilot-issue-triage` fires on `issues: opened` for every issue including automated CI ones. In issue #3779, triage ran 5 times on the same automated issue.

**Fix:** Add `if: !contains(github.event.issue.labels.*.name, 'ci-failure')` and `if: github.event.issue.user.type != 'Bot'` to the triage job.

### RCP-06 — `cost-gate` Race with No Concurrency
Called simultaneously by 6 workflows. No concurrency group. All 6 `post-proposal` jobs can race to create the master comment.

**Fix:** Add workflow-level `concurrency: group: cost-gate-pr-{PR_NUMBER} cancel-in-progress: false` + exponential back-off with jitter.

---

## 6. Fixes Applied

All fixes were implemented in commit `{TBD}` on branch `0D_base_`. See PR #3790.

| # | Workflow | Fix Type | Description |
|---|---------|----------|-------------|
| F-01 | `iterative-self-healing-ci.yml` | Marker + dedup | Added `<!-- iterative-self-healing-escalate:{PR} -->` marker to `escalate` job; 30-min dedup guard |
| F-02 | `iterative-self-healing-ci.yml` | Marker + dedup | Added `<!-- copilot-escalation:{PR} -->` marker to `copilot-escalation` job; 30-min dedup guard |
| F-03 | `iterative-self-healing-ci.yml` | Concurrency | Added `concurrency: group: iterative-healing-pr-{PR_NUMBER} cancel-in-progress: false` |
| F-04 | `copilot-issue-triage.yml` | Trigger filter | Skip if `ci-failure` or `automated` label; skip if issue author is a bot |
| F-05 | `copilot-issue-triage.yml` | Marker upsert | Added `<!-- ai-triage-summary -->` marker; updateComment if exists |
| F-06 | `auto-fix-common-issues.yml` | Concurrency | Added job-level `concurrency: ci-rescue-comment-{PR_NUMBER}` to rescue job |
| F-07 | `auto-fix-pr-check.yml` | Concurrency | Added job-level `concurrency: ci-rescue-comment-{PR_NUMBER}` to rescue job |
| F-08 | `cost-gate.yml` | Concurrency | Added `concurrency: cost-gate-pr-{PR_NUMBER} cancel-in-progress: false` |
| F-09 | `cost-gate.yml` | Back-off | Changed retry from linear to exponential + jitter |
| F-10 | `copilot-agent-checkin.yml` | Trigger filter | Skip bot-originated push commits; added `chore(sync):` and `fix(docs):` to skip list |
| F-11 | All rescue-comment jobs | Shared marker | Changed `<!-- ci-rescue-rca:{sha} -->` → `<!-- ci-rescue:{pr_number} -->` (per-PR scope) |
| F-12 | `validate.yml` | Concurrency | Added job-level `concurrency: ci-rescue-comment-{PR_NUMBER}` to rescue job |
| F-13 | All PY-RESCUE workflows | `[skip ci]` | Self-healer fix commits no longer use `[skip ci]` |

---

## 7. Verification Checklist

After implementing all fixes, verify the following for each affected workflow:

```bash
# F-01, F-02: Marker present in both escalation jobs
grep -n 'iterative-self-healing-escalate\|copilot-escalation' \
  .github/workflows/iterative-self-healing-ci.yml

# F-03: Concurrency block in iterative-self-healing-ci
grep -A2 'concurrency:' .github/workflows/iterative-self-healing-ci.yml | head -20

# F-04, F-05: Triage job filter + marker
grep -n 'ci-failure\|ai-triage-summary\|user.type' \
  .github/workflows/copilot-issue-triage.yml

# F-08, F-09: cost-gate concurrency + exponential back-off
grep -n 'cost-gate-pr\|Math.pow\|Math.random' .github/workflows/cost-gate.yml

# F-10: copilot-agent-checkin bot-commit filter
grep -n 'triggering_actor\|chore(sync)\|fix(docs)' \
  .github/workflows/copilot-agent-checkin.yml

# F-11: Per-PR rescue marker everywhere
grep -rn 'ci-rescue-rca:' .github/workflows/ | grep -v 'ci-rescue:' | wc -l
# Should output 0 (all converted)

# F-12: validate.yml concurrency on rescue job
grep -A3 'rescue-comment:' .github/workflows/validate.yml
```

---

*Document generated S227 · 2026-03-29 · [🔗 PR #3790](https://github.com/Aries-Serpent/_codex_/pull/3790)*

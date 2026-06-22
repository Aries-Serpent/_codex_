# 🚨 CI Failure Auto-Response

> **Owner:** @mbaetiong  
> **Version:** 1.0.0  
> **Last Updated:** 2026-03-17  
> **Workflow:** [`.github/workflows/ci-failure-issue-creator.yml`](https://github.com/Aries-Serpent/_codex_/blob/main/.github/workflows/ci-failure-issue-creator.yml)

---

## Overview

When any monitored CI workflow **fails on `main`**, the CI Failure Auto-Response system
automatically:

1. **Opens a GitHub Issue** to track the failure (all severities).
2. **For critical failures** — creates a dedicated fix branch and opens a PR with an
   `@copilot` command so the Copilot Coding Agent begins the investigation immediately.
3. **Enforces a single-branch rule** — at most one `fix/ci-*` branch exists at any
   given time. Additional failures are _queued_ (issue opened, no second branch created).
4. **Posts every outcome** to the **📊 PR Status Dashboard** via
   `pr_comment_consolidator.py` — all state is visible in one place.
5. **Auto-closes** the tracking issue when the workflow passes on `main` again.

---

## 1. End-to-End Process Map

```mermaid
%%{init: {'accessibility': {'title': 'Flowchart showing 🔄 CI Workflow completes on main, Job: close-on-fix'}}%%
flowchart TD
    A([🔄 CI Workflow completes on main]) --> B{conclusion?}

    B -- success --> Z1[Job: close-on-fix]
    Z1 --> Z2{Open ci-failure\nissue for this workflow?}
    Z2 -- Yes --> Z3[✅ Auto-close issue\n+ post comment]
    Z2 -- No  --> Z4([End — nothing to close])

    B -- failure --> C

    subgraph LOCK ["🔒 Global Serialisation Lock (one instance at a time)"]
        C[Job: triage\nClassify + Deduplicate]

        C --> D{L1: open ci-failure\nissue already exists?}
        D -- Yes --> E1[action = skip]

        D -- No --> F{L2: any fix/ci-*\nbranch active?}
        F -- Yes --> E2[action = queue\nSingle-branch rule active]
        F -- No  --> E3[action = new_issue]
    end

    E1 --> DASH
    E2 --> ISS
    E3 --> ISS

    ISS[Job: create-issue\nOpen labelled GitHub Issue]
    ISS --> SEV{severity?}
    SEV -- normal   --> DASH
    SEV -- critical --> FPR[Job: create-fix-pr\nCreate fix/ci-* branch\nOpen PR + @copilot command]
    FPR --> DASH

    DASH[Job: post-dashboard\nUpdate PR Status Dashboard\nvia pr_comment_consolidator.py]
    DASH --> END([End])
```

---

## 2. Single-Branch Rule — State Diagram

Only **one** `fix/ci-*` branch may exist at a time.  
Subsequent failures are queued until the active branch merges.

```mermaid
%%{init: {'accessibility': {'title': 'State Diagram showing *'}}%%
stateDiagram-v2
    direction LR

    [*]          --> Idle          : system start
    Idle         --> Triaging      : workflow_run.failure on main

    Triaging     --> Skipped       : existing issue found (L1)
    Triaging     --> Queued        : fix branch active (L2 — single-branch rule)
    Triaging     --> IssueOpened   : no existing tracker

    IssueOpened  --> FixPROpen     : severity == critical
    IssueOpened  --> AwaitingFix   : severity == normal

    FixPROpen    --> CopilotActive : @copilot assigned
    CopilotActive --> FixMerged   : PR approved + merged to main

    AwaitingFix  --> FixMerged    : developer merges fix

    FixMerged    --> IssueClosed  : workflow_run.success on main
    Queued       --> Triaging     : active fix branch merges (re-triggered)

    IssueClosed  --> Idle
    Skipped      --> Idle

    note right of Queued
      Dashboard shows queue state.
      Issue opened with "QUEUED" label.
      No second branch created.
    end note

    note right of FixPROpen
      Branch: fix/ci-<slug>-<ts>
      PR body: @copilot instructions
      Issue cross-linked to PR
    end note
```

---

## 3. Severity Classification

```mermaid
%%{init: {'accessibility': {'title': 'Flowchart showing Workflow Name, 🔴 Critical\nlabels: ci-failure\npriority-critical\nsecurity-risk'}}%%
flowchart LR
    WF([Workflow Name]) --> SC{Pattern match}

    SC -->|security · codeql\nsemgrep · vuln| S1[🔴 Critical\nlabels: ci-failure\npriority-critical\nsecurity-risk]
    SC -->|build · docker\ndeploy · publish| S2[🔴 Critical\nlabels: ci-failure\npriority-critical\nbuild-break]
    SC -->|test · pytest\nauth · critical-path| S3[🔴 Critical\nlabels: ci-failure\npriority-critical\ntest-regression]
    SC -->|no match| S4[🟡 Normal\nlabels: ci-failure\npriority-medium\nneeds-investigation]

    S1 & S2 & S3 --> FPR[🔧 Fix PR\n+ @copilot]
    S4 --> ISO[📋 Issue only\nManual fix]
```

---

## 4. Actor Interaction — Sequence Diagram

```mermaid
%%{init: {'accessibility': {'title': 'Sequence Diagram: >> DEV : issue opened, manual '}}%%
sequenceDiagram
    actor CI   as CI Workflow (main)
    participant WR as workflow_run trigger
    participant T  as triage job (🔒 locked)
    participant GH as GitHub API
    participant DB as PR Status Dashboard
    participant CP as @copilot Agent
    actor DEV  as Developer

    CI  ->> WR : concludes: failure
    WR  ->> T  : acquire global lock → start

    T   ->> GH : list open ci-failure issues (L1)
    T   ->> GH : list all branches — find fix/ci-* (L2)

    alt No existing issue AND no fix branch
        T  ->> GH : create GitHub Issue
        alt severity == critical
            T  ->> GH : create fix/ci-<slug> branch
            T  ->> GH : open PR (head=fix/ci-*, base=main)
            T  ->> CP : @copilot diagnose and fix
            CP ->> GH : push commits to fix branch
            DEV ->> GH : review + approve PR
            GH ->> CI : merge fix/ci-* → main
        else severity == normal
            T  -->> DEV : issue opened, manual fix required
        end
    else Fix branch already active  (single-branch rule)
        T  ->> GH : create GitHub Issue (queued state)
        Note over T,GH : No new branch. Queue shown on dashboard.
    else Existing issue already open
        Note over T : Skip — no duplicate issue or branch
    end

    T   ->> DB : update PR Status Dashboard section
    WR  -->> T : release global lock

    CI  ->> WR : concludes: success (after fix)
    WR  ->> GH : auto-close matching ci-failure issues
    GH  ->> DB : post ✅ resolved section to dashboard
```

---

## 5. Dashboard Integration

Every outcome writes **one section** to the **📊 PR Status Dashboard** comment on the
active PR.  No additional standalone comments are posted.

| Outcome | Dashboard status | Dashboard summary example |
|---------|-----------------|--------------------------|
| Workflow passed (resolved) | ✅ success | `✅ \`CodeQL Analysis\` — passing on \`main\`` |
| Skip (existing issue) | ⚠️ warning | `🔴 \`CodeQL Analysis\` failed — existing tracker covers this` |
| Queued (branch active) | ⚠️ warning | `🔴 \`CodeQL Analysis\` failed — queued (single-branch rule active)` |
| Normal failure → new issue | ❌ failure | `🟡 \`Data Quality Suite\` failed — issue opened, manual fix required` |
| Critical → fix PR opened | ❌ failure | `🔴 CRITICAL \`Auth Tests\` failed — fix PR opened, @copilot assigned` |

---

## 6. Single-Branch Queue Visualisation

```mermaid
%%{init: {'accessibility': {'title': 'Timeline'}}%%
gantt
    title  Single-Branch Rule — Failure Queue Timeline
    dateFormat HH:mm
    axisFormat %H:%M

    section Active Fix
    fix/ci-auth-tests (PR #N)   : active, a1, 09:00, 60m

    section Queued Failures
    CodeQL fails → Issue #M     : crit, q1, 09:05, 55m
    Docker Build fails → Issue #P : crit, q2, 09:20, 40m

    section Resolution
    fix/ci-auth-tests merged    : milestone, m1, 10:00, 0m
    Queue processed (next triage) : q3, 10:00, 5m
```

> **Queue rule:** Issues `#M` and `#P` are opened immediately with a "QUEUED" note
> linking to the active fix branch. No second `fix/ci-*` branch is created until
> `fix/ci-auth-tests` merges and the system re-triages.

---

## 7. Job Dependency Graph

```mermaid
%%{init: {'accessibility': {'title': 'Flowchart showing triage\n🔒 holds global lock, create-issue\nall non-skip failures'}}%%
graph LR
    T[triage\n🔒 holds global lock]

    T --> CI[create-issue\nall non-skip failures]
    T --> CF[close-on-fix\nsuccess path only]

    CI --> FP[create-fix-pr\ncritical + new_issue only]

    CI  --> PD[post-dashboard]
    FP  --> PD
    T   --> PD
```

---

## 8. Configuration Reference

| Setting | Value | Purpose |
|---------|-------|---------|
| Concurrency group | `ci-failure-issue-creator-global-lock` | Serialises all invocations — race-free branch check |
| `cancel-in-progress` | `false` | Queues instead of dropping concurrent failures |
| Fix branch prefix | `fix/ci-<slug>-<timestamp>` | Enables L2 scan to detect any active fix branch |
| Critical label | `priority-critical` | Applied to issue + PR |
| Normal label | `priority-medium` + `needs-investigation` | Applied to issue |
| Issue marker | `<!-- CI_FAILURE_TRACKER:<slug> -->` | Enables L1 deduplication across re-runs |
| Auto-close trigger | `workflow_run.conclusion == 'success'` on `main` | Closes matching `ci-failure` issues |

---

## 9. Adding a New Monitored Workflow

To monitor an additional workflow, add its **exact `name:` field value** to the
`workflows:` list in `.github/workflows/ci-failure-issue-creator.yml`:

```yaml
on:
  workflow_run:
    workflows:
      - "My New Workflow"   # ← add here
    types: [completed]
    branches: [main]
```

---

## 10. Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Duplicate issues created | Race between two simultaneous failure events | Check concurrency group — must be `ci-failure-issue-creator-global-lock` with `cancel-in-progress: false` |
| Fix PR not created for critical failure | `action` resolved to `queue` (a `fix/ci-*` branch already exists) | Merge or delete the active fix branch first |
| Issue not auto-closed | Workflow name in `close-on-fix` slug doesn't match issue title | Check that the issue title contains the slugified workflow name |
| Dashboard not updated | No open PR found in `find-pr` step | Manually trigger with a `workflow_dispatch` and supply a `pr_number` |

---

> 🤖 _This document is maintained alongside `.github/workflows/ci-failure-issue-creator.yml`.  
> Update both when changing the process logic._

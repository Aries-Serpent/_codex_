# CI Rescue Pipeline — Golden Path Documentation

> **Status:** Canonical reference (S280, 2026-04-02)
> **Scope:** End-to-end lifecycle from workflow failure to Copilot fix — including Proactive CI Monitor and Fast-Forward Safe-File Promotion
> **Golden-path example:** PR [#3818](https://github.com/Aries-Serpent/_codex_/pull/3818) comment [#4158728043](https://github.com/Aries-Serpent/_codex_/pull/3818#issuecomment-4158728043)
> **S280 additions:** `proactive-ci-monitor.yml` (scheduled safety net), `fast-forward-safe-files.yml` (immediate main promotion), WEC FF checkbox gate

---

## Table of Contents

1. [Overview](#1-overview)
2. [Complete Pipeline Flowchart](#2-complete-pipeline-flowchart)
3. [Comment Channel Architecture](#3-comment-channel-architecture)
4. [Deduplication State Machine](#4-deduplication-state-machine)
5. [Sequence Diagram — Golden Path (2026-03-30)](#5-sequence-diagram--golden-path-2026-03-30)
6. [Rescue Comment Lifecycle](#6-rescue-comment-lifecycle)
7. [Workflow Dependency Graph](#7-workflow-dependency-graph)
8. [Anti-Pattern Map](#8-anti-pattern-map)
9. [Component Responsibility Matrix](#9-component-responsibility-matrix)
10. [Rules for Adding New Rescue Channels](#10-rules-for-adding-new-rescue-channels)

---

## 1. Overview

The CI Rescue pipeline converts any monitored workflow failure into a structured `@copilot` session automatically — no human intervention required. The pipeline consists of **five cooperating layers** (S280):

| Layer | System | Role |
|-------|--------|------|
| 1 | **`ci-rescue.yml` + `ci_rescue.py`** | Push-triggered: pattern analysis, structured RCA comment with `@copilot` mention |
| 2 | **Inline rescue jobs** in monitored workflows | Channel A fallback: generic fix-instructions comment on every failure |
| 3 | **`copilot-iterative-self-healing.yml`** | Push-triggered: escalation when patterns are exhausted; `cancel-in-progress: false` ensures no run is lost |
| 4 | **`proactive-ci-monitor.yml`** (S280 🆕) | **Scheduled safety net (every 30 min):** polls ALL open PRs for failures that slipped past layers 1–3; posts `@copilot` rescue for any gap. Also manually triggerable by maintainer from the GitHub Actions UI or via `gh workflow run` |
| 5 | **`copilot-agent-checkin.yml`** missed-trigger guard | Final guard: re-triggers Copilot if the session was silently dropped after a new push |

### Fast-Forward Safe-File Promotion (S280 🆕)

For files that **only take effect from `main`** (workflow schedules, `workflow_run` triggers, `workflow_dispatch` UI buttons), the pipeline now includes a promotion path that bypasses the full PR merge cycle:

| Trigger | System | Description |
|---------|--------|-------------|
| WEC checkbox `⚡ Fast-Forward Approved` | **`workflow-execution-gate.yml`** → `fast-forward-safe-files.yml` | Maintainer ticks checkbox in PR body → WEC gate parses it → FF workflow auto-fires |
| Manual | **`fast-forward-safe-files.yml`** | Direct trigger from GitHub Actions UI or `gh workflow run` |
| CLI | **`codex-skill ff --pr <N>`** | Copilot Agent or maintainer previews/applies from terminal |

Allowed file patterns are governed by `.codex/fast_forward_allowlist.yaml`.

---

## 2. Complete Pipeline Flowchart

```mermaid
flowchart TD
    A([Push to PR branch]) --> B[GitHub Actions triggers\nmonitored workflow]
    B --> C{Workflow\nresult?}
    C -->|success| Z([CI green — no rescue needed])
    C -->|failure| D

    D[Inline rescue job inside\nfailing workflow fires] --> E[POST or PATCH\nChannel A comment\ngeneric fix instructions]

    D --> F[workflow_run: completed\ntriggers ci-rescue.yml]

    F --> G[ci-rescue.yml\nRescue — analyse and post RCA]
    G --> H[Download ci_rescue.py\nfrom PR head SHA]
    H --> I[Fetch failed job logs\nvia GitHub API]
    I --> J[Match against\nci_failure_patterns.yaml]
    J --> K{Pattern\nmatched?}
    K -->|known pattern| L[Build structured RCA comment\nwith fix command + log snippet]
    K -->|unknown| M[Build generic escalation\nwith raw log excerpt]
    L --> N[Upsert SHA-scoped comment\nChannel B RCA\nat-copilot+claude-sonnet-4.6]
    M --> N

    D --> SH[copilot-iterative-self-healing.yml\ncancel-in-progress=false\nevery failure gets own run]
    SH --> SH2{Auto-fix\npatterns\nexhausted?}
    SH2 -->|no| SH3[Apply auto-fix pattern\npush fix commit]
    SH2 -->|yes| SH4[Escalation comment\nto @copilot]

    SCHED([⏱️ Scheduled every 30 min\nproactive-ci-monitor.yml\nS280 NEW]) --> PM[Poll ALL open PRs\nfor unaddressed failures]
    PM --> PM2{Failure found\nwith no rescue\ncomment yet?}
    PM2 -->|no| PM3([Nothing to do])
    PM2 -->|transient infra| PM4([Skip — auto-retry])
    PM2 -->|real failure| PM5[Classify with\npattern catalogue\nconfidence score]
    PM5 --> PM6{confidence ≥\nthreshold?}
    PM6 -->|no| PM7([Below threshold\nskip])
    PM6 -->|yes| PM8[POST @copilot rescue\ncomment to PR]

    N --> O{Copilot session\nstarted within\n45 min?}
    PM8 --> O
    SH4 --> O
    O -->|yes| P[Copilot Coding Agent\nreads RCA and applies fix]
    O -->|no / dropped| Q[copilot-agent-checkin.yml\nmissed-trigger guard fires]
    Q --> T[POST retrigger comment\nsession-done-retrigger]
    T --> P

    P --> U[Apply fix locally\nrun ruff + pytest]
    U --> V[commit + report_progress\npush to branch]
    V --> W[Reply to RCA comment:\nFixed in commit SHA]
    W --> X[New CI run\non fixed commit]
    X --> C

    subgraph FF ["⚡ Fast-Forward Safe Files (S280 NEW)"]
        FF1([WEC checkbox ticked\nOR manual trigger\nOR codex-skill ff]) --> FF2[workflow-execution-gate.yml\nparses FF section]
        FF2 --> FF3[fast-forward-safe-files.py\nclassifies files vs allowlist]
        FF3 --> FF4{Merge\nmode?}
        FF4 -->|create-pr| FF5[Open fast-forward PR\nstaging → main]
        FF4 -->|direct-push| FF6[Push files directly\nto main]
        FF5 --> FF7([Files take effect on main\nimmediately])
        FF6 --> FF7
    end
```

---

## 3. Comment Channel Architecture

```mermaid
graph LR
    subgraph "Channel A — Generic Fix Notice"
        A1[auto-fix-pr-check.yml\nrescue-comment job] --> A2[PATCH or POST\nci-rescue:NNN]
        A3[pre-merge-validation.yml\nrescue-comment job] --> A2
    end

    subgraph "Channel B — RCA Golden Path"
        B1[ci-rescue.yml\nworkflow_run trigger] --> B2[ci_rescue.py\npattern analysis engine]
        B2 --> B3[POST or PATCH\nci-rescue:NNN:sha12\nat-copilot+claude-sonnet-4.6]
    end

    subgraph "Missed-Trigger Guard"
        C1[copilot-agent-checkin.yml\npush trigger every commit] --> C2{Latest rescue comment\nhas at-copilot + age under 45 min?}
        C2 -->|yes| C3[Skip — RCA is live]
        C2 -->|no| C4[POST retrigger\nsession-done-retrigger]
    end

    A2 -.->|both markers detected by| C1
    B3 -.->|both markers detected by| C1

    style B3 fill:#d4edda,stroke:#28a745
    style C3 fill:#d4edda,stroke:#28a745
```

**Key insight:** Channel B (SHA-scoped RCA from `ci_rescue.py`) is the **golden path** because it:
- Contains a **pattern-matched root cause** with exact fix command
- Directly **invokes `@copilot+claude-sonnet-4.6`** to start a session immediately
- Uses **SHA-scoped dedup** so each commit gets exactly one RCA comment
- Accumulates failure updates for multiple workflows failing on the **same SHA**

---

## 4. Deduplication State Machine

```mermaid
stateDiagram-v2
    [*] --> NoRescue : branch has no open rescue comment

    NoRescue --> ChannelA_Open : Workflow fails\ninline rescue job posts Channel A

    NoRescue --> ChannelB_Open : Workflow fails\nci-rescue.yml fires\nci_rescue.py posts Channel B

    ChannelA_Open --> ChannelA_Appended : Same PR fails again\nPATCH to existing comment

    ChannelB_Open --> ChannelB_Appended : Same SHA fails again\ndifferent workflow\nPATCH to existing RCA

    ChannelB_Open --> SessionActive : at-copilot mention\nstarts Copilot session

    ChannelB_Appended --> SessionActive : at-copilot mention\nstarts Copilot session

    ChannelA_Open --> Retriggered : over 45 min, no Copilot reply\nmissed-trigger guard fires

    ChannelB_Open --> GracePeriod : Copilot not seen yet\nbut RCA under 45 min old\nmissed-trigger guard skips

    GracePeriod --> SessionActive : Copilot session starts\nwithin grace period

    GracePeriod --> Retriggered : over 45 min elapsed\nno Copilot action

    Retriggered --> SessionActive : Retrigger at-copilot\nstarts session

    SessionActive --> Resolved : Copilot replies\nFixed in SHA

    Resolved --> [*] : CI green on new commit
```

---

## 5. Sequence Diagram — Golden Path (2026-03-30)

This documents the **exact sequence** that produced the ideal rescue scenario — commit `1a9fcaab`, run [23772216208](https://github.com/Aries-Serpent/_codex_/actions/runs/23772216208), comment [#4158728043](https://github.com/Aries-Serpent/_codex_/pull/3818#issuecomment-4158728043):

```mermaid
sequenceDiagram
    autonumber
    actor Dev as Copilot Agent S243
    participant GH as GitHub Actions
    participant AutoFix as auto-fix-pr-check.yml
    participant Rescue as ci-rescue.yml
    participant Engine as ci_rescue.py
    participant PR as PR 3818 Comments
    participant Guard as copilot-agent-checkin.yml
    participant Agent as Copilot Coding Agent S244

    Dev->>GH: push f8718be9 S243 fixes P2A/P2B/P2C
    Note over GH: CI bot auto-commits follow:<br/>chore(auth) [skip ci]<br/>chore(d00) [skip ci]<br/>1a9fcaab (non-skip-ci fix)

    GH->>AutoFix: push 1a9fcaab triggers PR Auto-Fix Check run 23772216208

    AutoFix->>AutoFix: auto_fix_common_issues.py --check-only<br/>Pattern 22 detected<br/>CODEX_MANIFEST stale after bot commits

    AutoFix->>PR: PATCH Channel A comment<br/>ci-rescue:3818<br/>Append Failure Update

    AutoFix-->>AutoFix: exit 1 auto_fixable over 0

    GH->>Rescue: workflow_run completed failure<br/>PR Auto-Fix Check

    Rescue->>Rescue: Download ci_rescue.py from branch head SHA

    Rescue->>Engine: python3 ci_rescue.py --run-id 23772216208

    Engine->>GH: GET actions/runs/23772216208/jobs
    GH-->>Engine: Job logs failed job

    Engine->>Engine: Match logs against ci_failure_patterns.yaml<br/>RP-004 Pattern 22 matched<br/>CODEX_MANIFEST drift

    Engine->>PR: POST Channel B RCA comment 4158728043<br/>ci-rescue:3818:1a9fcaab5380<br/>at-copilot+claude-sonnet-4.6 please investigate

    Note over PR: Comment 4158728043 created<br/>THE GOLDEN PATH COMMENT

    PR->>Agent: at-copilot+claude-sonnet-4.6 mention<br/>triggers Copilot Coding Agent session

    Agent->>Agent: Load CODEBASE_AGENCY_POLICY.md<br/>Run sync_tracked_files.py --check

    Agent->>Agent: Fix RP-004 loop root cause<br/>Pattern 22 to soft_warning_patterns<br/>no longer blocks CI exit code

    Agent->>Agent: Harden missed-trigger guard<br/>rescueMarkerRe matches both channels<br/>45-min grace period for at-copilot RCA

    Agent->>Agent: Create docs/ci/CI_RESCUE_PIPELINE.md<br/>Create tests/ci/test_generate_coverage_map.py

    Agent->>Agent: sync_tracked_files.py --fix<br/>all 5 checks pass

    Agent->>GH: report_progress push S244 commit

    Agent->>PR: Reply to comment 4158728043<br/>Fixed in commit SHA

    GH->>AutoFix: New CI run on S244 commit<br/>Pattern 22 is warning only no exit 1

    Note over AutoFix: CI green no rescue needed
```

---

## 6. Rescue Comment Lifecycle

```mermaid
timeline
    title Single PR Rescue Comment Timeline PR 3818 commit 1a9fcaab

    section Before Rescue
        2026-03-30T22-52Z : S243 Copilot push f8718be9
                          : CI bot auto-commits skip ci
                          : 1a9fcaab pushed non-skip-ci

    section Auto-Fix Check Run 23772216208
        2026-03-30T23-11Z : auto-fix-pr-check.yml starts
        2026-03-30T23-14Z : Pattern 22 detected exit 1
                          : Channel A comment appended

    section CI Rescue
        2026-03-30T23-14Z : ci-rescue.yml triggered
        2026-03-30T23-15Z : ci_rescue.py RP-004 matched
                          : Channel B RCA posted comment 4158728043
                          : at-copilot+claude-sonnet-4.6 invoked

    section Copilot Session S244
        2026-03-30T23-22Z : S244 session starts
                          : RP-004 loop-break implemented
                          : Missed-trigger guard hardened
                          : Docs and tests created
                          : Fix pushed
```

---

## 7. Workflow Dependency Graph

```mermaid
graph TD
    subgraph "Monitored Workflows — trigger ci-rescue.yml"
        W1[PR Auto-Fix Check]
        W2[Pre-Merge Validation]
        W3[Validation Pipeline]
        W4[mypy Baseline]
        W5[Workflow Compliance Audit]
        W6[Iterative Self-Healing CI]
        W7[Test RAG Pipeline]
        W8[Resilient Validation Suite]
        W9[Security Scan]
        W10[Auto-Fix Common CI Issues]
    end

    subgraph "Rescue Infrastructure"
        R1[ci-rescue.yml\nworkflow_run trigger]
        R2[ci_rescue.py\npattern analysis engine]
        R3[ci_failure_patterns.yaml\npattern library]
    end

    subgraph "Comment System"
        C1[Channel A\nci-rescue:NNN\ngeneric fix notice]
        C2[Channel B RCA\nci-rescue:NNN:sha\nat-copilot mention GOLDEN PATH]
    end

    subgraph "Session Management"
        S1[copilot-agent-checkin.yml\nmissed-trigger guard]
        S2[Copilot Coding Agent\nsession]
    end

    W1 & W2 & W3 & W4 & W5 & W6 & W7 & W8 & W9 & W10 -->|failure| R1
    W1 & W2 & W3 & W4 & W5 & W6 & W7 & W8 -->|inline rescue job| C1
    R1 --> R2
    R2 --> R3
    R2 --> C2
    C1 -.->|detected by| S1
    C2 -.->|detected by| S1
    C2 -->|at-copilot mention| S2
    S1 -->|retrigger if dropped| S2
    S2 -->|push fix| W1

    style C2 fill:#d4edda,stroke:#28a745
    style S2 fill:#cce5ff,stroke:#004085
```

---

## 8. Anti-Pattern Map

### Anti-Pattern 1: RP-004 Infinite Loop (Fixed in S244)

```mermaid
graph LR
    subgraph "BEFORE fix — infinite loop"
        AP1[Bot auto-commit\nchore auth / chore d00] --> AP2[CODEX_MANIFEST\nhash drifts]
        AP2 --> AP3[Pattern 22 = hard ERROR\nin auto_fixable_patterns]
        AP3 --> AP4[CI fails exit 1]
        AP4 --> AP5[ci-rescue.yml fires\nRCA posted]
        AP5 --> AP6[Copilot session\nruns sync --fix]
        AP6 --> AP7[Fix commit pushed]
        AP7 --> AP1
    end

    subgraph "AFTER fix — loop broken"
        FX1[Bot auto-commit] --> FX2[CODEX_MANIFEST drifts]
        FX2 --> FX3[Pattern 22 = soft WARNING\nin soft_warning_patterns]
        FX3 --> FX4[CI reports warning\nno exit 1]
        FX4 --> FX5[No rescue comment\nno loop]
    end

    style AP1 fill:#ffcccc,stroke:#cc0000
    style AP4 fill:#ffcccc,stroke:#cc0000
    style AP5 fill:#ffcccc,stroke:#cc0000
    style AP7 fill:#ffcccc,stroke:#cc0000
    style FX4 fill:#d4edda,stroke:#28a745
    style FX5 fill:#d4edda,stroke:#28a745
```

### Anti-Pattern 2: Duplicate Retriggers (Fixed in S244)

```mermaid
graph LR
    subgraph "BEFORE fix — competing sessions"
        D1[RCA Channel B posted\nat-copilot+claude-sonnet] --> D2[Bot commit pushes\ntriggers checkin.yml]
        D2 --> D3[Guard sees open\nChannel A rescue\nno at-copilot check]
        D3 --> D4[Guard posts retrigger\nduplicate at-copilot\ncompeting sessions]
    end

    subgraph "AFTER fix — 45-min grace"
        G1[RCA Channel B posted\nat-copilot+claude-sonnet] --> G2[Bot commit pushes\ntriggers checkin.yml]
        G2 --> G3[Guard detects\nrcaHasCopilotCall\nage under 45 min]
        G3 --> G4[Guard skips\nRCA is still live\nno duplicate]
    end

    style D4 fill:#ffcccc,stroke:#cc0000
    style G4 fill:#d4edda,stroke:#28a745
```

---

## 9. Component Responsibility Matrix

| Component | Detects failure | Posts Channel A | Posts Channel B RCA | Deduplicates | Retriggers dropped sessions |
|-----------|:-:|:-:|:-:|:-:|:-:|
| Inline rescue jobs (auto-fix-pr-check, pre-merge-validation, etc.) | ✅ | ✅ | ❌ | ✅ PR-scoped PATCH | ❌ |
| `ci-rescue.yml` | ✅ workflow_run | ❌ | ✅ | ✅ SHA-scoped PATCH | ❌ |
| `ci_rescue.py` | ✅ log analysis | ❌ | ✅ | ✅ HTTP_STATUS delimiter | ❌ |
| `copilot-agent-checkin.yml` missed-trigger guard | ❌ | ❌ | ❌ | ✅ grace period | ✅ |
| `auto_fix_common_issues.py` | ✅ Pattern 22+ | ❌ | ❌ | N/A | ❌ |

### Marker Reference

| Marker | Channel | Scope | Who posts | Who reads |
|--------|---------|-------|-----------|-----------|
| `<!-- ci-rescue:{pr} -->` | A | PR | inline rescue jobs | checkin.yml guard |
| `<!-- ci-rescue:{pr}:{sha12} -->` | B | SHA | `ci_rescue.py` | checkin.yml guard |
| `<!-- session-done-retrigger -->` | Guard | PR | checkin.yml | checkin.yml dedup |
| `<!-- incomplete-session-retrigger -->` | Guard | PR | checkin.yml | checkin.yml dedup |
| `<!-- ci-rescue-rca:{sha12} -->` | B fallback | SHA | `ci-rescue.yml` inline fallback | checkin.yml guard |

---

## 10. Rules for Adding New Rescue Channels

```mermaid
flowchart LR
    A([New rescue channel needed]) --> B{Can ci_rescue.py\nhandle this pattern?}
    B -->|yes| C[Add pattern to\nci_failure_patterns.yaml\nfix_command + log_regexes]
    B -->|no| D[Create inline rescue job\nin the failing workflow]
    C --> E[ci-rescue.yml picks it up\nautomatically]
    D --> F[Use PR-scoped marker or\nSHA-scoped if per-commit context needed]
    E --> G[Update SKIP_BODY_MARKERS\nin check_pr_comments.py]
    F --> G
    G --> H[Add to monitoring list\nin ci-rescue.yml workflows:]
    H --> I([Done])
```

**Mandatory checklist for new rescue channels:**

1. ☐ **Unique parseable HTML marker** — use `<!-- ci-rescue-{source}:{pr}:{sha} -->` for new sources
2. ☐ **`@copilot+claude-sonnet-4.6`** in body — triggers session without human intervention
3. ☐ **Paginate comment search** (up to 50 pages) before creating to find existing marker
4. ☐ **Upsert semantics** — `PATCH` existing comment, `POST` only if not found
5. ☐ **Register pattern** in `.codex/patterns/ci_failure_patterns.yaml`
6. ☐ **Update `SKIP_BODY_MARKERS`** in `check_pr_comments.py` — prevent circular gate failure
7. ☐ **Update `rescueMarkerRe`** in `copilot-agent-checkin.yml` if marker format differs
8. ☐ **Add workflow** to monitored list in `ci-rescue.yml` `on.workflow_run.workflows:`

---

## Related Files

| File | Role |
|------|------|
| `.github/workflows/ci-rescue.yml` | Orchestrator — downloads engine, runs pattern analysis |
| `scripts/ci/ci_rescue.py` | Core engine — log analysis, SHA-scoped RCA posting |
| `.codex/patterns/ci_failure_patterns.yaml` | Known patterns: id, log_regexes, fix_command |
| `.github/workflows/copilot-agent-checkin.yml` | Missed-trigger guard (every push) |
| `.github/workflows/auto-fix-pr-check.yml` | Channel A: PR-scoped fix notice |
| `.github/workflows/pre-merge-validation.yml` | Channel A: pre-merge fix notice |
| `scripts/ci/auto_fix_common_issues.py` | Pattern detection + soft_warning_patterns Pattern 22 |
| `scripts/ci/sync_tracked_files.py` | Fixes RP-004: CODEX_MANIFEST/CHANGELOG sync |
| `scripts/ci/check_pr_comments.py` | SKIP_BODY_MARKERS prevents circular gate failures |
| `tests/ci/test_generate_coverage_map.py` | Unit tests for coverage map generation |

---

*Generated: S244 — 2026-03-30T23:22Z · Golden-path rescue: PR #3818 comment #4158728043*

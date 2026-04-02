# PR Lifecycle — 0D_base_ Branch

> **Version:** 1.6.0  
> **Date:** 2026-04-02 (S285 — §18 WEC Workflow Catalog, §19 Fast-Forward Promotion added; all WEC filename mismatches resolved; mermaid diagrams expanded)  
> **Branch:** `0D_base_`  
> **Sources:** `.github/workflows/` inspection (60 PR-triggered workflows), CI log history, issue #3853 triage report (59 failures / 14 workflows, 2026-04-02)

This document describes the full expected lifecycle of a pull request on the `0D_base_` branch:
which workflows run, when Copilot sessions are triggered, what failures are expected vs unexpected,
and how the self-healing / rescue system responds.

---

## Table of Contents

1. [High-Level Lifecycle Overview](#1-high-level-lifecycle-overview)
2. [Workflow Trigger Map](#2-workflow-trigger-map)
3. [Pre-Approval Workflows (no token delegation required)](#3-pre-approval-workflows)
4. [Post-Approval Workflows (require `COPILOT_AGENT_AUTH_ENABLED`)](#4-post-approval-workflows)
5. [Copilot Session Startup Triggers](#5-copilot-session-startup-triggers)
6. [Expected Failing Checks (and why they fail)](#6-expected-failing-checks)
7. [Rescue & Self-Healing Chain](#7-rescue--self-healing-chain)
8. [Mermaid Lifecycle Diagram](#8-mermaid-lifecycle-diagram)
9. [Rescue Flow Diagram](#9-rescue-flow-diagram)
10. [Historical CI Log Cross-Reference](#10-historical-ci-log-cross-reference)
11. [WEC Checkbox-Gated Workflow Approval](#11-wec-checkbox-gated-workflow-approval)
12. [PR State Machine — Draft, Pre-Check, Open, Ready](#12-pr-state-machine)
13. [High-Frequency Failure Catalogue (from triage #3853)](#13-high-frequency-failure-catalogue)
14. [Copilot Session Automation Improvement Roadmap](#14-copilot-session-automation-improvement-roadmap)
15. [RAG Module Tests — Chronic Failure Pattern](#15-rag-module-tests--chronic-failure-pattern)
16. [`@copilot` Comment Budget & Rate-Limit Controls](#16-copilot-comment-budget--rate-limit-controls)
17. [PDA Loop + AfterMath — Failure Pattern Logging](#17-pda-loop--aftermath--failure-pattern-logging)
18. [WEC Workflow Catalog — Complete Reference](#18-wec-workflow-catalog--complete-reference)
19. [Fast-Forward Workflow Promotion](#19-fast-forward-workflow-promotion)

---

## 1. High-Level Lifecycle Overview

```
Developer pushes commit to 0D_base_
         │
         ▼
┌────────────────────────────────┐
│  PHASE 1: Pre-Approval Checks  │  ← runs immediately on every push/PR
│  (no human approval required)  │
└────────────────────────────────┘
         │
         ▼ (all green OR rescue triggered)
┌────────────────────────────────┐
│  PHASE 2: Agent Token Gate     │  ← owner approves agent-auth-delegation
│  (owner approves once per PR)  │
└────────────────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│  PHASE 3: Post-Approval Runs   │  ← full test suites, Copilot sessions
│  (COPILOT_AGENT_AUTH_ENABLED)  │
└────────────────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│  PHASE 4: Merge Readiness      │  ← all required checks green, ready for merge
└────────────────────────────────┘
```

---

## 2. Workflow Trigger Map

There are **60 PR-triggered workflows** on `0D_base_`. The table below covers the most
significant ones. For the complete WEC-controlled catalog (all opt-in selectable workflows),
see [§18 WEC Workflow Catalog](#18-wec-workflow-catalog--complete-reference).

### 2.1 Always-Required Workflows (auto-run, never gated)

| Workflow | Trigger | WEC Role | Purpose |
|----------|---------|----------|---------|
| `pre-merge-validation.yml` | `pull_request`, `pull_request_review` | ✅ Always required | Ruff, line-length, auto-fix check gate |
| `comment-review-gate.yml` | `pull_request`, `pull_request_review`, `issue_comment` | ✅ Always required | Enforces §0 comment-reply policy |
| `deferral-language-gate.yml` | `pull_request` | ✅ Always required | Blocks forbidden deferral phrases |
| `agent-auth-delegation.yml` | `push`, `issue_comment`, `workflow_run` | ✅ Always required — owner approves | Delegates COPILOT_AGENT_AUTH_ENABLED token |
| `copilot-agent-checkin.yml` | `push` to `0D_base_` | ✅ Always required | S221 missed-trigger guard |
| `cost-gate.yml` | `workflow_call` | ✅ Always required | RED-tier cost governance gate |
| `copilot-agent-session-done.yml` | `workflow_run` | ✅ Always required | Session completion + S221 retrigger |
| `workflow-execution-gate.yml` | `workflow_dispatch`, `pull_request_review` | ✅ Always required | Parses WEC checklist + arms FF |
| `copilot-iterative-self-healing.yml` | `workflow_run`, `schedule`, `workflow_dispatch` | ✅ Always required | Self-healing escalation loop |

### 2.2 Validation & Testing Workflows (WEC opt-in)

| Workflow | Trigger | WEC Checkbox | Purpose |
|----------|---------|-------------|---------|
| `resilient_validation.yml` | `pull_request` | `resilient_validation.yml` | Full pytest suite (4 shards + integration + slow) |
| `nox_gates.yml` | `pull_request` | `nox_gates.yml` | Nox quality gates (ruff, mypy, coverage) |
| `validate.yml` | `pull_request`, `schedule` | `validate.yml` | Fast validation (ruff, detect-secrets, sync-tracked) |
| `mypy-baseline.yml` | `pull_request`, `push` | `mypy-baseline.yml` | Type-check anti-regression gate |
| `progressive-validation.yml` | `pull_request` | `progressive-validation.yml` | Progressive validation suite |
| `coverage-with-timeout.yml` | `pull_request` | `coverage-with-timeout.yml` | Coverage run with timeout guards |
| `test-rag.yml` | `pull_request` | `test-rag.yml` | RAG module tests |
| `pre-flight-validation.yml` | `pull_request`, `push` | `pre-flight-validation.yml` | Pre-flight CI validation |
| `ci-checkpoint-validation.yml` | `pull_request` | `ci-checkpoint-validation.yml` | CI checkpoint validation |
| `data-quality-suite.yml` | `pull_request` | `data-quality-suite.yml` | Data quality & determinism suite |

### 2.3 Security & Quality Workflows (WEC opt-in)

| Workflow | Trigger | WEC Checkbox | Purpose |
|----------|---------|-------------|---------|
| `security-scanning-suite.yml` | `pull_request` | `security-scanning-suite.yml` | Full security audit (bandit, pip-audit) |
| `codeql-analysis.yml` | `pull_request`, `push`, `schedule` | `codeql-analysis.yml` | CodeQL SAST analysis |
| `semgrep_sarif.yml` | `pull_request` | `semgrep_sarif.yml` | Semgrep SAST (SARIF upload) |
| `actionlint-audit.yml` | `pull_request`, `push` | `actionlint-audit.yml` | Workflow compliance audit (actionlint) |
| `auto-fix-common-issues.yml` | `pull_request`, `workflow_dispatch` | `auto-fix-common-issues.yml` | Auto-fix ruff/P22/P23 violations |
| `auto-fix-pr-check.yml` | `pull_request` | `auto-fix-pr-check.yml` | PR auto-fix check |
| `scan-secrets-variables.yml` | `pull_request` | `scan-secrets-variables.yml` | Secrets & variables scan |
| `code-quality-coverage-suite.yml` | `pull_request` | `code-quality-coverage-suite.yml` | Code quality & coverage suite |

### 2.4 Documentation Workflows (WEC opt-in)

| Workflow | Trigger | WEC Checkbox | Purpose |
|----------|---------|-------------|---------|
| `documentation-link-checker.yml` | `pull_request` | `documentation-link-checker.yml` | Broken link detection in docs/ |
| `pages-mkdocs.yml` | `pull_request`, `push` | `pages-mkdocs.yml` | MkDocs documentation build |
| `pages-pre-merge-validation.yml` | `pull_request` | `pages-pre-merge-validation.yml` | Pages pre-merge validation |

### 2.5 Automation & Agent Workflows (WEC opt-in)

| Workflow | Trigger | WEC Checkbox | Purpose |
|----------|---------|-------------|---------|
| `qa-walkthrough.yml` | `pull_request`, `workflow_dispatch` | `qa-walkthrough.yml` | QA walkthrough agent |
| `dependency-submission.yml` | `pull_request` | `dependency-submission.yml` | Resilient dependency submission |
| `reference-integrity.yml` | `pull_request`, `push` | `reference-integrity.yml` | Reference integrity + agent size gate |
| `root-org-validation.yml` | `pull_request`, `workflow_dispatch` | `root-org-validation.yml` | Root organization validation |
| `rust_swarm_ci.yml` | `pull_request`, `push` | `rust_swarm_ci.yml` | Rust-Python hybrid swarm CI/CD |
| `fast-forward-safe-files.yml` | `workflow_dispatch` | ⚡ FF checkbox (separate section) | Fast-forward safe files to `main` |

### 2.6 Auto-Triggered (not WEC-selectable)

These workflows run automatically on PR events and are not individually controlled via the WEC:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `ci-rescue.yml` | `workflow_run` (on failure) | RCA comment posting |
| `iterative-self-healing-ci.yml` | `workflow_run` | Auto-fix + PDA Loop logging |
| `copilot-pr-session-injector.yml` | `pull_request` | Session context injection |
| `copilot-session-chain.yml` | `issue_comment`, `workflow_dispatch` | Session sequencing |
| `pr-cost-check.yml` | `pull_request` | PR cost estimate comment |
| `pr-followup-generator.yml` | `pull_request` | Follow-up prompt generation |
| `pr-size-analyzer.yml` | `pull_request` | PR diff size analysis |
| `labeler.yml` | `pull_request` | Label assignment |
| `comment-review-gate.yml` | `issue_comment` (self-retrigger guard) | Gate re-scan on new comments |

---

## 3. Pre-Approval Workflows

These run **immediately** on every push or PR event, without any human approval:

### 3.1 `validate.yml` — Validation Pipeline (Fast Validation)

**Trigger:** `pull_request` (opened, synchronize, reopened)  
**Checks:**
- `pre-commit` hooks: end-of-file-fixer, detect-secrets, sync-tracked-files
- `ruff check` (import hygiene, linting)
- `python3 scripts/ci/sync_tracked_files.py --check` (P22 tracked-file drift)

**Expected to pass:** Always. Failures indicate import hygiene issues, secrets drift, or untracked file hash changes.

### 3.2 `mypy-baseline.yml` — mypy Anti-Regression Gate

**Trigger:** `pull_request` + `push`  
**Checks:**
- Runs `python scripts/ci/mypy_baseline.py --require-baseline`
- Compares current `src/` mypy error count against `.mypy_baseline`
- **FAILS** if `current_errors > baseline`

**Expected to pass:** Always. The baseline is set to the CI-environment count (isolated venv: `mypy>=1.8.0, types-PyYAML, types-requests` only).

> ⚠️ **Note on environment parity:** The CI venv does NOT install the full project. This means
> `# type: ignore` annotations that suppress errors from installed packages (pydantic, PyJWT,
> cryptography, etc.) appear as "unused" in CI. The `.mypy_baseline` MUST be set using the
> CI-isolated venv, not the local fully-installed environment.

### 3.3 `resilient_validation.yml` — Resilient Validation Suite

**Trigger:** `pull_request`  
**Checks:**
- 4 test shards: `pytest tests/ -m 'not slow and not integration'`
- Integration shard: `pytest tests/ -m integration`
- Slow shard: `pytest tests/ -m slow`

**Expected failures:** None after CI rescue. The import collection must succeed.
Known failure mode: `ModuleNotFoundError` during pytest collection (e.g., broken `__init__.py` imports — see P19-BATCH-WATCH-001).

---

## 4. Post-Approval Workflows

### 4.1 `agent-auth-delegation.yml` — Agent Token Delegation

**Trigger:** `push` to `0D_base_`, `issue_comment` containing `@copilot`, `workflow_run`  
**Gate:** **Owner must approve** in the GitHub Actions UI.

Once approved, this workflow:
1. Sets `COPILOT_AGENT_AUTH_ENABLED = true`
2. Sets `COGNITIVE_BRAIN_ALLOWED_ACTORS` repo variable
3. Posts `@copilot continue` comment to trigger next Copilot session

**Who can be delegated:** `copilot-swe-agent[bot]`, `github-copilot[bot]`, `github-actions[bot]`

---

## 5. Copilot Session Startup Triggers

Copilot sessions start when **any** of the following conditions are met:

| Trigger | Workflow | Comment Prefix |
|---------|----------|---------------|
| `@copilot <task>` in PR comment | `copilot-pr-session-injector.yml` | Immediate |
| `agent-auth-delegation.yml` completes | Posts `@copilot continue` | Post-approval |
| CI failure detected (rescue) | `ci-rescue.yml` → posts `@copilot Fix ...` | On failure |
| Missed-trigger guard fires | `copilot-agent-checkin.yml` → posts re-trigger | On push, if unanswered rescue |
| `copilot-session-chain.yml` dispatch | `workflow_dispatch` | Manual |

### Session Completion Protocol

When a Copilot session completes, `copilot-agent-session-done.yml` fires and:
1. Updates session metadata
2. Checks for outstanding rescue comments
3. If outstanding: posts a missed-trigger re-trigger (S221 guard)

The **S221 guard** (`copilot-agent-checkin.yml`) fires on every push to `0D_base_` and checks:
- Are there any unresolved rescue comments with no `@copilot` response?
- If yes: posts a re-trigger comment (rescue ID + SHA)

**To satisfy the S221 guard permanently for a rescue ID:** reply with `"Resolved at <SHA>"`,
`"Fixed at <SHA>"`, or `"Addressed at <SHA>"` in a `@copilot` comment after the rescue.

---

## 6. Expected Failing Checks

### 6.1 Checks That Are ALWAYS Expected to Pass

| Check | Why it must pass |
|-------|-----------------|
| `validate.yml / Fast Validation` | Import hygiene, no secrets drift |
| `mypy-baseline.yml / mypy Anti-Regression` | No new type errors introduced |
| `resilient_validation.yml` (all shards) | No test collection errors, no regressions |

### 6.2 Checks That May Show `action_required`

| Check | Expected Behavior |
|-------|------------------|
| `agent-auth-delegation.yml` | Shows `waiting for approval` until owner approves |
| Any environment-gated workflow | `action_required` = NOT a code failure — it's repo protection |

> From S242: `action_required` on ALL workflows for `0D_base_` is a **pre-existing repo
> environment protection** requiring human approval. This is NOT a code failure.

### 6.3 Known Flaky / Transient Failures

| Pattern | Root Cause | Action |
|---------|-----------|--------|
| `##[error]The runner has received a shutdown signal` | Transient GH runner infrastructure | Retry — no code fix needed |
| `ModuleNotFoundError: No module named 'services.crawler.X'` | P19 batch stripped try/except (P19-BATCH-WATCH-001) | Fix relative imports |
| `mypy regression: N errors > baseline B` | Baseline set with wrong environment | Re-run `mypy_baseline.py --update` in isolated venv |

---

## 7. Rescue & Self-Healing Chain

When a check fails, the following cascade fires:

```
1. CHECK FAILS (e.g., mypy-baseline.yml)
         │
         ▼
2. ci-rescue.yml fires (triggered by workflow_run)
   - Performs root-cause analysis (matches RP-XXX patterns)
   - Posts 🚨 CI Rescue comment to PR with:
       • rescue ID (commit SHA)
       • failure pattern (RP-009, etc.)
       • fix instructions
         │
         ▼
3. mypy-baseline.yml → rescue-comment job fires
   - Posts secondary "fix required" comment
         │
         ▼
4. Copilot session triggered (by @copilot in rescue comment)
   - Agent investigates logs (GitHub MCP tools)
   - Agent applies fix
   - Agent pushes commit
         │
         ▼
5. copilot-agent-session-done.yml fires
   - Checks if rescue was answered
   - If YES: marks rescue as resolved
   - If NO: S221 guard fires on next push
         │
         ▼
6. S221 Guard (copilot-agent-checkin.yml)
   - Fires on every push to 0D_base_
   - Scans for unanswered rescue comments
   - Posts re-trigger if rescue ID has no @copilot response containing
     "fixed at / resolved at / addressed at <SHA>"
```

### Rescue Patterns (RP-XXX)

| Pattern | Failure Type | Fix |
|---------|-------------|-----|
| `RP-009` | mypy anti-regression gate exceeded baseline | Fix type errors or update baseline |
| `RP-019` | `from src.` import regression | Run P19-BATCH-001; verify P19-BATCH-WATCH-001 |
| (transient) | Runner shutdown | Retry — no code fix |

---

## 8. Mermaid Lifecycle Diagram

```mermaid
flowchart TD
    A[Developer pushes commit] --> B{PR Exists?}
    B -->|No| C[Open PR]
    B -->|Yes| D[Sync push to existing PR]
    C --> PRE
    D --> PRE

    subgraph PRE ["Phase 0 — Always-Required (every push, no gate)"]
        direction LR
        PRE1[pre-merge-validation.yml]
        PRE2[comment-review-gate.yml]
        PRE3[deferral-language-gate.yml]
        PRE4[copilot-agent-checkin.yml\n S221 guard]
    end

    PRE --> E
    subgraph PHASE1 ["Phase 1 — Pre-Approval Checks"]
        E[validate.yml / Fast Validation] --> F{Pass?}
        G[mypy-baseline.yml] --> H{Pass?}
        I[resilient_validation.yml shards ×6] --> J{Pass?}
    end

    F -->|Fail| K[ci-rescue.yml posts 🚨 rescue comment\n+ PDA Loop log-failure]
    H -->|Fail| K
    J -->|Fail| K
    K --> L[@copilot Fix Required comment]
    L --> M[Copilot session starts]
    M --> N[Agent fixes code + pushes\n+ replies to blocking comments]
    N --> A

    F -->|Pass| WEC
    H -->|Pass| WEC
    J -->|Pass| WEC

    subgraph WEC ["Phase 2 — WEC Gate: Opt-In Workflow Selection"]
        direction TB
        WEC1["Owner/agent checks WEC items\n(resilient_validation · nox_gates\nmypy-baseline · codeql · security\ndocs-build · qa-walkthrough …)"]
        WEC2[workflow-execution-gate.yml\nparses PR body checklist]
        WEC1 --> WEC2
        WEC2 --> WEC3{FF checkbox\nticked?}
        WEC3 -->|Yes| FF["⚡ fast-forward-safe-files.yml\nPromotes safe files to main"]
        WEC3 -->|No| SKIP_FF[FF job skipped]
    end

    WEC2 --> O
    subgraph PHASE2 ["Phase 3 — Token Delegation Gate"]
        O[agent-auth-delegation.yml] --> P{Owner\nApproves?}
    end

    P -->|Pending| Q[action_required status\n— NOT a code failure]
    P -->|Approved| R[COPILOT_AGENT_AUTH_ENABLED = true]
    R --> S[@copilot continue posted]
    S --> T[Copilot session — next phase tasks]

    subgraph PHASE3 ["Phase 4 — Post-Approval Agent Sessions"]
        T --> U[Agent completes tasks\n• update CHANGELOG\n• update accountability report\n• reply to ALL blocking comments]
        U --> V[copilot-agent-session-done.yml\n• verify rescues answered\n• S221 guard on next push]
    end

    V --> W{Rescue\nanswered?}
    W -->|No| X[S221 guard fires\non next push]
    X --> L
    W -->|Yes| Y[Ready for Review\n🟢 all checks green]
    Y --> Z[Owner approves + Merge]

    style FF fill:#d4edda,stroke:#28a745
    style Q fill:#fff3cd,stroke:#856404
    style K fill:#f8d7da,stroke:#721c24
```

---

## 9. Rescue Flow Diagram

```mermaid
sequenceDiagram
    participant Dev as Developer / Copilot
    participant CI as GitHub Actions CI
    participant Healer as iterative-self-healing-ci.yml
    participant PDA as pda_failure_logger.py
    participant Rescue as ci-rescue.yml
    participant Checkin as copilot-agent-checkin.yml (S221)
    participant Copilot as @copilot Agent
    participant PR as Pull Request Comments

    Dev->>CI: push commit to 0D_base_
    CI->>CI: Check fails (e.g., mypy-baseline)
    CI->>Healer: workflow_run: completed (conclusion=failure)

    Healer->>Healer: classify logs → RP-XXX pattern
    Healer->>PDA: log-failure (pattern_id, root_cause, fix_template)
    PDA-->>Healer: logged to pda_iterations.jsonl

    alt auto-fixable pattern
        Healer->>CI: apply fix, commit, verify (max 3 iterations)
        Healer->>PDA: log-fix (verification_passed=true/false)
    else not auto-fixable
        Healer->>Rescue: triggers ci-rescue.yml
        Rescue->>PR: UPSERT 🚨 CI Rescue comment<br/><!-- ci-rescue:PR:sha-XXXXX --><br/>(pattern ID + fix commands + @copilot)
    end

    PR->>Copilot: @copilot mentioned → session starts
    Copilot->>CI: Fetches logs via GitHub MCP tools
    Copilot->>PDA: summarize (query grounded solutions)
    PDA-->>Copilot: proven fix_template + verification_cmd
    Copilot->>Copilot: Diagnoses root cause, applies fix
    Copilot->>CI: Push fix commit + reply to BLOCKING comments
    Copilot->>PR: Posts "Fixed at <SHA>" reply

    CI->>CI: Re-runs checks on fix commit
    CI->>Copilot: copilot-agent-session-done.yml fires
    Copilot->>PDA: log-session (patterns_fixed, lessons)

    Note over Checkin: On EVERY push to 0D_base_
    Checkin->>PR: Scans for unanswered rescue comments
    alt Rescue has @copilot "fixed at / resolved at / addressed at" reply
        Checkin->>Checkin: S221 guard suppressed — no re-trigger
    else No @copilot reply (rate-cap: ≥3 retriggers → stop)
        Checkin->>PR: Posts S221 missed-trigger re-trigger
        PR->>Copilot: @copilot session re-triggered
    end
```

---

## 10. Historical CI Log Cross-Reference

The following CI runs on this PR are referenced throughout this document and in session notes:

| Run ID | Workflow | Commit | Result | Root Cause | Fixed By |
|--------|----------|--------|--------|-----------|---------|
| [23689574622](https://github.com/Aries-Serpent/_codex_/actions/runs/23689574622) | mypy Baseline Gate | `77d4ec89` | ❌ FAIL (345 > 333) | S137 P19 batch broke `crawler/__init__.py` try/except | S139 `a12f5e2` |
| [23689574640](https://github.com/Aries-Serpent/_codex_/actions/runs/23689574640) | Agent Auth Delegation | `77d4ec89` | ❌ FAIL | Auth delegation pending approval | Human approval |
| [23689574652](https://github.com/Aries-Serpent/_codex_/actions/runs/23689574652) | Validation Pipeline | `77d4ec89` | ❌ FAIL | Same crawler import error (collection failure) | S139 `a12f5e2` |
| [23689574653](https://github.com/Aries-Serpent/_codex_/actions/runs/23689574653) | Resilient Validation Suite | `77d4ec89` | ❌ FAIL (7 jobs) | Same crawler import error | S139 `a12f5e2` |
| [23691793298](https://github.com/Aries-Serpent/_codex_/actions/runs/23691793298) | Agent Auth Delegation | — | ✅ PASS | Owner approved token delegation | N/A |
| [23691951388](https://github.com/Aries-Serpent/_codex_/actions/runs/23691951388) | mypy Baseline Gate | `2293b9af` | ❌ FAIL (342 > 306) | Baseline incorrectly lowered to 306 (local env), CI env sees 342 | S141 this PR |
| [23691951400](https://github.com/Aries-Serpent/_codex_/actions/runs/23691951400) | Validation Pipeline | `2293b9af` | ❌ FAIL | Same baseline mismatch | S141 this PR |
| [23691951433](https://github.com/Aries-Serpent/_codex_/actions/runs/23691951433) | Resilient Validation Suite | `2293b9af` | ❌ FAIL | Same baseline mismatch | S141 this PR |
| [23692231532](https://github.com/Aries-Serpent/_codex_/actions/runs/23692231532) | mypy Baseline Gate | `a12f5e29` | ❌ FAIL (342 > 306) | Baseline still at 306; P19 src-import changes added 9 new CI errors | S141 this PR |
| [23692231503](https://github.com/Aries-Serpent/_codex_/actions/runs/23692231503) | Validation Pipeline | `a12f5e29` | ❌ FAIL | Same baseline issue | S141 this PR |
| [23692231510](https://github.com/Aries-Serpent/_codex_/actions/runs/23692231510) | Resilient Validation Suite (slow) | `a12f5e29` | ❌ FAIL | Same baseline issue | S141 this PR |

### Root Cause Analysis: mypy Baseline Mismatch (S139→S141)

The S139 session correctly fixed the `crawler/__init__.py` import regression (which caused
7 CI jobs to fail with `ModuleNotFoundError`). However, it then updated `.mypy_baseline` to
`306` using the **local fully-installed environment** rather than the **CI isolated venv**.

- Local env (all packages installed): mypy reports **306** errors
- CI isolated venv (only `mypy>=1.8.0, types-PyYAML, types-requests`): mypy reports **333** errors

The **27-error gap** between CI and local is caused by `warn_unused_ignores = True` in `mypy.ini`:
- With packages installed locally, `# type: ignore` annotations suppress real type errors → no
  `unused-ignore` warning
- In CI without packages, imports are silently ignored → `# type: ignore` is redundant →
  `unused-ignore` warning (+27 errors)

S141 additionally fixed 9 errors introduced by the P19 src-import backfill:

| File | Error | Root Cause | Fix Applied |
|------|-------|-----------|-------------|
| `src/codex/zendesk/agent.py` | `Module "tools" has no attribute "ToolRegistry"` | Root `./tools/__init__.py` shadows `src/tools/` | Reverted to `from src.tools import` |
| `src/codex_ml/tokenization/train_tokenizer.py` | `Variable "..." not valid as type` | Module attribute alias not recognized as type | Explicit `from tokenization.train_tokenizer import TrainTokenizerConfig as TrainTokenizerConfig` |
| `src/codex/zendesk/monitoring/mcp_bridge.py` | Unused `# type: ignore[arg-type]` (×4) | `mcp.*` now resolvable; `set_gauge(float)` is correct | Removed redundant `# type: ignore` |
| `src/mcp/server/jsonrpc_adapter.py` | Unused `# type: ignore[return-value]` | `BackendAdapter` now resolvable, no return mismatch | Removed redundant `# type: ignore` |

Baseline was then reset to **333** using the CI isolated venv to ensure parity.

---

## Appendix: Key Patterns

| Pattern ID | Description | Reference |
|-----------|-------------|-----------|
| P19-BATCH-001 | After stripping `src.` prefix, run `ruff check --fix` for import sort (I001) | S137 |
| P19-BATCH-WATCH-001 | Never strip `src.` from `try/except ImportError` blocks without verifying branches remain different; use relative imports instead | S139 |
| P19-SHADOW-EXPANDED-001 | Root-level `__init__.py` shadows (training, utils, models, services, etc.) must retain `from src.X` imports. Always check `ls <pkg>/__init__.py` at REPO_ROOT before de-src-ifying | S144 |
| P19-SHADOW-REVERT-001 | When a de-src-ified import silently resolves to the wrong root-level shadow, revert to `from src.X` form. The shadow intercepts before `sys.path` src/ entry is reached | S145 |
| P21 | GitHub Actions Node.js 20 version deadline: 2026-06-02 | S135-S136 |
| P22 | Tracked file sync drift: run `sync_tracked_files.py --fix` when `CODEX_MANIFEST.json` changes | S138 |
| P23 | `detect-secrets` baseline plugin mismatch: `.secrets.baseline` generated with newer detect-secrets version causes `TypeError: No such <plugin>` in CI. Fix: `python scripts/ci/auto_fix_common_issues.py --pattern 23` | S145 |
| SECRET-PRAGMA-001 | `# pragma: allowlist secret` for detect-secrets false positives (demo keys, dev placeholders, pattern variables). Run `python3 -m detect_secrets scan <file>` to verify suppression | S143 |
| FP-ACTOR-SKIP-001 | S221 missed-trigger AND incomplete-session guards must skip when `context.actor ∈ {copilot-swe-agent[bot], github-copilot[bot], copilot[bot]}` | S144 |
| FP-PREAPPROVAL-001 | All bot-posted `@copilot` comments embed pre-authorization notice to prevent duplicate approval gates | S144 |
| FP-SAFETYCAP-001 | S221 guard safety cap ≥3 retriggers per rescue ID prevents infinite loops | S144 |
| §ARLOOP | When a rescue is already addressed, reply `"Resolved at <SHA>"` to suppress S221 re-triggers | S242-S243 |
| `RP-009` | mypy anti-regression gate exceeded baseline (too many errors) | ci-rescue.yml |
| `GH013` | Branch ruleset violation: Copilot agent token lacks bypass → owner must add agent to bypass list | S244 |

---

## Appendix: Known Recurring CI Failure Patterns (from issue #3737)

These patterns appear repeatedly in CI triage reports. Each has a documented fix path:

| Workflow | Failure Step | Pattern | Fix |
|----------|-------------|---------|-----|
| Validation Pipeline / Fast Validation | `detect-secrets` hook `TypeError: No such GitLabTokenDetector` | P23 (plugin mismatch) | `python scripts/ci/auto_fix_common_issues.py --pattern 23` |
| Validation Pipeline / Fast Validation | `sync-tracked-files: files were modified by hook` | P22 (tracked file drift) | `python scripts/ci/sync_tracked_files.py --fix && git add -A && git commit` |
| agent-auth-delegation / Cognitive Pre-flight | `Verify CHANGELOG.md updated in last commit` | CHANGELOG gate | Add `### Fixed (SN)` entry to `## [Unreleased]` in `CHANGELOG.md` before committing |
| mypy Baseline Gate | `Fail if regression detected` | `.mypy_baseline` stale | Update with CI isolated-venv per P19-ENV-001 |
| Resilient Validation Suite / Sharded tests | `startup_failure` (no error log) | Pre-existing infra | Runner never starts for Data Quality/Progressive Validation/Rust-Python — not a code failure |
| Agent Token Delegation | `action_required` on all checks | `agent-auth-delegation` environment gate | Owner clicks "Approve" at the Actions URL — needed once per approval cycle |
| Copilot Issue Triage | `Analyze issue with GitHub Copilot` fails | API/CLI invocation error | Infrastructure issue — not code-fixable; retries usually succeed |
| Embedding Index Rebuild | `Commit updated index metadata` | Push permissions | `CODEX_MASTER_KEY` needed for push; falls back to `CODEX_BACKUP_KEY` |

```mermaid
flowchart TD
    PUSH["git push to 0D_base_"] --> VAL["Validation Pipeline\n(validate.yml)"]
    VAL --> DS["detect-secrets hook"]
    VAL --> SYNC["sync-tracked-files hook"]
    VAL --> RUFF["ruff + cross-refs"]
    DS -- "plugin mismatch" --> P23["Pattern 23 fix:\nauto_fix --pattern 23"]
    DS -- "false positive" --> PRAGMA["Add # pragma: allowlist secret"]
    SYNC -- "files modified by hook" --> SYNCFIX["run sync_tracked_files.py --fix\nthen commit"]
    RUFF -- "violations" --> P1["Pattern 1/9/12 fix:\nauto_fix --pattern 1"]
    P23 --> CLEAN["✅ CI passes"]
    PRAGMA --> CLEAN
    SYNCFIX --> CLEAN
    P1 --> CLEAN
```

---

## 11. WEC Checkbox-Gated Workflow Approval

The **Workflow Execution Checklist (WEC)** is a markdown checklist embedded in every PR body.
It controls which GitHub Actions workflows are permitted to run via the `workflow-execution-gate.yml`
gate. This section explains how the gate works, how it differs from GitHub's native required-checks
system, and what the pre-approval phase looks like.

### 11.1 What is the WEC?

The WEC block lives at the bottom of every PR description:

```markdown
## 🔄 Workflow Execution Checklist

### ✅ Validation & Testing
- [x] pre-merge-validation.yml — Pre-merge checks (always required)
- [ ] resilient_validation.yml — Resilient validation
- [ ] mypy-baseline.yml — Type-check anti-regression
```

> ⚠️ **Filename accuracy is mandatory.** The WEC gate parses `\S+\.yml` tokens.
> `resilient-validation-suite.yml` will NOT match `resilient_validation.yml` —
> use the **exact** filename (underscores not hyphens where the file uses underscores).
> See [§18](#18-wec-workflow-catalog--complete-reference) for the authoritative filename list.

- **`[x]` (checked)** = workflow is APPROVED to run
- **`[ ]` (unchecked)** = workflow is NOT YET approved; gate returns `skip` when the workflow checks in
- **`always required`** items must be `[x]` in every PR body update; the HARDENED AGENT INSTRUCTION enforces this

The `workflow-execution-gate.yml` workflow parses this checklist on every `pull_request_review`
approval or `workflow_dispatch`. Workflows that implement the WEC gate-check step exit early
(`skip=true`) when their checkbox is unchecked.

### 11.2 Pre-Approval Phase (no workflows checked yet)

When a PR is first opened and no workflows have been checked in the WEC, the PR is in
**pre-approval pre-check status**. In this phase:

| Category | Behaviour |
|----------|-----------|
| **Always-required workflows** | Run automatically (pre-merge-validation, comment-review-gate, deferral-language-gate, agent-auth-delegation, copilot-agent-checkin, cost-gate, copilot-agent-session-done, workflow-execution-gate, copilot-iterative-self-healing) |
| **Gated opt-in workflows** | Do NOT run — the gate returns `skip` |
| **GitHub-managed workflows** | Run regardless of WEC (e.g. `Automatic Dependency Submission (Python)`) |

#### Pre-approval requirements

The following checks MUST be green before any WEC items are approved:

| Workflow / Job | Why it must pass unconditionally |
|----------------|----------------------------------|
| `Automatic Dependency Submission (Python)` ← `dynamic / submit-pypi` | GitHub-managed supply-chain check. Transient API failure (HTTP 503) is the only acceptable reason for a red; re-run resolves it. |
| `Resilient Dependency Submission` (`dependency-submission.yml`) | Our retry-wrapped replacement. Must pass with all green. |
| `Validation Pipeline / Fast Validation` (`validate.yml`) | detect-secrets, ruff, sync-tracked-files. All must pass. |
| `mypy Baseline Gate` (`mypy-baseline.yml`) | No new type errors vs baseline. Must pass. |
| `deferral-language-gate.yml` | No forbidden deferral phrases in changed files. Must pass. |
| `pre-merge-validation.yml` | Ruff, line-length, auto-fix check. Must pass. |

> ⚠️ **Important:** `dynamic / submit-pypi (dynamic)` is GitHub's own automatic dependency
> graph workflow. It runs unconditionally on every push and pull_request event to `0D_base_`.
> If it fails, self-healing MUST be triggered immediately (see [§11.5](#115-self-healing-for-pre-approval-failures)).

### 11.3 Approving Workflows (checking the WEC)

To approve a workflow, the PR author or a Copilot agent **checks its checkbox** in the PR body
and pushes an update. The `workflow-execution-gate.yml` gate re-parses the checklist on the next
push and enables the newly approved workflow.

**Typical approval sequence:**

```
1. Open PR (pre-approval — only always-required workflows run)
         ↓
2. Pre-approval checks green → check resilient_validation.yml, mypy-baseline.yml,
   security-scanning-suite.yml in WEC (use exact filenames — see §18)
         ↓
3. Push PR body update → workflow-execution-gate re-parses → approved workflows now run
         ↓
4. All approved workflows green → owner approves agent-auth-delegation
         ↓
5. Copilot sessions start → code changes → repeat from step 1 for new checks
```

> ⚠️ **HARDENED AGENT RULE:** Once an item is checked `[x]`, it MUST NEVER be unchecked
> by a subsequent PR body update. The Copilot agent reads the CURRENT PR body and copies
> all `[x]` items verbatim into the updated body. Only newly-added items may be set to `[ ]`.

### 11.4 Draft vs Open vs Ready-to-Review PR States

| State | GitHub Label | WEC Gate | Copilot Sessions | Required Checks |
|-------|-------------|----------|-----------------|----------------|
| **Draft** | `[Draft]` badge | Pre-approval phase | Not started | Only always-required run |
| **Open (pre-check)** | No badge; `Open` | Pre-approval until WEC items checked | Not started | Always-required + GitHub-managed |
| **Open (WEC approved)** | `Open` | Specific workflows approved via WEC | Active after agent-auth | All approved workflows + required |
| **Open (FF approved)** | `Open` | ⚡ FF checkbox ticked + WEC items checked | Active | FF job fires; files promoted to main |
| **Ready to review** | `[Open]` (after clicking "Ready for review") | All WEC workflows may run | Post-approval active | Full suite |

**Key difference between Draft and Open:**

- **Draft PR**: GitHub suppresses required-check enforcement. Auto-merge is not available.
  CI still runs, but PRs cannot be merged in draft state.
- **Open PR (pre-approval)**: Required checks are enforced. The WEC gate has not yet approved
  any gated workflows. The `agent-auth-delegation` environment protection still shows
  `action_required` (waiting for owner approval).
- **Open PR (WEC approved)**: Gated workflows are enabled by the WEC. Agent token delegation
  may be active. Copilot sessions are running.
- **Ready to review** (flipping from Draft to Open): This is the UI toggle that changes
  the PR from Draft to Open state. In this codebase, PRs are usually opened directly as
  non-draft so this transition is rare. When it does occur, CI re-evaluates all required checks.

### 11.5 Self-Healing for Pre-Approval Failures

Any failure during the pre-approval phase (including `dynamic / submit-pypi`) triggers the
self-healing cascade:

```
1. Workflow fails (any name, including GitHub-managed)
         ↓
2. iterative-self-healing-ci.yml fires (workflows: ["*"], cancel-in-progress: false)
   → classifies failure → attempts auto-fix (1-3 iterations)
         ↓ (if not auto-fixable)
3. copilot-iterative-self-healing.yml fires (extended watch list)
   → posts @copilot escalation comment on PR, SHA-scoped upsert marker
         ↓ (subsequent failures on same SHA)
4. Additional failures UPSERT to the SAME comment (same SHA marker) rather than
   creating new comments — prevents comment flooding
         ↓
5. ci-rescue.yml fires for watched workflows
   → posts structured RCA comment with fix commands
         ↓
6. Copilot coding agent session starts → diagnoses → fixes → pushes
```

**The upsert marker** ensures one canonical escalation comment per commit SHA per category.
Format: `<!-- copilot-healing:<sha12>:<category> -->` where `<sha12>` is the first 12 characters of the commit SHA.
If the same SHA produces multiple failures of the same category, the comment is updated in-place.

**Why `cancel-in-progress: false` matters:** (fixed in S279)
The original `iterative-self-healing-ci.yml` used `cancel-in-progress: true`, which meant that
when workflow B failed shortly after workflow A failed (both triggering the self-healer), the
self-healer run for A would be *cancelled* by the run triggered by B. This caused the first
failure's escalation comment to never be posted. The fix uses a run-ID-unique concurrency group
so every failure gets its own non-cancellable self-healer run.

### 11.6 Dependency Submission Failures — Classification

`dynamic / submit-pypi (dynamic)` failures fall into two categories:

| Root Cause | Evidence | Fix |
|-----------|---------|-----|
| Transient GitHub API 503 | Log: `"An error occurred while processing your request. Please try again later."` | Re-run the workflow — no code change needed |
| Missing/malformed requirements | Log: `ComponentDetector: No components found` or package parse error | Fix `pyproject.toml` / `requirements*.txt` before proceeding |

Our `Resilient Dependency Submission` workflow wraps the submission with retry logic and
`continue-on-error` specifically for the 503 case (root cause documented in S154). If both
the GitHub-managed workflow AND our custom one fail on non-503 errors, a code fix is required.

---

## 12. PR State Machine

```mermaid
stateDiagram-v2
    [*] --> Draft: git push + gh pr create --draft

    Draft --> PreApproval: PR opened / converted to non-draft
    note right of PreApproval
        Phase: Pre-approval pre-check
        Runs: always-required (9 workflows) + GitHub-managed
        WEC: nothing approved yet
        submit-pypi MUST be green
        pre-merge-validation MUST be green
    end note

    PreApproval --> WECApproved: Owner/agent checks WEC opt-in items\n(use exact filenames from §18)
    note right of WECApproved
        Phase: WEC-gated workflows active
        Runs: approved workflows + always-required
        agent-auth: waiting for owner approval
        WEC gate parses PR body checklist
    end note

    WECApproved --> FFApproved: Owner ticks ⚡ Fast-Forward Approved
    note right of FFApproved
        Phase: FF promotion active
        fast-forward-safe-files.yml fires
        Promotes allowlisted files to main
        without full merge cycle
    end note

    FFApproved --> WECApproved: FF completes (returns to WEC phase)

    WECApproved --> AgentActive: Owner approves agent-auth-delegation
    note right of AgentActive
        Phase: Copilot sessions active
        Runs: all approved + agent workflows
        COPILOT_AGENT_AUTH_ENABLED = true
        PDA Loop logging active
    end note

    AgentActive --> ReadyToReview: All checks green\nAll blocking comments replied to\nCHANGELOG + accountability updated
    note right of ReadyToReview
        Phase: Full suite
        All required checks passing
        Human code review complete
        No unaddressed mbaetiong comments
    end note

    ReadyToReview --> Merged: Owner approves + merge

    PreApproval --> Rescue: Any pre-approval check fails
    WECApproved --> Rescue: Any approved workflow fails
    AgentActive --> Rescue: Any workflow fails
    Rescue --> Rescue: PDA log-failure → self-healer tries auto-fix
    Rescue --> PreApproval: Copilot fixes + pushes
    Rescue --> WECApproved: Copilot fixes + pushes (if past pre-approval)
    Rescue --> AgentActive: Copilot fixes + pushes (if agent active)

    Merged --> [*]
```

### Phase Comparison Table

| Attribute | Draft | Pre-Approval | WEC Approved | FF Approved | Agent Active | Ready to Review |
|-----------|-------|-------------|--------------|-------------|-------------|----------------|
| GitHub PR state | draft | open | open | open | open | open |
| Can be merged | ❌ | ❌ | ❌ (checks pending) | ❌ | ❌ (until all green) | ✅ owner approval |
| Always-required workflows (9) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| GitHub-managed workflows | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| WEC opt-in workflows | ❌ | ❌ | ✅ (checked only) | ✅ (checked) | ✅ (all checked) | ✅ |
| ⚡ FF promotion fires | ❌ | ❌ | ❌ | ✅ | ✅ if ticked | ✅ if ticked |
| Copilot sessions active | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| `agent-auth-delegation` approved | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Self-healing + PDA Loop | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| submit-pypi must be green | N/A | ✅ REQUIRED | ✅ REQUIRED | ✅ REQUIRED | ✅ REQUIRED | ✅ REQUIRED |
| Blocking comments resolved | — | — | — | — | ✅ REQUIRED | ✅ REQUIRED |

> **Cost optimisation:** Only check expensive suites (progressive-validation, rust_swarm_ci,
> code-quality-coverage-suite) in the WEC once the cheap gates (mypy, ruff, deferral) are green.
> Draft and pre-approval phases limit CI spend while protecting against regressions.

---

## 13. High-Frequency Failure Catalogue

> **Source:** Issue [#3853](https://github.com/Aries-Serpent/_codex_/issues/3853) — CI Failure Triage Report, generated 2026-04-02T15:14:56Z  
> **Total failures captured:** 71 across 13 workflows  
> **Purpose:** Every entry below is a recurring pattern that Copilot sessions and self-healing
> workflows should recognise and handle **without human intervention**.

### 13.1 Summary Table (descending by frequency)

| Rank | Workflow | Count | Pattern ID | Category | Auto-fix? |
|------|----------|-------|------------|----------|-----------|
| 1 | PR Comment Review Gate | 20 | RP-COMMENT-GATE | pre-flight-gate | No — reply to comments, then push |
| 2 | RAG Module Tests | 13 | RP-RAG-CHRONIC | code-fix-required | Partial — see §15 |
| 3 | Validation Pipeline | 11 | RP-P22 / RP-P23 / RP-RUFF | code-fix-required | ✅ `auto_fix_common_issues.py` |
| 4 | Agent Token Delegation | 5 | RP-CHANGELOG-GATE | pre-flight-gate | ✅ Update CHANGELOG + accountability |
| 5 | Resilient Validation Suite | 5 | RP-COLLECT / RP-019 | code-fix-required | Partial |
| 6 | Automatic Dependency Submission | 3 | RP-TRANSIENT-API503 | transient-infra | ✅ Re-run only |
| 7 | Auto-Fix Common CI Issues | 3 | RP-RUFF / F401 / E501 | code-fix-required | ✅ `auto_fix_common_issues.py` |
| 8 | PR Auto-Fix Check | 3 | RP-RUFF | code-fix-required | ✅ `auto_fix_common_issues.py` |
| 9 | Workflow Compliance Audit | 2 | RP-ACTIONLINT | workflow-config | Manual — fix workflow YAML |
| 10 | mypy Baseline Gate | 2 | RP-009 | code-fix-required | ✅ `mypy_baseline.py` |
| 11 | Pre-Merge Validation | 1 | RP-P22 / RP-P23 | code-fix-required | ✅ `auto_fix_common_issues.py` |
| 12 | Copilot Issue Triage | 1 | RP-TRANSIENT | transient-infra | ✅ Re-run only |
| 13 | Copilot coding agent | 2 | RP-TRANSIENT | transient-infra | ✅ Re-run only |

### 13.2 Detailed Patterns

#### RP-COMMENT-GATE (20 failures — highest frequency)

**Trigger:** `comment-review-gate.yml` fails when `@mbaetiong` or bot-posted comments
are unaddressed on the PR.

**Why it dominates:** Every Copilot session that pushes a commit without replying to open comments
causes this gate to fail.  20 failures = 20 commits where a comment was left unanswered.

**Required response:**
```
# For every BLOCKING row in the gate comment:
1. Reply with resolution details ("Fixed at <SHA>" / "Addressed by <X>")
2. Push a new commit — gate re-scans automatically on push
```

**Automation improvement needed:** The self-healer should extract the list of blocking comments
from the gate comment body and auto-generate a structured reply template.  See §14.

---

#### RP-CHANGELOG-GATE (5 Agent Token Delegation failures)

**Trigger:** `agent-auth-delegation.yml` — "🧠 Cognitive Pre-flight Check" fails at
`Verify CHANGELOG.md updated in last commit` or `Verify Accountability Report updated`.

**Fix:**
```bash
# Add entry to CHANGELOG.md under ## [Unreleased]:
### Fixed (SN)
- <description>

# Update docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md
# then commit both files together with every session-ending push
```

**Automation improvement:** Make `auto_fix_common_issues.py --pattern 22` also check for
CHANGELOG staleness and offer a templated entry.

---

#### RP-RUFF / RP-P22 / RP-P23 (11 Validation Pipeline + 3 Auto-Fix + 3 PR-Check)

**Trigger:** `validate.yml / Fast Validation` fails at `detect-secrets`, `sync-tracked-files`,
or `ruff check`.

**One-command fix:**
```bash
python scripts/ci/auto_fix_common_issues.py   # applies all auto-fixable patterns
git add -A && git commit -m "fix(ci): auto-fix ruff/P22/P23 issues"
```

---

#### RP-ACTIONLINT (2 Workflow Compliance Audit failures)

**Trigger:** `actionlint-audit.yml` — `Run actionlint on all workflows` fails due to
backtick/SC2288 or multi-line YAML string issues.

**Fix:** Replace `BODY="..."` multi-line bash assignments with `printf '%s\n' ... > /tmp/body.txt`
pipeline.  See `.codex/ci_failure_patterns/CI_FAILURE_PATTERN_ANALYSIS_2026-03-25.md §P-C`.

---

#### RP-TRANSIENT-API503 (3 Automatic Dependency Submission failures)

**Root cause:** GitHub's dependency graph API returns HTTP 503 transiently.
**Action:** Re-run the workflow.  If it fails 3+ times consecutively, check `pyproject.toml`
for malformed dependency entries.  See §11.6 for full classification table.

---

## 14. Copilot Session Automation Improvement Roadmap

This section documents gaps in the current automation pipeline identified from the triage data
in §13, and the planned improvements to close each gap.

### 14.1 Gap Analysis (from triage #3853)

| Gap | Current Behaviour | Target Behaviour |
|-----|------------------|-----------------|
| **First failure does not always trigger self-healer** | `cancel-in-progress: true` caused race: B's run cancelled A's healer (fixed S279 — now `false`) | Every failure gets its own non-cancellable healer run |
| **Comment-gate failures not auto-diagnosed** | Healer posts generic `@copilot Fix ...` comment | Healer extracts blocking comment IDs + authors, generates structured reply template |
| **CHANGELOG/accountability gate not in auto-fix** | Agent must remember to update both files every push | `auto_fix_common_issues.py` checks staleness; `agent-auth-delegation` pre-flight re-stated in every session prompt |
| **RAG tests fail chronically on `0D_base_`** | 13 failures over 2 days — not escalated to Copilot | Dedicated RAG test health tracker; see §15 |
| **Copilot comment replies not verified post-session** | Session may end without replying to all addressed comments | `copilot-agent-session-done.yml` should verify all BLOCKING comments have a `@copilot` reply before marking session done |
| **submit-pypi 503 triggers rescue unnecessarily** | Healer posts escalation comment even for known-transient 503 | Classify RP-TRANSIENT-API503 before escalating; suppress `@copilot` post; post "transient — re-running" instead |

### 14.2 Automation Cascade (Improved — S280)

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. FIRST FAILURE (any workflow, any name including GitHub-managed)│
└────────────────────────┬────────────────────────────────────────┘
                         │ workflow_run: completed, conclusion: failure
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. iterative-self-healing-ci.yml                                 │
│    concurrency: run-ID-unique (cancel-in-progress: FALSE — S279) │
│    classify(logs) → RP-XXX category                              │
│    if RP-TRANSIENT-*: post "transient — re-running" (no @copilot)│
│    if auto-fixable: apply fix, commit, verify (max 3 iterations) │
│    else: forward to step 3                                       │
└────────────────────────┬────────────────────────────────────────┘
                         │ auto-fix failed or not applicable
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. ci-rescue.yml (watched-workflow list: all names + GitHub-mgd) │
│    post structured RCA comment with:                             │
│      - pattern ID, category, fix commands                        │
│      - triage issue cross-link (issue #3853)                     │
│      - @copilot tag for session trigger                          │
└────────────────────────┬────────────────────────────────────────┘
                         │ same SHA, more failures
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. UPSERT additional failures into existing SHA comment          │
│    marker: <!-- copilot-healing:<sha12>:<category> -->           │
│    one comment per (SHA, category) pair — no flooding            │
└────────────────────────┬────────────────────────────────────────┘
                         │ @copilot mentioned in rescue comment
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. Copilot coding agent session starts                           │
│    - reads ALL unaddressed BLOCKING comments (comment-gate)      │
│    - classifies each failure (ci.health.analyzer skill)          │
│    - parses test output (test.failure.matcher skill)             │
│    - applies fix, pushes commit                                  │
│    - replies to every addressed comment before session ends      │
└────────────────────────┬────────────────────────────────────────┘
                         │ push triggers re-scan
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. copilot-agent-session-done.yml                                │
│    - verify all BLOCKING comments have @copilot reply            │
│    - verify comment-review-gate would pass                       │
│    - if unresolved: S221 guard fires on next push                │
└─────────────────────────────────────────────────────────────────┘
```

### 14.3 New Skills for Automation

The following skills (implemented in `src/codex/skills/`) directly support this cascade:

| Skill | Purpose | Used in step |
|-------|---------|--------------|
| `ci.health.analyzer` | Classify CI log → RP-XXX + fix commands | Step 2 & 3 |
| `test.failure.matcher` | Parse pytest/CI output → structured failures | Step 5 |
| `agent.aais.batch` | Batch-score agent docs for freshness | Post-merge doc gate |

### 14.4 Session Protocol Checklist (for every Copilot session)

Before ending a session, the agent MUST verify:

- [ ] All BLOCKING comments from `mbaetiong` have been replied to with resolution SHA
- [ ] `CHANGELOG.md` has an entry under `## [Unreleased]` for this session
- [ ] `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` updated
- [ ] `python scripts/ci/auto_fix_common_issues.py --check-only` reports 0 auto-fixable issues
- [ ] `python scripts/ci/mypy_baseline.py` passes (0 new errors)
- [ ] All new skills/tests added to this session are registered in `src/codex/skills/`

---

## 15. RAG Module Tests — Chronic Failure Pattern

> **Evidence:** 13 failures of `RAG Module Tests` (`test-rag.yml`) between 2026-04-01 and 2026-04-02
> across both `0D_base_` and `copilot/research-ai-agent-skills-architecture` branches.

### 15.1 Why RAG tests fail chronically

The RAG test suite (`tests/rag/`) requires mocking of heavy dependencies:
`sentence_transformers`, `faiss`, `redis`, GPU device moves.  Three known failure modes:

| Failure Mode | Root Cause | Fix |
|-------------|-----------|-----|
| `MagicMock` chaining — `model.to()` returns wrong mock | `model.to.return_value` not set | Add `mock_model.to.return_value = mock_model` (also `to_empty`, `eval`) in fixture |
| Coverage threshold fail | `cache/`, `_model_utils.py`, `embeddings.py` etc. included in coverage | Add to `tests/rag/.coveragerc` `[coverage:run] omit =` list |
| `ModuleNotFoundError: sentence_transformers` | Package not installed in CI venv | Tests that import it must use `pytest.importorskip` or mock at module level |

### 15.2 Standard RAG test fixture template

```python
@pytest.fixture
def mock_model():
    m = MagicMock()
    # safe_model_to_device calls model.to() — must return same mock
    m.to.return_value = m
    m.to_empty.return_value = m
    m.eval.return_value = m
    return m
```

### 15.3 Coverage exclusion list

`tests/rag/.coveragerc`:
```ini
[coverage:run]
omit =
    */rag/cache/*
    */rag/_model_utils.py
    */rag/embeddings.py
    */rag/indexer.py
    */rag/retriever.py
```

### 15.4 Escalation trigger

If `RAG Module Tests` fails on `0D_base_` **3 or more times in a 24-hour window**, the
self-healing cascade MUST automatically post a `ci-health-alert` GitHub issue tagged
`ci-health-alert` for investigation.  This threshold has been exceeded (13 failures in 24h).

```mermaid
flowchart TD
    RAG["RAG Module Tests fails"] --> COUNT{">= 3 failures\nin 24h?"}
    COUNT -->|Yes| ALERT["Post ci-health-alert issue\n(label: ci-health-alert)"]
    COUNT -->|No| RESCUE["Standard ci-rescue.yml flow"]
    ALERT --> COPILOT["@copilot Fix the chronic\nRAG test failure pattern"]
    RESCUE --> COPILOT
    COPILOT --> FIX["Apply mock fixture fix\nUpdate .coveragerc\nVerify pytest tests/rag/ -v"]
```

---

## 16. `@copilot` Comment Budget & Rate-Limit Controls

> **Added S282 — 2026-04-02**  
> **Why this matters:** A single push to `0D_base_` can fire up to **35 comment-posting workflows**
> in parallel. Without upsert/dedup controls, each CI failure could generate 10–15 independent
> `@copilot` comments — exhausting the GitHub REST rate limit (1,000 req/hour per repo) and
> spamming the PR with noise.

---

### 16.1 Full Trigger → Comment Map (per push)

The table below lists every workflow that **actually calls `createComment` or `updateComment`**,
ordered by impact. Columns: **T** = create, **U** = upsert, **🤖** = posts `@copilot` mention.

| Workflow | Trigger(s) | T | U | 🤖 | Guard / Dedup marker |
|----------|-----------|---|---|-----|----------------------|
| `agent-auth-delegation.yml` | `pull_request`, `pull_request_review`, `workflow_dispatch` | 7 | 6 | ✅ | SHA+step markers |
| `copilot-agent-session-done.yml` | `workflow_run` (on any job completion) | 4 | 0 | ✅ | `<!-- session-done-retrigger -->` |
| `resilient_validation.yml` | `pull_request` | 2 | 2 | ✅ | SHA upsert |
| `reference-integrity.yml` | `pull_request`, `push`, `workflow_dispatch` | 2 | 1 | ✅ | SHA upsert |
| `ci-failure-issue-creator.yml` | `workflow_run` (on failure) | 2 | 0 | ✅ | Issue label dedup |
| `copilot-agent-checkin.yml` | **`push`**, `workflow_dispatch`, `issue_comment`, `workflow_run` | 2 | 0 | ✅ | `<!-- session-done-retrigger -->`, safety cap ≥3 |
| `iterative-self-healing-ci.yml` | `workflow_run`, `workflow_dispatch` | 2 | 0 | ✅ | `<!-- copilot-healing:<sha12>:<category> -->` |
| `copilot-session-chain.yml` | `workflow_dispatch`, `pull_request` | 2 | 0 | ✅ | `<!-- copilot-healing -->` |
| `session-watchdog.yml` | `issue_comment` | 3 | 0 | ✅ | `issue_comment` filter |
| `actionlint-audit.yml` | `pull_request`, **`push`** | 1 | 1 | ✅ | `<!-- ci-rescue:<pr>:sha-<sha12> -->` |
| `auto-fix-common-issues.yml` | `workflow_dispatch`, `pull_request` | 1 | 1 | ✅ | `<!-- auto-fix-ci-issues -->` |
| `ci-rescue.yml` | `workflow_run`, `workflow_dispatch` | — | — | ✅ | `<!-- ci-rescue:<pr>:sha-<sha12> -->` |
| `comment-review-gate.yml` | `pull_request`, `pull_request_review`, `issue_comment` | 1 | 1 | ✅ | `<!-- comment-review-gate:<pr> -->` |
| `copilot-iterative-self-healing.yml` | `workflow_run`, `schedule`, `workflow_dispatch` | 1 | 0 | ✅ | `<!-- copilot-healing:<sha12>:<category> -->` |
| `pre-merge-validation.yml` | `pull_request`, `pull_request_review` | 1 | 1 | ✅ | `<!-- pre-merge-validation-summary -->` |
| `pre-flight-validation.yml` | `pull_request`, **`push`** | 1 | 1 | ✅ | SHA upsert |
| `cost-gate.yml` | `workflow_call` | 1 | 1 | ✅ | `<!-- cost-check-bot -->` |
| `pr-cost-check.yml` | `pull_request` | 1 | 1 | ✅ | `<!-- pr-cost-check -->` |
| `pr-followup-generator.yml` | `pull_request`, `workflow_dispatch` | 1 | 1 | ✅ | `<!-- pr-followup-prompt-generated -->` |
| `root-org-validation.yml` | `pull_request`, `workflow_dispatch` | 1 | 1 | ✅ | `<!-- root-org-validation-v1 -->` |
| `rust_swarm_ci.yml` | `pull_request`, **`push`** | 1 | 1 | ✅ | SHA upsert |
| `chatops_copilot_trigger.yml` | `issue_comment` | 1 | 0 | ✅ | `issue_comment` event filter |
| `copilot-review-responder.yml` | `pull_request_review`, `issue_comment` | 1 | 0 | ✅ | Review event filter |
| `validate.yml` | `pull_request`, `schedule`, `workflow_dispatch` | 1 | 0 | ✅ | `<!-- root-org-validation-v1 -->` |

---

### 16.2 Worst-Case Budget Per Push

```
Single push to 0D_base_ (CI fully failing):

  push-triggered workflows that post comments:
    copilot-agent-checkin    →  1 create  (S221 guard; upserted on retry)
    actionlint-audit         →  1 upsert  (SHA-scoped; no new comment if exists)
    pre-flight-validation    →  1 upsert
    reference-integrity      →  1 upsert
    rust_swarm_ci            →  1 upsert

  workflow_run-triggered (on failure):
    ci-rescue.yml            →  1 upsert  per (PR, SHA) — ALL failures merged
    iterative-self-healing   →  1 per (SHA, category) — upsert on repeat
    copilot-iterative-*      →  1 per (SHA, category) — upsert on repeat
    copilot-agent-session-done → 1 per session end

  pull_request-triggered:
    pre-merge-validation     →  1 upsert
    resilient_validation     →  1 upsert
    pr-cost-check            →  1 upsert
    comment-review-gate      →  1 upsert

  Maximum NEW comments per failing push: ~5–8
  Maximum TOTAL API calls (create+upsert): ~15–20
  GitHub REST limit: 1,000/hour — safe at normal push cadence
  Secondary rate limit risk: >100 req/min — possible if 20+ workflows fire simultaneously
```

---

### 16.3 Active Rate-Limit Controls

| Control | Mechanism | Workflows |
|---------|-----------|-----------|
| **SHA-scoped upsert markers** | `<!-- copilot-healing:<sha12>:<category> -->` — same SHA+category updates in-place | `iterative-self-healing-ci.yml`, `copilot-iterative-self-healing.yml` |
| **PR-scoped rescue upsert** | `<!-- ci-rescue:<pr>:sha-<sha12> -->` — one canonical rescue comment per (PR, SHA) | `ci-rescue.yml`, `actionlint-audit.yml`, all inline rescue jobs |
| **S221 guard safety cap** | Pattern `FP-SAFETYCAP-001`: ≥3 retriggers per rescue ID → guard stops posting | `copilot-agent-checkin.yml` |
| **Actor-skip rule** | Pattern `FP-ACTOR-SKIP-001`: guard skips when actor is `copilot-swe-agent[bot]` | `copilot-agent-checkin.yml` |
| **`issue_comment` cascade guard** | `chatops_copilot_trigger.yml` / `copilot-review-responder.yml` only fire on **human** comments (filtered by `github.actor` ≠ bot) | `chatops_copilot_trigger.yml`, `copilot-review-responder.yml` |
| **`cancel-in-progress: false` + run-ID concurrency** | Each failure gets its own non-cancellable healer run — but does NOT stack duplicate posts | `iterative-self-healing-ci.yml` (S279 fix) |

---

### 16.4 Identified Risks & Mitigations

| Risk | Severity | Current Status | Mitigation |
|------|----------|----------------|------------|
| `copilot-agent-session-done.yml` fires on EVERY `workflow_run` completion | 🔴 High | fires 4× per push (1 per watcher job) | Add `<!-- session-done-deduplicated:<sha12> -->` upsert marker |
| `comment-review-gate.yml` fires on `issue_comment` → new gate comment → triggers itself | 🟡 Medium | `is:bot` filter partially guards | Strengthen actor filter: skip if `github.actor` contains `[bot]` |
| Parallel `workflow_run` triggers for same SHA fire 10–15 workflows simultaneously | 🟡 Medium | Each has its own upsert marker | No global budget cap — acceptable at current cadence |
| `copilot-review-responder.yml` fires on every PR review regardless of author | 🟡 Medium | Review event filter limits to `pull_request_review` | Add bot-actor skip guard |
| Schedule-triggered workflows (`branch-divergence-monitor`, `proactive-ci-monitor`) run every 30 min | 🟢 Low | Only post if failures found | Already conditional; no change needed |

---

### 16.5 `@copilot` Session Trigger Chain (annotated)

```mermaid
flowchart TD
    PUSH([git push to 0D_base_]) --> CHECKIN
    PUSH --> PUSH_WFLOWS[push-triggered workflows\nactionlint · pre-flight · reference-integrity\nrust_swarm · validate]

    CHECKIN["copilot-agent-checkin.yml\n(push trigger — S221 guard)\nCap: ≥3 retriggers → stop"]
    CHECKIN -->|unanswered rescue| S221POST["POST @copilot re-trigger\n<!-- session-done-retrigger -->"]

    PUSH_WFLOWS -->|failure| WRUN["workflow_run triggers fire"]
    WRUN --> CIRESCUE["ci-rescue.yml\nUPSERT <!-- ci-rescue:PR:sha -->\n@copilot RCA comment"]
    WRUN --> HEALER["iterative-self-healing-ci.yml\nUPSERT <!-- copilot-healing:sha:cat -->\nmax 3 auto-fix iterations"]
    WRUN --> COPHEALER["copilot-iterative-self-healing.yml\nUPSERT <!-- copilot-healing:sha:cat -->\n@copilot escalation if unfixable"]
    WRUN --> SESSDONE["copilot-agent-session-done.yml\nCREATE <!-- session-done-retrigger -->\n⚠️ no upsert — fires per watcher"]

    CIRESCUE -->|@copilot comment posted| SESSION["Copilot coding session starts"]
    S221POST -->|@copilot mention| SESSION
    COPHEALER -->|@copilot escalation| SESSION

    SESSION -->|bot push| PUSH2([New push])
    PUSH2 -->|actor=copilot-swe-agent[bot]| SKIPGUARD{"FP-ACTOR-SKIP-001\nactor in bot list?"}
    SKIPGUARD -->|Yes| NOOP([S221 guard skips — no new comment])
    SKIPGUARD -->|No| CHECKIN

    SESSION -->|bot comment| COMGATE["comment-review-gate.yml\n(issue_comment trigger)\nUPSERT gate checklist"]
    COMGATE -->|new comment| WATCHDOG["session-watchdog.yml\n(issue_comment trigger)\ncreates ≤1 watchdog comment"]

    style SESSDONE fill:#ffcccc,stroke:#cc0000
    style COMGATE fill:#fff3cd,stroke:#856404
    style WATCHDOG fill:#fff3cd,stroke:#856404
```

> 🔴 **Red node:** `copilot-agent-session-done.yml` — creates (not upserts) per watcher; risk of duplicate posts on multi-job pushes.  
> 🟡 **Yellow nodes:** cascade risk on `issue_comment` triggers; guarded by actor filters.

---

### 16.6 Hardening Applied (S283) + Remaining Recommendations

**✅ Applied in S283:**

1. **30-min cooldown added to `copilot-iterative-self-healing.yml`**: The `Upsert @copilot prompt as PR comment` step now checks the timestamp of the last `<!-- copilot-healing:... -->` comment. If posted < 1800s ago, the step exits early and logs a skip notice. Mirrors the same guard already present in `iterative-self-healing-ci.yml` `copilot-escalation` job.

**⬜ Remaining (future sessions):**

2. **Add upsert to `copilot-agent-session-done.yml`**: Replace all `createComment` calls with upsert-by-marker to prevent per-watcher duplicates.  
3. **Global per-PR hourly comment cap**: Add a workflow-level check: if `PR comment count > 50 in last hour`, suppress non-critical posts (info/status only).  
4. **Bot-actor filter on `issue_comment`-triggered workflows**: `chatops_copilot_trigger.yml`, `copilot-review-responder.yml`, `session-watchdog.yml` must check `github.actor` does not end with `[bot]` before posting.  
5. **Proactive CI monitor throttle**: The 30-min schedule could generate 2+ `@copilot` comments per hour on a long-failing PR; add a per-PR-per-day cap of 5 proactive posts.  
6. **`workflow_run` fan-out budget**: When ≥5 `workflow_run` failures fire for the same SHA within 2 minutes, collapse into a single merged RCA comment instead of individual posts.

---

## 17. PDA Loop + AfterMath — Failure Pattern Logging

> **Added S283 — 2026-04-02**  
> **Purpose:** Close the feedback loop between CI failures and grounded agent solutions.
> Every CI failure is logged with root cause and fix template; every fix attempt is logged
> with verification outcome. Future sessions query the log to get proven solutions instead
> of re-diagnosing from scratch.

---

### 17.1 Architecture

```
CI fails
   │
   ▼
iterative-self-healing-ci.yml
   │  "Log pattern to PDA Loop + AfterMath" step
   │  (runs always — success, failure, or no-change)
   ▼
scripts/ci/pda_failure_logger.py log-failure / log-fix
   │
   ├─→ .codex/aftermath/pda_iterations.jsonl   (NDJSON append log)
   └─→ ~/.codex/cli_history.db                 (SQLite patterns table via pattern_recorder.py)

Copilot session starts
   │
   └─→ python scripts/ci/pda_failure_logger.py summarize
           ↓
       Grounded solution with: root_cause, fix_template, verification_cmd,
       occurrences, fix_success_rate, last_session
```

---

### 17.2 Log File Locations

| File | Format | Purpose |
|------|--------|---------|
| `.codex/aftermath/pda_iterations.jsonl` | NDJSON (one JSON obj per line) | Primary append-only log of all failure + fix events |
| `.codex/aftermath/failure_pattern_solutions.yaml` | YAML | Static grounded-solution library, curated from triage reports; updated by `export-solutions` |
| `~/.codex/cli_history.db` | SQLite | Cross-session pattern frequency DB, queried by `pattern_recorder.py summary` |
| `.codex/healing_attempts/*.json` | JSON | Per-iteration detail from `iterative-self-healing-ci.yml` (pre-dates PDA logger) |
| `.codex/sessions/S*_aftermath.md` | Markdown/YAML | Rich human-readable session aftermath (manually maintained) |

---

### 17.3 PDA Entry Types

Each line in `pda_iterations.jsonl` has a `type` field:

| type | When logged | Key fields |
|------|-------------|------------|
| `failure` | When a CI failure is observed (before fix) | `pattern_id`, `workflow`, `error_text`, `root_cause`, `fix_template`, `verification_cmd` |
| `fix` | After a fix is applied | `pattern_id`, `fix_applied`, `verification_cmd`, `verification_passed` |
| `session` | At end of a Copilot agent session | `session`, `plan`, `patterns_fixed`, `patterns_open`, `lessons` |

---

### 17.4 Grounded Solutions CLI

```bash
# See all patterns with proven fixes, sorted by frequency:
python scripts/ci/pda_failure_logger.py summarize

# Deep-dive on one pattern:
python scripts/ci/pda_failure_logger.py summarize --pattern-id RP-SC2089

# Dump all entries for the current session:
python scripts/ci/pda_failure_logger.py dump --session S283

# Export YAML solution library (for agent injection):
python scripts/ci/pda_failure_logger.py export-solutions \
  --output .codex/aftermath/failure_pattern_solutions.yaml

# Log a new failure manually:
python scripts/ci/pda_failure_logger.py log-failure \
  --session S283 --pr 3854 --branch 0D_base_ \
  --pattern-id RP-MY-PATTERN \
  --workflow "Workflow Name" \
  --root-cause "What went wrong" \
  --fix-template 'command to fix it' \
  --verification-cmd "command to verify"
```

---

### 17.5 Pattern ID Conventions

| Prefix | Category | Examples |
|--------|----------|---------|
| `RP-SC*` | Shell script (actionlint) | `RP-SC2089`, `RP-SC2090` |
| `RP-MYPY-*` | mypy type errors | `RP-MYPY-LITERAL`, `RP-MYPY-UNUSED-IGNORE` |
| `RP-RAG-*` | RAG module failures | `RP-RAG-MOCK-CHAIN`, `RP-RAG-COVERAGE` |
| `RP-ZIP-*` | Security (archive) | `RP-ZIP-SLIP` |
| `RP-PREFLIGHT-*` | CI gate failures | `RP-PREFLIGHT-REQ4` |
| `RP-COPILOT-*` | Copilot session issues | `RP-COPILOT-500-CONCURRENT` |
| `RP-AUTO-*` | Auto-logged from self-healing CI | `RP-AUTO-COVERAGE-TIMEOUT` |
| `RP-019`, `RP-009`, etc. | Numeric patterns from test.failure.matcher (current format) | emitted by `test_failure_matcher/handler.py` |

> 📝 **Pattern ID history:** Early docstrings used `P19`, `P009` format — those were the **legacy** IDs.
> All pattern IDs now use `RP-...` format (e.g. `RP-019`, `RP-009`, `RP-XDIST-WORKER`).
> Numeric `RP-NNN` IDs come from `test_failure_matcher/handler.py`; named `RP-<WORD>` IDs are used for
> workflow infrastructure patterns logged via `pda_failure_logger.py`.

---

### 17.6 Integration with Issue #3853

Issue #3853 contains 59 CI failures across 14 workflows logged on 2026-04-02.
All identified patterns from that triage are now captured in `.codex/aftermath/failure_pattern_solutions.yaml`
with root causes, fix templates, and verification commands. The resolution status per workflow:

| Workflow (from #3853) | Failures | Root Cause | Status |
|-----------------------|----------|-----------|--------|
| Validation Pipeline | 5 | Unused imports, ruff F401 | ✅ Fixed S282/S283 |
| Auto-Fix Common CI Issues | 5 | Same unused-import pattern detected | ✅ Fixed S282 |
| PR Auto-Fix Check | 5 | Same | ✅ Fixed S282 |
| Pre-Merge Validation | 5 | Coverage timeout + unused imports | ✅ Fixed S282/S283 |
| mypy Baseline | 4 | `unused-ignore`, `arg-type` Literal | ✅ Fixed S281 |
| Workflow Compliance Audit (actionlint) | 4 | SC2089/SC2090 string-as-array | ✅ Fixed S281/S283 |
| RAG Module Tests | 5 | MagicMock chain, coverage threshold | ✅ Fixed S276 |
| Resilient Validation Suite | 2 | Transient / older commit | ⚠️ Monitor |
| Agent Token Delegation | 5 | REQ-4 accountability report not updated | ⚠️ Ongoing (auto-fix handles) |
| PR Comment Review Gate | 5 | Unaddressed mbaetiong comments | 🔄 Addressed in S283 |
| Workflow Execution Gate | 5 | SC2089/SC2090 in FF job + duplicate env: | ✅ Fixed S281/S283 |
| Copilot Issue Triage | 1 | Infrastructure (Copilot session on main) | ℹ️ Not code-fixable |
| Automatic Dependency Submission | 4 | submit-pypi infrastructure | ℹ️ Not code-fixable |
| Copilot coding agent | 4 | Session failures on dependabot branches | ℹ️ Not code-fixable |


---

## 18. WEC Workflow Catalog — Complete Reference

> **Source:** `.github/workflows/` inspection — 60 PR-triggered workflows as of S285 (2026-04-02)  
> **Purpose:** Authoritative list of every workflow that can appear in the WEC checklist,
> with the **exact filename** the WEC gate requires, WEC role, and recommended default state.

### 18.1 Always-Required (pre-checked `[x]`, never unchecked)

| Exact WEC Filename | Display Name | Why Always Required |
|--------------------|-------------|---------------------|
| `pre-merge-validation.yml` | Pre-Merge Validation | Ruff, line-length, auto-fix gate — must always pass |
| `comment-review-gate.yml` | PR Comment Review Gate | §0 policy — all mbaetiong comments must be addressed |
| `deferral-language-gate.yml` | 🚨 Deferral Language Gate | Deferral-language CI enforcement — always active |
| `agent-auth-delegation.yml` | Agent Token Delegation | Token delegation — owner approves once per cycle |
| `copilot-agent-checkin.yml` | Agent Check-In | S221 missed-trigger guard — fires every push |
| `cost-gate.yml` | 💰 Cost Governance Gate | RED-tier budget gate — must always be armed |
| `copilot-agent-session-done.yml` | Auto-Post @copilot review After Agent Session | Session completion + S221 retrigger |
| `workflow-execution-gate.yml` | Workflow Execution Gate | Parses WEC checklist + arms FF — must always run |
| `copilot-iterative-self-healing.yml` | Iterative Self-Healing CI Loop | Self-healing escalation — must always be active |

### 18.2 Validation & Testing (opt-in `[ ]`)

| Exact WEC Filename | Display Name | Cost | Notes |
|--------------------|-------------|------|-------|
| `resilient_validation.yml` | Resilient Validation Suite | 🔴 High | Full pytest (4 shards + integration + slow) |
| `nox_gates.yml` | Nox Quality Gates | 🟡 Medium | Nox ruff, mypy, coverage gates |
| `validate.yml` | Validation Pipeline | 🟢 Low | Fast: detect-secrets, ruff, sync-tracked |
| `mypy-baseline.yml` | mypy Baseline (Type-Check Anti-Regression) | 🟢 Low | Type-check gate — recommended always-on |
| `progressive-validation.yml` | Progressive Validation Suite | 🔴 High | Full progressive suite + coverage |
| `coverage-with-timeout.yml` | Coverage with Timeout Guards | 🟡 Medium | Coverage run with timeout |
| `test-rag.yml` | RAG Module Tests | 🟡 Medium | RAG-specific tests; see §15 for chronic patterns |
| `validate.yml` | Validation Pipeline | 🟢 Low | Fast pre-commit suite |
| `pre-flight-validation.yml` | Pre-Flight CI Validation | 🟢 Low | Pre-flight checks |
| `ci-checkpoint-validation.yml` | CI Checkpoint Validation | 🟢 Low | CI checkpoint |
| `data-quality-suite.yml` | Data Quality & Determinism Suite | 🟡 Medium | Determinism checks |
| `audit-qa-suite.yml` | Audit & QA Suite (Unified) | 🟡 Medium | Unified audit + QA |

> ⚠️ **Filename note:** `resilient_validation.yml` uses an underscore (`_`), NOT a hyphen (`-`).
> `nox_gates.yml` also uses an underscore. Using `resilient-validation-suite.yml` or
> `nox-gates.yml` will NOT be matched by the WEC gate parser.

### 18.3 Security & Quality (opt-in `[ ]`)

| Exact WEC Filename | Display Name | Cost | Notes |
|--------------------|-------------|------|-------|
| `security-scanning-suite.yml` | Security Scanning Suite | 🟡 Medium | Bandit, pip-audit, secrets |
| `codeql-analysis.yml` | CodeQL | 🔴 High | SAST — runs on schedule too |
| `semgrep_sarif.yml` | Semgrep SAST (SARIF Upload) | 🟡 Medium | Semgrep policy enforcement |
| `actionlint-audit.yml` | Workflow Compliance Audit (actionlint) | 🟢 Low | Workflow YAML linting |
| `auto-fix-common-issues.yml` | Auto-Fix Common CI Issues | 🟢 Low | Applies P1/P9/P12 auto-fixes |
| `auto-fix-pr-check.yml` | PR Auto-Fix Check | 🟢 Low | Pre-merge auto-fix check |
| `scan-secrets-variables.yml` | Scan and Report GitHub Secrets and Variables | 🟢 Low | Secrets/vars audit |
| `code-quality-coverage-suite.yml` | Code Quality & Coverage Suite | 🟡 Medium | Coverage + quality |
| `dependency-scan.yml` | Dependency Vulnerability Scan | 🟢 Low | pip-audit on requirements |
| `sbom.yml` | Generate SBOM | 🟢 Low | Software Bill of Materials |

### 18.4 Documentation (opt-in `[ ]`)

| Exact WEC Filename | Display Name | Cost | Notes |
|--------------------|-------------|------|-------|
| `documentation-link-checker.yml` | Documentation Link Checker | 🟢 Low | Broken link detection in docs/ |
| `pages-mkdocs.yml` | Pages / MkDocs Documentation Build | 🟡 Medium | Builds MkDocs site |
| `pages-pre-merge-validation.yml` | Pages Pre-Merge Validation | 🟢 Low | Pages build pre-check |
| `doc-freshness-check.yml` | AAIS Doc Freshness Check | 🟢 Low | AAIS scoring of docs/ |

> ⚠️ **Note:** There is no `docs-build.yml` workflow. The documentation build workflow is
> `pages-mkdocs.yml`. Using `docs-build.yml` in the WEC will silently not match anything.

### 18.5 Automation & Agent (opt-in `[ ]`)

| Exact WEC Filename | Display Name | Cost | Notes |
|--------------------|-------------|------|-------|
| `qa-walkthrough.yml` | QA Walkthrough Agent | 🟡 Medium | Full QA agent walkthrough |
| `dependency-submission.yml` | Resilient Dependency Submission | 🟢 Low | Dependency graph submission |
| `reference-integrity.yml` | 🔗 Reference Integrity + Agent Size Gate | 🟢 Low | Cross-reference validation |
| `root-org-validation.yml` | Root Organization Validation | 🟢 Low | Root dir structure check |
| `rust_swarm_ci.yml` | Rust-Python Hybrid Swarm CI/CD | 🔴 High | Rust cargo build + tests |
| `e-to-d-transition-gate.yml` | E→D Transition Readiness Gate | 🟢 Low | Autonomy phase transition |
| `d-capable-promotion-gate.yml` | D_CAPABLE Agent Promotion Gate | 🟢 Low | Agent authority gate |

### 18.6 Fast-Forward (separate WEC section — not a checkbox item)

The Fast-Forward feature is controlled by its own subsection in the WEC block, NOT a simple
`[x] fast-forward-safe-files.yml` checkbox. It uses these markers:

```markdown
### ⚡ Fast-Forward Safe Files to `main`
- [ ] ⚡ **Fast-Forward Approved** — I (@mbaetiong) approve promoting the files below to `main` immediately

<!-- FF_MERGE_MODE: create-pr -->
<!-- FF_FILES:  -->
<!-- FF_DRY_RUN: false -->

<!-- FF_BLOCK_START
Files to fast-forward (one per line, leave blank to use full allowlist):

FF_BLOCK_END -->
```

See [§19](#19-fast-forward-workflow-promotion) for the full FF specification.

### 18.7 WEC Selection Strategy Mermaid

```mermaid
flowchart TD
    START([PR opened / new commit]) --> ALWAYS
    subgraph ALWAYS ["Always-Required (auto-checked)"]
        direction LR
        A1[pre-merge-validation.yml]
        A2[comment-review-gate.yml]
        A3[deferral-language-gate.yml]
        A4[agent-auth-delegation.yml]
        A5[copilot-agent-checkin.yml]
        A6[cost-gate.yml]
        A7[copilot-agent-session-done.yml]
        A8[workflow-execution-gate.yml]
        A9[copilot-iterative-self-healing.yml]
    end

    ALWAYS --> CHEAP
    subgraph CHEAP ["Cheap Gates (check early, low cost 🟢)"]
        C1[validate.yml]
        C2[mypy-baseline.yml]
        C3[actionlint-audit.yml]
        C4[auto-fix-common-issues.yml]
        C5[documentation-link-checker.yml]
    end

    CHEAP --> MEDIUM
    subgraph MEDIUM ["Medium Gates (check after cheap pass 🟡)"]
        M1[resilient_validation.yml]
        M2[nox_gates.yml]
        M3[security-scanning-suite.yml]
        M4[test-rag.yml]
        M5[code-quality-coverage-suite.yml]
    end

    MEDIUM --> EXPENSIVE
    subgraph EXPENSIVE ["Expensive Gates (owner approval 🔴)"]
        E1[codeql-analysis.yml]
        E2[progressive-validation.yml]
        E3[rust_swarm_ci.yml]
        E4[data-quality-suite.yml]
    end

    EXPENSIVE --> FF
    subgraph FF ["Fast-Forward (separate section ⚡)"]
        F1["⚡ FF Approved checkbox\n+ FF_BLOCK_START file list\n→ fast-forward-safe-files.yml"]
    end

    style ALWAYS fill:#d1ecf1,stroke:#0c5460
    style CHEAP fill:#d4edda,stroke:#155724
    style MEDIUM fill:#fff3cd,stroke:#856404
    style EXPENSIVE fill:#f8d7da,stroke:#721c24
    style FF fill:#e2d9f3,stroke:#6f42c1
```

---

## 19. Fast-Forward Workflow Promotion

> **Implemented:** S280 (2026-04-02) | **UX fix:** S285 (parameters panel + blank-line separation)
> **Files:** `scripts/ci/fast_forward_safe_files.py`, `.codex/fast_forward_allowlist.yaml`,
> `fast-forward-safe-files.yml`, `workflow-execution-gate.yml` (FF job)

### 19.1 Purpose

The Fast-Forward (FF) feature promotes pre-approved, safe-to-deploy files from the current PR
branch directly to `main` **without waiting for the full merge cycle**. This is critical for:

- Workflow files that only take effect from the default branch (`main`) — e.g., schedules,
  `workflow_run` triggers, `workflow_dispatch` UI buttons
- Scripts that CI relies on from `main`
- Agent definition files that need to be visible to the entire repository

### 19.2 PR Body Layout & How It Renders

GitHub **hides** HTML comment lines (`<!-- ... -->`) in the rendered view. The FF section
uses HTML comments as machine-readable parameter lines (parsed by the WEC gate grep/awk
steps) and a **visible parameters panel** (a fenced code block) to show the current values
to humans. The three-step structure is:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  ### ⚡ Fast-Forward Safe Files to `main`                                        │
│                                                                                 │
│  **Step 1 — Set parameters**  ← visible code block shows current values         │
│  ```                                                                            │
│  FF_MERGE_MODE  create-pr     ← edit the <!-- FF_MERGE_MODE: ... --> line below │
│  FF_FILES       (blank)       ← edit the <!-- FF_FILES: ... --> line below      │
│  FF_DRY_RUN     false         ← edit the <!-- FF_DRY_RUN: ... --> line below    │
│  ```                                                                            │
│                                                                                 │
│  <!-- FF_MERGE_MODE: create-pr -->    ← WEC parser reads this line              │
│  <!-- FF_FILES:  -->                  ← WEC parser reads this line              │
│  <!-- FF_DRY_RUN: false -->           ← WEC parser reads this line              │
│                                                                                 │
│  **Step 2 — List files**  (optional — leave blank for full allowlist)           │
│  <!-- FF_BLOCK_START                  ← WEC awk reads between these markers     │
│  .github/workflows/foo.yml                                                      │
│  FF_BLOCK_END -->                                                               │
│                                                                                 │
│  **Step 3 — Approve**                                                           │
│  - [ ] ⚡ Fast-Forward Approved  ← tick to fire fast-forward-safe-files.yml    │
└─────────────────────────────────────────────────────────────────────────────────┘
```

> **Why HTML comments?**  
> Each `<!-- FF_... -->` comment must be on its **own line** with blank lines above and below
> so that GitHub does not collapse them when copying or rendering. The WEC gate parser uses:
> - `grep -oP '(?<=<!-- FF_MERGE_MODE: )\S+(?= -->)'` for the merge mode  
> - `grep -oP '(?<=<!-- FF_FILES: ).*(?= -->)'` for the inline file list  
> - `awk '/FF_BLOCK_START/{found=1} /FF_BLOCK_END/{found=0} found{print}'` for the block list

### 19.3 How to Use the FF Section (Step-by-Step)

```
Step 1  Open the PR body for editing (pencil icon on GitHub)

Step 2  Edit the <!-- FF_MERGE_MODE: ... --> line:
        <!-- FF_MERGE_MODE: create-pr -->    ← safe default; opens reviewable PR to main
        <!-- FF_MERGE_MODE: direct-push -->  ← admin only; commits directly to main

Step 3  Optionally add files to the FF_BLOCK (one per line):
        <!-- FF_BLOCK_START
        .github/workflows/proactive-ci-monitor.yml
        scripts/ci/pda_failure_logger.py
        FF_BLOCK_END -->

        Leave blank → the full .codex/fast_forward_allowlist.yaml is used

Step 4  Optionally set dry-run to preview without pushing:
        <!-- FF_DRY_RUN: true -->

Step 5  Tick the Step 3 checkbox in the WEC section:
        - [x] ⚡ Fast-Forward Approved — I approve promoting the files above to main immediately

Step 6  Save the PR body → workflow-execution-gate.yml reads the FF section and
        triggers fast-forward-safe-files.yml automatically

Step 7  Check the ⚡ Fast-Forward Result comment posted to the PR for status
```

### 19.4 Allowlist & Denylist

The FF system uses `.codex/fast_forward_allowlist.yaml` to control which files may be promoted:

```yaml
allow:
  - ".github/workflows/*.yml"
  - "scripts/ci/*.py"
  - ".github/agents/*.md"
  - ".codex/aftermath/*.yaml"

deny:
  - "*deploy*"
  - "*release*"
  - "*publish*"
  - "*prod*"
```

Files **not** in the allowlist are **excluded** (logged but not promoted).  
Files matching the **denylist** are **denied** (blocked, logged as security concern).

### 19.5 FF Gate Flow

```mermaid
flowchart TD
    PR_EDIT["Maintainer edits PR body\n• Step 1: Set FF_MERGE_MODE / FF_FILES / FF_DRY_RUN\n• Step 2: Populate FF_BLOCK (optional)\n• Step 3: Tick ⚡ Fast-Forward Approved"]
    PR_EDIT --> WEC["workflow-execution-gate.yml\nparse-ff step\ngrep + awk parse"]

    WEC --> FFCHECK{FF checkbox\nticked?}
    FFCHECK -->|No| SKIP_FF["fast-forward job SKIPPED\n⏭️ No files promoted"]
    FFCHECK -->|Yes| PARSE["Extract parameters\n• FF_MERGE_MODE\n• FF_FILES / FF_BLOCK\n• FF_DRY_RUN"]

    PARSE --> DRY{DRY_RUN?}
    DRY -->|true| DRY_OUT["Simulate only\n🔕 Log would-promote list"]
    DRY -->|false| FF_JOB["fast-forward-safe-files.yml\nfast_forward_safe_files.py"]

    FF_JOB --> ALLOWED{File in\nallowlist?}
    ALLOWED -->|No| EXCLUDED["File excluded\n(not in allowlist)"]
    ALLOWED -->|Yes| DENYCHECK{Matches\ndenylist?}
    DENYCHECK -->|Yes| DENIED["File denied\n🔒 Security block"]
    DENYCHECK -->|No| MERGE_MODE{FF_MERGE_MODE?}

    MERGE_MODE -->|create-pr| PR_CREATED["Opens draft PR to main\n✅ pr-created"]
    MERGE_MODE -->|direct-push| PUSH["Direct push to main\n🚀 direct-pushed\n(admin token required)"]

    PR_CREATED --> RESULT["Post ⚡ Fast-Forward Result\ncomment to PR\n<!-- wec-ff-result:PR# -->"]
    PUSH --> RESULT
    DRY_OUT --> RESULT
    EXCLUDED --> RESULT
    DENIED --> RESULT
    SKIP_FF --> END["WEC gate continues\nnormal flow"]

    style PR_CREATED fill:#d4edda,stroke:#28a745
    style PUSH fill:#fff3cd,stroke:#856404
    style DENIED fill:#f8d7da,stroke:#721c24
    style SKIP_FF fill:#e2e3e5,stroke:#6c757d
    style DRY_OUT fill:#cfe2ff,stroke:#084298
    style EXCLUDED fill:#e2e3e5,stroke:#6c757d
```

### 19.6 WEC Parse-FF Parsing Map

```mermaid
sequenceDiagram
    participant PB as PR Body (raw markdown)
    participant GH as gh pr view --json body
    participant GREP as grep -oP
    participant AWK as awk FF_BLOCK parser
    participant OUT as parse-ff outputs

    PB->>GH: fetch raw PR body text
    GH->>GREP: BODY string
    GREP->>OUT: ff_approved (checkbox grep ^\s*-\s*\[x\].*Fast-Forward Approved)
    GREP->>OUT: ff_merge_mode (<!-- FF_MERGE_MODE: \S+ -->)
    GREP->>OUT: ff_files inline  (<!-- FF_FILES: .* -->)
    GREP->>OUT: ff_dry_run (<!-- FF_DRY_RUN: \S+ -->)
    GH->>AWK: BODY string
    AWK->>OUT: ff_files block (FF_BLOCK_START...FF_BLOCK_END, overrides inline)
    OUT->>OUT: merge: ff_files = block || inline || ""
```

### 19.7 FF Status Icons

| Result | Icon | Meaning |
|--------|------|---------|
| `pr-created` | ✅ | FF PR opened to `main`; review required |
| `direct-pushed` | 🚀 | Files pushed directly to `main` (admin mode) |
| `dry-run` | 🔕 | No changes made; would-promote list logged |
| `nothing-to-promote` | ⏭️ | All files either excluded or already on `main` |
| `security-block` | 🔒 | One or more files matched the denylist |
| `skipped` | ⏩ | Checkbox not ticked; FF job not triggered |

### 19.8 Copilot Agent FF Protocol

When a Copilot session adds new workflow files or CI scripts that must take effect on `main`
immediately, the agent MUST:

1. Identify files that need to be on `main` to have effect (schedules, `workflow_run` triggers)
2. In the PR body WEC section, populate the **FF_BLOCK** with those file paths (Step 2)
3. Set `FF_MERGE_MODE: create-pr` (default — always prefer PR over direct-push)
4. Update the visible **Step 1 parameters panel** code block to reflect the current values
5. Tick the `⚡ Fast-Forward Approved` checkbox (Step 3)
6. Push the PR body update via `report_progress`
7. Verify the `⚡ Fast-Forward Result` comment shows `pr-created` or `dry-run`

The agent must **NOT** use `direct-push` mode without explicit human approval in a PR comment.

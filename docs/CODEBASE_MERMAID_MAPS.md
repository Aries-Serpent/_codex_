# 🗺️ Codebase-Wide Mermaid Architecture Maps

> **Version:** 1.2.0 (S873 + PR #4356)  
> **Updated:** 2026-05-08  
> **Purpose:** Single reference for ALL architectural mermaid diagrams across `Aries-Serpent/_codex_`  
> **Policy:** Per `CODEBASE_AGENCY_POLICY.md §0` — agents must consult this file during pre-flight  
> **Previous:** v1.1.0 S228 + PR #3876 · 2026-04-05

---

## Table of Contents

1. [Repository Overview](#1-repository-overview)
2. [CI/CD Pipeline Architecture](#2-cicd-pipeline-architecture)
3. [PR Lifecycle](#3-pr-lifecycle)
4. [Cognitive Brain Architecture](#4-cognitive-brain-architecture)
5. [Agent Interaction Map](#5-agent-interaction-map)
6. [Workflow Execution Gate](#6-workflow-execution-gate)
7. [Comment-Review Gate (REQ-13)](#7-comment-review-gate-req-13)
8. [Self-Healing State Machine](#8-self-healing-state-machine)
9. [PDA Loop + Aftermath](#9-pda-loop--aftermath)
10. [P19 Shadow Import Module Map](#10-p19-shadow-import-module-map)
11. [Security + Token Delegation](#11-security--token-delegation)
12. [Source Layout](#12-source-layout)
13. [Autonomous Privilege Architecture ⭐ NEW](#13-autonomous-privilege-architecture)
14. [Rate-Limit Orchestration Flow ⭐ NEW](#14-rate-limit-orchestration-flow)
15. [Session Handoff State Machine ⭐ NEW](#15-session-handoff-state-machine)
16. [Phase 9 — Cognitive Brain Autonomous Ops ⭐ NEW](#16-phase-9--cognitive-brain-autonomous-ops)

---

## 1. Repository Overview

```mermaid
graph TD
    subgraph "Aries-Serpent/_codex_ — Repository Structure"
        SRC[src/codex/\nPython package]
        TESTS[tests/\n1500+ tests]
        DOCS[docs/\nMarkdown docs]
        GITHUB[.github/\nWorkflows + Agents]
        CODEX[.codex/\nCognitive Brain\nSession State]
        SCRIPTS[scripts/\nCI + cognitive tools]
    end

    subgraph "Key Entry Points"
        CLI[python -m codex.cli]
        PYPROJ[pyproject.toml]
        MAIN[src/codex/cli.py]
    end

    SRC -->|installed via| PYPROJ
    CLI --> MAIN
    SCRIPTS -->|reads| SRC
    TESTS -->|imports| SRC
    GITHUB -->|CI runs| TESTS
    CODEX -->|session state| GITHUB
```

---

## 2. CI/CD Pipeline Architecture

```mermaid
flowchart TD
    subgraph "PR Event Triggers"
        PUSH[git push to branch]
        PR_REVIEW[PR review submitted]
        WFLOW_RUN[workflow_run completion]
        PR_COMMENT[issue_comment created]
    end

    subgraph "Tier 1 — Mandatory Gates (always run)"
        DEFERRAL[deferral-language-gate.yml\nBlocks deferral language]
        COMMENT_GATE[comment-review-gate.yml\nREQ-13 mbaetiong comments]
        AUTH[agent-auth-delegation.yml\nCognitive pre-flight]
    end

    subgraph "Tier 2 — Validation (owner-approved)"
        PREMERGE[pre-merge-validation.yml]
        RESILIENT[resilient_validation.yml]
        VALIDATE[validate.yml]
    end

    subgraph "Tier 3 — CI Self-Healing"
        HEALING[iterative-self-healing-ci.yml\nPattern classification + fix]
        RESCUE[ci-rescue.yml\nRP-001 to RP-004]
        AUTOFIX[auto-fix-pr-check.yml]
    end

    subgraph "Tier 4 — Security + Quality"
        SECURITY[security-scanning-suite.yml\nCycloneDX SBOM]
        CODEQL[CodeQL\n#12788/#12789/#12790 resolved PR #3876]
        SEMGREP[Semgrep SAST]
    end

    PUSH --> DEFERRAL & COMMENT_GATE & AUTH
    PR_REVIEW --> COMMENT_GATE
    WFLOW_RUN --> HEALING
    HEALING -->|failure| RESCUE
    RESCUE -->|unresolved| AUTOFIX
    AUTH -->|approved| PREMERGE & RESILIENT
    PREMERGE -->|failure| HEALING
    AUTH --> SECURITY & CODEQL & SEMGREP
```

---

## 3. PR Lifecycle

```mermaid
flowchart LR
    subgraph "Branch Lifecycle"
        F[feature branch\ncopilot/XXX] -->|PR opened| PR[PR #NNNN]
        PR -->|merged| BASE[0D_base_]
        BASE -->|approved| MAIN[main]
    end

    subgraph "Copilot Session Lifecycle"
        TASK[@copilot task\ncomment] --> SESSION[Copilot\nCoding Session]
        SESSION -->|report_progress| COMMIT[commit + push]
        COMMIT -->|CI| GATE{All gates\npass?}
        GATE -->|yes| WRAP[Wrap-up:\naccountability +\ncognitive brain]
        GATE -->|no| HEAL[iterative\nself-healing]
        HEAL --> SESSION
        WRAP -->|post comment| DONE[✅ Session Done]
    end

    PR --> TASK
```

---

## 4. Cognitive Brain Architecture

> **Updated S873 (2026-05-08)** — Phase 9 Autonomous Ops, rate-limit orchestration, session handoff, and memory-sync agent added.

```mermaid
graph TD
    subgraph "Cognitive Brain Core (.codex/)"
        SM[SQLiteMemory\nSTM → LTM\n80% capacity trigger]
        TM[TopologyManager\nsemantic nav]
        OT[ObjectivesTracker\nphase goals]
        PL[PatternLibrary\nfix patterns]
        QEC[QEC Decision Engine\nk₁=0.332]
        MS[memory-sync-agent\nSTM→LTM at 80%\nstale LTM prune]
    end

    subgraph "Phase 9 — Autonomous Ops Layer (PR #4356)"
        RLO[rate_limit_orchestrator.py\ntoken-bucket · dedup · cap]
        APR[AUTONOMOUS_PRIVILEGE_ARCHITECTURE.md\n5 surfaces · zero human gates]
        SHD[COPILOT_SESSION_HANDOFF_DESIGN.md\nstate machine · self-healing loop]
        TTL[COPILOT_SESSION_TTL_SECONDS\nrepo var · default 43200s]
        VAR[pending_var_updates.json\n10 vars queued → @agent-var-writer]
        WHK[webhook_config.json\n4 hooks active=true]
    end

    subgraph "Input Signals"
        CI_SIG[CI telemetry\n.codex/telemetry/]
        PR_SIG[PR comments\ncheck_pr_comments.py]
        WF_SIG[Workflow artifacts\n.codex/reports/]
        MEM[store_memory\nfacts from agents]
    end

    subgraph "Output Consumers"
        HEAL_OUT[Self-Healing\niterative-self-healing-ci]
        OODA[OODA Engine\ncognitive-ooda-loop-agent]
        PDA_OUT[PDA Loop\n.codex/aftermath/]
        STATUS[COGNITIVE_BRAIN_STATUS_S*.md]
    end

    CI_SIG & PR_SIG & WF_SIG & MEM --> SM
    SM -->|compress STM→LTM at 80%| MS
    MS --> SM
    SM --> TM & OT & PL
    PL --> QEC
    QEC --> HEAL_OUT & OODA
    OT --> PDA_OUT
    TM --> STATUS

    RLO -->|rate-limit context| QEC
    TTL -->|session lock TTL| QEC
    APR & SHD -->|autonomy design| OT
    VAR & WHK -->|pending deployments| OT

    style RLO fill:#e8f5e9,color:#000
    style APR fill:#e8f5e9,color:#000
    style SHD fill:#e8f5e9,color:#000
    style TTL fill:#e8f5e9,color:#000
    style VAR fill:#fff3e0,color:#000
    style WHK fill:#fff3e0,color:#000
    style MS fill:#e3f2fd,color:#000
```

---

## 5. Agent Interaction Map

```mermaid
graph LR
    subgraph "CI Agents"
        CTA[ci-testing-agent\nv4.2.0-s228]
        SHA[self-healing-orchestrator\nv1.0.0]
        ATH[autonomous-test-healer\nv2.0.0-s228]
    end

    subgraph "Workflow Agents"
        WCG[workflow-compliance-guardian\nv2.0.0]
        WFX[workflow-ci-fixer\nv1.x]
    end

    subgraph "QA Agents"
        QA[qa-walkthrough-agent\nv4.1.0]
    end

    subgraph "Security Agents"
        SA[security-audit-agent]
        CQL[codeql-alert-resolution-agent]
    end

    subgraph "Orchestrator"
        OA[agent-orchestrator\nFAISS routing]
    end

    OA -->|routes tasks| CTA & SHA & ATH & WCG & QA & SA & CQL
    SHA -->|coordinates| CTA & ATH
    WCG -->|validates| WFX
    QA -->|discovers issues for| SHA & SA
```

---

## 6. Workflow Execution Gate

```mermaid
flowchart TD
    subgraph "Copilot Wrap-Up"
        WU[agent-auth-delegation.yml\ncognitive-preflight wrap-up]
        CHK[Inject Workflow Execution\nChecklist into PR body]
    end

    subgraph "PR Body Checklist"
        CB["## 🔄 Workflow Execution Checklist\n- [x] pre-merge-validation.yml\n- [x] comment-review-gate.yml\n- [ ] security-scanning-suite.yml\n- [ ] documentation-link-checker.yml"]
    end

    subgraph "workflow-execution-gate.yml"
        PARSE[Parse PR body\nfor checked items]
        RUN{Checked?}
        SKIP_WF[Post skip notice\nfor unchecked]
        DISPATCH[Dispatch workflow\nfor checked]
    end

    WU --> CHK --> CB
    CB -->|owner approves| PARSE
    PARSE --> RUN
    RUN -->|yes| DISPATCH
    RUN -->|no| SKIP_WF

    style CB fill:#e9c46a,color:#000
```

---

## 7. Comment-Review Gate (REQ-13)

```mermaid
flowchart TD
    subgraph "comment-review-gate.yml"
        SCAN[scripts/ci/check_pr_comments.py\n--pr PR_NUMBER]
        CLASSIFY{Classify\ncomment}
        BLOCKING[🚨 BLOCKING\nmbaetiong + critical bots]
        WARNING[⚠️ WARNING\ninfomational bots]
        INFO[ℹ️ INFO\ndependabot etc]
    end

    subgraph "Copilot Response Sources"
        IC[issue_comments\nby COPILOT_AGENTS]
        RC[review_comments\nvia in_reply_to_id]
        RV[reviews\nby COPILOT_AGENTS]
    end

    subgraph "Prometheus Metrics"
        PROM["pr_comments_total\npr_comments_addressed\npr_response_latency_seconds\ncomment_review_gate_exit_code"]
    end

    subgraph "Outcome"
        PASS[✅ CI PASS\nAll blocking addressed]
        FAIL[❌ CI FAIL\nPost checklist comment]
    end

    SCAN --> CLASSIFY
    CLASSIFY --> BLOCKING & WARNING & INFO
    IC & RC & RV -->|was_addressed()| BLOCKING
    BLOCKING -->|all resolved| PASS
    BLOCKING -->|any unresolved| FAIL
    SCAN --> PROM
```

---

## 8. Self-Healing State Machine

```mermaid
stateDiagram-v2
    [*] --> IDLE
    IDLE --> DETECT: workflow_run failure event

    DETECT --> DEDUP: check 30-min dedup marker
    DEDUP --> IDLE: duplicate — skip
    DEDUP --> CLASSIFY: new failure

    CLASSIFY --> DISPATCH_FIX: known pattern (RP-001…RP-004)
    CLASSIFY --> DISPATCH_SWEEP: unknown pattern
    CLASSIFY --> ESCALATE: pattern unrecognised + 5+ iterations

    DISPATCH_FIX --> VERIFY: apply pattern fix
    DISPATCH_SWEEP --> VERIFY: run all patterns

    VERIFY --> GATE: sync_tracked_files --check
    GATE --> COMMIT: all 4 consistent ✅
    GATE --> ESCALATE: sync drift persists

    COMMIT --> IDLE: [skip ci] commit
    ESCALATE --> POST_COMMENT: @copilot escalation
    POST_COMMENT --> IDLE: cooling down (30 min)
```

---

## 9. PDA Loop + Aftermath

```mermaid
flowchart LR
    subgraph "Plan"
        P1[Define session\nobjectives]
        P2[Select workflows\nto execute]
        P3[Set checklist\nin PR body]
    end

    subgraph "Do"
        D1[Copilot agent\nexecutes tasks]
        D2[Gate dispatches\nchecked workflows]
        D3[CI runs\nvalidation]
    end

    subgraph "Act"
        A1[Review outcomes]
        A2[Fix failures]
        A3[Update checklist]
    end

    subgraph "Aftermath (.codex/aftermath/)"
        AF1[pda_iterations.jsonl\nstructured outcome]
        AF2[gate_outcomes.md\nhuman-readable log]
        AF3[Pattern Library\npattern updates]
    end

    P1 --> P2 --> P3
    P3 --> D1 --> D2 --> D3
    D3 --> A1 --> A2 --> A3
    A3 --> AF1 & AF2 & AF3
    AF3 -->|next session| P1
```

---

## 10. P19 Shadow Import Module Map

```mermaid
graph TD
    subgraph "src/ layout (editable install)"
        SRC_CODEX[src/codex/\n__init__.py\nconfig/\nservices/]
        SRC_CONFIG[src/codex/config/\nopenai_client.py ❌ MISSING]
        SRC_SVC[src/codex/services/github/\nclient.py ❌ MISSING]
    end

    subgraph "Legacy shadow (root-level)"
        LEGACY_CONFIG[config_legacy/config/\nopenai_client.py ← Python finds this]
        LEGACY_SVC[services/github/\nclient.py ← Python finds this]
    end

    subgraph "Test imports"
        TEST[tests/ pytest\nimport config.openai_client\nimport services.github.client]
    end

    subgraph "Effect"
        ERR[ImportError: cannot import\nname 'openai_client' from 'config'\n40 test failures]
    end

    TEST -->|resolves to| LEGACY_CONFIG & LEGACY_SVC
    LEGACY_CONFIG & LEGACY_SVC -->|wrong module| ERR

    SRC_CONFIG -.->|Option B fix: add file| SRC_CODEX
    SRC_SVC -.->|Option B fix: add file| SRC_CODEX

    style ERR fill:#e63946,color:#fff
    style SRC_CONFIG fill:#f4a261,color:#000
    style SRC_SVC fill:#f4a261,color:#000
```

---

## 11. Security + Token Delegation

> **Updated S873 (2026-05-08)** — T-01 fix: `workflow-link-validation.yml` now uses canonical token chain. TTL read from `COPILOT_SESSION_TTL_SECONDS` repo variable (PR #4356).

```mermaid
flowchart TD
    subgraph "Token Sources"
        MK[CODEX_MASTER_KEY\nfull repo access]
        BK[CODEX_BACKUP_KEY\nrotation backup]
        GT[GITHUB_TOKEN\nworkflow scope]
    end

    subgraph "Token Chain (T-01 Fixed — PR #4356)"
        CHAIN["GH_TOKEN = CODEX_MASTER_KEY\n|| CODEX_BACKUP_KEY\n|| github.token\nAll checkout + write ops"]
        T01_NOTE["⚠️ Before T-01 fix: workflow-link-validation.yml\nused bare github.token — now uses chain"]
    end

    subgraph "Session TTL Control (PR #4356)"
        TTL_VAR[COPILOT_SESSION_TTL_SECONDS\nrepo variable · default 43200]
        TTL_NOTE["Set to 3600 once CI stable\nNo workflow edit required"]
    end

    subgraph "Agent Auth Delegation"
        AAD[agent-auth-delegation.yml\nREQ-4 gate]
        AUTH_CHECK{COPILOT_AGENT_AUTH_ENABLED\n== 'true'?}
        ALLOWED{Actor in\nCOGNITIVE_BRAIN_ALLOWED_ACTORS?}
    end

    subgraph "Allowed Actors"
        MB[mbaetiong]
        GA[github-actions bot]
        CS[copilot-swe-agent bot]
        GH[github-copilot bot]
    end

    subgraph "Protected Operations"
        MANIFEST[CODEX_MANIFEST.json updates]
        BASELINE[.secrets.baseline updates]
        REPORT[AGENT_ACCOUNTABILITY_REPORT.md]
    end

    subgraph "Variables & Secrets Knowledge Layer"
        VARS_REF[docs/reference/\nGITHUB_VARIABLES_SECRETS_REFERENCE.md\n7 upstream sources · all scopes]
        CB_REF[.codex/docs/\nGITHUB_API_AND_MCP_REFERENCE.md\nCognitive Brain knowledge entry]
        VAR_TEST[scripts/ci/test_variables_api.py\nlive token validation + variable CRUD]
        VAR_WRITER[agent-var-writer.yml\nallowlist: 13 variables\n@agent-var-writer apply]
    end

    MK & BK --> CHAIN
    GT --> CHAIN
    CHAIN --> AAD
    TTL_VAR --> AAD
    AAD --> AUTH_CHECK
    AUTH_CHECK -->|yes| ALLOWED
    ALLOWED --> MB & GA & CS & GH
    MB & CS -->|can write| MANIFEST & BASELINE & REPORT
    MK -->|CODEX_MASTER_KEY required| VAR_TEST
    VAR_TEST -->|reads scopes allowlist| VARS_REF
    VARS_REF --> CB_REF
    MK -->|write ops| VAR_WRITER

    style CHAIN fill:#e8f5e9,color:#000
    style T01_NOTE fill:#fff3e0,color:#000
    style TTL_VAR fill:#e1f5fe,color:#000
    style TTL_NOTE fill:#e1f5fe,color:#000
    style VARS_REF fill:#e1f5fe,color:#000
    style CB_REF fill:#e1f5fe,color:#000
    style VAR_TEST fill:#e8f5e9,color:#000
    style VAR_WRITER fill:#e8f5e9,color:#000
```

---

## 12. Source Layout

```mermaid
graph TD
    subgraph "src/codex/ — Python Package"
        CLI2[cli.py\nEntry point]
        CAPS[capabilities/\nci_test, monitoring,\nusage_logger]
        CONFIG2[config/\napp config]
        SERVICES[services/\nAPI clients]
        UTILS[utils/\npath_utils,\nhash_table]
        LOGGING[logging/\nsession_logger,\nviewer]
        AGENTS2[agents/\nAutoAgent,\nActionProposer]
    end

    subgraph "tests/"
        T_CAPS[capabilities/\nci_test/]
        T_UNIT[unit/]
        T_INTEG[integration/]
        CONF[conftest.py\nsys.path guard P19]
    end

    subgraph "scripts/"
        CI_SCRIPTS[ci/\nauto_fix_common_issues.py\ncheck_pr_comments.py\nsync_tracked_files.py\ntest_variables_api.py ← PR #3876]
        COG_SCRIPTS[cognitive/\ntopology_manager.py\ncache_manager.py]
    end

    CLI2 --> CAPS & CONFIG2 & SERVICES
    UTILS --> CAPS
    LOGGING --> AGENTS2
    T_CAPS --> CAPS
    T_UNIT --> UTILS & CONFIG2
    CONF -->|sys.path fix| T_CAPS & T_UNIT
    CI_SCRIPTS -->|reads| T_CAPS
    COG_SCRIPTS -->|indexes| CLI2
```

---

*All diagrams render on GitHub markdown. Use [Mermaid Live Editor](https://mermaid.live) for offline preview.*

*Previously: S228 + PR #3876 · 2026-04-05 — Section 11 expanded; Section 12 updated with test_variables_api.py*

---

## 13. Autonomous Privilege Architecture

> **Added S867 (PR #4356)** — Full reference: `docs/plans/AUTONOMOUS_PRIVILEGE_ARCHITECTURE.md`

```mermaid
graph TD
    subgraph "5 Autonomy Surfaces"
        WEC[WEC Checklist\nworkflow-execution-gate.yml\nArms workflows per checkbox]
        AAD2[Agent Auth Delegation\nagent-auth-delegation.yml\nPre-authorises token write ops]
        DISCUSS[GitHub Discussions\nAsync command channel\n@agent-* triggers]
        WHK2[Webhook Event Bus\nwebhook_config.json\n4 hooks active=true]
        VARS2[Variable Control Plane\nagent-var-writer.yml\n13-var allowlist]
    end

    subgraph "Zero Human Gate Loop"
        PUSH2[git push] --> GATE[WEC Gate\nparse checklist]
        GATE -->|armed| AUTO_APPROVE[auto-approve-workflows.yml\nApproves action_required]
        AUTO_APPROVE --> DELEGATE[agent-auth-delegation.yml\nIssue session token\nTTL=COPILOT_SESSION_TTL_SECONDS]
        DELEGATE --> AGENT_OPS[Copilot Agent\nfull write ops]
        AGENT_OPS -->|report_progress| PUSH2
    end

    subgraph "Privilege Routing"
        CODEX_MK[CODEX_MASTER_KEY\nrepo+workflow+actions:write]
        BACKUP_KEY[CODEX_BACKUP_KEY\nrotation fallback]
        COPILOT_AUTH[COPILOT_AGENT_AUTH_ENABLED=true\nPERMANENT - no expiry]
    end

    CODEX_MK -->|write ops| AGENT_OPS
    BACKUP_KEY -->|fallback| AGENT_OPS
    COPILOT_AUTH -->|pre-authorises| DELEGATE
    WEC & AAD2 & DISCUSS & WHK2 & VARS2 -->|compose| AGENT_OPS

    style WEC fill:#e8f5e9,color:#000
    style COPILOT_AUTH fill:#e8f5e9,color:#000
    style AGENT_OPS fill:#e3f2fd,color:#000
    style CODEX_MK fill:#fff3e0,color:#000
```

---

## 14. Rate-Limit Orchestration Flow

> **Added S867 (PR #4356)** — Script: `scripts/ci/rate_limit_orchestrator.py`

```mermaid
flowchart TD
    subgraph "CLI Entry Points"
        CLI_CAP[cancel-superseded\ncancel all but latest run per workflow]
        CLI_CHECK[check-rate-limit\nall tokens report]
        CLI_TRICKLE[trickle-dispatch\nqueued workflows with backoff]
    end

    subgraph "_gh_api_with_retry()"
        REQ[HTTP request to GitHub API]
        STATUS{HTTP status}
        RETRY[Retry backoff\n2^attempt capped at 64s\nattempt up to 6]
        LAST[return last_status last_result\non exhaustion - PR 4356 fix]
    end

    subgraph "check_rate_limit_status()"
        TOKEN_LOOP[for each token GET /rate_limit]
        CRITICAL{remaining under 10?}
        CRIT_STATUS[overall_status = critical\nCaller decides abort or sleep]
        OK_STATUS[overall_status = ok]
    end

    subgraph "cancel_superseded_runs()"
        LIST[GET /repos/../actions/runs page-by-page]
        KEEP{--keep-latest or --no-keep-latest\nBooleanOptionalAction - PR 4356 fix}
        CANCEL[POST /runs/ID/cancel]
    end

    CLI_CAP --> cancel_superseded_runs
    CLI_CHECK --> check_rate_limit_status
    CLI_TRICKLE --> REQ
    REQ --> STATUS
    STATUS -->|429 or 5xx| RETRY
    STATUS -->|success| RETURN[return status result]
    RETRY -->|exhausted| LAST
    TOKEN_LOOP --> CRITICAL
    CRITICAL -->|yes| CRIT_STATUS
    CRITICAL -->|no| OK_STATUS
    LIST --> KEEP
    KEEP --> CANCEL

    style LAST fill:#fff3e0,color:#000
    style CRIT_STATUS fill:#fff3e0,color:#000
```

---

## 15. Session Handoff State Machine

> **Added S867 (PR #4356)** — Full doc: `docs/plans/COPILOT_SESSION_HANDOFF_DESIGN.md`

```mermaid
stateDiagram-v2
    [*] --> Idle

    Idle --> Acquiring: maintainer push or copilot continue
    Acquiring --> Active: agent-auth-delegation issues token TTL=COPILOT_SESSION_TTL_SECONDS

    Active --> Wrapping: session objectives complete or TTL approaching
    Wrapping --> Committed: report_progress push P-045 gate passed

    Committed --> Idle: copilot-agent-session-done.yml fires

    Active --> SelfHealing: CI failure detected
    SelfHealing --> Active: fix applied iterative-self-healing-ci.yml

    Active --> Escalating: all auto-fix patterns exhausted
    Escalating --> Active: maintainer approves re-dispatches

    Committed --> [*]: PR merged
```

---

## 16. Phase 9 — Cognitive Brain Autonomous Ops

> **Added S867–S873 (PR #4356)**

```mermaid
graph LR
    subgraph "Phase 9 Completed"
        P9A[12 problem-statement diffs S867]
        P9B[T-01 token chain fix S867]
        P9C[rate_limit_orchestrator.py S867]
        P9D[Session TTL repo var S867]
        P9E[Secrets baseline clean S867 to S870]
        P9F[31 docs archived S870]
        P9G[8 of 8 review comments S871 to S872]
        P9H[Living docs updated S868 to S873]
        P9I[CODEBASE_MERMAID_MAPS updated S873]
    end

    subgraph "Phase 9 Pending"
        P9J[10 vars deploy post-merge @agent-var-writer]
        P9K[4 webhooks deploy post-merge @agent-infra]
        P9L[T-03 security_events admin @mbaetiong]
        P9M[TTL tighten to 3600 once CI stable]
    end

    subgraph "Phase 10 Next"
        P10A[Phase 8.3 Adaptive Learning 80 to 100 percent]
        P10B[Phase 8.4 Transfer Learning planned]
        P10C[Archive 5 merge-candidate CI docs]
        P10D[Webhook event bus triggers]
    end

    P9A & P9B & P9C & P9D & P9E --> P9J
    P9F & P9G & P9H & P9I --> P9K
    P9J & P9K & P9L & P9M --> P10A & P10B & P10C & P10D

    style P9A fill:#e8f5e9,color:#000
    style P9B fill:#e8f5e9,color:#000
    style P9C fill:#e8f5e9,color:#000
    style P9D fill:#e8f5e9,color:#000
    style P9E fill:#e8f5e9,color:#000
    style P9F fill:#e8f5e9,color:#000
    style P9G fill:#e8f5e9,color:#000
    style P9H fill:#e8f5e9,color:#000
    style P9I fill:#e8f5e9,color:#000
    style P9J fill:#fff3e0,color:#000
    style P9K fill:#fff3e0,color:#000
    style P9L fill:#fce4ec,color:#000
    style P9M fill:#e1f5fe,color:#000
```

---

*All diagrams render on GitHub markdown. Use [Mermaid Live Editor](https://mermaid.live) for offline preview.*

*Updated: S873 + PR #4356 · 2026-05-08 — Sections 4 and 11 refreshed; Sections 13-16 added. See CHANGELOG.md for full details.*

# 🗺️ Codebase-Wide Mermaid Architecture Maps

> **Version:** 1.4.1 (S1292a · 2026-06-03)  
> **Updated:** 2026-06-03  
> **Purpose:** Single reference for ALL architectural mermaid diagrams across `Aries-Serpent/_codex_`  
> **Policy:** Per `CODEBASE_AGENCY_POLICY.md §0` — agents must consult this file during pre-flight  
> **Previous:** v1.3.0 S1259 · 2026-05-23

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
13. [Autonomous Privilege Architecture](#13-autonomous-privilege-architecture)
14. [Rate-Limit Orchestration Flow](#14-rate-limit-orchestration-flow)
15. [Session Handoff State Machine](#15-session-handoff-state-machine)
16. [Phase 9 — Cognitive Brain Autonomous Ops](#16-phase-9--cognitive-brain-autonomous-ops)
17. [Phase 10 — Post-Coverage Maintenance](#17-phase-10--post-coverage-maintenance)
18. [Phase 10 Progress — Coverage Expansion ⭐ NEW](#18-phase-10-progress--coverage-expansion)

---

## 1. Repository Overview

```mermaid
%%{init: {'accessibility': {'title': 'Flowchart showing src/codex/\nPython package, tests/\n2,130 test files'}}%%
graph TD
    subgraph "Aries-Serpent/_codex_ — Repository Structure"
        SRC[src/codex/\nPython package]
        TESTS[tests/\n2,130 test files]
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
%%{init: {'accessibility': {'title': 'Flowchart showing git push to branch, PR review submitted'}}%%
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
%%{init: {'accessibility': {'title': 'Flowchart showing feature branch\ncopilot/XXX, PR #NNNN'}}%%
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
%%{init: {'accessibility': {'title': 'Flowchart showing SQLiteMemory\nSTM → LTM\n80% capacity trigger, TopologyManager\nsemantic nav'}}%%
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
%%{init: {'accessibility': {'title': 'Flowchart showing Repository Variables\nNODE_JS_VERSION\nCODEX_CACHE_VERSION\nCOPILOT_RUNNER_PROFILE\nCODEX_CI_FAILURE_*, Agents Variables\nCOPILOT_AGENT_*\nCOPILOT_WEC_*\nCOGNITIVE_BRAIN_*'}}%%
graph LR
    subgraph "Configuration Surfaces"
        REPOV[Repository Variables\nNODE_JS_VERSION\nCODEX_CACHE_VERSION\nCOPILOT_RUNNER_PROFILE\nCODEX_CI_FAILURE_*]
        AGENTV[Agents Variables\nCOPILOT_AGENT_*\nCOPILOT_WEC_*\nCOGNITIVE_BRAIN_*]
        ORGS[Org / Repo Secrets\nCODEX_MASTER_KEY\nCODEX_BACKUP_KEY\n_GITHUB_APP_*]
        SETUP[.github/workflows/\ncopilot-setup-steps.yml\nruns-on → ubuntu-latest fallback\ncache → v2]
    end

    subgraph "Runtime Exports"
        ENVX[CODEX_ENV=copilot-agent]
        LOGX[CODEX_LOG_LEVEL=INFO]
        DBX[CODEX_DB_PATH=$GITHUB_WORKSPACE/.codex/codex.db]
        LOGDB[CODEX_LOG_DB_PATH\n.codex/session_logs.db default]
    end

    subgraph "Agent Families"
        CIA[CI / Self-Healing Agents\nci-testing-agent\nautonomous-test-healer-agent\nself-healing-orchestrator-agent]
        WFA[Workflow / Orchestration Agents\nworkflow-compliance-guardian\nworkflow-ci-fixer\nagent-orchestrator]
        CBA[Cognitive Brain Agents\ncognitive-brain-session-injector\nmemory-sync-agent\nsession-analysis-agent]
        SCA[Security / Compliance Agents\nsecurity-audit-agent\nsecret-detection-agent\npii-scrubber]
    end

    REPOV --> SETUP
    AGENTV --> CIA & WFA & CBA & SCA
    ORGS --> SETUP
    SETUP --> ENVX & LOGX & DBX
    REPOV --> LOGDB
    ENVX --> SCA
    LOGX --> CIA & CBA
    DBX --> CBA
    LOGDB --> CIA & CBA
    REPOV --> CIA & WFA
    WFA -->|routes / validates| CIA & CBA & SCA
```

---

## 6. Workflow Execution Gate

```mermaid
%%{init: {'accessibility': {'title': 'Flowchart showing agent-auth-delegation.yml\ncognitive-preflight wrap-up, Inject Workflow Execution\nChecklist into PR body'}}%%
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
%%{init: {'accessibility': {'title': 'Flowchart showing scripts/ci/check_pr_comments.py\n--pr PR_NUMBER, 🚨 BLOCKING\nmbaetiong + critical bots'}}%%
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
%%{init: {'accessibility': {'title': 'State Diagram showing *, skip ci'}}%%
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
%%{init: {'accessibility': {'title': 'Flowchart showing Define session\nobjectives, Select workflows\nto execute'}}%%
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
%%{init: {'accessibility': {'title': 'Flowchart showing src/codex/\n__init__.py\nconfig/\nservices/, src/codex/config/\nopenai_client.py ❌ MISSING'}}%%
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
%%{init: {'accessibility': {'title': 'Flowchart showing CODEX_MASTER_KEY\nfull repo access, CODEX_BACKUP_KEY\nrotation backup'}}%%
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
%%{init: {'accessibility': {'title': 'Flowchart showing cli.py\nEntry point, capabilities/\nci_test, monitoring,\nusage_logger'}}%%
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
%%{init: {'accessibility': {'title': 'Flowchart showing WEC Checklist\nworkflow-execution-gate.yml\nArms workflows per checkbox, Agent Auth Delegation\nagent-auth-delegation.yml\nPre-authorises token write ops'}}%%
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
%%{init: {'accessibility': {'title': 'Flowchart showing cancel-superseded\ncancel all but latest run per workflow, check-rate-limit\nall tokens report'}}%%
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
%%{init: {'accessibility': {'title': 'State Diagram showing *, *'}}%%
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

> **Added S867–S873 (PR #4356) · Completed S1259 (2026-05-23)**

```mermaid
%%{init: {'accessibility': {'title': 'Flowchart showing 12 problem-statement diffs S867, T-01 token chain fix S867'}}%%
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
        P9J[Phase 9.1 — public API + class API tests S1259]
        P9K[Phase 9.2 — CLI smoke + coverage rollup S1259]
        P9L[Phase 9.3 — error-path coverage 50 new tests S1259]
        P9M[Phase 9.4 — edge-case coverage 71 new tests S1259]
    end

    subgraph "Phase 10 In Progress"
        P10A[Coverage maintenance gate — 17.57% overall baseline S1292]
        P10B[Fill src/ coverage gaps — security 90.72% ✅ S1292]
        P10C[Update all living docs to v1.4.0 baseline S1292]
        P10D[Adaptive Learning Phase 8.3 80 to 100 percent]
        P10E[ITA service coverage tests added ✅ S1292]
        P10F[MSP Gateway coverage tests added ✅ S1292]
    end

    P9A & P9B & P9C & P9D & P9E --> P9J
    P9F & P9G & P9H & P9I --> P9K
    P9J & P9K & P9L & P9M --> P10A & P10B & P10C & P10D & P10E & P10F

    style P9A fill:#e8f5e9,color:#000
    style P9B fill:#e8f5e9,color:#000
    style P9C fill:#e8f5e9,color:#000
    style P9D fill:#e8f5e9,color:#000
    style P9E fill:#e8f5e9,color:#000
    style P9F fill:#e8f5e9,color:#000
    style P9G fill:#e8f5e9,color:#000
    style P9H fill:#e8f5e9,color:#000
    style P9I fill:#e8f5e9,color:#000
    style P9J fill:#e8f5e9,color:#000
    style P9K fill:#e8f5e9,color:#000
    style P9L fill:#e8f5e9,color:#000
    style P9M fill:#e8f5e9,color:#000
    style P10A fill:#fff3e0,color:#000
    style P10B fill:#e8f5e9,color:#000
    style P10C fill:#e8f5e9,color:#000
    style P10D fill:#e1f5fe,color:#000
    style P10E fill:#e8f5e9,color:#000
    style P10F fill:#e8f5e9,color:#000
```

---

## 17. Phase 10 — Post-Coverage Maintenance

> **Added S1259 (2026-05-23) · Updated S1292 (2026-05-28)**

```mermaid
%%{init: {'accessibility': {'title': 'Flowchart showing Overall statements: 17.57%, src/security/: 90.72% ✅'}}%%
graph TD
    subgraph "Coverage Baseline (S1292 — 2026-05-28)"
        CB1[Overall statements: 17.57%]
        CB2[src/security/: 90.72% ✅]
        CB3[Test files: 2,130]
        CB4[Phase 9+10 tests added: 196+ ITA MSP training security]
    end

    subgraph "Phase 10A — Regression Gate"
        RG1[unified-coverage-agent monitors threshold]
        RG2[CI fail_under = 80 in pyproject.toml]
        RG3[fragile-test-guardian detects flakiness]
        RG4[Coverage delta reported on every PR]
    end

    subgraph "Phase 10B — Gap Fill: src/ — In Progress"
        GF1[src/codex/cli.py — CLI command coverage ⏳]
        GF2[src/codex/cognitive_brain/ — brain ops ⏳]
        GF3[src/training/ — trainer loops ⏳]
        GF4[src/codex/rag/ — retrieval paths ⏳]
        GF5[src/security/ — auth + secrets ✅ 90.72%]
        GF6[services/ita/ — ITA service ✅]
        GF7[services/msp_gateway/ — MSP Gateway ✅]
        GF8[Target: 25% overall statements milestone]
    end

    subgraph "Phase 10C — Documentation Alignment"
        DA1[CODEBASE_MERMAID_MAPS v1.4.0 ✅ S1292]
        DA2[ARCHITECTURE.md metrics refresh ✅ S1292]
        DA3[docs/diagrams/*.mmd updated ✅ S1292]
        DA4[AGENT_NAVIGATION.md — Phase 10 agents ⏳]
        DA5[.codex/cognitive_brain/ status update ⏳]
    end

    subgraph "Phase 10D — Adaptive Learning"
        AL1[Phase 8.3: QEC k₁ tuning 80 to 100%]
        AL2[Phase 8.4: Transfer Learning scaffold]
        AL3[Cognitive Brain pattern harvest from Phase 9]
        AL4[memory-sync-agent STM→LTM consolidation]
    end

    CB1 & CB2 & CB3 & CB4 --> RG1 & RG2 & RG3 & RG4
    RG1 & RG2 & RG3 & RG4 --> GF1 & GF2 & GF3 & GF4 & GF5 & GF6 & GF7
    GF1 & GF2 & GF3 & GF4 & GF5 & GF6 & GF7 --> GF8
    GF8 --> DA1 & DA2 & DA3 & DA4 & DA5
    DA1 & DA2 & DA3 --> AL1 & AL2 & AL3 & AL4

    style CB1 fill:#fff3e0,color:#000
    style CB2 fill:#e8f5e9,color:#000
    style CB3 fill:#e8f5e9,color:#000
    style CB4 fill:#e8f5e9,color:#000
    style DA1 fill:#e8f5e9,color:#000
    style DA2 fill:#e8f5e9,color:#000
    style DA3 fill:#e8f5e9,color:#000
    style RG1 fill:#fff3e0,color:#000
    style RG2 fill:#fff3e0,color:#000
    style RG3 fill:#fff3e0,color:#000
    style RG4 fill:#fff3e0,color:#000
    style GF1 fill:#e3f2fd,color:#000
    style GF2 fill:#e3f2fd,color:#000
    style GF3 fill:#e3f2fd,color:#000
    style GF4 fill:#e3f2fd,color:#000
    style GF5 fill:#e8f5e9,color:#000
    style GF6 fill:#e8f5e9,color:#000
    style GF7 fill:#e8f5e9,color:#000
    style GF8 fill:#e3f2fd,color:#000
    style DA4 fill:#e1f5fe,color:#000
    style DA5 fill:#e1f5fe,color:#000
    style AL1 fill:#fce4ec,color:#000
    style AL2 fill:#fce4ec,color:#000
    style AL3 fill:#fce4ec,color:#000
    style AL4 fill:#fce4ec,color:#000
```

---

## 18. Phase 10 Progress — Coverage Expansion

> **Updated S1293 (2026-05-28)**

```mermaid
%%{init: {'accessibility': {'title': 'Flowchart showing Security module: src/security/\n90.72% coverage ✅, ITA service tests\ntests/services/ita/ ✅'}}%%
graph LR
    subgraph "Completed in S1292"
        S1A[Security module: src/security/\n90.72% coverage ✅]
        S1B[ITA service tests\ntests/services/ita/ ✅]
        S1C[MSP Gateway tests\ntests/services/msp_gateway/ ✅]
        S1D[Training module tests\ntests/training/ targeted ✅]
        S1E[Docs + mermaid maps\nv1.4.0 refresh ✅]
    end

    subgraph "Completed in S1293"
        P1[src/codex/cognitive_brain/\nbrain ops coverage 76.92% ✅]
        P2[src/codex/cli.py\nCLI CliRunner smoke tests ✅]
        P3[src/codex/rag/\nFAISS-mocked retriever + indexer ✅]
        P4[src/training/trainer.py\nmixed-precision + checkpoint hooks ✅]
        P5[Adaptive Learning Phase 8.3\nk₁ Bayesian tuning from PDA ✅]
        P6[AGENT_NAVIGATION.md + agent_context.json\nPhase 10 agents registered ✅]
        P7[CI rate_limit_orchestrator.py\ncancel_superseded_runs hardened ✅]
    end

    subgraph "Phase 11 — Production Hardening"
        N1[Coverage zero-gaps\nokr_tracker.py + task_router.py 0% ⏳]
        N2[Cognitive depth\nknowledge_distiller + objective_adjuster 58% ⏳]
        N3[CodeQL + bandit clean run\nzero open findings ⏳]
        N4[Placeholder audit\nno unreachable TODO/FIXME in prod ⏳]
        N5[Overall ≥25% statement coverage\nmilestone gate ⏳]
        N6[RAG retrieval integration tests\nend-to-end corpus round-trip ⏳]
    end

    S1A & S1B & S1C & S1D & S1E --> P1 & P2 & P3 & P4
    P1 & P2 & P3 & P4 & P5 & P6 & P7 --> N1 & N2 & N3 & N4
    N1 & N2 & N3 & N4 --> N5 --> N6

    style S1A fill:#e8f5e9,color:#000
    style S1B fill:#e8f5e9,color:#000
    style S1C fill:#e8f5e9,color:#000
    style S1D fill:#e8f5e9,color:#000
    style S1E fill:#e8f5e9,color:#000
    style P1 fill:#e8f5e9,color:#000
    style P2 fill:#e8f5e9,color:#000
    style P3 fill:#e8f5e9,color:#000
    style P4 fill:#e8f5e9,color:#000
    style P5 fill:#e8f5e9,color:#000
    style P6 fill:#e8f5e9,color:#000
    style P7 fill:#e8f5e9,color:#000
    style N1 fill:#e3f2fd,color:#000
    style N2 fill:#e3f2fd,color:#000
    style N3 fill:#fce4ec,color:#000
    style N4 fill:#fff3e0,color:#000
    style N5 fill:#fff3e0,color:#000
    style N6 fill:#e3f2fd,color:#000
```

---

## Continuation Prompts

> One tailored prompt per component requiring ongoing work. Use these to resume work in a new session.
> **Phase 10 items below are COMPLETED (S1293).** Phase 11 prompts follow.

### ✅ DONE — Coverage: `src/codex/cognitive_brain/` (S1293)
> OODAOrchestrator, SharedMemory, PatternLibrary tests added. `tests/cognitive/test_ooda_meta_learning_coverage.py`

### ✅ DONE — Coverage: `src/codex/cli.py` (S1293)
> CliRunner smoke + branch tests. `tests/codex/test_cli_click_lightweight_smoke.py`

### ✅ DONE — Coverage: `src/codex/rag/` (S1293)
> FAISS-mocked indexer, retriever, embedding cache. `tests/rag/test_rag_faiss_mocked_units.py`

### ✅ DONE — Coverage: `src/training/trainer.py` (S1293)
> Mixed-precision + checkpoint hooks. `tests/unit/test_trainer_checkpoint_hooks_phase10.py`

### ✅ DONE — Adaptive Learning QEC k₁ Tuning Phase 8.3 (S1293)
> Bayesian tuning from pda_iterations.jsonl. `src/cognitive_brain/quantum/adaptive_scoring.py`

### ✅ DONE — AGENT_NAVIGATION.md + .codex status (S1293)
> Phase 10 agents registered. `.codex/AGENT_NAVIGATION.md`, `.codex/agent_context.json`

### ✅ DONE — CI superseded-run cancellation hardening (S1293)
> `cancel_superseded_runs()` wrapper with `--keep-latest` default. `scripts/ci/rate_limit_orchestrator.py`

---

## Phase 11 Continuation Prompts

> Target: ~100% production readiness — zero CodeQL/security findings, no placeholder code, overall ≥25% statement coverage.

### 🔴 P11-SEC: CodeQL + Bandit clean run
```
You are continuing Phase 11 security hardening on Aries-Serpent/_codex_.
Context: CodeQL open findings must reach zero before production gate.
Task:
1. Run bandit scan: bandit -r src/ -ll -ii -x src/codex/rag/,src/security/ --format json > reports/bandit_phase11.json
2. Review open CodeQL alerts via GitHub MCP (list_code_scanning_alerts)
3. Fix any CWE-078 (os.system), CWE-089 (SQLi), CWE-601 (open redirect) in src/
4. Re-run bandit; assert exit code 0
5. Run: python -m pytest tests/security/ --cov=src/security --cov-report=term-missing -q
6. Update docs/CODEBASE_MERMAID_MAPS.md Section 18 N3 node to ✅
Constraints: No suppression comments unless a true false-positive with justification.
```

### 🔴 P11-PLACEHOLDER: Audit TODO/FIXME/placeholder in production code
```
You are continuing Phase 11 code hardening on Aries-Serpent/_codex_.
Context: Production code must contain no unintentional TODO/FIXME stubs or NotImplementedError raises.
Task:
1. grep -r "TODO\|FIXME\|raise NotImplementedError\|pass  # placeholder" src/ > reports/placeholder_audit.txt
2. For each hit: either implement the stub, convert to a logged warning, or add an explicit @pytest.mark.skip
3. Verify no new test failures: python -m pytest tests/ -q --tb=no -x
4. Update docs/CODEBASE_MERMAID_MAPS.md Section 18 N4 node to ✅
Constraints: Do NOT delete test stubs — only production src/ paths.
```

### 🔵 P11-COV-ZERO: Close 0%-coverage modules
```
You are continuing Phase 11 coverage work on Aries-Serpent/_codex_.
Context: Two modules remain at 0% coverage from the S1293 cognitive run.
Files: src/codex/cognitive/okr_tracker.py (141 stmts, 0%), src/codex/cognitive/task_router.py (104 stmts, 0%)
Task: Add targeted tests to reach ≥60% on each file.
Constraints:
- Use tests/cognitive/ directory
- Mock all external I/O (DB, HTTP)
- Do NOT alter existing tests
- Run: python -m pytest tests/cognitive/ --cov=src/codex/cognitive --cov-report=term-missing -q
- Update docs/CODEBASE_MERMAID_MAPS.md Section 18 N1 node to ✅
```

### 🔵 P11-COV-DEPTH: Raise low-coverage cognitive modules to ≥75%
```
You are continuing Phase 11 coverage depth work on Aries-Serpent/_codex_.
Context: Several cognitive modules are at 58–69% coverage after S1293.
Files (current → target):
  src/codex/cognitive/knowledge_distiller.py     58% → 75%
  src/codex/cognitive/objective_adjuster.py      58% → 75%
  src/codex/cognitive/session_hook.py            69% → 80%
  src/codex/cognitive/retrieval_optimizer.py     69% → 80%
Task: Add gap-filling tests for each module.
Constraints:
- Use tests/cognitive/ directory
- Run: python -m pytest tests/cognitive/ --cov=src/codex/cognitive --cov-report=term-missing -q
- Update docs/CODEBASE_MERMAID_MAPS.md Section 18 N2 node to ✅
```

### 🔵 P11-COV-MILESTONE: Reach overall ≥25% statement coverage
```
You are driving the Phase 11 overall coverage milestone on Aries-Serpent/_codex_.
Context: Current overall coverage baseline is 17.57% (S1292). Target: 25%.
Task:
1. Run: python -m pytest tests/ --cov=src --cov-report=term-missing -q > reports/coverage_phase11.txt
2. Identify top-10 uncovered modules by statement count
3. Add targeted tests for the top-3 modules not already in the P11 backlog
4. Re-run coverage; assert ≥25%
5. Update docs/CODEBASE_MERMAID_MAPS.md Section 18 N5 node to ✅
```

### 🟡 P11-RAG-E2E: RAG end-to-end corpus round-trip test
```
You are continuing Phase 11 RAG integration work on Aries-Serpent/_codex_.
Context: Unit tests with FAISS mocks exist (S1293). Full corpus round-trip is not yet tested.
Task:
1. Read src/codex/rag/indexer.py and src/codex/rag/retriever.py
2. Write an integration test that indexes a 5-document corpus and queries it
3. Use pytest tmp_path for index persistence; skip if faiss not installed
4. Run: python -m pytest tests/rag/ --cov=src/codex/rag --cov-report=term-missing -q
5. Update docs/CODEBASE_MERMAID_MAPS.md Section 18 N6 node to ✅
```

---

*All diagrams render on GitHub markdown. Use [Mermaid Live Editor](https://mermaid.live) for offline preview.*

*Updated: S1293 · 2026-05-28 — v1.5.0: Phase 10 items fully completed (cognitive brain 76.92%, CLI, RAG, trainer, k₁ tuning, agent nav, CI dedup); Phase 11 hardening prompts added (CodeQL clean, placeholder audit, 0%-coverage modules, ≥25% overall milestone, RAG E2E).*

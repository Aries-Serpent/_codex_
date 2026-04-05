# 🗺️ Codebase-Wide Mermaid Architecture Maps

> **Version:** 1.1.0 (S228 + PR #3876)  
> **Updated:** 2026-04-05  
> **Purpose:** Single reference for ALL architectural mermaid diagrams across `Aries-Serpent/_codex_`  
> **Policy:** Per `CODEBASE_AGENCY_POLICY.md §0` — agents must consult this file during pre-flight

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

```mermaid
graph TD
    subgraph "Cognitive Brain Core (.codex/)"
        SM[SQLiteMemory\nSTM → LTM]
        TM[TopologyManager\nsemantic nav]
        OT[ObjectivesTracker\nphase goals]
        PL[PatternLibrary\nfix patterns]
        QEC[QEC Decision Engine\nk₁=0.332]
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
    SM -->|compress STM→LTM| SM
    SM --> TM & OT & PL
    PL --> QEC
    QEC --> HEAL_OUT & OODA
    OT --> PDA_OUT
    TM --> STATUS
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

```mermaid
flowchart TD
    subgraph "Token Sources"
        MK[CODEX_MASTER_KEY\nfull repo access]
        BK[CODEX_BACKUP_KEY\nrotation backup]
        GT[GITHUB_TOKEN\nworkflow scope]
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

    subgraph "Variables & Secrets Knowledge Layer (PR #3876)"
        VARS_REF[docs/reference/\nGITHUB_VARIABLES_SECRETS_REFERENCE.md\n7 upstream sources · all scopes]
        CB_REF[.codex/docs/\nGITHUB_API_AND_MCP_REFERENCE.md\nCognitive Brain knowledge entry]
        VAR_TEST[scripts/ci/test_variables_api.py\nlive token validation + variable CRUD\ndispatch via test-variables-api.yml]
    end

    MK & BK --> AAD
    GT --> AAD
    AAD --> AUTH_CHECK
    AUTH_CHECK -->|yes| ALLOWED
    ALLOWED --> MB & GA & CS & GH
    MB & CS -->|can write| MANIFEST & BASELINE & REPORT
    MK -->|CODEX_MASTER_KEY required| VAR_TEST
    VAR_TEST -->|reads scopes allowlist| VARS_REF
    VARS_REF --> CB_REF

    style VARS_REF fill:#e1f5fe,color:#000
    style CB_REF fill:#e1f5fe,color:#000
    style VAR_TEST fill:#e8f5e9,color:#000
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

*Updated: S228 + PR #3876 · 2026-04-05 — Section 11 expanded with Variables & Secrets Knowledge Layer; Section 12 updated with test_variables_api.py*

# Completion Governance Framework

This framework closes the remaining Phase 2-4 governance gaps by defining the score inputs, required artifacts, and explicit completion checks used for remediation validation.

## Assigned-agent completion validation

The assigned-agent completion requirement is tracked in `.codex/config/completion_governance.json`.

Validated completed agents:

- `phase1-gap-discovery` → `recon-scout-agent`
- `phase2-agent-assignment` → `agent-orchestrator`
- `phase3-completion-gate` → `qa-walkthrough-agent`

These agent records must remain `completed` before any Phase 2-4 completion gate is treated as valid.

## Governance inputs

The governance inputs file defines:

- per-phase score thresholds
- required audit artifacts
- baseline regression settings
- assigned-agent completion status

Current phase thresholds:

| Phase | Threshold | Extra requirement |
| --- | --- | --- |
| Phase 2 Stabilisation | `0.70` | `audit_artifacts/capabilities_scored.json` |
| Phase 3 Hardening | `0.85` | gap artifacts present |
| Phase 4 Completion Governance | `0.90` | no regression beyond `0.02` vs baseline |

## Workflow gate

Use `.github/workflows/completion-governance-gates.yml` to run the explicit completion gate.

Supported runs:

- `phase-2-stabilisation`
- `phase-3-hardening`
- `phase-4-completion-governance`
- `score-regression`
- `all`

## Validation sequence

1. Validate assigned-agent completion.
2. Generate the required audit artifacts.
3. Enforce the configured threshold for the selected phase.
4. Enforce regression limits when a baseline is configured.
5. Report a complete/partial/incomplete outcome from the selected gate run.

---

## Governance Lifecycle & Score Journey

```mermaid
flowchart LR
    subgraph SCORE["Score Journey"]
        S0["60.8%\nFunctional\nrisk-heavy\n2026-05-27"]
        S1["76.4%\nOperational\nneeds hardening\n2026-05-27 ✅"]
        S2["85.6%\nOperational\nhardened\n2026-06-17"]
        S3["90.4%\nProduction\nneeds polish\n2026-07-08"]
        S4["~95%\nProduction\nComplete\n2026-Q3"]
    end

    subgraph CB["Cognitive Brain Feeds"]
        CB1["workflow_patterns.jsonl\n373 patterns"]
        CB2["SQLiteMemory STM→LTM"]
        CB3["all_agents_completed\nCODEX_MANIFEST.json"]
    end

    subgraph GATES["Phase Gates\n(completion-governance-gates.yml)"]
        G2["Phase 2 Gate\nthreshold: 0.70\n✅ PASSED 76.4%"]
        G3["Phase 3 Gate\nthreshold: 0.85\ncapabilities_scored.json\ngaps.json"]
        G4["Phase 4 Gate\nthreshold: 0.90\naudit_run_manifest.json\nno regression >0.02"]
    end

    S0 --> S1 --> S2 --> S3 --> S4
    CB1 --> G3
    CB2 --> G3
    CB3 --> G3 & G4

    G2 --> S1
    S1 --> G3
    G3 --> S2
    S2 --> G4
    G4 --> S3
    S3 -->|"D10+D11+D2 polish"| S4

    style S0 fill:#e63946,color:#fff
    style S1 fill:#457b9d,color:#fff
    style S2 fill:#2a9d8f,color:#fff
    style S3 fill:#2d6a4f,color:#fff
    style S4 fill:#e9c46a,color:#000
    style CB fill:#7b2d8b,color:#fff
    style GATES fill:#f4a261,color:#000
```

---

## Assigned-Agent Phase Map

```mermaid
flowchart TD
    subgraph PHASE2["Phase 2 ✅ COMPLETE"]
        PA1["tracking-document-qa-agent\nRubric owner"]
        PA2["codebase-health-guardian\nD1 Architecture"]
        PA3["unified-security-scanner\nD5 Security"]
        PA4["agent-orchestrator\nD3 Orchestration"]
        PA5["rag-freshness-loop-agent\nD4 RAG"]
        PA6["workflow-health-monitor\nD6 CI/CD"]
        PA7["unified-coverage-agent\nD7 Tests"]
        PA8["performance-monitor-agent\nD8 Observability"]
        PA9["unified-doc-agent\nD9 Docs"]
    end

    subgraph PHASE3["Phase 3 — 2026-06-17"]
        PB1["ml-validation-suite-agent\nD2 ML Lifecycle"]
        PB2["cognitive-brain-session-injector\nD3 Backup / OODA"]
        PB3["workflow-compliance-guardian\nD6→5 CI gate"]
        PB4["fragile-test-guardian\nD7→5 Mutation"]
    end

    subgraph PHASE4["Phase 4 — 2026-07-08"]
        PC1["rag-index-manager\nD4→5 Quality nightly"]
        PC2["codebase-health-guardian\nD1→5 Arch layers"]
        PC3["msv-dashboard-monitor\nD8→5 SLO canary"]
    end

    PHASE2 --> PHASE3 --> PHASE4

    style PHASE2 fill:#2d6a4f,color:#fff
    style PHASE3 fill:#457b9d,color:#fff
    style PHASE4 fill:#9d4edd,color:#fff
```

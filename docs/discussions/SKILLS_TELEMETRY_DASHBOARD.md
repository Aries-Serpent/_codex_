# 📊 Skills Telemetry Dashboard

> **Category:** Autonomous Agentic Agency — Telemetry
> **Status:** ✅ Active | **Last Updated:** 2026-04-02T11:35:00Z | **Session:** S277
> **Owner:** skills-master-agent v1.0.0
> **Data Source:** `logs/skill_events.jsonl` via `codex-skill telemetry push`

---

## Overview

This dashboard tracks the Cognitive Brain Skills Registry telemetry: skill invocations,
AAIS quality scores, routing decisions, budget consumption, and agent-to-skill mappings.
It is designed to be updated in-place (upserts) by the Skills Master agent after each session.

---

## 🗺️ Skills-to-Agent Mapping

```mermaid
graph LR
    subgraph "Built-in Skills"
        S1["doc.retriever.core\nv1.0.0"]
        S2["doc.refresh.agent\nv1.0.0"]
        S3["code.search.extract\nv1.0.0"]
    end

    subgraph "CI/CD Agents"
        A1[ci-testing-agent]
        A2[ci-auto-healer-agent]
        A3[ci-failure-resolution-agent]
        A4[ci-emergency-response-agent]
        A5[ci-log-retrieval-agent]
        A6[ci-pattern-guardian]
        A7[ci-optimization-agent]
        A8[ci-health-alert-agent]
        A9[ci-triage-pipeline-agent]
    end

    subgraph "Testing Agents"
        B1[autonomous-test-healer-agent]
        B2[unified-coverage-agent]
        B3[test-failure-analyzer-agent]
        B4[test-enhancement-agent]
        B5[fragile-test-guardian]
        B6[mutation-testing-agent]
    end

    subgraph "Documentation Agents"
        C1[post-merge-doc-alignment-agent]
        C2[documentation-quality-agent]
        C3[doc-freshness-checker]
        C4[link-validator-agent]
        C5[unified-doc-agent]
    end

    subgraph "Security Agents"
        D1[security-audit-agent]
        D2[codeql-alert-resolution-agent]
        D3[code-scanning-remediation-agent]
        D4[secret-detection-agent]
        D5[dependency-vulnerability-scanner]
    end

    subgraph "RAG/ML Agents"
        E1[rag-index-manager]
        E2[meta-tensor-validator]
        E3[rag-meta-tensor-guardian]
        E4[rag-module-management-agent]
    end

    subgraph "Orchestration"
        F1[skills-master-agent]
        F2[agent-orchestrator]
        F3[self-healing-orchestrator-agent]
    end

    S1 --> C1 & C2 & C3 & F1
    S2 --> C1 & C3 & C5 & F1
    S3 --> A1 & A2 & B1 & B3 & F1
    F1 --> S1 & S2 & S3
```

---

## 📋 Skill Registry Status

| Skill ID | Version | AAIS | Risk | Calls Budget | Tokens Budget | Status | Agent Consumers |
|----------|---------|------|------|-------------|--------------|--------|-----------------|
| `doc.retriever.core` | 1.0.0 | 0.92 | 🟢 low | 1,000 | 200K | ✅ Active | doc-alignment, doc-quality, skills-master |
| `doc.refresh.agent` | 1.0.0 | 0.90 | 🟡 medium | 200 | 500K | ✅ Active | doc-alignment, freshness-checker, skills-master |
| `code.search.extract` | 1.0.0 | 0.88 | 🟡 medium | 500 | 150K | ✅ Active | ci-testing, test-healer, skills-master |

---

## 🎯 AAIS Scores — Radar Chart

```mermaid
%%{init: {'theme': 'base', 'themeVariables': {'primaryColor': '#4CAF50'}}}%%
graph TD
    subgraph "AAIS Breakdown — doc.retriever.core (0.92)"
        DR_C["Concision: 0.85"]
        DR_A["Acronym: 0.95"]
        DR_S["Structure: 1.00"]
        DR_CL["Clarity: 0.90"]
        DR_CI["Citation: 0.80"]
    end

    subgraph "AAIS Breakdown — doc.refresh.agent (0.90)"
        RF_C["Concision: 0.82"]
        RF_A["Acronym: 0.93"]
        RF_S["Structure: 1.00"]
        RF_CL["Clarity: 0.88"]
        RF_CI["Citation: 0.80"]
    end

    subgraph "AAIS Breakdown — code.search.extract (0.88)"
        CS_C["Concision: 0.80"]
        CS_A["Acronym: 0.90"]
        CS_S["Structure: 0.90"]
        CS_CL["Clarity: 0.88"]
        CS_CI["Citation: 0.80"]
    end
```

---

## 🔄 Stratified Routing — Scoring Formula

```mermaid
flowchart LR
    Q["Query Objective\n+ Capability Tags"] --> MATCH["Match Score\n(Jaccard similarity)"]
    Q --> FRESH["Freshness Score\n(1 − budget exhaustion)"]

    MATCH --> |"w=0.40"| TOTAL
    FRESH --> |"w=0.15"| TOTAL
    AAIS["AAIS Score\n(doc quality)"] --> |"w=0.25"| TOTAL
    COST["Cost Penalty\n(token usage %)"] --> |"w=−0.10"| TOTAL
    RISK["Risk Penalty\n(tier: low/med/high)"] --> |"w=−0.10"| TOTAL

    TOTAL["Total Score\n= Σ(w × dim)"] --> SELECT["Select\nHighest Score"]
    SELECT --> EXEC["ExecutionEnvelope\n.run()"]
```

---

## 🔀 Fusion Merge Options — Agent Consolidation Recommendations

The Skills Master recommends these fusion merges based on overlapping capability_tags, shared
consumers, and complementary execution patterns. Percentage = recommendation confidence.

| Merge Candidate A | Merge Candidate B | Overlap | Recommendation % | Status | Rationale |
|---|---|---|---|---|---|
| `ci-failure-resolution-agent` | `ci-testing-agent` | 85% tags | **95%** ✅ | ✅ Merged (v4.0) | Already absorbed — identical fix patterns |
| `ci-emergency-response-agent` | `ci-testing-agent` | 80% tags | **92%** ✅ | ✅ Merged (v4.0) | Emergency = critical subset of CI triage |
| `coverage-gapfill-agent` | `unified-coverage-agent` | 90% tags | **98%** ✅ | ✅ Deprecated | Gap-fill is a sub-workflow of unified |
| `coverage-maintenance-agent` | `unified-coverage-agent` | 88% tags | **96%** ✅ | ✅ Deprecated | Maintenance folded into unified |
| `test-coverage-agent` | `unified-coverage-agent` | 92% tags | **97%** ✅ | ✅ Deprecated | Monitoring folded into unified |
| `doc-freshness-checker` | `post-merge-doc-alignment-agent` | 65% tags | **72%** 🟡 | 📋 Review | Freshness check is a subset of alignment loop |
| `ci-auto-healer-agent` | `self-healing-orchestrator-agent` | 70% tags | **78%** 🟡 | 📋 Review | Auto-healer handles patterns; orchestrator coordinates |
| `rag-meta-tensor-guardian` | `meta-tensor-validator` | 75% tags | **80%** 🟡 | 📋 Review | Guardian + validator = complementary checks |
| `link-validator-agent` | `doc-freshness-checker` | 55% tags | **60%** 🟠 | ⏳ Future | Link validation + freshness = two angles on doc quality |
| `security-audit-agent` | `unified-security-scanner` | 60% tags | **68%** 🟠 | ⏳ Future | Audit = manual; scanner = automated |

---

## 📈 Telemetry Flow

```mermaid
flowchart TD
    SKILL["Skill Handler\n(handler.py)"] --> ENV["ExecutionEnvelope\n.run()"]
    ENV --> TEL["emit_event()"]
    TEL --> JSONL["logs/skill_events.jsonl"]
    TEL --> OTEL["OpenTelemetry Span\n(when SDK available)"]
    JSONL --> READ["read_events()"]
    READ --> SUM["summarise_events()"]
    SUM --> DASH["📊 This Dashboard\n(update via upsert)"]
    SUM --> APP["Cognitive Brain App\npush_to_app()"]
    SUM --> GH["GitHub Discussions\n(telemetry category)"]
```

---

## 🏗️ Agent Lifecycle Pipeline

```mermaid
stateDiagram-v2
    [*] --> Discovery: registry.discover()
    Discovery --> Scoring: AAISScorer.score()
    Scoring --> GapAnalysis: identify AAIS < 0.75
    GapAnalysis --> DocRefresh: doc.refresh.agent
    DocRefresh --> ReScore: re-score AAIS
    ReScore --> PassGate: AAIS ≥ 0.80?
    PassGate --> Compress: Yes → compress_skill()
    PassGate --> DocRefresh: No → re-apply refresh
    Compress --> Distribute: install_skill()
    Distribute --> EmitTelemetry: emit_event()
    EmitTelemetry --> UpdateRegistry: store patterns
    UpdateRegistry --> RetireCheck: budget exhausted?
    RetireCheck --> Retire: Yes → archive agent
    RetireCheck --> [*]: No → active
    Retire --> Retrain: design replacement
    Retrain --> [*]
```

---

## 📊 Budget Consumption — Per Skill

| Skill ID | Calls Used | Calls Budget | % Used | Tokens Used | Tokens Budget | % Used | Status |
|----------|-----------|-------------|--------|------------|--------------|--------|--------|
| `doc.retriever.core` | 0 | 1,000 | 0% | 0 | 200,000 | 0% | 🟢 Fresh |
| `doc.refresh.agent` | 0 | 200 | 0% | 0 | 500,000 | 0% | 🟢 Fresh |
| `code.search.extract` | 0 | 500 | 0% | 0 | 150,000 | 0% | 🟢 Fresh |

> Budget resets at the start of each policy window. Updated by `ExecutionEnvelope.run()`.

---

## 🔍 Gap Analysis — Skills Coverage

### Covered Capabilities

| Capability | Skill | Coverage |
|-----------|-------|----------|
| Document retrieval | `doc.retriever.core` | ✅ Full |
| Document refresh | `doc.refresh.agent` | ✅ Full |
| Code search | `code.search.extract` | ✅ Full |
| AAIS scoring | `codex.skills.aais` (module) | ✅ Full |
| Telemetry | `codex.skills.telemetry` (module) | ✅ Full |
| Compression | `codex.skills.compression` (module) | ✅ Full |

### Identified Gaps — Candidate New Skills

| Gap | Proposed Skill ID | Priority | Status |
|-----|------------------|----------|--------|
| Test failure pattern matching | `test.failure.matcher` | 🔴 High | 📋 Planned |
| CI workflow health analysis | `ci.health.analyzer` | 🔴 High | 📋 Planned |
| Dependency vulnerability scan | `security.dep.scanner` | 🟡 Medium | 📋 Planned |
| RAG index rebuild | `rag.index.rebuild` | 🟡 Medium | 📋 Planned |
| Agent AAIS batch scorer | `agent.aais.batch` | 🟢 Low | 📋 Planned |

---

## 🔄 Retrain / Retire Plan

### Retirement Criteria

An agent or skill is a **retirement candidate** when:
1. Budget exhaustion ≥ 90% with no refresh
2. AAIS score drops below 0.60 after 2 consecutive scoring cycles
3. Fusion merge with a higher-capability agent is approved
4. No invocations for 30+ days

### Currently Retired / Deprecated

| Agent | Retired Date | Absorbed By | Reason |
|-------|-------------|-------------|--------|
| `ci-failure-resolution-agent` | 2026-03-15 | `ci-testing-agent v4.0` | Full merge |
| `ci-emergency-response-agent` | 2026-03-15 | `ci-testing-agent v4.0` | Full merge |
| `coverage-gapfill-agent` | 2026-03-21 | `unified-coverage-agent` | Consolidation |
| `coverage-maintenance-agent` | 2026-03-21 | `unified-coverage-agent` | Consolidation |
| `coverage-roadmap-agent` | 2026-03-21 | `unified-coverage-agent` | Consolidation |
| `test-coverage-agent` | 2026-03-21 | `unified-coverage-agent` | Consolidation |
| `test-coverage-monitor` | 2026-03-21 | `unified-coverage-agent` | Consolidation |

### Retrain Queue

| Agent | Current AAIS | Target AAIS | Retrain Method | ETA |
|-------|-------------|-------------|----------------|-----|
| — | — | — | — | No agents currently queued |

> Retrain is triggered when AAIS < 0.75. The Skills Master redesigns the agent
> following the Agent Design Protocol (ADP) in `skills-master-agent.md`.

---

## 🛠️ CLI Quick Reference

```bash
# Discover all skills
codex-skill list

# Score a specific skill
codex-skill score --skill doc.retriever.core --emit dist/aais_score.json

# Run a skill
codex-skill run doc.retriever.core --payload '{"query": "AAIS scoring", "top_k": 5}'

# Compress for distribution
codex-skill compress --skill doc.retriever.core --format 7z --out dist/

# Push telemetry summary
codex-skill telemetry push --from logs/skill_events.jsonl --to file --summary

# Refresh docs
codex-skill refresh-docs --paths docs/ --style aais --prune-stale
```

---

## 📝 Update Protocol

This dashboard is updated by the **Skills Master agent** using the PDA Loop:

1. **PLAN:** Run `registry.discover()` + `AAISScorer.score()` on all skills
2. **DO:** Execute doc-refresh, compress, emit telemetry, update tables above
3. **ASSESS:** Re-score, compare AAIS deltas, update fusion merge recommendations

**To update:** `@copilot Use skills-master-agent to update the telemetry dashboard`

---

> **Document Version:** 1.0.0 | **Format:** GitHub Discussions–compatible Markdown
> **Rendering:** Mermaid diagrams render natively on GitHub

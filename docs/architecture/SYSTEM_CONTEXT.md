# System Context Diagram (C4 Context)
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Last Updated**: 2026-01-20
**Version**: v0.2.1
**Reference**: [5-Layer Architecture](5_LAYER_ARCHITECTURE.md)

---

## Context Level Overview

The Aries-Serpent/_codex_ system operates within a broader ecosystem of users and external systems:

```mermaid
%%{init: {'accessibility': {'title': 'System Context Diagram<br/>Users and External Systems'}, 'theme': 'base'}}%%

graph TB
    subgraph "External Systems"
        GH["🐙 GitHub<br/>PR Management<br/>Issue Tracking<br/>Workflows"]
        ZD["🎫 Zendesk<br/>Support Tickets<br/>Customer Data<br/>CRM Integration"]
        HF["🤗 Hugging Face<br/>Model Hub<br/>Model Weights<br/>Community Models"]
        MLFLOW[" MLflow<br/>Experiment Tracking<br/>Model Registry<br/>Artifacts"]
        S3["☁️ Cloud Storage<br/>S3/GCS/Azure<br/>Model Storage<br/>Data Backup"]
        BENCH[" Benchmark<br/>Services<br/>Performance Tracking<br/>Leaderboards"]
    end

    subgraph "Aries-Serpent/_codex_ System"
        CORE[" Core Platform<br/>Training<br/>Evaluation<br/>Serving<br/>RAG Pipeline"]
        AGENTS[" Agent System<br/>161 Autonomous Agents<br/>Task Orchestration<br/>Execution Engine"]
        BRAIN[" Cognitive Brain<br/>OODA Loops<br/>Quantum Orchestration<br/>Decision Making"]
        INFRA[" Infrastructure<br/>Config Management<br/>Database<br/>Monitoring<br/>Caching"]
    end

    subgraph "Users"
        DEV["👨‍💻 ML Engineers<br/>Model Development<br/>Experimentation<br/>Training"]
        DS[" Data Scientists<br/>Feature Engineering<br/>Data Analysis<br/>EDA"]
        OPS[" DevOps/SRE<br/>Deployment<br/>Monitoring<br/>Operations"]
        LEAD["👔 Team Leads<br/>Progress Tracking<br/>Resource Planning<br/>Governance"]
    end

    %% User interactions with system
    DEV -->|"CLI Commands<br/>API Calls"| CORE

    DEV -->|"Configure<br/>Trigger"| AGENTS

    DS -->|"Query<br/>Analyze"| INFRA

    OPS -->|"Deploy<br/>Monitor"| INFRA

    LEAD -->|"Metrics<br/>Reports"| BRAIN

    %% System internal flows
    CORE -->|"Execute<br/>Tasks"| AGENTS

    AGENTS -->|"Request<br/>Context"| BRAIN

    BRAIN -->|"Decision<br/>Feedback"| AGENTS

    CORE -->|"Persist<br/>State"| INFRA

    AGENTS -->|"Log<br/>Metrics"| INFRA

    %% External system integrations
    CORE -.->|"Push Models<br/>Pull Weights"| HF
    AGENTS -.->|"PR/Issue<br/>Actions"| GH
    BRAIN -.->|"Support<br/>Tickets"| ZD
    CORE -.->|"Track<br/>Experiments"| MLFLOW
    INFRA -.->|"Store<br/>Retrieve"| S3
    AGENTS -.->|"Upload<br/>Results"| BENCH

    %% Styling
    style DEV fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#000
    style DS fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#000
    style OPS fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#000
    style LEAD fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#000

    style CORE fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#000
    style AGENTS fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#000
    style BRAIN fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#000
    style INFRA fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#000

    style GH fill:#f3e8ff,stroke:#7c3aed,stroke-width:2px,color:#000
    style ZD fill:#f3e8ff,stroke:#7c3aed,stroke-width:2px,color:#000
    style HF fill:#f3e8ff,stroke:#7c3aed,stroke-width:2px,color:#000
    style MLFLOW fill:#f3e8ff,stroke:#7c3aed,stroke-width:2px,color:#000
    style S3 fill:#f3e8ff,stroke:#7c3aed,stroke-width:2px,color:#000
    style BENCH fill:#f3e8ff,stroke:#7c3aed,stroke-width:2px,color:#000
```

---

## System Responsibilities

### Core Platform
- **Training**: Model training with hyperparameter tuning
- **Evaluation**: Metric computation and benchmark execution
- **Serving**: Inference and prediction pipelines
- **RAG**: Vector indexing and semantic retrieval

### Agent System
- **Task Orchestration**: Route and coordinate work
- **Autonomous Execution**: Run tasks without human intervention
- **Error Recovery**: Self-healing and resilience
- **Feedback Loop**: Learn from outcomes

### Cognitive Brain
- **OODA Loops**: Observe Orient Decide Act
- **Pattern Recognition**: Identify recurring issues
- **Decision Making**: Choose optimal actions
- **Quantum Orchestration**: Coordinate complex workflows

### Infrastructure
- **Configuration**: Hydra-based setup and secrets
- **Database**: Session and checkpoint persistence
- **Monitoring**: Metrics, logs, alerts, dashboards
- **Caching**: Results, models, embeddings

---

## User Types & Interactions

| User Type | Primary Interactions | Key Workflows |
|-----------|-------------------|---------------|
| **ML Engineers** | CLI, API, training | Develop models, run experiments, deploy |
| **Data Scientists** | Query tools, analysis | Feature engineering, data analysis, EDA |
| **DevOps/SRE** | Deployment, monitoring | Production deployment, system health |
| **Team Leads** | Dashboards, reports | Progress tracking, resource planning |

---

## External System Integrations

| System | Purpose | Direction | Frequency |
|--------|---------|-----------|-----------|
| **GitHub** | PR automation, workflows | Bidirectional | Per-commit |
| **Zendesk** | Support ticket sync | Bidirectional | Per-ticket |
| **Hugging Face** | Model sharing | Bidirectional | Per-release |
| **MLflow** | Experiment tracking | Unidirectional () | Per-run |
| **Cloud Storage** | Model/data persistence | Bidirectional | On-demand |
| **Benchmarks** | Performance tracking | Unidirectional () | Per-release |

---

## Key Boundary Crossings

### Incoming (Users System)
1. **CLI Commands** - User runs `codex train --config config.yaml`
2. **API Calls** - Programmatic model requests: `POST /api/predict`
3. **GitHub Triggers** - PR opened Automated checks
4. **Configuration Changes** - Update `configs/` System reloads

### Outgoing (System External)
1. **Model Upload** - Push trained models to Hugging Face
2. **PR Comments** - Agent post findings to GitHub PR
3. **Support Tickets** - Update customer issues in Zendesk
4. **Metrics Upload** - Submit benchmark results
5. **Artifact Storage** - Save models/data to cloud storage

---

## Architecture Context

This C4 Context diagram represents **Level 1** of the C4 model:

```
Level 1: System Context (this diagram)
  ↓
Level 2: Containers (see 5-Layer Architecture)
  ↓
Level 3: Components (see individual layer docs)
  ↓
Level 4: Code (see source files)
```

---

## Next Steps

- See [5-Layer Architecture](5_LAYER_ARCHITECTURE.md) for internal layer structure
- See [End-to-End Request Flow](E2E_REQUEST_FLOW.md) for request lifecycle
- See [Component Dependencies](COMPONENT_DEPENDENCIES.md) for module relationships

---

**Related Documentation**:
- [ARCHITECTURE.md](./INDEX.md) - Full architecture documentation
- [5-Layer Architecture](5_LAYER_ARCHITECTURE.md) - Internal system layers
- Check the integration documentation in the repository for external system integration details

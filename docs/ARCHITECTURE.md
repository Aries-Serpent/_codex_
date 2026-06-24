# ⚠️ ARCHIVED: Consolidated Architecture Document Available

> **Status**: ARCHIVED - Please use the consolidated document instead
> **Redirect Target**: [`docs/architecture/ARCHITECTURE_CONSOLIDATED.md`](./architecture/ARCHITECTURE_CONSOLIDATED.md)
> **Reason**: This content has been merged into a single authoritative architecture reference
> **Last Updated**: 2026-06-22

---

## 🔗 Documentation Update

This document has been **consolidated** with `Architecture.md` and `ARCHITECTURE_BLUEPRINT.md` into a single comprehensive reference:

### **→ [Read the Consolidated Architecture](./architecture/ARCHITECTURE_CONSOLIDATED.md)**

All content from this document is now available in the consolidated version with:
- ✅ Unified system context and container architecture
- ✅ Complete component documentation
- ✅ repository structure guides
- ✅ Deployment patterns
- ✅ Cross-references to all guides

---

## Historical Content (Preserved for Reference)

The original content below is preserved for historical purposes only. **Please refer to the consolidated document for current architecture information.**

---

# Codex ML Architecture (v0.1.0) - ARCHIVED

> **Version**: v0.1.0 Pre-Release
> **Last Updated**: 2026-05-28
> **Status**: Archived - See Consolidated Version
> **Managed By**: AI Assistant Autonomous System

**AI-Managed repository Notice**: This repository is designed for and managed by AI Assistants and Agents. All architectural decisions, reviews, and updates are performed autonomously by AI systems.

**Package Name**: `codex-ml` (PyPI/Distribution) | repository: `_codex_`

This document provides a comprehensive architectural overview of the `_codex_` ML training, evaluation, and plugin framework using C4-lite modeling. **(See consolidated version for updates)**

## Table of Contents
- <!-- TODO: Add section or remove TOC entry - [System Context]() -->
- <!-- TODO: Add section or remove TOC entry - [Container Architecture]() -->
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Operational Concerns](#operational-concerns)
- [Technology Choices](#technology-choices)
- [Roadmap](#roadmap)
- [Architecture Decision Records](#architecture-decision-records)

---

## System Context (current)

The Codex ML system provides a comprehensive framework for ML model training, evaluation, and deployment with emphasis on reproducibility, observability, and extensibility. It includes the MCP ecosystem, Cognitive Brain system, and 145 active autonomous agents.

<!-- METRICS_LAST_UPDATED: 2026-05-28 S1292 Phase 10 progress -->
```mermaid
%%{init: {'accessibility': {'title': 'Diagram showing Data Scientist / ML Engineer<br/>Platform User, GitHub Copilot<br/>AI Coding agent'}}%%
graph TB
    User[Data Scientist / ML Engineer<br/>Platform User]
    Copilot[GitHub Copilot<br/>AI Coding agent]
    Agents[145 Active Autonomous Agents<br/>🤖 MCP-enabled]

    Codex[codex-ml<br/>Production-Ready ML Platform<br/>2,130 Test Files | 17.57% overall cov]

    Brain[Cognitive Brain<br/>k₁=0.35 | 2.86x Advantage<br/>289 patterns learned]
    MCP[MCP System<br/>Model Context Protocol<br/>134 active workflows<br/>298 workflow files incl. stubs]
    Pipeline[Python Ingestion<br/>Ingest → Analyze → Transform → Verify]

    HF[Hugging Face Hub<br/>Models + Datasets]
    MLflow[MLflow Tracking Server<br/>Experiments + Registry]
    Storage[Cloud Storage<br/>S3 / Azure / GCS]
    Compute[GPU Compute<br/>Ray Cluster / Distributed]
    GitHub[GitHub<br/>Actions + PR Automation]

    User -->|Configure & Train| Codex
    Copilot -->|Code Generation & Review| Codex
    Agents -->|Autonomous Operations| Codex

    Codex --> Brain
    Codex --> MCP
    Codex --> Pipeline

    Brain -->|Pattern-guided Decisions| Agents
    MCP -->|Context Protocol| Agents

    Codex -->|Load Models & Data| HF
    Codex -->|Track Experiments| MLflow
    Codex -->|Store Artifacts| Storage
    Codex -->|Distribute Training| Compute
    Codex -->|CI/CD Automation| GitHub

    style Codex fill:#3b82f6,stroke:#fff,stroke-width:4px,color:#fff
    style Brain fill:#8b5cf6,stroke:#fff,stroke-width:3px,color:#fff
    style MCP fill:#10b981,stroke:#fff,stroke-width:3px,color:#fff
    style Agents fill:#f59e0b,stroke:#fff,stroke-width:2px,color:#fff
```

### External Actors (current)

- **Data Scientists / ML Engineers**: Primary users who configure, train, and evaluate models
- **GitHub Copilot**: AI coding agent that autonomously fixes CI failures, fills coverage gaps, and implements features
- **145 Active Autonomous Agents**: Specialized domain agents for testing, documentation, security, and operations
- **CI/CD Systems**: 134 active GitHub Actions workflows (298 workflow files including stubs) for testing, deployment, and self-healing

### External Systems

- **Hugging Face Hub**: Model and dataset repository
- **MLflow**: Experiment tracking and model registry
- **Cloud Storage**: Artifact storage (checkpoints, logs, data) - S3, Azure, GCS
- **Ray Cluster**: Distributed compute for training and serving
- **GitHub**: PR automation, Actions workflows, agent orchestration

---

## Container Architecture (current)

The system is organized into several logical containers (processes or deployable units). Version 0.1.0 introduces MCP system, Cognitive Brain, and autonomous agent orchestration.

```mermaid
%%{init: {'accessibility': {'title': 'Diagram showing CLI Interface<br/>Typer/Click<br/>🔧 Main Entry Point, Training Engine<br/>PyTorch + Transformers<br/>📈 Distributed Training'}}%%
graph TB
    subgraph "codex-ml v0.1.0 System"
        subgraph "Core ML Platform"
            CLI[CLI Interface<br/>Typer/Click<br/>🔧 Main Entry Point]
            Training[Training Engine<br/>PyTorch + Transformers<br/>📈 Distributed Training]
            Eval[Evaluation Engine<br/>lm-eval + custom metrics<br/>📊 2,130 Test Files]
            Serve[Model Serving<br/>Ray Serve + FastAPI<br/>🚀 Production API]
            Config[Configuration<br/>Hydra + OmegaConf<br/>⚙️ Hierarchical]
            Logging[Session Logging<br/>SQLite + Telemetry<br/>📝 Complete Audit]
        end

        subgraph "Cognitive Brain (k₁=0.35)"
            Brain[Decision Engine<br/>Superposition + Entanglement<br/>🧠 2.86x Advantage]
            Memory[Memory Manager<br/>STM/LTM + Patterns<br/>💾 60% Compression]
            Optimizer[Adaptive Scoring<br/>ML-inspired Weights<br/>📈 Self-optimizing]
        end

        subgraph "MCP Ecosystem"
            MCPCore[MCP Core<br/>Model Context Protocol<br/>🔌 Standardized]
            Adapters[Adapters<br/>Pinecone/Mock/Custom<br/>🔗 Extensible]
            Workers[Background Workers<br/>Embeddings + Checkpoints<br/>⚙️ Async]
            Metrics[MCP Metrics<br/>Telemetry + Monitoring<br/>📊 Observability]
        end

        subgraph "Python Ingestion Pipeline"
            Ingest[Ingest Module<br/>File/ZIP/Git/URL<br/>📥 Multi-source]
            Analyze[Analysis Module<br/>AST + Runtime<br/>🔍 Static + Dynamic]
            Transform[Transform Module<br/>Tier A/B/C<br/>🔄 LLM-guided]
            Verify[Verify Module<br/>Behavior Compare<br/>✅ Test Gen]
        end

        subgraph "agent System (145 Active Agents)"
            AgentCore[agent Core<br/>RAG + RAGIndexer<br/>🤖 Autonomous]
            ToolRegistry[Tool Registry<br/>Centralized Discovery<br/>🔧 Dynamic]
            AgentMemory[agent Memory<br/>SQLite Persistent<br/>💾 Pattern Library]
        end

        subgraph "Infrastructure"
            Security[Security Layer<br/>48 CVEs Fixed<br/>🔒 Production]
            CICD[CI/CD Automation<br/>Auto-Fix + Self-Heal<br/>🔧 Time Savings]
            Plugins[Plugin Framework<br/>Dynamic Loading<br/>🔌 Extensible]
        end
    end

    subgraph "External Services"
        MLflow[MLflow Server<br/>Experiments + Registry]
        Storage[Object Storage<br/>S3/Azure/GCS]
        HF[Hugging Face<br/>Models + Datasets]
        GitHub[GitHub<br/>Actions + API]
    end

    %% Core Flow
    CLI --> Config
    CLI --> Training
    CLI --> Eval
    CLI --> Serve
    CLI --> Ingest

    Config -.configures.-> Training
    Config -.configures.-> Eval
    Config -.configures.-> Brain

    Training --> Logging
    Eval --> Logging
    Serve --> Logging

    %% Cognitive Brain
    Brain --> Memory
    Brain --> Optimizer
    AgentCore --> Brain

    %% MCP System
    MCPCore --> Adapters
    MCPCore --> Workers
    MCPCore --> Metrics
    AgentCore --> MCPCore

    %% Pipeline
    Ingest --> Analyze
    Analyze --> Transform
    Transform --> Verify
    CLI --> Ingest

    %% agent System
    AgentCore --> ToolRegistry
    AgentCore --> AgentMemory
    AgentCore --> CICD

    %% Infrastructure
    Security -.protects.-> Training
    Security -.protects.-> MCPCore
    CICD -.automates.-> GitHub
    Plugins -.extends.-> Training

    %% External
    Training --> MLflow
    Eval --> MLflow
    Training --> Storage
    Training --> HF
    Eval --> HF
    AgentCore --> GitHub

    %% Styling
    style CLI fill:#3b82f6,stroke:#1e40af,stroke-width:2px,color:#fff
    style Brain fill:#8b5cf6,stroke:#6d28d9,stroke-width:2px,color:#fff
    style MCPCore fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    style Ingest fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff
    style AgentCore fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff
    style Security fill:#dc2626,stroke:#991b1b,stroke-width:2px,color:#fff
```
    Serve --> HF

    Config -.->|Hydra compose| Training
    Config -.->|Hydra compose| Eval
    Config -.->|Hydra compose| Serve

    Plugins -.->|Extend| Training
    Plugins -.->|Extend| Eval

    style CLI fill:#4a9eff
    style Training fill:#ff6b6b
    style Eval fill:#51cf66
    style Serve fill:#ffd43b
    style Logging fill:#845ef7
    style Config fill:#ff8787
    style Plugins fill:#69db7c
```text

### Container Descriptions

| Container | Technology | Purpose | Dependencies |
|-----------|-----------|---------|--------------|
| **CLI Interface** | Typer, Click | Entry point for all user interactions | Config, Training, Eval, Serve |
| **Training Engine** | PyTorch, Transformers, PEFT, Accelerate | Model training with LoRA/QLoRA support | Config, Logging, MLflow, Storage |
| **Evaluation Engine** | lm-eval, custom metrics | Model evaluation and benchmarking | Config, Logging, HF Hub |
| **Model Serving** | Ray Serve, FastAPI | Production model inference API | Config, Logging, HF Hub |
| **Logging & Telemetry** | SQLite, custom session logger | Conversation tracking, session management | None |
| **Configuration** | Hydra, OmegaConf | Hierarchical configuration management | None |
| **Plugin Framework** | Python importlib | Dynamic plugin loading and extension | Config |

---

## Component Architecture

### Core Components

```mermaid
%%{init: {'accessibility': {'title': 'Diagram showing Trainer<br/>Main orchestrator, DataLoader<br/>Dataset preparation'}}%%
graph TB
    subgraph "Training Engine"
        Trainer[Trainer<br/>Main orchestrator]
        DataLoader[DataLoader<br/>Dataset preparation]
        ModelInit[Model Initializer<br/>Load/create models]
        Optimizer[Optimizer & Scheduler<br/>Training optimization]
        Checkpoint[Checkpoint Manager<br/>Save/resume training]
    end

    subgraph "Evaluation Engine"
        EvalRunner[Evaluation Runner]
        Metrics[Metrics Calculator]
        Benchmarks[Benchmark Suite]
        Reporter[Results Reporter]
    end

    subgraph "Configuration Management"
        HydraConfig[Hydra Config Loader]
        Validator[Config Validator<br/>Pydantic schemas]
        Defaults[Default Configs]
    end

    subgraph "Logging Infrastructure"
        SessionLogger[Session Logger<br/>SQLite backend]
        QueryEngine[Query Engine<br/>Search transcripts]
        Viewer[Log Viewer<br/>CLI interface]
    end

    Trainer --> DataLoader
    Trainer --> ModelInit
    Trainer --> Optimizer
    Trainer --> Checkpoint
    Trainer --> SessionLogger

    EvalRunner --> Metrics
    EvalRunner --> Benchmarks
    EvalRunner --> Reporter
    EvalRunner --> SessionLogger

    HydraConfig --> Validator
    HydraConfig --> Defaults

    style Trainer fill:#ff6b6b
    style EvalRunner fill:#51cf66
    style HydraConfig fill:#ff8787
    style SessionLogger fill:#845ef7
```text

### component Responsibilities

#### Training Engine Components

- **Trainer**: Orchestrates the training loop, manages epochs, batching, and gradient accumulation
- **DataLoader**: Prepares datasets from Hugging Face, local files, or custom sources
- **Model Initializer**: Loads pre-trained models or creates new architectures
- **Optimizer & Scheduler**: Manages learning rate schedules and optimization algorithms
- **Checkpoint Manager**: Handles model checkpointing, resumption, and artifact storage

#### Evaluation Engine Components

- **Evaluation Runner**: Coordinates evaluation tasks across different benchmarks
- **Metrics Calculator**: Computes accuracy, perplexity, BLEU, and custom metrics
- **Benchmark Suite**: Integrates lm-eval and custom evaluation tasks
- **Results Reporter**: Formats and outputs evaluation results

#### Configuration Management

- **Hydra Config Loader**: Composes configurations from multiple sources
- **Config Validator**: Validates configurations using Pydantic schemas
- **Default Configs**: Provides sensible defaults for common scenarios

#### Logging Infrastructure

- **Session Logger**: Records conversation events and training sessions to SQLite
- **Query Engine**: Enables searching through conversation transcripts
- **Log Viewer**: CLI tool for viewing and analyzing logs

---

## Data Flow

### Training Data Flow

```mermaid
%%{init: {'accessibility': {'title': 'Sequence Diagram: >>CLI: Resolved configuration
'}}%%
sequenceDiagram
    participant User
    participant CLI
    participant Config
    participant Trainer
    participant DataLoader
    participant Model
    participant MLflow
    participant Storage

    User->>CLI: Run training command
    CLI->>Config: Load Hydra config
    Config-->>CLI: Resolved configuration
    CLI->>Trainer: Initialize with config
    Trainer->>DataLoader: Load dataset
    DataLoader-->>Trainer: Batched data
    Trainer->>Model: Forward pass
    Model-->>Trainer: Loss
    Trainer->>Trainer: Backward pass & optimize

    loop Every N steps
        Trainer->>MLflow: Log metrics
        Trainer->>Storage: Save checkpoint
    end

    Trainer-->>CLI: Training complete
    CLI-->>User: Results & artifact paths
```text

### Evaluation Data Flow

```mermaid
%%{init: {'accessibility': {'title': 'Sequence Diagram: >>CLI: Resolved configuration
'}}%%
sequenceDiagram
    participant User
    participant CLI
    participant Config
    participant EvalRunner
    participant Model
    participant Benchmarks
    participant Reporter

    User->>CLI: Run evaluation command
    CLI->>Config: Load Hydra config
    Config-->>CLI: Resolved configuration
    CLI->>EvalRunner: Initialize evaluator
    EvalRunner->>Model: Load checkpoint
    EvalRunner->>Benchmarks: Run tasks

    loop For each task
        Benchmarks->>Model: Generate predictions
        Model-->>Benchmarks: Outputs
        Benchmarks->>Benchmarks: Compute metrics
    end

    Benchmarks-->>EvalRunner: Aggregated results
    EvalRunner->>Reporter: Format results
    Reporter-->>CLI: Formatted report
    CLI-->>User: Evaluation results
```text

### Configuration Resolution Flow

```mermaid
%%{init: {'accessibility': {'title': 'Flowchart showing Default Configs<br/>config/, User Overrides<br/>CLI args'}}%%
flowchart LR
    Defaults[Default Configs<br/>config/]
    User[User Overrides<br/>CLI args]
    Env[Environment Variables<br/>CODEX_*]

    Hydra[Hydra Composer]
    Validator[Pydantic Validator]
    Final[Final Config Object]

    Defaults --> Hydra
    User --> Hydra
    Env --> Hydra
    Hydra --> Validator
    Validator --> Final

    style Final fill:#51cf66
```text

---

## Operational Concerns

### Deployment Patterns

#### Local Development
- Run training on local GPU
- Use SQLite for session logging
- Store artifacts locally or in cloud storage

#### Cloud Training
- Distribute training across Ray cluster
- Use MLflow for experiment tracking
- Store artifacts in S3/GCS

#### Model Serving
- Deploy with Ray Serve for horizontal scaling
- FastAPI endpoints for inference
- Health checks and monitoring

### Observability

```mermaid
%%{init: {'accessibility': {'title': 'Flowchart showing Codex ML, Session Logs<br/>SQLite'}}%%
graph LR
    App[Codex ML]

    Logs[Session Logs<br/>SQLite]
    Metrics[MLflow Metrics<br/>Training/Eval]
    Traces[Conversation Traces<br/>Query Engine]

    App --> Logs
    App --> Metrics
    App --> Traces

    Viewer[Log Viewer CLI]
    MLflowUI[MLflow UI]
    QueryCLI[Query CLI]

    Logs --> Viewer
    Metrics --> MLflowUI
    Traces --> QueryCLI

    style App fill:#326ce5,color:#fff
```text

**Logging Levels:**
- Session events (system, user, assistant, tool roles)
- Training metrics (loss, learning rate, throughput)
- Evaluation results (accuracy, perplexity, custom metrics)
- Error tracking and stack traces

**Key Metrics:**
- Training: Loss, learning rate, gradient norm, samples/sec
- Evaluation: Accuracy, F1, perplexity, BLEU
- Infrastructure: GPU utilization, memory usage, I/O throughput

### Security Considerations

- **Secrets Management**: Use environment variables, never commit secrets
- **Input Validation**: Validate all configurations and user inputs
- **Dependency Scanning**: Automated vulnerability scanning via Dependabot
- **Code Analysis**: Bandit for Python security issues

See [SECURITY.md](./SECURITY.md) for vulnerability reporting.

### Scalability

- **Horizontal Scaling**: Ray for distributed training and serving
- **Vertical Scaling**: Multi-GPU support via Accelerate
- **Data Parallelism**: Sharded datasets for large-scale training
- **Model Parallelism**: Support for large models via FSDP/DeepSpeed

### Reliability

- **Checkpointing**: Automatic checkpoint saving and resumption
- **Fault Tolerance**: Ray's fault-tolerant execution
- **Graceful Degradation**: Fallback to CPU if GPU unavailable
- **Validation**: Pydantic-based configuration validation

---

## Technology Choices

### Core Technologies

| Category | Technology | Rationale |
|----------|-----------|-----------|
| **ML Framework** | PyTorch | Industry standard, excellent ecosystem |
| **Transformers** | Hugging Face Transformers | De facto standard for NLP models |
| **Configuration** | Hydra + OmegaConf | Composable configs, CLI overrides |
| **Experiment Tracking** | MLflow | Open-source, model registry, UI |
| **Distributed Compute** | Ray | Scalable, fault-tolerant, Python-native |
| **Model Serving** | Ray Serve + FastAPI | Scalable inference, familiar API patterns |
| **CLI Framework** | Typer | Modern, type-safe, auto-docs |
| **Data Validation** | Pydantic | Type safety, automatic validation |
| **Testing** | pytest | Powerful, extensive plugin ecosystem |
| **Linting** | Ruff + Black + mypy | Fast, comprehensive, type-checked |

### Design Patterns

- **Dependency Injection**: Hydra provides configs to all components
- **Plugin Architecture**: Dynamic loading for extensibility
- **Factory Pattern**: Model and dataset creation
- **Strategy Pattern**: Different training strategies (LoRA, full fine-tuning)
- **Observer Pattern**: Event logging throughout training

---

## Roadmap

### Current Capabilities (v0.1.0)
- ✅ LoRA/QLoRA fine-tuning
- ✅ Hydra-based configuration
- ✅ MLflow experiment tracking
- ✅ Session logging to SQLite
- ✅ CLI interface
- ✅ Evaluation with lm-eval
- ✅ Plugin framework
- ✅ MCP ecosystem (134 active workflows; 298 workflow files including stubs)
- ✅ Cognitive Brain (289 patterns, k₁=0.35)
- ✅ 145 active autonomous agents deployed

### Phase 9 — Completed (2026-05-23)
- ✅ Phase 9.1: agents/ public API + class contract tests
- ✅ Phase 9.2: CLI smoke tests + coverage rollup
- ✅ Phase 9.3: error-path coverage (50 new tests)
- ✅ Phase 9.4: edge-case coverage (71 new tests)
- ✅ Rate-limit orchestrator + session TTL repo var
- ✅ Secrets baseline clean; living docs aligned to v1.3.0

### Phase 10 — Coverage Expansion (Current · S1292 · 2026-05-28)
- ✅ src/security/ coverage raised to 90.72% (S1292)
- ✅ ITA service tests added (tests/services/ita/)
- ✅ MSP Gateway tests added (tests/services/msp_gateway/)
- ✅ Training module targeted tests added (S1292)
- ✅ Documentation + mermaid maps refreshed to v1.4.0 (S1292)
- 🔄 Overall coverage: 17.57% → 25% milestone (in progress)
- 🔄 src/codex/cognitive_brain/ coverage expansion
- 🔄 src/codex/cli.py CLI branch coverage
- 🔄 src/codex/rag/ retrieval path tests
- 🔄 src/training/trainer.py: 12.20% → 50% target
- 📋 Adaptive Learning Phase 8.3: QEC k₁ tuning (80→100%)
- 📋 AGENT_NAVIGATION.md + .codex/cognitive_brain/ status update
- 📋 workflow superseded-run cancellation hardening

### Medium-Term (Phase 11+)
- 📋 Multi-modal support (vision + language)
- 📋 Reinforcement learning from human feedback (RLHF)
- 📋 Model compression and quantization
- 📋 75% → 100% coverage roadmap (Phase 11 final milestone)
- 📋 Enhanced monitoring and alerting

### Long-Term
- 💡 Auto-ML capabilities
- 💡 Federated learning support
- 💡 Edge deployment
- 💡 Advanced privacy-preserving techniques

**Legend**: ✅ Complete | 🔄 In Progress | 📋 Planned | 💡 Under Consideration

---

## Architecture Decision Records

For detailed architectural decisions and their rationale, see:

- [ADR Directory](./decision_records/) - All architecture decision records
- [ADR-0001: Record Architecture Decisions](./decision_records/0001-record-architecture-decisions.md) - Meta-ADR about the ADR process

### Key Decisions

1. **ADR-0001**: Use Architecture Decision Records for documenting significant decisions
2. **Use Hydra for Configuration**: Enables composable, overridable configurations
3. **SQLite for Session Logging**: Lightweight, local-first, queryable logs
4. **Ray for Distribution**: Python-native, supports both training and serving
5. **Plugin-Based Extensibility**: Allow users to extend without forking

---

## Fence Validation Architecture (Legacy)

> **Note**: This section documents the fence validation tooling used for Markdown quality checks.

The `tools/validate_fences.py` traverses Markdown inputs and surfaces fence issues for local contributors.

### component Overview

- **Target discovery (`iter_files`)**: Walks requested roots while skipping generated locations
- **Line preparation (`_prepare_line`)**: Strips diff prefixes and indentation
- **Fence analysis (`_scan_file`)**: Maintains `FenceState` metadata to validate symmetry
- **Public entry points**: `validate_file` (Python API), `main` (CLI)

```mermaid
%%{init: {'accessibility': {'title': 'Flowchart showing CLI or caller, _parse_args + _gather_targets'}}%%
flowchart TD
    A[CLI or caller] -->|argv / path list| B[_parse_args + _gather_targets]
    B --> C{Targets?}
    C -- none --> D[Emit "[fence-check] No matching files"]
    C -- files --> E[iter_files]
    E --> F[_scan_file]
    F -->|errors| G[[STDOUT error lines]]
    F -->|warnings| H[[STDOUT warning lines]]
    F -->|ok state| I[["[fence-check] OK"]]
```text

### Running Locally

```bash
python -m pip install -r requirements-dev.txt
pytest -q tests/test_validate_fences.py
```

---

## Contributing to Architecture

When proposing architectural changes:

1. **Create an ADR**: Document the decision in `docs/decision_records/`
2. **Update diagrams**: Keep Mermaid diagrams current
3. **AI Assistant autonomous review**: Automated architectural validation and feedback
4. **Update this document**: Reflect changes in this ARCHITECTURE.md
5. **Update related docs**: Keep API docs, guides, and README in sync

---

## References

- [Hugging Face Documentation](https://huggingface.co/docs)
- [Hydra Documentation](https://hydra.cc/)
- [Ray Documentation](https://docs.ray.io/)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [C4 Model](https://c4model.com/)

---

**Questions or suggestions?** Open a discussion or submit for AI Assistant autonomous review


---
## 📎 Consolidated from: docs/Architecture.md

# Architecture: Shim Governance & Canonical Import Policy (v1.2.9)

> Generated: 2025-12-05 | Author: mbaetiong  
> Status: Active | Readiness: 85% → 99% path

🧠 Roles: [Audit Orchestrator], [Capability Cartographer] ⚡ Energy: 5

## Overview

This document defines the governance policy for import shims and canonical module paths during the convergence from split-brain architecture to a unified `src.*` canonical structure.

## Policy Summary

- **Canonical Location**: All runtime modules should ultimately live under `src/`
- **Legacy Shims**: Temporary shims may exist in root paths (e.g., `training/`) during convergence
- **Shim Implementation**: Shims MUST re-export from `src.*` and maintain API equivalence
- **Identity Requirements**: `training.X` must resolve to equivalent functionality as `src.training.X`
- **CI Enforcement**: Strict conflict detection enabled; duplicates allowed only if whitelisted

## Current State (v1.2.9)

### Import Reduction Progress
- **Baseline**: 99 legacy import occurrences
- **Current**: 42 occurrences (57.6% reduction ✅)
- **Tokenization**: 100% migrated to `src.*` (13 → 0)
- **Training**: 79% migrated to `src.*` (53 → 11)
- **Models**: 50% migrated to `src.*` (4 → 2)
- **Hydra**: config_legacy fallbacks (29 preserved for compatibility)

### Shim Architecture

**Active Shims** (as of v1.2.9):
- `src/training/engine_hf_trainer.py` → forwards to `training.engine_hf_trainer`
- `src/training/functional_training.py` → forwards to `training.functional_training`
- `src/training/data_utils.py` → forwards to `training.data_utils`
- `src/training/checkpoint_manager.py` → forwards to `training.checkpoint_manager`
- `src/training/config.py` → forwards to `training.config`
- `src/tokenization/train_tokenizer.py` → forwards to `tokenization.train_tokenizer`

**Shim Pattern**:
```python
"""Canonical import shim for src.training.module_name"""
from importlib import import_module as _im

_mod = _im("training.module_name")
globals().update({k: getattr(_mod, k) for k in dir(_mod) if not k.startswith("_")})
__all__ = [k for k in globals() if not k.startswith("_")]
```

## Governance Rules

### Rule 1: Canonicalization Priority

| Priority | Action | Timeline |
|----------|--------|----------|
| P0 | Migrate high-usage runtime modules to `src/` | Phase 1 (Current Cycle) |
| P1 | Keep minimal, documented shims during transition | Until migration complete |
| P2 | Deprecate and remove shims after migration | Phase 2 (Current Cycle) |

### Rule 2: Shim Requirements
All shims MUST:
- Re-export ALL public APIs from the legacy module
- Maintain API equivalence (validated by `test_shim_equivalence.py`)
- Include deprecation date in `.github/SHIM_INVENTORY.yaml`
- Document rationale and ownership

### Rule 3: CI Gating
- **Strict Mode**: Enabled in CI via `verify_conflicts.py --mode strict`
- **Whitelist**: Duplicates allowed only if listed in `.github/SHIM_INVENTORY.yaml`
- **PR Blocking**: Non-whitelisted duplicates block merge
- **Shim-Aware Mode**: Available for local debugging only

### Rule 4: Decision Gates for Consolidation
Before moving a module from legacy to `src/`:

| Gate | Requirement | Validation |
|------|-------------|------------|
| **Ownership** | Owner approved in SHIM_INVENTORY.yaml | Manual review |
| **Usage Trend** | Legacy imports for module < 10% for 90 iterations | Nightly audit metrics |
| **Test Equivalence** | test_shim_equivalence + full suite PASS | CI validation |
| **No Split-Brain** | verify_conflicts strict shows no violations | CI check |
| **Low Risk** | Affects < 10 tests | Impact analysis |
| **Rollback Ready** | Backup branch + tested rollback script | Pre-consolidation prep |

### Rule 5: Rollback Procedures
Every consolidation PR MUST include:
- Backup branch before changes
- Tested rollback script
- Rollback validation (tests + determinism)
- Documented rollback steps in PR description

## Tooling & Automation

### Inventory Management
```bash
# Generate shim inventory
python scripts/remediation/list_shims.py \
  --roots training src/training tokenization src/tokenization \
  --output .github/SHIM_INVENTORY.yaml
```

## Conflict Detection
```bash
# Strict mode (CI gating)
python scripts/remediation/verify_conflicts.py \
  --mode strict \
  --output audit_artifacts/conflicts.json

# Shim-aware mode (local debugging)
python scripts/remediation/verify_conflicts.py \
  --mode shim-aware \
  --output audit_artifacts/conflicts.json
```

## Equivalence Testing
```bash
# Run shim equivalence tests
pytest -q tests/validation/test_shim_equivalence.py

# Strict identity mode (CI only)
SHIM_IDENTITY_STRICT=1 pytest -q tests/validation/test_shim_equivalence.py
```

## Nightly Audit
- **workflow**: `.github/workflows/nightly-audit.yml`
- **Schedule**: Daily at 02:00 UTC
- **Outputs**: Inventory, conflicts, legacy usage report
- **Alerting**: Auto-creates issue on violations

### Determinism Validation
- **workflow**: `.github/workflows/determinism.yml`
- **Trigger**: Pull requests touching `src/`, `scripts/`, `tests/`, `training/`, `tokenization/`
- **Checks**: Full audit, 2-run determinism, strict conflicts
- **Artifacts**: Uploaded for review

## Path to 99% Readiness

### Current: 85% Ready (v1.2.9)
✅ Split-brain resolved via shims  
✅ All imports work correctly  
✅ CI gating in place  
✅ Inventory and governance established

### Target: 99% Ready (v1.3.0)
Two paths available:

**Option A: Full Consolidation** (99% readiness)
1. Move legacy modules from `training/` → `src/training/`
2. Move legacy modules from `tokenization/` → `src/tokenization/`
3. Update root `__init__.py` files as compatibility shims
4. Remove canonical shim files (no longer needed)
5. Update remaining legacy imports (11 training + 29 hydra)
6. Final validation and baseline update

**Option B: Shim Governance** (85-90% readiness, permanent)
1. Keep shims as architectural pattern
2. Formalize in ADR (Architecture Decision Record)
3. Maintain via inventory and nightly audits
4. System remains operational and maintainable

## References

- **Shim Inventory**: `.github/SHIM_INVENTORY.yaml`
- **Consolidation Playbook**: `.github/CONSOLIDATION_PLAYBOOK.md`
- **Wave 3 Convergence Plan**: `docs/validation/Wave3_SplitBrain_Convergence.md`
- **v1.2.9 Validation Log**: `docs/validation/v1.2.9_Validation_Log.md`
- **v1.3.0 Next Steps**: `.github/copilot_agent_task_prompt_v1.3.0.md`

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| v1.2.9 | 2025-12-05 | mbaetiong | Initial policy definition |

---

**Status**: Active | **Next Review**: Phase 1 (Current Cycle) or upon consolidation decision



---
## 📎 Consolidated from: docs/ARCHITECTURE_BLUEPRINT.md

# repository Architecture Blueprint and Roadmap

**Document Version**: 1.0.0
**Generated**: 2025-12-11
**Branch Context**: `copilot/sub-pr-2459-again`
**Author**: GitHub Copilot with mbaetiong
**Audience**: Developer-Architects, AI Assistants/Agents, DevOps Engineers

---

## Executive Summary

The `_codex_` repository is a Level 4 MLOps-certified, production-grade machine learning framework designed with AI Assistant/agent intuitiveness as a core principle. This blueprint provides an exhaustive technical reference for understanding the repository's architecture, structure, and operational workflows, enabling effective collaboration between human developers and AI agents (GitHub Copilot, ChatGPT 5.1 agent Mode).

### Key Characteristics

- **MLOps Maturity**: Level 4 Certified (100/100 Azure MLOps capabilities)
- **Test Coverage**: 2,079+ test files, 10.7% coverage, 100% pass rate
- **Documentation**: 693+ markdown files, 64KB added in recent PRs
- **Architecture**: Plugin-driven, Hydra-configured, containerized
- **AI Integration**: Native support for Copilot workflows, agent orchestration, tokenized workflows
- **Security**: Zero known vulnerabilities, comprehensive scanning infrastructure
- **Reproducibility**: Deterministic training with RNG checkpointing, environment snapshots

### Purpose and Scope

This blueprint serves multiple audiences:
1. **Human Developers**: Comprehensive onboarding, architecture understanding, contribution guidelines
2. **AI Agents**: Tokenized workflows, structured prompts, automated task execution
3. **DevOps Engineers**: Deployment patterns, CI/CD configuration, infrastructure management
4. **Architects**: System design, integration patterns, scalability considerations

---

## Table of Contents

1. [Repository Structure](#repository-structure)
2. [Architecture Overview](#architecture-overview)
3. [Core Components](#core-components)
4. <!-- BROKEN ANCHOR: [Runtime & Data Flow](#runtime-data-flow) -->
5. <!-- BROKEN ANCHOR: [CI/CD & Testing](#cicd-testing) -->
6. <!-- BROKEN ANCHOR: [Security & Compliance](#security-compliance) -->
7. [AI agent Integration](#ai-agent-integration)
8. <!-- BROKEN ANCHOR: [Deployment & Operations](#deployment-operations) -->
9. [Development Workflows](#development-workflows)
10. <!-- BROKEN ANCHOR: [Roadmap & Priorities](#roadmap-priorities) -->
11. [Appendices](#appendices)

---

## Repository Structure

### Root-Level Organization

```
_codex_/
├── .codex/                      # Codex environment kit & setup scripts
├── .github/                     # CI/CD workflows (gated for cost control)
├── agents/                      # AI agent infrastructure
│   ├── prompts/                 # Pre-defined prompts library
│   ├── workflow_navigator.py   # Tokenized workflow execution
│   └── codex_client/           # Codex-GitHub bridge client
├── src/codex_ml/               # Core ML framework
│   ├── training/               # Training pipelines
│   ├── evaluation/             # Evaluation metrics
│   ├── connectors/             # Storage connectors
│   └── plugins/                # Plugin system
├── scripts/                     # Utility scripts (195+ files)
│   └── space_traversal/        # Audit pipeline v1.5.5
├── tests/                       # Test suite (2,079+ files)
├── docs/                        # Documentation (693+ files)
│   ├── mcp/                    # MCP (Model Context Protocol) docs
│   ├── archive/                # Historical planning docs & session reports
│   ├── api/                    # API reference documentation
│   └── ADMIN_*.md              # Administrator guides
├── reports/                     # Generated reports & diagnostics
│   ├── codex/                  # Codex-specific reports
│   └── diagnostics/            # Diagnostic outputs
├── coverage_reports/            # Test coverage JSON reports
├── training/                    # Training configurations
├── services/                    # Microservices (ITA, etc.)
├── cli/                         # CLI entrypoints
├── configs/                     # Hydra configurations
├── deploy/                      # Deployment manifests
├── monitoring/                  # Observability tools
├── audit_artifacts/            # Audit results & trends
├── misc/                        # Archival & review
│   └── repo-owner-review/      # Deprecated files for owner review
└── [core config files]          # pyproject.toml, requirements*.txt, etc.
```

### Key Directories Deep Dive

#### 1. Core ML Framework (`src/codex_ml/`)

**Purpose**: Central machine learning framework with modular, extensible architecture.

**Structure**:
```
src/codex_ml/
├── training/
│   ├── config.py              # TrainingConfig with gradient accumulation
│   ├── engine_hf_trainer.py   # HuggingFace Trainer integration
│   └── functional_training.py # Functional training pipeline
├── evaluation/
│   └── runner.py              # Evaluation orchestration
├── connectors/
│   └── base.py                # LocalConnector (async, path-validated)
├── plugins/
│   ├── plugin_registry.py     # Plugin system
│   └── plugin_sandbox.py      # Sandboxed plugin execution
├── metrics/
│   └── api.py                 # NDJSON metrics aggregation
└── utils/
    └── stub_cleanup.py        # Stub analysis tool
```

**Key Features**:
- Deterministic training with RNG state management
- Async storage connectors with path traversal protection
- Plugin-based extensibility for models, metrics, trainers
- NDJSON metrics for standardized aggregation

#### 2. AI agent Infrastructure (`agents/`)

**Purpose**: Enable AI Assistant/agent workflows with structured prompts and orchestration.

**Components**:
```
agents/
├── prompts/                    # Prompt library
│   ├── audit/                  # Audit operations
│   ├── debugging/              # Debugging guides (26KB)
│   ├── deployment/             # Deployment workflows
│   ├── documentation/          # Doc generation
│   └── organization/           # repository organization
├── workflow_navigator.py       # Token-based workflow execution
├── physics_orchestrator.py    # Energy-based decision making
├── mental_mapping.py           # Decision tracking
├── TOKENIZED_WORKFLOWS.md     # workflow documentation
└── codex_client/              # API bridge for Codex-GitHub ops
```

**workflow Tokens**:
- `AUDIT_EXEC`: Full audit pipeline execution
- `PHYS_DECIDE`: Physics-inspired decision-making
- `DOC_GEN`: Documentation generation
- `REPO_ORG`: repository organization
- `SELF_HEAL`: Automated feedback loops

#### 3. Audit Pipeline (`scripts/space_traversal/`)

**Purpose**: Deterministic capability tracking and trend analysis (v1.5.5).

**Components**:
```
scripts/space_traversal/
├── audit_runner.py            # Main orchestration
├── trend_database.py          # SQLite trend storage
├── performance.py             # Caching & profiling utilities
├── ci_integration.py          # CI/CD integration
├── migrations/                # Schema migrations
├── viz_html.py                # HTML dashboards
├── viz_ascii.py               # Terminal output
├── viz_swagger.py             # OpenAPI docs
└── viz_docs_hub.py            # Documentation hub
```

**Features**:
- SQLite-based trend tracking with migrations
- Multiple visualization formats (HTML, ASCII, Swagger)
- Webhook notifications (Slack, Teams, generic)
- CI/CD integration (GitHub Actions, GitLab CI, Jenkins)

#### 4. Testing Infrastructure (`tests/`)

**Purpose**: Comprehensive test coverage with multiple strategies.

**Structure**:
```
tests/
├── capabilities/              # Capability-specific tests
├── tokenization/              # Tokenization parity tests
├── space_traversal/           # Audit pipeline tests
├── plugins/                   # Plugin system tests
├── training/                  # Training pipeline tests
└── [2,079+ test files]        # Unit, integration, smoke tests
```

**Test Categories**:
- Unit tests: Individual function/class testing
- Integration tests: component interaction testing
- Smoke tests: Quick sanity checks
- Property-based tests: Hypothesis-driven testing
- Capability tests: Feature-specific validation

---

## Architecture Overview

### High-Level System Architecture

```mermaid
%%{init: {'accessibility': {'title': 'Flowchart showing "👥 Users", Developers'}}%%
flowchart TB
    subgraph Users["👥 Users"]
        Dev[Developers]
        agent[AI Agents]
        CI[CI/CD Systems]
    end

    subgraph Core["🔷 Codex Core"]
        CLI[CLI Interface]
        Logging[Session Logger]
        Config[Configuration]
    end

    subgraph Pipeline["🔍 Audit Pipeline v1.5.5"]
        Runner[Audit Runner]
        Scanner[Code Scanner]
        Metrics[Metrics Collector]
        Trends[Trend Database]
    end

    subgraph ML["🤖 ML Framework"]
        Training[Training Engine]
        Eval[Evaluation]
        Models[Model Registry]
    end

    subgraph Viz["📊 Visualization"]
        Dashboard[HTML Dashboard]
        Terminal[ASCII Terminal]
        Reports[Markdown Reports]
    end

    subgraph Storage["💾 Storage"]
        SQLite[(SQLite DB)]
        Logs[Log Files]
        Cache[Cache Layer]
    end

    Dev --> CLI
    agent --> Runner
    CI --> Runner

    CLI --> Training
    CLI --> Eval

    Runner --> Scanner
    Scanner --> Metrics
    Metrics --> Trends

    Trends --> SQLite
    Trends --> Viz

    Training --> Models
    Eval --> Models

    Dashboard --> Reports
```

### component Interaction Patterns

#### 1. Training Pipeline Flow

```
Data Validation → Configuration → Model Init → Training Loop → Checkpoint → Metrics
     ↓                 ↓              ↓             ↓              ↓          ↓
validate_dataset   Hydra      model_registry  engine_hf    RNGState   metrics.api
```

#### 2. Audit Pipeline Flow

```
Trigger → Scan → Analyze → Score → Store → Visualize → Notify
   ↓       ↓       ↓         ↓       ↓        ↓          ↓
 CLI   Scanner  Metrics  Scorer  SQLite   viz_html  Webhooks
```

#### 3. agent workflow Flow

```
Request → Parse → Execute → Validate → Report → Learn
   ↓        ↓        ↓         ↓         ↓        ↓
 agent  Navigator  workflow   Tests   Progress  Mental Map
```

### Design Principles (Physics-Inspired)

Based on the repository's physics-inspired orchestration (`agents/ORCHESTRATION.md`):

1. **Energy Minimization**: Workflows optimize for minimum "energy" (time, resources)
2. **Path Optimization**: Clear, non-redundant navigation paths through codebase
3. **Field Theory**: Configuration fields create "force fields" for dynamic behavior
4. **Pattern Reuse**: Reusable patterns reduce redundancy (DRY principle)
5. **Balanced Operations**: Training vs monitoring, security vs usability
6. **Entropy Management**: Order through structured documentation and organization

---

## Core Components

### 1. Training Configuration (`training/config.py`)

**Key Features**:
```python
@dataclass
class TrainingConfig:
    gradient_accumulation_steps: int = 1  # Exposed gradient accumulation
    batch_size: int = 8
    learning_rate: float = 5e-5
    num_train_epochs: int = 3
    precision: str = "fp32"  # fp32, fp16, bf16
    deterministic: bool = True  # Reproducible training
```

**Validation**: Built-in constraints (gradient_accumulation_steps >= 1, etc.)

### 2. Storage Connectors (`src/codex_ml/connectors/base.py`)

**Security Features**:
- Path traversal prevention with `_resolve()` method
- Async I/O with `asyncio.to_thread`
- Comprehensive error handling

```python
class LocalConnector(Connector):
    async def read_file(self, path: str) -> bytes:
        target = self._resolve(path)  # Validates path safety
        if not target.exists():
            raise ConnectorError(f"file does not exist: {path}")
        return await asyncio.to_thread(target.read_bytes)
```

### 3. Plugin System (`src/codex_ml/plugins/`)

**Abstract Base Pattern**:
```python
class Plugin(ABC):
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """Execute plugin logic. Override in subclass."""
        raise NotImplementedError
```

**Registry**: Dynamic plugin loading via entry points

### 4. Metrics Aggregation (`src/codex_ml/metrics/api.py`)

**NDJSON Format**: Newline-delimited JSON for streaming metrics
**Standardization**: Consistent metric schema across training runs

### 5. workflow Navigator (`agents/workflow_navigator.py`)

**Token-Based Execution**:
```python
navigator = WorkflowNavigator()
navigator.execute('AUDIT_EXEC')  # Execute by token
navigator.execute("Run audit pipeline")  # Natural language
navigator.execute_chain(['AUDIT_EXEC', 'PHYS_DECIDE'])  # Chaining
```

---

## Runtime & Data Flow

### Development Lifecycle

```
1. Setup Environment
   └─> .codex/scripts/setup.sh
       └─> UV lockfile resolution
           └─> Virtual environment creation

2. Code Development
   └─> Local editing with Copilot
       └─> Pre-commit hooks (ruff, black, mypy)
           └─> Incremental validation

3. Testing
   └─> pytest tests/ -v
       └─> Coverage reporting
           └─> Test artifacts

4. Training
   └─> codex_exec train --config config.yaml
       └─> Training loop with checkpoints
           └─> Metrics emission (NDJSON)

5. Audit
   └─> python scripts/space_traversal/audit_runner.py run
       └─> Capability scoring
           └─> Trend storage (SQLite)

6. Documentation
   └─> Automated generation via agents/prompts/documentation/
       └─> Wiki bundle creation
           └─> Deployment to GitHub Wiki

7. Deployment
   └─> Docker build
       └─> Container registry push
           └─> Kubernetes/service deployment
```

### Data Flow Diagram

```
Source Code → Validation → Training → Checkpoints
     ↓            ↓           ↓           ↓
 Git Repo    validate.py  Training   RNGState
                             ↓
                          Metrics
                             ↓
                        Aggregation
                             ↓
                       Visualization
```

---

## CI/CD & Testing

### GitHub Actions (Gated)

**Current State**: Workflows disabled by default for cost control

**Enabled Workflows** (when activated):
- `determinism.yml`: Deterministic audit execution
- `pre-release-deployment.yml`: Release preparation
- `self-healing-feedback-loop.yml`: Automated gap detection

**Self-Hosted Runner Policy**: Required for all workflows to prevent cloud cost

### Pre-Commit Hooks

**Configuration**: `.pre-commit-config.yaml`

**Hooks**:
- `ruff`: Linting
- `black`: Code formatting
- `isort`: Import sorting
- `mypy`: Type checking
- Custom validators

### Nox Sessions

**Configuration**: `noxfile.py`

**Sessions**:
- `tests`: Run full test suite
- `lint`: Linting with ruff
- `type_check`: MyPy validation
- `security`: Security scans (bandit, semgrep)

### Testing Strategy

**Pyramid Approach**:
```
        /\
       /E2E\      ← 5% (End-to-end)
      /------\
     /Integ  \   ← 15% (Integration)
    /--------\
   /   Unit   \  ← 80% (Unit tests)
  /------------\
```

**Test Execution**:
```bash
# Full suite
pytest tests/ -v

# Specific category
pytest -k "tokenization" -v

# With coverage
pytest tests/ --cov=src/codex_ml --cov-report=html

# Smoke tests only
pytest -m smoke -v
```

---

## Security & Compliance

### Security Infrastructure

**Scanning Tools**:
- **Gitleaks**: Secret detection (`.gitleaks.toml`)
- **Bandit**: Python security linter (`.bandit.yaml`)
- **Semgrep**: Pattern-based scanning (`semgrep_rules/`)
- **CodeQL**: Static analysis (GitHub Advanced Security)

**Current Status**: ✅ Zero known vulnerabilities

### Recent Security Fixes

1. **XSS Prevention** (`scripts/planning_components.py`):
   - Hash-based ID generation
   - Type validation for user inputs
   - `CSS.escape()` for selector safety

2. **Path Traversal Prevention** (`src/codex_ml/connectors/base.py`):
   - Path validation in `_resolve()`
   - Common path verification

### Secrets Management

**Configuration**: `.codex/cache/secrets.status.json`

**Best Practices**:
- Environment variables for sensitive data
- No hardcoded credentials
- Token rotation policies
- Least-privilege access

### Compliance Artifacts

- `SECURITY.md`: Security policy
- `CODE_OF_CONDUCT.md`: Community standards
- `GOVERNANCE.md`: Governance model
- `security_allowlist.json`: Approved exceptions

---

## AI agent Integration

### agent Architecture

The repository is explicitly designed for AI Assistant/agent intuitiveness:

#### 1. Prompt Library (`agents/prompts/`)

**Categories**:
- **Audit**: Full audits, regression checks, trend analysis
- **Debugging**: Test failures, merge conflicts, performance, security
- **Deployment**: Pre-release preparation, validation
- **Documentation**: Wiki generation, API docs
- **Organization**: Cleanup, archival, structure analysis
- **Self-Healing**: Feedback loops, gap detection

**Recent Additions** (26KB):
- `debugging/test-failure-debugging.md` (4.8KB)
- `debugging/resolve-merge-conflicts.md` (6.3KB)
- `debugging/performance-optimization.md` (7.0KB)
- `debugging/security-remediation.md` (8.6KB)

#### 2. workflow Navigator

**Tokenized Execution**:
```python
from agents.workflow_navigator import WorkflowNavigator

navigator = WorkflowNavigator()

# High-frequency workflows
navigator.execute('AUDIT_EXEC')     # Audit pipeline
navigator.execute('PHYS_DECIDE')    # Decision making
navigator.execute('SELF_HEAL')      # Self-healing

# Medium-frequency workflows
navigator.execute('DOC_GEN')        # Documentation
navigator.execute('MENTAL_REVIEW')  # Review decisions

# Low-frequency workflows
navigator.execute('REPO_ORG')       # Organization
```

## 3. Physics-Inspired Orchestration

**Energy-Based Decision Making** (`agents/physics_orchestrator.py`):
- Assigns "energy" costs to actions
- Optimizes workflow paths
- Balances competing objectives

**Mental Mapping** (`agents/mental_mapping.py`):
- Tracks decision history
- Learns from outcomes
- Improves future decisions

### 4. agent Control Interface

**Generation**:
```bash
python scripts/space_traversal/audit_runner.py agent-interface --output agent_interface.html
```

**Features**:
- Interactive HTML dashboard
- Direct action triggers
- Real-time status updates

### Integration Patterns

#### Pattern 1: Copilot-Driven Development

```
Developer + Copilot
    ↓
Code Changes
    ↓
Pre-Commit Validation
    ↓
agent Review (via prompts/debugging/)
    ↓
Test Execution
    ↓
Audit Pipeline
```

#### Pattern 2: Automated agent Tasks

```
Trigger (Schedule/Event)
    ↓
workflow Navigator
    ↓
Tokenized Workflow Execution
    ↓
Results Collection
    ↓
Mental Mapping Update
```

#### Pattern 3: Self-Healing Loop

```
Gap Detection
    ↓
Priority Assessment
    ↓
Auto-Fix Attempt
    ↓
Validation
    ↓
Success → Document
    ↓
Failure → Escalate
```

---

## Deployment & Operations

### Containerization

**Docker Variants**:
- `Dockerfile`: Standard CPU image
- `Dockerfile.gpu`: NVIDIA GPU support
- `Dockerfile.local`: Local development
- `Dockerfile.optimized`: Production-optimized

**Docker Compose**: `docker-compose.yml` for local orchestration

### Environment Management

**UV Lockfiles**: Deterministic dependency resolution
- `uv.lock`: Primary lockfile
- Fallback to `requirements*.txt` if UV unavailable

**Environment Variables**:
- `CODEX_ENV_PYTHON_VERSION`: Python version selector
- `CODEX_SESSION_ID`: Session identifier
- `CODEX_LOG_DB_PATH`: SQLite database path
- `CODEX_SQLITE_POOL`: Enable connection pooling

### Deployment Patterns

#### Pattern 1: Kubernetes Deployment

```yaml
# deploy/k8s/deployment.yaml (example)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codex-ml
spec:
  replicas: 3
  selector:
    matchLabels:
      app: codex-ml
  template:
    spec:
      containers:
      - name: codex-ml
        image: codex-ml:latest
        resources:
          limits:
            nvidia.com/gpu: 1
```

## Pattern 2: Self-Hosted Runner

**Requirements**:
- Dedicated runner machine
- GitHub Actions runner software
- Self-hosted label in workflows
- Cost monitoring

### Pattern 3: Model Serving

**Service Stack** (`services/`):
- FastAPI-based REST API
- Model registry integration
- Health checks and metrics
- Autoscaling policies

### Monitoring & Observability

**Tools**:
- Prometheus metrics
- Psutil for system monitoring
- Evidently for drift detection
- Custom metrics via `codex_ml.metrics.api`

**Key Metrics**:
- Training loss and accuracy
- Model inference latency
- Resource utilization (CPU, GPU, memory)
- Capability maturity scores

---

## Development Workflows

### Contributor Onboarding

**Quick Start** (from `docs/CONTRIBUTOR_ONBOARDING.md`):
```bash
# 1. Clone repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# 2. Setup environment
./.codex/scripts/setup.sh

# 3. Install dependencies
pip install -e .
pip install -r requirements-dev.txt

# 4. Run tests
pytest tests/ -v

# 5. Explore
python -m codex.cli --help
```

## Common Tasks

### task 1: Add New Feature

```bash
# 1. Create branch
git checkout -b feature/my-feature

# 2. Implement feature
# ... code changes ...

# 3. Add tests
touch tests/test_my_feature.py
# ... write tests ...

# 4. Run tests
pytest tests/test_my_feature.py -v

# 5. Lint and format
ruff check .
black .
isort .

# 6. Commit
git add .
git commit -m "feat: Add my feature"

# 7. Push
git push origin feature/my-feature
```

## task 2: Fix Bug

```bash
# 1. Reproduce bug
pytest tests/test_failing.py::test_specific -v

# 2. Debug
pytest tests/test_failing.py::test_specific -vv -s --pdb

# 3. Fix
# ... code changes ...

# 4. Verify fix
pytest tests/test_failing.py::test_specific -v

# 5. Commit
git add .
git commit -m "fix: Fix specific bug"
```

## task 3: Run Audit

```bash
# Full audit
python scripts/space_traversal/audit_runner.py run

# Generate dashboard
python scripts/generate_audit_dashboard.py

# View results
cat audit_artifacts/capabilities_scored.json | jq '.[] | select(.score < 0.85)'
```

## AI agent Workflows

**Using workflow Navigator**:
```python
from agents.workflow_navigator import WorkflowNavigator

# Initialize
nav = WorkflowNavigator()

# Execute workflows
nav.execute('AUDIT_EXEC')
nav.execute_chain(['AUDIT_EXEC', 'DOC_GEN', 'SELF_HEAL'])
```

**Using Prompts**:
```bash
# Refer to agents/prompts/ for specific scenarios
# Example: Test failure debugging
cat agents/prompts/debugging/test-failure-debugging.md
```

---

## Roadmap & Priorities

### Current Status

**Achieved**:
- ✅ Level 4 MLOps Certification (100/100)
- ✅ 2,079+ test files with 10.7% coverage (ratchet roadmap in progress)
- ✅ Zero critical gaps (all P0 stubs are correct patterns)
- ✅ Comprehensive documentation (693+ files)
- ✅ AI agent infrastructure operational

**Metrics**:
- MLOps Score: 100/100
- Test Pass Rate: 100%
- Security Vulnerabilities: 0
- Documentation: 64KB added in recent PRs

### Short-Term (0-4 phases)

#### Priority 1: CI/CD Enablement
- **task**: Enable self-hosted CI workflows
- **Components**: lint, type-check, unit tests, smoke training
- **Effort**: 2-3 iterations
- **Owner**: DevOps team

#### Priority 2: Dependency Canonicalization
- **task**: Standardize on `pyproject.toml` + `uv.lock`
- **Components**: Remove conflicting `requirements*.txt`
- **Effort**: 1 iteration
- **Owner**: Build team

#### Priority 3: Secrets Hardening
- **task**: Centralized secrets management
- **Components**: Pre-merge secret scanning, token rotation
- **Effort**: 3-4 iterations
- **Owner**: Security team

#### Priority 4: Documentation Consolidation
- **task**: Organize 693 markdown files with index
- **Components**: Active vs historical categorization
- **Effort**: 2-3 iterations
- **Owner**: Documentation team

#### Priority 5: Stub Cleanup Enhancement
- **task**: AST-based abstract method detection
- **Components**: Enhance `stub_cleanup.py`
- **Effort**: 2 iterations
- **Owner**: Code quality team

### Mid-Term (1-3 Months)

#### Priority 1: Deterministic Infrastructure
- **task**: Reproducible training harness
- **Components**: Device placement, RNGState verification
- **Effort**: 2 phases
- **Owner**: ML team

#### Priority 2: Artifact Signing
- **task**: Sign and version reproducibility manifests
- **Components**: GPG signing, manifest versioning
- **Effort**: 1 phase
- **Owner**: Security team

#### Priority 3: Security Hardening
- **task**: Automated security scanning in CI
- **Components**: Semgrep, Bandit, baseline checks
- **Effort**: 1 phase
- **Owner**: Security team

#### Priority 4: agent Memory System
- **task**: Context preservation between invocations
- **Components**: agent memory store, context retrieval
- **Effort**: 2 phases
- **Owner**: AI team

#### Priority 5: Performance Benchmarking
- **task**: Systematic performance regression testing
- **Components**: Benchmark suite, CI integration
- **Effort**: 1 phase
- **Owner**: Performance team

### Long-Term (3-9 Months)

#### Priority 1: Production Serving Stack
- **task**: Scalable model serving
- **Components**: Autoscaling, versioning, monitoring
- **Effort**: 4-6 phases
- **Owner**: Platform team

#### Priority 2: MLOps Pipelines
- **task**: Continuous evaluation and monitoring
- **Components**: Drift detection, retraining triggers
- **Effort**: 6-8 phases
- **Owner**: ML team

#### Priority 3: Multi-Version Python Support
- **task**: CI testing across Python 3.9-3.12
- **Components**: Matrix testing, compatibility checks
- **Effort**: 2 phases
- **Owner**: Build team

#### Priority 4: HAR Integration
- **task**: Complete HAR file support
- **Components**: Per `docs/HAR_INTEGRATION_PLAN.md`
- **Effort**: 3-4 phases
- **Owner**: Integration team

#### Priority 5: Advanced Monitoring
- **task**: Production-grade observability
- **Components**: Distributed tracing, alerting
- **Effort**: 4 phases
- **Owner**: SRE team

### Implementation Checklist

**Immediate Actions** (This Week):
- [ ] Enable minimal self-hosted CI
- [ ] Run security scan baseline
- [ ] Create documentation index
- [ ] Verify UV lockfile consistency

**Next Sprint** (Next 2 phases):
- [ ] Implement token rotation
- [ ] Enhance stub_cleanup.py
- [ ] Add performance benchmarks
- [ ] Automate archival process

**This Quarter** (Next 3 Months):
- [ ] Complete agent memory system
- [ ] Harden security infrastructure
- [ ] Implement artifact signing
- [ ] Launch deterministic CI

---

## Appendices

### Appendix A: Key Files Reference

| File | Purpose | Last Updated |
|------|---------|-------------|
| `COMPREHENSIVE_GAP_ANALYSIS.md` | Gap analysis with priority matrix | 2025-12-11 |
| `PR_FINAL_SUMMARY.md` | PR summary with metrics | 2025-12-11 |
| `docs/CONTRIBUTOR_ONBOARDING.md` | Onboarding guide | 2025-12-11 |
| `AGENTS.md` | agent operations playbook | 2025-12-10 |
| `codex_gap_registry.yaml` | Known gaps tracking | 2025-12-11 |
| `pyproject.toml` | Package configuration | Current |
| `uv.lock` | Dependency lockfile | Current |

### Appendix B: Command Reference

**Environment Setup**:
```bash
./.codex/scripts/setup.sh
source venv/bin/activate  # or .venv/bin/activate
```

**CLI Usage**:
```bash
python -m codex.cli --help
python -m codex_ml.exec.codex_exec --help
```

**Testing**:
```bash
pytest tests/ -v
pytest -k "pattern" -v
pytest --cov=src/codex_ml --cov-report=html
```

**Auditing**:
```bash
python scripts/space_traversal/audit_runner.py run
python scripts/generate_audit_dashboard.py
```

**agent Workflows**:
```python
from agents.workflow_navigator import WorkflowNavigator
nav = WorkflowNavigator()
nav.execute('AUDIT_EXEC')
```

### Appendix C: Architecture Diagrams

**System Components**:
```
┌─────────────────────────────────────────────────────────────┐
│                         Users Layer                          │
│  Developers │ AI Agents │ CI/CD │ Operators                  │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                      Interface Layer                         │
│  CLI │ workflow Navigator │ agent Prompts                    │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                      Application Layer                       │
│  Training │ Evaluation │ Audit Pipeline │ Documentation     │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                      Core Services                           │
│  Plugin System │ Metrics │ Connectors │ Configuration       │
└────────────┬────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│                      Storage Layer                           │
│  SQLite │ File System │ Cache │ Logs                        │
└─────────────────────────────────────────────────────────────┘
```

### Appendix D: Glossary

- **codex_exec**: CLI entrypoint for tasks, training, audits
- **RNGState**: Deterministic random seed snapshot for reproducibility
- **NDJSON**: Newline-delimited JSON for metrics
- **Self-Hosted Runner**: GitHub Actions runner to avoid cloud costs
- **workflow Token**: Short identifier for workflow execution (e.g., `AUDIT_EXEC`)
- **Mental Mapping**: Decision tracking for agent learning
- **Physics Orchestration**: Energy-based workflow optimization
- **Capability Score**: Maturity metric (0.0-1.0 scale)
- **Trend Database**: SQLite database tracking audit history
- **Plugin Registry**: Dynamic plugin loading system

### Appendix E: Metrics Schema

**Audit Metrics**:
```json
{
  "capability": "string",
  "score": "float (0.0-1.0)",
  "evidence": ["file paths"],
  "timestamp": "ISO8601",
  "trend": "increasing|stable|decreasing"
}
```

**Training Metrics** (NDJSON):
```json
{"run_id": "uuid", "timestamp": "ISO8601", "metric": "loss", "value": 0.123}
{"run_id": "uuid", "timestamp": "ISO8601", "metric": "accuracy", "value": 0.95}
```

**Reproducibility Manifest**:
```json
{
  "run_id": "uuid",
  "timestamp": "ISO8601",
  "python_version": "3.12",
  "dependencies": {"package": "version"},
  "rng_state": "base64_encoded",
  "checkpoint_uri": "path/to/checkpoint"
}
```

### Appendix F: Security Checklist

- [ ] No hardcoded secrets
- [ ] Environment variables for sensitive data
- [ ] Pre-merge secret scanning enabled
- [ ] Token rotation policy documented
- [ ] Self-hosted runners only
- [ ] Branch protection enabled
- [ ] Signed commits required
- [ ] Security scans passing (Gitleaks, Bandit, Semgrep)
- [ ] Dependency scanning enabled
- [ ] Incident response procedures documented

### Appendix G: Testing Checklist

- [ ] Unit tests for new code
- [ ] Integration tests for interactions
- [ ] Smoke tests for quick validation
- [ ] Property-based tests for edge cases
- [ ] Capability tests for features
- [ ] Security tests for vulnerabilities
- [ ] Performance tests for regressions
- [ ] Reproducibility tests for determinism

---

## Conclusion

This blueprint provides a comprehensive technical reference for the `_codex_` repository. The repository has achieved Level 4 MLOps maturity with extensive documentation, testing, and AI agent integration. The roadmap prioritizes CI/CD enablement, security hardening, and continued enhancement of the AI-friendly infrastructure.

### Key Takeaways

1. **Production-Ready**: Zero critical gaps, 100% test pass rate, comprehensive security
2. **AI-Friendly**: Native support for Copilot workflows, tokenized workflows, structured prompts
3. **Well-Documented**: 693+ markdown files, detailed guides, comprehensive onboarding
4. **Secure**: Zero vulnerabilities, comprehensive scanning, path validation
5. **Reproducible**: Deterministic training, RNG checkpointing, environment snapshots
6. **Extensible**: Plugin system, modular architecture, clear interfaces

### Next Steps

**For Developers**:
1. Read `docs/CONTRIBUTOR_ONBOARDING.md`
2. Run `.codex/scripts/setup.sh`
3. Explore `AGENTS.md` for workflows
4. Contribute using Copilot-assisted development

**For AI Agents**:
1. Use `agents/workflow_navigator.py` for orchestration
2. Refer to `agents/prompts/` for structured prompts
3. Execute tokenized workflows (e.g., `AUDIT_EXEC`)
4. Update mental mappings for learning

**For Architects**:
1. Review this blueprint for system understanding
2. Assess roadmap priorities
3. Plan infrastructure enhancements
4. Ensure alignment with MLOps best practices

---

**Document Version**: 1.0.0
**Maintenance**: Update quarterly or after major changes
**Contact**: repository owners (@mbaetiong)
**Last Updated**: 2025-12-11



---
## 📎 Consolidated from: docs/ARCHITECTURE_INDEX.md

# Architecture Documentation Index

**Status**: Master index for all architecture documentation  
**Last Updated**: 2026-06-20  
**Maintainer**: @mbaetiong

## Overview

The _codex_ repository implements a Level 4 MLOps-certified, production-grade ML framework. This index consolidates all architecture documentation and fixes broken references.

---

## 📋 Architecture Documents

### Core Architecture Documents

| Document | Purpose | Audience | Size |
|----------|---------|----------|------|
| [ARCHITECTURE_BLUEPRINT.md](./ARCHITECTURE_BLUEPRINT.md) | Comprehensive repository blueprint | Developers, Architects | 1162 lines |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | ML framework architecture overview | ML Engineers | 642 lines |
| [Architecture.md](./Architecture.md) | Import shim governance & policy | Developers | 177 lines |
| [architecture.md](./architecture.md) | Quick runtime flow diagrams | Quick Reference | 55 lines |

### Supporting Architecture Documents

- [REPOSITORY_ARCHITECTURE_DIAGRAMS.md](./REPOSITORY_ARCHITECTURE_DIAGRAMS.md) - Visual architecture diagrams
- [docs/architecture/ARCHITECTURE_LAYERS.md](./architecture/ARCHITECTURE_LAYERS.md) - Layer-by-layer breakdown
- [docs/architecture/INDEX.md](./architecture/INDEX.md) - Architecture directory index

---

## 🏗️ Architecture Layers

The _codex_ system is organized in the following layers:

### 1. **Interface Layer**
- CLI (Command Line Interface)
- Python API
- REST API (optional)
- Jupyter notebooks integration

### 2. **Orchestration Layer**
- Hydra configuration management
- workflow execution
- Plugin system
- agent orchestration (145+ active agents)

### 3. **Core Engine Layer**
- Training pipelines (HuggingFace Trainer, custom loops)
- Evaluation framework
- Model inference
- Data processing

### 4. **Storage & Integration Layer**
- Data connectors (S3, Azure, GCS)
- Model registry
- Experiment tracking (MLflow, W&B)
- Checkpoint management

### 5. **Infrastructure Layer**
- Ray cluster support
- Kubernetes deployment
- Docker containerization
- Git/GitHub integration

### 6. **Observability Layer**
- Logging and telemetry
- Performance monitoring
- Error tracking
- Metrics collection

---

## 🔄 Runtime Data Flow

```mermaid
%%{init: {'accessibility': {'title': 'Flowchart showing Ingestion, Tokenizer'}}%%
flowchart LR
    A[Ingestion] --> B[Tokenizer]
    B --> C[Datasets]
    C --> D[Model Loader]
    D --> E{Training Engine}
    E --> F[Metrics]
    F --> G[Logging]
    G --> H[Experiment Tracking]
    E --> I[Checkpoint Manager]
    I --> J[Model Registry]
```

**Data Flow Steps:**

1. **Ingestion**: Raw data ingestion from various sources
2. **Tokenization**: Convert raw data to token sequences
3. **Datasets**: Create training/validation/test splits
4. **Model Loading**: Load model from local or Hugging Face Hub
5. **Training Engine**: Execute training loop
6. **Metrics**: Compute performance metrics
7. **Logging**: Log metrics and metadata
8. **Experiment Tracking**: Send to experiment tracking backend
9. **Checkpoint Management**: Save and manage model checkpoints
10. **Model Registry**: Register trained models

---

## 📁 Repository Structure

```
_codex_/
├── .codex/                      # Codex environment configuration
├── .github/                     # CI/CD workflows
├── agents/                      # AI agent infrastructure
│   ├── prompts/                 # Pre-defined prompts
│   └── codex_client/            # GitHub integration
├── src/codex_ml/               # Core ML framework
│   ├── training/               # Training pipelines
│   ├── evaluation/             # Evaluation metrics
│   ├── connectors/             # Storage connectors
│   └── plugins/                # Plugin system
├── scripts/                     # Utility scripts (195+)
├── tests/                       # Test suite (2,079+)
├── docs/                        # Documentation (693+)
│   ├── mcp/                    # MCP documentation
│   ├── api/                    # API reference
│   ├── architecture/           # Architecture docs
│   ├── deployment/             # Deployment guides
│   ├── security/               # Security documentation
│   └── operations/             # Operations guides
├── config/                      # Configuration files
│   └── training/               # Training configs
├── requirements/                # Dependency specifications
└── README.md                    # Project README
```

---

## 🔌 Component Architecture

### Core Components

```mermaid
%%{init: {'accessibility': {'title': 'Class Diagram: > DataHandling
    TrainingEng'}}%%
classDiagram
    class TrainingEngine {
      +run(cfg)
      +evaluate()
      +save_checkpoint()
    }
    class DataHandling {
      +iter_jsonl(path)
      +deterministic_split()
      +validate_schema()
    }
    class Metrics {
      +batch_metrics()
      +compute_accuracy()
      +compute_loss()
    }
    class Checkpointing {
      +save_checkpoint()
      +load_checkpoint()
      +resume_training()
    }
    class Logging {
      +TBWriter
      +wandb_logger
      +file_logger
    }
    class ModelRegistry {
      +register_model()
      +load_model()
      +list_versions()
    }
    TrainingEngine --> DataHandling
    TrainingEngine --> Metrics
    TrainingEngine --> Checkpointing
    TrainingEngine --> Logging
    TrainingEngine --> ModelRegistry
```

---

## 🔐 Security & Compliance

### Security Layers

- **Code Security**: Bandit, CodeQL scanning
- **Dependency Security**: Pip-audit, Dependabot
- **Secret Management**: Git secrets scanning
- **Access Control**: RBAC, GitHub teams
- **Audit Logging**: Comprehensive activity logging

### Compliance

- **MLOps Maturity**: Level 4 Certified
- **Test Coverage**: 2,079+ test files
- **Documentation**: 693+ markdown files
- **Reproducibility**: Deterministic training with RNG checkpointing

---

## 🚀 Deployment Architecture

### Local Development

```bash
# Install dependencies
pip install -e .

# Run training
codex train config/training.yaml

# Evaluate model
codex evaluate --model model.pth
```

## Docker Deployment

```dockerfile
FROM python:3.10
WORKDIR /app
COPY . .
RUN pip install -e .
CMD ["python", "-m", "codex.training"]
```

### Kubernetes Deployment

- StatefulSet for training jobs
- Service mesh integration
- Pod autoscaling
- Persistent volume management

---

## 🔧 Configuration Management

The system uses Hydra for configuration management:

```yaml
# config/training.yaml
defaults:
  - override hydra/job_logging: custom

model:
  name: "bert-base"
  pretrained: true

training:
  learning_rate: 1e-4
  batch_size: 32
  epochs: 10

data:
  dataset: "wikitext"
  split: [0.8, 0.1, 0.1]
```

## Configuration Hierarchy

1. **Base Configs**: defaults/
2. **Overrides**: Command-line
3. **Environment**: Environment variables
4. **Local**: Local config.yaml

---

## 📊 Key Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Test Coverage | ≥90% | 10.7% |
| Documentation Coverage | ≥95% | 85% |
| Code Quality Score | ≥8.0 | 7.2 |
| Security Score | 100% | 100% ✅ |
| Availability | ≥99.9% | N/A |

---

## 🛣️ Development Workflows

### Feature Development

1. Create feature branch from `main`
2. Implement feature with tests
3. Run local validation
4. Open pull request
5. Pass CI/CD checks
6. Get code review approval
7. Merge to `main`

### Release Process

1. Bump version in setup.py
2. Update CHANGELOG
3. Create release branch
4. Publish to PyPI
5. Create GitHub release
6. Update documentation

---

## 🔗 Integration Points

### External Systems

- **Hugging Face Hub**: Model and dataset storage
- **MLflow**: Experiment tracking
- **W&B**: Weights & Biases integration
- **GitHub**: Version control and CI/CD
- **Cloud Providers**: AWS, GCP, Azure support

### APIs

- **Python API**: Direct library usage
- **CLI**: Command-line interface
- **REST API**: HTTP endpoints (optional)
- **GraphQL**: Query interface (optional)

---

## 📚 Documentation Links

### Architecture-Related Docs

- [ARCHITECTURE_BLUEPRINT.md](./ARCHITECTURE_BLUEPRINT.md) - Full blueprint
- [ARCHITECTURE.md](./ARCHITECTURE.md) - ML architecture
- [Architecture.md](./Architecture.md) - Import governance
- [docs/architecture/](./architecture/) - Architecture directory

### Other Key Docs

- [API Reference](./api/) - API documentation
- [Deployment Guides](./deployment/) - Deployment procedures
- [Security Documentation](./security/) - Security policies
- [Operations Guide](./operations/) - Operations procedures
- [Development Guide](../CONTRIBUTING.md) - Contributing guidelines

---

## 🤖 AI agent Integration

The system includes native support for AI agents:

- **Copilot Integration**: Native GitHub Copilot support
- **agent Orchestration**: 145+ active agents
- **Tokenized Workflows**: Efficient token usage
- **Structured Prompts**: Pre-defined prompt templates
- **agent Context**: Session-based context management

---

## 🆘 Troubleshooting

### Common Issues

**Q: Which architecture document should I read?**  
A: Start with [architecture.md](./architecture.md) for quick overview, then [ARCHITECTURE_BLUEPRINT.md](./ARCHITECTURE_BLUEPRINT.md) for detailed information.

**Q: How is the data flow organized?**  
A: See [Runtime Data Flow](#-runtime-data-flow) section above.

**Q: Where do I find deployment information?**  
A: See [docs/deployment/](./deployment/) directory.

**Q: How is security implemented?**  
A: See [Security & Compliance](#-security--compliance) section and [docs/security/](./security/) directory.

---

## 🏗️ Future Roadmap

### Short Term (1-3 months)
- [ ] Improve test coverage to ≥50%
- [ ] Complete API documentation
- [ ] Add performance benchmarks

### Medium Term (3-6 months)
- [ ] Multi-GPU distributed training
- [ ] Advanced monitoring dashboard
- [ ] Enhanced plugin system

### Long Term (6-12 months)
- [ ] Production-grade monitoring
- [ ] Advanced agent orchestration
- [ ] Federated learning support

---

## 📞 Support

For questions or clarifications about architecture:

1. Check the relevant documentation file
2. Search GitHub issues and discussions
3. Open a new discussion or issue
4. Contact the maintainers: @mbaetiong

---

## 📝 Maintenance

- **Last Updated**: 2026-06-20
- **Next Review**: 2026-07-20
- **Owner**: @mbaetiong
- **Contributing**: Please open issues for documentation improvements

---

**See Also**: [ARCHITECTURE_BLUEPRINT.md](./ARCHITECTURE_BLUEPRINT.md) for comprehensive technical reference

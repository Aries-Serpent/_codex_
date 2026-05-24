# Codex ML Architecture (v0.1.0)

> **Version**: v0.1.0 Pre-Release
> **Last Updated**: 2026-05-23
> **Status**: Living Document
> **Managed By**: AI Assistant Autonomous System

**AI-Managed Repository Notice**: This repository is designed for and managed by AI Assistants and Agents. All architectural decisions, reviews, and updates are performed autonomously by AI systems.

**Package Name**: `codex-ml` (PyPI/Distribution) | Repository: `_codex_`

This document provides a comprehensive architectural overview of the `_codex_` ML training, evaluation, and plugin framework using C4-lite modeling.

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

The Codex ML system provides a comprehensive framework for ML model training, evaluation, and deployment with emphasis on reproducibility, observability, and extensibility. It includes the MCP ecosystem, Cognitive Brain system, and 280+ autonomous agents.

<!-- METRICS_LAST_UPDATED: 2026-05-24 Phase 10 alignment -->
```mermaid
graph TB
    User[Data Scientist / ML Engineer<br/>Platform User]
    Copilot[GitHub Copilot<br/>AI Coding Agent]
    Agents[280+ Autonomous Agents<br/>🤖 MCP-enabled]

    Codex[codex-ml<br/>Production-Ready ML Platform<br/>22,000+ Tests | 34.56% agents/ coverage]

    Brain[Cognitive Brain<br/>k₁=0.35 | 2.86x Advantage<br/>289 patterns learned]
    MCP[MCP System<br/>Model Context Protocol<br/>162 active workflows]
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
- **300+ Autonomous Agents**: Specialized domain agents for testing, documentation, security, and operations
- **CI/CD Systems**: 162 active GitHub Actions workflows for testing, deployment, and self-healing

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
graph TB
    subgraph "codex-ml v0.1.0 System"
        subgraph "Core ML Platform"
            CLI[CLI Interface<br/>Typer/Click<br/>🔧 Main Entry Point]
            Training[Training Engine<br/>PyTorch + Transformers<br/>📈 Distributed Training]
            Eval[Evaluation Engine<br/>lm-eval + custom metrics<br/>📊 22,000+ Tests]
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

        subgraph "Agent System (300+ Agents)"
            AgentCore[Agent Core<br/>RAG + RAGIndexer<br/>🤖 Autonomous]
            ToolRegistry[Tool Registry<br/>Centralized Discovery<br/>🔧 Dynamic]
            AgentMemory[Agent Memory<br/>SQLite Persistent<br/>💾 Pattern Library]
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

    %% Agent System
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

### Component Responsibilities

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
- ✅ MCP ecosystem (162 active workflows)
- ✅ Cognitive Brain (289 patterns, k₁=0.35)
- ✅ 300+ autonomous agents deployed

### Phase 9 — Completed (2026-05-23)
- ✅ Phase 9.1: agents/ public API + class contract tests
- ✅ Phase 9.2: CLI smoke tests + coverage rollup (34.56%)
- ✅ Phase 9.3: error-path coverage (50 new tests)
- ✅ Phase 9.4: edge-case coverage (71 new tests)
- ✅ Rate-limit orchestrator + session TTL repo var
- ✅ Secrets baseline clean; living docs aligned to v1.3.0

### Phase 10 — Post-Coverage Maintenance (Current)
- 🔄 Coverage regression gate: hold ≥34% agents/ (CI enforced)
- 🔄 Gap-fill src/ toward 50% overall statement coverage
- 🔄 Documentation alignment (CODEBASE_MERMAID_MAPS v1.3.0 ✅)
- 📋 Adaptive Learning Phase 8.3: QEC k₁ tuning (80→100%)
- 📋 Transfer Learning Phase 8.4 scaffold
- 📋 Archive merge-candidate CI docs
- 📋 Webhook event bus triggers (post-merge)

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

### Component Overview

- **Target discovery (`iter_files`)**: Walks requested roots while skipping generated locations
- **Line preparation (`_prepare_line`)**: Strips diff prefixes and indentation
- **Fence analysis (`_scan_file`)**: Maintains `FenceState` metadata to validate symmetry
- **Public entry points**: `validate_file` (Python API), `main` (CLI)

```mermaid
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

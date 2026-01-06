# Codex ML Architecture

> **Last Updated**: Previous Cycle-12-16  
> **Status**: Living Document  
> **Managed By**: AI Assistant Autonomous System

**AI-Managed Repository Notice**: This repository is designed for and managed by AI Assistants and Agents. All architectural decisions, reviews, and updates are performed autonomously by AI systems.

This document provides a comprehensive architectural overview of the `_codex_` ML training, evaluation, and plugin framework using C4-lite modeling.

## Table of Contents
- [System Context](#system-context)
- [Container Architecture](#container-architecture)
- [Component Architecture](#component-architecture)
- [Data Flow](#data-flow)
- [Operational Concerns](#operational-concerns)
- [Technology Choices](#technology-choices)
- [Roadmap](#roadmap)
- [Architecture Decision Records](#architecture-decision-records)

---

## System Context

The Codex ML system provides a comprehensive framework for ML model training, evaluation, and deployment with emphasis on reproducibility, observability, and extensibility.

```mermaid
graph TB
    User[Data Scientist / ML Engineer]
    Copilot[GitHub Copilot / ChatGPT]
    
    Codex[Codex ML System]
    
    HF[Hugging Face Hub]
    MLflow[MLflow Tracking Server]
    Storage[Cloud Storage / S3]
    Compute[GPU Compute / Ray Cluster]
    
    User -->|Configure & Train| Codex
    Copilot -->|Code Generation & Review| Codex
    Codex -->|Load Models & Data| HF
    Codex -->|Track Experiments| MLflow
    Codex -->|Store Artifacts| Storage
    Codex -->|Distribute Training| Compute
    
    style Codex fill:#326ce5,stroke:#fff,stroke-width:3px,color:#fff
```text

### External Actors

- **Data Scientists / ML Engineers**: Primary users who configure, train, and evaluate models
- **GitHub Copilot / ChatGPT**: AI assistants that help navigate the codebase and generate code
- **CI/CD Systems**: Automated workflows for testing and deployment

### External Systems

- **Hugging Face Hub**: Model and dataset repository
- **MLflow**: Experiment tracking and model registry
- **Cloud Storage**: Artifact storage (checkpoints, logs, data)
- **Ray Cluster**: Distributed compute for training and serving

---

## Container Architecture

The system is organized into several logical containers (processes or deployable units):

```mermaid
graph TB
    subgraph "Codex ML System"
        CLI[CLI Interface<br/>Typer/Click]
        Training[Training Engine<br/>PyTorch + Transformers]
        Eval[Evaluation Engine<br/>lm-eval + custom metrics]
        Serve[Model Serving<br/>Ray Serve + FastAPI]
        Logging[Logging & Telemetry<br/>SQLite + session tracking]
        Config[Configuration<br/>Hydra + OmegaConf]
        Plugins[Plugin Framework<br/>Dynamic loading]
    end
    
    subgraph "External Services"
        MLflow[MLflow Server]
        Storage[Object Storage]
        HF[Hugging Face]
    end
    
    CLI --> Config
    CLI --> Training
    CLI --> Eval
    CLI --> Serve
    
    Training --> Logging
    Eval --> Logging
    Serve --> Logging
    
    Training --> MLflow
    Eval --> MLflow
    
    Training --> Storage
    Training --> HF
    Eval --> HF
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

See [SECURITY.md](../SECURITY.md) for vulnerability reporting.

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

### Current Capabilities (v0.x)
- ✅ LoRA/QLoRA fine-tuning
- ✅ Hydra-based configuration
- ✅ MLflow experiment tracking
- ✅ Session logging to SQLite
- ✅ CLI interface
- ✅ Evaluation with lm-eval
- ✅ Plugin framework

### Near-Term (Phase 1 (Current Cycle))
- 🔄 Enhanced model serving with caching
- 🔄 Advanced evaluation metrics
- 🔄 Automated hyperparameter tuning
- 🔄 Better documentation and tutorials
- 🔄 Distributed training optimizations

### Medium-Term (Cycle 2-Phase 3 (Current Cycle))
- 📋 Multi-modal support (vision + language)
- 📋 Reinforcement learning from human feedback (RLHF)
- 📋 Model compression and quantization
- 📋 Automated dataset curation
- 📋 Enhanced monitoring and alerting

### Long-Term (Current Cycle+)
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
```text

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

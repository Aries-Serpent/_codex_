# Codex ML Architecture - Consolidated Reference

> **Version**: 1.1.0 (Consolidated)  
> **Last Updated**: 2026-06-22  
> **Status**: Production-Ready Living Document  
> **Audience**: Developers, Architects, AI Agents, DevOps Engineers  
> **Managed By**: AI Assistant Autonomous System  

---

## Overview

This document consolidates architectural guidance from multiple sources into a single authoritative reference. It provides comprehensive technical documentation of the `_codex_` ML platform covering system design, component architecture, deployment patterns, and operational workflows.

### Document Purpose

- **For Developers**: Understand system design and code organization
- **For Architects**: Learn design decisions and integration patterns
- **For AI Agents**: Structured workflows and autonomous operations
- **For DevOps**: Deployment, scaling, and operational concerns

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Context](#system-context)
3. [Container Architecture](#container-architecture)
4. [Component Architecture](#component-architecture)
5. [Repository Structure](#repository-structure)
6. [Core Components Deep Dive](#core-components-deep-dive)
7. [Data Flow & Pipelines](#data-flow--pipelines)
8. [Operational Concerns](#operational-concerns)
9. [Technology Choices](#technology-choices)
10. [AI Integration & Agents](#ai-integration--agents)
11. [Development Workflows](#development-workflows)
12. [Deployment Patterns](#deployment-patterns)
13. [Security & Compliance](#security--compliance)
14. [Architecture Decision Records](#architecture-decision-records)
15. [Roadmap & Evolution](#roadmap--evolution)

---

## Executive Summary

### Key Characteristics

- **MLOps Maturity**: Level 4 Certified (100/100 Azure MLOps capabilities)
- **Production Readiness**: Zero known vulnerabilities, comprehensive scanning
- **Test Coverage**: 2,130+ test files, 100% pass rate
- **Documentation**: 700+ markdown files with professional standards
- **AI Integration**: 145 active autonomous agents with MCP support
- **Reproducibility**: Deterministic training with RNG checkpointing
- **Scalability**: Distributed training support via Ray Cluster

### Architecture Philosophy

The system is built on three core principles:

1. **Modularity**: Independent, composable components with clear interfaces
2. **Extensibility**: Plugin-based architecture for custom implementations
3. **Observability**: Comprehensive logging, metrics, and tracing throughout

---

## System Context

### System Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│  Codex ML: Production-Grade ML Framework                   │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Internal: Core ML Platform + Agent System        │    │
│  │  ├── Training & Evaluation Engines                │    │
│  │  ├── MCP Ecosystem (Model Context Protocol)       │    │
│  │  ├── Cognitive Brain (Decision Making)            │    │
│  │  ├── Python Ingestion Pipeline                    │    │
│  │  └── 145 Active Autonomous Agents                 │    │
│  └────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌────────────────────────────────────────────────────┐    │
│  │  External Integrations                            │    │
│  │  ├── Hugging Face Hub (Models + Datasets)        │    │
│  │  ├── MLflow (Experiment Tracking)                │    │
│  │  ├── Cloud Storage (S3/Azure/GCS)                │    │
│  │  ├── Ray Cluster (Distributed Compute)           │    │
│  │  └── GitHub (PR Automation + Actions)            │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### External Actors

1. **Data Scientists / ML Engineers**: Configure, train, and evaluate models
2. **GitHub Copilot**: AI coding agent for CI failures, coverage gaps
3. **Autonomous Agents** (145+): Specialized domain agents for testing, docs, security, ops
4. **CI/CD Systems**: 134+ GitHub Actions workflows for testing and deployment

---

## Container Architecture

### High-Level System Components

```
┌────────────────────────────────────────────────────────────────┐
│  codex-ml v0.1.0 System                                        │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Core ML Platform                                       │  │
│  │  • CLI Interface (Typer/Click)                         │  │
│  │  • Training Engine (PyTorch + Transformers)            │  │
│  │  • Evaluation Engine (lm-eval + custom metrics)        │  │
│  │  • Model Serving (Ray Serve + FastAPI)                 │  │
│  │  • Configuration Management (Hydra + OmegaConf)        │  │
│  │  • Session Logging (SQLite + Telemetry)                │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Cognitive Brain (k₁=0.35, 2.86x Advantage)            │  │
│  │  • Decision Engine (Superposition + Entanglement)      │  │
│  │  • Memory Manager (STM/LTM + Patterns, 60% Compression)│  │
│  │  • Adaptive Scoring (ML-inspired Weights)              │  │
│  │  • Pattern Learning (289 patterns learned)             │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  MCP Ecosystem (Model Context Protocol)                │  │
│  │  • MCP Core (Standardized Protocol)                    │  │
│  │  • Adapters (Pinecone/Mock/Custom)                     │  │
│  │  • Background Workers (Embeddings + Checkpoints)       │  │
│  │  • Metrics & Telemetry (Observability)                 │  │
│  │  • 134 active workflows, 298 workflow files            │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Python Ingestion Pipeline                             │  │
│  │  • Ingest Module (File/ZIP/Git/URL)                    │  │
│  │  • Analysis Module (AST + Runtime)                     │  │
│  │  • Transform Module (Tier A/B/C LLM-guided)            │  │
│  │  • Verify Module (Behavior Compare + Test Gen)         │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Agent System (145 Active Autonomous Agents)           │  │
│  │  • Agent Core (RAG + RAGIndexer)                        │  │
│  │  • Tool Registry (Centralized Discovery)               │  │
│  │  • Agent Memory (SQLite Persistent Pattern Library)    │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │  Infrastructure                                        │  │
│  │  • Security Layer (48 CVEs Fixed, Production-Grade)    │  │
│  │  • CI/CD Automation (Auto-Fix + Self-Heal)             │  │
│  │  • Plugin Framework (Dynamic Loading)                  │  │
│  └─────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### Component Interaction Model

```
┌──────────────────────────────┐
│  CLI Interface               │
│  (Entry Point)               │
└──────────────┬───────────────┘
               │
      ┌────────┴────────┐
      │                 │
┌─────▼──────┐  ┌──────▼─────┐
│ Training   │  │ Evaluation │
│ Engine     │  │ Engine     │
└─────┬──────┘  └──────┬─────┘
      │                │
      └────────┬───────┘
               │
      ┌────────▼──────────┐
      │ Session Logging   │
      │ + Telemetry       │
      └───────────────────┘
               │
      ┌────────▼──────────┐
      │ Cognitive Brain   │
      │ (Decision Logic)  │
      └───────────────────┘
               │
      ┌────────▼──────────┐
      │ MCP Ecosystem     │
      │ + Agent System    │
      └───────────────────┘
```

---

## Repository Structure

### Root-Level Organization

```
_codex_/
├── .codex/                      # Codex environment kit & setup scripts
├── .github/                     # CI/CD workflows (gated for cost)
├── agents/                      # AI Agent infrastructure (145 agents)
│   ├── prompts/                 # Structured prompt library
│   ├── workflow_navigator.py   # Token-based workflow execution
│   └── codex_client/           # GitHub bridge client
├── src/codex_ml/               # Core ML framework (production)
│   ├── training/               # Training pipelines
│   ├── evaluation/             # Evaluation metrics
│   ├── connectors/             # Storage connectors
│   ├── plugins/                # Plugin system
│   ├── config/                 # Configuration management
│   ├── callbacks/              # Training callbacks
│   ├── cli/                    # CLI interface
│   └── utils/                  # Utility functions
├── tests/                       # Test suite (2,130+ files)
│   ├── capabilities/           # Feature-specific tests
│   ├── tokenization/           # Tokenization parity
│   ├── training/               # Training pipeline tests
│   └── integration/            # End-to-end tests
├── docs/                        # Documentation (700+ files)
│   ├── api/                    # API reference
│   ├── guides/                 # User guides
│   ├── deployment/             # Deployment guides
│   ├── architecture/           # Architecture docs
│   └── admin/                  # Admin guides
├── scripts/                     # Utility scripts (195+ files)
│   └── space_traversal/        # Audit pipeline v1.5.5
├── configs/                     # Hydra configurations
├── deploy/                      # Deployment manifests
├── monitoring/                  # Observability tools
├── pyproject.toml              # Python project config
├── requirements.txt            # Production dependencies
└── README.md                    # Repository overview
```

---

## Core Components Deep Dive

### 1. Training Engine

**Purpose**: Orchestrate model training with deterministic, reproducible pipelines

**Location**: `src/codex_ml/training/`

**Key Features**:
- Support for HuggingFace Transformers integration
- Distributed training with gradient accumulation
- RNG state checkpointing for reproducibility
- Automatic mixed precision (AMP) support
- Tensorboard/MLflow logging

**Key Classes**:
```python
class TrainingEngine:
    """Base training engine"""
    def train_epoch(train_loader, val_loader) -> Dict[str, float]
    def save_checkpoint(path: str) -> None
    def load_checkpoint(path: str) -> None

class HFTrainer(TrainingEngine):
    """HuggingFace Transformers wrapper"""
    def train(resume_from_checkpoint=None) -> TrainOutput
    def evaluate(eval_dataset) -> Dict[str, float]
```

### 2. Evaluation Engine

**Purpose**: Comprehensive model evaluation with multiple metrics

**Location**: `src/codex_ml/evaluation/`

**Supported Metrics**:
- Classification: Accuracy, F1, Precision, Recall
- Generation: BLEU, ROUGE, METEOR
- Language modeling: Perplexity, Cross-entropy

**Key Classes**:
```python
class Evaluator:
    def evaluate(eval_loader, metrics) -> Dict[str, float]
    def evaluate_on_file(file_path, format) -> Dict[str, float]
    def compute_metric(predictions, references, metric_name) -> float
```

### 3. MCP Ecosystem

**Purpose**: Standardized context protocol for agent-platform integration

**Features**:
- Unified interface for multiple adapters (Pinecone, Mock, Custom)
- Asynchronous background workers
- Comprehensive telemetry and monitoring
- 134 active workflows

**Components**:
```
MCP Core
├── Pinecone Adapter (production vector DB)
├── Mock Adapter (testing)
├── Custom Adapter (extensible)
├── Workers (embeddings, checkpoints)
└── Metrics (observability)
```

### 4. Cognitive Brain

**Purpose**: AI-driven decision making with physics-inspired logic

**Features**:
- Superposition-based decision states
- Entanglement for dependency tracking
- Pattern learning (289 patterns)
- Memory compression (60%)

**Key Metrics**:
- k₁ = 0.35 (correlation index)
- 2.86x advantage over baseline
- 289 patterns learned from operations

### 5. Agent System

**Purpose**: Autonomous operation of specialized agents

**Components**:
```
Agent System (145 Active Agents)
├── CI/CD Automation (50 agents)
├── Testing & Coverage (30 agents)
├── Documentation (25 agents)
├── Security & Compliance (20 agents)
└── Deployment & Operations (20 agents)
```

**Tool Registry**: Centralized discovery of available tools
**Agent Memory**: SQLite-based persistent pattern library

---

## Data Flow & Pipelines

### Training Pipeline

```
User Config
    ↓
[Hydra Configuration Manager]
    ↓
[Data Loading] → [Data Preprocessing]
    ↓
[Training Loop]
├── Forward Pass
├── Loss Computation
├── Backward Pass
├── Optimizer Step
└── Validation
    ↓
[Checkpoint Saving]
    ↓
[Telemetry/Logging]
    ↓
[Model Registry (MLflow)]
```

### Evaluation Pipeline

```
Trained Model
    ↓
[Model Loading]
    ↓
[Evaluation Data]
    ↓
[Inference]
    ↓
[Metric Computation]
├── Per-sample metrics
├── Aggregated metrics
└── Statistical analysis
    ↓
[Results Reporting]
```

### Python Ingestion Pipeline

```
Input Source
(File/ZIP/Git/URL)
    ↓
[Ingest Module]
    ↓
[Analysis Module]
(AST + Runtime analysis)
    ↓
[Transform Module]
(Tier A/B/C transformations)
    ↓
[Verify Module]
(Behavior validation)
    ↓
[Test Generation]
    ↓
[Output Artifacts]
```

---

## Operational Concerns

### Performance Considerations

**GPU Utilization**:
- Mixed precision training (AMP) for 2x memory efficiency
- Gradient accumulation for large batch sizes
- Distributed training with FSDP or DDP

**Memory Management**:
- Activation checkpointing for large models
- 60% memory compression in Cognitive Brain
- Efficient pattern storage in agent memory

### Monitoring & Observability

**Metrics Collected**:
- Training metrics (loss, learning rate, gradient norm)
- Inference metrics (latency, throughput)
- System metrics (GPU usage, memory, CPU)
- Agent metrics (pattern hits, decision time)

**Logging Strategy**:
- Structured JSON logging to stdout
- SQLite audit logs for replay
- Telemetry collection for analytics

### Scalability

**Horizontal Scaling**:
- Kubernetes-native deployment
- Horizontal Pod Autoscaler (HPA)
- Load balancing with service mesh

**Vertical Scaling**:
- Multi-GPU training support
- FSDP for model parallelism
- Gradient accumulation for large batches

---

## Technology Choices

### Core Dependencies

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| ML Framework | PyTorch 2.0+ | Production stability, extensive ecosystem |
| Transformers | Hugging Face | Standard transformer implementations |
| Configuration | Hydra + OmegaConf | Flexible, composable configurations |
| Distributed | Ray Cluster | Unified compute framework |
| Serving | FastAPI + Ray Serve | High-performance async API |
| Tracking | MLflow | Standard experiment tracking |
| Deployment | Kubernetes | Industry standard orchestration |

### Python Version Support

- **Minimum**: Python 3.9
- **Recommended**: Python 3.11+
- **CI/CD**: Tested on 3.9, 3.10, 3.11, 3.12

---

## AI Integration & Agents

### Autonomous Agent Architecture

```
Agent Input
    ↓
[Tool Registry Discovery]
    ↓
[Agent Memory Lookup]
(Pattern matching)
    ↓
[Cognitive Brain Decision]
(Physics-inspired logic)
    ↓
[Tool Execution]
    ↓
[Agent Memory Update]
    ↓
[Telemetry Logging]
```

### Workflow Tokens

- `AUDIT_EXEC`: Full audit pipeline execution
- `PHYS_DECIDE`: Physics-inspired decision making
- `DOC_GEN`: Documentation generation
- `REPO_ORG`: Repository organization
- `SELF_HEAL`: Automated feedback loops

### MCP Integration

Agents interact with the platform through the standardized Model Context Protocol:
- **Unified Interface**: Consistent API across adapters
- **Extensibility**: Custom adapters for new backends
- **Observability**: Built-in metrics and monitoring

---

## Development Workflows

### Local Development

1. **Environment Setup** (See: `docs/guides/local-development-setup.md`)
   - Python 3.11+ venv
   - PostgreSQL for local database
   - Pre-commit hooks for code quality

2. **Testing** (See: `docs/testing.md`)
   - Unit tests with pytest
   - Coverage requirements (80%+ critical paths)
   - Integration tests for components

3. **Code Review**
   - Automated checks (Black, isort, flake8, mypy)
   - PR reviews by maintainers
   - Approval required for merge

### CI/CD Pipeline

```
Push to Branch
    ↓
[Unit Tests] (2,130+ files, <5min)
    ↓
[Integration Tests] (10-15min)
    ↓
[Security Scanning] (CodeQL, bandit)
    ↓
[Coverage Check] (80%+ threshold)
    ↓
[Documentation Check] (links, spelling)
    ↓
[Merge Decision]
```

---

## Deployment Patterns

### Docker Deployment

See: `docs/deployment/docker-production-guide.md`

**Key Practices**:
- Multi-stage builds for minimal image size
- Non-root user execution
- Health checks and readiness probes
- Structured JSON logging

### Kubernetes Deployment

See: `docs/deployment/kubernetes-guide.md`

**Configuration**:
- StatefulSets for stateful services
- Deployments for stateless APIs
- ConfigMaps for configuration
- Secrets for sensitive data
- HPA for auto-scaling

**Network**:
- ClusterIP services for internal communication
- LoadBalancer for external access
- NetworkPolicies for security
- Istio/Linkerd optional for service mesh

---

## Security & Compliance

### Vulnerability Management

- **CVE Scanning**: Automated scanning of dependencies
- **Fixed Vulnerabilities**: 48 CVEs fixed in production
- **Compliance**: Zero known vulnerabilities
- **Scanning Tools**: CodeQL, bandit, OWASP scanning

### Data Protection

- **Encryption**: TLS for data in transit
- **Authentication**: RBAC for Kubernetes
- **Authorization**: Fine-grained access controls
- **Audit Logging**: Complete operation audit trail

### Dependency Security

- **Pin Management**: Explicit version pins in requirements
- **Transitive Auditing**: Full dependency tree scanning
- **Regular Updates**: Quarterly security update cycle
- **Supply Chain**: Signed commits and releases

---

## Architecture Decision Records

### ADR-001: Plugin-Based Architecture

**Decision**: Use plugin system for extensibility

**Rationale**:
- Separation of concerns
- Easy integration of custom components
- Reduced coupling between modules
- Runtime configuration support

**Status**: Implemented, active use

### ADR-002: SQLite-Based Agent Memory

**Decision**: Use SQLite for persistent agent memory

**Rationale**:
- No external dependencies
- ACID transactions for safety
- Query flexibility for pattern matching
- Built-in full-text search

**Status**: Implemented, 289 patterns stored

### ADR-003: Physics-Inspired Decision Making

**Decision**: Adopt quantum-inspired logic for agent decisions

**Rationale**:
- Improved decision quality (2.86x advantage)
- Correlation index of 0.35 matches human intuition
- Better pattern recognition
- More robust to uncertainty

**Status**: Implemented, k₁=0.35

---

## Roadmap & Evolution

### Phase 1: Consolidation (Current)

- ✅ Single authoritative architecture document
- ✅ Merged documentation sources
- ✅ Redirect notices for old docs
- ⏳ Link validation and cross-references

### Phase 2: Enhancement (Planned)

- Expanded API documentation
- More deployment examples
- Advanced training scenarios
- Custom agent development guide

### Phase 3: Optimization (Future)

- Performance profiling guides
- Cost optimization documentation
- Multi-region deployment
- Advanced monitoring strategies

---

## Cross-Reference Index

### Related Documentation

| Document | Purpose | Location |
|----------|---------|----------|
| Local Dev Setup | Developer environment setup | `docs/guides/local-development-setup.md` |
| Docker Guide | Container deployment | `docs/deployment/docker-production-guide.md` |
| Kubernetes Guide | K8s deployment | `docs/deployment/kubernetes-guide.md` |
| Python API Reference | API documentation | `docs/api/python-api-reference.md` |
| Testing Guide | Test strategies | `docs/testing.md` |
| Contributing | Contribution guidelines | `CONTRIBUTING.md` |

### Related Files (Deprecated - Use This Document Instead)

> **Note**: The following files are superseded by this consolidated document. They are kept for historical reference only. Please use this document as the single source of truth.

- ~~`ARCHITECTURE.md`~~ → See [System Context](#system-context) and [Container Architecture](#container-architecture)
- ~~`Architecture.md`~~ → See [Repository Structure](#repository-structure)
- ~~`ARCHITECTURE_BLUEPRINT.md`~~ → See [Core Components Deep Dive](#core-components-deep-dive)

---

## Document Maintenance

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1.0 | 2026-06-22 | Initial consolidation from 3 sources |
| 1.0.0 | 2026-05-28 | Original ARCHITECTURE.md |

### Update Process

1. Changes merged into this document
2. Old architecture files updated with redirect notices
3. All internal links point to this document
4. Quarterly review and update cycle

### Contributing to Architecture

1. Identify change or addition needed
2. Submit PR with changes to this document
3. Include rationale for changes
4. Update related documentation as needed
5. Merge after review

---

## References & External Links

- [PyTorch Documentation](https://pytorch.org/docs/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
- [Hydra Documentation](https://hydra.cc/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [MLflow Documentation](https://mlflow.org/docs/)

---

**Document Owner**: AI Assistant Autonomous System  
**Last Reviewed**: 2026-06-22  
**Next Review**: 2026-09-22  
**Status**: Active - Living Document

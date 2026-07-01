# 5-Layer Architecture Overview

**Last Updated**: 2026-01-20  
**Version**: v0.9.0  
**Status**: Production-Ready  
**Coverage**: 108+ Components

---

## Quick Reference

The Aries-Serpent/_codex_ platform is organized into **5 horizontal layers**, each handling specific responsibilities:

```mermaid
%%{init: {'accessibility': {'title': '5-Layer Architecture<br/>Layer 1: CLI/API<br/>Layer 2: ML Platform<br/>Layer 3: Data Pipeline<br/>Layer 4: Infrastructure<br/>Layer 5: Integration'}, 'theme': 'base', 'primaryColor': '#10b981', 'primaryBorderColor': '#059669', 'textColor': '#000'}}%%
graph TB
    subgraph L1["Layer 1: Interface & CLI"]
        CLI["🖥️ Command Line Interface<br/>●Hydra configuration<br/>●Command routing<br/>●Help & documentation"]
        API["📡 REST API Gateway<br/>●Endpoint definitions<br/>●Request validation<br/>●Response formatting"]
    end

    subgraph L2["Layer 2: ML Platform"]
        TRAIN["🔄 Training Engine<br/>●Model training loops<br/>●Hyperparameter tuning<br/>●Checkpoint management"]
        EVAL["📊 Evaluation Engine<br/>●Metric computation<br/>●Benchmark runs<br/>●Performance tracking"]
        SERVE["🚀 Serving/Inference<br/>●Model loading<br/>●Prediction pipeline<br/>●Batch processing"]
    end

    subgraph L3["Layer 3: Data Pipeline"]
        INGEST["📥 Code Ingestion<br/>●File parsing<br/>●AST analysis<br/>●Token counting"]
        RAG["🔍 RAG System<br/>●Vector indexing<br/>●Semantic retrieval<br/>●Context building"]
        TRANSFORM["⚙️ Data Transformation<br/>●Preprocessing<br/>●Format conversion<br/>●Feature extraction"]
    end

    subgraph L4["Layer 4: Infrastructure"]
        CONFIG["⚙️ Configuration<br/>●Hydra composition<br/>●Secret management<br/>●Environment handling"]
        DB["💾 Database Layer<br/>●Session storage<br/>●Checkpoint persistence<br/>●Metadata management"]
        CACHE["⚡ Caching<br/>●Result caching<br/>●Model cache<br/>●Embedding cache"]
        MONITOR["📈 Monitoring<br/>●Metrics collection<br/>●Health checks<br/>●Alerts & notifications"]
    end

    subgraph L5["Layer 5: Integration"]
        GH["🐙 GitHub Integration<br/>●PR automation<br/>●Issue management<br/>●Workflow triggers"]
        ZENDESK["🎫 Zendesk Integration<br/>●Ticket sync<br/>●Customer support<br/>●CRM integration"]
        CLOUD["☁️ Cloud Services<br/>●Storage backends<br/>●Compute resources<br/>●API services"]
        AUTH["🔐 Auth & Security<br/>●User authentication<br/>●Access control<br/>●Audit logging"]
    end

    %% Dependencies flow upward
    API --> TRAIN
    API --> EVAL
    API --> SERVE
    CLI --> TRAIN
    CLI --> EVAL
    CLI --> SERVE

    TRAIN --> INGEST
    TRAIN --> RAG
    TRAIN --> TRANSFORM
    EVAL --> RAG
    EVAL --> TRANSFORM
    SERVE --> RAG

    INGEST --> CONFIG
    RAG --> DB
    TRANSFORM --> CACHE

    TRAIN --> MONITOR
    EVAL --> MONITOR
    SERVE --> MONITOR

    GH -.integration.-> TRAIN
    GH -.integration.-> EVAL
    ZENDESK -.integration.-> SERVE
    CLOUD -.backend.-> DB
    CLOUD -.backend.-> CACHE
    AUTH -.security.-> API

    %% Styling
    style L1 fill:#e0f2fe,stroke:#0284c7,stroke-width:2px
    style L2 fill:#dcfce7,stroke:#16a34a,stroke-width:2px
    style L3 fill:#fef3c7,stroke:#d97706,stroke-width:2px
    style L4 fill:#fce7f3,stroke:#db2777,stroke-width:2px
    style L5 fill:#f3e8ff,stroke:#7c3aed,stroke-width:2px

    style CLI fill:#0284c7,stroke:#075985,stroke-width:2px,color:#fff
    style API fill:#0284c7,stroke:#075985,stroke-width:2px,color:#fff
    style TRAIN fill:#16a34a,stroke:#15803d,stroke-width:2px,color:#fff
    style EVAL fill:#16a34a,stroke:#15803d,stroke-width:2px,color:#fff
    style SERVE fill:#16a34a,stroke:#15803d,stroke-width:2px,color:#fff
    style INGEST fill:#d97706,stroke:#b45309,stroke-width:2px,color:#fff
    style RAG fill:#d97706,stroke:#b45309,stroke-width:2px,color:#fff
    style TRANSFORM fill:#d97706,stroke:#b45309,stroke-width:2px,color:#fff
    style CONFIG fill:#db2777,stroke:#9f1239,stroke-width:2px,color:#fff
    style DB fill:#db2777,stroke:#9f1239,stroke-width:2px,color:#fff
    style CACHE fill:#db2777,stroke:#9f1239,stroke-width:2px,color:#fff
    style MONITOR fill:#db2777,stroke:#9f1239,stroke-width:2px,color:#fff
    style GH fill:#7c3aed,stroke:#6d28d9,stroke-width:2px,color:#fff
    style ZENDESK fill:#7c3aed,stroke:#6d28d9,stroke-width:2px,color:#fff
    style CLOUD fill:#7c3aed,stroke:#6d28d9,stroke-width:2px,color:#fff
    style AUTH fill:#7c3aed,stroke:#6d28d9,stroke-width:2px,color:#fff
```

---

## Layer Descriptions

### Layer 1: Interface & CLI 🖥️
**Responsibility**: User interaction and request entry points  
**Key Components**:
- **CLI** - Command-line interface with Hydra-based configuration management
- **REST API** - HTTP endpoint gateway for programmatic access
- **Command Routing** - Routes commands to appropriate layer 2 engines

**Typical Flow**:
```
User Command → CLI Parser → Hydra Config → Layer 2 (Training/Eval/Serving)
```

**Technologies**: Click, Hydra, FastAPI

---

### Layer 2: ML Platform 🔄
**Responsibility**: Core machine learning operations  
**Key Components**:
- **Training Engine** - Model training with checkpoint management
- **Evaluation Engine** - Metrics computation and benchmark execution
- **Serving/Inference** - Model loading and prediction pipelines

**Typical Flow**:
```
Config → Model Architecture → Training Loop → Checkpoints → Evaluation → Metrics
```

**Technologies**: PyTorch, Ray, MLflow

---

### Layer 3: Data Pipeline 📥
**Responsibility**: Data ingestion, transformation, and retrieval  
**Key Components**:
- **Code Ingestion** - Parses source files and generates ASTs
- **RAG System** - Builds vector indices and retrieves relevant context
- **Transformation** - Preprocesses and transforms data formats

**Typical Flow**:
```
Raw Files → AST Analysis → Token Encoding → Vector Embedding → Storage
Query → Semantic Search → Ranking → Context Assembly → Return
```

**Technologies**: tokenizers, transformers, FAISS/Pinecone, SentenceBERT

---

### Layer 4: Infrastructure ⚙️
**Responsibility**: System support, persistence, and observability  
**Key Components**:
- **Configuration** - Hydra composition and secret management
- **Database** - Session/checkpoint/metadata persistence
- **Caching** - Results, model, and embedding caches
- **Monitoring** - Metrics, health checks, alerts

**Typical Flow**:
```
Config Files → Hydra Composition → Validated Config → Layer 2/3 Operations
Operations → Metrics → Monitoring Stack → Alerts/Dashboards
```

**Technologies**: OmegaConf, SQLite, Redis/Memcached, Prometheus

---

### Layer 5: Integration 🔌
**Responsibility**: External system connections  
**Key Components**:
- **GitHub Integration** - PR automation, issue management
- **Zendesk Integration** - CRM and support ticket sync
- **Cloud Services** - Storage, compute, API services
- **Auth & Security** - User management and access control

**Typical Flow**:
```
External Trigger (GitHub PR) → Validation → Layer 1-4 Processing → Update External System
```

**Technologies**: GitHub API, Zendesk API, Cloud SDKs, OAuth/JWT

---

## Data Flow Through Layers

```mermaid
graph LR
    U["👤 User/System"] -->|"Input<br/>(command/API)"| L1["Layer 1<br/>Interface"]
    L1 -->|"Validated<br/>Request"| L2["Layer 2<br/>ML Platform"]
    L2 -->|"Data Need"| L3["Layer 3<br/>Data Pipeline"]
    L3 -->|"Processed<br/>Data"| L2
    L2 -->|"Metrics/Model"| L4["Layer 4<br/>Infrastructure"]
    L4 -->|"Stored<br/>State"| L2
    L2 -->|"Results"| L1
    L1 -->|"Output<br/>(response)"| U
    L2 -.->|"Events"| L5["Layer 5<br/>Integration"]
    L5 -.->|"External<br/>Updates"| U

    style U fill:#f0f0f0,stroke:#333,stroke-width:2px
    style L1 fill:#e0f2fe,stroke:#0284c7,stroke-width:2px
    style L2 fill:#dcfce7,stroke:#16a34a,stroke-width:2px
    style L3 fill:#fef3c7,stroke:#d97706,stroke-width:2px
    style L4 fill:#fce7f3,stroke:#db2777,stroke-width:2px
    style L5 fill:#f3e8ff,stroke:#7c3aed,stroke-width:2px
```

---

## Component Inventory by Layer

| Layer | Component | Status | Docs |
|-------|-----------|--------|------|
| **L1** | CLI | ✅ Production | [docs/cli](../cli/) |
| **L1** | API Gateway | ✅ Production | [docs/api](../api/) |
| **L2** | Training Engine | ✅ Production | [docs/training](../training/) |
| **L2** | Evaluation Engine | ✅ Production | [docs/evaluation](../evaluation/) |
| **L2** | Serving | ✅ Production | [docs/serving](../serving/) |
| **L3** | Code Ingestion | ✅ Production | [docs/ingestion](../ingestion/) |
| **L3** | RAG System | ✅ Production | [docs/rag](../rag/) |
| **L3** | Data Transform | ✅ Production | [docs/transformation](../transformation/) |
| **L4** | Configuration | ✅ Production | [docs/configuration](../configuration/) |
| **L4** | Database | ✅ Production | [docs/database](../database/) |
| **L4** | Caching | ✅ Production | [docs/caching](../caching/) |
| **L4** | Monitoring | ✅ Production | [docs/monitoring](../monitoring/) |
| **L5** | GitHub Integration | ✅ Production | [docs/integration](../integration/) |
| **L5** | Zendesk Integration | ✅ Production | [docs/zendesk](../zendesk/) |
| **L5** | Cloud Services | ✅ Production | [docs/cloud](../cloud/) |
| **L5** | Auth & Security | ✅ Production | [docs/security](../security/) |

---

## Key Design Principles

1. **Separation of Concerns** - Each layer has a single responsibility
2. **Layered Dependency** - Higher layers depend on lower layers, not vice versa
3. **Modularity** - Components within layers are independently testable
4. **Scalability** - Each layer can scale independently based on demand
5. **Observability** - Layer 4 provides insights into all other layers

---

## Next Steps

- 👉 See [System Context Diagram](SYSTEM_CONTEXT.md) for user/external system perspective
- 👉 See [End-to-End Request Flow](E2E_REQUEST_FLOW.md) for request lifecycle
- 👉 See [Component Dependencies](COMPONENT_DEPENDENCIES.md) for module relationships
- 👉 See individual layer docs for detailed architecture

---

**Related Documentation**:
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Full architecture documentation
- [CODEBASE_MERMAID_MAPS.md](../CODEBASE_MERMAID_MAPS.md) - All system diagrams
- [System Context](SYSTEM_CONTEXT.md) - C4 Context diagram

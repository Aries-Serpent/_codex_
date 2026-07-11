# Component Dependencies
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Last Updated**: 2026-01-20  
**Version**: v0.9.0  
**Total Components**: 57 modules across 5 layers

---

## Dependency Graph Overview

```mermaid
%%{init: {'accessibility': {'title': 'Component Dependencies<br/>Module Relationships'}, 'theme': 'base'}}%%
graph TB
    subgraph L1["Layer 1: Interface"]
        CLI["cli"]
        API["api"]
    end

    subgraph L2["Layer 2: ML Platform"]
        TRAIN["train"]
        EVAL["eval"]
        SERVE["serve"]
    end

    subgraph L3["Layer 3: Data Pipeline"]
        INGEST["ingest"]
        RAG["rag"]
        TRANSFORM["transform"]
    end

    subgraph L4["Layer 4: Infrastructure"]
        CONFIG["config"]
        DB["db"]
        CACHE["cache"]
        MONITOR["monitor"]
        LOG["logging"]
    end

    subgraph L5["Layer 5: Integration"]
        GH["github"]
        ZD["zendesk"]
        CLOUD["cloud"]
        AUTH["auth"]
    end

    %% Interface depends on ML Platform
    CLI --> TRAIN
    CLI --> EVAL
    CLI --> SERVE
    API --> TRAIN
    API --> EVAL
    API --> SERVE

    %% ML Platform depends on Data Pipeline
    TRAIN --> INGEST
    TRAIN --> RAG
    TRAIN --> TRANSFORM
    EVAL --> RAG
    EVAL --> TRANSFORM
    SERVE --> RAG

    %% Data Pipeline depends on Infrastructure
    INGEST --> CONFIG
    INGEST --> DB
    INGEST --> LOG
    RAG --> CONFIG
    RAG --> DB
    RAG --> CACHE
    RAG --> LOG
    TRANSFORM --> CONFIG
    TRANSFORM --> LOG

    %% ML Platform depends on Infrastructure
    TRAIN --> CONFIG
    TRAIN --> DB
    TRAIN --> CACHE
    TRAIN --> MONITOR
    TRAIN --> LOG
    EVAL --> CONFIG
    EVAL --> DB
    EVAL --> MONITOR
    EVAL --> LOG
    SERVE --> CONFIG
    SERVE --> CACHE
    SERVE --> MONITOR
    SERVE --> LOG

    %% Integration depends on everything
    GH -.audit.-> MONITOR
    ZD -.audit.-> MONITOR
    CLOUD -.backup.-> DB
    CLOUD -.backup.-> CACHE
    AUTH -.secures.-> API

    %% Infrastructure internal deps
    LOG --> DB
    MONITOR --> LOG
    CACHE --> CONFIG

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
    style LOG fill:#db2777,stroke:#9f1239,stroke-width:2px,color:#fff
    style GH fill:#7c3aed,stroke:#6d28d9,stroke-width:2px,color:#fff
    style ZD fill:#7c3aed,stroke:#6d28d9,stroke-width:2px,color:#fff
    style CLOUD fill:#7c3aed,stroke:#6d28d9,stroke-width:2px,color:#fff
    style AUTH fill:#7c3aed,stroke:#6d28d9,stroke-width:2px,color:#fff
```

---

## Dependency Analysis

### Core Dependencies (Foundation)

**Layer 4 (Infrastructure)** - No external dependencies
- `config` ← Hydra, OmegaConf
- `db` ← SQLite/PostgreSQL
- `cache` ← Redis/Memcached
- `monitor` ← Prometheus, Grafana
- `logging` ← Python logging

**Layer 3 (Data)** - Depends on Layer 4
- `ingest` → config, db, logging
- `rag` → config, db, cache, logging
- `transform` → config, logging

**Layer 2 (ML)** - Depends on Layer 3 & 4
- `train` → ingest, rag, transform, config, db, cache, monitor, logging
- `eval` → rag, transform, config, db, monitor, logging
- `serve` → rag, config, cache, monitor, logging

**Layer 1 (Interface)** - Depends on Layer 2
- `cli` → train, eval, serve
- `api` → train, eval, serve

**Layer 5 (Integration)** - Cross-cutting
- `github` → monitor, any layer (async)
- `zendesk` → monitor, logging (async)
- `cloud` → db, cache (backup)
- `auth` → api, config (security)

---

## Module Inventory by Layer

### Layer 1: Interface (2 modules)
```
cli/              - Command-line interface
  ├── cli.py      - Main CLI dispatcher
  ├── commands/   - Command handlers
  └── config_cli/ - Config management

api/              - REST API
  ├── api.py      - FastAPI app
  ├── routes/     - Endpoint handlers
  └── schemas/    - Request/response models
```

### Layer 2: ML Platform (3 modules)
```
train/            - Training engine
  ├── trainer.py  - Main trainer
  ├── loop.py     - Training loop
  └── checkpoint/ - Model checkpointing

eval/             - Evaluation engine
  ├── evaluator.py - Metrics computation
  └── metrics/    - Metric definitions

serve/            - Serving/inference
  ├── server.py   - Inference server
  ├── predict.py  - Prediction pipeline
  └── batching/   - Batch prediction
```

### Layer 3: Data Pipeline (3 modules)
```
ingest/           - Code ingestion
  ├── parser.py   - File parsing
  ├── ast_gen.py  - AST generation
  └── tokenizer/  - Tokenization

rag/              - RAG system
  ├── indexer.py  - Vector indexing
  ├── retriever.py - Semantic search
  └── ranker.py   - Result ranking

transform/        - Data transformation
  ├── preprocessor.py - Data prep
  ├── formatter.py    - Format conversion
  └── extractor.py    - Feature extraction
```

### Layer 4: Infrastructure (4 modules)
```
config/           - Configuration
  ├── loader.py   - Hydra loading
  ├── validator.py - Schema validation
  └── secrets.py  - Secret management

db/               - Database layer
  ├── session.py  - SQLite/PostgreSQL
  ├── models.py   - ORM models
  └── migrations/ - Database migrations

cache/            - Caching layer
  ├── redis.py    - Redis client
  ├── memcached.py- Memcached client
  └── local.py    - Local cache

monitor/          - Monitoring
  ├── metrics.py  - Metrics collection
  ├── health.py   - Health checks
  └── alerts.py   - Alert engine

logging/          - Structured logging
  ├── logger.py   - Log setup
  ├── formatters/ - Log formatting
  └── handlers/   - Log handlers
```

### Layer 5: Integration (4 modules)
```
github/           - GitHub integration
  ├── client.py   - GitHub API wrapper
  ├── pr.py       - PR operations
  └── workflows/  - Workflow triggers

zendesk/          - Zendesk integration
  ├── client.py   - Zendesk API wrapper
  ├── tickets.py  - Ticket operations
  └── sync.py     - CRM synchronization

cloud/            - Cloud storage
  ├── s3.py       - AWS S3 integration
  ├── gcs.py      - Google Cloud
  └── azure.py    - Azure integration

auth/             - Authentication
  ├── oauth.py    - OAuth2/GitHub
  ├── jwt.py      - JWT tokens
  └── rbac.py     - Role-based access
```

---

## Dependency Patterns

### Pattern 1: Config Injection
All modules depend on `config` for settings:
```
Any Module
  ├── Get config from config module
  ├── Validate schema
  ├── Apply defaults
  └── Use configuration
```

### Pattern 2: Logging Throughout
All modules use `logging` for observability:
```
Any Module
  ├── Create logger instance
  ├── Log at key decision points
  ├── Include context
  └── Send to configured handlers
```

### Pattern 3: Monitoring Integration
ML Platform modules report metrics:
```
train/eval/serve
  ├── During execution
  ├── Emit metrics to monitor
  ├── Track timing
  └── Report errors
```

### Pattern 4: Database Persistence
Data operations use `db` for storage:
```
ingest/rag/transform
  ├── Prepare data
  ├── Store in database
  ├── Query when needed
  └── Maintain indexes
```

### Pattern 5: Cache Acceleration
High-frequency operations use `cache`:
```
rag (retrieval)
  ├── Check cache for similar queries
  ├── Return cached result if hit
  ├── Fall back to DB/compute if miss
  └── Cache result for future use
```

---

## Critical Path Analysis

**Longest dependency chain** (for any request):

```
CLI Command
  → train (L2)
    → ingest (L3)
      → config (L4)  [critical path]
      → db (L4)
      → logging (L4) ← all serialize to DB
```

**Slowest I/O dependencies**:
1. `ingest` → `db` (file I/O + SQL queries)
2. `rag` → `db` (large vector searches)
3. `serve` → `cache` (fallback if cache miss)
4. `monitor` → `db` (append-only logs)

---

## Next Steps

- 👉 See [5-Layer Architecture](../architecture/5_LAYER_ARCHITECTURE.md) for layer structure
- 👉 See module-specific docs for detailed component architectures
- 👉 Review source code for performance optimization patterns

---

**Related Documentation**:
- [5-Layer Architecture](../architecture/5_LAYER_ARCHITECTURE.md) - System layers
- [ARCHITECTURE.md](./INDEX.md) - Full architecture

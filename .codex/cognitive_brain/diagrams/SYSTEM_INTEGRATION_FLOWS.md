# 🔄 System Integration Flow Diagrams
> **Version**: 2.1.0
> **Generated**: 2026-01-11T10:00:00Z
> **Last updated**: 2026-05-14T00:30Z (S1003-ctep — agent count 153, CI self-healing hardened)
> **Purpose**: Complete flow diagrams for all system integrations

---

## 1. Complete Agent Orchestration Flow

```mermaid
flowchart TB
    subgraph "External Triggers"
        T_USER[User Request]
        T_PR[Pull Request]
        T_CI[CI Event]
        T_SCHED[Scheduled Job]
    end

    subgraph "Gateway Layer"
        GW_API[API Gateway<br/>FastAPI]
        GW_GH[GitHub Webhook<br/>Handler]
        GW_CLI[CLI Interface<br/>Click]
    end

    subgraph "Orchestration Layer"
        ORCH_MAIN[Main Orchestrator<br/>developer_orchestrator.py]
        ORCH_PHYS[Physics Orchestrator<br/>physics_orchestrator.py]
        ORCH_WF[Workflow Navigator<br/>workflow_navigator.py]
    end

    subgraph "Agent Layer"
        AG_RAG[RAG Agent<br/>rag_ticket_context.py]
        AG_KB[Knowledge Agent<br/>knowledge_base_integrator.py]
        AG_QGT[Quantum Agent<br/>quantum_game_theory.py]
        AG_SH[Self-Healing<br/>self_healing.py]
    end

    subgraph "Custom Agents (153 active — see AGENTS.md)"
        CA_TAU[Test Alignment Fixer<br/>test-alignment-fixer]
        CA_CLV[CI Testing Agent<br/>ci-testing-agent]
        CA_SAR[CodeQL Alert Resolution<br/>codeql-alert-resolution-agent]
        CA_CFD[CI Failure Resolution<br/>ci-failure-resolution-agent]
        CA_COV[Unified Coverage Agent<br/>unified-coverage-agent]
        CA_SEC[Unified Security Scanner<br/>unified-security-scanner]
    end

    subgraph "Core Services"
        SVC_RAG[RAG Service<br/>src/codex/rag/]
        SVC_ML[ML Service<br/>src/codex/ml/]
        SVC_BRAIN[Cognitive Brain<br/>src/cognitive_brain/]
    end

    subgraph "Data Layer"
        DB_CACHE[Cache<br/>LRU+TTL]
        DB_INDEX[Vector Index<br/>FAISS]
        DB_STATE[State Store<br/>File/Redis]
    end

    T_USER --> GW_API
    T_PR --> GW_GH
    T_CI --> GW_GH
    T_SCHED --> ORCH_MAIN

    GW_API --> ORCH_MAIN
    GW_GH --> ORCH_MAIN
    GW_CLI --> ORCH_MAIN

    ORCH_MAIN --> ORCH_PHYS
    ORCH_MAIN --> ORCH_WF

    ORCH_WF --> AG_RAG
    ORCH_WF --> AG_KB
    ORCH_PHYS --> AG_QGT
    ORCH_MAIN --> AG_SH

    AG_SH -.->|Triggers| CA_TAU
    AG_SH -.->|Triggers| CA_CLV
    AG_SH -.->|Triggers| CA_SAR
    AG_SH -.->|Triggers| CA_CFD
    AG_SH -.->|Triggers| CA_COV
    AG_SH -.->|Triggers| CA_SEC

    AG_RAG --> SVC_RAG
    AG_KB --> SVC_ML
    AG_QGT --> SVC_BRAIN

    SVC_RAG --> DB_CACHE
    SVC_RAG --> DB_INDEX
    SVC_BRAIN --> DB_STATE
```

---

## 2. RAG Pipeline Data Flow

```mermaid
flowchart LR
    subgraph "Input"
        IN_QUERY[User Query]
        IN_DOC[Documents]
        IN_CTX[Context]
    end

    subgraph "Preprocessing"
        PRE_CHUNK[Chunker<br/>Split Text]
        PRE_CLEAN[Cleaner<br/>Normalize]
        PRE_TOK[Tokenizer<br/>Encode]
    end

    subgraph "Embedding Layer"
        EMB_MODEL[SentenceTransformer<br/>all-MiniLM-L6-v2]
        EMB_CACHE[Embedding Cache<br/>LRU + TTL]
        EMB_BATCH[Batch Processor<br/>Async]
    end

    subgraph "Retrieval Layer"
        RET_INDEX[Vector Index<br/>FAISS/Annoy]
        RET_SEARCH[Semantic Search<br/>Top-K]
        RET_RERANK[Reranker<br/>Cross-Encoder]
    end

    subgraph "Generation Layer"
        GEN_PROMPT[Prompt Builder<br/>Templates]
        GEN_LLM[LLM API<br/>OpenAI/Local]
        GEN_POST[Post-Process<br/>Format]
    end

    subgraph "Output"
        OUT_RESP[Response]
        OUT_CITE[Citations]
        OUT_META[Metadata]
    end

    IN_QUERY --> PRE_CLEAN
    IN_DOC --> PRE_CHUNK
    IN_CTX --> PRE_CLEAN

    PRE_CHUNK --> PRE_TOK
    PRE_CLEAN --> PRE_TOK

    PRE_TOK --> EMB_MODEL
    EMB_MODEL --> EMB_CACHE
    EMB_CACHE --> EMB_BATCH

    EMB_BATCH --> RET_INDEX
    RET_INDEX --> RET_SEARCH
    RET_SEARCH --> RET_RERANK

    RET_RERANK --> GEN_PROMPT
    GEN_PROMPT --> GEN_LLM
    GEN_LLM --> GEN_POST

    GEN_POST --> OUT_RESP
    GEN_POST --> OUT_CITE
    GEN_POST --> OUT_META
```

---

## 3. Rust-Python Bridge Architecture

```mermaid
flowchart TB
    subgraph "Python Layer"
        PY_API[Python API<br/>codex_engine module]
        PY_BRIDGE[bridge_protocol_v2.py<br/>Protocol Handler]
        PY_TYPES[bridge_types.py<br/>Type Definitions]
    end

    subgraph "FFI Bridge"
        FFI_PYMOD[PyO3 Module<br/>lib.rs]
        FFI_SERDE[Serialization<br/>serde_json]
        FFI_ERROR[Error Handling<br/>PyResult]
    end

    subgraph "Rust Core"
        RS_ENGINE[Swarm Engine<br/>swarm_engine.rs]
        RS_TASK[Task Manager<br/>task_manager.rs]
        RS_QUEUE[Queue System<br/>queue.rs]
        RS_STATE[State Machine<br/>state.rs]
    end

    subgraph "Performance Layer"
        PERF_ASYNC[Async Runtime<br/>tokio]
        PERF_POOL[Thread Pool<br/>rayon]
        PERF_CACHE[Memory Cache<br/>hashmap]
    end

    PY_API --> PY_BRIDGE
    PY_BRIDGE --> PY_TYPES
    PY_TYPES --> FFI_PYMOD

    FFI_PYMOD --> FFI_SERDE
    FFI_SERDE --> FFI_ERROR

    FFI_ERROR --> RS_ENGINE
    RS_ENGINE --> RS_TASK
    RS_TASK --> RS_QUEUE
    RS_QUEUE --> RS_STATE

    RS_ENGINE --> PERF_ASYNC
    RS_TASK --> PERF_POOL
    RS_STATE --> PERF_CACHE
```

---

## 4. CI/CD Complete Pipeline

```mermaid
flowchart TB
    subgraph "Source Control"
        GIT_PUSH[Git Push]
        GIT_PR[Pull Request]
        GIT_TAG[Git Tag]
    end

    subgraph "Trigger Phase"
        TR_VALIDATE[Validate Trigger]
        TR_CHECKOUT[Checkout Code]
        TR_CACHE[Restore Cache]
    end

    subgraph "Quality Phase"
        Q_LINT[Linting<br/>Ruff + Black]
        Q_TYPE[Type Check<br/>mypy]
        Q_FORMAT[Format Check<br/>isort]
    end

    subgraph "Security Phase"
        S_DEPS[Dependency Scan<br/>pip-audit]
        S_SAST[Static Analysis<br/>Semgrep + CodeQL]
        S_SECRETS[Secret Scan<br/>git-secrets]
        S_CARGO[Rust Audit<br/>cargo audit]
    end

    subgraph "Test Phase"
        T_UNIT[Unit Tests<br/>pytest]
        T_INT[Integration Tests<br/>pytest-docker]
        T_E2E[E2E Tests<br/>Playwright]
        T_RUST[Rust Tests<br/>cargo test]
    end

    subgraph "Build Phase"
        B_PYTHON[Python Wheel<br/>build]
        B_RUST[Rust Binary<br/>maturin]
        B_DOCS[Documentation<br/>MkDocs]
        B_DOCKER[Docker Image<br/>Buildx]
    end

    subgraph "Deploy Phase (TBD)"
        D_STAGING[Staging Deploy<br/>Preview]
        D_SMOKE[Smoke Tests<br/>Health Check]
        D_PROD[Production Deploy<br/>Blue/Green]
    end

    GIT_PUSH --> TR_VALIDATE
    GIT_PR --> TR_VALIDATE
    GIT_TAG --> TR_VALIDATE

    TR_VALIDATE --> TR_CHECKOUT
    TR_CHECKOUT --> TR_CACHE

    TR_CACHE --> Q_LINT
    Q_LINT --> Q_TYPE
    Q_TYPE --> Q_FORMAT

    Q_FORMAT --> S_DEPS
    S_DEPS --> S_SAST
    S_SAST --> S_SECRETS
    S_SECRETS --> S_CARGO

    S_CARGO --> T_UNIT
    T_UNIT --> T_INT
    T_INT --> T_E2E
    T_E2E --> T_RUST

    T_RUST --> B_PYTHON
    B_PYTHON --> B_RUST
    B_RUST --> B_DOCS
    B_DOCS --> B_DOCKER

    B_DOCKER -.-> D_STAGING
    D_STAGING -.-> D_SMOKE
    D_SMOKE -.-> D_PROD
```

---

## 5. Custom Agent Implementation Architecture

```mermaid
flowchart TB
    subgraph "Agent Registry"
        REG_CONFIG[Agent Configs<br/>.github/agents/*/agent.yaml]
        REG_PROMPTS[Prompt Templates<br/>.github/agents/*/prompts/]
        REG_CATALOG[Agent Catalog<br/>CUSTOM_AGENTS_CATALOG.md]
    end

    subgraph "test-assertion-updater"
        TAU_PARSE[Failure Parser<br/>Extract Errors]
        TAU_ANALYZE[AST Analyzer<br/>Python/libcst]
        TAU_GEN[Fix Generator<br/>Assertion Update]
        TAU_VALID[Property Validator<br/>Hypothesis]
    end

    subgraph "cache-logic-validator"
        CLV_PROP[Property Generator<br/>Hypothesis]
        CLV_TEST[Cache Tester<br/>Concurrent Access]
        CLV_REPORT[Report Generator<br/>Coverage Map]
    end

    subgraph "security-advisory-resolver"
        SAR_SCAN[Advisory Scanner<br/>cargo audit + pip-audit]
        SAR_ANALYZE[Impact Analyzer<br/>Dependency Tree]
        SAR_FIX[Fix Generator<br/>Version Bumps]
    end

    subgraph "ci-failure-diagnostician"
        CFD_PARSE[Log Parser<br/>Regex + Patterns]
        CFD_CLASS[Failure Classifier<br/>Flaky/Real/Infra]
        CFD_FIX[Fix Suggester<br/>Pattern Match]
    end

    subgraph "Integration Points"
        INT_GH[GitHub Actions<br/>Workflow Dispatch]
        INT_BRAIN[Cognitive Brain<br/>Pattern Storage]
        INT_PR[PR Comments<br/>Status Updates]
    end

    REG_CONFIG --> TAU_PARSE
    REG_CONFIG --> CLV_PROP
    REG_CONFIG --> SAR_SCAN
    REG_CONFIG --> CFD_PARSE

    TAU_PARSE --> TAU_ANALYZE
    TAU_ANALYZE --> TAU_GEN
    TAU_GEN --> TAU_VALID

    CLV_PROP --> CLV_TEST
    CLV_TEST --> CLV_REPORT

    SAR_SCAN --> SAR_ANALYZE
    SAR_ANALYZE --> SAR_FIX

    CFD_PARSE --> CFD_CLASS
    CFD_CLASS --> CFD_FIX

    TAU_VALID --> INT_GH
    CLV_REPORT --> INT_GH
    SAR_FIX --> INT_GH
    CFD_FIX --> INT_GH

    INT_GH --> INT_BRAIN
    INT_GH --> INT_PR
```

---

## 6. Cognitive Brain Knowledge Graph

```mermaid
flowchart TB
    subgraph "Knowledge Sources"
        KS_CODE[Source Code<br/>AST Analysis]
        KS_TEST[Test Results<br/>pytest/cargo]
        KS_CI[CI Logs<br/>GitHub Actions]
        KS_PR[PR History<br/>Comments/Reviews]
    end

    subgraph "Pattern Extraction"
        PE_PARSE[Log Parser<br/>Structure Extract]
        PE_LEARN[Pattern Learner<br/>Frequency Analysis]
        PE_VALIDATE[Pattern Validator<br/>Cross-Reference]
    end

    subgraph "Knowledge Base"
        KB_PATTERNS[Patterns<br/>Best Practices]
        KB_ANTI[Anti-Patterns<br/>Avoid These]
        KB_ERRORS[Error Catalog<br/>Solutions]
        KB_METRICS[Metrics<br/>Performance Data]
    end

    subgraph "Application Layer"
        APP_SUGGEST[Suggestion Engine<br/>Recommendations]
        APP_FIX[Auto-Fix Engine<br/>Apply Patterns]
        APP_REPORT[Report Generator<br/>Dashboards]
    end

    KS_CODE --> PE_PARSE
    KS_TEST --> PE_PARSE
    KS_CI --> PE_PARSE
    KS_PR --> PE_PARSE

    PE_PARSE --> PE_LEARN
    PE_LEARN --> PE_VALIDATE

    PE_VALIDATE --> KB_PATTERNS
    PE_VALIDATE --> KB_ANTI
    PE_VALIDATE --> KB_ERRORS
    PE_VALIDATE --> KB_METRICS

    KB_PATTERNS --> APP_SUGGEST
    KB_ANTI --> APP_FIX
    KB_ERRORS --> APP_FIX
    KB_METRICS --> APP_REPORT
```

---

## 7. End-to-End Request Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend as Cognitive App
    participant API as API Gateway
    participant Orch as Orchestrator
    participant RAG as RAG Service
    participant ML as ML Pipeline
    participant Brain as Cognitive Brain
    participant Rust as Rust Engine

    User->>Frontend: Submit Query
    Frontend->>API: POST /api/query
    API->>Orch: Process Request

    Orch->>Brain: Check Pattern Cache
    Brain-->>Orch: Cached Patterns

    Orch->>RAG: Retrieve Context
    RAG->>ML: Generate Embeddings
    ML->>Rust: Batch Processing
    Rust-->>ML: Processed Vectors
    ML-->>RAG: Embeddings
    RAG-->>Orch: Context Documents

    Orch->>API: Generate Response
    API-->>Frontend: Response JSON
    Frontend-->>User: Display Results

    Note over Brain: Async Pattern Learning
    Orch->>Brain: Log Interaction
    Brain->>Brain: Update Patterns
```

---

## 8. Deployment Topology (TBD)

```mermaid
flowchart TB
    subgraph "Edge Layer"
        CDN[CloudFlare CDN<br/>Static Assets]
        WAF[Web Application Firewall<br/>OWASP Rules]
    end

    subgraph "Load Balancer"
        LB1[Primary LB<br/>NGINX]
        LB2[Failover LB<br/>HAProxy]
    end

    subgraph "Application Cluster"
        APP1[Codex Pod 1<br/>Python + Rust]
        APP2[Codex Pod 2<br/>Python + Rust]
        APP3[Codex Pod 3<br/>Python + Rust]
    end

    subgraph "Cache Layer"
        REDIS1[Redis Primary<br/>Session + Cache]
        REDIS2[Redis Replica<br/>Read Replicas]
    end

    subgraph "Database Layer"
        PG1[PostgreSQL Primary<br/>Write Master]
        PG2[PostgreSQL Replica<br/>Read Replicas]
        VDB[Vector Database<br/>Pinecone/Weaviate]
    end

    subgraph "Storage"
        S3[Object Storage<br/>Models + Assets]
        EFS[Elastic Filesystem<br/>Logs + Data]
    end

    subgraph "Observability"
        PROM[Prometheus<br/>Metrics]
        LOKI[Loki<br/>Logs]
        TEMPO[Tempo<br/>Traces]
        GRAF[Grafana<br/>Dashboards]
    end

    CDN --> WAF
    WAF --> LB1
    WAF --> LB2

    LB1 --> APP1
    LB1 --> APP2
    LB1 --> APP3
    LB2 --> APP1
    LB2 --> APP2
    LB2 --> APP3

    APP1 --> REDIS1
    APP2 --> REDIS1
    APP3 --> REDIS1
    REDIS1 --> REDIS2

    APP1 --> PG1
    APP2 --> PG1
    APP3 --> PG1
    PG1 --> PG2

    APP1 --> VDB

    APP1 --> S3
    APP2 --> S3
    APP3 --> S3

    APP1 --> EFS
    APP2 --> EFS
    APP3 --> EFS

    APP1 --> PROM
    APP2 --> PROM
    APP3 --> PROM
    PROM --> GRAF
    LOKI --> GRAF
    TEMPO --> GRAF
```

---

## Legend

| Symbol | Meaning |
|--------|---------|
| Solid Arrow | Active Connection |
| Dashed Arrow | Planned/TBD Connection |
| Green Fill | Production Ready |
| Yellow Fill | In Progress |
| Gray Fill | TBD (Future) |

---

*Generated by CI Testing Agent - System Integration Diagrams*
*Last updated: 2026-05-14 (S1003-ctep) — v2.1.0*

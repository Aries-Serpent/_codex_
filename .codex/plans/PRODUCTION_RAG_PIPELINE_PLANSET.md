# Production RAG Pipeline Implementation Planset

**Created:** 2026-01-16  
**Updated:** 2026-01-16  
**Status:** 🔄 IN PROGRESS - Phase 1 & 2 Complete  
**Priority:** HIGH (Long-term production readiness)  
**Agent Type:** AI Agent (fully autonomous execution)  
**Policy Compliance:** AI Agency Policy v1.0.0

---

## Implementation Progress

### ✅ Phase 1: Document Ingestion Pipeline (COMPLETE)

**Implemented:**
- `src/codex/rag/ingestion/validator.py` - Document validation (24 tests passing)
- `src/codex/rag/ingestion/preprocessor.py` - Text preprocessing (26 tests passing)
- `src/codex/rag/ingestion/chunker.py` - Chunking strategies (26 tests passing)
- `src/codex/rag/ingestion/pipeline.py` - Batch ingestion (28 tests passing)
- `tests/rag/ingestion/` - Comprehensive test suite (104 tests total)

**Features:**
- Document format detection (TXT, MD, HTML, PDF, JSON, YAML, CSV, XML, DOCX)
- Content validation with size limits and malicious content detection
- Unicode normalization and text preprocessing
- Multiple chunking strategies (fixed-size, sentence, paragraph, sliding window)
- Batch processing with parallel execution
- Error recovery with retry logic
- Deduplication support
- Progress callbacks

### ✅ Phase 2: Query Optimization (COMPLETE)

**Implemented:**
- `src/codex/retrieval/reranker.py` - Re-ranking with multiple strategies (18 tests passing)
- `src/codex/retrieval/query_rewriter.py` - Query rewriting and expansion (29 tests passing)
- `src/codex/rag/cache/query_cache.py` - LRU query result cache (27 tests passing)
- `src/codex/rag/cache/embedding_cache.py` - Embedding vector cache (20 tests passing)
- `src/codex/rag/cache/distributed_cache.py` - Distributed cache with Redis support (22 tests passing)
- `tests/retrieval/test_reranker.py` - Re-ranker test suite
- `tests/retrieval/test_query_rewriter.py` - Query rewriter test suite
- `tests/rag/cache/` - Cache test suite (69 tests total)

**Features:**
- **Re-ranking Strategies:**
  - Score fusion (weighted sum, reciprocal rank, max)
  - MMR (Maximal Marginal Relevance) for diversity
  - Cross-encoder re-ranking (neural)
  - Hybrid strategy (fusion + MMR)
- **Query Optimization:**
  - Query normalization
  - Query expansion with synonyms
  - Query decomposition into sub-queries
  - Hybrid query generation (sparse + dense)
  - Multi-query variants for improved recall
- **Caching:**
  - LRU eviction with TTL expiration
  - Thread-safe operations
  - Embedding-specific cache with float16 optimization
  - Distributed cache with Redis backend
  - Cache warming and statistics

### ⏳ Phase 3: Production Features (PENDING)

Requires Human Admin tasks:
- Infrastructure provisioning
- Secrets management

---

## Executive Summary

This planset provides end-to-end implementation guidance for building a production-ready RAG (Retrieval Augmented Generation) pipeline. The current repository has RAG infrastructure (vector stores, retrieval modules, example workflows) but lacks production-grade features required for deployment at scale.

### Current State Analysis

**Existing Infrastructure (✅):**
- `src/codex/retrieval/` - Vector store implementations (FAISS, Pinecone, pgvector, Weaviate)
- `src/codex/retrieval/search.py` - Search and query logic
- `src/codex/retrieval/optimizations.py` - Performance optimizations
- `examples/rag_workflow.py` - End-to-end example workflow
- `tests/retrieval/` - Comprehensive test suite (70+ tests)
- `configs/rag_config.yaml` - Configuration templates

**New Production Features (✅ Phase 1):**
- `src/codex/rag/ingestion/` - Complete ingestion pipeline with validation, preprocessing, and chunking
- 104 new tests covering all ingestion components

**Remaining Production Features (⏳ Phase 2-3):**
- Query optimization and caching at scale
- Vector store high availability and failover
- Monitoring and observability
- Multi-tenancy and rate limiting
- Security and access control
- Production deployment configuration

---

## Architecture Overview

```mermaid
graph TB
    subgraph "Ingestion Pipeline"
        DOC[Document Sources] --> VAL[Validation]
        VAL --> PROC[Processing]
        PROC --> CHUNK[Chunking]
        CHUNK --> EMB[Embedding]
        EMB --> IDX[Indexing]
    end
    
    subgraph "Vector Store Layer"
        IDX --> VS[Vector Store]
        VS --> FAISS[FAISS]
        VS --> PINE[Pinecone]
        VS --> PG[pgvector]
        VS --> WEAV[Weaviate]
    end
    
    subgraph "Query Pipeline"
        QUERY[User Query] --> OPT[Optimization]
        OPT --> CACHE[Cache Layer]
        CACHE --> RETR[Retrieval]
        RETR --> VS
        RETR --> RANK[Reranking]
        RANK --> RESP[Response]
    end
    
    subgraph "Production Features"
        MON[Monitoring] --> VS
        MON --> RETR
        HA[High Availability] --> VS
        SEC[Security] --> QUERY
        SEC --> IDX
    end
```

---

## Human Admin Tasks vs AI Agent Tasks

### Human Admin Planset (Manual Steps Required)

#### Task HA-RAG-1: Infrastructure Provisioning
**Blocker:** Requires cloud provider access and payment configuration
**Best-Effort Alternative:** AI Agent can generate IaC templates and deployment scripts

**Manual Steps:**
1. Provision cloud infrastructure (vector databases, compute)
2. Configure cloud credentials and access keys
3. Set up networking (VPCs, security groups, load balancers)
4. Configure DNS and SSL certificates
5. Review and approve infrastructure costs

**AI Agent Support:**
- Generate Terraform/CloudFormation templates
- Create Kubernetes manifests
- Document infrastructure requirements
- Estimate costs and resource needs
- Provide deployment checklists

---

#### Task HA-RAG-2: Production Secrets Management
**Blocker:** Requires access to production secret management systems
**Best-Effort Alternative:** AI Agent can create secret templates and documentation

**Manual Steps:**
1. Create API keys for vector store providers (Pinecone, Weaviate)
2. Generate service account credentials
3. Configure secret management system (AWS Secrets Manager, Vault)
4. Set up secret rotation policies
5. Grant appropriate IAM permissions

**AI Agent Support:**
- Generate secret configuration templates
- Document required secrets
- Create secret rotation procedures
- Implement secret validation logic
- Provide security best practices

---

### AI Agent Planset (Autonomous Tasks)

#### Phase 1: Enhanced Document Ingestion Pipeline

**Pre-commit 1-2: Document Validation and Preprocessing**

**Goal:** Build robust document validation and preprocessing pipeline

**Tasks:**
- [ ] Create `src/codex/rag/ingestion/validator.py`:
  - Document format validation (PDF, TXT, MD, HTML)
  - Size and content validation
  - Encoding detection and normalization
  - Malicious content detection
- [ ] Create `src/codex/rag/ingestion/preprocessor.py`:
  - Text cleaning and normalization
  - Metadata extraction
  - Language detection
  - Deduplication logic
- [ ] Add comprehensive error handling
- [ ] Create validation test suite (20+ tests)

**Success Criteria:**
- [ ] Support for 10+ document formats
- [ ] 100% validation coverage for edge cases
- [ ] Malformed document handling tested
- [ ] Performance: >100 docs/second validation

**Files to Create:**
- `src/codex/rag/ingestion/__init__.py` (50 lines)
- `src/codex/rag/ingestion/validator.py` (300 lines)
- `src/codex/rag/ingestion/preprocessor.py` (400 lines)
- `tests/rag/ingestion/test_validator.py` (250 lines)
- `tests/rag/ingestion/test_preprocessor.py` (300 lines)

**Alternative if Blocked:**
- Implement basic validation first, expand formats iteratively
- Use existing libraries (textract, PyPDF2, etc.)
- Document format-specific limitations

---

**Pre-commit 3-4: Chunking Strategy and Optimization**

**Goal:** Implement production-grade chunking with multiple strategies

**Tasks:**
- [ ] Create `src/codex/rag/ingestion/chunker.py`:
  - Fixed-size chunking with overlap
  - Semantic chunking (sentence boundaries)
  - Hierarchical chunking (sections, paragraphs)
  - Sliding window chunking
  - Configurable chunk size and overlap
- [ ] Implement chunk metadata tracking
- [ ] Add chunk quality metrics
- [ ] Create chunking benchmarks
- [ ] Add configuration management for chunking strategies

**Success Criteria:**
- [ ] 4+ chunking strategies implemented
- [ ] Configurable via YAML/Hydra
- [ ] Chunk size optimization validated
- [ ] Performance: >1000 chunks/second

**Files to Create:**
- `src/codex/rag/ingestion/chunker.py` (500 lines)
- `configs/rag/chunking.yaml` (50 lines)
- `tests/rag/ingestion/test_chunker.py` (400 lines)
- `docs/RAG_CHUNKING_STRATEGIES.md` (documentation)

**Alternative if Blocked:**
- Start with fixed-size chunking (simplest)
- Add semantic chunking incrementally
- Document trade-offs for each strategy

---

**Pre-commit 5-6: Batch Ingestion and Pipeline Orchestration**

**Goal:** Build scalable batch ingestion pipeline with monitoring

**Tasks:**
- [ ] Create `src/codex/rag/ingestion/pipeline.py`:
  - Batch processing with configurable batch size
  - Progress tracking and resumption
  - Error recovery and retry logic
  - Parallel processing support
  - Pipeline status reporting
- [ ] Implement ingestion monitoring
- [ ] Add rate limiting for API calls
- [ ] Create pipeline CLI interface
- [ ] Add ingestion metrics tracking

**Success Criteria:**
- [ ] Support for 1M+ documents ingestion
- [ ] Automatic error recovery
- [ ] Progress resumption on failure
- [ ] Performance: >10k docs/hour throughput

**Files to Create:**
- `src/codex/rag/ingestion/pipeline.py` (600 lines)
- `src/codex/cli/rag_ingest.py` (200 lines)
- `tests/rag/ingestion/test_pipeline.py` (500 lines)
- `docs/RAG_INGESTION_GUIDE.md` (documentation)

**CLI Interface:**
```bash
codex rag ingest \
  --source /path/to/docs \
  --index my_index \
  --tenant acme_corp \
  --batch-size 100 \
  --parallel 4 \
  --resume
```

**Alternative if Blocked:**
- Implement single-threaded pipeline first
- Add parallelization incrementally
- Use simpler retry logic initially

---

#### Phase 2: Query Optimization and Caching

**Pre-commit 7-8: Advanced Query Optimization**

**Goal:** Implement production-grade query optimization strategies

**Tasks:**
- [ ] Enhance `src/codex/retrieval/optimizations.py`:
  - Query rewriting and expansion
  - Hybrid search (dense + sparse)
  - Re-ranking with cross-encoders
  - Query result fusion
  - Diversity-aware retrieval
- [ ] Add query performance profiling
- [ ] Implement A/B testing framework for strategies
- [ ] Create optimization benchmarks
- [ ] Add configuration for optimization strategies

**Success Criteria:**
- [ ] 5+ optimization strategies implemented
- [ ] Retrieval quality improvement: +15% MRR
- [ ] Query latency maintained: <50ms p95
- [ ] A/B testing framework functional

**Files to Modify/Create:**
- `src/codex/retrieval/optimizations.py` (+500 lines)
- `src/codex/retrieval/reranker.py` (400 lines - new)
- `src/codex/retrieval/query_rewriter.py` (300 lines - new)
- `configs/rag/optimization.yaml` (100 lines)
- `tests/retrieval/test_reranker.py` (350 lines)
- `tests/retrieval/test_query_rewriter.py` (300 lines)

**Alternative if Blocked:**
- Implement hybrid search first (highest impact)
- Add re-ranking as second priority
- Document trade-offs and quality metrics

---

**Pre-commit 9-10: Multi-Level Caching System**

**Goal:** Build distributed caching system for production scale

**Tasks:**
- [ ] Create `src/codex/rag/cache/distributed_cache.py`:
  - Redis integration for distributed cache
  - Cache invalidation strategies
  - Cache warming and preloading
  - Cache analytics and monitoring
  - TTL and eviction policies
- [ ] Implement cache hit rate tracking
- [ ] Add cache synchronization for multi-instance
- [ ] Create cache management CLI
- [ ] Add cache performance benchmarks

**Success Criteria:**
- [ ] Cache hit rate: >90% for common queries
- [ ] Cache latency: <5ms p99
- [ ] Support for 1M+ cached queries
- [ ] Automatic cache warming functional

**Files to Create:**
- `src/codex/rag/cache/__init__.py` (50 lines)
- `src/codex/rag/cache/distributed_cache.py` (500 lines)
- `src/codex/rag/cache/warmup.py` (200 lines)
- `src/codex/cli/rag_cache.py` (150 lines)
- `tests/rag/cache/test_distributed_cache.py` (400 lines)
- `configs/rag/cache.yaml` (50 lines)

**Cache CLI:**
```bash
# Cache management
codex rag cache stats --tenant acme_corp
codex rag cache warm --queries popular_queries.txt
codex rag cache clear --pattern "prefix:*"
codex rag cache export --output cache_backup.json
```

**Alternative if Blocked:**
- Use in-memory caching initially (no Redis)
- Add distributed caching incrementally
- Document single-instance limitations

---

#### Phase 3: Production Features and Observability

**Pre-commit 11-12: High Availability and Failover**

**Goal:** Implement HA vector store with automatic failover

**Tasks:**
- [ ] Create `src/codex/rag/ha/store_manager.py`:
  - Multi-region vector store support
  - Automatic failover on store failure
  - Health checking and monitoring
  - Load balancing across stores
  - Graceful degradation strategies
- [ ] Implement store health metrics
- [ ] Add automatic recovery procedures
- [ ] Create HA configuration templates
- [ ] Add HA integration tests

**Success Criteria:**
- [ ] Zero-downtime failover: <1s
- [ ] Support for 3+ replica stores
- [ ] Automatic health checks every 30s
- [ ] 99.9% availability target

**Files to Create:**
- `src/codex/rag/ha/__init__.py` (50 lines)
- `src/codex/rag/ha/store_manager.py` (600 lines)
- `src/codex/rag/ha/health_checker.py` (300 lines)
- `configs/rag/ha.yaml` (100 lines)
- `tests/rag/ha/test_failover.py` (500 lines)

**Alternative if Blocked:**
- Implement health checking first
- Add manual failover initially
- Document automatic failover as future enhancement

---

**Pre-commit 13-14: Monitoring and Observability**

**Goal:** Build comprehensive monitoring and alerting system

**Tasks:**
- [ ] Create `src/codex/rag/monitoring/metrics.py`:
  - Query latency metrics (p50, p95, p99)
  - Ingestion throughput metrics
  - Cache hit rate tracking
  - Error rate monitoring
  - Vector store health metrics
- [ ] Implement Prometheus exporter
- [ ] Add structured logging with correlation IDs
- [ ] Create Grafana dashboard templates
- [ ] Add alerting rule templates

**Success Criteria:**
- [ ] 50+ metrics tracked
- [ ] Prometheus integration functional
- [ ] Dashboards visualizing all metrics
- [ ] Alert rules for critical issues

**Files to Create:**
- `src/codex/rag/monitoring/__init__.py` (50 lines)
- `src/codex/rag/monitoring/metrics.py` (500 lines)
- `src/codex/rag/monitoring/prometheus.py` (300 lines)
- `src/codex/rag/monitoring/logger.py` (200 lines)
- `configs/monitoring/grafana_dashboards/rag_pipeline.json` (500 lines)
- `configs/monitoring/prometheus/rag_alerts.yaml` (200 lines)
- `tests/rag/monitoring/test_metrics.py` (400 lines)

**Alternative if Blocked:**
- Start with basic metrics (latency, throughput)
- Add Prometheus export incrementally
- Use simple logging before structured logging

---

**Pre-commit 15-16: Security and Access Control**

**Goal:** Implement production-grade security features

**Tasks:**
- [ ] Create `src/codex/rag/security/access_control.py`:
  - Tenant isolation and validation
  - API key authentication
  - Rate limiting per tenant
  - Query sanitization (injection prevention)
  - Audit logging for all operations
- [ ] Implement permission management
- [ ] Add security testing suite
- [ ] Create security documentation
- [ ] Add compliance verification

**Success Criteria:**
- [ ] Multi-tenant isolation verified
- [ ] API authentication functional
- [ ] Rate limits enforced
- [ ] Audit log captures all operations

**Files to Create:**
- `src/codex/rag/security/__init__.py` (50 lines)
- `src/codex/rag/security/access_control.py` (500 lines)
- `src/codex/rag/security/rate_limiter.py` (300 lines)
- `src/codex/rag/security/audit_logger.py` (200 lines)
- `tests/rag/security/test_access_control.py` (450 lines)
- `docs/RAG_SECURITY_GUIDE.md` (documentation)

**Alternative if Blocked:**
- Implement tenant isolation first (critical)
- Add authentication incrementally
- Document security considerations for manual review

---

**Pre-commit 17-18: Production Deployment Configuration**

**Goal:** Create production-ready deployment configurations

**Tasks:**
- [ ] Create Kubernetes deployment manifests:
  - Ingestion service deployment
  - Query service deployment
  - Cache service deployment
  - ConfigMaps and Secrets
  - Horizontal Pod Autoscaling
- [ ] Create Docker production images
- [ ] Add health check endpoints
- [ ] Create deployment documentation
- [ ] Add deployment validation scripts

**Success Criteria:**
- [ ] Complete K8s manifests for all services
- [ ] Docker images optimized for production
- [ ] Health checks functional
- [ ] Deployment tested in staging environment

**Files to Create:**
- `deploy/kubernetes/rag-ingestion-deployment.yaml` (200 lines)
- `deploy/kubernetes/rag-query-deployment.yaml` (200 lines)
- `deploy/kubernetes/rag-cache-deployment.yaml` (150 lines)
- `deploy/kubernetes/rag-configmap.yaml` (100 lines)
- `deploy/kubernetes/rag-hpa.yaml` (50 lines)
- `deploy/docker/Dockerfile.rag-production` (100 lines)
- `docs/RAG_DEPLOYMENT_GUIDE.md` (documentation)
- `scripts/validate_rag_deployment.sh` (200 lines)

**Alternative if Blocked:**
- Create Docker Compose for simpler deployment
- Document manual deployment steps
- Provide configuration examples for common scenarios

---

### Review, Verify, Commit

**Final Checklist:**
- [ ] All 18 pre-commits completed
- [ ] Full test suite passing (500+ new tests)
- [ ] Documentation complete and reviewed
- [ ] Security validation passed
- [ ] Performance benchmarks met
- [ ] Deployment configurations validated
- [ ] Monitoring dashboards functional
- [ ] Production readiness review complete

---

## AI Agency Policy Compliance

### Comprehensive Issue Resolution
✅ Addresses complete production readiness gap
✅ No partial implementations - end-to-end solution
✅ Security, monitoring, and HA included

### Planning Before Execution
✅ 3 phases with 18 pre-commits
✅ Clear dependencies and ordering
✅ Success criteria for each step

### No Deferral Without Plan
✅ All blockers identified (infrastructure provisioning, secrets)
✅ Best-effort alternatives documented
✅ Minimum 5 iterations met (18 pre-commits)

### Timeline Terminology
✅ Uses pre-commit/commit cycles
✅ Organized into Phases
✅ No time-based estimates

---

## Blocker Documentation and Alternatives

### Known Blockers

1. **Cloud Infrastructure Provisioning**
   - **Task:** HA-RAG-1
   - **Blocker:** Requires cloud provider access and payment
   - **AI Agent Alternative:** Generate IaC templates, document requirements

2. **Production Secrets**
   - **Task:** HA-RAG-2
   - **Blocker:** Requires access to secret management systems
   - **AI Agent Alternative:** Generate templates, document secret requirements

3. **Vector Store Provider APIs**
   - **Task:** Phase 2-3 (caching, HA)
   - **Blocker:** May require paid API access (Pinecone, Weaviate)
   - **AI Agent Alternative:** Use FAISS (local), mock external services for testing

---

## Success Metrics

### Quantitative
- Ingestion throughput: >10k docs/hour
- Query latency p95: <50ms
- Cache hit rate: >90%
- Test coverage: >80% for new code
- Availability: 99.9%

### Qualitative
- Production-grade error handling
- Comprehensive monitoring and alerting
- Security best practices implemented
- Complete deployment documentation
- Smooth upgrade path from current infrastructure

---

## Cognitive Brain Context

This planset is designed for autonomous execution with the following understanding:

1. **Build on Existing:** Leverage current RAG infrastructure
2. **Production First:** Focus on reliability, security, monitoring
3. **Incremental:** Each phase adds production capability
4. **Testing Required:** No code without comprehensive tests
5. **Documentation Critical:** Operations teams need complete guides

The cognitive brain should approach this work with:
- **Quality focus:** Production-grade only, no shortcuts
- **Security mindset:** Every feature considers security
- **Operational awareness:** Monitoring and observability first-class
- **Scalability:** Design for millions of documents and queries

---

## Estimated Effort

- **AI Agent Autonomous Work:** 18 pre-commits (3 phases)
- **Human Admin Manual Tasks:** 2 tasks (infrastructure + secrets)
- **Total Phases:** 3 phases
- **Complexity:** High (production-grade system)

---

## Next Steps

For AI Agent to begin autonomous execution:

```markdown
@copilot Begin Production RAG Pipeline implementation following `.codex/plans/PRODUCTION_RAG_PIPELINE_PLANSET.md`.

Start with Phase 1: Enhanced Document Ingestion Pipeline.

**Policy Compliance:**
- Follow `.codex/CODEBASE_AGENCY_POLICY.md`
- Use pre-commit/commit terminology
- 5+ self-review iterations
- Address ALL issues discovered
- Build on existing RAG infrastructure in `src/codex/retrieval/`

**Success Criteria:**
- ✅ Production-grade ingestion, caching, HA, monitoring
- ✅ 500+ new tests with >80% coverage
- ✅ Complete deployment documentation
- ✅ Security validation passed
```

---

**Status:** Ready for autonomous AI Agent execution with documented Human Admin checkpoints

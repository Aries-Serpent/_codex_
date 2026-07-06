# 🚀 PHASE 13 TRACK 13.4: PERFORMANCE OPTIMIZATION & CACHING
## Advisory Phase Design (Days 1-2: 2026-07-06 → 2026-07-07)

**Status:** 🟢 ADVISORY MODE (NO MERGE AUTHORITY)  
**Date:** 2026-07-06T05:43:52Z  
**Lead Agent:** cache-management-agent  
**Authority:** @mbaetiong (D-tier autonomous)  
**Phase Gates:** Dependent on Track 12.3 ≥95% clearance  

---

## EXECUTIVE SUMMARY

Phase 13 Track 13.4 designs a production-grade **4-layer cache hierarchy** to optimize performance and reduce latency across all AI agent endpoints. This advisory phase (Days 1-2) establishes:

1. **L1 Request Cache** (in-process, TTL=300s) — <100ms hit latency
2. **L2 Session Cache** (Redis, TTL=3600s) — <150ms ops
3. **L3 Knowledge Cache** (disk-backed, TTL=86400s) — persistent RAG context
4. **L4 Model Cache** (weights, TTL=forever) — pre-loaded model weights

**Advisory Phase Objectives:**
- ✅ Design all 4 cache layers with clear interfaces
- ✅ Set performance targets (<500ms p99 all endpoints)
- ✅ Define cache hit rate targets (>85% L1/L2, >70% L3)
- ✅ Map integration points with other tracks
- ✅ Plan capacity and resource allocation
- ✅ Document metrics and monitoring strategy

**Full Execution Gate:** Deploys Days 7-11 upon Track 12.3 ≥95% clearance

---

## LAYER 1: REQUEST CACHE (L1)

### Purpose
Reduce repeated request processing within a single session or user context. Cache frequently accessed request results (queries, search results, inference outputs) with automatic expiration.

### Architecture

```
┌─────────────────────────────────────┐
│   REQUEST LAYER (In-Process)        │
├─────────────────────────────────────┤
│ • Thread-safe LRU eviction          │
│ • TTL-based expiration (300s)       │
│ • Capacity: 1000 entries (~100MB)   │
│ • Hit latency: <100ms (avg 5-10ms)  │
│ • Miss latency: Transparent fallback │
│ • Hit rate target: >85% on hot paths │
└─────────────────────────────────────┘
```

### Implementation Details

**Storage:** OrderedDict-based LRU cache (Python standard library)

**Config:**
```python
@dataclass
class L1CacheConfig:
    max_entries: int = 1000
    default_ttl: float = 300.0  # 5 minutes
    enable_stats: bool = True
    cleanup_interval: float = 60.0
    thread_safe: bool = True
    # Memory budget per entry (avg)
    max_entry_size_bytes: int = 102400  # 100KB
    # Eviction policy
    eviction_policy: str = "lru"  # LRU, LFU, FIFO
```

**Key Patterns:**
- Request deduplication (hash request parameters)
- Automatic expiration on access (lazy cleanup)
- Periodic cleanup background task
- Per-layer metrics collection

**Thread Safety:**
- RLock for mutation operations
- CAS-style updates for consistency
- No blocking on cache misses

### Performance Targets

| Metric | Target | Baseline | Improvement |
|--------|--------|----------|-------------|
| Hit Latency | <100ms | — | N/A |
| Miss Latency | <10ms overhead | — | N/A |
| Hit Rate | >85% | ~0% (new) | Massive |
| Memory Overhead | <200MB | 0 | Acceptable |
| Cleanup Cost | <1% CPU | 0 | Negligible |

### Integration Points

- **Track 13.1 (Test Healing):** Cache test result patterns
- **Track 13.2 (Meta-Tensor):** Cache tensor metadata
- **RAG Retriever:** Cache query results (embeddings, retrievals)
- **AI Agent Inference:** Cache prompt/completion pairs

### Monitoring

```python
L1CacheMetrics = {
    "hit_count": Counter,
    "miss_count": Counter,
    "eviction_count": Counter,
    "avg_latency_ms": Histogram(0-500ms buckets),
    "memory_usage_bytes": Gauge,
    "entry_count": Gauge,
    "cleanup_cost_ms": Histogram,
}
```

---

## LAYER 2: SESSION CACHE (L2)

### Purpose
Maintain session state and frequently used data across distributed instances. Share cache results across multiple processes/machines via Redis with longer TTL (1 hour).

### Architecture

```
┌─────────────────────────────────────┐
│   SESSION LAYER (Redis, Distributed)│
├─────────────────────────────────────┤
│ • Redis cluster (HA-enabled)        │
│ • Connection pooling (10 conns)     │
│ • TTL-based expiration (3600s)      │
│ • Capacity: 100,000+ entries        │
│ • Hit latency: <150ms (network RTT) │
│ • Hit rate target: >85% sessions    │
│ • Serialization: msgpack/JSON       │
│ • Compression: zlib for >1KB        │
└─────────────────────────────────────┘
```

### Implementation Details

**Config:**
```python
@dataclass
class L2CacheConfig:
    backend: CacheBackend = CacheBackend.REDIS
    redis_host: str = "redis.default.svc.cluster.local"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None  # pragma: allowlist secret
    redis_key_prefix: str = "codex:session:"
    redis_ttl: int = 3600  # 1 hour
    redis_socket_timeout: float = 5.0
    redis_connection_pool_size: int = 10
    
    # Fallback to L1 if Redis unavailable
    fallback_to_l1: bool = True
    
    # Serialization
    compress: bool = True
    compression_threshold: int = 1024  # bytes
    serializer: str = "msgpack"  # msgpack or json
```

**Key Features:**
- Automatic serialization (msgpack by default)
- Compression for entries >1KB
- Connection pooling for performance
- Fallback to L1 cache on Redis unavailability
- Consistent key namespacing (workflow + user + session)

**Key Naming Pattern:**
```
codex:session:{workflow_id}:{user_id}:{session_id}:{entity_type}:{entity_id}
```

### Performance Targets

| Metric | Target | Baseline | Improvement |
|--------|--------|----------|-------------|
| Hit Latency | <150ms | — | N/A |
| Miss Latency | <200ms | — | N/A |
| Hit Rate | >85% | ~0% (new) | Massive |
| Network Bandwidth | <10 Mbps | 0 | Acceptable |
| Redis Memory | <5GB | 0 | Planned |
| Connection Efficiency | >90% reuse | 0 | Good |

### Integration Points

- **L1 Cache:** Write-through strategy (updates both layers)
- **Track 13.1:** Session-specific test patterns
- **Track 13.2:** Meta-tensor state across workers
- **RAG Search:** Cross-instance search result sharing
- **Cognitive Brain:** Session context and patterns

### Monitoring

```python
L2CacheMetrics = {
    "hit_count": Counter,
    "miss_count": Counter,
    "network_latency_ms": Histogram(0-1000ms buckets),
    "serialization_time_ms": Histogram,
    "compression_ratio": Gauge,
    "memory_usage_bytes": Gauge,
    "connection_pool_usage": Histogram,
    "redis_unavailable_fallbacks": Counter,
}
```

---

## LAYER 3: KNOWLEDGE CACHE (L3)

### Purpose
Persistent disk-backed cache for large knowledge entities (embeddings, contexts, patterns) with 24-hour TTL. Survives process/instance restarts; enables fast cold-starts.

### Architecture

```
┌─────────────────────────────────────┐
│ KNOWLEDGE LAYER (Disk-Backed, 24h)  │  # pragma: allowlist secret
├─────────────────────────────────────┤
│ • Storage: SQLite or LevelDB        │
│ • TTL-based expiration (86400s)     │
│ • Capacity: 10GB+ (configurable)    │
│ • Hit latency: <500ms (disk I/O)    │
│ • Hit rate target: >70% on searches │
│ • Batch loading support             │
│ • Compaction and maintenance        │
└─────────────────────────────────────┘
```

### Implementation Details

**Storage Backend Options:**

**SQLite (Recommended for now):**
```python
@dataclass
class L3CacheConfig:
    backend: str = "sqlite"  # sqlite or leveldb
    db_path: str = "~/.cache/codex/knowledge.db"
    
    # Performance tuning
    page_size: int = 4096
    cache_size: int = 50000  # pages
    journal_mode: str = "WAL"  # Write-Ahead Logging
    synchronous: str = "NORMAL"  # Balance safety/speed
    
    # Capacity
    max_db_size_mb: int = 10000
    
    # TTL and cleanup
    default_ttl: int = 86400  # 24 hours
    cleanup_interval: float = 3600  # hourly
    
    # Compression
    compress: bool = True
    compression_threshold: int = 1024
```

**Schema:**
```sql
CREATE TABLE cache_entries (
    key TEXT PRIMARY KEY,
    entity_type TEXT,  -- embedding, context, pattern
    value BLOB,
    created_at INTEGER,
    expires_at INTEGER,
    access_count INTEGER DEFAULT 0,
    last_accessed INTEGER,
    size_bytes INTEGER,
    metadata TEXT  -- JSON
);

CREATE INDEX idx_entity_type ON cache_entries(entity_type);
CREATE INDEX idx_expires_at ON cache_entries(expires_at);
```

**Key Features:**
- Batch operations for bulk loading
- Automatic compaction (weekly)
- Rollback/recovery mechanisms
- Incremental backup support
- Corruption detection on startup

### Performance Targets

| Metric | Target | Baseline | Improvement |
|--------|--------|----------|-------------|
| Hit Latency | <500ms | — | N/A |
| Miss Latency | <100ms | — | N/A |
| Hit Rate | >70% | ~0% (new) | Significant |
| Disk Space | <10GB | 0 | Acceptable |
| Query Time | <50ms avg | — | N/A |
| Compaction Cost | <2% overhead | 0 | Negligible |

### Integration Points

- **L1/L2 Caches:** Overflow storage (cache promotion)
- **RAG Embeddings:** Persistent embedding cache
- **Context Manager:** Knowledge graph persistence
- **Track 13.1:** Test pattern database
- **Cognitive Brain:** Session history and learnings

### Monitoring

```python
L3CacheMetrics = {
    "hit_count": Counter,
    "miss_count": Counter,
    "disk_latency_ms": Histogram(0-2000ms buckets),  # pragma: allowlist secret
    "db_size_mb": Gauge,
    "entry_count": Gauge,
    "compaction_time_ms": Histogram,
    "disk_bandwidth_mbps": Gauge,  # pragma: allowlist secret
    "query_time_ms": Histogram,
}
```

---

## LAYER 4: MODEL CACHE (L4)

### Purpose
Pre-load and cache large model weights (LLMs, embedders, classifiers) in memory for instant inference. No TTL expiration (lives as long as process). Managed by model loader.

### Architecture

```
┌─────────────────────────────────────┐
│  MODEL LAYER (In-Process, Infinity) │
├─────────────────────────────────────┤
│ • In-memory model storage           │
│ • No TTL (refresh on code update)   │
│ • Capacity: 8-16GB (configurable)   │
│ • Load latency: <5s (first load)    │
│ • Hit latency: <1ms (memory)        │
│ • Version tracking and rollback     │
│ • Atomic model swaps                │
└─────────────────────────────────────┘
```

### Implementation Details

**Config:**
```python
@dataclass
class L4CacheConfig:
    # Model storage
    models_dir: str = "~/.cache/codex/models"
    
    # Memory budget
    max_memory_gb: int = 16
    
    # Models to preload
    preload_models: List[str] = field(default_factory=lambda: [
        "sentence-transformers/all-MiniLM-L6-v2",  # embeddings
        "gpt2",  # fallback generation
    ])
    
    # Version management
    version_tracking: bool = True
    allow_rollback: bool = True
    max_versions_per_model: int = 2
    
    # Loading strategy
    lazy_load: bool = False  # preload on startup
    offload_to_disk: bool = True  # disk as overflow
    offload_threshold_gb: float = 12.0  # GB
```

**Model Manager Interface:**
```python
class ModelManager:
    def load_model(self, model_name: str, version: str = "latest") -> Model
    def get_model(self, model_name: str) -> Model  # from cache
    def unload_model(self, model_name: str) -> None
    def list_loaded_models(self) -> List[str]
    def get_memory_usage(self) -> Dict[str, int]  # per model
    def swap_model_version(self, model_name: str, version: str) -> None
    def get_model_stats(self) -> Dict[str, ModelStats]
```

**Key Features:**
- Atomic model version swaps (no inference interruptions)
- Disk offloading when memory constrained
- Automatic cleanup of old versions
- Model health checks on load
- Inference profiling per model

### Performance Targets

| Metric | Target | Baseline | Improvement |
|--------|--------|----------|-------------|
| Load Latency | <5s | — | N/A |
| Hit Latency | <1ms | — | N/A |
| Memory Overhead | <20% extra | 0 | Acceptable |
| Model Swap Time | <100ms | — | N/A |
| Inference Time | Baseline | — | N/A |

### Integration Points

- **Model Loader:** Primary consumer (inference)
- **Track 13.1:** Test model loading patterns
- **Track 13.2:** Meta-tensor aware loading
- **Cognitive Brain:** Model awareness and selection
- **Monitoring:** Model health and performance

### Monitoring

```python
L4CacheMetrics = {
    "load_count": Counter,
    "load_time_ms": Histogram(0-10000ms buckets),
    "memory_usage_bytes": Gauge,
    "models_loaded": Gauge,
    "version_swaps": Counter,
    "inference_latency_ms": Histogram,
    "disk_offload_events": Counter,  # pragma: allowlist secret
}
```

---

## END-TO-END CACHE FLOW

### Request Path

```
Request
  ↓
┌─────────────────────────────────┐
│ L1: Check Request Cache (5-10ms)│
│ • Hit: Return (<100ms total)    │
│ • Miss: Continue               │
└─────────────────────────────────┘
  ↓
┌─────────────────────────────────┐
│ L2: Check Session Cache (50ms)  │
│ • Hit: Populate L1, return      │
│ • Miss: Continue                │
└─────────────────────────────────┘
  ↓
┌─────────────────────────────────┐
│ L3: Check Knowledge Cache (200ms)│
│ • Hit: Populate L1/L2, return   │
│ • Miss: Continue                │
└─────────────────────────────────┘
  ↓
┌─────────────────────────────────┐
│ Execute Request (5s-1m)         │
│ • Use L4 model cache            │
│ • Process with RAG              │
└─────────────────────────────────┘
  ↓
┌─────────────────────────────────┐
│ Populate All Caches (write-back)│
│ • Store in L1, L2, L3 per TTL   │
│ • Return result                 │
└─────────────────────────────────┘
```

### Performance Expected

**With Full Cache Hierarchy:**
- **L1 Hit:** <100ms (in-process)
- **L1+L2 Hit:** <150ms (Redis)
- **L1+L2+L3 Hit:** <500ms (disk)
- **Full Miss:** 5-60s (execution) + caching

**Hit Rate Projections:**
- L1 hit rate: >85% (request deduplication)
- L2 hit rate: >85% (session context)
- L3 hit rate: >70% (knowledge persistence)
- Blended improvement: **50-70% latency reduction**

---

## INTEGRATION WITH OTHER TRACKS

### Track 13.1: Test Healing
- **L1 Integration:** Cache test result patterns
- **L2 Integration:** Share healing patterns across sessions
- **L3 Integration:** Long-term test pattern repository
- **Impact:** Faster test analysis and remediation

### Track 13.2: Meta-Tensor Safety
- **L1 Integration:** Cache tensor shape/dtype metadata
- **L2 Integration:** Distributed meta-tensor health state
- **L3 Integration:** Historical tensor operation logs
- **Impact:** Faster meta-tensor validation and recovery

### Track 13.3: Security Hardening
- **L1 Integration:** Cache security scan results
- **L2 Integration:** Cross-instance vulnerability state
- **L3 Integration:** Historical vulnerability database
- **Impact:** Faster security scanning and response

---

## RESOURCE PLANNING

### Memory Budget

| Layer | Per Instance | Cluster (10 inst) |
|-------|--------------|-------------------|
| L1 | 100-200MB | 1-2GB |
| L2 (Redis) | N/A (shared) | 5GB |
| L3 (Disk) | N/A (disk) | 100GB |
| L4 (Models) | 8-16GB | 16GB (shared) |
| **Total** | **8-16GB** | **122GB** |

### Disk Budget

| Layer | Size | Type |
|-------|------|------|
| L3 SQLite | 10GB | Persistent |
| L4 Models | 6GB | Persistent |
| Backups | 2GB | Archival |
| **Total** | **18GB** | — |

### Network Budget

| Layer | Bandwidth | Direction |
|-------|-----------|-----------|
| L2 Redis | <10 Mbps | Bidirectional |
| Replication | <5 Mbps | L1→L2→L3 |
| Backup | <1 Mbps | Periodic |
| **Peak** | **<15 Mbps** | — |

---

## CACHE EVICTION & INVALIDATION

### L1 Eviction Policy

**LRU (Least Recently Used):**
- When capacity reached, evict least recently accessed
- O(1) operations via OrderedDict
- Per-entry TTL enforced on access

**TTL-Based Expiration:**
- Default: 300 seconds
- Auto-cleanup every 60 seconds
- Lazy cleanup on access

### L2 Invalidation

**Redis Key Expiration:**
- Redis handles automatic TTL expiration
- 3600-second default TTL
- Manual invalidation for eager cleanup

**Cross-Instance Sync:**
- Invalidation events published to all instances
- Pub/Sub channel: `codex:cache:invalidation`
- Format: `{layer}:{key}:{timestamp}`

### L3 Compaction

**Weekly Maintenance Window:**
- Runs Sunday 02:00 UTC (low-traffic window)
- Duration: <1 hour typical
- Removes expired entries, rebuilds indexes

**Compaction Strategy:**
1. Identify expired entries (WHERE expires_at < now())
2. Delete in batches of 10K
3. Run VACUUM to reclaim space
4. Rebuild indexes
5. Verify database integrity

### L4 Cleanup

**Version Management:**
- Keep max 2 versions per model
- Delete versions older than 7 days
- Preserve latest + previous (fallback)

**Manual Cleanup:**
- Triggered by code changes
- Invalidates entire model cache
- Reloads from disk on next access

---

## METRICS & OBSERVABILITY

### Dashboard Metrics

**Overall Cache Health:**
```
Cache Hit Rate Across Layers
├─ L1: ___ % (target: >85%)
├─ L2: ___ % (target: >85%)
└─ L3: ___ % (target: >70%)

Cache Memory Usage
├─ L1 (process): ___ MB / 200MB
├─ L2 (Redis): ___ MB / 5GB
└─ L3 (disk): ___ MB / 10GB

Latency Percentiles
├─ L1 hit: ___ ms (target: <100ms)
├─ L2 hit: ___ ms (target: <150ms)
└─ L3 hit: ___ ms (target: <500ms)
```

### Alerting Thresholds

| Alert | Threshold | Action |
|-------|-----------|--------|
| Hit rate low | <70% L1 or L2 | Investigate warm-up or invalidation |
| Memory exceeded | >180MB L1 | Manual eviction or config review |
| Redis down | Cannot connect | Trigger L1 fallback, page on-call |
| Disk space low | >9GB L3 | Alert ops, schedule cleanup |
| High latency | >500ms p95 | Profile and optimize |

### Logging

**Per-Layer Metrics (Prometheus format):**
```
codex_cache_hits_total{layer="l1",entity="request"}
codex_cache_misses_total{layer="l1",entity="request"}
codex_cache_latency_ms{layer="l1",quantile="0.95"}
codex_cache_memory_bytes{layer="l1"}
codex_cache_evictions_total{layer="l1"}
```

---

## SUCCESS CRITERIA (ADVISORY PHASE)

### Design Completeness
- [x] All 4 cache layers designed with clear interfaces
- [x] Performance targets established (<500ms p99)
- [x] Cache hit rate targets set (>85% L1/L2, >70% L3)
- [x] Integration points identified with other tracks
- [x] Resource budgets calculated and feasible
- [x] Latency improvement roadmap documented

### Technical Soundness
- [x] Serialization strategy chosen (msgpack + compression)
- [x] Fallback strategies defined (L2→L1, Redis unavailable)
- [x] Eviction policies specified (LRU + TTL)
- [x] Invalidation mechanisms designed
- [x] Monitoring and alerting scoped
- [x] Error handling and recovery planned

### Integration Readiness
- [x] API contracts defined (get, put, delete, clear)
- [x] Key namespacing strategy consistent
- [x] Cross-track dependencies mapped
- [x] Configuration management planned
- [x] Testing strategy outlined
- [x] Deployment plan prepared

---

## NEXT STEPS (UPON TRACK 12.3 CLEARANCE)

### Days 7-8: L1 Implementation & Deployment
- Implement in-process LRU cache with TTL
- Deploy to test environment
- Validate <100ms hit latency
- Monitor hit rate ramp-up (target >85%)

### Days 8-9: L2 Implementation & Deployment
- Integrate Redis backend
- Implement write-through strategy
- Deploy to staging with Redis cluster
- Validate <150ms hit latency

### Days 9-10: L3 Implementation & Deployment
- Implement SQLite knowledge cache
- Integrate with RAG embedding cache
- Deploy compaction and maintenance
- Validate <500ms hit latency, >70% hit rate

### Days 10-11: L4 & Integration Testing
- Integrate model cache with inference
- Deploy atomic model swaps
- Run load testing (validate <500ms p99)
- Integration testing across all tracks
- Performance validation and tuning

### Day 11: Gate 6 Verification
- Verify all targets met (<500ms p99, >85% hit rates)
- Security scanning of caching code
- Documentation completion
- Prepare Phase 14 handoff

---

## RISK ASSESSMENT

### High Risks

**Risk 1: Redis Availability**
- **Probability:** MEDIUM (production dependency)
- **Impact:** HIGH (cache layer unavailable)
- **Mitigation:** L1 fallback, health checks, multi-replica setup

**Risk 2: Memory Pressure**
- **Probability:** MEDIUM (load-dependent)
- **Impact:** MEDIUM (eviction storms)
- **Mitigation:** Capacity planning, auto-scaling, dynamic sizing

**Risk 3: Cache Invalidation Bugs**
- **Probability:** MEDIUM (complex distributed state)
- **Impact:** HIGH (stale data)
- **Mitigation:** Comprehensive test coverage, monitoring alerts

### Medium Risks

**Risk 4: Performance Regression**
- **Probability:** LOW (well-designed)
- **Impact:** MEDIUM (latency increase)
- **Mitigation:** Load testing, profiling, continuous monitoring

**Risk 5: Integration Gaps**
- **Probability:** MEDIUM (4 layers to coordinate)
- **Impact:** MEDIUM (reduced effectiveness)
- **Mitigation:** Daily integration tests, cross-track sync

---

## REFERENCES

**Existing Code:**
- `src/codex/rag/cache/distributed_cache.py` — L2 Redis implementation (existing)
- `src/codex/rag/cache/query_cache.py` — L1 pattern (existing)
- `src/codex/rag/cache/embedding_cache.py` — L3 pattern (existing)
- `scripts/cognitive/cache_manager.py` — Unified cache intelligence

**Documentation:**
- `.codex/PHASE_13_ACTIVATION_BRIEF.md` — Phase 13 launch plan
- `.codex/PHASE_13_REALTIME_DASHBOARD.md` — Progress tracking
- `docs/performance.md` — Performance guidelines

**Related Tracks:**
- Track 13.1 (Test Healing) — Uses L1/L2 for pattern caching
- Track 13.2 (Meta-Tensor) — Uses L1/L2 for state tracking
- Track 13.3 (Security) — Uses L1/L2 for scan results

---

## APPROVAL CHECKLIST

**Advisory Phase Sign-Off:**
- [ ] Design reviewed for technical soundness
- [ ] Performance targets validated as achievable
- [ ] Integration points confirmed with other tracks
- [ ] Resource budgets approved
- [ ] This document approved by @mbaetiong

**Pre-Execution (Upon Track 12.3 Clearance):**
- [ ] Implementation plan finalized
- [ ] Test infrastructure prepared
- [ ] Deployment checklist completed
- [ ] Load test scenarios validated

---

**Status:** ✅ ADVISORY PHASE DESIGN COMPLETE  
**Next Milestone:** Track 12.3 ≥95% clearance for full execution  
**Target Completion:** 2026-07-16 (Day 11)

**Lead Agent:** cache-management-agent  
**Authority:** @mbaetiong (D-tier autonomous)

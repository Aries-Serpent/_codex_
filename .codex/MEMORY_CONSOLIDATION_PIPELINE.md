# Memory Consolidation Pipeline - Complete Specification

**Phase:** 10.2 (STM → LTM Integration)  
**Status:** PRODUCTION READY  
**Last Updated:** 2026-07-01  
**Authority:** @mbaetiong (D-tier autonomy)

---

## Executive Summary

The Memory Consolidation Pipeline orchestrates the automatic promotion of valuable short-term memory (STM) entries to long-term memory (LTM) through a rigorous OODA-loop based process. This document specifies the complete technical architecture, API contracts, implementation details, and operational guidelines for production deployment.

**Key Targets:**
- ✅ Zero data loss during consolidation (100% reliability)
- ✅ STM→LTM transfer overhead: < 2% of total execution time
- ✅ LTM post-prune size: < 50MB (95% capacity utilization)
- ✅ Consolidation latency: < 10 seconds per cycle
- ✅ Pattern promotion accuracy: > 98%

---

## Architecture Overview

### Memory Hierarchy

```
┌────────────────────────────────────────────────────────────┐
│                    SESSION CONTEXT                         │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  STM (Short-Term Memory) — Volatile                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • Recent session events (30 min window)             │   │
│  │ • Capacity: 100-500 entries                         │   │
│  │ • TTL: Session duration                            │   │
│  │ • Access tracking: frequency counter               │   │
│  │ • Scope: Single session context                    │   │
│  └────────────────┬────────────────────────────────────┘   │
│                   │ CONSOLIDATION TRIGGER                  │
│                   │ (fill_ratio > 0.80)                    │
│                   ▼                                         │
│  LTM (Long-Term Memory) — Persistent                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • Promoted patterns (frequency ≥ 3)                │   │
│  │ • Capacity: 5,000-10,000 entries                   │   │
│  │ • Retention: Policy-governed (7yr minimum)         │   │
│  │ • Access tracking: last_accessed timestamp         │   │
│  │ • Scope: Cross-session knowledge base              │   │
│  │ • Indexed: FAISS embeddings + SQLite               │   │
│  └────────────────┬────────────────────────────────────┘   │
│                   │ ARCHIVE TRIGGER                        │
│                   │ (age > window AND confidence < 0.3)    │
│                   ▼                                         │
│  Archive (Compressed History) — Read-only                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ • Low-confidence patterns                           │   │
│  │ • Aged-out entries per policy                       │   │
│  │ • Capacity: Unbounded (compressed)                 │   │
│  │ • Retention: Full 7-year compliance window         │   │
│  │ • Queryable: Via archive search API                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### Consolidation OODA Loop

The consolidation process follows the OODA (Observe-Orient-Decide-Act) paradigm:

```
PHASE 1: OBSERVE (Baseline State)
├─ Query STM stats:
│  ├─ count: current number of STM entries
│  ├─ capacity: configured max entries
│  └─ fill_ratio: count / capacity
├─ Query LTM stats:
│  ├─ count: current number of LTM entries
│  ├─ capacity: configured max entries
│  └─ average_confidence: mean confidence score
└─ Decision: Trigger consolidation if fill_ratio > 0.80

PHASE 2: ORIENT (Analysis)
├─ Identify hot STM entries:
│  ├─ Query: SELECT * FROM stm_entries WHERE access_count >= 3
│  ├─ Order by: access_count DESC, last_accessed DESC
│  ├─ Limit: max_promote_per_cycle (default: 100)
│  └─ Result: hot_entries list (sorted by promotion score)
├─ Identify cold LTM entries:
│  ├─ Query: SELECT * FROM ltm_entries WHERE
│  │            created_at < cutoff AND confidence < 0.3
│  ├─ Cutoff: 30 days ago
│  ├─ Limit: 1000 entries max
│  └─ Result: cold_entries list (pruning candidates)
└─ Classify patterns:
   ├─ Type classification: decision | error | performance | success | risk
   ├─ ImprovementArea tagging: CI_SELF_HEALING | COVERAGE | SECURITY | etc.
   └─ Confidence scoring: (freq × recency × importance) / age_decay

PHASE 3: DECIDE (Plan Generation)
├─ Promotion plan:
│  ├─ Score each hot_entry via pattern_score algorithm
│  ├─ Select entries with score ≥ 0.60 (default threshold)
│  ├─ Assign retention policy based on success_rate
│  └─ Order by score DESC (highest confidence first)
├─ Pruning plan:
│  ├─ Select cold_entries (age > 30d AND confidence < 0.3)
│  ├─ Exclude evergreen entries (protected by policy)
│  ├─ Archive to ltm_archive table
│  └─ Order by (age DESC, confidence ASC)
└─ Plan validation:
   ├─ Check for duplicates (merge if found)
   ├─ Validate schema consistency
   ├─ Estimate storage impact
   └─ Generate transaction ID for tracing

PHASE 4: ACT (Execution)
├─ Database transaction (ACID guarantees):
│  ├─ BEGIN TRANSACTION
│  │
│  ├─ Promote hot entries:
│  │  ├─ INSERT OR REPLACE INTO ltm_entries
│  │  │  (key, value, pattern_type, frequency, success_rate,
│  │  │   confidence, created_at, last_accessed, metadata, tags, policy)
│  │  ├─ DELETE FROM stm_entries WHERE key IN (promoted_keys)
│  │  └─ Log: operation_id, timestamp, num_promoted
│  │
│  ├─ Prune cold entries:
│  │  ├─ INSERT INTO ltm_archive SELECT * FROM ltm_entries
│  │  │  WHERE key IN (pruned_keys)
│  │  ├─ DELETE FROM ltm_entries WHERE key IN (pruned_keys)
│  │  └─ Log: operation_id, timestamp, num_pruned
│  │
│  └─ COMMIT
│
└─ Post-execution:
   ├─ Update graph relationships (if exists)
   ├─ Invalidate query caches
   └─ Publish consolidation:completed event

PHASE 5: ANALYZE (Measurement)
├─ Collect metrics:
│  ├─ State after consolidation (stm_count, ltm_count)
│  ├─ Promotion results (num_promoted, success_count)
│  ├─ Pruning results (num_pruned, archive_size)
│  ├─ Performance metrics (duration_ms, throughput)
│  └─ Storage metrics (compression_rate, size_delta)
├─ Validation:
│  ├─ Verify zero data loss: sum_before == sum_after
│  ├─ Verify promotion accuracy: > 98% of promoted items still valuable
│  ├─ Verify retention policy compliance: 100% of entries follow policy
│  └─ Verify graph consistency: no orphaned edges
└─ Logging:
   ├─ Write to .codex/action_log.ndjson
   ├─ Tag with operation_id for traceability
   └─ Alert on anomalies (>10% variance)
```

---

## Pattern Scoring Algorithm

The pattern score determines promotion eligibility and LTM placement.

### Formula

```
PATTERN_SCORE = (Frequency × Recency × Importance) / Age_Decay

Range: 0.0 - 1.0
Promotion Threshold: ≥ 0.60 (adjustable)
```

### Component Breakdown

#### 1. Frequency Component
```
frequency_norm = min(access_count / threshold, 1.0)
where:
  access_count = number of times pattern was accessed
  threshold = 3 (configurable via CODEX_STM_HOT_THRESHOLD)
  
Example:
  access_count = 5, threshold = 3 → frequency_norm = 1.0
  access_count = 2, threshold = 3 → frequency_norm = 0.67
```

#### 2. Recency Component
```
recency = exp(-(days_since_access / 30))
where:
  days_since_access = (now - last_accessed).total_seconds() / 86400
  
Behavior:
  0 days ago → recency = 1.0
  7 days ago → recency = 0.78
  30 days ago → recency = 0.37
  60 days ago → recency = 0.14 (decays exponentially)
```

#### 3. Importance Component
```
importance = success_rate
where:
  success_rate = successful_outcomes / total_outcomes
  range: 0.0 - 1.0
  
Interpretation:
  Pattern is valuable only if it leads to successful outcomes
  Patterns with SR < 0.3 are unlikely to be promoted
```

#### 4. Age Decay Component
```
age_decay = exp(days_since_creation / 90)
where:
  days_since_creation = (now - created_at).total_seconds() / 86400
  
Behavior:
  0 days old → age_decay = 1.0 (new patterns scored higher)
  30 days old → age_decay = 1.38 (slightly penalized)
  90 days old → age_decay = 2.72 (penalized significantly)
  
Rationale:
  Newer patterns are more relevant to current context
  Older patterns may be stale or outdated
```

### Example Calculation

```
Scenario: Pattern discovered 7 days ago, accessed 3x, 80% success rate

1. Frequency: min(3/3, 1.0) = 1.0
2. Recency: exp(-7/30) = 0.784
3. Importance: 0.80
4. Age_decay: exp(7/90) = 1.082

SCORE = (1.0 × 0.784 × 0.80) / 1.082 = 0.580

Result: score = 0.580
  → Below 0.60 threshold → NOT promoted immediately
  → Eligible for promotion after one more access (next score ≈ 0.62)
```

---

## API Specification

### 1. Consolidation Endpoint

```http
POST /api/memory/consolidate

Request:
{
  "session_id": "sess-123456",
  "force_consolidation": false,  # Skip threshold check
  "retention_policy": "standard",  # Override default policy
  "dry_run": false  # Test without persisting
}

Response (200 OK):
{
  "operation_id": "consolidate-2026-07-01T12:30:45Z",
  "timestamp": "2026-07-01T12:30:45Z",
  "stm_count": {"before": 424, "after": 12},
  "ltm_count": {"before": 1250, "after": 1362},
  "patterns_promoted": 110,
  "patterns_pruned": 28,
  "compression_rate": 0.92,
  "duration_ms": 234.5,
  "status": "success",
  "metrics": {
    "promotion_accuracy": 0.98,
    "storage_efficiency": 10.2,
    "policy_compliance": 1.0
  }
}

Response (400 Bad Request):
{
  "error": "consolidation_not_needed",
  "fill_ratio": 0.45,
  "threshold": 0.80
}
```

### 2. Memory State Endpoint

```http
GET /api/memory/state

Response (200 OK):
{
  "timestamp": "2026-07-01T12:30:45Z",
  "stm": {
    "count": 12,
    "capacity": 500,
    "fill_ratio": 0.024,
    "hot_entries": 2
  },
  "ltm": {
    "count": 1362,
    "capacity": 10000,
    "fill_ratio": 0.136,
    "avg_confidence": 0.72,
    "by_policy": {
      "evergreen": 45,
      "standard": 892,
      "decay": 425,
      "archived": 0
    }
  },
  "health": {
    "consolidation_needed": false,
    "pruning_candidates": 28,
    "data_integrity": "verified",
    "last_consolidation": "2026-07-01T12:30:45Z"
  }
}
```

### 3. Pattern Tagging Endpoint

```http
POST /api/memory/tag

Request:
{
  "pattern_keys": ["pattern-1", "pattern-2", "pattern-3"],
  "tags": ["security", "critical"],
  "improvement_areas": ["CI_SELF_HEALING", "SECURITY"]
}

Response (200 OK):
{
  "operation_id": "tag-2026-07-01T12:30:45Z",
  "patterns_tagged": 3,
  "timestamp": "2026-07-01T12:30:45Z",
  "status": "success"
}
```

---

## Database Schema

### STM Table (stm_entries)

```sql
CREATE TABLE stm_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  key TEXT UNIQUE NOT NULL,
  value TEXT NOT NULL,
  pattern_type TEXT NOT NULL,  -- decision|error|performance|success|risk
  frequency INTEGER DEFAULT 1,  -- Access count
  success_rate REAL DEFAULT 0.5,  -- 0.0-1.0
  confidence REAL DEFAULT 0.0,  -- Calculated score
  metadata JSON,  -- Additional context
  tags JSON,  -- Array of tags
  created_at TEXT NOT NULL,  -- ISO 8601 timestamp
  last_accessed TEXT NOT NULL,  -- ISO 8601 timestamp
  session_id TEXT  -- Source session
);

CREATE INDEX idx_stm_frequency ON stm_entries(frequency DESC);
CREATE INDEX idx_stm_accessed ON stm_entries(last_accessed DESC);
CREATE INDEX idx_stm_type ON stm_entries(pattern_type);
```

### LTM Table (ltm_entries)

```sql
CREATE TABLE ltm_entries (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  key TEXT UNIQUE NOT NULL,
  value TEXT NOT NULL,
  pattern_type TEXT NOT NULL,
  frequency INTEGER DEFAULT 1,
  success_rate REAL DEFAULT 0.5,
  confidence REAL,  -- Calculated during promotion
  policy TEXT NOT NULL,  -- evergreen|standard|decay|archived
  metadata JSON,
  tags JSON,
  created_at TEXT NOT NULL,
  last_accessed TEXT NOT NULL,
  promoted_at TEXT NOT NULL,  -- Promotion timestamp
  scheduled_review TEXT  -- Next review date
);

CREATE INDEX idx_ltm_confidence ON ltm_entries(confidence DESC);
CREATE INDEX idx_ltm_policy ON ltm_entries(policy);
CREATE INDEX idx_ltm_created ON ltm_entries(created_at);
CREATE INDEX idx_ltm_review ON ltm_entries(scheduled_review);
```

### Archive Table (ltm_archive)

```sql
CREATE TABLE ltm_archive (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  key TEXT NOT NULL,
  value TEXT NOT NULL,
  pattern_type TEXT NOT NULL,
  frequency INTEGER,
  success_rate REAL,
  confidence REAL,
  policy TEXT,
  metadata JSON,
  tags JSON,
  created_at TEXT,
  archived_at TEXT NOT NULL,
  archived_reason TEXT  -- age_exceeded|policy_expired|manual
);

CREATE INDEX idx_archive_created ON ltm_archive(created_at);
CREATE INDEX idx_archive_reason ON ltm_archive(archived_reason);
```

### Operation Log Table (consolidation_log)

```sql
CREATE TABLE consolidation_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  operation_id TEXT UNIQUE NOT NULL,
  operation_type TEXT NOT NULL,  -- consolidate|prune|archive
  timestamp TEXT NOT NULL,
  stm_count_before INTEGER,
  stm_count_after INTEGER,
  ltm_count_before INTEGER,
  ltm_count_after INTEGER,
  patterns_promoted INTEGER,
  patterns_pruned INTEGER,
  compression_rate REAL,
  duration_ms REAL,
  status TEXT,  -- success|failure|partial
  error_message TEXT,
  metrics JSON  -- Additional metrics
);

CREATE INDEX idx_log_timestamp ON consolidation_log(timestamp DESC);
CREATE INDEX idx_log_type ON consolidation_log(operation_type);
```

---

## Duplicate Detection & Intelligent Merging

### Duplicate Detection Strategy

```python
def detect_duplicates(entry_a: PatternEntry, entry_b: PatternEntry) -> float:
    """
    Compute similarity score between two patterns.
    Returns: 0.0 (completely different) to 1.0 (identical)
    """
    similarity_scores = {
        "key_match": 1.0 if entry_a.key == entry_b.key else 0.0,
        "type_match": 1.0 if entry_a.pattern_type == entry_b.pattern_type else 0.0,
        "semantic_similarity": compute_embedding_similarity(entry_a.value, entry_b.value),
        "tag_overlap": len(set(a.tags) & set(b.tags)) / max(len(a.tags), len(b.tags)),
    }
    
    weights = {
        "key_match": 0.4,
        "type_match": 0.3,
        "semantic_similarity": 0.2,
        "tag_overlap": 0.1,
    }
    
    return sum(similarity_scores[k] * weights[k] for k in weights.keys())
```

### Merging Strategy

When `similarity_score > 0.85`, merge patterns:

```python
def merge_patterns(primary: PatternEntry, duplicate: PatternEntry) -> PatternEntry:
    """
    Merge duplicate patterns, keeping highest-value data.
    """
    merged = PatternEntry(
        key=primary.key,  # Keep primary key
        value=primary.value if primary.confidence > duplicate.confidence else duplicate.value,
        pattern_type=primary.pattern_type,
        frequency=primary.frequency + duplicate.frequency,  # Combine counts
        success_rate=(
            (primary.success_rate * primary.frequency + 
             duplicate.success_rate * duplicate.frequency) /
            (primary.frequency + duplicate.frequency)
        ),  # Weighted average
        confidence=max(primary.confidence, duplicate.confidence),
        tags=list(set(primary.tags) | set(duplicate.tags)),  # Union of tags
        metadata={
            **primary.metadata,
            **duplicate.metadata,
            "merged_from": [primary.key, duplicate.key],
            "merge_timestamp": datetime.now(timezone.utc).isoformat(),
        },
        last_accessed=max(primary.last_accessed, duplicate.last_accessed),
    )
    return merged
```

---

## Transfer Scheduling Algorithm

The consolidation process triggers automatically or on-demand:

### Automatic Trigger

```python
def should_consolidate(current_state: MemoryState) -> bool:
    """
    Determine if consolidation should run automatically.
    """
    fill_ratio = current_state.stm_count / current_state.stm_capacity
    
    # Primary trigger: STM fill ratio exceeds threshold
    if fill_ratio > CONSOLIDATION_THRESHOLD:  # 0.80
        return True
    
    # Secondary trigger: Time-based (daily consolidation)
    time_since_last = datetime.now() - current_state.last_consolidation
    if time_since_last > timedelta(hours=24):
        return True
    
    # Tertiary trigger: Anomaly detection
    if current_state.anomaly_score > 0.8:
        return True
    
    return False
```

### Scheduling Window

```
Consolidation runs in these windows (UTC):

Production:
  - 03:00 UTC (daily deep clean)
  - On-demand via API (immediate)
  - Automatic when STM > 80% (reactive)

Test/Dev:
  - Any time (no restrictions)
  - Smaller batch sizes for validation

Optimization:
  - Cluster consolidations: batch multiple sessions
  - Avoid peak hours: defer if CPU > 80%
  - Rate limit: max 1 per 10 minutes globally
```

---

## Error Handling & Rollback

### Transaction Safety

```python
def consolidate_with_rollback(plan: ConsolidationPlan) -> Result:
    """
    Execute consolidation with automatic rollback on error.
    """
    try:
        with db.transaction():  # ACID guarantees
            # Phase 4: Execute plan
            promoted_keys = execute_promotions(plan.promote)
            pruned_keys = execute_pruning(plan.prune)
            
            # Verify result
            assert len(promoted_keys) == len(plan.promote)
            assert len(pruned_keys) == len(plan.prune)
            
            # Commit
            db.commit()
            
            return Result.success(
                promoted=len(promoted_keys),
                pruned=len(pruned_keys),
            )
    
    except Exception as e:
        db.rollback()  # Automatic on context exit
        logger.error(f"Consolidation failed: {e}")
        return Result.failure(reason=str(e))
```

### Data Validation

```python
def validate_consolidation_result(before: State, after: State) -> bool:
    """
    Validate consolidation preserved all data.
    """
    # Check: No data loss
    total_before = before.stm_count + before.ltm_count
    total_after = after.stm_count + after.ltm_count
    
    if total_before != total_after:
        raise DataIntegrityError(
            f"Data loss detected: {total_before} -> {total_after}"
        )
    
    # Check: No duplicates introduced
    if after.duplicate_count > 0:
        raise DataIntegrityError(
            f"Duplicates detected: {after.duplicate_count}"
        )
    
    # Check: All policies respected
    if after.policy_violations > 0:
        raise PolicyViolationError(
            f"Policy violations: {after.policy_violations}"
        )
    
    return True
```

---

## Monitoring & Observability

### Consolidation Metrics

```python
@dataclass
class ConsolidationMetrics:
    """Metrics for a consolidation cycle."""
    
    timestamp: datetime
    operation_id: str
    
    # Counts
    stm_count_before: int
    stm_count_after: int
    ltm_count_before: int
    ltm_count_after: int
    
    # Promotions
    patterns_promoted: int
    promotion_accuracy: float  # % still valuable after 30d
    
    # Pruning
    patterns_pruned: int
    archive_size_delta: int
    
    # Performance
    duration_ms: float
    throughput: float  # patterns/ms
    
    # Storage
    compression_rate: float  # ltm_size / total_size
    size_delta: int
    
    # Quality
    data_integrity: str  # "verified" | "warning" | "error"
    policy_compliance: float  # 0.0-1.0
```

### Alerting Thresholds

```yaml
alerts:
  high:
    - consolidation_duration > 10s
    - data_integrity != "verified"
    - policy_compliance < 0.99
    - promotion_accuracy < 0.90
  
  medium:
    - compression_rate < 0.5
    - stm_fill_ratio > 0.95
    - ltm_fill_ratio > 0.95
  
  low:
    - consolidation_frequency > 6/hour
    - promotion_accuracy < 0.98
    - size_delta > 1MB
```

---

## Performance Targets & Validation

### Target Metrics

| Metric | Target | Method |
|--------|--------|--------|
| Consolidation latency | < 10 seconds | Time entire cycle |
| Transfer overhead | < 2% of execution time | (duration_ms / session_duration_ms) |
| LTM size after prune | < 50MB | du -sh .codex/ltm/ |
| Promotion accuracy | > 98% | Track promoted items for 30 days |
| Pruning compression | > 10:1 | Measure duplicate reduction |
| Data integrity | 100% | Verify before==after sums |
| Pattern tagging accuracy | > 98% | Manual validation sample |
| Zero failed consolidations | 100% | Log all operations |

### Validation Tests

```python
class ConsolidationValidationSuite:
    """Comprehensive validation for consolidation pipeline."""
    
    def test_zero_data_loss(self):
        """Verify no patterns are lost during consolidation."""
        
    def test_promotion_accuracy(self):
        """Verify >98% of promoted patterns are still valuable."""
        
    def test_pattern_tagging(self):
        """Verify pattern tags match expected classification."""
        
    def test_retention_policy_compliance(self):
        """Verify 100% of patterns follow assigned retention policy."""
        
    def test_transfer_overhead(self):
        """Verify consolidation adds <2% overhead."""
        
    def test_duplicate_detection(self):
        """Verify duplicate detection and merging works correctly."""
        
    def test_graph_consistency(self):
        """Verify knowledge graph has no orphaned edges."""
```

---

## Operational Guidelines

### Normal Operation

```
1. Monitor STM fill ratio (target: 0-80%)
2. Run daily consolidation at 03:00 UTC
3. Archive patterns older than 7 years (compliance)
4. Validate data integrity after each consolidation
5. Generate daily health reports
```

### Troubleshooting

| Issue | Root Cause | Resolution |
|-------|-----------|-----------|
| STM > 90% fill | Consolidation not running | Check scheduler, manually trigger |
| LTM > 90% fill | Archive not running | Verify retention policies, prune old entries |
| Data integrity error | DB corruption | Restore from backup, run validation |
| High latency | Large batch size | Reduce max_promote_per_cycle |
| Low accuracy | Scoring algorithm | Review parameters, retrain thresholds |

### Recovery Procedures

```
If consolidation fails:

1. Check error message in consolidation_log
2. Verify database integrity (PRAGMA integrity_check)
3. Restore from backup if corrupted
4. Re-run consolidation with smaller batch size
5. Escalate if > 2 consecutive failures
```

---

## Next Steps

1. ✅ **Pipeline specification** (this document)
2. **Pruning engine implementation** (ltm_pruning_engine.py)
3. **Pattern tagger implementation** (pattern_tagger.py)
4. **Health dashboard** (PHASE_10_2_MEMORY_HEALTH.md)
5. **Integration tests** (test_memory_consolidation.py)
6. **Production deployment** (Day 8)

---

**Document Status:** PRODUCTION READY  
**Next Review:** 2026-07-08  
**Owner:** @mbaetiong (memory-sync-agent)

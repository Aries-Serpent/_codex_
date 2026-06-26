# Phase 10.2: STM → LTM Memory Consolidation System

**Status:** 🟢 IN PROGRESS  
**Date:** 2026-07-01  
**Target Completion:** 2026-07-06  
**Authority:** @mbaetiong (D-tier, fully autonomous)

---

## Executive Summary

This document describes the comprehensive memory consolidation system that automatically promotes valuable patterns from short-term memory (STM) to long-term memory (LTM), implements retention policies, and maintains a knowledge graph for rapid pattern retrieval.

**Key Objectives:**
- Automatic pattern discovery and promotion (frequency, recency, importance)
- Multi-policy retention system (evergreen, standard, decay, archived)
- Knowledge graph construction with 50+ patterns
- <10s consolidation latency per session
- 90%+ promotion accuracy

---

## Architecture Overview

### Memory Hierarchy

```
┌─────────────────────────────────────────────────┐
│         AGENT SESSION (Session N)               │
├─────────────────────────────────────────────────┤
│  STM (Short-Term Memory)                        │
│  ├─ Recent events (last 30 mins)                │
│  ├─ Active patterns (frequency 1-3)             │
│  └─ Discovery queue                             │
│  Capacity: ~100-200 entries                     │
└──────────┬──────────────────────────────────────┘
           │ CONSOLIDATION TRIGGER
           │ (stm_count > capacity × 0.8)
           ▼
┌─────────────────────────────────────────────────┐
│  LTM (Long-Term Memory)                         │
│  ├─ Promoted patterns (frequency ≥ 3)           │
│  ├─ High-confidence items                       │
│  ├─ Policy-governed retention                   │
│  └─ Knowledge graph indexed                     │
│  Capacity: ~5,000-10,000 entries               │
└──────────┬──────────────────────────────────────┘
           │ ARCHIVE/CLEANUP
           │ (age > retention window)
           ▼
┌─────────────────────────────────────────────────┐
│  Archive (Compressed History)                   │
│  ├─ Low-confidence items                        │
│  ├─ Aged-out patterns                           │
│  └─ Historical reference                        │
│  Capacity: Unbounded                            │
└─────────────────────────────────────────────────┘
```

### Consolidation Workflow

```
Phase 1: OBSERVE
├─ Query STM state (count, capacity)
└─ Query LTM state (count, policies)

Phase 2: ORIENT
├─ Rank STM entries by access_count DESC
├─ Identify hot entries (access_count ≥ 3)
├─ Scan LTM for cold entries (age > retention_window, confidence < threshold)
└─ Classify patterns by type

Phase 3: DECIDE
├─ Calculate consolidation plan
│  ├─ N_promote = len([e for e in stm if e.access_count ≥ 3])
│  ├─ N_prune = len([e for e in ltm if age > window and conf < threshold])
│  └─ Tags per pattern (ImprovementArea keywords)
└─ Generate diff

Phase 4: ACT
├─ SQLite direct writes
│  ├─ INSERT ltm_entries (key, value, confidence, pattern_type, timestamp)
│  ├─ DELETE stm_entries (WHERE access_count ≥ 3)
│  └─ DELETE ltm_entries (WHERE age > window AND confidence < threshold)
└─ Update graph relationships

Phase 5: ANALYZE
├─ Measure consolidation metrics
│  ├─ N_promoted (# patterns promoted)
│  ├─ N_pruned (# patterns pruned)
│  ├─ compression_rate = ltm_size / (stm_size + ltm_size)
│  └─ duration_ms
└─ Log all operations
```

---

## Pattern Discovery System

### Pattern Types

#### 1. **Decision Patterns**
- **Description:** Recurring decision scenarios and outcomes
- **Identifier:** Decision branches encountered ≥3 times
- **Metrics:** success_rate, decision_type, outcome_distribution
- **Example:** "When choosing between algorithm A vs B, B is chosen 80% of the time with 95% success"

#### 2. **Error Patterns**
- **Description:** Recurring errors and successful fixes
- **Identifier:** Exception types encountered ≥3 times
- **Metrics:** error_type, frequency, fix_method, resolution_rate
- **Example:** "Import errors in CI resolved by clearing pip cache 100% of the time"

#### 3. **Performance Patterns**
- **Description:** Latency/throughput correlations
- **Identifier:** Performance metrics sampled ≥3 times
- **Metrics:** latency_mean, throughput_mean, correlation_coefficient
- **Example:** "Batch size 32 consistently achieves 2.5x throughput vs batch size 8"

#### 4. **Success Patterns**
- **Description:** Patterns correlated with successful outcomes
- **Identifier:** Patterns preceding successful sessions ≥3 times
- **Metrics:** success_rate, pattern_specificity, impact_score
- **Example:** "Running pre-commit checks before pushing reduces CI failures by 75%"

#### 5. **Risk Patterns**
- **Description:** Patterns indicating high-risk conditions
- **Identifier:** Patterns preceding failures ≥3 times
- **Metrics:** risk_score, incident_frequency, severity
- **Example:** "Missing .gitignore entries causes accidental secret commits 90% of the time"

### Pattern Scoring Algorithm

```python
def calculate_pattern_score(entry: PatternEntry) -> float:
    """
    Pattern Score = (Frequency × Recency × Importance) / Age_Decay
    
    Components:
    - Frequency: access_count / threshold (capped at 1.0)
    - Recency: exp(-(days_since_last_access / 30))
    - Importance: success_rate | impact_score | risk_score (0-1)
    - Age_Decay: exp(days_since_creation / 90)
    
    Range: 0.0 - 1.0
    Promotion Threshold: ≥ 0.6 (80% of patterns)
    """
    frequency = min(entry.access_count / 5, 1.0)  # Normalize to 5+
    recency = math.exp(-(entry.days_since_access / 30))
    importance = getattr(entry, 'success_rate', 0.5)
    age_decay = math.exp(entry.days_since_creation / 90)
    
    return (frequency * recency * importance) / age_decay
```

---

## LTM Retention Policies

### 1. **Evergreen Policy**
- **Definition:** Permanent retention
- **Candidates:** Successful patterns, security fixes, critical workflows
- **Criteria:** `success_rate > 0.95 OR tagged:security OR tagged:critical`
- **Retention:** Infinite
- **Characteristics:** Protected (never auto-pruned)

### 2. **Standard Policy**
- **Definition:** Fixed-window retention
- **Candidates:** Most discovered patterns
- **Criteria:** `success_rate > 0.70 AND NOT evergreen`
- **Retention:** 90 days
- **Characteristics:** Auto-pruned after window if not accessed

### 3. **Decay Policy**
- **Definition:** Exponential confidence decay
- **Candidates:** Medium-value patterns with uncertain future relevance
- **Criteria:** `0.50 < success_rate ≤ 0.70`
- **Retention:** Exponential decay to 0 confidence over 180 days
- **Characteristics:** Gradually fades; purged when confidence < 0.1

### 4. **Archived Policy**
- **Definition:** Compressed historical storage
- **Candidates:** Aged-out patterns, low-confidence items
- **Criteria:** `success_rate < 0.50 OR age > retention_window`
- **Retention:** 1 year (queryable via archive search)
- **Characteristics:** Compressed; queryable but not in active rotation

### Retention Timeline

```
Day 0    Day 30   Day 60   Day 90   Day 180  Day 365  Day 730+
├────────┼────────┼────────┼────────┼────────┼────────┼────────┤
         ├─ Evergreen: Permanent
                  ├─ Standard: High confidence → Archived after 90d
                           ├─ Decay: Exponential fade over 180d
                                    ├─ Archive: 1-year historical view
                                                ├─ Purge: Older items removed
```

---

## Knowledge Graph Structure

### Node Types

```
PATTERN
├─ id: unique pattern identifier
├─ name: descriptive name
├─ type: decision | error | performance | success | risk
├─ description: natural language summary
├─ metrics:
│  ├─ frequency: # of occurrences
│  ├─ success_rate: success outcomes / total
│  ├─ confidence: 0.0-1.0 promotion confidence
│  └─ last_accessed: timestamp
├─ policy: evergreen | standard | decay | archived
└─ tags: [ImprovementArea, keyword1, keyword2, ...]
```

### Edge Types

```
CAUSALITY
├─ source: pattern A
├─ target: pattern B
├─ weight: 0.0-1.0 (confidence)
└─ relationship_type: "causes" | "mitigates" | "correlates_with"

SUCCESSION
├─ source: pattern A
├─ target: pattern B
├─ weight: temporal co-occurrence probability
└─ temporal_offset: milliseconds between occurrences

SIMILARITY
├─ source: pattern A
├─ target: pattern B
├─ weight: similarity score (0.0-1.0)
└─ dimensions: [frequency, recency, type, tags]
```

### Graph Metrics

```
Size: 50-100 active patterns
      100-500 relationships (edges)
      5-10k archived pattern versions

Query Performance:
├─ Pattern lookup: <10ms
├─ Relationship traversal (depth 2): <50ms
├─ Graph export (GraphML): <500ms
└─ Complex pattern matching: <1s
```

---

## Implementation Components

### Core Modules

#### 1. `memory_consolidation.py` (250+ lines)
Consolidation orchestrator:
- `MemoryConsolidationEngine`: Main orchestrator class
- `ConsolidationStrategy`: Promotion/pruning logic
- `ConsolidationMetrics`: Performance tracking
- Methods: `run()`, `promote_patterns()`, `prune_stale()`, `log_operations()`

#### 2. `pattern_discovery.py` (250+ lines)
Pattern identification system:
- `PatternDiscovery`: Discovery engine
- `PatternScorer`: Scoring algorithm
- `PatternClassifier`: Type classification
- Methods: `discover()`, `score()`, `classify()`, `extract_metadata()`

#### 3. `ltm_retention.py` (200+ lines)
Retention policy manager:
- `RetentionPolicyManager`: Policy orchestrator
- `EvergreenPolicy`, `StandardPolicy`, `DecayPolicy`, `ArchivedPolicy`: Policy classes
- Methods: `apply_policy()`, `cleanup()`, `calculate_retention_window()`, `archive()`

#### 4. `pattern_graph.py` (300+ lines)
Knowledge graph builder:
- `PatternNode`: Graph node representation
- `PatternEdge`: Relationship representation
- `PatternGraph`: Graph container
- `GraphBuilder`: Construction logic
- Methods: `add_node()`, `add_edge()`, `query()`, `export_graphml()`, `compute_metrics()`

#### 5. `memory_sync.py` (Integration module)
Session integration:
- `SessionMemorySynchronizer`: Entry point
- Hooks: `on_session_end()`, `on_checkpoint()`, `on_session_resume()`

### Configuration Files

#### `.codex/PHASE_10_2_CONSOLIDATION_CONFIG.yaml`
```yaml
memory:
  stm_capacity: 500
  ltm_capacity: 10000
  consolidation_threshold: 0.80  # Trigger at 80% STM fill

promotion:
  frequency_threshold: 3  # Minimum access count
  score_threshold: 0.60   # Promotion score threshold
  max_promote_per_cycle: 100  # Limit promotions

patterns:
  types:
    - decision
    - error
    - performance
    - success
    - risk
  discovery_interval: 3600  # seconds
  
cleanup:
  daily: "03:00"  # UTC
  prune_old_patterns: true
  archive_interval: 7  # days
```

#### `.codex/PHASE_10_2_RETENTION_POLICIES.yaml`
```yaml
policies:
  evergreen:
    retention_days: null  # Permanent
    criteria:
      - "success_rate > 0.95"
      - "tag:security"
      - "tag:critical"
    protected: true
    
  standard:
    retention_days: 90
    criteria:
      - "success_rate > 0.70"
    protected: false
    
  decay:
    retention_days: 180
    criteria:
      - "0.50 < success_rate <= 0.70"
    decay_function: "exponential"
    decay_halflife: 60  # days
    protected: false
    
  archived:
    retention_days: 365
    criteria:
      - "age > standard_window"
    compressed: true
    queryable: true
```

---

## Integration Points

### Session Lifecycle Hooks

```python
# On session end
@hook("session:end")
def consolidate_on_session_end(session_context):
    """Consolidate STM→LTM when session ends"""
    engine = MemoryConsolidationEngine()
    engine.run(session_context)

# On checkpoint creation
@hook("checkpoint:created")
def preserve_on_checkpoint(checkpoint_context):
    """Preserve LTM state in checkpoint"""
    checkpoint_context.ltm_snapshot = get_ltm_state()

# On session resume
@hook("session:resume")
def inject_on_resume(session_context):
    """Inject relevant LTM patterns on resume"""
    patterns = query_relevant_patterns(session_context)
    session_context.injected_patterns = patterns
```

### Agent Framework Integration

- **Frequency Tracking:** Agent captures `event_type`, `timestamp`, `outcome`
- **Outcome Recording:** Session stores `success/failure`, `duration`, `metrics`
- **Pattern Extraction:** On consolidation, engine analyzes event sequences
- **Recommendation Injection:** Resume injects top-N patterns for context

---

## Success Metrics

### Consolidation Accuracy
- **Promotion Accuracy:** % of promoted patterns still valuable after 30 days (target: >90%)
- **False Positive Rate:** % of promoted patterns with low usage (target: <5%)
- **False Negative Rate:** % of valuable patterns not promoted (target: <2%)

### Performance
- **Consolidation Latency:** Time to run full consolidation cycle (target: <10s)
- **Pattern Discovery Latency:** Time to classify and score new patterns (target: <1s)
- **Graph Query Latency:** Time to retrieve related patterns (target: <100ms)

### Coverage
- **Pattern Count:** Active LTM patterns at any time (target: 50+)
- **Pattern Diversity:** Distribution across 5 pattern types (target: balanced)
- **Relationship Count:** Edges in knowledge graph (target: 100+)

### Quality
- **Retention Policy Compliance:** % patterns following assigned policy (target: 100%)
- **Memory Consistency:** No corrupted LTM entries (target: 0 issues)
- **Storage Efficiency:** Compression ratio for archived patterns (target: 10:1)

---

## Deployment Roadmap

### Phase 1: Core Implementation (Day 1-2)
- [ ] Implement consolidation engine
- [ ] Implement pattern discovery
- [ ] Implement retention policies
- [ ] Create configuration files

### Phase 2: Graph Construction (Day 2-3)
- [ ] Build pattern graph framework
- [ ] Implement graph export/visualization
- [ ] Create 50+ test patterns
- [ ] Validate graph queries

### Phase 3: Integration (Day 3-4)
- [ ] Wire session lifecycle hooks
- [ ] Implement checkpoint/resume
- [ ] Deploy to test environment
- [ ] Run integration tests

### Phase 4: Validation & Monitoring (Day 4-5)
- [ ] Run production validation
- [ ] Monitor consolidation metrics
- [ ] Document operations guide
- [ ] Final go/no-go decision

---

## Reference Materials

- **Configuration:** `.codex/PHASE_10_2_CONSOLIDATION_CONFIG.yaml`
- **Policies:** `.codex/PHASE_10_2_RETENTION_POLICIES.yaml`
- **Deployment:** `.codex/PHASE_10_2_DEPLOYMENT_GUIDE.md`
- **Operations:** `.codex/PHASE_10_2_OPERATIONS_GUIDE.md`
- **Graph Guide:** `.codex/PHASE_10_2_PATTERN_GRAPH_GUIDE.md`

---

## Next Steps

1. Implement `memory_consolidation.py` (Task 10.2.1)
2. Implement `pattern_discovery.py` (Task 10.2.2)
3. Implement `ltm_retention.py` (Task 10.2.3)
4. Implement `pattern_graph.py` + tests (Task 10.2.4)
5. Deploy and integrate (Task 10.2.5)

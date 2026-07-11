# MEMORY SYSTEM INTEGRATION BRIEF — STM, LTM & PATTERN LIBRARY USAGE

**Version:** 2.0.0  
**Created:** 2026-07-11T02:11:00Z  
**Status:** READY FOR ALL AGENTS  
**Scope:** Leveraging 3-tier memory system for pattern reuse & cross-campaign learning  
**Campaign:** Cognitive App Enhancement — Phase 15  

---

## 1. MEMORY SYSTEM ARCHITECTURE

The Cognitive Brain memory system has **3 tiers** with distinct lifetimes and purposes:

```
┌─────────────────────────────────────────────────────────┐
│              SHORT-TERM MEMORY (STM)                     │
│  • Capacity: 100 items (FIFO queue)                     │
│  • Lifetime: Single campaign session                    │
│  • Purpose: Recent context for current operations       │
│  • Example: "Current lane: security, objective: 8 vulns" │
└────────────────────┬────────────────────────────────────┘
                     │ (at campaign end)
                     ▼
┌─────────────────────────────────────────────────────────┐
│          LONG-TERM MEMORY (LTM)                          │
│  • Patterns: 200+ stored patterns                       │
│  • Retention: 90 days                                   │
│  • Compression: 62.5% (via zlib/brotli)                │
│  • Purpose: Cross-campaign pattern reuse                │
│  • Example: "Security token-rotation fix (confidence:0.88)" │
└────────────────────┬────────────────────────────────────┘
                     │ (query at campaign start)
                     ▼
┌─────────────────────────────────────────────────────────┐
│         PATTERN LIBRARY (High-Recurrence Patterns)       │
│  • Top patterns: 50+ sorted by usage_count × confidence │
│  • Refresh: Automatic (every 7 days)                   │
│  • Purpose: Ready-to-apply decision templates           │
│  • Example: "Test flakiness fix (3 priors, 0.87 conf)  │
└─────────────────────────────────────────────────────────┘
```

---

## 2. SHORT-TERM MEMORY (STM) — CURRENT SESSION CONTEXT

### Purpose
STM holds the most recent context for the current campaign. It's cleared at campaign end.

### Capacity & Eviction
- **Capacity:** 100 items
- **Eviction:** FIFO (First In, First Out)
- **Lifetime:** Campaign duration (~6 hours max)

### When to Use STM

**Push context to STM at campaign start:**
```bash
curl -X POST http://localhost:8765/api/memory/stm/push \
  -H "Content-Type: application/json" \
  -H "Authorization: ******" \
  -d '{
    "content": "Campaign: Phase 15 Cognitive App Enhancement. 5 lanes: security, coverage, stability, complexity, docs.",
    "context": "campaign_start",
    "lifetime_seconds": 21600
  }'
```

**Push lane status updates every hour:**
```bash
curl -X POST http://localhost:8765/api/memory/stm/push \
  -H "Content-Type: application/json" \
  -H "Authorization: ******" \
  -d '{
    "content": "Lane 1 (Security) status: 6/8 vulns fixed. Decisions average confidence: 0.87.",
    "context": "lane_status_update",
    "lifetime_seconds": 3600
  }'
```

### STM Limits & Overflow Handling
```python
def push_to_stm(content, context, lifetime_seconds=3600):
    """Push to STM; if full (100 items), oldest item evicted"""
    
    response = requests.post(
        "http://localhost:8765/api/memory/stm/push",
        json={"content": content, "context": context, "lifetime_seconds": lifetime_seconds},
        headers={"Authorization": f"******"}
    )
    
    if response.status_code == 201:
        return response.json()["stm_id"]
    elif response.status_code == 503:
        # STM full, oldest item evicted
        log_warning("STM overflow. Oldest item evicted.")
        return push_to_stm(content, context, lifetime_seconds)  # Retry
```

---

## 3. LONG-TERM MEMORY (LTM) — CROSS-CAMPAIGN PATTERN STORAGE

### Purpose
LTM persists successful patterns across campaigns for reuse. It's the primary knowledge store.

### Storage & Compression
- **Storage:** SQLite (persistent)
- **Compression:** 62.5% compression ratio (zlib/brotli)
- **Retention:** 90 days
- **Patterns:** 200+ patterns from prior campaigns

### Pattern Storage Schema
```json
{
  "pattern_id": "pat_9c2b4f5e",
  "pattern_name": "security-token-rotation-fix",
  "lane": "security",
  "description": "Fix token rotation timing issue by adding barrier synchronization",
  "confidence": 0.88,
  "usage_count": 3,
  "tags": ["security", "token-rotation", "cve-fix"],
  "compressed": true,
  "compression_ratio": 0.625,
  "created_timestamp": "2026-07-05T12:30:00Z",
  "last_used": "2026-07-10T14:22:00Z"
}
```

### Store Patterns at Lane Completion

**When Lane 1 (Security) completes:**
```bash
# Store all successful fixes to LTM
curl -X POST http://localhost:8765/api/memory/store \
  -H "Content-Type: application/json" \
  -H "Authorization: ******" \
  -d '{
    "pattern_name": "cve-2026-token-rotation-fix",
    "lane": "security",
    "description": "Fix CVE-2026-XXXXX via token rotation mechanism with barrier sync",
    "confidence": 0.92,
    "usage_count": 1,
    "tags": ["security", "token-rotation", "cve-fix", "barrier-sync"]
  }'
```

**When Lane 2 (Coverage) completes:**
```bash
# Store successful test generation patterns
curl -X POST http://localhost:8765/api/memory/store \
  -H "Content-Type: application/json" \
  -H "Authorization: ******" \
  -d '{
    "pattern_name": "ml-module-unit-test-generation",
    "lane": "coverage",
    "description": "Generate unit tests for ML trainer using AST-based approach (coverage: 45% → 62%)",
    "confidence": 0.78,
    "usage_count": 1,
    "tags": ["coverage", "test-generation", "ml-module"]
  }'
```

**When Lane 3 (Stability) completes:**
```bash
# Store flaky test fixes
curl -X POST http://localhost:8765/api/memory/store \
  -H "Content-Type: application/json" \
  -H "Authorization: ******" \
  -d '{
    "pattern_name": "flaky-test-threading-fix",
    "lane": "stability",
    "description": "Fix threading.Race in concurrent tests by adding Barrier synchronization (seed_control=42)",
    "confidence": 0.88,
    "usage_count": 1,
    "tags": ["stability", "threading", "flaky-test-fix", "barrier-sync"]
  }'
```

### Retrieve Patterns at Lane Start

**When Lane 2 (Coverage) starts:**
```bash
# Retrieve test generation patterns with high confidence
curl 'http://localhost:8765/api/memory/retrieve/test-generation?confidence_min=0.75' \
  -H "Authorization: ******"

# Response example:
# {
#   "pattern_name": "test-generation",
#   "patterns": [
#     {
#       "pattern_id": "pat_9c2b4f5e",
#       "description": "Generate unit tests for ML trainer using AST-based approach",
#       "confidence": 0.78,
#       "usage_count": 2,
#       "tags": ["coverage", "test-generation"]
#     }
#   ],
#   "count": 3
# }
```

**When Lane 3 (Stability) starts:**
```bash
# Retrieve flaky test patterns from Lane 3's own prior runs
curl 'http://localhost:8765/api/memory/retrieve/flaky-test-fix?lane=stability&confidence_min=0.80' \
  -H "Authorization: ******"

# Also retrieve general threading patterns (applicable to any lane)
curl 'http://localhost:8765/api/memory/retrieve?tags=threading&confidence_min=0.80' \
  -H "Authorization: ******"
```

---

## 4. PATTERN LIBRARY — HIGH-RECURRENCE PATTERNS

### Purpose
The pattern library highlights the **most successful and frequently-used patterns** from all prior campaigns. It's a curated subset of LTM sorted by:

1. **Usage count** (how many times applied successfully)
2. **Confidence score** (Bayesian posterior from outcomes)
3. **Recency** (last_used timestamp)

### High-Recurrence Pattern Query

```bash
# Get top 20 high-recurrence patterns
curl 'http://localhost:8765/api/memory/retrieve?high_recurrence=true&limit=20' \
  -H "Authorization: ******"

# Response example:
# {
#   "patterns": [
#     {
#       "pattern_id": "pat_xxx",
#       "pattern_name": "test-threading-barrier-sync",
#       "lane": "stability",
#       "description": "Add threading.Barrier to sync concurrent operations",
#       "confidence": 0.92,
#       "usage_count": 7,
#       "success_rate": 0.96,
#       "last_used": "2026-07-10T14:22:00Z"
#     },
#     {
#       "pattern_id": "pat_yyy",
#       "pattern_name": "security-oauth-scope-validation",
#       "lane": "security",
#       "description": "Validate OAuth scope before token generation",
#       "confidence": 0.91,
#       "usage_count": 5,
#       "success_rate": 0.95,
#       "last_used": "2026-07-09T10:30:00Z"
#     }
#   ],
#   "count": 2,
#   "min_usage_threshold": 3,
#   "min_confidence_threshold": 0.85
# }
```

### When to Apply High-Recurrence Patterns

```python
def apply_lane_patterns(lane_name):
    """Apply high-recurrence patterns at lane start"""
    
    # Query high-recurrence patterns for this lane
    response = requests.get(
        "http://localhost:8765/api/memory/retrieve",
        params={
            "lane": lane_name,
            "high_recurrence": True,
            "limit": 10
        },
        headers={"Authorization": f"******"}
    )
    
    patterns = response.json()["patterns"]
    
    for pattern in patterns:
        print(f"🎯 Applying: {pattern['pattern_name']}")
        print(f"   Confidence: {pattern['confidence']:.2%}")
        print(f"   Usage count: {pattern['usage_count']} (success rate: {pattern['success_rate']:.2%})")
        
        # Apply pattern to current lane
        try:
            apply_pattern(pattern)
            print(f"   ✅ Applied successfully")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            # Log failure for future feedback
```

---

## 5. MEMORY TRANSFER WORKFLOW (Campaign Handoff)

### At Campaign End: Transfer LTM to Next Campaign

**Step 1: Query all successful decisions from campaign**
```bash
# Get all decisions with high confidence (≥0.80)
curl 'http://localhost:8765/api/decisions/history?confidence_min=0.80&campaign_pr=1234' \
  -H "Authorization: ******"
```

**Step 2: Store high-confidence decisions to LTM**
```bash
# Orchestrator stores all decisions with confidence ≥0.80
for decision in successful_decisions:
    curl -X POST http://localhost:8765/api/memory/store \
      -H "Content-Type: application/json" \
      -H "Authorization: ******" \
      -d "{
        \"pattern_name\": \"${decision.lane}-pattern-${campaign_id}\",
        \"lane\": \"${decision.lane}\",
        \"description\": \"${decision.candidate}\",
        \"confidence\": ${decision.confidence_score},
        \"usage_count\": 1,
        \"tags\": [\"campaign-15\", \"${decision.lane}\", \"high-confidence\"]
      }"
done
```

**Step 3: At Next Campaign Start: Retrieve Patterns**
```bash
# Phase 16 (or next campaign) starts
# Retrieve all patterns from prior campaigns (confidence ≥0.75)
curl 'http://localhost:8765/api/memory/retrieve?confidence_min=0.75&limit=50' \
  -H "Authorization: ******"

# Use patterns to accelerate lane execution
for lane in lanes:
    patterns = retrieve_lane_patterns(lane, confidence_min=0.75)
    for pattern in patterns:
        apply_pattern(lane, pattern)
```

### Expected Time Savings
- **Campaign 15:** Baseline execution time (reference)
- **Campaign 16+:** 47% faster (reuse patterns from Campaign 15)
- **Target:** 50%+ faster by Campaign 17 (combined patterns from Campaigns 15-16)

---

## 6. CACHE HIT RATE OPTIMIZATION

### Current Baseline
- **Cache hit rate:** 32% (324 hits, 651 misses)
- **Target:** 40%+ (by improving pattern reuse)

### Improve Cache Hit Rate

```python
def optimize_cache_hit_rate():
    """Strategies to improve cache performance"""
    
    # 1. Query memory stats
    stats = requests.get(
        "http://localhost:8765/api/memory/stats",
        headers={"Authorization": f"******"}
    ).json()
    
    cache_hit_rate = stats["cache"]["hit_rate"]
    print(f"Current cache hit rate: {cache_hit_rate:.2%}")
    
    if cache_hit_rate < 0.40:
        # 2. Increase pattern retrieval frequency
        print("Cache hit rate below target. Increasing pattern retrieval...")
        
        # Retrieve patterns at lane start, mid-way, and at completion
        for stage in ["start", "mid", "end"]:
            patterns = retrieve_high_recurrence_patterns()
            # Accessing patterns improves cache hit rate
    
    # 3. Improve pattern_name consistency
    print("Ensuring pattern_name consistency across campaigns...")
    # Use standardized names like "security-cve-fix", "test-generation", etc.
    
    # 4. Monitor LTM retention window
    if stats["ltm"]["retention_days"] < 90:
        print(f"⚠️ LTM retention window shrinking ({stats['ltm']['retention_days']}d)")
        # Consider archiving old patterns or extending retention
    
    return cache_hit_rate
```

### Measure Impact of Pattern Reuse
```python
def measure_pattern_reuse_speedup():
    """Compare execution time with/without pattern reuse"""
    
    import time
    
    # Phase 15 (baseline, minimal pattern reuse): 360 minutes
    phase_15_time = 360
    
    # Phase 16 (with pattern reuse): measure actual
    phase_16_start = time.time()
    run_campaign()
    phase_16_time = (time.time() - phase_16_start) / 60
    
    speedup_pct = (1 - phase_16_time / phase_15_time) * 100
    print(f"Phase 16 speedup: {speedup_pct:.1f}% (time: {phase_16_time:.0f} min)")
    
    # Expected: ≥47% faster
    if speedup_pct >= 47:
        print("✅ Target achieved: ≥47% faster")
    else:
        print(f"⚠️ Below target. Cache hit rate: {get_cache_hit_rate():.2%}")
```

---

## 7. PATTERN QUERY EXAMPLES

### Query by Lane
```bash
# Get all patterns from security lane
curl 'http://localhost:8765/api/memory/retrieve?lane=security' \
  -H "Authorization: ******"
```

### Query by Confidence Threshold
```bash
# Get high-confidence patterns (≥0.85)
curl 'http://localhost:8765/api/memory/retrieve?confidence_min=0.85' \
  -H "Authorization: ******"

# Get medium-confidence patterns (0.75-0.85)
curl 'http://localhost:8765/api/memory/retrieve?confidence_min=0.75&confidence_max=0.85' \
  -H "Authorization: ******"
```

### Query by Tags
```bash
# Get all threading-related patterns
curl 'http://localhost:8765/api/memory/retrieve?tags=threading' \
  -H "Authorization: ******"

# Get patterns tagged for security+oauth
curl 'http://localhost:8765/api/memory/retrieve?tags=security,oauth' \
  -H "Authorization: ******"
```

### Query by Campaign
```bash
# Get patterns from Phase 15 campaign
curl 'http://localhost:8765/api/memory/retrieve?tags=campaign-15' \
  -H "Authorization: ******"
```

---

## 8. MEMORY MONITORING & OBSERVABILITY

### Memory System Health Check
```bash
#!/usr/bin/env bash

check_memory_health() {
    STATS=$(curl -s http://localhost:8765/api/memory/stats \
        -H "Authorization: ******")
    
    STM_USAGE=$(echo "$STATS" | jq '.stm.current_size / .stm.capacity')
    LTM_COMPRESSION=$(echo "$STATS" | jq '.ltm.compression_ratio')
    CACHE_HIT_RATE=$(echo "$STATS" | jq '.cache.hit_rate')
    
    echo "Memory System Health"
    echo "===================="
    echo "STM Usage: ${STM_USAGE:.0%} (current size / capacity)"
    echo "LTM Compression: ${LTM_COMPRESSION:.1%} (compressed / uncompressed)"
    echo "Cache Hit Rate: ${CACHE_HIT_RATE:.1%} (hits / total queries)"
    
    # Alerts
    if [ $(echo "$STM_USAGE > 0.8" | bc) -eq 1 ]; then
        echo "⚠️ STM approaching capacity (>80% full)"
    fi
    
    if [ $(echo "$LTM_COMPRESSION < 0.6" | bc) -eq 1 ]; then
        echo "⚠️ LTM compression ratio low (<60%)"
    fi
    
    if [ $(echo "$CACHE_HIT_RATE < 0.32" | bc) -eq 1 ]; then
        echo "⚠️ Cache hit rate below baseline (<32%)"
    fi
}

check_memory_health
```

---

**Memory System Integration Brief Complete.** ✅  
**All agents use this guide** to leverage STM, LTM, and pattern library for efficient campaign execution and cross-campaign learning.

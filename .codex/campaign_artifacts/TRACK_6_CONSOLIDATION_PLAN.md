# Track 6 — Memory Consolidation Plan for Gate 2→3
## STM/LTM Optimization & PDA Growth Strategy

**Plan Date:** 2026-06-16  
**Target Gate:** Gate 3 (2026-07-06, Day 20)  
**Target PDA:** 320+ (Current: 298)  
**Target Health:** 8.5+/10 (Current: 8.3/10)

---

## 🎯 CONSOLIDATION PHASE OVERVIEW

### Phase 2a: Quick Wins (Days 1-3)
**Effort:** Low | **Risk:** Very Low | **Expected Gain:** +30-43 PDA

#### 1.1 STM Hot Entry Threshold Tuning
```
Change: access_count >= 3  →  access_count >= 2
Rationale: More aggressive promotion of warm entries
Impact:
  - Additional 15-20 entries promoted to LTM per cycle
  - Lower fragmentation, higher cache efficiency
  - Compression rate: improves by 5-8%

Implementation:
  File: cognitive_app/src/server/cli_api_server.py
  Line: ~715 (memory_consolidate function)
  Change: Replace "access_count >= 3" with "access_count >= 2"
  Testing: Run memory_consolidate, verify stm_count decrease

PDA Gain: +15-20
Timeline: 1 hour (implementation + testing)
```

#### 1.2 Confidence Scoring Refinement
```
Change: Linear confidence  →  Weighted confidence
Current Formula:
  confidence = min(1.0, access_count / 10)

Proposed Formula:
  recency_weight = 0.4  (entries accessed in last 7 days)
  frequency_weight = 0.6 (normalized access_count)
  confidence = (recency_weight * 1.0) + (frequency_weight * min(1.0, access_count / 5))

Rationale: Reflect both freshness and popularity
Impact:
  - Better prediction of pattern relevance
  - Improved pruning accuracy
  - LTM entry quality: +15%

Implementation:
  File: cognitive_app/src/server/cli_api_server.py
  Function: memory_consolidate (line ~725)
  Testing: Run 100-entry consolidation cycle, validate confidence distribution

PDA Gain: +5-8
Timeline: 2 hours (implementation + testing)
```

#### 1.3 Pattern Keyword Tagging Expansion
```
Current Pattern Mapping (4 patterns):
  - "stm|ltm|memory|consolidat" → ML_PATTERN_FEEDING
  - "ci|fail|heal|self-heal" → CI_SELF_HEALING
  - "agent|chain|orchestrat" → AGENT_CHAINING
  - "coverage|test" → COVERAGE_IMPROVEMENT

Proposed Additions (6-8 new patterns):
  - "security|vulnerability|cve|scan" → SECURITY_HARDENING
  - "performance|optimization|cache|latency" → PERFORMANCE_TUNING
  - "documentation|readme|doc|api-docs" → DOCUMENTATION_QUALITY
  - "deployment|rollout|release|ci-cd" → DEPLOYMENT_RELIABILITY
  - "error|bug|fix|regression" → QUALITY_ASSURANCE
  - "architecture|refactor|modular|design" → ARCHITECTURE_EVOLUTION
  - "monitoring|observability|logging|telemetry" → OPERATIONAL_EXCELLENCE
  - "governance|policy|compliance|audit" → GOVERNANCE_MATURITY

Rationale: Expand coverage across all codex domains
Impact:
  - Capture previously unmapped patterns
  - Enable cross-domain analysis
  - New PDA opportunities: +40-60 across domains

Implementation:
  File: cognitive_app/src/server/cli_api_server.py
  Location: PATTERN_IMPROVEMENT_AREA mapping (around line 700-720)
  Testing: Run search on all new patterns, verify tagging accuracy

PDA Gain: +10-15
Timeline: 1.5 hours (pattern library creation + testing)
```

### Phase 2a Summary
```
Total Time: ~4.5 hours
Total PDA Gain: +30-43
Target State: 298 + 30 = 328 PDA ✅ EXCEEDS 320+ TARGET
Success Criteria:
  - All 3 changes committed
  - 100 test consolidation cycle runs cleanly
  - No health score regression
  - Compression rate ≥ 8%
```

---

### Phase 2b: Systematic Improvements (Days 4-7)
**Effort:** Medium | **Risk:** Low-Medium | **Expected Gain:** +30-50 PDA

#### 2.1 Cross-Session Memory Synthesis
```
Objective: Link patterns across 50+ past Copilot sessions
Current State: Single-session memory isolation
Opportunity: Multi-session pattern consolidation

Implementation Strategy:
  1. Query session_store_sql for all sessions in last 30 days
  2. Extract common pattern themes across sessions
  3. Create synthetic high-confidence LTM entries
  4. Tag with "cross_session_pattern" metadata

Data Sources:
  - turns table: user_message + assistant_response
  - session_files: modified files and tools used
  - checkpoints: session milestones and decisions
  - session_refs: linked PRs, issues, commits

Pattern Extraction Logic:
  - Identify recurring code patterns (e.g., "memory sync" appears in 15 sessions)
  - Identify recurring issue types (e.g., "ci-failure" + "heal")
  - Identify recurring tools usage (e.g., "task" agent + "test failures")
  - Aggregate confidence scores across sessions

Expected Discoveries:
  - 20-30 high-confidence cross-session patterns
  - 15-25 medium-confidence patterns
  - Confidence boost to existing patterns: +5-15%

Implementation Timeline:
  Days 4-5: Data extraction & analysis
  Days 5-6: Synthetic LTM entry creation
  Days 6-7: Integration & testing

PDA Gain: +30-50
Health Impact: +0.2-0.4 (higher confidence LTM)
```

#### 2.2 Agent-Memory Loop Integration
```
Objective: Direct orchestrator-memory wiring for agent decisions
Current State: CLI API silo (separate from agent invocations)
Opportunity: Real-time pattern injection into agent context

Integration Points:
  1. orchestrator-agent reads from memory_search API
  2. Injects top-5 relevant patterns into agent system prompt
  3. Agent decisions logged back to memory as high-confidence patterns
  4. Feedback loop: decision → confidence update

Benefits:
  - Agent decisions become patterns
  - Patterns inform agent decisions → virtuous cycle
  - Self-improving agent intelligence

Implementation:
  File: agents/orchestrator-agent.py (system prompt)
  Change: Add memory_search call before agent dispatch

  Pattern Injection Template:
    "Recent high-confidence patterns from memory:
     1. [Pattern A] (confidence: 0.95)
     2. [Pattern B] (confidence: 0.87)
     3. [Pattern C] (confidence: 0.79)"

Feedback Logging:
  After agent decision, create LTM entry:
    - key: "orchestrator_decision_{agent_id}_{timestamp}"
    - value: decision summary
    - metadata: agent_type, success_indicator
    - confidence: 0.8-1.0 (agent decisions weighted highly)

Expected Outcomes:
  - 25-40 new agent-decision patterns per gate
  - Agent consistency improvement: +10-15%
  - Decision quality: measurable improvement

PDA Gain: +20-30
Timeline: Days 4-7
```

### Phase 2b Summary
```
Total Time: ~4 days
Total PDA Gain: +50-80
Target State: 298 + 50 = 348 PDA ✅ WELL EXCEEDS TARGET
Success Criteria:
  - Cross-session patterns integrated
  - Orchestrator memory loop active
  - Agent decision logging active
  - Health score: 8.5+/10
  - Confidence distribution: 60%+ entries ≥0.7
```

---

## 📊 STM/LTM CONSOLIDATION SCHEDULE

### Daily Consolidation Cycle
```
Trigger Frequency: Every 30 minutes (configurable)
Trigger Threshold: stm_count/capacity > 0.80

Consolidation Operations:
1. Identify hot entries (access_count ≥ 2 after Phase 2a)
2. Calculate confidence scores (weighted formula)
3. Promote to LTM with metadata tags
4. Prune stale LTM entries (age > 30d AND confidence < 0.3)
5. Log metrics to action_log.ndjson
6. Report compression rate, cache hit rate

Monitoring:
  - POST /api/memory/consolidate every 30 min
  - Alert if compression_rate drops below 5%
  - Alert if cache_hit_rate drops below 60%
```

### Weekly Review Cycle
```
Schedule: Every Friday (2026-06-21, 06-28, 07-05)
Scope:
  1. STM/LTM balance analysis
  2. Confidence score distribution
  3. New pattern emergence
  4. Pruning effectiveness
  5. PDA growth trajectory

Output: Weekly consolidation report
```

---

## 🔍 METRICS TRACKING DURING CONSOLIDATION

### Key Metrics
```
1. STM Metrics
   - stm_count: target <350 (50% of capacity)
   - stm_avg_access_count: track average hotness
   - stm_turnover: entries promoted per day

2. LTM Metrics
   - ltm_count: target 100-200 (compressed patterns)
   - ltm_avg_confidence: target >0.75
   - ltm_pruning_rate: target 5-10% per week

3. Memory Health
   - compression_rate: target >10%
   - cache_hit_rate: target >75%
   - health_score: target 8.5+/10

4. PDA Metrics
   - pda_count: target 298→320+ progression
   - new_patterns_per_day: target ≥2
   - pattern_confidence_improvement: track monthly
```

### Tracking Dashboard
```
Location: MemoryManagementDashboard (React component)
Update Frequency: Real-time (via /api/memory/state)
Metrics Displayed:
  - STM: count, avg_access_count, fill %
  - LTM: count, avg_confidence, pruning rate
  - Health: overall score, cache hit rate
  - PDA: current count, trend, velocity
  - Consolidation: last run time, duration, entries processed
```

---

## ⚠️ RISK MITIGATION

### Risk 1: Confidence Score Regression
```
Risk: New confidence formula could lower average confidence
Impact: Reduced LTM entry reliability
Mitigation:
  - Test with historical data before committing
  - Cap confidence at 0.95 to preserve existing high-confidence patterns
  - A/B test: run both formulas in parallel for 1 day
  - Rollback capability: keep old formula available
```

### Risk 2: Over-Promotion of Hot Entries
```
Risk: Lowering threshold to >= 2 could promote noise
Impact: Lower LTM entry quality
Mitigation:
  - Add secondary filter: min_recency_score > 0.5
  - Monitor LTM compression rate (warn if <5%)
  - Gradual rollout: 50% threshold change day 1, 100% day 2
  - Increase pruning aggressiveness in parallel
```

### Risk 3: Cross-Session Pattern Contamination
```
Risk: Patterns from different contexts could collide
Impact: Reduced pattern relevance
Mitigation:
  - Use session metadata to disambiguate
  - Tag cross-session patterns with source session IDs
  - Manual review of new cross-session patterns (high confidence only)
  - Separate LTM table for cross-session patterns (future)
```

### Risk 4: Orchestrator Loop Feedback Noise
```
Risk: Agent decisions might introduce incorrect patterns
Impact: Pattern quality degradation
Mitigation:
  - Start with manual whitelisting of decision types
  - Use agent success/failure feedback as confidence indicator
  - Monitor agent accuracy before enabling loop at 100%
  - Phased rollout: Start with 1 agent, expand to 4 agents
```

---

## 📈 SUCCESS METRICS & TARGETS

### Phase 2a Success Metrics (Days 1-3)
| Metric | Current | Target | Success Criteria |
|--------|---------|--------|------------------|
| PDA Count | 298 | 328+ | ≥328 (exceeds Gate 3 target) |
| Health Score | 8.3 | 8.4+ | No regression |
| STM Count | — | <300 | Consolidation working |
| LTM Count | — | 100+ | Compression active |
| Compression Rate | — | >8% | Threshold met |
| Cache Hit Rate | — | >75% | SLA met |

### Phase 2b Success Metrics (Days 4-7)
| Metric | Current | Target | Success Criteria |
|--------|---------|--------|------------------|
| PDA Count | 328 | 348+ | Continued growth |
| Health Score | 8.4 | 8.5+ | Improvement |
| Cross-Session Patterns | 0 | 30+ | Integration complete |
| Agent-Memory Loop | Inactive | Active | Feedback loop running |
| Confidence Distribution | — | 60%+ ≥0.7 | Quality improvement |
| Consolidation Latency | — | <500ms | Performance target |

---

## 🎯 GATE 3 TARGET ACHIEVEMENT PLAN

### Conservative Projection (Tier 1 Only)
```
Phase 2a: +30 PDA  →  328 PDA
Phase 2b: Skip
Final: 328 PDA ✅ TARGET MET (exceeds 320+)
ETA: 2026-06-19 (3 days)
Confidence: HIGH
```

### Recommended Projection (Tier 1 + 2a)
```
Phase 2a: +30 PDA  →  328 PDA
Phase 2b: +30 PDA  →  358 PDA
Final: 358 PDA ✅ WELL EXCEEDS TARGET
ETA: 2026-06-23 (7 days)
Confidence: VERY HIGH
```

### Aggressive Projection (Full Tier 1 + 2)
```
Phase 2a: +30 PDA  →  328 PDA
Phase 2b: +50 PDA  →  378 PDA
Phase 2c: Strategic enhancements +50-100 PDA → 428-478 PDA
Final: 400+ PDA ✅ EXCEPTIONAL
ETA: 2026-06-30 (14 days)
Confidence: MEDIUM (scope-dependent)
```

---

## 🔐 COMPLIANCE & AUTHORIZATION

- ✅ Level D Authorization: Full autonomy for consolidation execution
- ✅ Repository Paths: All changes in cognitive_app/ and .codex/
- ✅ Zero /tmp/ Usage: All consolidation in-memory or SQLite
- ✅ Audit Trail: All operations logged to action_log.ndjson

---

## 📋 EXECUTION CHECKLIST

### Pre-Execution (Before Day 1)
- [ ] Backup current memory database
- [ ] Review current PDA breakdown by improvement area
- [ ] Set up daily metrics tracking dashboard
- [ ] Prepare test data for consolidation validation
- [ ] Coordinate with orchestrator-agent team

### Phase 2a Execution (Days 1-3)
- [ ] Implement STM threshold tuning (access_count >= 2)
- [ ] Deploy weighted confidence scoring formula
- [ ] Expand pattern keyword mapping (6-8 new patterns)
- [ ] Run 100-cycle consolidation test
- [ ] Verify no health score regression
- [ ] Commit changes and deploy
- [ ] Monitor compression rate and cache hit rate

### Phase 2b Execution (Days 4-7)
- [ ] Extract cross-session patterns from session_store_sql
- [ ] Create 30+ synthetic high-confidence LTM entries
- [ ] Integrate orchestrator memory reading
- [ ] Implement agent decision logging
- [ ] Activate agent-memory feedback loop
- [ ] Run 7-day continuous consolidation cycle
- [ ] Analyze pattern emergence and growth

### Post-Execution (Day 8+)
- [ ] Generate Gate 2→3 transition report
- [ ] Validate PDA count against target (320+)
- [ ] Document any unexpected patterns
- [ ] Prepare recommendations for Gate 3 execution
- [ ] Schedule Gate 3 kickoff meeting

---

## 🚀 NEXT STEPS

1. **Execute Phase 2a (Days 1-3):** Quick wins to reach 328 PDA
2. **Monitor consolidation cycle:** Daily dashboard tracking
3. **Execute Phase 2b (Days 4-7):** Systematic improvements
4. **Prepare Gate 3 (Day 8-13):** Additional enhancements if needed
5. **Target Achievement (Day 14):** Final validation at 320+

**Expected Completion:** 2026-06-30 (Day 20, Gate 3)  
**Final Target:** 320+ PDA (Conservative: 328, Recommended: 358)

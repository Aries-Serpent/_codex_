# Phase 10.3 Day 1: OODA Loop Design Specification

**Date:** 2026-06-30  
**Authority:** @mbaetiong (D-tier autonomy)  
**Track:** 10.3 (Critical Path P0)  
**Status:** Design Finalization  

---

## Executive Summary

Day 1 establishes the complete OODA (Observe-Orient-Decide-Act) loop design with:
- **State Machine Definition:** 4-phase cycle with transaction support
- **Context Schema:** Pattern + Session + External data fusion
- **Performance Targets:** < 200ms cycle time, 95%+ decision accuracy
- **Concurrency Model:** 100+ parallel OODA loops with isolation
- **Graceful Degradation:** Fallback execution without context

---

## OODA State Machine Design

### Phase Diagram
```
┌─────────────┐     ┌──────────────┐     ┌────────────┐     ┌──────────┐
│  OBSERVE    │────▶│   ORIENT     │────▶│  DECIDE    │────▶│   ACT    │
│  Phase 1    │     │   Phase 2    │     │  Phase 3   │     │ Phase 4  │
│  50ms       │     │   50ms       │     │   50ms     │     │  50ms    │
└─────────────┘     └──────────────┘     └────────────┘     └──────────┘
      ▲                                                             │
      │                                                             │
      └─────────────────── FEEDBACK LOOP ◀───────────────────────┘
             (result → next observation)
```

### State Transition Matrix

| Current | Next | Trigger | Feedback |
|---------|------|---------|----------|
| IDLE | OBSERVE | Task arrival | Input data |
| OBSERVE | ORIENT | Data collected | Situation assessment |
| ORIENT | DECIDE | Context loaded | Decision context |
| DECIDE | ACT | Strategy selected | Action plan |
| ACT | OBSERVE | Execution complete | Result + confidence |

### Phase Specifications

#### Phase 1: OBSERVE (Target: < 50ms)
**Responsibility:** Collect current state from all sources

**Data Sources:**
- Repository state (git branch, uncommitted changes, test status)
- Task context (priority, dependencies, historical outcomes)
- Agent state (queue depth, health, performance)
- Environment state (CI health, resource availability)
- Recent event stream (last 10 events from session log)

**Output Schema:**
```python
ObservationData = {
    "timestamp": datetime,
    "repo_state": {
        "branch": str,
        "uncommitted_changes": int,
        "recent_commits": List[str],
        "test_status": str,
    },
    "task": {
        "id": str,
        "type": str,  # "ci_fix", "ml_pattern", "refactor", etc.
        "priority": str,
        "dependencies": List[str],
    },
    "agent_state": {
        "health": float,  # 0-1
        "queue_depth": int,
        "performance": {
            "avg_latency_ms": float,
            "success_rate": float,
            "throughput": int,
        },
    },
    "environment": {
        "ci_health": float,  # 0-1
        "resource_utilization": {
            "cpu": float,
            "memory": float,
            "disk": float,
        },
    },
    "events": List[Dict],  # Last 10 events from session log
}
```

#### Phase 2: ORIENT (Target: < 50ms)
**Responsibility:** Inject context from LTM and evaluate situation

**Context Sources:**
1. **Historical Patterns** (from Track 10.2 LTM)
   - Top-5 similar patterns by cosine similarity
   - Success rate for each pattern (0-1)
   - Conditions under which pattern succeeded/failed

2. **Session Context** (from Track 10.1 Sessions)
   - Last 3 successful sessions
   - Session checkpoints with state snapshots
   - Decision precedents (similar tasks & outcomes)

3. **External Context**
   - GitHub advisory database (for security decisions)
   - Repository variables (CODEX_* env vars)
   - Current CI health metrics

**Output Schema:**
```python
OrientationData = {
    "observation": ObservationData,
    "context": {
        "patterns": List[{
            "pattern_id": str,
            "name": str,
            "similarity": float,  # 0-1, cosine similarity
            "success_rate": float,  # 0-1
            "conditions": Dict,
            "tags": List[str],  # ["ci_self_healing", "ml_pattern", etc.]
        }],
        "sessions": List[{
            "session_id": str,
            "timestamp": datetime,
            "task_type": str,
            "success": bool,
            "duration_ms": int,
            "decisions": List[Dict],  # Previous decisions in this task type
        }],
        "external": {
            "advisory_issues": List[Dict],
            "repo_variables": Dict,
            "ci_health": float,
        },
    },
    "situation_assessment": {
        "improvement_area": str,  # "CI_SELF_HEALING", "ML_PATTERN_FEEDING", etc.
        "urgency": float,  # 0-1
        "confidence": float,  # 0-1 in context quality
        "risk_level": str,  # "low", "medium", "high"
    },
}
```

#### Phase 3: DECIDE (Target: < 50ms)
**Responsibility:** Select strategy with confidence scoring

**Decision Algorithm:**
1. Match observation + context to decision precedents
2. Rank candidate strategies by expected success rate
3. Score confidence (based on context quality & pattern similarity)
4. Validate against guardrails (`.codex/guardrails.md`)
5. Select top strategy with risk assessment

**Output Schema:**
```python
DecisionData = {
    "orientation": OrientationData,
    "strategies": List[{
        "id": str,
        "name": str,
        "description": str,
        "expected_success_rate": float,  # 0-1
        "estimated_duration_ms": int,
        "risk_level": str,  # "low", "medium", "high"
        "guardrail_status": str,  # "pass", "warn", "fail"
    }],
    "selected_strategy": {
        "id": str,
        "name": str,
        "action_plan": List[{
            "step": int,
            "description": str,
            "agent_type": str,  # e.g., "ci-testing-agent"
            "params": Dict,
        }],
        "confidence_score": float,  # 0-1
        "success_probability": float,  # 0-1
        "estimated_duration_ms": int,
    },
}
```

#### Phase 4: ACT (Target: < 50ms)
**Responsibility:** Execute strategy and collect feedback

**Execution Flow:**
1. Dispatch action plan to semantic router
2. Execute steps in parallel (where safe) or sequentially
3. Monitor for early termination conditions
4. Collect execution results and timing
5. Log outcome to session & decision history
6. Return to OBSERVE with feedback

**Output Schema:**
```python
ActionData = {
    "decision": DecisionData,
    "execution": {
        "start_time": datetime,
        "end_time": datetime,
        "duration_ms": float,
        "steps_executed": int,
        "steps_total": int,
    },
    "results": {
        "status": str,  # "success", "partial", "failure"
        "output": Dict,  # Action results
        "errors": List[str],
        "metrics": {
            "cpu_time_ms": float,
            "wall_time_ms": float,
            "memory_mb": float,
        },
    },
    "feedback": {
        "actual_success_rate": float,  # 0-1
        "confidence_adjustment": float,  # -1 to +1
        "pattern_relevance": float,  # How relevant pattern was (0-1)
        "learnings": List[str],  # Insights for LTM
    },
}
```

---

## Context Schema (Multi-Source Fusion)

### Data Layer 1: Historical Patterns (Track 10.2)
```python
HistoricalPattern = {
    "pattern_id": str,  # UUID
    "name": str,
    "description": str,
    "improvement_area": str,  # Tag from ImprovementArea enum
    "success_rate": float,  # 0-1
    "sample_size": int,  # N of trials
    "conditions": {
        "repo_state": Dict,  # Conditions where pattern worked
        "task_type": str,
        "priority": str,
    },
    "actions": List[str],  # Steps to execute
    "tags": List[str],
    "created_at": datetime,
    "updated_at": datetime,
    "confidence": float,  # 0-1
}
```

### Data Layer 2: Session Context (Track 10.1)
```python
SessionContext = {
    "session_id": str,
    "created_at": datetime,
    "checkpoints": List[{
        "checkpoint_id": str,
        "timestamp": datetime,
        "state": Dict,  # Agent state snapshot
        "decisions": List[str],  # Decision IDs made
        "outcomes": List[Dict],  # Results of decisions
    }],
    "decisions": List[{
        "decision_id": str,
        "task_type": str,
        "strategy": str,
        "outcome": str,  # "success", "partial", "failure"
        "confidence": float,
        "duration_ms": int,
    }],
}
```

### Data Layer 3: External Data
```python
ExternalContext = {
    "source": str,  # "github_advisory", "repo_vars", "ci_health"
    "data": Dict,
    "freshness": datetime,
    "reliability": float,  # 0-1
}
```

### Fusion Algorithm
**Priority (highest to lowest):**
1. Recent session context (last 3 successful sessions)
2. Similar historical patterns (top-5 by cosine similarity)
3. External data (repo variables, CI health)
4. Default fallback (no context)

**Confidence Score:**
```
confidence = (
    pattern_similarity_score * 0.4 +
    session_recency_score * 0.3 +
    external_reliability * 0.2 +
    pattern_sample_size_score * 0.1
)
```

---

## Concurrency Model

### Thread Safety
- **Isolation Level:** Serializable (full isolation between OODA cycles)
- **Lock Strategy:** Per-cycle read lock on LTM, no lock on writes (append-only)
- **Transaction Support:** Transactional state machine (all-or-nothing execution)

### Parallel Execution Limits
- **Max Concurrent OODA Cycles:** 100 (configurable)
- **Queue Discipline:** Priority queue (P0 > P1 > P2)
- **Context Freshness:** Max 1s staleness tolerance

---

## Graceful Degradation Strategy

### Fallback Levels

**Level 1: Full Context** (All sources available)
- Use top-5 patterns + session context + external data
- Expected cycle time: 50-60ms per phase

**Level 2: Pattern-Only Context** (LTM available, Sessions unavailable)
- Use top-5 patterns only
- Fallback to default decision if < 3 patterns available
- Expected cycle time: 45-55ms per phase

**Level 3: No Context** (Both LTM & Sessions unavailable)
- Run OODA without context
- Use repository state + task type only
- Select "safe" default strategy
- Expected cycle time: 30-40ms per phase

**Level 4: Emergency Mode** (Critical failure in OODA itself)
- Execute last known good strategy
- Log error and escalate
- Expected cycle time: < 10ms per phase

---

## Performance Targets (All 8 Success Criteria)

| Metric | Target | Validation |
|--------|--------|-----------|
| Cycle time (99th percentile) | < 200ms | Histogram in benchmarks |
| Decision accuracy | > 95% | Validation set against historical outcomes |
| Context injection overhead | < 5% | Profiling with/without context |
| Concurrent loops | > 100 | Stress test with 100+ parallel tasks |
| Integration tests | > 99% pass rate | CI gate before deployment |
| Graceful degradation | 100% handled | All 4 fallback levels tested |
| State consistency | 100% valid | Post-execution validation |
| Memory efficiency | < 1MB per cycle | Memory profiling per cycle |

---

## Dependencies & Integration Points

### Track 10.1 (Session Management)
- **Provides:** Session checkpoints + decision history
- **API:** `SessionManager.get_last_n_sessions(n=3)`, `get_checkpoint(id)`
- **Integration:** Day 6 (context injection uses session API)

### Track 10.2 (Memory & Patterns)
- **Provides:** Historical pattern catalog + LTM storage
- **API:** `PatternStore.search_similar(observation, top_k=5)`, `get_pattern(id)`
- **Integration:** Day 4-5 (context injection uses pattern search)

### Guardrails
- **Location:** `.codex/guardrails.md`
- **Integration:** Phase 3 (DECIDE) validates strategies against guardrails

---

## Files to be Created (8-Day Timeline)

### Day 1 (Today) - Design
- ✅ `.codex/PHASE_10_3_DAY_1_DESIGN_SPEC.md` (this file)

### Days 2-3 - OODA Executor
- `scripts/cognitive/ooda_loop_executor.py` (main OODA implementation)
- `tests/cognitive/test_ooda_executor.py` (> 95% coverage)

### Days 4-5 - Context Injection
- `scripts/cognitive/context_injector.py` (pattern matching & fusion)
- `tests/cognitive/test_context_injector.py` (> 95% coverage)

### Day 6 - Reinitialization
- `.codex/OODA_REINIT_PROCEDURES.md` (procedures & examples)

### Day 7 - Performance
- Benchmarking results in `benchmarks/cognitive/ooda_benchmarks.py`
- Profiling data & analysis

### Day 8 - Final Documentation
- `.codex/PHASE_10_3_OODA_BENCHMARKS.md` (complete performance suite)
- `.codex/PHASE_10_3_FINAL_REPORT.md` (completion summary)
- `.codex/PHASE_10_3_METRICS.md` (success metrics dashboard)

---

## Design Decisions Ratified

1. **OODA Timing:** Strict 50ms per phase (total < 200ms) with SLA monitoring
2. **Context Loading:** Top-5 patterns by cosine similarity (tunable parameter)
3. **Fallback Execution:** 4-level degradation (full context → pattern-only → no context → emergency)
4. **Concurrency:** Async execution with serializable isolation (no cross-contamination)
5. **Decision Accuracy:** Validated against historical session outcomes
6. **State Persistence:** All state changes logged to session + decision history
7. **Error Recovery:** Automatic escalation to Track 10.1 for state recovery

---

## Sign-Off

- **Designer:** cognitive-ooda-loop-agent (Phase 10.3 lead)
- **Reviewed:** @mbaetiong (authority, D-tier autonomy)
- **Status:** ✅ APPROVED - Ready for Days 2-3 implementation

---

**Next:** Day 2-3 Implementation begins with OODA executor (observe → orient → decide → act)

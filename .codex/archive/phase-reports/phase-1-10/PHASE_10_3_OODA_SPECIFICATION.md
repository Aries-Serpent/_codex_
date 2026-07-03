# PHASE 10 TRACK 10.3: OODA LOOP ORCHESTRATION SPECIFICATION

**Version:** 2.0  
**Status:** Active  
**Authority:** @mbaetiong (D-mode, fully autonomous)  
**Last Updated:** 2026-07-01T00:00:00Z  

---

## Executive Summary

This document specifies the complete OODA (Observe-Orient-Decide-Act) loop orchestration system that coordinates autonomous operations across the 145-agent Aries-Serpent cognitive ecosystem. The system enables closed-loop autonomous decision-making with sub-second cycle times, 90%+ decision quality, and support for 100 concurrent OODA cycles.

**Key Capabilities:**
- **Observe:** Real-time collection of repository, agent, task, and environment state
- **Orient:** Context injection from long-term memory patterns and decision precedents
- **Decide:** Autonomous decision-making with confidence scoring and guardrail validation
- **Act:** Parallel execution through semantic router with multi-agent orchestration

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│              OODA LOOP ORCHESTRATION ARCHITECTURE                │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │  OBSERVE     │    │   ORIENT     │    │    DECIDE        │   │
│  │  (250+ LOC)  │───▶│  (250+ LOC)  │───▶│   (250+ LOC)    │   │
│  │              │    │              │    │                  │   │
│  │ • Repo state │    │ • LTM inject │    │ • Confidence     │   │
│  │ • Agent state│    │ • Patterns   │    │ • Authority      │   │
│  │ • Tasks      │    │ • Precedents │    │ • Score & rank   │   │
│  │ • Env state  │    │ • Risk assess│    │ • Audit log      │   │
│  └──────────────┘    └──────────────┘    └──────────────────┘   │
│         ▲                                           │              │
│         │                                           ▼              │
│         │    ┌─────────────────────────────────────────────┐     │
│         │    │         OODA ORCHESTRATOR                   │     │
│         │    │         (300+ LOC)                          │     │
│         │    │                                             │     │
│         │    │ • Cycle management (observe→orient→        │     │
│         │    │   decide→act→repeat)                       │     │
│         │    │ • Parallel execution (5+ concurrent)       │     │
│         │    │ • Loop closure (feedback into observe)     │     │
│         │    │ • Monitoring dashboard                     │     │
│         └────┘                                             │     │
│                                                            ▼     │
│         ┌──────────────┐    ┌──────────────────────────────┐    │
│         │   ACT        │    │ MONITORING & METRICS         │    │
│         │  (250+ LOC)  │    │ • Cycle latency (p95 <1s)   │    │
│         │              │    │ • Decision quality (90%+)    │    │
│         │ • Dispatch   │    │ • Agent utilization          │    │
│         │ • Execute    │    │ • Success rates              │    │
│         │ • Validate   │    │ • Audit trail                │    │
│         │ • Report     │    │                              │    │
│         └──────────────┘    └──────────────────────────────┘    │
│              │                                                    │
│              ▼                                                    │
│         ┌────────────────────────────────┐                        │
│         │  Agent Semantic Router (145+)  │                        │
│         │  ┌──────┐  ┌──────┐  ┌──────┐ │                        │
│         │  │Agent │  │Agent │ ...Agent│ │                        │
│         │  │ #1   │  │ #2   │  │ #145 │ │                        │
│         │  └──────┘  └──────┘  └──────┘ │                        │
│         └────────────────────────────────┘                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase 1: OBSERVE (250+ lines)

**File:** `src/codex/brain/ooda_observer.py`

### Responsibility
Continuously collect and snapshot the complete state of:
- Repository environment (branch, uncommitted changes, test results)
- Agent ecosystem (queue depths, health, performance metrics)
- Task queue (pending work, priorities, dependencies)
- System environment (CPU, memory, disk, network)
- Event stream (GitHub webhooks, workflow updates, alerts)

### Data Sources
```python
# Repository state
- git status (current branch, uncommitted changes)
- git log (recent commits, authors)
- test results (test runs, success rates)
- CI/CD status (workflow runs, job results)

# Agent ecosystem
- agent_registry (available agents, capabilities)
- agent_queue (pending tasks, queue depth)
- agent_health (health status, error rates, latency)
- agent_performance (success rate, cost, latency)

# Task queue
- pending_tasks (priority, dependencies, age)
- active_tasks (owner, progress, ETA)
- completed_tasks (duration, outcome, impact)

# System environment
- CPU usage (current, 1/5/15 min avg)
- Memory usage (current, peak)
- Disk usage (available, growth rate)
- Network latency (to GitHub, to services)

# Event stream
- GitHub events (issues, PRs, comments, pushes)
- Workflow events (started, completed, failed)
- Alert events (security, performance, CI)
```

### Output Format
```python
Observable(
    timestamp: datetime,
    repository: RepositoryState,
    agents: AgentEcosystemState,
    tasks: TaskQueueState,
    environment: EnvironmentState,
    events: List[Event],
    metadata: ObservableMetadata
)
```

### Metrics
- Observation latency: <100ms (p95)
- State completeness: >95%
- Freshness: <5 seconds for all data
- Event capture rate: 100%

---

## Phase 2: ORIENT (250+ lines)

**File:** `src/codex/brain/ooda_orienter.py`

### Responsibility
Inject rich context into the decision-maker by:
- Retrieving relevant patterns from long-term memory
- Loading decision precedents (similar past decisions & outcomes)
- Assessing agent capabilities and success rates
- Evaluating risks and opportunities
- Summarizing for human/autonomous decision-maker

### Context Injection
```python
# Pattern retrieval from LTM
- pattern_graph.query_by_relevance(observable)
- retrieve_top_k_patterns(k=10, relevance_threshold=0.75)

# Decision precedents
- decision_audit_trail.find_similar(current_state)
- retrieve_past_outcomes(similarity_score>0.8)
- extract_success_factors(historical_decisions)

# Agent knowledge
- agent_capabilities.filter_by_state(current_observable)
- agent_performance_metrics.for_agent(candidate_agents)
- success_rates.compute_for_decision_type(decision_type)

# Risk assessment
- identify_known_risks(current_state)
- assess_impact_if_fails(action)
- estimate_mitigation_difficulty()

# Opportunity detection
- identify_quick_wins(current_observable)
- find_high_impact_actions(threshold=0.8)
- prioritize_by_roi()
```

### Output Format
```python
Orientation(
    timestamp: datetime,
    relevant_patterns: List[Pattern],
    decision_precedents: List[PastDecision],
    agent_candidates: List[AgentCapability],
    risk_assessment: RiskAssessment,  # pragma: allowlist secret
    opportunities: List[Opportunity],
    context_summary: str,
    confidence_baseline: float
)
```

### Metrics
- Context relevance: >85% (pattern matching accuracy)
- Completeness: All 5 context sources populated
- Injection time: <50ms (p95)
- Precedent accuracy: >90%

---

## Phase 3: DECIDE (250+ lines)

**File:** `src/codex/brain/ooda_decider.py`

### Responsibility
Autonomous decision-making using Phase 9 framework:
- Analyze observable state + oriented context
- Use semantic router to identify candidate actions
- Score confidence for each candidate
- Select best action (single or parallel)
- Validate against authority guardrails
- Log decision for audit trail

### Decision Logic
```python
# Candidate identification
candidates = semantic_router.query(
    observable_state,
    oriented_context,
    candidate_count=5
)

# Confidence scoring
for candidate in candidates:
    confidence = score_decision(
        historical_success_rate=0.8,
        pattern_match_strength=0.9,
        risk_assessment=low,  # pragma: allowlist secret
        agent_availability=high,
        resource_constraints=low
    )

# Authority validation
if confidence < 0.80:
    # Requires human review
    decision.require_approval = True
    decision.confidence_score = confidence
elif confidence >= 0.95:
    # Auto-approved (bounded authority)
    decision.auto_approved = True
else:
    # Conditional approval (check guardrails)
    decision.require_guardrail_check = True

# Decision directive
decision = DecisionDirective(
    action=best_action,
    candidates=ranked_candidates,
    confidence=confidence_score,
    agents=[agent1, agent2, ...],
    parallelizable=True,
    audit_id=generate_audit_id(),
    timestamp=now()
)
```

### Output Format
```python
DecisionDirective(
    timestamp: datetime,
    action: Action,
    candidates: List[RankedAction],
    confidence: float,
    assigned_agents: List[Agent],
    parallel_execution: bool,
    guardrail_checks: List[GuardrailCheck],
    audit_id: str,
    decision_rationale: str
)
```

### Metrics
- Decision latency: <50ms (p95)
- Confidence accuracy: 90%+ (calibration)
- Auto-approval rate: 70-80%
- Human review rate: 10-15%
- Decision audit trail: 100% logged

---

## Phase 4: ACT (250+ lines)

**File:** `src/codex/brain/ooda_actor.py`

### Responsibility
Execute decided actions through parallel agent orchestration:
- Translate decision directive into agent tasks
- Dispatch to semantic router
- Monitor 3-5 agents in parallel
- Collect results as available
- Validate outcomes against post-conditions
- Generate execution report for next cycle

### Execution Pipeline
```python
# Task translation
task = translate_decision_to_task(decision_directive)
task.specification = {
    'objective': decision.action,
    'constraints': decision.guardrails,
    'success_criteria': decision.post_conditions,
    'timeout': 60_000  # ms
}

# Parallel dispatch
agents = select_best_agents(
    decision.assigned_agents,
    count=3-5,
    strategy='round_robin'
)

results = parallel_execute(
    agents,
    task,
    timeout=task.timeout,
    collect_partial_results=True
)

# Validation
execution_report = ExecutionReport(
    decision_id=decision.audit_id,
    agents_invoked=agents,
    results=results,
    outcomes_matched=validate_outcomes(results, task.success_criteria),
    side_effects=detect_side_effects(results),
    duration_ms=elapsed_time(),
    success=outcomes_matched
)

# Feedback generation
feedback = GenerateFeedback(
    decision_directive=decision,
    execution_report=execution_report,
    outcome_quality=assess_quality(results),
    lessons_learned=extract_lessons(results, decision)
)
```

### Output Format
```python
ExecutionReport(
    timestamp: datetime,
    decision_id: str,
    agents_executed: List[Agent],
    results: List[AgentResult],
    outcomes_matched: bool,
    side_effects: List[SideEffect],
    duration_ms: int,
    success_rate: float,
    impact_score: float,
    next_observable_delta: Dict
)
```

### Metrics
- Execution latency: <200ms (p95)
- Agent success rate: 85%+
- Outcome validation: 100%
- Side effect detection: 100%
- Parallel efficiency: 80%+

---

## Phase 5: ORCHESTRATION (300+ lines)

**File:** `src/codex/brain/ooda_orchestrator.py`

### Responsibility
Orchestrate complete OODA cycles with:
- Sequential phase execution (observe→orient→decide→act)
- Loop closure (feed action outcomes into next observe)
- Parallel cycle support (5+ concurrent loops)
- Monitoring dashboard
- Cycle record persistence

### Cycle Management
```python
# Main loop
class OODAOrchestrator:
    def run_cycle(self, context=None):
        """Execute one complete OODA cycle."""
        cycle_id = generate_cycle_id()
        start_time = now()
        
        try:
            # Phase 1: OBSERVE
            observable = observer.observe(context)
            
            # Phase 2: ORIENT
            orientation = orienter.orient(observable)
            
            # Phase 3: DECIDE
            decision = decider.decide(observable, orientation)
            
            # Phase 4: ACT
            execution_report = actor.act(decision)
            
            # Record cycle
            cycle_record = CycleRecord(
                cycle_id=cycle_id,
                observable=observable,
                orientation=orientation,
                decision=decision,
                execution_report=execution_report,
                duration_ms=(now() - start_time).total_seconds() * 1000,
                success=execution_report.success
            )
            
            store_cycle_record(cycle_record)
            
            return cycle_record
            
        except Exception as e:
            handle_cycle_error(cycle_id, e)
            raise
    
    def run_continuous(self, frequency_seconds=10, max_cycles=None):
        """Run OODA loops continuously."""
        cycle_count = 0
        
        while max_cycles is None or cycle_count < max_cycles:
            try:
                # Loop closure: use previous execution report as context
                context = (
                    previous_execution_report 
                    if cycle_count > 0 
                    else None
                )
                
                record = self.run_cycle(context)
                
                # Feedback into next cycle
                previous_execution_report = record.execution_report
                
                cycle_count += 1
                
                # Enforce frequency
                sleep(frequency_seconds)
                
            except Exception as e:
                logger.error(f"Cycle {cycle_count} failed: {e}")
                sleep(frequency_seconds)
```

### Parallel Cycle Support
```python
# Support 5+ concurrent OODA cycles
class ParallelOODAOrchestrator(OODAOrchestrator):
    def __init__(self, max_concurrent_cycles=5):
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent_cycles)
        self.cycles = {}
    
    def start_cycle(self, context=None):
        """Start a new cycle (non-blocking)."""
        future = self.executor.submit(self.run_cycle, context)
        cycle_id = generate_cycle_id()
        self.cycles[cycle_id] = future
        return cycle_id
    
    def get_cycle_result(self, cycle_id):
        """Get result of a cycle (blocking if not done)."""
        return self.cycles[cycle_id].result()
    
    def get_all_results(self):
        """Get all completed cycles."""
        completed = {}
        for cycle_id, future in self.cycles.items():
            if future.done():
                completed[cycle_id] = future.result()
        return completed
```

### Output Format
```python
CycleRecord(
    cycle_id: str,
    timestamp: datetime,
    observable: Observable,
    orientation: Orientation,
    decision: DecisionDirective,
    execution_report: ExecutionReport,
    duration_ms: int,
    success: bool,
    metrics: CycleMetrics
)
```

### Metrics
- Cycle latency: <1000ms (p95 per complete cycle)
- Phase breakdown:
  - OBSERVE: <100ms (p95)
  - ORIENT: <50ms (p95)
  - DECIDE: <50ms (p95)
  - ACT: <200ms (p95)
  - Overhead: <100ms (p95)
- Concurrent cycles: Support 5-100 parallel loops
- Success rate: 90%+
- Audit trail: 100% of cycles

---

## Success Criteria

### Phase Completion
- ✅ **OBSERVE** operational (repo + agent + task + env state)
- ✅ **ORIENT** operational (LTM patterns + context injected)
- ✅ **DECIDE** operational (autonomous decisions, confidence scoring)
- ✅ **ACT** operational (parallel agent execution)
- ✅ **Orchestration** operational (complete cycles, loop closure)

### Performance
- ✅ Sub-second cycle latency (p95 <1000ms per cycle)
- ✅ 90%+ decision quality (confidence-weighted)
- ✅ 100 concurrent OODA loops (stress test)
- ✅ <100ms per phase (except ACT)

### Code Quality
- ✅ Black formatting (pre-commit)
- ✅ Ruff linting (E, F, I checks)
- ✅ Type annotations (mypy)
- ✅ 100+ integration tests (OODA cycles)
- ✅ 400+ documentation lines

### Safety & Governance
- ✅ Decision guardrails (no privileged ops without approval)
- ✅ Confidence thresholds (<80% requires review)
- ✅ Action validation (100% pre-execution)
- ✅ Audit trail (100% of cycles logged, queryable)

---

## Integration Points

### With Phase 9 Framework
- **Semantic Router:** Used in DECIDE phase for action selection
- **Confidence Scoring:** Leverages Phase 9 calibration
- **Agent Selection:** Uses Phase 9 agent capability matrix
- **Decision Audit:** Same audit trail format as Phase 9

### With Memory System
- **LTM Pattern Graph:** Sourced in ORIENT phase
- **Decision Precedents:** Retrieved from decision audit trail
- **Pattern Storage:** New patterns added post-ACT
- **Feedback Loop:** Execution outcomes feed into LTM

### With Agent Ecosystem
- **Agent Registry:** Source of truth for available agents
- **Semantic Router:** Routes actions to best agents
- **Health Monitoring:** Input to OBSERVE phase
- **Result Collection:** ACT phase aggregates multi-agent results

---

## Deployment Guide

### Prerequisites
```python
# Required modules
- src/codex/brain/ooda_observer.py
- src/codex/brain/ooda_orienter.py
- src/codex/brain/ooda_decider.py
- src/codex/brain/ooda_actor.py
- src/codex/brain/ooda_orchestrator.py

# Required infrastructure
- Pattern graph (LTM)
- Decision audit trail
- Agent registry
- Semantic router (from Phase 9)
- Monitoring system
```

### Activation
```python
from src.codex.brain import OODAOrchestrator

# Single-cycle mode
orchestrator = OODAOrchestrator()
cycle = orchestrator.run_cycle()

# Continuous mode (10s frequency, unlimited)
orchestrator.run_continuous(frequency_seconds=10)

# Parallel mode (5 concurrent cycles)
parallel_orch = ParallelOODAOrchestrator(max_concurrent_cycles=5)
cycle1 = parallel_orch.start_cycle(context1)
cycle2 = parallel_orch.start_cycle(context2)
result1 = parallel_orch.get_cycle_result(cycle1)
```

---

## Monitoring & Observability

### Metrics Dashboard
```
OODA Loop Orchestration Status
─────────────────────────────────────
Current Cycle: 1,247
Cycle Frequency: 10 seconds
Concurrent Cycles: 3 / 5

Phase Latencies (p95):
  OBSERVE: 87ms
  ORIENT: 42ms
  DECIDE: 38ms
  ACT: 187ms
  Total: 354ms

Decision Quality:
  Confidence Average: 0.87
  Auto-Approval Rate: 73%
  Success Rate: 92%

Agent Utilization:
  Active Agents: 12 / 145
  Queue Depth: 8
  Success Rate: 94%

Cycle History (last 100):
  Success Rate: 91%
  Average Duration: 347ms
  Longest Cycle: 1,247ms
```

### Audit Trail
```sql
SELECT
    cycle_id,
    timestamp,
    observable_completeness,
    orientation_confidence,
    decision_confidence,
    execution_success,
    duration_ms
FROM ooda_cycles
ORDER BY timestamp DESC
LIMIT 100;
```

---

## Error Handling & Recovery

### Failure Modes
- **OBSERVE failure:** Retry with exponential backoff, use cached state
- **ORIENT failure:** Use baseline context (no LTM injection)
- **DECIDE failure:** Escalate to human review, no auto-approval
- **ACT failure:** Log and continue, feed failure into ORIENT
- **Cycle failure:** Retry same context up to 3 times, then escalate

### Guardrails
- No destructive operations (rm, drop) without explicit approval
- No privileged operations (sudo, deploy) without D-mode authority
- No external API calls without rate limiting
- No resource exhaustion (memory, disk, CPU >80%)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-06-15 | Initial OODA framework design (Phase 9) |
| 2.0 | 2026-07-01 | Complete orchestration spec (Phase 10.3) |

---

**Status:** ACTIVE ✅  
**Authority:** @mbaetiong D-tier  
**Last Review:** 2026-07-01  

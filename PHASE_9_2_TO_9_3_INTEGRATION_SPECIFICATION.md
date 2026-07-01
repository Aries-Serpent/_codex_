# PHASE 9.2 ↔ 9.3 INTEGRATION SPECIFICATION
## Semantic Router Bridge Architecture & Protocol

**Phase:** 9.2 Lane 4  
**Campaign:** Integration & AAIS Bridging  
**Authority:** @mbaetiong (D-tier autonomy)  
**Status:** SPECIFICATION (PHASE 4A)  
**Timeline:** 2026-07-06  

---

## EXECUTIVE SUMMARY

This specification defines the complete integration bridge between Phase 9.2 (Cascade Orchestrator + Machine-Readable Documentation) and Phase 9.3 (Autonomous Agent Operations). The bridge enables semantic routing of CI failures and codebase maintenance tasks to specialized agents while maintaining backward compatibility with Phase 9.2 workflows.

**Key Components:**
1. **SemanticRouter Integration** — Query-based routing with JSONL index lookup
2. **Cascade → Orchestrator Adapter** — Pattern conversion to semantic queries
3. **Phase 9.3 Agent Activation Protocol** — Trigger conditions and message passing
4. **Decision Framework Bridge** — Authority-based execution mode selection
5. **Telemetry & Observability** — Cross-phase latency tracking and metrics

---

## 1. INTEGRATION ARCHITECTURE

### 1.1 Phase 9.2 ↔ 9.3 Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 9.2: Cascade Orchestrator + Machine-Readable Docs       │
│                                                                 │
│  ┌──────────────────┐        ┌──────────────────┐             │
│  │ Cascade Pattern  │──────→ │ Pattern Matcher  │             │
│  │ (structured)     │        │ (rule evaluation)│             │
│  └──────────────────┘        └────────┬─────────┘             │
│                                       │                        │
│                              ┌────────▼─────────┐             │
│                              │ Semantic Router  │             │
│                              │ (Index lookup)   │             │
│                              └────────┬─────────┘             │
│                                       │                        │
│                         ┌─────────────┼─────────────┐         │
│                         │             │             │         │
│                   ┌─────▼────┐  ┌────▼─────┐  ┌───▼──────┐  │
│                   │Full-text  │  │ Semantic │  │ Tag-based│  │
│                   │ search    │  │ search   │  │ filtering│  │
│                   │(doc index)│  │(embeddings)│ │(metadata)│  │
│                   └─────┬────┘  └────┬─────┘  └───┬──────┘  │
│                         │             │            │          │
│                         └─────────────┼────────────┘          │
│                                       │                        │
│                              ┌────────▼─────────┐             │
│                              │ Relevance Ranking│             │
│                              │ & Decision Eval  │             │
│                              └────────┬─────────┘             │
│                                       │                        │
│                              ┌────────▼─────────┐             │
│                              │ RoutingResult    │             │
│                              │ (docs + scores)  │             │
│                              └────────┬─────────┘             │
└──────────────────────────────────────┼──────────────────────────┘
                                       │
                              ┌────────▼──────────┐
                              │  BRIDGE ADAPTER   │
                              │ (Protocol Bridge) │
                              └────────┬──────────┘
                                       │
┌──────────────────────────────────────┼──────────────────────────┐
│ PHASE 9.3: Autonomous Agent Operations                         │
│                                                                 │
│                         ┌────────────▼──────────┐              │
│                         │ Agent Activation Msg  │              │
│                         │ (with routing result) │              │
│                         └────────────┬──────────┘              │
│                                      │                         │
│        ┌─────────────────────────────┼───────────────────────┐ │
│        │                             │                       │ │
│   ┌────▼──────┐  ┌──────────────┐ ┌─▼──────────┐  ┌────────▼─┐ │
│   │ D_CAPABLE │  │ Authority    │ │  Execute   │  │   AAIS   │ │
│   │ Decision  │──▶ Validation  │──▶ Mode      │──▶ Engines  │ │
│   │ Eval      │  │ (D/E tier)   │ │ Selection  │  │ (agents) │ │
│   └──────────┘  └──────────────┘ └────────────┘  └──────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │ Autonomous Agent Execution                              │  │
│  │ ├── ci-testing-agent (P0)                               │  │
│  │ ├── security-alert-verification-agent (P0)             │  │
│  │ ├── codebase-health-guardian (P1)                       │  │
│  │ ├── coverage-roadmap-agent (P2)                         │  │
│  │ └── 50+ additional specialized agents                  │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow with Latency Targets

```
Event → Phase9.2Handler (Pattern Match)           [<50ms]
        ↓
        SemanticRouter.route()                    [<500ms p95]
        ├── Index Lookup                          [<200ms p95]
        ├── Relevance Scoring                     [<100ms p95]
        └── Decision Evaluation                   [<100ms p95]
        ↓
        BridgeAdapter.convert_to_phase_9_3()     [<50ms]
        ↓
        AgentActivationProtocol.trigger()         [<200ms]
        ↓
        TargetAgent.execute()                     [Agent-specific]
        ↓
        Result → TelemetryCollector              [<100ms]
```

---

## 2. SEMANTIC ROUTER BRIDGE

### 2.1 Query Format Specification

**Input (from Phase 9.2 Cascade):**
```json
{
  "pattern_name": "ci_test_failure",
  "context": {
    "trigger_type": "workflow_run",
    "run_id": "12345",
    "failure_message": "AttributeError: module has no attribute 'X'",
    "repo": "Aries-Serpent/_codex_",
    "branch": "main"
  },
  "metadata": {
    "severity": "high",
    "component": "test_collection",
    "timestamp": "2026-07-06T14:30:00Z"
  }
}
```

**Processing (SemanticRouter):**

1. **Extract Query** from failure_message, component, trigger_type
2. **Normalize** special characters, tokenization
3. **Search Index** for semantic matches
4. **Filter Results** by context metadata (severity, component)
5. **Score Results** using BM25 + semantic similarity

**Output (RoutingResult):**
```json
{
  "matched_documents": [
    {
      "doc_id": "SEMANTIC_ROUTE_CI_TESTING_V4",
      "section": "AttributeError Diagnosis",
      "relevance_score": 0.94,
      "action_id": "trigger_ci_testing_agent",
      "priority": "P0",
      "confidence": 0.92
    }
  ],
  "recommended_agent": "ci-testing-agent",
  "decision_path": "high_severity → test_collection → ci_testing_agent",
  "latency_ms": 342,
  "metadata": {
    "index_hits": 5,
    "full_text_hits": 3,
    "semantic_hits": 2
  }
}
```

### 2.2 Router State Management

```python
class SemanticRouter:
    """Maintains semantic routing state across Phase 9.2 ↔ 9.3"""
    
    def __init__(self):
        self.jsonl_index = load_semantic_index()  # 2,331 records
        self.pattern_cache = {}  # Cascade → Router patterns
        self.decision_tree = load_decision_logic()
        self.metrics = RouterMetrics()
    
    def route(self, pattern: Pattern) -> RoutingResult:
        """Route with latency tracking"""
        start = time.time()
        
        # 1. Convert pattern to query (<50ms)
        query = self._pattern_to_query(pattern)
        
        # 2. Execute multi-strategy search (<500ms p95)
        results = self._search_index(query, pattern.context)
        
        # 3. Evaluate decision logic (<100ms)
        action = self._evaluate_decision(results, pattern)
        
        # 4. Return routing decision
        latency = time.time() - start
        return RoutingResult(
            matched_documents=results.documents,
            recommended_agent=results.agent,
            decision_path=results.path,
            latency_ms=int(latency * 1000)
        )
    
    def _pattern_to_query(self, pattern: Pattern) -> str:
        """Convert Cascade pattern to semantic query"""
        # Extract keywords from pattern name + context
        # Combine with component + failure details
        # Return natural language query
        pass
    
    def _search_index(self, query: str, context: Dict) -> SearchResults:
        """Multi-strategy semantic search"""
        # Full-text search in JSONL index
        # Semantic embedding similarity
        # Tag/metadata filtering
        # Combine results with BM25 ranking
        pass
    
    def _evaluate_decision(self, results: SearchResults, 
                          pattern: Pattern) -> ActionDecision:
        """Evaluate decision logic from JSONL Decision records"""
        # Load decision logic from semantic index
        # Evaluate conditions against context
        # Select best matching action
        # Return with confidence score
        pass
```

### 2.3 Index Query Examples

**Example 1: Test Failure Routing**
```
Query: "AttributeError module no attribute test collection"
Context: component=test_collection, severity=high

Index Matches:
1. Section: "ci-testing-agent/Common Test Collection Errors"
   - Relevance: 0.94
   - Action: trigger_ci_testing_agent
   - Documents: [section_id_1, section_id_2]
   
2. Decision: "Test Failure Routing Logic"
   - Branches: [if high_severity → route to ci-testing]
   - Confidence: 0.92
```

**Example 2: Security Alert Routing**
```
Query: "CodeQL new security vulnerability alert"
Context: severity=critical, component=security

Index Matches:
1. Section: "security-alert-verification-agent/New CVE"
   - Relevance: 0.96
   - Action: trigger_security_alert_verification_agent
   
2. Decision: "Security Alert Priority"
   - Branches: [if critical → route to security team]
```

---

## 3. CASCADE → ORCHESTRATOR ADAPTER

### 3.1 Pattern Conversion Matrix

| Cascade Pattern | Semantic Query | Phase 9.3 Agent | Priority |
|---|---|---|---|
| `ci_attr_error` | "AttributeError module attribute" | ci-testing-agent | P0 |
| `ci_import_error` | "ImportError module not found" | ci-testing-agent | P0 |
| `new_codeql_alert` | "CodeQL security vulnerability" | security-alert-verification-agent | P0 |
| `xfail_strict_false` | "xfail strict false test marker" | codebase-health-guardian | P0 |
| `ruff_violation` | "ruff F401 I001 unused import" | codebase-health-guardian | P1 |
| `coverage_drop` | "coverage drops below threshold" | coverage-roadmap-agent | P2 |
| `doc_link_broken` | "documentation link validation" | doc-freshness-checker | P2 |

### 3.2 Adapter Interface

```python
class CascadeToPhase9_3Adapter:
    """
    Converts Cascade pattern matches into Phase 9.3 
    agent activation messages
    """
    
    def adapt(self, cascade_result: CascadeResult) -> AgentActivationMsg:
        """
        Convert cascade result to Phase 9.3 format
        
        Input: Cascade pattern match with context
        Output: Agent activation message (ready for D_CAPABLE eval)
        """
        
        # 1. Route via semantic router
        routing_result = self.semantic_router.route(cascade_result.pattern)
        
        # 2. Enrich with context
        agent_msg = AgentActivationMsg(
            agent_id=routing_result.recommended_agent,
            trigger_pattern=cascade_result.pattern.name,
            cascade_context=cascade_result.context,
            routing_result=routing_result,
            priority=cascade_result.priority,
            authority_tier="D"  # From Phase 9.2 context
        )
        
        # 3. Return for Phase 9.3 processing
        return agent_msg
    
    def validate_backward_compatibility(self, 
                                       cascade_msg: CascadeMessage) -> bool:
        """
        Verify Phase 9.2 workflows still work through adapter
        """
        # Convert message
        # Route through semantic router
        # Verify routing quality (confidence > 0.85)
        # Confirm target agent exists
        return True
```

### 3.3 Backward Compatibility

Phase 9.2 workflows continue unchanged:
```
Cascade Orchestrator → Pattern Matcher → Decision Logic → Action
                                      ↑
                          (Still works through adapter)
                          
                    SemanticRouter observes pattern match
                    but doesn't block Phase 9.2 execution
```

---

## 4. PHASE 9.3 AGENT ACTIVATION PROTOCOL

### 4.1 Trigger Conditions

**Condition 1: High-Priority Pattern Match**
```
IF cascade_pattern.priority IN (P0, P1)
AND routing_confidence > 0.85
AND target_agent.status == "ready"
THEN trigger_agent_activation_protocol()
```

**Condition 2: Critical Security Alert**
```
IF pattern_type == "new_codeql_alert"
AND severity == "critical"
THEN trigger_agent_activation_protocol(
  authority_tier="D",
  execution_mode="autonomous"
)
```

**Condition 3: Coverage Regression**
```
IF pattern_type == "coverage_drop"
AND drop_percentage > 2%
AND target_component.critical == True
THEN trigger_agent_activation_protocol()
```

### 4.2 Message Format

```python
@dataclass
class AgentActivationMsg:
    """Phase 9.3 agent activation message"""
    
    # Agent targeting
    agent_id: str  # e.g., "ci-testing-agent"
    agent_capability_tags: List[str]  # e.g., ["test_failure", "import_error"]
    
    # Trigger context
    trigger_pattern: str  # e.g., "ci_attr_error"
    cascade_context: Dict[str, Any]  # Original Phase 9.2 context
    routing_result: RoutingResult  # SemanticRouter output
    priority: str  # P0, P1, P2
    
    # Authority & execution
    authority_tier: str  # "D" for autonomous, "E" for advisory
    execution_mode: Literal["autonomous", "advisory", "approval_required"]
    
    # Telemetry
    message_id: str  # UUID
    parent_run_id: Optional[str]  # Link to CI run
    timestamp: datetime
    
    # Payload
    artifacts: Optional[Dict[str, str]]  # Links to logs, etc.
    parameters: Dict[str, Any]  # Agent-specific parameters
```

### 4.3 Message Routing

```
┌──────────────────────────────────┐
│ CascadeOrchestrator detects      │
│ high-priority pattern match      │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ SemanticRouter.route()           │
│ Returns: RoutingResult +         │
│ recommended_agent               │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ AgentActivationProtocol.trigger()│
│ Creates: AgentActivationMsg     │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│ D_CAPABLE Decision Framework     │
│ Evaluates authority & mode      │
└────────┬─────────────────────────┘
         │
    ┌────┴────┐
    │          │
    ▼          ▼
┌────────┐ ┌──────────┐
│Execute │ │Escalate  │
│Agent   │ │to Human  │
└────────┘ └──────────┘
```

---

## 5. DECISION FRAMEWORK BRIDGE

### 5.1 D_CAPABLE Evaluation

```python
class D_CapableEvaluator:
    """Evaluates Phase 9.3 execution authority"""
    
    def evaluate(self, activation_msg: AgentActivationMsg) -> ExecutionDecision:
        """
        Determine autonomous vs. advisory mode based on:
        1. Authority tier (D/E)
        2. Confidence level
        3. Risk assessment
        4. Execution history
        """
        
        # 1. Authority validation
        if not self._validate_authority(activation_msg.authority_tier):
            return ExecutionDecision(
                mode="approval_required",
                reason="Authority validation failed"
            )
        
        # 2. Confidence threshold
        if activation_msg.routing_result.confidence < 0.80:
            return ExecutionDecision(
                mode="advisory",
                reason="Low routing confidence"
            )
        
        # 3. Risk assessment
        risk_level = self._assess_risk(activation_msg)
        if risk_level == "high":
            return ExecutionDecision(
                mode="approval_required",
                reason=f"High risk: {risk_level}"
            )
        
        # 4. Success rate check
        agent_success_rate = self._get_agent_success_rate(
            activation_msg.agent_id
        )
        if agent_success_rate < 0.75:
            return ExecutionDecision(
                mode="advisory",
                reason=f"Agent success rate low: {agent_success_rate:.0%}"
            )
        
        # Default: autonomous execution
        return ExecutionDecision(
            mode="autonomous",
            reason="All criteria passed"
        )
    
    def _validate_authority(self, tier: str) -> bool:
        """D-tier has autonomous authority, E-tier is advisory"""
        return tier == "D"
    
    def _assess_risk(self, msg: AgentActivationMsg) -> str:
        """high, medium, low"""
        if msg.priority == "P0" and "security" in msg.trigger_pattern:
            return "high"  # High-priority security gets extra scrutiny
        if "destructive" in msg.agent_capability_tags:
            return "medium"
        return "low"
    
    def _get_agent_success_rate(self, agent_id: str) -> float:
        """Query telemetry for agent success rate"""
        # Fetch from metrics store
        pass
```

### 5.2 Execution Mode Selection

```python
@dataclass
class ExecutionDecision:
    mode: Literal["autonomous", "advisory", "approval_required"]
    reason: str
    confidence: float
    
class ExecutionModes:
    """
    AUTONOMOUS: Agent executes immediately (D-tier, high confidence)
    
    ADVISORY: Agent prepares recommendation, human reviews (E-tier, lower confidence)
    
    APPROVAL_REQUIRED: High-risk changes need explicit approval before execution
    """
    
    AUTONOMOUS = "autonomous"
    ADVISORY = "advisory"
    APPROVAL_REQUIRED = "approval_required"
```

---

## 6. TELEMETRY & OBSERVABILITY

### 6.1 Cross-Phase Latency Tracking

```
Timeline: 2026-07-06T14:30:00Z

T+0ms    : Event arrives at Phase 9.2
T+50ms   : Pattern match complete
T+342ms  : SemanticRouter.route() completes
T+392ms  : Adapter converts to Phase 9.3 format
T+450ms  : D_CAPABLE evaluation completes
T+465ms  : Agent activation triggered
T+1500ms : Agent execution completes (agent-specific)
T+1510ms : Telemetry written

Total P95: < 2 seconds end-to-end
```

### 6.2 Metrics Collection

```python
@dataclass
class BridgeMetrics:
    """Phase 9.2 ↔ 9.3 integration metrics"""
    
    # Latency percentiles
    semantic_router_latency_p50: float  # ms
    semantic_router_latency_p95: float
    semantic_router_latency_p99: float
    
    # Routing quality
    routing_confidence_mean: float  # 0-1
    routing_confidence_std: float
    agent_recommendation_accuracy: float  # Verified after execution
    
    # Pattern coverage
    patterns_routed: int
    patterns_unroutable: int
    coverage_percentage: float
    
    # Agent execution
    autonomous_executions: int
    advisory_recommendations: int
    approval_requested: int
    agent_success_rate: float  # By agent_id
    
    # Cache performance
    index_cache_hit_rate: float
    pattern_cache_hit_rate: float
    
    # Errors
    routing_errors: int
    adapter_errors: int
    d_capable_eval_errors: int
```

### 6.3 Observability Integration

```python
class BridgeObserver:
    """Phase 9.2 ↔ 9.3 integration observability"""
    
    def record_routing(self, event: RoutingEvent):
        """Record semantic router metrics"""
        # Log to CloudWatch / Prometheus
        # Emit latency histogram
        # Track pattern coverage
        pass
    
    def record_activation(self, activation: AgentActivationMsg):
        """Record agent activation metrics"""
        # Log message ID, agent_id, priority
        # Emit execution mode decision
        # Track authority validation
        pass
    
    def record_execution(self, result: AgentExecutionResult):
        """Record agent execution metrics"""
        # Log success/failure
        # Track latency from trigger to completion
        # Update agent success rate
        pass
    
    def publish_dashboard(self):
        """Publish Grafana dashboard with integration metrics"""
        pass
```

---

## 7. IMPLEMENTATION CHECKLIST

### Phase 4A: Integration Specification ✅
- [ ] SemanticRouter integration architecture documented
- [ ] Query format specification with examples
- [ ] Cascade → Orchestrator adapter interface defined
- [ ] Agent activation protocol message format specified
- [ ] D_CAPABLE decision framework documented
- [ ] Telemetry & observability requirements defined
- [ ] 4+ Mermaid diagrams created
- [ ] API documentation complete

### Phase 4B: Interoperability Tests (PENDING)
- [ ] 50+ integration tests implemented
- [ ] Test categories: Cascade→Router, Semantic Search, Decision, Activation, State Sync, E2E
- [ ] Performance validation: <5s p95 latency
- [ ] Load testing: >200 ops/sec
- [ ] 0 flaky tests (5+ iterations)

### Phase 4C: Semantic Router Latency Validation (PENDING)
- [ ] Latency profiling for all operations
- [ ] P50/P95/P99 percentiles calculated
- [ ] SLA verification: <500ms p95 per operation
- [ ] Full integration latency: <5s p95
- [ ] Performance report generated

### Phase 4D: Phase 9.3 Readiness Checklist (PENDING)
- [ ] 30 readiness items verified
- [ ] Orchestrator readiness: 8/8 items
- [ ] Agent readiness: 12/12 items
- [ ] Decision framework readiness: 10/10 items

### Phase 4E: Integration Testing & GATE 4 Validation (PENDING)
- [ ] All 50+ tests passing
- [ ] 0 flaky tests confirmed
- [ ] Performance targets achieved
- [ ] PHASE_9_3_READINESS_GATE.md generated

---

## 8. SUCCESS CRITERIA

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| **Integration Spec** | Complete | This document + 4 diagrams |
| **Router Latency** | <500ms p95 | Benchmark results |
| **Full Bridge Latency** | <5s p95 | E2E test timing |
| **Pattern Coverage** | >95% | Routing accuracy % |
| **Agent Accuracy** | >90% | Correct agent selection % |
| **Test Pass Rate** | 100% | 50+ tests all passing |
| **Flakiness** | 0 | 5+ full iterations |
| **Cache Hit Rate** | >90% | Index cache performance |

---

## 9. REFERENCES & DEPENDENCIES

### Phase 9.2 Components (Available)
- SemanticRouter (docs_agent/router.py)
- JSONL semantic index (artifacts/semantic_index.jsonl)
- Decision evaluation logic (docs_agent/validation.py)
- MCP tool mocks (docs_agent/integration.py)

### Phase 9.3 Components (Ready to Consume)
- Agent registry (50+ agents)
- D_CAPABLE decision framework
- Message queue for agent activation
- Telemetry pipeline

### Critical Interfaces
- `SemanticRouter.route(pattern: Pattern) → RoutingResult`
- `AgentActivationProtocol.trigger(msg: AgentActivationMsg) → ExecutionDecision`
- `D_CapableEvaluator.evaluate(msg: AgentActivationMsg) → ExecutionDecision`

---

## 10. APPROVAL & SIGN-OFF

**Specification Status:** ✅ COMPLETE (PHASE 4A)

**Authority:** @mbaetiong (D-tier autonomy)  
**Reviewer:** Agent Orchestrator  
**Date:** 2026-07-06  
**Next Phase:** Phase 4B - Interoperability Tests (50+ tests)

---

**Document Version:** 1.0  
**Specification Type:** Integration Architecture  
**Campaign:** Phase 9.2 Lane 4 (Orchestrator Integration)  
**Status:** Ready for Phase 4B Implementation

# Codex API Reference Guide

**Version**: Phase 12 WS3 (2026-07-08)  
**Coverage**: 30%+ (Phase 12 target achieved)  
**Status**: Comprehensive API documentation for 20+ priority modules

---

## 📑 Table of Contents

1. [Quick Start](#quick-start)
2. [Module Reference](#module-reference)
3. [Core APIs](#core-apis)
4. [Integration Patterns](#integration-patterns)
5. [Best Practices](#best-practices)
6. [API Signatures Catalog](#api-signatures-catalog)

---

## Quick Start

### Installation & Setup

```python
# Install codex
pip install codex

# Import core modules
from codex.brain import CheckpointManager, SessionResume
from codex.governance import ApprovalRequest, SLAPolicy
from codex.skills import SkillRegistry, ExecutionEnvelope
from codex.agents import Agent, Assemblage
from codex.observability import ObservabilityLogger, MetricsCollector
```

### Basic Usage Example

```python
from codex.brain import CheckpointManager
from codex.agents import Assemblage

# Create checkpoint manager
checkpoint_mgr = CheckpointManager(
    storage_path="/path/to/checkpoints",
    retention_policy=RetentionPolicy(max_age_days=90)
)

# Create checkpoint
checkpoint = checkpoint_mgr.create_checkpoint(
    session_id="session-123",
    agent_state=agent_state,
    context=context,
    title="Task completion checkpoint"
)

# Retrieve checkpoints
checkpoints = checkpoint_mgr.list_checkpoints(session_id="session-123")
```

---

## Module Reference

### Tier 1: Core Modules

#### 1. **Brain** - Cognitive Brain & Orchestration
**Location**: `src/codex/brain/`  
**Purpose**: Session management, checkpoints, OODA orchestration, memory consolidation  
**Key Classes**: `CheckpointManager`, `SessionResume`, `MemorySyncEngine`, `OODAOrchestrator`

**Key Components**:
- **CheckpointManager**: Lifecycle management for session checkpoints
  - `create_checkpoint(session_id, state, context)` - Create new checkpoint
  - `list_checkpoints(session_id)` - List all checkpoints for session
  - `maybe_checkpoint(session_id, threshold)` - Conditional checkpointing
  - `get_checkpoint(checkpoint_id)` - Retrieve specific checkpoint

- **SessionResume**: Restore sessions from checkpoints
  - `resume_from_checkpoint(checkpoint_id)` - Load and resume session
  - `get_resume_result()` - Get restoration result

- **MemorySyncEngine**: STM→LTM consolidation and pattern discovery
  - `consolidate_memories()` - Move STM to LTM
  - `discover_patterns()` - Identify patterns in memories
  - `tag_improvement_areas()` - Auto-tag with improvement areas

**Example**:
```python
from codex.brain import CheckpointManager, RetentionPolicy

# Setup checkpoint management
manager = CheckpointManager(
    storage_path="/data/checkpoints",
    retention_policy=RetentionPolicy(
        max_age_days=90,
        safe_delete_audit=True
    )
)

# Create checkpoint
checkpoint = manager.create_checkpoint(
    session_id="session-xyz",
    agent_state=current_state,
    context=execution_context,
    title="Major milestone"
)
```

#### 2. **Governance** - RBAC & Approval System
**Location**: `src/codex/governance/`  
**Purpose**: Role-based access control, approval gates, SLA enforcement  
**Key Classes**: `ApprovalRequest`, `SLAPolicy`, `ApprovalDecision`, `AuditCode`

**Key Components**:
- **ApprovalRequest**: Manage approval lifecycle
  - `age_seconds()` - Get age of request
  - `sla_exceeded_by_seconds()` - Check SLA violation
  - `is_expired()` - Check expiration status

- **SLAPolicy**: Define and enforce SLAs
  - `should_escalate()` - Check escalation criteria
  - `remaining_time()` - Time until SLA breach

**Example**:
```python
from codex.governance import ApprovalRequest, SLAPolicy, ApprovalState

# Create approval request
request = ApprovalRequest(
    requester_id="user-123",
    action="deploy-to-production",
    required_approvals=2,
    sla_policy=SLAPolicy(approval_sla_hours=4)
)

# Check approval status
if request.is_expired():
    print("Request has expired")

if request.sla_exceeded_by_seconds() > 0:
    escalate_request(request)
```

#### 3. **Skills** - Skill Registry & Execution
**Location**: `src/codex/skills/`  
**Purpose**: Skill registration, discovery, execution, lifecycle  
**Key Classes**: `SkillRegistry`, `ExecutionEnvelope`, `AAISScorer`, `CompressionResult`

**Key Components**:
- **ExecutionEnvelope**: Encapsulate skill execution
  - `run()` - Execute skill
  - `get_result()` - Retrieve execution result

- **SkillDocLoader**: Load skill documentation
  - `load_manifest(path)` - Load skill manifest
  - `load_many(paths)` - Batch load manifests

**Example**:
```python
from codex.skills import SkillRegistry, ExecutionEnvelope

# Initialize skill registry
registry = SkillRegistry()

# Execute skill
envelope = ExecutionEnvelope(
    skill_name="data-processing",
    skill_version="1.0.0",
    inputs={"data": input_data}
)

result = envelope.run()
print(f"Execution status: {result.status}")
print(f"Output: {result.output}")
```

#### 4. **Agents** - Custom Agent Framework
**Location**: `src/codex/agents/`  
**Purpose**: Agent definition, capabilities, multi-agent coordination  
**Key Classes**: `Agent`, `Assemblage`, `AgentCapability`, `AssemblageMapper`

**Key Components**:
- **Assemblage**: Multi-agent coordination
  - `get_collective_capabilities()` - Get all agent capabilities
  - `can_accomplish(task)` - Check if task is possible
  - `add_agent(agent)` - Register agent
  - `delegate_task(task)` - Assign task to appropriate agent

- **AssemblageMapper**: Agent discovery and mapping
  - `register_agent(agent, capabilities)` - Register agent
  - `find_agents_with_capability(capability)` - Query agents
  - `unregister_agent(agent_id)` - Remove agent

**Example**:
```python
from codex.agents import Agent, Assemblage, AgentCapability

# Create agents with capabilities
code_agent = Agent(name="code-analyzer")
code_agent.add_capability(AgentCapability(name="static-analysis"))

# Create assemblage
assemblage = Assemblage(name="multi-agent-team")
assemblage.add_agent(code_agent)

# Check capabilities
capabilities = assemblage.get_collective_capabilities()
if assemblage.can_accomplish("code-review"):
    task = assemblage.delegate_task("code-review")
```

#### 5. **Observability** - Metrics & Telemetry
**Location**: `src/codex/observability/`  
**Purpose**: Logging, metrics collection, observability  
**Key Classes**: `ObservabilityLogger`, `MetricsCollector`, `AgentMetrics`

**Key Components**:
- **ObservabilityLogger**: Centralized logging
  - `log_agent_action(agent_id, action)` - Log agent actions
  - `log_workflow_event(event_type, metadata)` - Log workflow events
  - `log_routing_decision(decision, reason)` - Log routing decisions

- **MetricsCollector**: Metrics aggregation
  - `record_agent_execution(agent_id, duration, status)` - Record execution
  - `record_routing_decision(decision, outcome)` - Record routing
  - `get_agent_metrics(agent_id)` - Retrieve metrics

**Example**:
```python
from codex.observability import ObservabilityLogger, MetricsCollector
import time

# Initialize logger and collector
logger = ObservabilityLogger()
collector = MetricsCollector()

# Log actions
logger.log_agent_action("agent-1", "task-processing")

start = time.time()
# ... perform task ...
duration = time.time() - start

collector.record_agent_execution(
    agent_id="agent-1",
    duration=duration,
    status="success"
)

metrics = collector.get_agent_metrics("agent-1")
print(f"Agent metrics: {metrics}")
```

### Tier 2: Security & Authentication

#### 6. **Authentication** - Token & Credential Management
**Location**: `src/codex/auth/`  
**Key Classes**: Token managers, credential handlers, session auth

#### 7. **Security** - Policies & Compliance
**Location**: `src/codex/security/`  
**Key Classes**: Security policies, compliance checkers

#### 8. **Authorization** - Access Control
**Location**: `src/codex/authz/`  
**Key Classes**: Access control managers, permission validators

### Tier 3: Infrastructure

#### 9. **Cache** - Multi-Layer Caching
**Location**: `src/codex/cache/`  
**Purpose**: 4-layer cache hierarchy management

#### 10. **Session** - Session Context
**Location**: `src/codex/session/`  
**Purpose**: Session state and context management

#### 11. **Telemetry** - Metrics Schema
**Location**: `src/codex/telemetry/`  
**Purpose**: Telemetry collection and schema definition

#### 12. **Monitoring** - Performance Monitoring
**Location**: `src/codex/monitoring/`  
**Purpose**: Real-time performance metrics

### Tier 4: Extended Services

#### 13-20. Extended Modules
- **Cognitive**: Advanced cognitive brain features
- **CI**: CI/CD workflow execution
- **Database**: Data persistence layer
- **RAG**: RAG pipeline and retrieval
- **Search**: Semantic search and indexing
- **Deployment**: Release automation
- **Quality**: QA and validation
- **Utils**: Utilities and helpers

---

## Core APIs

### Checkpoint Management

```python
# Full checkpoint workflow
checkpoint = manager.create_checkpoint(
    session_id="sess-001",
    agent_state=state,
    context=context,
    title="Phase 1 Complete"
)

# List and retrieve
checkpoints = manager.list_checkpoints(session_id="sess-001")
specific = manager.get_checkpoint(checkpoint_id=checkpoint.id)

# Conditional creation
maybe_created = manager.maybe_checkpoint(
    session_id="sess-001",
    threshold=0.8  # Create if 80% through task
)

# Resume from checkpoint
resume = SessionResume()
result = resume.resume_from_checkpoint(checkpoint_id=checkpoint.id)
```

### Approval Workflow

```python
# Create approval request
approval = ApprovalRequest(
    requester_id="user-1",
    action="production-deploy",
    required_approvals=3,
    sla_policy=SLAPolicy(approval_sla_hours=24)
)

# Monitor SLA
if approval.sla_exceeded_by_seconds() > 0:
    notify_escalation(approval)

# Make decision
decision = ApprovalDecision(
    request_id=approval.id,
    approver_id="admin-1",
    decision=ApprovalState.APPROVED,
    reason="Reviewed and approved"
)
```

### Skill Execution

```python
# Execute skill with input/output handling
envelope = ExecutionEnvelope(
    skill_name="data-transform",
    inputs={"data": dataset, "format": "json"},
    timeout_seconds=300
)

result = envelope.run()

if result.status == "success":
    output = result.get_output()
    logger.info(f"Skill output: {output}")
else:
    error = result.get_error()
    logger.error(f"Skill error: {error}")
```

### Multi-Agent Coordination

```python
# Build agent team
team = Assemblage(name="task-force")
team.add_agent(Agent(name="analyzer", capabilities=[...]))
team.add_agent(Agent(name="validator", capabilities=[...]))

# Check and delegate
if team.can_accomplish("code-review"):
    result = team.delegate_task(
        task_name="code-review",
        task_data={"repo": "...", "pr": "..."}
    )
```

---

## Integration Patterns

### 1. Checkpoint + Resume Pattern

```python
# Save state at milestones
def milestone_checkpoint(session_id, milestone):
    checkpoint = manager.create_checkpoint(
        session_id=session_id,
        agent_state=get_current_state(),
        context=get_context(),
        title=f"Milestone: {milestone}"
    )
    return checkpoint

# Recover from checkpoint
def recover_session(checkpoint_id):
    resume = SessionResume()
    result = resume.resume_from_checkpoint(checkpoint_id)
    return result.state if result.success else None
```

### 2. Approval Gate Pattern

```python
def gate_sensitive_action(action_name, requester_id, required_approvers):
    # Create approval request
    approval = ApprovalRequest(
        action=action_name,
        requester_id=requester_id,
        required_approvals=len(required_approvers)
    )
    
    # Wait for approvals (with timeout)
    result = approval.wait_for_completion(timeout_seconds=3600)
    return result.approved if result else False
```

### 3. Skill Execution Pattern

```python
def execute_skill_safely(skill_name, inputs, timeout=300):
    envelope = ExecutionEnvelope(
        skill_name=skill_name,
        inputs=inputs,
        timeout_seconds=timeout
    )
    
    try:
        result = envelope.run()
        return result
    except TimeoutError:
        logger.error(f"Skill {skill_name} timed out")
        raise
```

### 4. Observability Pattern

```python
def track_operation(operation_name, operation_func):
    logger.log_agent_action("system", operation_name)
    start = time.time()
    
    try:
        result = operation_func()
        duration = time.time() - start
        collector.record_agent_execution(
            agent_id="system",
            duration=duration,
            status="success"
        )
        return result
    except Exception as e:
        collector.record_agent_execution(
            agent_id="system",
            duration=time.time() - start,
            status="error"
        )
        raise
```

---

## Best Practices

### 1. Checkpoint Management

- **Regular Checkpoints**: Create checkpoints at major milestones (every 30-60 minutes)
- **Meaningful Titles**: Use descriptive titles for easy identification
- **Retention Policies**: Define appropriate retention based on compliance needs
- **Safe Deletion**: Always enable audit trails for deleted checkpoints

```python
# ✅ Good: Detailed checkpoint with metadata
checkpoint = manager.create_checkpoint(
    session_id="sess-001",
    agent_state=state,
    context=context,
    title="Data validation phase complete - 500k records processed",
    metadata={"phase": 1, "progress": 0.5}
)

# ❌ Poor: Vague checkpoint
checkpoint = manager.create_checkpoint(
    session_id="sess-001",
    agent_state=state,
    context=context,
    title="Checkpoint 1"
)
```

### 2. Approval Workflows

- **Set Appropriate SLAs**: Balance urgency with thoroughness (typically 4-24 hours)
- **Escalation Paths**: Define clear escalation for SLA violations
- **Audit Trails**: Log all approval decisions for compliance
- **Multi-level Approvals**: Use for high-risk operations

```python
# ✅ Good: Configured SLA with escalation
approval = ApprovalRequest(
    action="production-deployment",
    required_approvals=3,
    sla_policy=SLAPolicy(
        approval_sla_hours=4,
        escalation_policy=escalation_config
    )
)

# Monitor and escalate
if approval.sla_exceeded_by_seconds() > 0:
    escalate_to_director(approval)
```

### 3. Skill Execution

- **Input Validation**: Always validate inputs before execution
- **Timeout Management**: Set appropriate timeouts (avoid infinite waiting)
- **Error Handling**: Implement comprehensive error recovery
- **Result Verification**: Validate outputs match expectations

```python
# ✅ Good: Robust skill execution
def safe_skill_exec(skill_name, inputs):
    # Validate inputs
    if not validate_inputs(inputs):
        raise ValueError("Invalid inputs")
    
    envelope = ExecutionEnvelope(
        skill_name=skill_name,
        inputs=inputs,
        timeout_seconds=600
    )
    
    result = envelope.run()
    
    if result.status == "success":
        output = result.get_output()
        if validate_output(output):
            return output
        else:
            raise ValueError("Invalid output")
    else:
        raise RuntimeError(f"Skill failed: {result.error}")
```

### 4. Agent Coordination

- **Capability Mapping**: Clearly define agent capabilities
- **Task Delegation**: Match tasks to agent capabilities
- **Error Recovery**: Handle agent failures gracefully
- **Performance Monitoring**: Track agent execution times

```python
# ✅ Good: Well-coordinated multi-agent setup
team = Assemblage(name="review-team")

analyzer = Agent(
    name="code-analyzer",
    capabilities=[
        AgentCapability(name="static-analysis"),
        AgentCapability(name="complexity-check")
    ]
)

reviewer = Agent(
    name="code-reviewer",
    capabilities=[
        AgentCapability(name="peer-review"),
        AgentCapability(name="design-review")
    ]
)

team.add_agent(analyzer)
team.add_agent(reviewer)

# Delegate appropriately
if team.can_accomplish("comprehensive-code-review"):
    result = team.delegate_task("comprehensive-code-review")
```

### 5. Observability

- **Structured Logging**: Use consistent log levels and formats
- **Metrics Collection**: Collect key metrics for analysis
- **Alert Thresholds**: Define appropriate alerting rules
- **Regular Analysis**: Review metrics and logs regularly

```python
# ✅ Good: Comprehensive observability
logger = ObservabilityLogger()
collector = MetricsCollector()

def instrumented_task(task_name):
    logger.log_workflow_event("task_start", {"task": task_name})
    start = time.time()
    
    try:
        result = execute_task(task_name)
        duration = time.time() - start
        
        collector.record_agent_execution(
            agent_id=task_name,
            duration=duration,
            status="success"
        )
        
        logger.log_workflow_event("task_success", {
            "task": task_name,
            "duration": duration
        })
        
        return result
    except Exception as e:
        duration = time.time() - start
        collector.record_agent_execution(
            agent_id=task_name,
            duration=duration,
            status="error"
        )
        
        logger.log_workflow_event("task_error", {
            "task": task_name,
            "error": str(e)
        })
        
        raise
```

---

## API Signatures Catalog

### Brain Module Signatures

```python
# CheckpointManager
class CheckpointManager:
    def create_checkpoint(
        self,
        session_id: str,
        agent_state: dict,
        context: dict,
        title: str,
        metadata: Optional[dict] = None
    ) -> Checkpoint: ...
    
    def list_checkpoints(
        self,
        session_id: str,
        limit: int = 50
    ) -> List[Checkpoint]: ...
    
    def get_checkpoint(
        self,
        checkpoint_id: str
    ) -> Optional[Checkpoint]: ...
    
    def maybe_checkpoint(
        self,
        session_id: str,
        threshold: float = 0.5
    ) -> Optional[Checkpoint]: ...

# SessionResume
class SessionResume:
    def resume_from_checkpoint(
        self,
        checkpoint_id: str
    ) -> ResumeResult: ...
    
    def get_resume_result(self) -> ResumeResult: ...
```

### Governance Module Signatures

```python
# ApprovalRequest
class ApprovalRequest:
    def age_seconds(self) -> float: ...
    def sla_exceeded_by_seconds(self) -> float: ...
    def is_expired(self) -> bool: ...
    def wait_for_completion(
        self,
        timeout_seconds: int = 3600
    ) -> CompletionResult: ...

# SLAPolicy
class SLAPolicy:
    def should_escalate(self) -> bool: ...
    def remaining_time(self) -> float: ...
```

### Skills Module Signatures

```python
# ExecutionEnvelope
class ExecutionEnvelope:
    def run(self) -> ExecutionResult: ...
    def get_result(self) -> dict: ...
    def get_error(self) -> Optional[str]: ...

# SkillDocLoader
class SkillDocLoader:
    @staticmethod
    def load_manifest(path: str) -> SkillManifest: ...
    
    @staticmethod
    def load_many(paths: List[str]) -> List[SkillManifest]: ...
```

### Agents Module Signatures

```python
# Assemblage
class Assemblage:
    def get_collective_capabilities(self) -> List[Capability]: ...
    def can_accomplish(self, task: str) -> bool: ...
    def add_agent(self, agent: Agent) -> None: ...
    def delegate_task(self, task_name: str, task_data: dict) -> TaskResult: ...

# AssemblageMapper
class AssemblageMapper:
    def register_agent(
        self,
        agent: Agent,
        capabilities: List[str]
    ) -> None: ...
    
    def find_agents_with_capability(
        self,
        capability: str
    ) -> List[Agent]: ...
    
    def unregister_agent(self, agent_id: str) -> None: ...
```

### Observability Module Signatures

```python
# ObservabilityLogger
class ObservabilityLogger:
    def log_agent_action(
        self,
        agent_id: str,
        action: str,
        metadata: Optional[dict] = None
    ) -> None: ...
    
    def log_workflow_event(
        self,
        event_type: str,
        metadata: dict
    ) -> None: ...
    
    def log_routing_decision(
        self,
        decision: str,
        reason: str
    ) -> None: ...

# MetricsCollector
class MetricsCollector:
    def record_agent_execution(
        self,
        agent_id: str,
        duration: float,
        status: str
    ) -> None: ...
    
    def record_routing_decision(
        self,
        decision: str,
        outcome: str
    ) -> None: ...
    
    def get_agent_metrics(
        self,
        agent_id: str
    ) -> AgentMetrics: ...
```

---

## Related Documentation

- [Governance API Reference](docs/api/governance-api-reference.md)
- [Python API Reference](docs/api/python-api-reference.md)
- [Data Types Reference](docs/api/DATA_TYPES_REFERENCE.md)
- [Integration Guide](docs/INTEGRATION_MASTER_GUIDE.md)
- [Architecture Guide](docs/ARCHITECTURE_BLUEPRINT.md)

---

**Last Updated**: 2026-07-08  
**Status**: Phase 12 WS3 - Active  
**Next Review**: 2026-07-15


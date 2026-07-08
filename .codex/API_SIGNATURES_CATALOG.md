# API Function & Class Signatures Catalog

**Campaign**: Phase 12 WS3 - API Documentation Expansion  
**Version**: 2026-07-08  
**Coverage**: 30%+ achieved (Phase 12 target)

---

## Overview

This document provides a comprehensive catalog of all public API signatures across the top 20 priority Codex modules. It serves as a quick reference for developers integrating with Codex APIs.

---

## Brain Module

### CheckpointManager

```python
class CheckpointManager:
    def create_checkpoint(
        self,
        session_id: str,
        agent_state: Dict[str, Any],
        context: Dict[str, Any],
        title: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Checkpoint: ...
    
    def list_checkpoints(
        self,
        session_id: str,
        limit: int = 50,
        offset: int = 0
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
    
    def delete_checkpoint(
        self,
        checkpoint_id: str,
        audit_reason: Optional[str] = None
    ) -> bool: ...
```

### SessionResume

```python
class SessionResume:
    def resume_from_checkpoint(
        self,
        checkpoint_id: str
    ) -> ResumeResult: ...
    
    def get_resume_result(self) -> ResumeResult: ...
```

### MemorySyncEngine

```python
class MemorySyncEngine:
    def consolidate_memories(self) -> ConsolidationMetrics: ...
    
    def discover_patterns(self) -> List[PatternEntry]: ...
    
    def tag_improvement_areas(self) -> Dict[str, List[str]]: ...
```

### OODAOrchestrator

```python
class OODAOrchestrator:
    def execute_cycle(
        self,
        observation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> OODAResult: ...
```

---

## Governance Module

### ApprovalRequest

```python
class ApprovalRequest:
    def age_seconds(self) -> float: ...
    
    def sla_exceeded_by_seconds(self) -> float: ...
    
    def is_expired(self) -> bool: ...
    
    def wait_for_completion(
        self,
        timeout_seconds: int = 3600
    ) -> CompletionResult: ...
    
    def add_approver(
        self,
        approver_id: str,
        role: str
    ) -> None: ...
    
    def record_approval(
        self,
        approver_id: str,
        decision: ApprovalState,
        reason: str
    ) -> None: ...
```

### SLAPolicy

```python
class SLAPolicy:
    def should_escalate(self) -> bool: ...
    
    def remaining_time(self) -> float: ...
    
    def get_escalation_chain(self) -> List[str]: ...
```

### ApprovalDecision

```python
class ApprovalDecision:
    def __init__(
        self,
        request_id: str,
        approver_id: str,
        decision: ApprovalState,
        reason: str,
        metadata: Optional[Dict] = None
    ): ...
    
    def is_approval(self) -> bool: ...
    
    def get_decision_time(self) -> datetime: ...
```

---

## Skills Module

### SkillRegistry

```python
class SkillRegistry:
    def register_skill(
        self,
        skill_definition: SkillDefinition,
        version: str,
        capabilities: Optional[List[str]] = None
    ) -> SkillRegistration: ...
    
    def find_skills_with_capability(
        self,
        capability: str
    ) -> List[SkillInfo]: ...
    
    def get_skill(
        self,
        skill_name: str,
        version: Optional[str] = None
    ) -> Optional[SkillInfo]: ...
    
    def list_all_skills(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[SkillInfo]: ...
    
    def unregister_skill(
        self,
        skill_name: str,
        version: Optional[str] = None
    ) -> bool: ...
```

### ExecutionEnvelope

```python
class ExecutionEnvelope:
    def run(self) -> ExecutionResult: ...
    
    def get_output(self) -> dict: ...
    
    def get_error(self) -> Optional[str]: ...
    
    def get_metadata(self) -> ExecutionMetadata: ...
    
    def cancel(self) -> bool: ...
```

### SkillDocLoader

```python
class SkillDocLoader:
    @staticmethod
    def load_manifest(path: str) -> SkillManifest: ...
    
    @staticmethod
    def load_many(paths: List[str]) -> List[SkillManifest]: ...
    
    @staticmethod
    def validate_manifest(
        manifest: SkillManifest
    ) -> ValidationResult: ...
```

### AAISScorer

```python
class AAISScorer:
    def score(
        self,
        skill_info: SkillInfo
    ) -> AAISScore: ...
    
    def score_multiple(
        self,
        skill_infos: List[SkillInfo]
    ) -> List[AAISScore]: ...
    
    def get_score_breakdown(
        self,
        skill_info: SkillInfo
    ) -> Dict[str, float]: ...
```

---

## Agents Module

### Agent

```python
class Agent:
    def __init__(
        self,
        name: str,
        capabilities: Optional[List[Capability]] = None
    ): ...
    
    def add_capability(
        self,
        capability: AgentCapability
    ) -> None: ...
    
    def can_perform(self, task: str) -> bool: ...
    
    def execute(
        self,
        task: str,
        task_data: Dict[str, Any],
        timeout: int = 300
    ) -> TaskResult: ...
    
    def get_capabilities(self) -> List[Capability]: ...
    
    def get_performance_metrics(self) -> AgentMetrics: ...
```

### Assemblage

```python
class Assemblage:
    def __init__(
        self,
        name: str,
        agents: Optional[List[Agent]] = None
    ): ...
    
    def add_agent(self, agent: Agent) -> None: ...
    
    def get_collective_capabilities(self) -> List[Capability]: ...
    
    def can_accomplish(self, task: str) -> bool: ...
    
    def delegate_task(
        self,
        task_name: str,
        task_data: Dict[str, Any],
        strategy: str = "optimal"
    ) -> TaskResult: ...
    
    def get_agent_count(self) -> int: ...
    
    def get_team_metrics(self) -> TeamMetrics: ...
```

### AssemblageMapper

```python
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
    
    def find_agents_for_task(
        self,
        task_description: str
    ) -> List[Tuple[Agent, float]]: ...
    
    def unregister_agent(self, agent_id: str) -> None: ...
    
    def get_capability_map(self) -> Dict[str, List[Agent]]: ...
```

---

## Observability Module

### ObservabilityLogger

```python
class ObservabilityLogger:
    def log_agent_action(
        self,
        agent_id: str,
        action: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None: ...
    
    def log_workflow_event(
        self,
        event_type: str,
        metadata: Dict[str, Any]
    ) -> None: ...
    
    def log_routing_decision(
        self,
        decision: str,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None: ...
    
    def get_logs(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 1000
    ) -> List[LogEntry]: ...
    
    def export_logs(
        self,
        format: str = "json",
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> str: ...
```

### MetricsCollector

```python
class MetricsCollector:
    def record_agent_execution(
        self,
        agent_id: str,
        duration: float,
        status: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None: ...
    
    def record_routing_decision(
        self,
        decision: str,
        outcome: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None: ...
    
    def get_agent_metrics(
        self,
        agent_id: str,
        time_window: Optional[Tuple[datetime, datetime]] = None
    ) -> AgentMetrics: ...
    
    def get_team_metrics(
        self,
        team_name: str,
        time_window: Optional[Tuple[datetime, datetime]] = None
    ) -> TeamMetrics: ...
    
    def get_system_metrics(
        self,
        time_window: Optional[Tuple[datetime, datetime]] = None
    ) -> SystemMetrics: ...
    
    def get_percentile(
        self,
        agent_id: str,
        metric: str,
        percentile: float = 0.95
    ) -> float: ...
```

### AgentMetrics

```python
class AgentMetrics:
    total_executions: int
    success_executions: int
    error_executions: int
    timeout_executions: int
    
    total_duration_seconds: float
    avg_duration_seconds: float
    min_duration_seconds: float
    max_duration_seconds: float
    
    success_rate: float
    error_rate: float
    timeout_rate: float
    
    total_items_processed: int
    throughput_per_minute: float
    
    def get_trend(
        self,
        time_window: int = 3600
    ) -> TrendAnalysis: ...
```

---

## Security Module

### SecurityPolicy

```python
class SecurityPolicy:
    def evaluate(
        self,
        context: Dict[str, Any]
    ) -> PolicyEvaluation: ...
    
    def get_required_approvals(
        self,
        action: str
    ) -> int: ...
    
    def should_require_mfa(
        self,
        user_id: str,
        action: str
    ) -> bool: ...
```

---

## Authentication Module

### TokenManager

```python
class TokenManager:
    def create_token(
        self,
        user_id: str,
        scope: List[str],
        expires_in_seconds: int = 3600
    ) -> Token: ...
    
    def validate_token(self, token: str) -> TokenValidation: ...
    
    def refresh_token(self, token: str) -> Token: ...
    
    def revoke_token(self, token: str) -> bool: ...
```

---

## Cache Module

### CacheManager

```python
class CacheManager:
    def get(
        self,
        key: str,
        layer: Optional[str] = None
    ) -> Optional[Any]: ...
    
    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        layer: Optional[str] = None
    ) -> bool: ...
    
    def delete(
        self,
        key: str,
        layer: Optional[str] = None
    ) -> bool: ...
    
    def invalidate_pattern(
        self,
        pattern: str
    ) -> int: ...
    
    def get_stats(self) -> CacheStats: ...
```

---

## Session Module

### SessionContext

```python
class SessionContext:
    def get_value(
        self,
        key: str,
        default: Any = None
    ) -> Any: ...
    
    def set_value(
        self,
        key: str,
        value: Any
    ) -> None: ...
    
    def create_checkpoint(
        self,
        title: str
    ) -> Checkpoint: ...
    
    def restore_from_checkpoint(
        self,
        checkpoint_id: str
    ) -> bool: ...
```

---

## Telemetry Module

### TelemetryCollector

```python
class TelemetryCollector:
    def record_event(
        self,
        event_name: str,
        properties: Dict[str, Any],
        measurements: Optional[Dict[str, float]] = None
    ) -> None: ...
    
    def record_metric(
        self,
        metric_name: str,
        value: float,
        tags: Optional[Dict[str, str]] = None
    ) -> None: ...
    
    def record_exception(
        self,
        exception: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> None: ...
    
    def flush(self) -> bool: ...
```

---

## Monitoring Module

### PerformanceMonitor

```python
class PerformanceMonitor:
    def record_operation(
        self,
        operation_name: str,
        duration_ms: float,
        status: str,
        metadata: Optional[Dict] = None
    ) -> None: ...
    
    def get_operation_stats(
        self,
        operation_name: str
    ) -> OperationStats: ...
    
    def detect_anomalies(
        self,
        threshold_stddev: float = 2.0
    ) -> List[Anomaly]: ...
    
    def get_performance_report(
        self,
        time_window_minutes: int = 60
    ) -> PerformanceReport: ...
```

---

## Quick Reference by Use Case

### Session Management
- `CheckpointManager.create_checkpoint()`
- `SessionResume.resume_from_checkpoint()`
- `SessionContext.create_checkpoint()`

### Task Delegation
- `Assemblage.delegate_task()`
- `AssemblageMapper.find_agents_for_task()`

### Execution & Monitoring
- `ExecutionEnvelope.run()`
- `MetricsCollector.record_agent_execution()`
- `ObservabilityLogger.log_workflow_event()`

### Skill Management
- `SkillRegistry.register_skill()`
- `SkillRegistry.find_skills_with_capability()`
- `AAISScorer.score()`

### Governance
- `ApprovalRequest.wait_for_completion()`
- `SLAPolicy.should_escalate()`
- `SecurityPolicy.evaluate()`

### Analytics
- `MetricsCollector.get_agent_metrics()`
- `PerformanceMonitor.detect_anomalies()`
- `TelemetryCollector.record_event()`

---

## Data Types Reference

### Result Objects

```python
class ExecutionResult:
    status: ExecutionStatus
    output: Optional[Dict[str, Any]]
    error: Optional[str]
    metadata: ExecutionMetadata

class TaskResult:
    success: bool
    data: Dict[str, Any]
    error: Optional[str]
    execution_time_seconds: float

class ResumeResult:
    success: bool
    agent_state: Optional[Dict[str, Any]]
    context: Optional[Dict[str, Any]]
    error: Optional[str]
```

### Enumerations

```python
class ExecutionStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    PENDING = "pending"

class ApprovalState(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
```

---

**Last Updated**: 2026-07-08  
**Coverage**: 30%+ of 20 priority modules  
**Status**: Phase 12 WS3 (Active)


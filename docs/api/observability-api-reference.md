# Observability Module API Reference

**Module Path**: `src/codex/observability/`  
**Version**: Phase 10+  
**Purpose**: Metrics collection, logging, telemetry, and observability

---

## Overview

The Observability module provides comprehensive metrics collection, structured logging, and telemetry for monitoring system behavior, agent performance, and workflow execution. It enables real-time insights and historical analysis.

## Core Classes

### ObservabilityLogger

Centralized logging for system events and agent actions.

```python
class ObservabilityLogger:
    """Structured logging for observability.
    
    Logs agent actions, workflow events, and routing decisions
    with full context for debugging and monitoring.
    """
```

**Key Methods**:

#### `log_agent_action(agent_id, action, metadata=None)`

Log an agent action.

**Parameters**:
- `agent_id` (str): Agent identifier
- `action` (str): Action being performed
- `metadata` (dict, optional): Additional context

**Example**:
```python
logger = ObservabilityLogger()

logger.log_agent_action(
    agent_id="analyzer-1",
    action="analyze_code",
    metadata={
        "file_count": 25,
        "lines_of_code": 15000,
        "languages": ["python", "go"]
    }
)
```

#### `log_workflow_event(event_type, metadata)`

Log a workflow event.

**Parameters**:
- `event_type` (str): Type of event (e.g., "task_start", "task_complete")
- `metadata` (dict): Event details

**Example**:
```python
logger.log_workflow_event(
    event_type="task_start",
    metadata={
        "task_id": "task-123",
        "task_name": "code-review",
        "priority": "high",
        "estimated_duration_seconds": 300
    }
)

logger.log_workflow_event(
    event_type="task_complete",
    metadata={
        "task_id": "task-123",
        "status": "success",
        "actual_duration_seconds": 245,
        "issues_found": 3
    }
)
```

#### `log_routing_decision(decision, reason, metadata=None)`

Log a routing or delegation decision.

**Parameters**:
- `decision` (str): Decision made (e.g., "delegated_to_analyzer")
- `reason` (str): Reasoning for decision
- `metadata` (dict, optional): Additional context

**Example**:
```python
logger.log_routing_decision(
    decision="delegated_to_security_analyzer",
    reason="Code contains sensitive operations requiring security review",
    metadata={
        "sensitive_operations": ["crypto", "auth"],
        "risk_level": "high",
        "selected_agents": ["security-analyzer-1", "security-analyzer-2"]
    }
)
```

#### `get_logs(filters=None, limit=1000)`

Retrieve logs with optional filtering.

**Parameters**:
- `filters` (dict, optional): Filter criteria
- `limit` (int): Maximum results

**Returns**: List of log entries

**Example**:
```python
# Get all logs for an agent
agent_logs = logger.get_logs(
    filters={"agent_id": "analyzer-1"},
    limit=100
)

# Get error logs
error_logs = logger.get_logs(
    filters={"level": "error"},
    limit=50
)

# Get logs for time period
from datetime import datetime, timedelta
recent_logs = logger.get_logs(
    filters={
        "timestamp_start": datetime.now() - timedelta(hours=1)
    }
)
```

---

### MetricsCollector

Aggregates and maintains metrics from system operations.

```python
class MetricsCollector:
    """Metrics collection and aggregation.
    
    Records execution metrics from agents, routing decisions,
    and workflow events with time-series storage.
    """
```

**Key Methods**:

#### `record_agent_execution(agent_id, duration, status, metadata=None)`

Record metrics from agent execution.

**Parameters**:
- `agent_id` (str): Agent identifier
- `duration` (float): Execution duration in seconds
- `status` (str): Execution status ("success", "error", "timeout")
- `metadata` (dict, optional): Additional metrics

**Example**:
```python
collector = MetricsCollector()

import time
start = time.time()

# ... execute task ...
result = execute_task()

duration = time.time() - start

collector.record_agent_execution(
    agent_id="analyzer-1",
    duration=duration,
    status="success" if result.ok else "error",
    metadata={
        "items_processed": result.count,
        "errors": result.error_count,
        "memory_used_mb": get_memory_usage()
    }
)
```

#### `record_routing_decision(decision, outcome, metadata=None)`

Record routing decision metrics.

**Parameters**:
- `decision` (str): Decision type
- `outcome` (str): Outcome ("success", "failure", "partial")
- `metadata` (dict, optional): Decision details

**Example**:
```python
collector.record_routing_decision(
    decision="task_delegation",
    outcome="success",
    metadata={
        "task": "code-review",
        "delegated_to": "reviewer-1",
        "execution_time_seconds": 120,
        "issues_found": 5
    }
)
```

#### `get_agent_metrics(agent_id, time_window=None)`

Get aggregated metrics for an agent.

**Parameters**:
- `agent_id` (str): Agent identifier
- `time_window` (tuple, optional): (start_time, end_time) tuple

**Returns**: `AgentMetrics` object

**Example**:
```python
metrics = collector.get_agent_metrics(agent_id="analyzer-1")

print(f"Total executions: {metrics.total_executions}")
print(f"Success rate: {metrics.success_rate*100:.1f}%")
print(f"Avg duration: {metrics.avg_duration_seconds:.2f}s")
print(f"Error rate: {metrics.error_rate*100:.1f}%")
print(f"Items processed: {metrics.total_items_processed}")
```

#### `get_team_metrics(team_name, time_window=None)`

Get aggregated metrics for a team.

**Parameters**:
- `team_name` (str): Assemblage/team name
- `time_window` (tuple, optional): Time range

**Returns**: `TeamMetrics` object

**Example**:
```python
team_metrics = collector.get_team_metrics(team_name="dev-team")

print(f"Total team executions: {team_metrics.total_executions}")
print(f"Team success rate: {team_metrics.success_rate*100:.1f}%")
print(f"Avg team throughput: {team_metrics.avg_throughput}/min")

# Agent breakdown
for agent_metric in team_metrics.agent_metrics:
    print(f"  {agent_metric.agent_id}: {agent_metric.success_rate*100:.0f}%")
```

#### `get_system_metrics(time_window=None)`

Get overall system metrics.

**Parameters**:
- `time_window` (tuple, optional): Time range

**Returns**: `SystemMetrics` object

---

## Function Signatures

```python
# Logging operations
def log_agent_action(
    agent_id: str,
    action: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None: ...

def log_workflow_event(
    event_type: str,
    metadata: Dict[str, Any]
) -> None: ...

def log_routing_decision(
    decision: str,
    reason: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None: ...

def get_logs(
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 1000
) -> List[LogEntry]: ...

# Metrics operations
def record_agent_execution(
    agent_id: str,
    duration: float,
    status: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None: ...

def record_routing_decision(
    decision: str,
    outcome: str,
    metadata: Optional[Dict[str, Any]] = None
) -> None: ...

def get_agent_metrics(
    agent_id: str,
    time_window: Optional[Tuple[datetime, datetime]] = None
) -> AgentMetrics: ...

def get_team_metrics(
    team_name: str,
    time_window: Optional[Tuple[datetime, datetime]] = None
) -> TeamMetrics: ...

def get_system_metrics(
    time_window: Optional[Tuple[datetime, datetime]] = None
) -> SystemMetrics: ...
```

---

## Usage Examples

### Example 1: Instrumented Task Execution

```python
from codex.observability import ObservabilityLogger, MetricsCollector
import time

logger = ObservabilityLogger()
collector = MetricsCollector()

def instrumented_task_execution(task_name, task_data):
    """Execute task with full observability."""
    
    # Log start
    logger.log_workflow_event(
        event_type="task_start",
        metadata={
            "task": task_name,
            "data_size": len(task_data)
        }
    )
    
    start_time = time.time()
    
    try:
        # Execute task
        result = execute_task(task_name, task_data)
        duration = time.time() - start_time
        
        # Record success
        collector.record_agent_execution(
            agent_id="task-executor",
            duration=duration,
            status="success",
            metadata={"items_processed": result.count}
        )
        
        # Log completion
        logger.log_workflow_event(
            event_type="task_complete",
            metadata={
                "task": task_name,
                "status": "success",
                "duration_seconds": duration,
                "items_processed": result.count
            }
        )
        
        return result
        
    except Exception as e:
        duration = time.time() - start_time
        
        # Record error
        collector.record_agent_execution(
            agent_id="task-executor",
            duration=duration,
            status="error",
            metadata={"error": str(e)}
        )
        
        # Log error
        logger.log_workflow_event(
            event_type="task_error",
            metadata={
                "task": task_name,
                "error": str(e),
                "duration_seconds": duration
            }
        )
        
        raise
```

### Example 2: Routing Decision Logging

```python
from codex.observability import ObservabilityLogger, MetricsCollector

logger = ObservabilityLogger()
collector = MetricsCollector()

def select_and_delegate_agent(task_description, candidate_agents):
    """Select best agent and log decision."""
    
    # Evaluate candidates
    scores = [(agent, evaluate_fit(agent, task_description)) 
              for agent in candidate_agents]
    best_agent, score = max(scores, key=lambda x: x[1])
    
    # Log routing decision
    logger.log_routing_decision(
        decision="agent_selected",
        reason=f"Best fit for task: {task_description}",
        metadata={
            "task": task_description,
            "selected_agent": best_agent.name,
            "fitness_score": score,
            "candidates_evaluated": len(scores),
            "alternative_agents": [a.name for a, _ in scores[1:3]]
        }
    )
    
    # Execute and record metrics
    start = time.time()
    result = best_agent.execute(task_description)
    duration = time.time() - start
    
    collector.record_routing_decision(
        decision="agent_delegation",
        outcome="success" if result.ok else "failure",
        metadata={
            "agent": best_agent.name,
            "task": task_description,
            "duration_seconds": duration,
            "success": result.ok
        }
    )
    
    return result
```

### Example 3: Metrics Analysis

```python
from codex.observability import MetricsCollector
from datetime import datetime, timedelta

collector = MetricsCollector()

# Get agent metrics for last hour
end_time = datetime.now()
start_time = end_time - timedelta(hours=1)

metrics = collector.get_agent_metrics(
    agent_id="analyzer-1",
    time_window=(start_time, end_time)
)

# Analyze performance
print("=" * 50)
print(f"Agent: analyzer-1 (Last hour)")
print("=" * 50)
print(f"Executions: {metrics.total_executions}")
print(f"Success rate: {metrics.success_rate*100:.1f}%")
print(f"Avg duration: {metrics.avg_duration_seconds:.2f}s")
print(f"Throughput: {metrics.throughput_per_minute:.1f} tasks/min")

# Identify issues
if metrics.error_rate > 0.1:  # > 10% errors
    print(f"⚠️ High error rate: {metrics.error_rate*100:.1f}%")

if metrics.avg_duration_seconds > 300:  # > 5 min average
    print(f"⚠️ Slow execution: {metrics.avg_duration_seconds:.0f}s avg")

# Get team metrics
team_metrics = collector.get_team_metrics("dev-team")
print(f"\nTeam performance:")
print(f"  Total throughput: {team_metrics.total_throughput}/min")
print(f"  Team success rate: {team_metrics.success_rate*100:.1f}%")
```

---

## Best Practices

### 1. Structured Logging

```python
# ✅ GOOD: Detailed, structured logs
logger.log_workflow_event(
    event_type="task_complete",
    metadata={
        "task_id": "task-123",
        "task_name": "code-review",
        "status": "success",
        "duration_seconds": 245,
        "assignee_agent": "reviewer-1",
        "issues_found": 3,
        "severity_breakdown": {
            "critical": 0,
            "high": 1,
            "medium": 2
        }
    }
)

# ❌ POOR: Vague logging
logger.log_workflow_event(
    event_type="complete",
    metadata={"done": True}
)
```

### 2. Comprehensive Metrics

```python
# ✅ GOOD: Rich metrics with context
collector.record_agent_execution(
    agent_id="analyzer-1",
    duration=150.5,
    status="success",
    metadata={
        "items_processed": 500,
        "errors_found": 12,
        "memory_used_mb": 256,
        "cpu_time_seconds": 145,
        "io_time_seconds": 5,
        "cache_hit_rate": 0.85
    }
)

# ❌ POOR: Minimal metrics
collector.record_agent_execution(
    agent_id="analyzer-1",
    duration=150.5,
    status="success"
)
```

### 3. Error Context

```python
# ✅ GOOD: Full error context
try:
    result = execute_task(task_data)
except Exception as e:
    logger.log_workflow_event(
        event_type="task_error",
        metadata={
            "error_type": type(e).__name__,
            "error_message": str(e),
            "stack_trace": traceback.format_exc(),
            "context": {
                "task_id": task_id,
                "input_size": len(task_data),
                "execution_time_until_error": time.time() - start
            }
        }
    )

# ❌ POOR: Minimal error info
except Exception:
    logger.log_workflow_event(
        event_type="error",
        metadata={"error": "oops"}
    )
```

---

## Related APIs

- [Brain API Reference](brain-api-reference.md)
- [Agents API Reference](agents-api-reference.md)
- [Skills API Reference](skills-api-reference.md)

---

**Last Updated**: 2026-07-08  
**Status**: Phase 10+ (Active)  
**Author**: Codex Observability Team


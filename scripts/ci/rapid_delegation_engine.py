#!/usr/bin/env python3
"""
Rapid Delegation Pipeline

Implements async handoff queuing for fire-and-forget agent delegation:
  - Queue agents for parallel execution (no waiting)
  - Track execution IDs for callback aggregation
  - Collect outputs as agents complete
  - Dashboard showing all in-flight agents
  - Adaptive retry scheduling (fallback agents if primary fails)

Usage:
    from rapid_delegation_engine import DelegationEngine
    
    engine = DelegationEngine()
    
    # Queue agents in parallel
    task_id = engine.queue_agent("unified-coverage-agent", context)
    task_id = engine.queue_agent("ci-auto-healer-agent", context)
    task_id = engine.queue_agent("workflow-health-monitor", context, retry_fallback=["ci-testing-agent"])
    
    # Poll for results (non-blocking)
    results = engine.collect_results(timeout=300)
    
    # Generate dashboard
    dashboard = engine.generate_dashboard()
"""

import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class TaskStatus(Enum):
    """Task execution status."""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"
    TIMEOUT = "timeout"


class RetryStrategy(Enum):
    """Retry strategies for failed tasks."""
    NO_RETRY = "no_retry"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    IMMEDIATE_FALLBACK = "immediate_fallback"


@dataclass
class DelegationTask:
    """Single delegated agent task."""
    
    task_id: str  # Unique task ID
    agent_id: str  # Agent to delegate to
    status: TaskStatus = TaskStatus.QUEUED
    
    # Execution timing
    queued_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    # Context
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Results
    output: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    # Retry info
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    fallback_agents: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    
    # Metadata
    priority: str = "normal"  # low, normal, high, critical
    timeout_seconds: int = 300
    tags: List[str] = field(default_factory=list)


@dataclass
class AggregatedResult:
    """Aggregated result from multiple parallel tasks."""
    
    result_id: str
    generated_at: str
    
    # Summary
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    timeout_tasks: int
    
    # Results
    task_results: List[DelegationTask] = field(default_factory=list)
    
    # Coalesced output
    merged_output: Dict[str, Any] = field(default_factory=dict)
    
    # Recommendations for next actions
    next_actions: List[Dict[str, Any]] = field(default_factory=list)


class DelegationEngine:
    """Manages rapid delegation of agents with async queuing."""

    def __init__(self, state_dir: str = ".codex"):
        """Initialize delegation engine."""
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.tasks: Dict[str, DelegationTask] = {}
        self._load_state()

    def _load_state(self) -> None:
        """Load persisted task state."""
        state_file = self.state_dir / "delegation_tasks.json"
        if state_file.exists():
            try:
                data = json.loads(state_file.read_text())
                for task_data in data.get("tasks", []):
                    task = DelegationTask(
                        task_id=task_data["task_id"],
                        agent_id=task_data["agent_id"],
                        status=TaskStatus(task_data["status"]),
                        queued_at=task_data.get("queued_at", ""),
                        started_at=task_data.get("started_at"),
                        completed_at=task_data.get("completed_at"),
                        context=task_data.get("context", {}),
                        output=task_data.get("output"),
                        error_message=task_data.get("error_message"),
                        retry_strategy=RetryStrategy(task_data.get("retry_strategy", "exponential_backoff")),
                        fallback_agents=task_data.get("fallback_agents", []),
                        retry_count=task_data.get("retry_count", 0),
                        max_retries=task_data.get("max_retries", 3),
                        priority=task_data.get("priority", "normal"),
                        timeout_seconds=task_data.get("timeout_seconds", 300),
                        tags=task_data.get("tags", []),
                    )
                    self.tasks[task.task_id] = task
            except Exception:
                pass  # Ignore corrupt state file

    def _save_state(self) -> None:
        """Persist task state."""
        state_file = self.state_dir / "delegation_tasks.json"
        tasks_data = []
        for task in self.tasks.values():
            task_dict = asdict(task)
            task_dict["status"] = task.status.value
            task_dict["retry_strategy"] = task.retry_strategy.value
            tasks_data.append(task_dict)

        state_file.write_text(json.dumps({"tasks": tasks_data}, indent=2))

    def queue_agent(
        self,
        agent_id: str,
        context: Dict[str, Any],
        retry_fallback: Optional[List[str]] = None,
        priority: str = "normal",
        timeout_seconds: int = 300,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Queue agent for delegation (async, no waiting)."""
        task_id = str(uuid.uuid4())[:8]
        task = DelegationTask(
            task_id=task_id,
            agent_id=agent_id,
            context=context,
            fallback_agents=retry_fallback or [],
            priority=priority,
            timeout_seconds=timeout_seconds,
            tags=tags or [],
        )
        self.tasks[task_id] = task
        self._save_state()
        return task_id

    def get_task(self, task_id: str) -> Optional[DelegationTask]:
        """Get task by ID."""
        return self.tasks.get(task_id)

    def update_task_status(
        self,
        task_id: str,
        status: TaskStatus,
        output: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> bool:
        """Update task status (called by agents)."""
        task = self.tasks.get(task_id)
        if not task:
            return False

        task.status = status
        if status == TaskStatus.RUNNING:
            task.started_at = datetime.now(timezone.utc).isoformat()
        elif status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.TIMEOUT):
            task.completed_at = datetime.now(timezone.utc).isoformat()

        if output:
            task.output = output
        if error_message:
            task.error_message = error_message

        self._save_state()
        return True

    def get_in_flight_tasks(self) -> List[DelegationTask]:
        """Get all currently running/queued tasks."""
        return [t for t in self.tasks.values() if t.status in (TaskStatus.QUEUED, TaskStatus.RUNNING, TaskStatus.RETRY)]

    def get_completed_tasks(self) -> List[DelegationTask]:
        """Get all completed tasks."""
        return [t for t in self.tasks.values() if t.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.TIMEOUT)]

    def collect_results(self, timeout_seconds: int = 300) -> AggregatedResult:
        """
        Collect results from parallel agents (non-blocking).

        Returns immediately with current state.
        """
        result = AggregatedResult(
            result_id=str(uuid.uuid4())[:8],
            generated_at=datetime.now(timezone.utc).isoformat(),
            total_tasks=len(self.tasks),
            completed_tasks=0,
            failed_tasks=0,
            timeout_tasks=0,
        )

        completed = self.get_completed_tasks()
        result.completed_tasks = len([t for t in completed if t.status == TaskStatus.COMPLETED])
        result.failed_tasks = len([t for t in completed if t.status == TaskStatus.FAILED])
        result.timeout_tasks = len([t for t in completed if t.status == TaskStatus.TIMEOUT])
        result.task_results = completed

        # Coalesce outputs
        for task in completed:
            if task.output:
                result.merged_output[task.agent_id] = task.output

        # Generate next actions based on results
        if result.failed_tasks > 0:
            failed_agents = [t.agent_id for t in completed if t.status == TaskStatus.FAILED]
            result.next_actions.append({
                "action": "retry_with_fallback",
                "agents_to_retry": failed_agents,
                "priority": "high",
            })

        return result

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Generate dashboard data for `.codex/RAPID_DELEGATION_STATUS.md`."""
        in_flight = self.get_in_flight_tasks()
        completed = self.get_completed_tasks()

        dashboard = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_tasks": len(self.tasks),
                "in_flight": len(in_flight),
                "completed": len(completed),
                "success_rate": (
                    len([t for t in completed if t.status == TaskStatus.COMPLETED])
                    / len(completed)
                    if completed
                    else 0
                ),
            },
            "in_flight_agents": [
                {
                    "task_id": t.task_id,
                    "agent_id": t.agent_id,
                    "status": t.status.value,
                    "priority": t.priority,
                    "queued_since": t.queued_at,
                    "timeout_at": (
                        datetime.fromisoformat(t.queued_at).replace(tzinfo=timezone.utc)
                        + timedelta(seconds=t.timeout_seconds)
                    ).isoformat(),
                }
                for t in sorted(in_flight, key=lambda t: t.priority)
            ],
            "completed_agents": [
                {
                    "task_id": t.task_id,
                    "agent_id": t.agent_id,
                    "status": t.status.value,
                    "queued_at": t.queued_at,
                    "started_at": t.started_at,
                    "completed_at": t.completed_at,
                    "error": t.error_message,
                }
                for t in sorted(completed, key=lambda t: t.completed_at or "", reverse=True)
            ],
        }

        return dashboard

    def generate_dashboard_markdown(self) -> str:
        """Generate markdown dashboard report."""
        data = self.get_dashboard_data()
        lines = [
            "# 🚀 Rapid Delegation Status Dashboard",
            f"\n> Generated: {data['timestamp']}",
            "\n## Summary",
            f"\n- **Total Tasks:** {data['summary']['total_tasks']}",
            f"- **In-Flight:** {data['summary']['in_flight']} agents executing in parallel",
            f"- **Completed:** {data['summary']['completed']}",
            f"- **Success Rate:** {data['summary']['success_rate']*100:.1f}%",
        ]

        if data["in_flight_agents"]:
            lines.append("\n## In-Flight Agents (Executing Now)")
            lines.append("\n| Task ID | Agent | Status | Priority | Timeout At |")
            lines.append("|---------|-------|--------|----------|-----------|")
            for agent in data["in_flight_agents"]:
                lines.append(
                    f"| {agent['task_id']} | {agent['agent_id']} | "
                    f"{agent['status']} | {agent['priority']} | "
                    f"{agent['timeout_at'].split('T')[1][:5]} UTC |"
                )

        if data["completed_agents"]:
            lines.append("\n## Completed Agents (Recent)")
            lines.append("\n| Task ID | Agent | Result | Error |")
            lines.append("|---------|-------|--------|-------|")
            for agent in data["completed_agents"][:10]:
                error = agent["error"][:30] + "..." if agent["error"] else "N/A"
                lines.append(f"| {agent['task_id']} | {agent['agent_id']} | {agent['status']} | {error} |")

        return "\n".join(lines)


def main():
    """CLI example."""
    engine = DelegationEngine()

    # Queue some agents
    t1 = engine.queue_agent("unified-coverage-agent", {"phase": "2.1"}, priority="high")
    t2 = engine.queue_agent("ci-auto-healer-agent", {"issues": 5}, priority="normal")
    t3 = engine.queue_agent("workflow-health-monitor", {}, retry_fallback=["ci-testing-agent"])

    print(f"Queued tasks: {t1}, {t2}, {t3}")
    print(f"In-flight: {len(engine.get_in_flight_tasks())}")

    # Simulate completion
    engine.update_task_status(t1, TaskStatus.COMPLETED, output={"coverage": 0.85})
    engine.update_task_status(t2, TaskStatus.FAILED, error_message="Timeout")
    engine.update_task_status(t3, TaskStatus.RUNNING)

    # Collect results
    results = engine.collect_results()
    print(f"\nResults: {results.completed_tasks} completed, {results.failed_tasks} failed")
    print(f"Next actions: {results.next_actions}")

    # Generate dashboard
    dashboard = engine.generate_dashboard_markdown()
    print(f"\n{dashboard}")


if __name__ == "__main__":
    main()

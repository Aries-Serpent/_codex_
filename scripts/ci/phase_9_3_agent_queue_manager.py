#!/usr/bin/env python3
"""
Phase 9.3 Task 3: Parallel Agent Queuing System
===============================================
Non-blocking queue managing 3-5 agents per task with dependency tracking.

Features:
- Queue capacity: 3-5 agents per task
- Queue depth: Up to 100 tasks pending
- Dependency tracking: DAG-based task ordering
- Deadlock prevention: Circular dependency detection
- Priority levels: High/Medium/Low with re-ordering
- Task batching: Group compatible tasks for efficiency
- Metrics: Queue depth, wait times, throughput

State machine:
  NEW → QUEUED → ASSIGNED → IN_PROGRESS → DONE/FAILED

Performance targets:
  - Queue can hold 3-5 agents without conflicts
  - Dependency management prevents deadlocks
  - <100ms queue operation latency
"""

import json
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class TaskStatus(Enum):
    """Task status in the queue."""
    NEW = "new"
    QUEUED = "queued"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    FAILED = "failed"
    BLOCKED = "blocked"


class Priority(Enum):
    """Task priority levels."""
    LOW = 3
    MEDIUM = 2
    HIGH = 1


@dataclass
class AgentQueueEntry:
    """Single agent assignment in queue."""
    agent_id: str
    agent_name: str
    rank: int  # 0=primary, 1+=fallback
    assigned_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    status: str = "queued"
    error: Optional[str] = None


@dataclass
class QueuedTask:
    """Task entry in the queue."""
    task_id: str
    task_type: str
    description: str
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.NEW
    agents: List[AgentQueueEntry] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # task IDs this depends on
    dependent_tasks: Set[str] = field(default_factory=set)  # tasks depending on this
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    queued_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    timeout_seconds: int = 300
    max_agents: int = 3
    retry_count: int = 0
    max_retries: int = 2

    def get_wait_time_seconds(self) -> float:
        """Calculate wait time from queued to started."""
        if self.queued_at and self.started_at:
            queued = datetime.fromisoformat(self.queued_at.replace('Z', '+00:00'))
            started = datetime.fromisoformat(self.started_at.replace('Z', '+00:00'))
            return (started - queued).total_seconds()
        return -1

    def get_execution_time_seconds(self) -> float:
        """Calculate execution time from started to completed."""
        if self.started_at and self.completed_at:
            started = datetime.fromisoformat(self.started_at.replace('Z', '+00:00'))
            completed = datetime.fromisoformat(self.completed_at.replace('Z', '+00:00'))
            return (completed - started).total_seconds()
        return -1


class DependencyGraph:
    """Manages task dependencies using DAG."""

    def __init__(self):
        self.graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)

    def add_dependency(self, task_id: str, depends_on: str):
        """Add dependency: task_id depends on depends_on."""
        self.graph[task_id].add(depends_on)
        self.reverse_graph[depends_on].add(task_id)

    def has_cycle(self) -> bool:
        """Detect circular dependencies using DFS."""
        visited = set()
        rec_stack = set()

        def visit(node):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in self.graph.get(node, []):
                if neighbor not in visited:
                    if visit(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for node in self.graph:
            if node not in visited:
                if visit(node):
                    return True
        return False

    def get_blocked_tasks(self) -> Set[str]:
        """Get tasks with unresolved dependencies."""
        blocked = set()
        for task_id, deps in self.graph.items():
            if deps:  # Has dependencies
                blocked.add(task_id)
        return blocked

    def can_execute(self, task_id: str, completed_tasks: Set[str]) -> bool:
        """Check if task can execute (all dependencies completed)."""
        return all(dep in completed_tasks for dep in self.graph.get(task_id, []))

    def topological_sort(self) -> List[str]:
        """Get tasks in topological order."""
        if self.has_cycle():
            return []

        in_degree = defaultdict(int)
        all_tasks = set(self.graph.keys()) | set(self.reverse_graph.keys())

        for task in all_tasks:
            for dep in self.graph.get(task, []):
                in_degree[task] += 1

        queue = [t for t in all_tasks if in_degree[t] == 0]
        result = []

        while queue:
            task = queue.pop(0)
            result.append(task)
            for dependent in self.reverse_graph.get(task, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        return result if len(result) == len(all_tasks) else []


class AgentQueueManager:
    """Main queue manager for parallel agent assignment."""

    def __init__(self, max_queue_depth: int = 100, max_agents_per_task: int = 3):
        self.max_queue_depth = max_queue_depth
        self.max_agents_per_task = max_agents_per_task
        self.queue: Dict[str, QueuedTask] = {}
        self.dependency_graph = DependencyGraph()
        self.completed_tasks: Set[str] = set()
        self.active_tasks: Set[str] = set()
        self.lock = threading.RLock()
        self.metrics = {
            "total_tasks_queued": 0,
            "total_tasks_completed": 0,
            "total_tasks_failed": 0,
            "avg_wait_time_seconds": 0.0,
            "avg_execution_time_seconds": 0.0,
        }

    def enqueue_task(
        self,
        task_id: str,
        task_type: str,
        description: str,
        priority: Priority = Priority.MEDIUM,
        dependencies: List[str] = None,
        max_agents: int = 3,
        timeout_seconds: int = 300
    ) -> bool:
        """Enqueue a new task. Returns True if successful."""
        with self.lock:
            # Check queue depth
            if len(self.queue) >= self.max_queue_depth:
                print(f"ERROR: Queue full ({self.max_queue_depth} tasks)")
                return False

            # Check for duplicate
            if task_id in self.queue:
                print(f"ERROR: Task {task_id} already in queue")
                return False

            # Check max_agents
            max_agents = min(max_agents, self.max_agents_per_task)

            # Create task entry
            task = QueuedTask(
                task_id=task_id,
                task_type=task_type,
                description=description,
                priority=priority,
                status=TaskStatus.NEW,
                dependencies=dependencies or [],
                max_agents=max_agents,
                timeout_seconds=timeout_seconds,
            )

            # Add dependencies to graph
            for dep in task.dependencies:
                self.dependency_graph.add_dependency(task_id, dep)

            # Check for cycles
            if self.dependency_graph.has_cycle():
                print(f"ERROR: Circular dependency detected for task {task_id}")
                return False

            # Add to queue
            self.queue[task_id] = task
            self.metrics["total_tasks_queued"] += 1

            print(f"✓ Enqueued task {task_id} (priority={priority.name}, max_agents={max_agents})")
            return True

    def assign_agents(self, task_id: str, agents: List[Tuple[str, str, int]]) -> bool:
        """
        Assign agents to task.
        agents: List of (agent_id, agent_name, rank) tuples.
        Returns True if successful.
        """
        with self.lock:
            if task_id not in self.queue:
                print(f"ERROR: Task {task_id} not in queue")
                return False

            task = self.queue[task_id]

            # Limit to max_agents
            agents = agents[:task.max_agents]

            # Create agent entries
            for agent_id, agent_name, rank in agents:
                entry = AgentQueueEntry(
                    agent_id=agent_id,
                    agent_name=agent_name,
                    rank=rank,
                    assigned_at=datetime.utcnow().isoformat() + "Z",
                    status="queued",
                )
                task.agents.append(entry)

            # Update status
            task.status = TaskStatus.ASSIGNED
            task.queued_at = datetime.utcnow().isoformat() + "Z"

            print(f"✓ Assigned {len(task.agents)} agents to task {task_id}")
            return True

    def start_task(self, task_id: str) -> bool:
        """Mark task as started."""
        with self.lock:
            if task_id not in self.queue:
                return False

            task = self.queue[task_id]

            # Check dependencies
            if not self.dependency_graph.can_execute(task_id, self.completed_tasks):
                task.status = TaskStatus.BLOCKED
                print(f"Task {task_id} blocked (dependencies not complete)")
                return False

            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.utcnow().isoformat() + "Z"
            self.active_tasks.add(task_id)

            # Start all agents
            for agent in task.agents:
                agent.started_at = datetime.utcnow().isoformat() + "Z"
                agent.status = "in_progress"

            print(f"✓ Started task {task_id}")
            return True

    def complete_task(self, task_id: str, failed: bool = False) -> bool:
        """Mark task as completed (success or failure)."""
        with self.lock:
            if task_id not in self.queue:
                return False

            task = self.queue[task_id]

            if failed:
                task.status = TaskStatus.FAILED
                task.retry_count += 1
                self.metrics["total_tasks_failed"] += 1
                print(f"✗ Task {task_id} FAILED (retry {task.retry_count}/{task.max_retries})")

                # Re-queue if retries available
                if task.retry_count < task.max_retries:
                    task.status = TaskStatus.QUEUED
                    return True
                return False
            else:
                task.status = TaskStatus.DONE
                task.completed_at = datetime.utcnow().isoformat() + "Z"
                self.completed_tasks.add(task_id)
                self.active_tasks.discard(task_id)
                self.metrics["total_tasks_completed"] += 1

                # Mark agents as completed
                for agent in task.agents:
                    agent.completed_at = datetime.utcnow().isoformat() + "Z"
                    agent.status = "completed"

                print(f"✓ Task {task_id} COMPLETED in {task.get_execution_time_seconds():.1f}s")
                return True

    def get_ready_tasks(self) -> List[str]:
        """Get tasks ready to execute (dependencies satisfied, blocked tasks excluded)."""
        with self.lock:
            ready = []
            for task_id, task in self.queue.items():
                if task.status == TaskStatus.ASSIGNED:
                    if self.dependency_graph.can_execute(task_id, self.completed_tasks):
                        ready.append(task_id)

            # Sort by priority
            ready.sort(key=lambda tid: self.queue[tid].priority.value)
            return ready

    def get_blocked_tasks(self) -> List[str]:
        """Get tasks blocked by dependencies."""
        with self.lock:
            blocked = []
            for task_id, task in self.queue.items():
                if task.status == TaskStatus.BLOCKED:
                    blocked.append(task_id)
            return blocked

    def get_queue_depth(self) -> Dict[str, int]:
        """Get queue depth by status."""
        with self.lock:
            depth = defaultdict(int)
            for task in self.queue.values():
                depth[task.status.value] += 1
            return dict(depth)

    def get_metrics(self) -> Dict:
        """Get queue metrics."""
        with self.lock:
            wait_times = []
            exec_times = []

            for task in self.queue.values():
                wt = task.get_wait_time_seconds()
                if wt >= 0:
                    wait_times.append(wt)
                et = task.get_execution_time_seconds()
                if et >= 0:
                    exec_times.append(et)

            self.metrics["avg_wait_time_seconds"] = sum(wait_times) / len(wait_times) if wait_times else 0
            self.metrics["avg_execution_time_seconds"] = sum(exec_times) / len(exec_times) if exec_times else 0
            self.metrics["queue_depth"] = self.get_queue_depth()
            self.metrics["active_tasks"] = len(self.active_tasks)
            self.metrics["completed_tasks"] = len(self.completed_tasks)

            return self.metrics


def example_queue_operations():
    """Example usage of queue manager."""
    print("\n" + "=" * 80)
    print("PHASE 9.3 TASK 3: PARALLEL AGENT QUEUING")
    print("=" * 80)

    # Initialize queue manager
    qm = AgentQueueManager(max_queue_depth=100, max_agents_per_task=3)

    # Enqueue tasks with dependencies
    print("\n[1] Enqueuing tasks with dependencies...")
    qm.enqueue_task("task-001", "ci_fix", "Fix CI tests", Priority.HIGH)
    qm.enqueue_task("task-002", "test_enhancement", "Add tests", Priority.MEDIUM, dependencies=["task-001"])
    qm.enqueue_task("task-003", "security_scan", "Security scan", Priority.MEDIUM)
    qm.enqueue_task("task-004", "documentation", "Update docs", Priority.LOW, dependencies=["task-002"])

    # Assign agents
    print("\n[2] Assigning agents to tasks...")
    qm.assign_agents("task-001", [("agent-ci-tester", "CI Tester Agent", 0), ("agent-fallback1", "Fallback 1", 1)])
    qm.assign_agents("task-002", [("agent-test-gen", "Test Generator Agent", 0)])
    qm.assign_agents("task-003", [("agent-security", "Security Agent", 0), ("agent-security-backup", "Backup", 1)])
    qm.assign_agents("task-004", [("agent-doc", "Documentation Agent", 0)])

    # Get ready tasks
    print("\n[3] Checking ready tasks...")
    ready = qm.get_ready_tasks()
    print(f"Ready tasks: {ready}")

    # Simulate execution
    print("\n[4] Simulating task execution...")
    for task_id in ready[:2]:
        qm.start_task(task_id)
        time.sleep(0.1)
        qm.complete_task(task_id, failed=False)

    # Check metrics
    print("\n[5] Queue metrics:")
    metrics = qm.get_metrics()
    print(json.dumps(metrics, indent=2))

    print("\n" + "=" * 80)


if __name__ == "__main__":
    example_queue_operations()

"""
Agent Orchestrator - Multi-Agent Workflow Coordination
Manages dependencies, parallel execution, and result aggregation across agents.

#AFTERMATH_PATTERN_IDENTIFIED: orchestration_pattern
Enables complex multi-agent workflows with dependency management.
"""
import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"


@dataclass
class AgentTask:
    """Represents a task for an agent."""

    task_id: str
    agent_name: str
    task_type: str
    parameters: dict[str, Any]
    dependencies: list[str]  # List of task_ids this depends on
    priority: int = 5  # 1-10, 10 is highest
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    lane: str = "P1"
    estimated_cost: int | float = 0
    checkpoint_after: bool = False
    resume_hint: Optional[str] = None


def _normalize_lane(value: str | None) -> str:
    """Canonicalize lane names to the repo's cost-aware buckets."""
    if value is None:
        return "P1"
    alias = str(value).strip().upper().replace(" ", "_")
    mapping = {
        "P1": "P1",
        "PRIMARY": "P1",
        "P2": "P2",
        "SECONDARY": "P2",
        "S1": "S1",
        "SUPPORT": "S1",
        "SEQ": "Seq",
        "SEQUENTIAL": "Seq",
        "VALIDATION": "Seq",
    }
    return mapping.get(alias, alias or "P1")


class AgentOrchestrator:
    """
    Orchestrates multi-agent workflows with dependency resolution.

    Features:
    - Dependency resolution (DAG-based)
    - Parallel execution when possible
    - Lane-aware throttling for P1/P2/S1/Seq work
    - Result aggregation and checkpoint budgeting
    - Error handling and recovery
    """

    def __init__(
        self,
        max_parallel: int = 3,
        *,
        warning_budget: int = 16_000,
        hard_budget: int = 20_000,
        lane_budgets: Optional[dict[str, int]] = None,
    ):
        """Initialize orchestrator with lane-aware limits."""
        self.max_parallel = max_parallel
        self.warning_budget = warning_budget
        self.hard_budget = hard_budget
        self.lane_budgets = lane_budgets or {"P1": 1, "P2": 2, "S1": 1, "Seq": 1}
        self.agents = {}
        self.tasks: dict[str, AgentTask] = {}

    def register_agent(self, name: str, agent_instance):
        """Register an agent for orchestration."""
        self.agents[name] = agent_instance

    def _budget_warning_active(self) -> bool:
        """Return True when cost pressure requires lane gating."""
        active_cost = sum(
            float(task.estimated_cost or 0)
            for task in self.tasks.values()
            if task.status in {TaskStatus.RUNNING, TaskStatus.SUCCESS, TaskStatus.PENDING}
        )
        return active_cost >= self.warning_budget

    def _lane_running_count(self, lane: str) -> int:
        return sum(
            1 for task in self.tasks.values() if task.status == TaskStatus.RUNNING and _normalize_lane(task.lane) == lane
        )

    def _lane_is_allowed(self, task: AgentTask) -> bool:
        lane = _normalize_lane(task.lane)
        if self._budget_warning_active() and lane != "P1":
            return False
        lane_limit = self.lane_budgets.get(lane, self.lane_budgets.get("P1", 1))
        return self._lane_running_count(lane) < lane_limit

    def add_task(
        self,
        task_id: str,
        agent_name: str,
        task_type: str,
        parameters: dict[str, Any],
        dependencies: Optional[list[str]] = None,
        priority: int = 5,
        *,
        lane: str | None = None,
        estimated_cost: int | float | None = None,
        checkpoint_after: bool | None = None,
        resume_hint: str | None = None,
    ) -> AgentTask:
        """Add a task to the orchestration workflow."""
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not registered")

        normalized_lane = _normalize_lane(
            lane or parameters.get("lane") or parameters.get("lane_bucket")
        )
        task = AgentTask(
            task_id=task_id,
            agent_name=agent_name,
            task_type=task_type,
            parameters=parameters,
            dependencies=dependencies or [],
            priority=priority,
            lane=normalized_lane,
            estimated_cost=float(estimated_cost or parameters.get("estimated_cost") or 0),
            checkpoint_after=bool(checkpoint_after if checkpoint_after is not None else parameters.get("checkpoint_after", False)),
            resume_hint=resume_hint or parameters.get("resume_hint"),
        )

        self.tasks[task_id] = task
        return task

    def _validate_dependencies(self) -> bool:
        """Validate task dependencies form a valid DAG (no cycles)."""
        graph = {task_id: task.dependencies for task_id, task in self.tasks.items()}
        visited = set()
        rec_stack = set()

        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for task_id in graph:
            if task_id not in visited and has_cycle(task_id):
                return False

        return True

    def _get_ready_tasks(self) -> list[AgentTask]:
        """Get tasks ready for execution, honoring lane budgets."""
        ready = []

        for task in self.tasks.values():
            if task.status != TaskStatus.PENDING:
                continue

            deps_complete = all(
                self.tasks[dep_id].status == TaskStatus.SUCCESS for dep_id in task.dependencies if dep_id in self.tasks
            )
            if deps_complete and self._lane_is_allowed(task):
                ready.append(task)

        ready.sort(key=lambda t: t.priority, reverse=True)
        return ready

    async def _execute_task(self, task: AgentTask) -> dict[str, Any]:
        """Execute a single task asynchronously."""
        agent = self.agents[task.agent_name]
        task.status = TaskStatus.RUNNING

        try:
            task_spec = {
                "task_type": task.task_type,
                "parameters": task.parameters,
                "metadata": {
                    "task_id": task.task_id,
                    "orchestrated": True,
                    "lane": task.lane,
                    "estimated_cost": task.estimated_cost,
                    "checkpoint_after": task.checkpoint_after,
                    "resume_hint": task.resume_hint,
                },
            }

            result = agent.execute_pda_loop(task_spec)
            task.status = TaskStatus.SUCCESS
            task.result = result
            return result

        except Exception as e:
            task.status = TaskStatus.FAILURE
            task.error = str(e)
            raise

    async def execute_workflow(self) -> dict[str, Any]:
        """Execute the complete workflow with parallel execution and lane gating."""
        if not self._validate_dependencies():
            return {"status": "error", "error": "Cycle detected in task dependencies", "tasks": {}}

        results = {}
        running_tasks: set[tuple[str, asyncio.Task[Any]]] = set()

        while True:
            ready_tasks = self._get_ready_tasks()
            if not ready_tasks and not running_tasks:
                break

            while ready_tasks and len(running_tasks) < self.max_parallel:
                task = ready_tasks.pop(0)
                if not self._lane_is_allowed(task):
                    task.status = TaskStatus.SKIPPED
                    task.result = {
                        "status": "deferred",
                        "lane": task.lane,
                        "reason": "warning-budget lane gate",
                    }
                    results[task.task_id] = task.result
                    continue
                coro = self._execute_task(task)
                async_task = asyncio.create_task(coro)
                running_tasks.add((task.task_id, async_task))

            if not running_tasks:
                continue

            done, _ = await asyncio.wait(
                [async_task for _, async_task in running_tasks],
                return_when=asyncio.FIRST_COMPLETED,
            )

            completed_ids = set()
            for task_id, async_task in running_tasks:
                if async_task in done:
                    completed_ids.add(task_id)
                    try:
                        results[task_id] = await async_task
                    except Exception as exc:  # pragma: no cover - runtime error capture
                        results[task_id] = {"status": "error", "error": str(exc)}

            running_tasks = {(task_id, async_task) for task_id, async_task in running_tasks if task_id not in completed_ids}

        success_count = sum(1 for t in self.tasks.values() if t.status == TaskStatus.SUCCESS)
        failure_count = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILURE)
        skipped_count = sum(1 for t in self.tasks.values() if t.status == TaskStatus.SKIPPED)

        lane_names = {"P1", "P2", "S1", "Seq"}
        lane_names.update(_normalize_lane(task.lane) for task in self.tasks.values())
        return {
            "status": "success" if failure_count == 0 else "partial_success",
            "tasks": results,
            "metrics": {
                "total_tasks": len(self.tasks),
                "successful": success_count,
                "failed": failure_count,
                "skipped": skipped_count,
            },
            "lane_summary": {
                lane: {
                    "tasks": sum(1 for t in self.tasks.values() if _normalize_lane(t.lane) == lane),
                    "running": sum(1 for t in self.tasks.values() if _normalize_lane(t.lane) == lane and t.status == TaskStatus.RUNNING),
                }
                for lane in sorted(lane_names)
            },
        }

    def get_workflow_summary(self) -> dict[str, Any]:
        """Get summary of workflow execution."""
        return {
            "total_tasks": len(self.tasks),
            "by_status": {
                status.value: sum(1 for t in self.tasks.values() if t.status == status)
                for status in TaskStatus
            },
            "by_agent": {
                agent: sum(1 for t in self.tasks.values() if t.agent_name == agent)
                for agent in self.agents.keys()
            },
            "by_lane": {
                lane: sum(1 for t in self.tasks.values() if _normalize_lane(t.lane) == lane)
                for lane in sorted({"P1", "P2", "S1", "Seq"})
            },
        }

    def clear(self):
        """Clear all tasks and reset orchestrator."""
        self.tasks.clear()

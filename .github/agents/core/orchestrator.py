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


class AgentOrchestrator:
    """
    Orchestrates multi-agent workflows with dependency resolution.

    Features:
    - Dependency resolution (DAG-based)
    - Parallel execution when possible
    - Result aggregation
    - Error handling and recovery
    """

    def __init__(self, max_parallel: int = 3):
        """
        Initialize orchestrator.

        Args:
            max_parallel: Maximum parallel agent executions
        """
        self.max_parallel = max_parallel
        self.agents = {}
        self.tasks: dict[str, AgentTask] = {}

    def register_agent(self, name: str, agent_instance):
        """
        Register an agent for orchestration.

        Args:
            name: Agent name
            agent_instance: CognitiveAgent instance
        """
        self.agents[name] = agent_instance

    def add_task(
        self,
        task_id: str,
        agent_name: str,
        task_type: str,
        parameters: dict[str, Any],
        dependencies: Optional[list[str]] = None,
        priority: int = 5
    ) -> AgentTask:
        """
        Add a task to the orchestration workflow.

        Args:
            task_id: Unique task identifier
            agent_name: Name of agent to execute task
            task_type: Type of task
            parameters: Task parameters
            dependencies: List of task IDs this depends on
            priority: Task priority (1-10)

        Returns:
            AgentTask instance
        """
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' not registered")

        task = AgentTask(
            task_id=task_id,
            agent_name=agent_name,
            task_type=task_type,
            parameters=parameters,
            dependencies=dependencies or [],
            priority=priority
        )

        self.tasks[task_id] = task
        return task

    def _validate_dependencies(self) -> bool:
        """
        Validate task dependencies form a valid DAG (no cycles).

        Returns:
            True if valid, False if cycle detected
        """
        # Build adjacency list
        graph = {task_id: task.dependencies for task_id, task in self.tasks.items()}

        # Check for cycles using DFS
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
            if task_id not in visited:
                if has_cycle(task_id):
                    return False

        return True

    def _get_ready_tasks(self) -> list[AgentTask]:
        """
        Get tasks ready for execution (all dependencies completed).

        Returns:
            List of ready tasks sorted by priority
        """
        ready = []

        for task in self.tasks.values():
            if task.status != TaskStatus.PENDING:
                continue

            # Check if all dependencies are completed
            deps_complete = all(
                self.tasks[dep_id].status == TaskStatus.SUCCESS
                for dep_id in task.dependencies
                if dep_id in self.tasks
            )

            if deps_complete:
                ready.append(task)

        # Sort by priority (highest first)
        ready.sort(key=lambda t: t.priority, reverse=True)
        return ready

    async def _execute_task(self, task: AgentTask) -> dict[str, Any]:
        """
        Execute a single task asynchronously.

        Args:
            task: Task to execute

        Returns:
            Task result
        """
        agent = self.agents[task.agent_name]
        task.status = TaskStatus.RUNNING

        try:
            # Build task specification for agent
            task_spec = {
                "task_type": task.task_type,
                "parameters": task.parameters,
                "metadata": {
                    "task_id": task.task_id,
                    "orchestrated": True
                }
            }

            # Execute PDA loop
            result = agent.execute_pda_loop(task_spec)

            task.status = TaskStatus.SUCCESS
            task.result = result
            return result

        except Exception as e:
            task.status = TaskStatus.FAILURE
            task.error = str(e)
            raise

    async def execute_workflow(self) -> dict[str, Any]:
        """
        Execute the complete workflow with parallel execution.

        Returns:
            Dictionary with:
                - status: Overall workflow status
                - tasks: Dictionary of task results
                - metrics: Execution metrics

        #AFTERMATH_METRIC: workflow_execution
        """
        # Validate dependencies
        if not self._validate_dependencies():
            return {
                "status": "error",
                "error": "Cycle detected in task dependencies",
                "tasks": {}
            }

        results = {}
        running_tasks = set()

        while True:
            # Get tasks ready for execution
            ready_tasks = self._get_ready_tasks()

            # Check if workflow is complete
            if not ready_tasks and not running_tasks:
                break

            # Start new tasks up to max_parallel
            while ready_tasks and len(running_tasks) < self.max_parallel:
                task = ready_tasks.pop(0)

                # Create and start async task
                coro = self._execute_task(task)
                async_task = asyncio.create_task(coro)
                running_tasks.add((task.task_id, async_task))

            # Wait for at least one task to complete
            if running_tasks:
                done, pending = await asyncio.wait(
                    [t[1] for t in running_tasks],
                    return_when=asyncio.FIRST_COMPLETED
                )

                # Update running_tasks
                completed_ids = set()
                for task_id, async_task in running_tasks:
                    if async_task in done:
                        completed_ids.add(task_id)
                        try:
                            results[task_id] = await async_task
                        except Exception as e:
                            results[task_id] = {"status": "error", "error": str(e)}

                running_tasks = {(tid, t) for tid, t in running_tasks if tid not in completed_ids}

        # Calculate metrics
        success_count = sum(1 for t in self.tasks.values() if t.status == TaskStatus.SUCCESS)
        failure_count = sum(1 for t in self.tasks.values() if t.status == TaskStatus.FAILURE)

        return {
            "status": "success" if failure_count == 0 else "partial_success",
            "tasks": results,
            "metrics": {
                "total_tasks": len(self.tasks),
                "successful": success_count,
                "failed": failure_count,
                "skipped": len(self.tasks) - success_count - failure_count
            }
        }

    def get_workflow_summary(self) -> dict[str, Any]:
        """
        Get summary of workflow execution.

        Returns:
            Summary dictionary
        """
        return {
            "total_tasks": len(self.tasks),
            "by_status": {
                status.value: sum(1 for t in self.tasks.values() if t.status == status)
                for status in TaskStatus
            },
            "by_agent": {
                agent: sum(1 for t in self.tasks.values() if t.agent_name == agent)
                for agent in self.agents.keys()
            }
        }

    def clear(self):
        """Clear all tasks and reset orchestrator."""
        self.tasks.clear()

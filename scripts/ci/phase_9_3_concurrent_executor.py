#!/usr/bin/env python3
"""
PHASE 9.3: Concurrent Execution Coordinator
============================================

Orchestrates parallel execution of 3-5 agents with dependency tracking,
task bundling, and timeout management.

Author: @mbaetiong
Status: Production
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import networkx as nx

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class DependencyType(Enum):
    """Dependency relationship type"""
    SEQUENTIAL = "sequential"      # B waits for A
    PARALLEL = "parallel"          # A, B, C execute together
    AGGREGATION = "aggregation"    # D waits for (A AND B AND C)


@dataclass
class TaskMetadata:
    """Task metadata and configuration"""
    id: str
    name: str
    task_type: str
    category: str
    timeout_s: int = 600
    priority: int = 5  # 1-10, higher = more important
    estimated_duration_s: Optional[float] = None
    retry_count: int = 3
    max_parallel_agents: int = 5
    required_capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SubTask:
    """Sub-task in a task decomposition"""
    id: str
    parent_task_id: str
    name: str
    agent_id: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    attempt: int = 0
    max_retries: int = 3


@dataclass
class ExecutionResult:
    """Result of task execution"""
    task_id: str
    status: TaskStatus
    subtask_results: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    aggregated_result: Optional[Dict[str, Any]] = None
    total_duration_s: float = 0.0
    parallel_agents_count: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    execution_log: List[str] = field(default_factory=list)


class DependencyGraph:
    """Manages task dependency graph"""

    def __init__(self, task_id: str):
        self.task_id = task_id
        self.graph = nx.DiGraph()
        self.subtask_map: Dict[str, SubTask] = {}

    def add_subtask(self, subtask: SubTask) -> None:
        """Add a sub-task to the graph"""
        self.graph.add_node(subtask.id)
        self.subtask_map[subtask.id] = subtask

    def add_dependency(
        self,
        source_id: str,
        target_id: str,
        dep_type: DependencyType
    ) -> None:
        """Add a dependency relationship"""
        self.graph.add_edge(source_id, target_id, type=dep_type)

    def validate_dag(self) -> Tuple[bool, Optional[str]]:
        """Validate that the graph is a DAG (no cycles)"""
        if not nx.is_directed_acyclic_graph(self.graph):
            cycles = list(nx.simple_cycles(self.graph))
            return False, f"Circular dependencies detected: {cycles}"
        return True, None

    def get_execution_layers(self) -> List[List[str]]:
        """
        Partition sub-tasks into execution layers.
        Each layer contains independent tasks that can run in parallel.
        """
        try:
            layers = list(nx.algorithms.dag.topological_generations(self.graph))
            return [list(layer) for layer in layers]
        except nx.NetworkXError as e:
            logger.error(f"Failed to compute topological order: {e}")
            return []

    def get_dependencies(self, subtask_id: str) -> List[str]:
        """Get all dependencies for a subtask"""
        return list(self.graph.predecessors(subtask_id))


class TaskDecomposer:
    """Decomposes root tasks into independent sub-tasks"""

    @staticmethod
    def decompose(
        task: TaskMetadata,
        agent_routing: Dict[str, str]
    ) -> Tuple[List[SubTask], DependencyGraph]:
        """
        Decompose a root task into sub-tasks based on task characteristics.

        Args:
            task: Root task metadata
            agent_routing: Dict mapping sub-task IDs to agent IDs

        Returns:
            (sub_tasks, dependency_graph)
        """
        subtasks = []
        graph = DependencyGraph(task.id)

        # Decomposition strategy depends on task type
        if task.task_type == "ci_failure_analysis":
            subtasks = TaskDecomposer._decompose_ci_failure(task, agent_routing)
        elif task.task_type == "coverage_improvement":
            subtasks = TaskDecomposer._decompose_coverage(task, agent_routing)
        elif task.task_type == "security_audit":
            subtasks = TaskDecomposer._decompose_security(task, agent_routing)
        else:
            # Default: single subtask
            subtasks = [
                SubTask(
                    id=f"{task.id}-subtask-0",
                    parent_task_id=task.id,
                    name=f"{task.name} (unified)",
                    agent_id=agent_routing.get(f"{task.id}-subtask-0")
                )
            ]

        # Add subtasks to graph
        for subtask in subtasks:
            graph.add_subtask(subtask)

        # Add dependencies based on subtask list order
        for i in range(1, len(subtasks)):
            if "aggregation" in subtasks[i].metadata.get("depends_on", []):
                # Aggregation task depends on all previous tasks
                for j in range(i):
                    graph.add_dependency(
                        subtasks[j].id,
                        subtasks[i].id,
                        DependencyType.AGGREGATION
                    )
            else:
                # Default: sequential
                graph.add_dependency(
                    subtasks[i-1].id,
                    subtasks[i].id,
                    DependencyType.SEQUENTIAL
                )

        return subtasks, graph

    @staticmethod
    def _decompose_ci_failure(
        task: TaskMetadata,
        agent_routing: Dict[str, str]
    ) -> List[SubTask]:
        """Decompose CI failure analysis task"""
        subtasks = []

        # Subtask 1: Initial diagnostics (fast, required by others)
        subtasks.append(SubTask(
            id=f"{task.id}-diagnose",
            parent_task_id=task.id,
            name="CI Failure Diagnostics",
            agent_id=agent_routing.get(f"{task.id}-diagnose"),
            timeout_s=300
        ))

        # Subtask 2: Log analysis (parallel with other analysis)
        subtasks.append(SubTask(
            id=f"{task.id}-logs",
            parent_task_id=task.id,
            name="Log Analysis",
            agent_id=agent_routing.get(f"{task.id}-logs"),
            timeout_s=240
        ))

        # Subtask 3: Test collection analysis (parallel)
        subtasks.append(SubTask(
            id=f"{task.id}-tests",
            parent_task_id=task.id,
            name="Test Analysis",
            agent_id=agent_routing.get(f"{task.id}-tests"),
            timeout_s=240
        ))

        # Subtask 4: Result aggregation (depends on all above)
        subtasks.append(SubTask(
            id=f"{task.id}-aggregate",
            parent_task_id=task.id,
            name="Result Aggregation",
            agent_id=agent_routing.get(f"{task.id}-aggregate"),
            dependencies=[s.id for s in subtasks],
            timeout_s=120
        ))

        return subtasks

    @staticmethod
    def _decompose_coverage(
        task: TaskMetadata,
        agent_routing: Dict[str, str]
    ) -> List[SubTask]:
        """Decompose coverage improvement task"""
        subtasks = []

        # Subtask 1: Coverage analysis
        subtasks.append(SubTask(
            id=f"{task.id}-analyze",
            parent_task_id=task.id,
            name="Coverage Analysis",
            agent_id=agent_routing.get(f"{task.id}-analyze"),
            timeout_s=300
        ))

        # Subtask 2: Gap identification
        subtasks.append(SubTask(
            id=f"{task.id}-gaps",
            parent_task_id=task.id,
            name="Gap Identification",
            agent_id=agent_routing.get(f"{task.id}-gaps"),
            dependencies=[f"{task.id}-analyze"],
            timeout_s=240
        ))

        # Subtask 3: Test generation
        subtasks.append(SubTask(
            id=f"{task.id}-generate",
            parent_task_id=task.id,
            name="Test Generation",
            agent_id=agent_routing.get(f"{task.id}-generate"),
            dependencies=[f"{task.id}-gaps"],
            timeout_s=480
        ))

        return subtasks

    @staticmethod
    def _decompose_security(
        task: TaskMetadata,
        agent_routing: Dict[str, str]
    ) -> List[SubTask]:
        """Decompose security audit task"""
        subtasks = []

        # Subtask 1: SAST scanning
        subtasks.append(SubTask(
            id=f"{task.id}-sast",
            parent_task_id=task.id,
            name="SAST Scanning",
            agent_id=agent_routing.get(f"{task.id}-sast"),
            timeout_s=300
        ))

        # Subtask 2: Dependency scanning (parallel)
        subtasks.append(SubTask(
            id=f"{task.id}-deps",
            parent_task_id=task.id,
            name="Dependency Scanning",
            agent_id=agent_routing.get(f"{task.id}-deps"),
            timeout_s=240
        ))

        # Subtask 3: Secrets detection (parallel)
        subtasks.append(SubTask(
            id=f"{task.id}-secrets",
            parent_task_id=task.id,
            name="Secrets Detection",
            agent_id=agent_routing.get(f"{task.id}-secrets"),
            timeout_s=240
        ))

        # Subtask 4: Result aggregation
        subtasks.append(SubTask(
            id=f"{task.id}-aggregate",
            parent_task_id=task.id,
            name="Result Aggregation",
            agent_id=agent_routing.get(f"{task.id}-aggregate"),
            dependencies=[s.id for s in subtasks[:-1]],
            timeout_s=120
        ))

        return subtasks


class ConcurrentExecutor:
    """Executes tasks concurrently with dependency tracking"""

    def __init__(
        self,
        max_concurrent_agents: int = 5,
        global_timeout_s: int = 900,
        agent_dispatcher_fn: Optional[Any] = None
    ):
        self.max_concurrent_agents = max_concurrent_agents
        self.global_timeout_s = global_timeout_s
        self.agent_dispatcher_fn = agent_dispatcher_fn or self._mock_dispatch
        self.execution_results: Dict[str, ExecutionResult] = {}
        self.subtask_results: Dict[str, SubTask] = {}

    async def execute(
        self,
        task: TaskMetadata,
        agent_routing: Dict[str, str]
    ) -> ExecutionResult:
        """
        Execute a task with concurrent agents.

        Args:
            task: Root task to execute
            agent_routing: Mapping of sub-task IDs to agent IDs

        Returns:
            ExecutionResult with outcomes
        """
        start_time = time.time()
        execution_log = []

        try:
            # Decompose task into sub-tasks
            subtasks, dep_graph = TaskDecomposer.decompose(task, agent_routing)
            execution_log.append(f"Decomposed task into {len(subtasks)} sub-tasks")

            # Validate DAG
            is_dag, error_msg = dep_graph.validate_dag()
            if not is_dag:
                execution_log.append(f"ERROR: {error_msg}")
                return ExecutionResult(
                    task_id=task.id,
                    status=TaskStatus.FAILED,
                    errors=[error_msg],
                    execution_log=execution_log
                )

            # Get execution layers
            layers = dep_graph.get_execution_layers()
            execution_log.append(f"Execution plan: {len(layers)} layers")

            # Execute layers sequentially
            for layer_idx, layer in enumerate(layers):
                execution_log.append(f"Executing layer {layer_idx + 1}/{len(layers)} ({len(layer)} tasks)")

                # Execute tasks in this layer in parallel
                layer_results = await self._execute_layer(
                    layer,
                    dep_graph.subtask_map,
                    task.timeout_s
                )

                # Check for failures
                failed_tasks = [
                    task_id for task_id, result in layer_results.items()
                    if result.status in (TaskStatus.FAILED, TaskStatus.TIMEOUT)
                ]

                if failed_tasks:
                    execution_log.append(f"⚠️  {len(failed_tasks)} task(s) failed in layer {layer_idx + 1}")

            # Check global timeout
            elapsed = time.time() - start_time
            if elapsed > self.global_timeout_s:
                execution_log.append(f"Global timeout exceeded: {elapsed:.1f}s > {self.global_timeout_s}s")
                return ExecutionResult(
                    task_id=task.id,
                    status=TaskStatus.TIMEOUT,
                    total_duration_s=elapsed,
                    errors=["Global execution timeout"],
                    execution_log=execution_log
                )

            # Aggregate results
            aggregated = self._aggregate_results(
                [self.subtask_results[st.id] for st in subtasks]
            )

            elapsed = time.time() - start_time
            execution_log.append(f"✅ Task completed in {elapsed:.1f}s")

            return ExecutionResult(
                task_id=task.id,
                status=TaskStatus.COMPLETED,
                subtask_results={id: asdict(st) for id, st in self.subtask_results.items()},
                aggregated_result=aggregated,
                total_duration_s=elapsed,
                parallel_agents_count=len({st.agent_id for st in subtasks if st.agent_id}),
                execution_log=execution_log
            )

        except Exception as e:
            execution_log.append(f"ERROR: {str(e)}")
            logger.error(f"Task execution failed: {e}", exc_info=True)
            return ExecutionResult(
                task_id=task.id,
                status=TaskStatus.FAILED,
                errors=[str(e)],
                execution_log=execution_log
            )

    async def _execute_layer(
        self,
        task_ids: List[str],
        subtask_map: Dict[str, SubTask],
        timeout_s: int
    ) -> Dict[str, SubTask]:
        """Execute a layer of tasks in parallel"""
        tasks = [
            self._execute_subtask(subtask_map[task_id], timeout_s)
            for task_id in task_ids
            if task_id in subtask_map
        ]

        # Execute in parallel with timeout
        results = await asyncio.wait_for(
            asyncio.gather(*tasks, return_exceptions=True),
            timeout=timeout_s + 10  # 10s buffer for cleanup
        )

        return {
            task_id: result
            for task_id, result in zip(task_ids, results)
            if not isinstance(result, Exception)
        }

    async def _execute_subtask(
        self,
        subtask: SubTask,
        timeout_s: int
    ) -> SubTask:
        """Execute a single sub-task"""
        subtask.status = TaskStatus.RUNNING
        subtask.started_at = datetime.utcnow()
        subtask.attempt += 1

        try:
            # Dispatch to agent
            result = await asyncio.wait_for(
                self._dispatch_to_agent(subtask),
                timeout=subtask.timeout_s
            )
            subtask.result = result
            subtask.status = TaskStatus.COMPLETED
            subtask.completed_at = datetime.utcnow()

        except asyncio.TimeoutError:
            subtask.status = TaskStatus.TIMEOUT
            subtask.error = f"Task timeout after {subtask.timeout_s}s"
            subtask.completed_at = datetime.utcnow()

            # Retry if attempts remaining
            if subtask.attempt < subtask.max_retries:
                logger.warning(f"Retrying {subtask.id} (attempt {subtask.attempt}/{subtask.max_retries})")
                return await self._execute_subtask(subtask, timeout_s)

        except Exception as e:
            subtask.status = TaskStatus.FAILED
            subtask.error = str(e)
            subtask.completed_at = datetime.utcnow()
            logger.error(f"Sub-task {subtask.id} failed: {e}")

        # Store result
        self.subtask_results[subtask.id] = subtask
        return subtask

    async def _dispatch_to_agent(self, subtask: SubTask) -> Dict[str, Any]:
        """Dispatch subtask to agent (async wrapper)"""
        return await asyncio.to_thread(
            self.agent_dispatcher_fn,
            subtask
        )

    async def _mock_dispatch(self, subtask: SubTask) -> Dict[str, Any]:
        """Mock agent dispatch (for testing)"""
        # Simulate agent work
        await asyncio.sleep(0.1)
        return {"status": "completed", "duration_s": 0.1}

    @staticmethod
    def _aggregate_results(subtasks: List[SubTask]) -> Dict[str, Any]:
        """Aggregate results from all sub-tasks"""
        return {
            "total_subtasks": len(subtasks),
            "completed": sum(1 for st in subtasks if st.status == TaskStatus.COMPLETED),
            "failed": sum(1 for st in subtasks if st.status == TaskStatus.FAILED),
            "timeout": sum(1 for st in subtasks if st.status == TaskStatus.TIMEOUT),
            "results": {
                st.id: st.result
                for st in subtasks
                if st.result is not None
            },
            "errors": {
                st.id: st.error
                for st in subtasks
                if st.error is not None
            }
        }


def main():
    """Main entry point for testing"""

    # Create test task
    task = TaskMetadata(
        id="test-task-001",
        name="Test CI Failure Analysis",
        task_type="ci_failure_analysis",
        category="ci_cd",
        timeout_s=600
    )

    # Create agent routing
    routing = {
        "test-task-001-diagnose": "ci-testing-agent",
        "test-task-001-logs": "ci-log-retrieval-agent",
        "test-task-001-tests": "autonomous-test-healer-agent",
        "test-task-001-aggregate": "agent-orchestrator"
    }

    # Execute task
    executor = ConcurrentExecutor()
    result = asyncio.run(executor.execute(task, routing))

    # Print results
    print(json.dumps(asdict(result), indent=2, default=str))

    return 0 if result.status == TaskStatus.COMPLETED else 1


if __name__ == "__main__":
    exit(main())

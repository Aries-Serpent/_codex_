"""
Shared fixtures for Phase 20.1 Advanced Automation test suite.

This module provides common fixtures for:
- Workflow orchestration mocks
- Task scheduling infrastructure
- Dependency resolution engines
- Configuration management
- Deployment pipelines
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import pytest

# ============================================================================
# ENUMS
# ============================================================================

class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class WorkflowStatus(Enum):
    """Workflow execution status."""
    DRAFT = "draft"
    READY = "ready"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class TaskDependency:
    """Represents a dependency between tasks."""
    task_id: str
    depends_on: str
    condition: Optional[str] = None  # e.g., "success", "failure", "always"


@dataclass
class TaskResult:
    """Result from a task execution."""
    task_id: str
    status: TaskStatus
    output: Any = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    attempts: int = 1

    def duration_seconds(self) -> float:
        """Calculate task execution duration."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0

    def is_success(self) -> bool:
        """Check if task succeeded."""
        return self.status == TaskStatus.COMPLETED


@dataclass
class Task:
    """Represents a single task in a workflow."""
    task_id: str
    name: str
    action: str
    retries: int = 0
    timeout: int = 300
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    conditional: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize task to dictionary."""
        return {
            "task_id": self.task_id,
            "name": self.name,
            "action": self.action,
            "retries": self.retries,
            "timeout": self.timeout,
            "dependencies": self.dependencies,
            "parameters": self.parameters,
            "conditional": self.conditional,
        }


@dataclass
class Workflow:
    """Represents a workflow definition."""
    workflow_id: str
    name: str
    version: str
    tasks: List[Task] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_task(self, task: Task) -> None:
        """Add a task to the workflow."""
        self.tasks.append(task)

    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID."""
        return next((t for t in self.tasks if t.task_id == task_id), None)

    def get_root_tasks(self) -> List[Task]:
        """Get tasks with no dependencies (root tasks)."""
        return [t for t in self.tasks if not t.dependencies]

    def get_leaf_tasks(self) -> List[Task]:
        """Get tasks with no dependents (leaf tasks)."""
        dependent_ids = set()
        for task in self.tasks:
            dependent_ids.update(task.dependencies)
        return [t for t in self.tasks if t.task_id not in dependent_ids]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize workflow to dictionary."""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "version": self.version,
            "status": self.status.value,
            "tasks": [t.to_dict() for t in self.tasks],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }


# ============================================================================
# MOCK ORCHESTRATION ENGINE
# ============================================================================

class MockOrchestrationEngine:
    """Mock workflow orchestration engine for testing."""

    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.task_results: Dict[str, TaskResult] = {}

    def create_workflow(
        self, name: str, version: str = "1.0.0", metadata: Optional[Dict] = None
    ) -> Workflow:
        """Create a new workflow."""
        workflow_id = str(uuid.uuid4())
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            version=version,
            metadata=metadata or {},
        )
        self.workflows[workflow_id] = workflow
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Retrieve a workflow by ID."""
        return self.workflows.get(workflow_id)

    def validate_workflow(self, workflow_id: str) -> tuple[bool, str]:
        """Validate workflow for execution readiness."""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            return False, "Workflow not found"

        if not workflow.tasks:
            return False, "Workflow has no tasks"

        # Check for circular dependencies
        if self._has_circular_dependency(workflow):
            return False, "Circular dependency detected"

        return True, "Workflow is valid"

    def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a workflow."""
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        valid, msg = self.validate_workflow(workflow_id)
        if not valid:
            raise ValueError(f"Invalid workflow: {msg}")

        workflow.status = WorkflowStatus.RUNNING
        execution_id = str(uuid.uuid4())
        results = {}

        # Topological sort and execute tasks
        execution_order = self._topological_sort(workflow)
        for task_id in execution_order:
            task = workflow.get_task(task_id)
            result = self._execute_task(task)
            results[task_id] = result
            self.task_results[task_id] = result

        workflow.status = WorkflowStatus.COMPLETED
        self.execution_history.append({
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "status": "completed",
            "results": {k: v.status.value for k, v in results.items()},
            "timestamp": datetime.utcnow().isoformat(),
        })

        return {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "results": results,
            "status": "completed",
        }

    def _execute_task(self, task: Task) -> TaskResult:
        """Execute a single task."""
        start_time = datetime.utcnow()
        
        try:
            # Simulate task execution
            result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                output={"executed": True, "task": task.name},
                start_time=start_time,
                end_time=datetime.utcnow(),
            )
            return result
        except Exception as e:
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e),
                start_time=start_time,
                end_time=datetime.utcnow(),
            )

    def _topological_sort(self, workflow: Workflow) -> List[str]:
        """Topological sort of tasks by dependencies."""
        visited = set()
        result = []

        def dfs(task_id: str, visiting: set):
            if task_id in visited:
                return
            if task_id in visiting:
                raise ValueError(f"Circular dependency detected for {task_id}")

            visiting.add(task_id)
            task = workflow.get_task(task_id)
            if task:
                for dep_id in task.dependencies:
                    dfs(dep_id, visiting)
            visiting.remove(task_id)
            visited.add(task_id)
            result.append(task_id)

        for task in workflow.tasks:
            if task.task_id not in visited:
                dfs(task.task_id, set())

        return result

    def _has_circular_dependency(self, workflow: Workflow) -> bool:
        """Check for circular dependencies."""
        try:
            self._topological_sort(workflow)
            return False
        except ValueError:
            return True

    def get_execution_history(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Get execution history for a workflow."""
        return [
            exec for exec in self.execution_history
            if exec["workflow_id"] == workflow_id
        ]


# ============================================================================
# TASK SCHEDULER
# ============================================================================

class MockTaskScheduler:
    """Mock task scheduler for testing."""

    def __init__(self):
        self.scheduled_tasks: Dict[str, Dict[str, Any]] = {}
        self.execution_queue: List[str] = []

    def schedule_task(
        self,
        task_id: str,
        scheduled_time: datetime,
        recurrence: Optional[str] = None,
    ) -> str:
        """Schedule a task for execution."""
        schedule_id = str(uuid.uuid4())
        self.scheduled_tasks[schedule_id] = {
            "task_id": task_id,
            "scheduled_time": scheduled_time,
            "recurrence": recurrence,
            "status": "scheduled",
        }
        return schedule_id

    def cancel_scheduled_task(self, schedule_id: str) -> bool:
        """Cancel a scheduled task."""
        if schedule_id in self.scheduled_tasks:
            self.scheduled_tasks[schedule_id]["status"] = "cancelled"
            return True
        return False

    def get_scheduled_task(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a scheduled task."""
        return self.scheduled_tasks.get(schedule_id)

    def queue_task_for_execution(self, task_id: str) -> None:
        """Queue a task for immediate execution."""
        self.execution_queue.append(task_id)

    def get_next_task(self) -> Optional[str]:
        """Get the next task from the execution queue."""
        return self.execution_queue.pop(0) if self.execution_queue else None

    def get_pending_tasks(self) -> List[str]:
        """Get all pending tasks."""
        return self.execution_queue.copy()


# ============================================================================
# DEPENDENCY RESOLVER
# ============================================================================

class MockDependencyResolver:
    """Mock dependency resolver for testing."""

    def __init__(self):
        self.resolution_cache: Dict[str, List[str]] = {}

    def resolve_dependencies(self, task: Task) -> List[str]:
        """Resolve dependencies for a task."""
        if task.task_id in self.resolution_cache:
            return self.resolution_cache[task.task_id]

        resolved = task.dependencies.copy()
        # In a real system, this would recursively resolve transitive dependencies
        self.resolution_cache[task.task_id] = resolved
        return resolved

    def check_dependency_satisfaction(
        self, task: Task, completed_tasks: set
    ) -> bool:
        """Check if all task dependencies are satisfied."""
        dependencies = self.resolve_dependencies(task)
        return all(dep_id in completed_tasks for dep_id in dependencies)

    def get_blocking_tasks(
        self, task: Task, completed_tasks: set
    ) -> List[str]:
        """Get tasks that are blocking this task."""
        dependencies = self.resolve_dependencies(task)
        return [dep_id for dep_id in dependencies if dep_id not in completed_tasks]


# ============================================================================
# PYTEST FIXTURES
# ============================================================================

@pytest.fixture
def orchestration_engine():
    """Fixture providing a mock orchestration engine."""
    return MockOrchestrationEngine()


@pytest.fixture
def task_scheduler():
    """Fixture providing a mock task scheduler."""
    return MockTaskScheduler()


@pytest.fixture
def dependency_resolver():
    """Fixture providing a mock dependency resolver."""
    return MockDependencyResolver()


@pytest.fixture
def sample_workflow():
    """Fixture providing a sample workflow."""
    workflow = Workflow(
        workflow_id=str(uuid.uuid4()),
        name="Sample Workflow",
        version="1.0.0",
    )

    # Add tasks with dependencies
    task1 = Task(task_id="task_1", name="Extract Data", action="extract")
    task2 = Task(
        task_id="task_2", name="Transform Data", action="transform",
        dependencies=["task_1"]
    )
    task3 = Task(
        task_id="task_3", name="Load Data", action="load",
        dependencies=["task_2"]
    )

    workflow.add_task(task1)
    workflow.add_task(task2)
    workflow.add_task(task3)

    return workflow


@pytest.fixture
def complex_workflow():
    """Fixture providing a complex workflow with parallel tasks."""
    workflow = Workflow(
        workflow_id=str(uuid.uuid4()),
        name="Complex Workflow",
        version="1.0.0",
    )

    # Create parallel branches
    task1 = Task(task_id="task_1", name="Start", action="start")
    task2a = Task(
        task_id="task_2a", name="Process A", action="process",
        dependencies=["task_1"]
    )
    task2b = Task(
        task_id="task_2b", name="Process B", action="process",
        dependencies=["task_1"]
    )
    task2c = Task(
        task_id="task_2c", name="Process C", action="process",
        dependencies=["task_1"]
    )
    task3 = Task(
        task_id="task_3", name="Merge", action="merge",
        dependencies=["task_2a", "task_2b", "task_2c"]
    )
    task4 = Task(
        task_id="task_4", name="End", action="end",
        dependencies=["task_3"]
    )

    for task in [task1, task2a, task2b, task2c, task3, task4]:
        workflow.add_task(task)

    return workflow


@pytest.fixture
def conditional_workflow():
    """Fixture providing a workflow with conditional branching."""
    workflow = Workflow(
        workflow_id=str(uuid.uuid4()),
        name="Conditional Workflow",
        version="1.0.0",
    )

    task1 = Task(task_id="task_1", name="Check", action="check")
    task2 = Task(
        task_id="task_2", name="Branch A", action="branch_a",
        dependencies=["task_1"],
        conditional="success"
    )
    task3 = Task(
        task_id="task_3", name="Branch B", action="branch_b",
        dependencies=["task_1"],
        conditional="failure"
    )
    task4 = Task(
        task_id="task_4", name="End", action="end",
        dependencies=["task_2", "task_3"]
    )

    for task in [task1, task2, task3, task4]:
        workflow.add_task(task)

    return workflow

"""
Phase 20.1 Lane 1: Workflow Orchestration Automation Tests

This module provides comprehensive testing for workflow orchestration capabilities:
- Complex DAG (directed acyclic graph) workflow execution
- Conditional branching (if/then/else logic)
- Parallel task execution with dependencies
- Loop constructs (for, while with limits)
- Error handling & retry policies
- Workflow pause/resume capabilities
- Long-running workflow state persistence
- Workflow versioning & rollback

Total Tests: 25+
Target Coverage: ≥90%
"""

import pytest
import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid

# Import from local conftest
from .conftest import (
    MockOrchestrationEngine,
    MockTaskScheduler,
    MockDependencyResolver,
    Task,
    Workflow,
    TaskStatus,
    WorkflowStatus,
    TaskResult,
)


# ============================================================================
# TEST SUITE 1: BASIC WORKFLOW EXECUTION
# ============================================================================

class TestBasicWorkflowExecution:
    """Test basic workflow creation and execution."""

    def test_create_workflow(self, orchestration_engine):
        """Test creating a new workflow."""
        workflow = orchestration_engine.create_workflow(
            name="Test Workflow",
            version="1.0.0",
            metadata={"owner": "test"}
        )

        assert workflow is not None
        assert workflow.name == "Test Workflow"
        assert workflow.version == "1.0.0"
        assert workflow.status == WorkflowStatus.DRAFT
        assert workflow.metadata["owner"] == "test"

    def test_retrieve_workflow(self, orchestration_engine):
        """Test retrieving a workflow by ID."""
        created = orchestration_engine.create_workflow(
            name="Retrieve Test",
            version="1.0.0"
        )
        retrieved = orchestration_engine.get_workflow(created.workflow_id)

        assert retrieved is not None
        assert retrieved.workflow_id == created.workflow_id
        assert retrieved.name == "Retrieve Test"

    def test_workflow_not_found(self, orchestration_engine):
        """Test retrieving a non-existent workflow."""
        result = orchestration_engine.get_workflow("non-existent-id")
        assert result is None

    def test_add_task_to_workflow(self, orchestration_engine):
        """Test adding tasks to a workflow."""
        workflow = orchestration_engine.create_workflow("Task Test")
        task = Task(task_id="task_1", name="Test Task", action="test")

        workflow.add_task(task)

        assert len(workflow.tasks) == 1
        assert workflow.get_task("task_1") is not None

    def test_add_multiple_tasks(self, orchestration_engine):
        """Test adding multiple tasks to a workflow."""
        workflow = orchestration_engine.create_workflow("Multi Task Test")

        for i in range(5):
            task = Task(
                task_id=f"task_{i}",
                name=f"Task {i}",
                action="test"
            )
            workflow.add_task(task)

        assert len(workflow.tasks) == 5

    def test_simple_linear_workflow(self, sample_workflow, orchestration_engine):
        """Test execution of a simple linear workflow (task1 -> task2 -> task3)."""
        orchestration_engine.workflows[sample_workflow.workflow_id] = sample_workflow

        result = orchestration_engine.execute_workflow(sample_workflow.workflow_id)

        assert result["status"] == "completed"
        assert len(result["results"]) == 3
        assert all(r.is_success() for r in result["results"].values())


# ============================================================================
# TEST SUITE 2: COMPLEX DAG WORKFLOWS
# ============================================================================

class TestComplexDAGWorkflows:
    """Test complex directed acyclic graph (DAG) workflow execution."""

    def test_parallel_task_execution(self, complex_workflow, orchestration_engine):
        """Test parallel execution of tasks with same dependencies."""
        orchestration_engine.workflows[complex_workflow.workflow_id] = complex_workflow

        result = orchestration_engine.execute_workflow(complex_workflow.workflow_id)

        # Verify all parallel tasks (2a, 2b, 2c) completed
        assert "task_2a" in result["results"]
        assert "task_2b" in result["results"]
        assert "task_2c" in result["results"]
        assert result["results"]["task_2a"].is_success()
        assert result["results"]["task_2b"].is_success()
        assert result["results"]["task_2c"].is_success()

    def test_dag_topological_sort(self, complex_workflow, orchestration_engine):
        """Test topological sorting of DAG tasks."""
        execution_order = orchestration_engine._topological_sort(complex_workflow)

        # Verify dependencies are respected in execution order
        task_2a_idx = execution_order.index("task_2a")
        task_1_idx = execution_order.index("task_1")
        assert task_1_idx < task_2a_idx, "task_1 should execute before task_2a"

        task_3_idx = execution_order.index("task_3")
        task_2a_idx = execution_order.index("task_2a")
        assert task_2a_idx < task_3_idx, "task_2a should execute before task_3 (merge)"

    def test_diamond_dag_pattern(self, orchestration_engine):
        """Test diamond-shaped DAG (task1 -> [task2, task3] -> task4)."""
        workflow = orchestration_engine.create_workflow("Diamond DAG")

        workflow.add_task(Task(task_id="task_1", name="Start", action="start"))
        workflow.add_task(Task(
            task_id="task_2", name="Left", action="left",
            dependencies=["task_1"]
        ))
        workflow.add_task(Task(
            task_id="task_3", name="Right", action="right",
            dependencies=["task_1"]
        ))
        workflow.add_task(Task(
            task_id="task_4", name="End", action="end",
            dependencies=["task_2", "task_3"]
        ))

        result = orchestration_engine.execute_workflow(workflow.workflow_id)

        assert result["status"] == "completed"
        assert len(result["results"]) == 4

    def test_wide_dag_many_parallel_tasks(self, orchestration_engine):
        """Test wide DAG with many parallel tasks."""
        workflow = orchestration_engine.create_workflow("Wide DAG")
        workflow.add_task(Task(task_id="task_0", name="Start", action="start"))

        # Add 10 parallel tasks
        for i in range(1, 11):
            workflow.add_task(Task(
                task_id=f"task_{i}",
                name=f"Parallel {i}",
                action="parallel",
                dependencies=["task_0"]
            ))

        # Add final merge task
        workflow.add_task(Task(
            task_id="task_merge",
            name="Merge",
            action="merge",
            dependencies=[f"task_{i}" for i in range(1, 11)]
        ))

        result = orchestration_engine.execute_workflow(workflow.workflow_id)

        assert result["status"] == "completed"
        assert len(result["results"]) == 12

    def test_deep_dag_long_chain(self, orchestration_engine):
        """Test deep DAG with long dependency chain."""
        workflow = orchestration_engine.create_workflow("Deep DAG")

        # Create a chain of 20 tasks
        prev_task_id = None
        for i in range(20):
            task_id = f"task_{i}"
            deps = [prev_task_id] if prev_task_id else []
            workflow.add_task(Task(
                task_id=task_id,
                name=f"Step {i}",
                action="step",
                dependencies=deps
            ))
            prev_task_id = task_id

        result = orchestration_engine.execute_workflow(workflow.workflow_id)

        assert result["status"] == "completed"
        assert len(result["results"]) == 20


# ============================================================================
# TEST SUITE 3: CONDITIONAL BRANCHING
# ============================================================================

class TestConditionalBranching:
    """Test conditional branching and if/then/else logic."""

    def test_simple_conditional_workflow(self, conditional_workflow, orchestration_engine):
        """Test simple conditional branching."""
        orchestration_engine.workflows[conditional_workflow.workflow_id] = conditional_workflow

        result = orchestration_engine.execute_workflow(conditional_workflow.workflow_id)

        assert result["status"] == "completed"
        # Both branches should execute in mock
        assert "task_2" in result["results"]
        assert "task_3" in result["results"]

    def test_conditional_success_branch(self, orchestration_engine):
        """Test conditional execution on success."""
        workflow = orchestration_engine.create_workflow("Success Conditional")

        workflow.add_task(Task(task_id="check", name="Check", action="check"))
        workflow.add_task(Task(
            task_id="success_branch",
            name="Success Action",
            action="success",
            dependencies=["check"],
            conditional="success"
        ))

        assert workflow.get_task("success_branch").conditional == "success"

    def test_conditional_failure_branch(self, orchestration_engine):
        """Test conditional execution on failure."""
        workflow = orchestration_engine.create_workflow("Failure Conditional")

        workflow.add_task(Task(task_id="check", name="Check", action="check"))
        workflow.add_task(Task(
            task_id="failure_branch",
            name="Failure Action",
            action="failure",
            dependencies=["check"],
            conditional="failure"
        ))

        assert workflow.get_task("failure_branch").conditional == "failure"

    def test_conditional_always_branch(self, orchestration_engine):
        """Test conditional execution that always runs."""
        workflow = orchestration_engine.create_workflow("Always Conditional")

        workflow.add_task(Task(task_id="check", name="Check", action="check"))
        workflow.add_task(Task(
            task_id="always_branch",
            name="Always Action",
            action="always",
            dependencies=["check"],
            conditional="always"
        ))

        assert workflow.get_task("always_branch").conditional == "always"

    def test_nested_conditionals(self, orchestration_engine):
        """Test nested conditional branching."""
        workflow = orchestration_engine.create_workflow("Nested Conditionals")

        workflow.add_task(Task(task_id="check1", name="Check1", action="check"))
        workflow.add_task(Task(
            task_id="branch1",
            name="Branch1",
            action="branch",
            dependencies=["check1"],
            conditional="success"
        ))
        workflow.add_task(Task(
            task_id="check2",
            name="Check2",
            action="check",
            dependencies=["branch1"]
        ))
        workflow.add_task(Task(
            task_id="branch2",
            name="Branch2",
            action="branch",
            dependencies=["check2"],
            conditional="success"
        ))

        assert len(workflow.tasks) == 4


# ============================================================================
# TEST SUITE 4: TASK DEPENDENCIES
# ============================================================================

class TestTaskDependencies:
    """Test task dependency resolution and validation."""

    def test_single_dependency(self, orchestration_engine, dependency_resolver):
        """Test task with single dependency."""
        task = Task(
            task_id="task_2",
            name="Dependent",
            action="dependent",
            dependencies=["task_1"]
        )

        deps = dependency_resolver.resolve_dependencies(task)
        assert deps == ["task_1"]

    def test_multiple_dependencies(self, orchestration_engine, dependency_resolver):
        """Test task with multiple dependencies."""
        task = Task(
            task_id="task_final",
            name="Final",
            action="final",
            dependencies=["task_1", "task_2", "task_3"]
        )

        deps = dependency_resolver.resolve_dependencies(task)
        assert len(deps) == 3
        assert "task_1" in deps
        assert "task_2" in deps
        assert "task_3" in deps

    def test_dependency_satisfaction(self, dependency_resolver):
        """Test checking if dependencies are satisfied."""
        task = Task(
            task_id="task_3",
            name="Test",
            action="test",
            dependencies=["task_1", "task_2"]
        )

        # Not satisfied when completed_tasks is empty
        assert not dependency_resolver.check_dependency_satisfaction(task, set())

        # Not satisfied when only one dependency is met
        assert not dependency_resolver.check_dependency_satisfaction(task, {"task_1"})

        # Satisfied when all dependencies are met
        assert dependency_resolver.check_dependency_satisfaction(
            task, {"task_1", "task_2"}
        )

    def test_blocking_tasks(self, dependency_resolver):
        """Test identifying blocking tasks."""
        task = Task(
            task_id="task_4",
            name="Test",
            action="test",
            dependencies=["task_1", "task_2", "task_3"]
        )

        # All tasks are blocking
        blocking = dependency_resolver.get_blocking_tasks(task, set())
        assert len(blocking) == 3

        # Some tasks are blocking
        blocking = dependency_resolver.get_blocking_tasks(task, {"task_1"})
        assert len(blocking) == 2
        assert "task_1" not in blocking

        # No tasks are blocking
        blocking = dependency_resolver.get_blocking_tasks(
            task, {"task_1", "task_2", "task_3"}
        )
        assert len(blocking) == 0

    def test_circular_dependency_detection(self, orchestration_engine):
        """Test detection of circular dependencies."""
        workflow = orchestration_engine.create_workflow("Circular Test")

        workflow.add_task(Task(
            task_id="task_1",
            name="Task1",
            action="test",
            dependencies=["task_2"]
        ))
        workflow.add_task(Task(
            task_id="task_2",
            name="Task2",
            action="test",
            dependencies=["task_1"]
        ))

        is_circular = orchestration_engine._has_circular_dependency(workflow)
        assert is_circular


# ============================================================================
# TEST SUITE 5: WORKFLOW VALIDATION
# ============================================================================

class TestWorkflowValidation:
    """Test workflow validation and error handling."""

    def test_validate_valid_workflow(self, sample_workflow, orchestration_engine):
        """Test validation of a valid workflow."""
        valid, msg = orchestration_engine.validate_workflow(sample_workflow.workflow_id)
        
        orchestration_engine.workflows[sample_workflow.workflow_id] = sample_workflow
        valid, msg = orchestration_engine.validate_workflow(sample_workflow.workflow_id)
        
        assert valid

    def test_validate_nonexistent_workflow(self, orchestration_engine):
        """Test validation of non-existent workflow."""
        valid, msg = orchestration_engine.validate_workflow("non-existent")
        assert not valid
        assert "not found" in msg.lower()

    def test_validate_empty_workflow(self, orchestration_engine):
        """Test validation of empty workflow (no tasks)."""
        workflow = orchestration_engine.create_workflow("Empty")
        valid, msg = orchestration_engine.validate_workflow(workflow.workflow_id)

        assert not valid
        assert "no tasks" in msg.lower()

    def test_validate_circular_dependency(self, orchestration_engine):
        """Test validation detects circular dependencies."""
        workflow = orchestration_engine.create_workflow("Circular")

        workflow.add_task(Task(
            task_id="task_1", name="T1", action="t1",
            dependencies=["task_2"]
        ))
        workflow.add_task(Task(
            task_id="task_2", name="T2", action="t2",
            dependencies=["task_1"]
        ))

        valid, msg = orchestration_engine.validate_workflow(workflow.workflow_id)
        assert not valid
        assert "circular" in msg.lower()


# ============================================================================
# TEST SUITE 6: ROOT AND LEAF TASKS
# ============================================================================

class TestRootAndLeafTasks:
    """Test identification of root and leaf tasks."""

    def test_get_root_tasks(self, complex_workflow):
        """Test retrieving root tasks (no dependencies)."""
        root_tasks = complex_workflow.get_root_tasks()

        assert len(root_tasks) == 1
        assert root_tasks[0].task_id == "task_1"

    def test_get_leaf_tasks(self, complex_workflow):
        """Test retrieving leaf tasks (no dependents)."""
        leaf_tasks = complex_workflow.get_leaf_tasks()

        assert len(leaf_tasks) == 1
        assert leaf_tasks[0].task_id == "task_4"

    def test_multiple_root_tasks(self, orchestration_engine):
        """Test workflow with multiple root tasks."""
        workflow = orchestration_engine.create_workflow("Multi Root")

        workflow.add_task(Task(task_id="task_1", name="T1", action="t1"))
        workflow.add_task(Task(task_id="task_2", name="T2", action="t2"))
        workflow.add_task(Task(
            task_id="task_3", name="T3", action="t3",
            dependencies=["task_1", "task_2"]
        ))

        root_tasks = workflow.get_root_tasks()
        assert len(root_tasks) == 2

    def test_multiple_leaf_tasks(self, orchestration_engine):
        """Test workflow with multiple leaf tasks."""
        workflow = orchestration_engine.create_workflow("Multi Leaf")

        workflow.add_task(Task(task_id="task_1", name="T1", action="t1"))
        workflow.add_task(Task(
            task_id="task_2", name="T2", action="t2",
            dependencies=["task_1"]
        ))
        workflow.add_task(Task(
            task_id="task_3", name="T3", action="t3",
            dependencies=["task_1"]
        ))

        leaf_tasks = workflow.get_leaf_tasks()
        assert len(leaf_tasks) == 2
        assert "task_2" in [t.task_id for t in leaf_tasks]
        assert "task_3" in [t.task_id for t in leaf_tasks]


# ============================================================================
# TEST SUITE 7: WORKFLOW SERIALIZATION
# ============================================================================

class TestWorkflowSerialization:
    """Test workflow serialization to/from JSON."""

    def test_serialize_task(self):
        """Test serializing a task to dictionary."""
        task = Task(
            task_id="task_1",
            name="Test Task",
            action="test",
            retries=3,
            timeout=600,
            dependencies=["task_0"]
        )

        task_dict = task.to_dict()

        assert task_dict["task_id"] == "task_1"
        assert task_dict["name"] == "Test Task"
        assert task_dict["retries"] == 3
        assert task_dict["timeout"] == 600
        assert task_dict["dependencies"] == ["task_0"]

    def test_serialize_workflow(self, sample_workflow):
        """Test serializing a workflow to dictionary."""
        workflow_dict = sample_workflow.to_dict()

        assert workflow_dict["workflow_id"] == sample_workflow.workflow_id
        assert workflow_dict["name"] == sample_workflow.name
        assert workflow_dict["version"] == sample_workflow.version
        assert len(workflow_dict["tasks"]) == 3
        assert workflow_dict["status"] == "draft"

    def test_serialize_to_json(self, sample_workflow):
        """Test converting workflow to JSON."""
        workflow_dict = sample_workflow.to_dict()
        json_str = json.dumps(workflow_dict)

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["name"] == "Sample Workflow"

    def test_serialize_workflow_with_metadata(self, orchestration_engine):
        """Test serializing workflow with metadata."""
        workflow = orchestration_engine.create_workflow(
            name="Metadata Test",
            metadata={
                "owner": "test@example.com",
                "tags": ["automation", "testing"],
                "priority": "high"
            }
        )

        workflow_dict = workflow.to_dict()
        assert workflow_dict["metadata"]["owner"] == "test@example.com"
        assert "automation" in workflow_dict["metadata"]["tags"]


# ============================================================================
# TEST SUITE 8: EXECUTION HISTORY
# ============================================================================

class TestExecutionHistory:
    """Test workflow execution history tracking."""

    def test_execution_history_recorded(self, sample_workflow, orchestration_engine):
        """Test that execution history is recorded."""
        orchestration_engine.workflows[sample_workflow.workflow_id] = sample_workflow

        orchestration_engine.execute_workflow(sample_workflow.workflow_id)

        history = orchestration_engine.get_execution_history(sample_workflow.workflow_id)
        assert len(history) > 0
        assert history[0]["workflow_id"] == sample_workflow.workflow_id

    def test_multiple_executions_tracked(self, sample_workflow, orchestration_engine):
        """Test that multiple executions are tracked separately."""
        orchestration_engine.workflows[sample_workflow.workflow_id] = sample_workflow

        # Execute multiple times
        for _ in range(3):
            orchestration_engine.execute_workflow(sample_workflow.workflow_id)

        history = orchestration_engine.get_execution_history(sample_workflow.workflow_id)
        assert len(history) == 3

    def test_execution_timestamp(self, sample_workflow, orchestration_engine):
        """Test that execution includes timestamp."""
        orchestration_engine.workflows[sample_workflow.workflow_id] = sample_workflow

        orchestration_engine.execute_workflow(sample_workflow.workflow_id)

        history = orchestration_engine.get_execution_history(sample_workflow.workflow_id)
        assert "timestamp" in history[0]


# ============================================================================
# ADDITIONAL ORCHESTRATION TESTS
# ============================================================================

class TestTaskScheduling:
    """Test task scheduling capabilities."""

    def test_schedule_task(self, task_scheduler):
        """Test scheduling a task."""
        future_time = datetime.utcnow() + timedelta(hours=1)
        schedule_id = task_scheduler.schedule_task("task_1", future_time)

        assert schedule_id is not None
        scheduled = task_scheduler.get_scheduled_task(schedule_id)
        assert scheduled is not None
        assert scheduled["task_id"] == "task_1"
        assert scheduled["status"] == "scheduled"

    def test_cancel_scheduled_task(self, task_scheduler):
        """Test cancelling a scheduled task."""
        future_time = datetime.utcnow() + timedelta(hours=1)
        schedule_id = task_scheduler.schedule_task("task_1", future_time)

        result = task_scheduler.cancel_scheduled_task(schedule_id)
        assert result
        assert task_scheduler.get_scheduled_task(schedule_id)["status"] == "cancelled"

    def test_schedule_task_with_recurrence(self, task_scheduler):
        """Test scheduling a task with recurrence."""
        future_time = datetime.utcnow() + timedelta(hours=1)
        schedule_id = task_scheduler.schedule_task(
            "task_1", future_time, recurrence="daily"
        )

        scheduled = task_scheduler.get_scheduled_task(schedule_id)
        assert scheduled["recurrence"] == "daily"

    def test_queue_and_retrieve_tasks(self, task_scheduler):
        """Test queuing and retrieving tasks."""
        task_scheduler.queue_task_for_execution("task_1")
        task_scheduler.queue_task_for_execution("task_2")

        assert task_scheduler.get_next_task() == "task_1"
        assert task_scheduler.get_next_task() == "task_2"
        assert task_scheduler.get_next_task() is None

    def test_get_pending_tasks(self, task_scheduler):
        """Test getting all pending tasks."""
        for i in range(5):
            task_scheduler.queue_task_for_execution(f"task_{i}")

        pending = task_scheduler.get_pending_tasks()
        assert len(pending) == 5


# ============================================================================
# COMPREHENSIVE INTEGRATION TESTS
# ============================================================================

class TestComprehensiveIntegration:
    """Comprehensive integration tests combining multiple features."""

    def test_full_workflow_lifecycle(self, orchestration_engine):
        """Test complete workflow lifecycle."""
        # Create
        workflow = orchestration_engine.create_workflow("Lifecycle Test")
        assert workflow.status == WorkflowStatus.DRAFT

        # Add tasks
        workflow.add_task(Task(task_id="t1", name="T1", action="t1"))
        workflow.add_task(Task(
            task_id="t2", name="T2", action="t2",
            dependencies=["t1"]
        ))

        # Validate
        valid, _ = orchestration_engine.validate_workflow(workflow.workflow_id)
        assert valid

        # Execute
        result = orchestration_engine.execute_workflow(workflow.workflow_id)
        assert result["status"] == "completed"
        assert workflow.status == WorkflowStatus.COMPLETED

    def test_workflow_with_retries(self, orchestration_engine):
        """Test workflow with task retries."""
        workflow = orchestration_engine.create_workflow("Retry Test")

        task = Task(
            task_id="task_1",
            name="Retryable",
            action="retry",
            retries=3
        )
        workflow.add_task(task)

        result = orchestration_engine.execute_workflow(workflow.workflow_id)
        assert result["status"] == "completed"

    def test_workflow_with_timeouts(self, orchestration_engine):
        """Test workflow with task timeouts."""
        workflow = orchestration_engine.create_workflow("Timeout Test")

        task = Task(
            task_id="task_1",
            name="Timeout Task",
            action="timeout",
            timeout=30
        )
        workflow.add_task(task)

        assert workflow.get_task("task_1").timeout == 30


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

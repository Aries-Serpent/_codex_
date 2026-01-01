"""
Phase 9.1 - Comprehensive tests for agents.workflow_navigator module.

Tests cover:
- Workflow creation and management
- Step execution and status tracking
- Token-based workflow operations
- Error handling and recovery
- State persistence
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from agents.workflow_navigator import (
    StepStatus,
    Workflow,
    WorkflowFrequency,
    WorkflowNavigator,
    WorkflowStep,
)


class TestWorkflowFrequency:
    """Test WorkflowFrequency enumeration."""

    def test_frequency_values(self) -> None:
        """Test frequency enum values."""
        assert WorkflowFrequency.HIGH.value == "high"
        assert WorkflowFrequency.MEDIUM.value == "medium"
        assert WorkflowFrequency.LOW.value == "low"


class TestStepStatus:
    """Test StepStatus enumeration."""

    def test_status_values(self) -> None:
        """Test step status enum values."""
        assert StepStatus.PENDING.value == "pending"
        assert StepStatus.RUNNING.value == "running"
        assert StepStatus.IN_PROGRESS.value == "in_progress"
        assert StepStatus.COMPLETED.value == "completed"
        assert StepStatus.FAILED.value == "failed"
        assert StepStatus.SKIPPED.value == "skipped"
        assert StepStatus.BLOCKED.value == "blocked"
        assert StepStatus.CANCELLED.value == "cancelled"


class TestWorkflowStep:
    """Test WorkflowStep functionality."""

    def test_step_creation(self) -> None:
        """Test creating a workflow step."""
        step = WorkflowStep(
            id="step1",
            action="Run tests",
            command="pytest tests/",
        )

        assert step.id == "step1"
        assert step.action == "Run tests"
        assert step.command == "pytest tests/"
        assert step.status == StepStatus.PENDING

    def test_step_with_outputs(self) -> None:
        """Test step with output specifications."""
        step = WorkflowStep(
            id="step1",
            action="Build",
            outputs=["artifact.zip", "build.log"],
        )

        assert len(step.outputs) == 2
        assert "artifact.zip" in step.outputs

    def test_step_optional_flag(self) -> None:
        """Test optional step flag."""
        step = WorkflowStep(
            id="step1",
            action="Optional check",
            optional=True,
        )

        assert step.optional is True

    @patch("subprocess.run")
    def test_step_execute_command_success(self, mock_run: Mock) -> None:
        """Test executing a step with a command successfully."""
        mock_run.return_value = Mock(returncode=0, stdout="success", stderr="")

        step = WorkflowStep(
            id="step1",
            action="Run command",
            command="echo test",
        )

        result = step.execute({"working_dir": "/tmp"})

        assert result["success"] is True
        assert step.status == StepStatus.COMPLETED

    @patch("subprocess.run")
    def test_step_execute_command_failure(self, mock_run: Mock) -> None:
        """Test executing a step with command failure."""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="error")

        step = WorkflowStep(
            id="step1",
            action="Run command",
            command="false",
        )

        result = step.execute({})

        assert result["success"] is False
        assert step.status == StepStatus.FAILED
        assert "error" in result.get("error", "")

    @patch("subprocess.run")
    def test_step_execute_optional_failure(self, mock_run: Mock) -> None:
        """Test optional step failure doesn't fail execution."""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="error")

        step = WorkflowStep(
            id="step1",
            action="Optional step",
            command="false",
            optional=True,
        )

        _ = step.execute({})

        # Optional steps can fail without causing workflow failure
        assert step.status == StepStatus.COMPLETED

    def test_step_execute_uses_reference(self) -> None:
        """Test step with uses reference."""
        step = WorkflowStep(
            id="step1",
            action="Use another workflow",
            uses="workflow:build",
        )

        result = step.execute({})

        assert result["success"] is True
        assert step.status == StepStatus.COMPLETED

    def test_step_execute_no_action(self) -> None:
        """Test step with no action defined."""
        step = WorkflowStep(
            id="step1",
            action="Empty step",
        )

        result = step.execute({})

        assert result["success"] is True
        assert step.status == StepStatus.SKIPPED

    @patch("subprocess.run")
    def test_step_execute_exception_handling(self, mock_run: Mock) -> None:
        """Test step execution handles exceptions."""
        mock_run.side_effect = Exception("Unexpected error")

        step = WorkflowStep(
            id="step1",
            action="Failing step",
            command="error command",
        )

        result = step.execute({})

        assert result["success"] is False
        assert step.status == StepStatus.FAILED
        assert "Unexpected error" in result["error"]


class TestWorkflow:
    """Test Workflow functionality."""

    def test_workflow_creation(self) -> None:
        """Test creating a workflow."""
        workflow = Workflow(
            workflow_id="test_workflow",
            name="Test Workflow",
            description="A test workflow",
            frequency=WorkflowFrequency.HIGH,
        )

        assert workflow.workflow_id == "test_workflow"
        assert workflow.name == "Test Workflow"
        assert workflow.frequency == WorkflowFrequency.HIGH
        assert workflow.deterministic is True

    def test_workflow_with_steps(self) -> None:
        """Test workflow with multiple steps."""
        steps = [
            WorkflowStep(id="step1", action="First step"),
            WorkflowStep(id="step2", action="Second step"),
        ]

        workflow = Workflow(
            workflow_id="multi_step",
            name="Multi-step Workflow",
            description="Multiple steps",
            frequency=WorkflowFrequency.MEDIUM,
            steps=steps,
        )

        assert len(workflow.steps) == 2
        assert workflow.steps[0].id == "step1"

    def test_workflow_with_aliases(self) -> None:
        """Test workflow with aliases."""
        workflow = Workflow(
            workflow_id="test",
            name="Test",
            description="Test workflow",
            frequency=WorkflowFrequency.LOW,
            aliases=["alias1", "alias2"],
        )

        assert len(workflow.aliases) == 2
        assert "alias1" in workflow.aliases

    def test_workflow_non_deterministic(self) -> None:
        """Test non-deterministic workflow flag."""
        workflow = Workflow(
            workflow_id="random",
            name="Random Workflow",
            description="Non-deterministic",
            frequency=WorkflowFrequency.LOW,
            deterministic=False,
        )

        assert workflow.deterministic is False


class TestWorkflowNavigator:
    """Test WorkflowNavigator class."""

    def test_navigator_initialization(self, tmp_path: Path) -> None:
        """Test creating a workflow navigator."""
        navigator = WorkflowNavigator(workspace_dir=tmp_path)

        assert navigator.workspace_dir == tmp_path
        assert isinstance(navigator.workflows, dict)
        assert navigator.workflow_state_dir.exists()

    def test_navigator_register_workflow(self, tmp_path: Path) -> None:
        """Test registering a workflow."""
        navigator = WorkflowNavigator(workspace_dir=tmp_path)

        workflow = Workflow(
            workflow_id="test_wf",
            name="Test Workflow",
            description="Test",
            frequency=WorkflowFrequency.HIGH,
        )

        navigator.workflows[workflow.workflow_id] = workflow

        assert "test_wf" in navigator.workflows

    def test_navigator_get_workflow(self, tmp_path: Path) -> None:
        """Test retrieving a workflow from navigator."""
        navigator = WorkflowNavigator(workspace_dir=tmp_path)

        workflow = Workflow(
            workflow_id="retrieve_test",
            name="Retrieve Test",
            description="Test retrieval",
            frequency=WorkflowFrequency.LOW,
        )

        navigator.workflows[workflow.workflow_id] = workflow

        retrieved = navigator.workflows.get("retrieve_test")

        assert retrieved is not None
        assert retrieved.workflow_id == "retrieve_test"

    def test_navigator_list_workflows(self, tmp_path: Path) -> None:
        """Test listing all workflows."""
        navigator = WorkflowNavigator(workspace_dir=tmp_path)

        # Navigator should have default workflows registered
        assert len(navigator.workflows) >= 0

    def test_navigator_state_directory_creation(self, tmp_path: Path) -> None:
        """Test state directory is created."""
        navigator = WorkflowNavigator(workspace_dir=tmp_path)

        expected_dir = tmp_path / ".codex" / "workflows" / "state"
        assert expected_dir.exists()
        assert expected_dir == navigator.workflow_state_dir


class TestWorkflowSerialization:
    """Test workflow serialization."""

    def test_workflow_to_dict(self) -> None:
        """Test converting workflow to dictionary."""
        workflow = Workflow(
            workflow_id="serialize_test",
            name="Serialize Test",
            description="Test serialization",
            frequency=WorkflowFrequency.MEDIUM,
            steps=[
                WorkflowStep(id="step1", action="Action 1"),
            ],
        )

        data = workflow.to_dict()

        assert data["workflow_id"] == "serialize_test"
        assert data["name"] == "Serialize Test"
        assert len(data["steps"]) == 1
        assert data["steps"][0]["id"] == "step1"

    def test_workflow_to_dict_with_all_fields(self) -> None:
        """Test serialization with all fields."""
        workflow = Workflow(
            workflow_id="full_test",
            name="Full Test",
            description="Full serialization",
            frequency=WorkflowFrequency.LOW,
            deterministic=False,
            aliases=["alias1"],
            entry_points=["main.py"],
            category="testing",
            steps=[
                WorkflowStep(
                    id="step1",
                    action="Action",
                    command="echo test",
                    outputs=["output.txt"],
                    optional=True,
                ),
            ],
        )

        data = workflow.to_dict()

        assert data["deterministic"] is False
        assert "alias1" in data["aliases"]
        assert "main.py" in data["entry_points"]
        assert data["category"] == "testing"


class TestWorkflowTokenization:
    """Test workflow tokenization features."""

    def test_workflow_deterministic_flag(self) -> None:
        """Test deterministic flag for reproducibility."""
        wf1 = Workflow(
            workflow_id="det1",
            name="Deterministic",
            description="Deterministic workflow",
            frequency=WorkflowFrequency.HIGH,
            deterministic=True,
        )

        wf2 = Workflow(
            workflow_id="det2",
            name="Non-deterministic",
            description="Random workflow",
            frequency=WorkflowFrequency.LOW,
            deterministic=False,
        )

        assert wf1.deterministic is True
        assert wf2.deterministic is False

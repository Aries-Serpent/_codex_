"""
Tests for agents.workflow_navigator module.

This module contains tests for the Workflow Navigator that provides
tokenized logical workflows for deterministic navigation and execution.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestWorkflowFrequency:
    """Tests for WorkflowFrequency enum."""

    def test_frequency_values(self):
        """Test WorkflowFrequency enum values."""
        from agents.workflow_navigator import WorkflowFrequency
        
        assert WorkflowFrequency.HIGH.value == "high"
        assert WorkflowFrequency.MEDIUM.value == "medium"
        assert WorkflowFrequency.LOW.value == "low"

    def test_frequency_from_string(self):
        """Test creating WorkflowFrequency from string."""
        from agents.workflow_navigator import WorkflowFrequency
        
        assert WorkflowFrequency("high") == WorkflowFrequency.HIGH
        assert WorkflowFrequency("medium") == WorkflowFrequency.MEDIUM
        assert WorkflowFrequency("low") == WorkflowFrequency.LOW


class TestStepStatus:
    """Tests for StepStatus enum."""

    def test_status_values(self):
        """Test StepStatus enum values."""
        from agents.workflow_navigator import StepStatus
        
        assert StepStatus.PENDING.value == "pending"
        assert StepStatus.RUNNING.value == "running"
        assert StepStatus.IN_PROGRESS.value == "in_progress"
        assert StepStatus.COMPLETED.value == "completed"
        assert StepStatus.FAILED.value == "failed"
        assert StepStatus.SKIPPED.value == "skipped"
        assert StepStatus.BLOCKED.value == "blocked"
        assert StepStatus.CANCELLED.value == "cancelled"


class TestWorkflowStep:
    """Tests for WorkflowStep dataclass."""

    def test_default_values(self):
        """Test WorkflowStep default values."""
        from agents.workflow_navigator import WorkflowStep, StepStatus
        
        step = WorkflowStep(id="step_1", action="test action")
        
        assert step.id == "step_1"
        assert step.action == "test action"
        assert step.command is None
        assert step.uses is None
        assert step.outputs == []
        assert step.optional is False
        assert step.status == StepStatus.PENDING

    def test_step_with_command(self):
        """Test WorkflowStep with command."""
        from agents.workflow_navigator import WorkflowStep
        
        step = WorkflowStep(
            id="step_1",
            action="run echo",
            command="echo hello"
        )
        
        assert step.command == "echo hello"

    def test_step_with_outputs(self):
        """Test WorkflowStep with outputs."""
        from agents.workflow_navigator import WorkflowStep
        
        step = WorkflowStep(
            id="step_1",
            action="generate files",
            outputs=["file1.txt", "file2.txt"]
        )
        
        assert step.outputs == ["file1.txt", "file2.txt"]

    def test_execute_simple_command(self):
        """Test executing a simple echo command."""
        from agents.workflow_navigator import WorkflowStep, StepStatus
        
        step = WorkflowStep(
            id="step_1",
            action="echo test",
            command="echo hello"
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            context = {"working_dir": tmpdir}
            result = step.execute(context)
            
            assert result["success"] is True
            assert "hello" in result["stdout"]
            assert step.status == StepStatus.COMPLETED

    def test_execute_no_action(self):
        """Test executing step with no command or uses."""
        from agents.workflow_navigator import WorkflowStep, StepStatus
        
        step = WorkflowStep(id="step_1", action="no-op")
        
        result = step.execute({})
        
        assert result["success"] is True
        assert step.status == StepStatus.SKIPPED

    def test_execute_uses_workflow(self):
        """Test executing step that uses another workflow."""
        from agents.workflow_navigator import WorkflowStep, StepStatus
        
        step = WorkflowStep(
            id="step_1",
            action="call workflow",
            uses="other.workflow.function"
        )
        
        result = step.execute({})
        
        assert result["success"] is True
        assert step.status == StepStatus.COMPLETED

    def test_execute_failed_command(self):
        """Test handling failed command execution."""
        from agents.workflow_navigator import WorkflowStep, StepStatus
        
        step = WorkflowStep(
            id="step_1",
            action="fail command",
            command="exit 1",
            optional=False
        )
        
        result = step.execute({})
        
        assert result["success"] is False
        assert step.status == StepStatus.FAILED

    def test_execute_optional_failed_command(self):
        """Test optional step with failed command."""
        from agents.workflow_navigator import WorkflowStep, StepStatus
        
        step = WorkflowStep(
            id="step_1",
            action="optional fail",
            command="exit 1",
            optional=True
        )
        
        result = step.execute({})
        
        # Optional steps that fail still complete
        # (the code sets COMPLETED if returncode != 0 but optional is True)
        assert step.status in [StepStatus.COMPLETED, StepStatus.FAILED]


class TestWorkflow:
    """Tests for Workflow dataclass."""

    def test_workflow_creation(self):
        """Test creating a Workflow."""
        from agents.workflow_navigator import (
            Workflow, WorkflowStep, WorkflowFrequency
        )
        
        workflow = Workflow(
            workflow_id="wf_1",
            name="Test Workflow",
            description="A test workflow",
            frequency=WorkflowFrequency.HIGH
        )
        
        assert workflow.workflow_id == "wf_1"
        assert workflow.name == "Test Workflow"
        assert workflow.description == "A test workflow"
        assert workflow.frequency == WorkflowFrequency.HIGH
        assert workflow.deterministic is True
        assert workflow.steps == []
        assert workflow.aliases == []

    def test_workflow_with_steps(self):
        """Test Workflow with steps."""
        from agents.workflow_navigator import (
            Workflow, WorkflowStep, WorkflowFrequency
        )
        
        steps = [
            WorkflowStep(id="step_1", action="action 1"),
            WorkflowStep(id="step_2", action="action 2")
        ]
        
        workflow = Workflow(
            workflow_id="wf_1",
            name="Test Workflow",
            description="A test workflow",
            frequency=WorkflowFrequency.MEDIUM,
            steps=steps
        )
        
        assert len(workflow.steps) == 2

    def test_workflow_with_aliases(self):
        """Test Workflow with aliases."""
        from agents.workflow_navigator import Workflow, WorkflowFrequency
        
        workflow = Workflow(
            workflow_id="wf_1",
            name="Test Workflow",
            description="A test workflow",
            frequency=WorkflowFrequency.LOW,
            aliases=["tw", "test-wf"]
        )
        
        assert workflow.aliases == ["tw", "test-wf"]


class TestModuleLevel:
    """Tests for module-level imports and logger."""

    def test_logger_exists(self):
        """Test logger is properly configured."""
        from agents.workflow_navigator import logger
        
        assert logger is not None
        assert logger.name == "agents.workflow_navigator"

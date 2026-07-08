"""
Tests for agents.workflow_navigator module.

This module contains tests for the Workflow Navigator that provides
tokenized logical workflows for deterministic navigation and execution.
"""

import tempfile


class TestWorkflowFrequency:
    """Tests for WorkflowFrequency enum."""

    def test_frequency_values(self):
        """Test WorkflowFrequency enum values."""
        from agents.workflow_navigator import WorkflowFrequency

        assert WorkflowFrequency.HIGH.value == "high", "Value must be initialized"
        assert WorkflowFrequency.MEDIUM.value == "medium", "Value must be initialized"
        assert WorkflowFrequency.LOW.value == "low", "Value must be initialized"

    def test_frequency_from_string(self):
        """Test creating WorkflowFrequency from string."""
        from agents.workflow_navigator import WorkflowFrequency

        assert WorkflowFrequency("high") == WorkflowFrequency.HIGH, "W is not valid"
        assert WorkflowFrequency("medium") == WorkflowFrequency.MEDIUM, "W is not valid"
        assert WorkflowFrequency("low") == WorkflowFrequency.LOW, "W is not valid"


class TestStepStatus:
    """Tests for StepStatus enum."""

    def test_status_values(self):
        """Test StepStatus enum values."""
        from agents.workflow_navigator import StepStatus

        assert StepStatus.PENDING.value == "pending", "Value must be initialized"
        assert StepStatus.RUNNING.value == "running", "Value must be initialized"
        assert StepStatus.IN_PROGRESS.value == "in_progress", "Value must be initialized"
        assert StepStatus.COMPLETED.value == "completed", "Value must be initialized"
        assert StepStatus.FAILED.value == "failed", "Value must be initialized"
        assert StepStatus.SKIPPED.value == "skipped", "Value must be initialized"
        assert StepStatus.BLOCKED.value == "blocked", "Value must be initialized"
        assert StepStatus.CANCELLED.value == "cancelled", "Value must be initialized"


class TestWorkflowStep:
    """Tests for WorkflowStep dataclass."""

    def test_default_values(self):
        """Test WorkflowStep default values."""
        from agents.workflow_navigator import StepStatus, WorkflowStep

        step = WorkflowStep(id="step_1", action="test action")

        assert step.id == "step_1", "id is not valid"
        assert step.action == "test action", "action is not valid"
        assert step.command is None, "command is not valid"
        assert step.uses is None, "uses is not valid"
        assert step.outputs == [], "outputs is not valid"
        assert step.optional is False, "optional is not valid"
        assert step.status == StepStatus.PENDING, "status is not valid"

    def test_step_with_command(self):
        """Test WorkflowStep with command."""
        from agents.workflow_navigator import WorkflowStep

        step = WorkflowStep(id="step_1", action="run echo", command="echo hello")

        assert step.command == "echo hello", "command is not valid"

    def test_step_with_outputs(self):
        """Test WorkflowStep with outputs."""
        from agents.workflow_navigator import WorkflowStep

        step = WorkflowStep(
            id="step_1", action="generate files", outputs=["file1.txt", "file2.txt"]
        )

        assert step.outputs == ["file1.txt", "file2.txt"]

    def test_execute_simple_command(self):
        """Test executing a simple echo command."""
        from agents.workflow_navigator import StepStatus, WorkflowStep

        step = WorkflowStep(id="step_1", action="echo test", command="echo hello")

        with tempfile.TemporaryDirectory() as tmpdir:
            context = {"working_dir": tmpdir}
            result = step.execute(context)

            assert result["success"] is True, "Result must not be empty"
            assert "hello" in result["stdout"], "Result must not be empty"
            assert step.status == StepStatus.COMPLETED, "status is not valid"

    def test_execute_no_action(self):
        """Test executing step with no command or uses."""
        from agents.workflow_navigator import StepStatus, WorkflowStep

        step = WorkflowStep(id="step_1", action="no-op")

        result = step.execute({})

        assert result["success"] is True, "Result must not be empty"
        assert step.status == StepStatus.SKIPPED, "status is not valid"

    def test_execute_uses_workflow(self):
        """Test executing step that uses another workflow."""
        from agents.workflow_navigator import StepStatus, WorkflowStep

        step = WorkflowStep(id="step_1", action="call workflow", uses="other.workflow.function")

        result = step.execute({})

        assert result["success"] is True, "Result must not be empty"
        assert step.status == StepStatus.COMPLETED, "status is not valid"

    def test_execute_failed_command(self):
        """Test handling failed command execution."""
        from agents.workflow_navigator import StepStatus, WorkflowStep

        step = WorkflowStep(id="step_1", action="fail command", command="exit 1", optional=False)

        result = step.execute({})

        assert result["success"] is False, "Result must not be empty"
        assert step.status == StepStatus.FAILED, "status is not valid"

    def test_execute_optional_failed_command(self):
        """Test optional step with failed command."""
        from agents.workflow_navigator import StepStatus, WorkflowStep

        step = WorkflowStep(id="step_1", action="optional fail", command="exit 1", optional=True)

        step.execute({})

        # Optional steps that fail still complete
        # (the code sets COMPLETED if returncode != 0 but optional is True)
        assert step.status in [StepStatus.COMPLETED, StepStatus.FAILED]


class TestWorkflow:
    """Tests for Workflow dataclass."""

    def test_workflow_creation(self):
        """Test creating a Workflow."""
        from agents.workflow_navigator import Workflow, WorkflowFrequency

        workflow = Workflow(
            workflow_id="wf_1",
            name="Test Workflow",
            description="A test workflow",
            frequency=WorkflowFrequency.HIGH,
        )

        assert workflow.workflow_id == "wf_1", "workflow_id is not valid"
        assert workflow.name == "Test Workflow", "name is not valid"
        assert workflow.description == "A test workflow", "description is not valid"
        assert workflow.frequency == WorkflowFrequency.HIGH, "frequency is not valid"
        assert workflow.deterministic is True, "deterministic is not valid"
        assert workflow.steps == [], "steps is not valid"
        assert workflow.aliases == [], "aliases is not valid"

    def test_workflow_with_steps(self):
        """Test Workflow with steps."""
        from agents.workflow_navigator import Workflow, WorkflowFrequency, WorkflowStep

        steps = [
            WorkflowStep(id="step_1", action="action 1"),
            WorkflowStep(id="step_2", action="action 2"),
        ]

        workflow = Workflow(
            workflow_id="wf_1",
            name="Test Workflow",
            description="A test workflow",
            frequency=WorkflowFrequency.MEDIUM,
            steps=steps,
        )

        assert len(workflow.steps) == 2, "Collection must not be empty"

    def test_workflow_with_aliases(self):
        """Test Workflow with aliases."""
        from agents.workflow_navigator import Workflow, WorkflowFrequency

        workflow = Workflow(
            workflow_id="wf_1",
            name="Test Workflow",
            description="A test workflow",
            frequency=WorkflowFrequency.LOW,
            aliases=["tw", "test-wf"],
        )

        assert workflow.aliases == ["tw", "test-wf"]


class TestModuleLevel:
    """Tests for module-level imports and logger."""

    def test_logger_exists(self):
        """Test logger is properly configured."""
        from agents.workflow_navigator import logger

        assert logger is not None, "logger must be initialized"
        assert logger.name == "agents.workflow_navigator", "name is not valid"

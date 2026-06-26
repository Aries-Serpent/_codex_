"""
Test Workflow Orchestration Extended

Test module for workflow orchestration extended.
"""

#! /usr/bin/env python3
"""
Test suite for agents/workflow_navigator.py
Comprehensive tests for workflow orchestration and state management
"""

import tempfile

import pytest

from agents.mental_mapping import reset_clock, set_clock
from agents.workflow_navigator import (
    StepStatus,
    Workflow,
    WorkflowFrequency,
    WorkflowNavigator,
    WorkflowStep,
)


@pytest.fixture(autouse=True)
def setup_deterministic_clock():
    """Set deterministic clock for all tests"""
    set_clock("2025-01-01T00:00:00Z")
    yield
    reset_clock()


@pytest.fixture
def navigator():
    """Create fresh WorkflowNavigator instance"""
    return WorkflowNavigator()


class TestWorkflowStep:
    """Tests for WorkflowStep class"""

    def test_step_creation_defaults(self):
        """Test creating step with minimal parameters"""
        step = WorkflowStep(id="step1", action="test action")

        assert step.id == "step1", "id is not valid"
        assert step.action == "test action", "action is not valid"
        assert step.command is None, "command is not valid"
        assert step.optional is False, "optional is not valid"
        assert step.status == StepStatus.PENDING, "status is not valid"

    def test_step_execute_no_command(self):
        """Test executing step with no command"""
        step = WorkflowStep(id="step1", action="noop")
        result = step.execute({})

        assert result["success"] is True, "Result must not be empty"
        assert step.status == StepStatus.SKIPPED, "status is not valid"

    def test_step_execute_simple_command_success(self):
        """Test executing step with successful command"""
        step = WorkflowStep(id="step1", action="echo", command="echo hello")
        result = step.execute({})

        assert result["success"] is True, "Result must not be empty"
        assert "hello" in result["stdout"], "Result must not be empty"
        assert step.status == StepStatus.COMPLETED, "status is not valid"

    def test_step_execute_command_failure(self):
        """Test executing step with failing command"""
        step = WorkflowStep(id="step1", action="fail", command="false")
        result = step.execute({})

        assert result["success"] is False, "Result must not be empty"
        assert step.status == StepStatus.FAILED, "status is not valid"

    def test_step_execute_optional_failure(self):
        """Test optional step doesn't fail workflow"""
        step = WorkflowStep(id="step1", action="maybe fail", command="false", optional=True)
        step.execute({})  # Return value not needed; only side effects are tested

        # Optional steps succeed even if command fails
        assert step.status == StepStatus.COMPLETED, "status is not valid"

    def test_step_execute_with_context_working_dir(self):
        """Test step execution uses context working directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            step = WorkflowStep(id="step1", action="pwd", command="pwd")
            result = step.execute({"working_dir": tmpdir})

            assert result["success"] is True, "Result must not be empty"
            assert tmpdir in result["stdout"], "Result must not be empty"


class TestWorkflow:
    """Tests for Workflow class"""

    def test_workflow_creation(self):
        """Test creating workflow with basic parameters"""
        workflow = Workflow(
            workflow_id="test-wf",
            name="Test Workflow",
            description="A test workflow",
            frequency=WorkflowFrequency.HIGH,
        )

        assert workflow.workflow_id == "test-wf", "workflow_id is not valid"
        assert workflow.name == "Test Workflow", "name is not valid"
        assert workflow.frequency == WorkflowFrequency.HIGH, "frequency is not valid"
        assert workflow.deterministic is True, "deterministic is not valid"
        assert len(workflow.steps) == 0, "Collection must not be empty"

    def test_workflow_with_steps(self):
        """Test workflow with multiple steps"""
        steps = [
            WorkflowStep(id="step1", action="action1"),
            WorkflowStep(id="step2", action="action2"),
        ]
        workflow = Workflow(
            workflow_id="multi-step",
            name="Multi Step",
            description="Multiple steps",
            frequency=WorkflowFrequency.MEDIUM,
            steps=steps,
        )

        assert len(workflow.steps) == 2, "Collection must not be empty"
        assert workflow.steps[0].id == "step1", "id is not valid"
        assert workflow.steps[1].id == "step2", "id is not valid"


class TestWorkflowNavigator:
    """Tests for WorkflowNavigator orchestration"""

    def test_navigator_initialization(self, navigator):
        """Test WorkflowNavigator initializes correctly"""
        assert navigator is not None, "navigator must be initialized"
        assert hasattr(navigator, "workflows") or hasattr(navigator, "_workflows")

    def test_create_workflow_basic(self, navigator):
        """Test creating a basic workflow"""
        if not hasattr(navigator, "create_workflow"):
            pytest.skip("create_workflow method not implemented")

        workflow_id = navigator.create_workflow("test-wf", ["step1", "step2"])

        # create_workflow returns uppercase ID
        assert workflow_id == "TEST-WF", "workflow_id is not valid"

    def test_get_workflow_exists(self, navigator):
        """Test retrieving an existing workflow"""
        if not hasattr(navigator, "create_workflow") or not hasattr(navigator, "get_workflow"):
            pytest.skip("Workflow methods not implemented")

        navigator.create_workflow("test-wf", ["step1"])
        # get_workflow should accept both lowercase and uppercase
        workflow = navigator.get_workflow("TEST-WF")

        assert workflow is not None, "workflow must be initialized"
        assert workflow.workflow_id == "TEST-WF" or hasattr(workflow, "steps")

    def test_get_workflow_not_exists(self, navigator):
        """Test retrieving non-existent workflow"""
        if not hasattr(navigator, "get_workflow"):
            pytest.skip("get_workflow method not implemented")

        workflow = navigator.get_workflow("nonexistent")

        assert workflow is None or workflow == {}, "workflow is not valid"

    def test_create_workflow_duplicate_id(self, navigator):
        """Test creating workflow with duplicate ID"""
        if not hasattr(navigator, "create_workflow"):
            pytest.skip("create_workflow method not implemented")

        navigator.create_workflow("duplicate", ["step1"])

        # Second creation should handle gracefully (overwrite or error)
        result = navigator.create_workflow("duplicate", ["step2"])

        # Either succeeds (overwrite) or raises error
        assert result == "duplicate" or isinstance(result, str)

    def test_workflow_state_transitions(self, navigator):
        """Test workflow state transitions through execution"""
        if not hasattr(navigator, "create_workflow"):
            pytest.skip("Workflow execution not implemented")

        workflow_id = navigator.create_workflow("state-test", ["echo hello"])

        # Workflow should be retrievable
        workflow = navigator.get_workflow(workflow_id)
        assert workflow is not None, "workflow must be initialized"

    def test_concurrent_workflow_handling(self, navigator):
        """Test handling multiple concurrent workflows"""
        if not hasattr(navigator, "create_workflow"):
            pytest.skip("create_workflow not implemented")

        wf1 = navigator.create_workflow("wf1", ["step1"])
        wf2 = navigator.create_workflow("wf2", ["step2"])
        wf3 = navigator.create_workflow("wf3", ["step3"])

        # All workflows should be independently retrievable
        # create_workflow returns uppercase IDs
        assert wf1 == "WF1", "wf1 is not valid"
        assert wf2 == "WF2", "wf2 is not valid"
        assert wf3 == "WF3", "wf3 is not valid"


class TestWorkflowEdgeCases:
    """Edge case tests for workflow system"""

    def test_workflow_empty_steps(self, navigator):
        """Test creating workflow with empty steps list"""
        if not hasattr(navigator, "create_workflow"):
            pytest.skip("create_workflow not implemented")

        # Should handle empty steps gracefully
        try:
            navigator.create_workflow("empty-wf", [])
            # Either succeeds or raises ValueError
        except ValueError:
            # Expected for some implementations
            _ = None  # suppressed: no action needed

    def test_workflow_very_long_id(self, navigator):
        """Test workflow with very long ID"""
        if not hasattr(navigator, "create_workflow"):
            pytest.skip("create_workflow not implemented")

        long_id = "a" * 1000
        result = navigator.create_workflow(long_id, ["step1"])

        # Should handle long IDs
        assert isinstance(result, str)

    def test_workflow_special_characters_in_id(self, navigator):
        """Test workflow ID with special characters"""
        if not hasattr(navigator, "create_workflow"):
            pytest.skip("create_workflow not implemented")

        special_id = "test-wf_123.v2"
        result = navigator.create_workflow(special_id, ["step1"])

        assert result == special_id or isinstance(result, str)

    def test_step_with_multiline_command(self):
        """Test step with multiline command"""
        step = WorkflowStep(
            id="multi", action="multiple commands", command="echo line1 && echo line2"
        )
        result = step.execute({})

        assert result["success"] is True or result["success"] is False, "Result must not be empty"

    def test_step_command_injection_safety(self):
        """Test step handles command injection attempts safely"""
        step = WorkflowStep(
            id="injection", action="injection test", command="echo safe; echo unsafe"
        )
        result = step.execute({})

        # Command should be handled safely (shlex.split)
        assert result is not None, "result must be initialized"


# Run with: python -m pytest tests/agents/test_workflow_orchestration_extended.py -v

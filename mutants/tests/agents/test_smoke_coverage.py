"""
Smoke tests for agents package modules.

Uses physics-guided testing strategy (Reference Table #49, #56):
- Coverage/Time objective J = Coverage/Runtime
- Minimal import + initialization + invariant checks
- Defers comprehensive tests to follow-up iterations

These tests provide baseline coverage and validate:
- Module can be imported
- Classes can be instantiated
- Basic invariants hold
"""

import pytest


class TestAgentMemorySmoke:
    """Smoke tests for agent_memory module."""

    def test_import(self):
        """Test module can be imported."""
        from agents import agent_memory

        assert agent_memory is not None, "agent_memory must be initialized"

    def test_mental_mapping_import(self):
        """Test MentalMappingModel import."""
        from agents.mental_mapping import MentalMappingModel

        assert MentalMappingModel is not None, "MentalMappingModel must be initialized"


class TestQuantumGameTheorySmoke:
    """Smoke tests for quantum_game_theory module."""

    def test_import(self):
        """Test module can be imported."""
        from agents import quantum_game_theory

        assert quantum_game_theory is not None, "quantum_game_theory must be initialized"

    def test_team_type_enum(self):
        """Test TeamType enum."""
        from agents.quantum_game_theory import TeamType

        assert TeamType.BLUE is not None, "BLUE must be initialized"
        assert TeamType.RED is not None, "RED must be initialized"

    def test_strategy_state_basic(self):
        """Test StrategyState initialization."""
        from agents.quantum_game_theory import StrategyState, TeamType

        state = StrategyState(team=TeamType.BLUE, strategies=["defend", "monitor"])

        assert state.num_strategies == 2, "num_strategies is not valid"
        assert state.team == TeamType.BLUE, "team is not valid"


class TestSelfHealingSmoke:
    """Smoke tests for self_healing module."""

    def test_import(self):
        """Test module can be imported."""
        from agents import self_healing

        assert self_healing is not None, "self_healing must be initialized"

    def test_issue_severity_enum(self):
        """Test IssueSeverity enum."""
        from agents.self_healing import IssueSeverity

        assert IssueSeverity.LOW is not None, "LOW must be initialized"
        assert IssueSeverity.HIGH is not None, "HIGH must be initialized"

    def test_detected_issue_creation(self):
        """Test DetectedIssue can be created."""
        from agents.self_healing import DetectedIssue, IssueSeverity, IssueType

        issue = DetectedIssue(
            issue_id="test-001",
            issue_type=IssueType.BUILD_FAILURE,
            severity=IssueSeverity.HIGH,
            title="Test Build Failure",
            description="Test build failure description",
        )

        assert issue.issue_id == "test-001", "issue_id is not valid"
        assert issue.issue_type == IssueType.BUILD_FAILURE, "issue_type is not valid"
        assert issue.severity == IssueSeverity.HIGH, "severity is not valid"


class TestMSPClientSmoke:
    """Smoke tests for msp_client module - skip if httpx not available."""

    def test_import_attempt(self):
        """Test module import (may require httpx)."""
        try:
            from agents import msp_client

            assert msp_client is not None, "msp_client must be initialized"
        except ImportError as e:
            # Expected if httpx not installed
            pytest.skip(f"msp_client requires additional dependencies: {e}")


class TestPhysicsIntegrationImproved:
    """Additional tests for physics_integration."""

    def test_get_capabilities(self):
        """Test capability reporting."""
        from agents.physics_integration import HybridPhysicsOrchestrator

        orchestrator = HybridPhysicsOrchestrator()
        capabilities = orchestrator.get_capabilities()

        assert isinstance(capabilities, dict)
        assert "classical_physics" in capabilities, "Condition must be true"
        # Keys should match actual capability structure
        assert len(capabilities) > 0, "Capabilities must not be empty"


class TestWorkflowNavigatorImproved:
    """Additional tests for workflow_navigator."""

    def test_list_workflows(self):
        """Test listing workflows."""
        from agents.workflow_navigator import WorkflowNavigator

        navigator = WorkflowNavigator()
        workflows = navigator.list_workflows()

        assert isinstance(workflows, list)
        assert len(workflows) > 0, "Workflows must not be empty"

    def test_get_workflow_exists(self):
        """Test retrieving existing workflow."""
        from agents.workflow_navigator import WorkflowNavigator

        navigator = WorkflowNavigator()
        workflow = navigator.get_workflow("AUDIT_EXEC")

        assert workflow is not None, "workflow must be initialized"
        assert workflow.workflow_id == "AUDIT_EXEC", "workflow_id is not valid"


class TestDeveloperOrchestratorSimple:
    """Simplified tests for developer_orchestrator."""

    def test_import(self):
        """Test module import."""
        from agents import developer_orchestrator

        assert developer_orchestrator is not None, "developer_orchestrator must be initialized"

    def test_app_type_enum(self):
        """Test AppType enum."""
        from agents.developer_orchestrator import AppType

        assert AppType.PYTHON_CLI is not None, "PYTHON_CLI must be initialized"
        assert AppType.PYTHON_WEB is not None, "PYTHON_WEB must be initialized"

    def test_orchestrator_init(self):
        """Test orchestrator can be initialized."""
        from agents.developer_orchestrator import PhysicsGuidedDeveloperOrchestrator

        orchestrator = PhysicsGuidedDeveloperOrchestrator(session_id="test")

        assert orchestrator.session_id == "test", "session_id is not valid"
        assert orchestrator.current_phase is not None, "current_phase must be initialized"
        assert isinstance(orchestrator.components, list)


class TestExceptionsModule:
    """Tests for the new exceptions module."""

    def test_import(self):
        """Test exceptions module can be imported."""
        from agents import exceptions

        assert exceptions is not None, "exceptions must be initialized"

    def test_agent_error_hierarchy(self):
        """Test exception hierarchy."""
        from agents.exceptions import (
            AgentConfigError,
            AgentError,
            AgentImportError,
            AgentValidationError,
        )

        # Test inheritance
        assert issubclass(AgentImportError, AgentError)
        assert issubclass(AgentConfigError, AgentError)
        assert issubclass(AgentValidationError, AgentError)

    def test_agent_import_error_message(self):
        """Test AgentImportError provides helpful message."""
        from agents.exceptions import AgentImportError

        error = AgentImportError("numpy", extra="perf")
        msg = str(error)

        assert "numpy" in msg, "Condition must be true"
        assert "pip install" in msg, "Condition must be true"
        assert "[perf]" in msg, "Condition must be true"

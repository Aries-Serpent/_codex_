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

        assert agent_memory is not None

    def test_mental_mapping_import(self):
        """Test MentalMappingModel import."""
        from agents.mental_mapping import MentalMappingModel

        assert MentalMappingModel is not None


class TestQuantumGameTheorySmoke:
    """Smoke tests for quantum_game_theory module."""

    def test_import(self):
        """Test module can be imported."""
        from agents import quantum_game_theory

        assert quantum_game_theory is not None

    def test_team_type_enum(self):
        """Test TeamType enum."""
        from agents.quantum_game_theory import TeamType

        assert TeamType.BLUE is not None
        assert TeamType.RED is not None

    def test_strategy_state_basic(self):
        """Test StrategyState initialization."""
        from agents.quantum_game_theory import StrategyState, TeamType

        state = StrategyState(team=TeamType.BLUE, strategies=["defend", "monitor"])

        assert state.num_strategies == 2
        assert state.team == TeamType.BLUE


class TestSelfHealingSmoke:
    """Smoke tests for self_healing module."""

    def test_import(self):
        """Test module can be imported."""
        from agents import self_healing

        assert self_healing is not None

    def test_issue_severity_enum(self):
        """Test IssueSeverity enum."""
        from agents.self_healing import IssueSeverity

        assert IssueSeverity.LOW is not None
        assert IssueSeverity.HIGH is not None

    def test_detected_issue_creation(self):
        """Test DetectedIssue can be created."""
        from agents.self_healing import DetectedIssue, IssueType, IssueSeverity

        issue = DetectedIssue(
            issue_id="test-001",
            issue_type=IssueType.BUILD_FAILURE,
            severity=IssueSeverity.HIGH,
            title="Test Build Failure",
            description="Test build failure description",
        )

        assert issue.issue_id == "test-001"
        assert issue.issue_type == IssueType.BUILD_FAILURE
        assert issue.severity == IssueSeverity.HIGH


class TestMSPClientSmoke:
    """Smoke tests for msp_client module - skip if httpx not available."""

    def test_import_attempt(self):
        """Test module import (may require httpx)."""
        try:
            from agents import msp_client

            assert msp_client is not None
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
        assert "classical_physics" in capabilities
        # Keys should match actual capability structure
        assert len(capabilities) > 0


class TestWorkflowNavigatorImproved:
    """Additional tests for workflow_navigator."""

    def test_list_workflows(self):
        """Test listing workflows."""
        from agents.workflow_navigator import WorkflowNavigator

        navigator = WorkflowNavigator()
        workflows = navigator.list_workflows()

        assert isinstance(workflows, list)
        assert len(workflows) > 0

    def test_get_workflow_exists(self):
        """Test retrieving existing workflow."""
        from agents.workflow_navigator import WorkflowNavigator

        navigator = WorkflowNavigator()
        workflow = navigator.get_workflow("AUDIT_EXEC")

        assert workflow is not None
        assert workflow.workflow_id == "AUDIT_EXEC"


class TestDeveloperOrchestratorSimple:
    """Simplified tests for developer_orchestrator."""

    def test_import(self):
        """Test module import."""
        from agents import developer_orchestrator

        assert developer_orchestrator is not None

    def test_app_type_enum(self):
        """Test AppType enum."""
        from agents.developer_orchestrator import AppType

        assert AppType.PYTHON_CLI is not None
        assert AppType.PYTHON_WEB is not None

    def test_orchestrator_init(self):
        """Test orchestrator can be initialized."""
        from agents.developer_orchestrator import PhysicsGuidedDeveloperOrchestrator

        orchestrator = PhysicsGuidedDeveloperOrchestrator(session_id="test")

        assert orchestrator.session_id == "test"
        assert orchestrator.current_phase is not None
        assert isinstance(orchestrator.components, dict)


class TestExceptionsModule:
    """Tests for the new exceptions module."""

    def test_import(self):
        """Test exceptions module can be imported."""
        from agents import exceptions

        assert exceptions is not None

    def test_agent_error_hierarchy(self):
        """Test exception hierarchy."""
        from agents.exceptions import (
            AgentError,
            AgentImportError,
            AgentConfigError,
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

        assert "numpy" in msg
        assert "pip install" in msg
        assert "[perf]" in msg

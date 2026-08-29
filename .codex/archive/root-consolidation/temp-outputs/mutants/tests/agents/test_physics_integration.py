"""
Tests for agents.physics_integration module.

This module contains tests for the hybrid physics integration
connecting advanced physics calculators with existing systems.
"""

from unittest.mock import patch


class TestHybridPhysicsOrchestrator:
    """Tests for HybridPhysicsOrchestrator class."""

    @patch("agents.physics_integration.ADVANCED_PHYSICS_AVAILABLE", False)
    @patch("agents.physics_integration.PHYSICS_ORCHESTRATOR_AVAILABLE", False)
    def test_init_no_physics(self):
        """Test initialization when no physics modules available."""
        from agents.physics_integration import HybridPhysicsOrchestrator

        orchestrator = HybridPhysicsOrchestrator()

        assert orchestrator.classical_orchestrator is None, "classical_orchestrator is not valid"
        assert orchestrator.advanced_orchestrator is None, "advanced_orchestrator is not valid"
        assert orchestrator.session_id == "hybrid_physics", "session_id is not valid"

    @patch("agents.physics_integration.ADVANCED_PHYSICS_AVAILABLE", False)
    @patch("agents.physics_integration.PHYSICS_ORCHESTRATOR_AVAILABLE", False)
    def test_init_custom_session_id(self):
        """Test initialization with custom session_id."""
        from agents.physics_integration import HybridPhysicsOrchestrator

        orchestrator = HybridPhysicsOrchestrator(session_id="custom_session")

        assert orchestrator.session_id == "custom_session", "session_id is not valid"

    @patch("agents.physics_integration.ADVANCED_PHYSICS_AVAILABLE", False)
    @patch("agents.physics_integration.PHYSICS_ORCHESTRATOR_AVAILABLE", False)
    def test_decision_history_empty(self):
        """Test decision_history starts empty."""
        from agents.physics_integration import HybridPhysicsOrchestrator

        orchestrator = HybridPhysicsOrchestrator()

        assert orchestrator.decision_history == [], "decision_history is not valid"

    @patch("agents.physics_integration.ADVANCED_PHYSICS_AVAILABLE", False)
    @patch("agents.physics_integration.PHYSICS_ORCHESTRATOR_AVAILABLE", False)
    @patch("agents.physics_integration.log_message")
    def test_log_method(self, mock_log):
        """Test _log method calls log_message."""
        from agents.physics_integration import HybridPhysicsOrchestrator

        orchestrator = HybridPhysicsOrchestrator(session_id="test")
        orchestrator._log("system", "Test message")

        mock_log.assert_called_once_with("test", "system", "Test message")

    @patch("agents.physics_integration.ADVANCED_PHYSICS_AVAILABLE", False)
    @patch("agents.physics_integration.PHYSICS_ORCHESTRATOR_AVAILABLE", False)
    def test_orchestrate_no_physics(self):
        """Test orchestrate when no physics modules available."""
        from agents.physics_integration import HybridPhysicsOrchestrator

        orchestrator = HybridPhysicsOrchestrator()
        decision_space = {"current_position": "start", "goal_position": "end"}

        result = orchestrator.orchestrate_with_all_paradigms(decision_space)

        assert "paradigms_used" in result, "Result must not be empty"
        assert "recommendations" in result, "Result must not be empty"
        assert result["classical_physics"] is None, "Result must not be empty"
        assert result["advanced_physics"] is None, "Result must not be empty"

    @patch("agents.physics_integration.ADVANCED_PHYSICS_AVAILABLE", False)
    @patch("agents.physics_integration.PHYSICS_ORCHESTRATOR_AVAILABLE", False)
    def test_synthesize_recommendations_empty(self):
        """Test _synthesize_recommendations with empty results."""
        from agents.physics_integration import HybridPhysicsOrchestrator

        orchestrator = HybridPhysicsOrchestrator()
        results = {"classical_physics": None, "advanced_physics": None}

        recommendations = orchestrator._synthesize_recommendations(results)

        assert isinstance(recommendations, list)

    @patch("agents.physics_integration.ADVANCED_PHYSICS_AVAILABLE", False)
    @patch("agents.physics_integration.PHYSICS_ORCHESTRATOR_AVAILABLE", False)
    def test_synthesize_recommendations_classical(self):
        """Test _synthesize_recommendations with classical physics result."""
        from agents.physics_integration import HybridPhysicsOrchestrator

        orchestrator = HybridPhysicsOrchestrator()
        results = {
            "classical_physics": {"action_taken": "move_forward"},
            "advanced_physics": None,
        }

        recommendations = orchestrator._synthesize_recommendations(results)

        assert any("move_forward" in rec for rec in recommendations), "Condition must be true"


class TestModuleLevelFlags:
    """Tests for module-level flags."""

    def test_advanced_physics_available_exists(self):
        """Test ADVANCED_PHYSICS_AVAILABLE flag exists."""
        from agents import physics_integration

        assert hasattr(physics_integration, "ADVANCED_PHYSICS_AVAILABLE")
        assert isinstance(physics_integration.ADVANCED_PHYSICS_AVAILABLE, bool)

    def test_physics_orchestrator_available_exists(self):
        """Test PHYSICS_ORCHESTRATOR_AVAILABLE flag exists."""
        from agents import physics_integration

        assert hasattr(physics_integration, "PHYSICS_ORCHESTRATOR_AVAILABLE")
        assert isinstance(physics_integration.PHYSICS_ORCHESTRATOR_AVAILABLE, bool)

    def test_logging_available_exists(self):
        """Test LOGGING_AVAILABLE flag exists."""
        from agents import physics_integration

        assert hasattr(physics_integration, "LOGGING_AVAILABLE")
        assert isinstance(physics_integration.LOGGING_AVAILABLE, bool)

    def test_logger_exists(self):
        """Test logger is configured."""
        from agents.physics_integration import logger

        assert logger is not None, "logger must be initialized"
        assert logger.name == "agents.physics_integration", "name is not valid"

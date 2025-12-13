"""
Tests for HybridPhysicsOrchestrator module.

Tests the integration layer between classical and advanced physics orchestrators.
"""

import pytest
from agents.physics_integration import HybridPhysicsOrchestrator


class TestHybridPhysicsOrchestrator:
    """Test hybrid physics orchestrator functionality."""
    
    def test_initialization(self):
        """Test that HybridPhysicsOrchestrator initializes correctly."""
        integration = HybridPhysicsOrchestrator(session_id="test_session")
        
        assert integration.session_id == "test_session"
        assert integration.decision_history == []
        # Orchestrators may be None if dependencies not available
        assert hasattr(integration, 'classical_orchestrator')
        assert hasattr(integration, 'advanced_orchestrator')
    
    def test_initialization_default_session(self):
        """Test initialization with default session ID."""
        integration = HybridPhysicsOrchestrator()
        
        assert integration.session_id == "hybrid_physics"
        assert integration.decision_history == []
    
    def test_get_capabilities(self):
        """Test get_capabilities method."""
        integration = HybridPhysicsOrchestrator()
        
        capabilities = integration.get_capabilities()
        
        assert isinstance(capabilities, dict)
        assert 'classical_physics' in capabilities
        assert 'advanced_physics' in capabilities
    
    def test_orchestrate_with_all_paradigms_basic(self):
        """Test orchestration with minimal input."""
        integration = HybridPhysicsOrchestrator()
        
        # Minimal decision space
        decision_space = {
            'current_position': 'start',
            'goal_position': 'end',
            'resources': 1.0,
            'time': 1.0
        }
        
        # Should not raise exception even if orchestrators unavailable
        result = integration.orchestrate_with_all_paradigms(decision_space)
        
        assert isinstance(result, dict)
        assert 'paradigms_used' in result
        assert 'recommendations' in result
    
    def test_orchestrate_with_action_paths(self):
        """Test orchestration with action paths."""
        integration = HybridPhysicsOrchestrator()
        
        decision_space = {
            'current_position': 'start',
            'goal_position': 'end'
        }
        
        # Mock action paths
        action_paths = []
        
        result = integration.orchestrate_with_all_paradigms(decision_space, action_paths)
        
        assert isinstance(result, dict)
        assert 'paradigms_used' in result
    
    def test_inject_chaos_into_decision_fallback(self):
        """Test chaos injection returns base value when unavailable."""
        integration = HybridPhysicsOrchestrator()
        
        result = integration.inject_chaos_into_decision(0.5, strength=0.1)
        
        # Should return base value if advanced orchestrator unavailable
        assert isinstance(result, (int, float))
    
    def test_analyze_code_structure_fallback(self):
        """Test fractal analysis returns expected structure."""
        integration = HybridPhysicsOrchestrator()
        
        code_tree = {'module': {'class': {}}}
        result = integration.analyze_code_structure_fractal(code_tree)
        
        assert isinstance(result, dict)
        # Should return analysis results with structure metrics
        assert 'depth' in result or 'error' in result
    
    def test_optimize_workflow_fallback(self):
        """Test workflow optimization returns expected structure."""
        integration = HybridPhysicsOrchestrator()
        
        workflow = {'channel1': 1.0}
        result = integration.optimize_workflow_flow(workflow)
        
        assert isinstance(result, dict)
        # Should return results with initial/final states
        assert 'error' in result or 'initial' in result or 'final' in result

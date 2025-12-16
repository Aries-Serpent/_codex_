"""
Smoke Tests for Production Readiness Targets

These tests verify basic functionality of critical modules to ensure
the system is in a working state. They are designed to run quickly
and catch obvious regressions.

Run with: pytest tests/smoke/test_readiness_smoke.py -v
"""

import pytest
from pathlib import Path


class TestAgentMemorySmoke:
    """Smoke tests for AgentMemory module."""
    
    def test_memory_import(self):
        """Test that AgentMemory can be imported."""
        from agents.agent_memory import AgentMemory
        assert AgentMemory is not None
    
    def test_memory_creation(self):
        """Test basic memory instance creation."""
        from agents.agent_memory import AgentMemory
        memory = AgentMemory()
        assert memory is not None
    
    def test_memory_store_retrieve(self):
        """Test basic store and retrieve operations."""
        from agents.agent_memory import AgentMemory
        memory = AgentMemory()
        
        # Store a value
        memory.store_memory(key="test_key", value="test_value")
        
        # Retrieve it
        result = memory.retrieve_memory(key="test_key")
        assert result == "test_value"
    
    def test_memory_update(self):
        """Test memory update operations."""
        from agents.agent_memory import AgentMemory
        memory = AgentMemory()
        
        # Store initial value
        memory.store_memory(key="counter", value="1")
        
        # Update it
        memory.store_memory(key="counter", value="2")
        
        # Verify update
        result = memory.retrieve_memory(key="counter")
        assert result == "2"


class TestPhysicsOrchestratorSmoke:
    """Smoke tests for PhysicsOrchestrator module."""
    
    def test_orchestrator_import(self):
        """Test that PhysicsOrchestrator can be imported."""
        from agents.physics_orchestrator import PhysicsOrchestrator
        assert PhysicsOrchestrator is not None
    
    def test_orchestrator_creation(self):
        """Test basic orchestrator instance creation."""
        from agents.physics_orchestrator import PhysicsOrchestrator
        orchestrator = PhysicsOrchestrator()
        assert orchestrator is not None
    
    def test_decision_state_creation(self):
        """Test DecisionState creation."""
        from agents.physics_orchestrator import DecisionState
        
        state = DecisionState(
            current_position="start",
            goal_position="end",
            available_resources=0.8
        )
        assert state is not None
        assert state.current_position == "start"
        assert state.goal_position == "end"
    
    def test_force_vector_creation(self):
        """Test ForceVector creation and magnitude calculation."""
        from agents.physics_orchestrator import ForceVector
        
        force = ForceVector(name="test", x=3.0, y=4.0, z=0.0)
        assert force is not None
        # Magnitude should be 5.0 (3-4-5 triangle)
        assert abs(force.magnitude - 5.0) < 0.001


class TestMentalMappingSmoke:
    """Smoke tests for MentalMapping module."""
    
    def test_mental_mapping_import(self):
        """Test that MentalMappingModel can be imported."""
        from agents.mental_mapping import MentalMappingModel, NodeType
        assert MentalMappingModel is not None
        assert NodeType is not None
    
    def test_model_creation(self):
        """Test basic model instance creation."""
        from agents.mental_mapping import MentalMappingModel
        model = MentalMappingModel()
        assert model is not None
    
    def test_node_creation(self):
        """Test creating nodes in the mental map."""
        from agents.mental_mapping import MentalMappingModel, NodeType
        
        model = MentalMappingModel()
        node = model.create_node(NodeType.CONCEPT, content="test concept")
        
        assert node is not None
        assert node.node_id is not None
        assert node.content == "test concept"
    
    def test_node_connection(self):
        """Test connecting nodes."""
        from agents.mental_mapping import MentalMappingModel, NodeType, EdgeType
        
        model = MentalMappingModel()
        node1 = model.create_node(NodeType.CONCEPT, content="concept1")
        node2 = model.create_node(NodeType.CONCEPT, content="concept2")
        
        edge = model.connect_nodes(
            source_id=node1.node_id,
            target_id=node2.node_id,
            edge_type=EdgeType.LEADS_TO
        )
        
        assert edge is not None


class TestWorkflowNavigatorSmoke:
    """Smoke tests for WorkflowNavigator module."""
    
    def test_navigator_import(self):
        """Test that WorkflowNavigator can be imported."""
        from agents.workflow_navigator import WorkflowNavigator, WorkflowStep
        assert WorkflowNavigator is not None
        assert WorkflowStep is not None
    
    def test_navigator_creation(self):
        """Test basic navigator instance creation."""
        from agents.workflow_navigator import WorkflowNavigator
        navigator = WorkflowNavigator()
        assert navigator is not None
    
    def test_workflow_creation(self):
        """Test creating a workflow."""
        from agents.workflow_navigator import WorkflowNavigator, WorkflowStep
        
        navigator = WorkflowNavigator()
        steps = [
            WorkflowStep(id="step1", action="Initialize"),
            WorkflowStep(id="step2", action="Process"),
        ]
        
        workflow_id = navigator.create_workflow("test_workflow", steps)
        assert workflow_id is not None
        assert workflow_id in navigator.workflows
    
    def test_workflow_navigation(self):
        """Test navigating through workflow steps."""
        from agents.workflow_navigator import WorkflowNavigator, WorkflowStep
        
        navigator = WorkflowNavigator()
        steps = [
            WorkflowStep(id="step1", action="First"),
            WorkflowStep(id="step2", action="Second"),
        ]
        
        workflow_id = navigator.create_workflow("nav_test", steps)
        navigator.current_workflow_id = workflow_id
        
        # Check current step
        current = navigator.current_step()
        assert current.action == "First"
        
        # Navigate to next
        next_step = navigator.next_step()
        assert next_step.action == "Second"


class TestAdvancedPhysicsSmoke:
    """Smoke tests for Advanced Physics Calculators."""
    
    def test_import_without_numpy(self):
        """Test graceful handling when numpy is not available."""
        # This should not crash even if numpy is missing
        try:
            from agents.advanced_physics_calculators import ChaoticAttractor
            assert ChaoticAttractor is not None
        except ImportError as e:
            # If import fails, it should be due to missing optional dependency
            assert "numpy" in str(e).lower() or "scipy" in str(e).lower()
    
    def test_chaotic_attractor_creation(self):
        """Test ChaoticAttractor creation (requires numpy)."""
        pytest.importorskip("numpy")
        from agents.advanced_physics_calculators import ChaoticAttractor
        
        attractor = ChaoticAttractor(attractor_type="logistic")
        assert attractor is not None
        assert attractor.attractor_type == "logistic"


class TestQuantumGameTheorySmoke:
    """Smoke tests for Quantum Game Theory module."""
    
    def test_quantum_import(self):
        """Test that quantum modules can be imported."""
        from agents.quantum_game_theory import QuantumGameState, StrategyState
        assert QuantumGameState is not None
        assert StrategyState is not None
    
    def test_strategy_state_creation(self):
        """Test StrategyState creation."""
        from agents.quantum_game_theory import StrategyState, TeamType
        
        state = StrategyState(team=TeamType.BLUE, strategies=["cooperate", "defect"])
        assert state is not None
        assert state.team == TeamType.BLUE


class TestExceptionHandlingSmoke:
    """Smoke tests for exception handling."""
    
    def test_agent_error_import(self):
        """Test that custom exceptions can be imported."""
        from agents.exceptions import (
            AgentError,
            AgentImportError,
            AgentConfigError,
            AgentValidationError
        )
        assert all([
            AgentError,
            AgentImportError,
            AgentConfigError,
            AgentValidationError
        ])
    
    def test_agent_import_error_message(self):
        """Test AgentImportError provides helpful message."""
        from agents.exceptions import AgentImportError
        
        error = AgentImportError("test_module", package_name="test-package")
        message = str(error)
        
        assert "test_module" in message
        assert "pip install" in message
        assert "test-package" in message


class TestIntegrationSmoke:
    """High-level integration smoke tests."""
    
    def test_memory_with_physics(self):
        """Test AgentMemory integration with PhysicsOrchestrator."""
        from agents.agent_memory import AgentMemory
        from agents.physics_orchestrator import DecisionState
        
        memory = AgentMemory()
        state = DecisionState(
            current_position="location_A",
            goal_position="location_B",
            available_resources=0.75
        )
        
        # Store physics state in memory
        memory.store_memory(key="physics_state", value=state.current_position)
        
        # Retrieve it
        retrieved = memory.retrieve_memory(key="physics_state")
        assert retrieved == "location_A"
    
    def test_workflow_with_memory(self):
        """Test WorkflowNavigator integration with AgentMemory."""
        from agents.workflow_navigator import WorkflowNavigator, WorkflowStep
        from agents.agent_memory import AgentMemory
        
        navigator = WorkflowNavigator()
        memory = AgentMemory()
        
        # Create workflow
        steps = [WorkflowStep(id="s1", action="Action1")]
        wf_id = navigator.create_workflow("test", steps)
        
        # Store workflow ID in memory
        memory.store_memory(key="current_workflow", value=wf_id)
        
        # Retrieve and verify
        retrieved_id = memory.retrieve_memory(key="current_workflow")
        assert retrieved_id == wf_id
    
    def test_mental_map_with_memory(self):
        """Test MentalMapping integration with AgentMemory."""
        from agents.mental_mapping import MentalMappingModel, NodeType
        from agents.agent_memory import AgentMemory
        
        model = MentalMappingModel()
        memory = AgentMemory()
        
        # Create node
        node = model.create_node(NodeType.CONCEPT, content="test")
        
        # Store node ID in memory
        memory.store_memory(key="concept_node", value=node.node_id)
        
        # Retrieve and verify
        retrieved_id = memory.retrieve_memory(key="concept_node")
        assert retrieved_id == node.node_id


# Readiness checkpoint marker
def test_readiness_checkpoint():
    """
    Meta-test that verifies all critical modules are importable.
    This is a checkpoint to ensure the system meets basic readiness criteria.
    """
    required_modules = [
        "agents.agent_memory",
        "agents.physics_orchestrator",
        "agents.mental_mapping",
        "agents.workflow_navigator",
        "agents.exceptions",
    ]
    
    failed_imports = []
    for module_name in required_modules:
        try:
            __import__(module_name)
        except ImportError as e:
            failed_imports.append((module_name, str(e)))
    
    assert not failed_imports, f"Failed to import critical modules: {failed_imports}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

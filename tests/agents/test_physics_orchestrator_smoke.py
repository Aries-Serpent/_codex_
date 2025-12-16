"""
Smoke tests for agents/physics_orchestrator.py to improve coverage from 24.71% to 85%+

Targets:
- PhysicsInspiredOrchestrator class and all public methods
- Decision state transitions  
- Force vector calculations
- Equilibrium computation
- Path optimization logic
"""

import pytest
from typing import List, Dict, Any
import math


class TestPhysicsOrchestratorInitialization:
    """Test initialization and basic setup."""
    
    def test_orchestrator_init_default(self):
        """Test default initialization."""
        from agents.physics_orchestrator import PhysicsInspiredOrchestrator
        
        orch = PhysicsInspiredOrchestrator()
        assert orch is not None
        
    def test_orchestrator_with_config(self):
        """Test initialization with config file."""
        from agents.physics_orchestrator import PhysicsInspiredOrchestrator
        
        # Initialize with default config
        orch = PhysicsInspiredOrchestrator()
        assert hasattr(orch, 'config')


class TestForceVectorOperations:
    """Test ForceVector calculations and operations."""
    
    def test_force_vector_components_2d(self):
        """Test 2D force vector component calculation."""
        from agents.physics_orchestrator import ForceVector
        
        force = ForceVector(
            name="test_force",
            magnitude=10.0,
            direction=0.0,  # 0 radians = pointing right
            priority=1.0
        )
        
        x, y = force.get_components()
        assert abs(x - 10.0) < 0.01  # cos(0) = 1
        assert abs(y) < 0.01  # sin(0) = 0
        
    def test_force_vector_components_45deg(self):
        """Test force vector at 45 degrees."""
        from agents.physics_orchestrator import ForceVector
        
        force = ForceVector(
            name="diagonal_force",
            magnitude=10.0,
            direction=math.pi / 4,  # 45 degrees
            priority=1.0
        )
        
        x, y = force.get_components()
        # At 45 degrees, x and y should be equal
        assert abs(x - y) < 0.01
        assert abs(x - 10.0 * math.cos(math.pi/4)) < 0.01
        
    def test_force_vector_components_3d(self):
        """Test 3D force vector projection."""
        from agents.physics_orchestrator import ForceVector
        
        force = ForceVector(
            name="3d_force",
            magnitude=5.0,
            direction=[1.0, 2.0, 3.0],  # 3D vector
            priority=2.0
        )
        
        x, y = force.get_components()
        # 3D vectors project to 2D
        assert x == 5.0 * 2.0  # magnitude * priority
        assert y == 0.0


class TestActionPathCalculations:
    """Test ActionPath energy and optimization score calculations."""
    
    def test_action_path_total_energy(self):
        """Test total energy calculation."""
        from agents.physics_orchestrator import ActionPath, ActionType
        
        path = ActionPath(
            action_type=ActionType.TEST,
            description="Test path",
            potential_energy=50.0,
            kinetic_energy=30.0,
            friction=2.0,
            momentum=3.0
        )
        
        total = path.calculate_total_energy()
        # E_total = 50 + 30 - (3 * 5) + (2 * 10) = 50 + 30 - 15 + 20 = 85
        assert total == 85.0
        assert path.total_energy == 85.0
        
    def test_action_path_optimization_score(self):
        """Test optimization score calculation."""
        from agents.physics_orchestrator import ActionPath, ActionType
        
        path = ActionPath(
            action_type=ActionType.OPTIMIZE,
            description="Optimization path",
            potential_energy=10.0,
            kinetic_energy=5.0,
            friction=1.0,
            momentum=2.0,
            impact=0.8,
            confidence=0.9,
            risk=0.2,
            urgency=0.5
        )
        
        path.calculate_total_energy()
        score = path.calculate_optimization_score()
        
        # Score should be positive
        assert score > 0
        assert path.optimization_score == score
        
    def test_action_path_zero_energy_handling(self):
        """Test handling of zero/near-zero energy."""
        from agents.physics_orchestrator import ActionPath, ActionType
        
        path = ActionPath(
            action_type=ActionType.DEBUG,
            description="Low energy path",
            potential_energy=0.0,
            kinetic_energy=0.0,
            friction=0.0,
            momentum=0.0,
            impact=1.0,
            confidence=1.0,
            risk=0.0,
            urgency=0.0
        )
        
        path.calculate_total_energy()
        score = path.calculate_optimization_score()
        
        # Should not raise division by zero
        assert score is not None
        assert score > 0  # Due to minimum denominator of 0.01


class TestDecisionStateOperations:
    """Test DecisionState creation and manipulation."""
    
    def test_decision_state_creation(self):
        """Test creating a decision state."""
        from agents.physics_orchestrator import DecisionState
        
        state = DecisionState(
            current_position="task_a",
            goal_position="task_b",
            available_resources=0.8,
            time_available=0.6,
            current_velocity=0.5
        )
        
        assert state.current_position == "task_a"
        assert state.goal_position == "task_b"
        assert state.available_resources == 0.8
        assert state.time_available == 0.6
        assert state.current_velocity == 0.5
        
    def test_decision_state_with_context(self):
        """Test decision state with context dictionary."""
        from agents.physics_orchestrator import DecisionState
        
        state = DecisionState(
            current_position="start",
            goal_position="end",
            context={"priority": "high", "department": "engineering"}
        )
        
        assert "priority" in state.context
        assert state.context["priority"] == "high"
        assert state.context["department"] == "engineering"
        
    def test_decision_state_with_forces(self):
        """Test decision state with active forces."""
        from agents.physics_orchestrator import DecisionState, ForceVector
        
        forces = [
            ForceVector(name="urgency", magnitude=5.0, direction=0.0),
            ForceVector(name="importance", magnitude=7.0, direction=math.pi/2)
        ]
        
        state = DecisionState(
            current_position="planning",
            goal_position="execution",
            active_forces=forces
        )
        
        assert len(state.active_forces) == 2
        assert state.active_forces[0].name == "urgency"


class TestPhysicsOrchestratorDecisionMaking:
    """Test core decision-making functionality."""
    
    def test_assess_situation_basic(self):
        """Test basic situation assessment."""
        from agents.physics_orchestrator import PhysicsInspiredOrchestrator, DecisionState
        
        orch = PhysicsInspiredOrchestrator()
        
        state = DecisionState(
            current_position="backlog",
            goal_position="production",
            available_resources=0.8
        )
        
        # Assess the situation
        assessment = orch.assess_situation(state)
        
        assert assessment is not None
        assert isinstance(assessment, dict)
        
    def test_orchestrate_decision_simple(self):
        """Test simple orchestration."""
        from agents.physics_orchestrator import (
            PhysicsInspiredOrchestrator,
            DecisionState,
            ActionPath,
            ActionType
        )
        
        orch = PhysicsInspiredOrchestrator()
        
        state = DecisionState(
            current_position="backlog",
            goal_position="production"
        )
        
        paths = [
            ActionPath(
                action_type=ActionType.TEST,
                description="Write tests"
            )
        ]
        
        # Request orchestration
        result = orch.orchestrate(state, paths)
        
        assert result is not None
        
    def test_optimize_path_selection(self):
        """Test path optimization."""
        from agents.physics_orchestrator import (
            PhysicsInspiredOrchestrator,
            ActionPath,
            ActionType
        )
        
        orch = PhysicsInspiredOrchestrator()
        
        paths = [
            ActionPath(
                action_type=ActionType.TEST,
                description="Write tests",
                potential_energy=20.0,
                impact=0.7,
                confidence=0.9,
                risk=0.1
            ),
            ActionPath(
                action_type=ActionType.DEPLOY,
                description="Deploy to production",
                potential_energy=50.0,
                impact=0.9,
                confidence=0.6,
                risk=0.5
            ),
            ActionPath(
                action_type=ActionType.REFACTOR,
                description="Refactor code",
                potential_energy=30.0,
                impact=0.5,
                confidence=0.8,
                risk=0.2
            )
        ]
        
        # Calculate scores for all paths
        for path in paths:
            path.calculate_total_energy()
            path.calculate_optimization_score()
        
        # Find best path
        best_path = max(paths, key=lambda p: p.optimization_score)
        
        assert best_path is not None
        assert best_path.optimization_score > 0


class TestActionTypeEnum:
    """Test ActionType enum operations."""
    
    def test_action_type_values(self):
        """Test all ActionType enum values."""
        from agents.physics_orchestrator import ActionType
        
        # Verify expected action types exist
        assert ActionType.AUDIT is not None
        assert ActionType.REFACTOR is not None
        assert ActionType.TEST is not None
        assert ActionType.DEPLOY is not None
        
    def test_action_type_string_values(self):
        """Test ActionType string representations."""
        from agents.physics_orchestrator import ActionType
        
        assert ActionType.AUDIT.value == "audit"
        assert ActionType.TEST.value == "test"
        assert ActionType.DEPLOY.value == "deploy"
        
    def test_action_type_iteration(self):
        """Test iterating over ActionType enum."""
        from agents.physics_orchestrator import ActionType
        
        action_types = list(ActionType)
        
        assert len(action_types) >= 5  # Should have multiple action types
        assert all(isinstance(at, ActionType) for at in action_types)


class TestPhysicsOrchestratorEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_context(self):
        """Test with empty context."""
        from agents.physics_orchestrator import DecisionState
        
        state = DecisionState(
            current_position="a",
            goal_position="b",
            context={}
        )
        
        assert state.context == {}
        
    def test_zero_resources(self):
        """Test with zero available resources."""
        from agents.physics_orchestrator import DecisionState
        
        state = DecisionState(
            current_position="start",
            goal_position="end",
            available_resources=0.0
        )
        
        assert state.available_resources == 0.0
        
    def test_force_vector_zero_magnitude(self):
        """Test force vector with zero magnitude."""
        from agents.physics_orchestrator import ForceVector
        
        force = ForceVector(
            name="zero_force",
            magnitude=0.0,
            direction=0.0
        )
        
        x, y = force.get_components()
        assert x == 0.0
        assert y == 0.0
        
    def test_action_path_high_risk(self):
        """Test action path with very high risk."""
        from agents.physics_orchestrator import ActionPath, ActionType
        
        path = ActionPath(
            action_type=ActionType.EXECUTE,
            description="High risk path",
            risk=0.95,
            impact=0.5,
            confidence=0.5
        )
        
        path.calculate_total_energy()
        score = path.calculate_optimization_score()
        
        # High risk should reduce score
        assert score >= 0

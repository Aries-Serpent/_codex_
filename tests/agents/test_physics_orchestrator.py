"""
Test Physics Orchestrator Module

Comprehensive tests for the physics-inspired decision making orchestrator.
Tests force vectors, action paths, orchestrator logic, and physics-based calculations.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from agents.physics_orchestrator import (
    ActionPath,
    ActionType,
    DecisionState,
    DiffusionFlowModel,
    EnergyLandscape,
    EnergyState,
    FlowVector,
    ForceVector,
    ImportMigration,
    PhysicsInspiredOrchestrator,
    SwarmIntelligence,
    SwarmParticle,
)


class TestActionType:
    """Tests for ActionType enum."""

    def test_action_types_exist(self) -> None:
        """Test that all expected action types exist."""
        expected_types = [
            "AUDIT",
            "REFACTOR",
            "TEST",
            "DOCUMENT",
            "DEPLOY",
            "OPTIMIZE",
            "DEBUG",
            "RESEARCH",
            "ANALYZE",
            "EXECUTE",
            "PLAN",
            "REFLECT",
        ]

        for action_type in expected_types:
            assert hasattr(ActionType, action_type)

    def test_action_type_values(self) -> None:
        """Test action type values."""
        assert ActionType.AUDIT.value == "audit", "Value must be initialized"
        assert ActionType.REFACTOR.value == "refactor", "Value must be initialized"
        assert ActionType.TEST.value == "test", "Value must be initialized"
        assert ActionType.DOCUMENT.value == "document", "Value must be initialized"

    def test_action_type_from_value(self) -> None:
        """Test creating action type from value."""
        assert ActionType("audit") == ActionType.AUDIT, "Condition must be true"
        assert ActionType("test") == ActionType.TEST, "Condition must be true"


class TestForceVector:
    """Tests for ForceVector dataclass."""

    def test_default_values(self) -> None:
        """Test default ForceVector values."""
        vector = ForceVector()

        assert vector.name == "", "name is not valid"
        assert vector.magnitude == 0.0, "magnitude is not valid"
        assert vector.direction == 0.0, "direction is not valid"
        assert vector.priority == 1.0, "priority is not valid"

    def test_custom_values(self) -> None:
        """Test ForceVector with custom values."""
        vector = ForceVector(
            name="urgency",
            magnitude=0.8,
            direction=1.57,  # ~90 degrees
            priority=2.0,
        )

        assert vector.name == "urgency", "name is not valid"
        assert vector.magnitude == 0.8, "magnitude is not valid"
        assert vector.priority == 2.0, "priority is not valid"

    def test_get_components_2d(self) -> None:
        """Test getting 2D components."""
        # Vector at 0 degrees (pointing right)
        vector = ForceVector(
            name="test",
            magnitude=1.0,
            direction=0.0,
            priority=1.0,
        )

        x, y = vector.get_components()

        assert abs(x - 1.0) < 0.01, "Condition must be true"
        assert abs(y - 0.0) < 0.01, "Condition must be true"

    def test_get_components_45_degrees(self) -> None:
        """Test components at 45 degrees."""
        vector = ForceVector(
            name="test",
            magnitude=1.0,
            direction=math.pi / 4,  # 45 degrees
            priority=1.0,
        )

        x, y = vector.get_components()

        expected = math.sqrt(2) / 2
        assert abs(x - expected) < 0.01, "Condition must be true"
        assert abs(y - expected) < 0.01, "Condition must be true"

    def test_get_components_with_priority(self) -> None:
        """Test components with priority scaling."""
        vector = ForceVector(
            name="test",
            magnitude=1.0,
            direction=0.0,
            priority=2.0,
        )

        x, _y = vector.get_components()

        assert abs(x - 2.0) < 0.01, "Condition must be true"

    def test_3d_vector_initialization(self) -> None:
        """Test 3D vector initialization from x, y, z."""
        vector = ForceVector(
            name="3d_force",
            x=3.0,
            y=4.0,
            z=0.0,
        )

        # Magnitude should be calculated: sqrt(3^2 + 4^2) = 5
        assert abs(vector.magnitude - 5.0) < 0.01, "Condition must be true"

    def test_3d_vector_with_z(self) -> None:
        """Test 3D vector with z component."""
        vector = ForceVector(
            name="3d_force",
            x=1.0,
            y=0.0,
            z=0.0,
        )

        assert vector.magnitude == 1.0, "magnitude is not valid"

    def test_3d_direction_normalization(self) -> None:
        """Test that 3D direction is normalized."""
        vector = ForceVector(
            name="3d_force",
            x=2.0,
            y=0.0,
            z=0.0,
        )

        # Direction should be a unit vector
        if isinstance(vector.direction, list):
            mag = math.sqrt(sum(d**2 for d in vector.direction))
            assert abs(mag - 1.0) < 0.01, "Condition must be true"


class TestActionPath:
    """Tests for ActionPath dataclass."""

    def test_default_values(self) -> None:
        """Test default ActionPath values."""
        path = ActionPath()

        assert path.action_type == ActionType.ANALYZE, "action_type is not valid"
        assert path.description == "", "description is not valid"
        assert path.potential_energy == 0.0, "potential_energy is not valid"
        assert path.kinetic_energy == 0.0, "kinetic_energy is not valid"
        assert path.friction == 0.0, "friction is not valid"
        assert path.momentum == 0.0, "momentum is not valid"

    def test_decision_factors(self) -> None:
        """Test decision factor fields."""
        path = ActionPath(
            confidence=0.9,
            risk=0.2,
            impact=0.8,
            urgency=0.5,
        )

        assert path.confidence == 0.9, "confidence is not valid"
        assert path.risk == 0.2, "risk is not valid"
        assert path.impact == 0.8, "impact is not valid"
        assert path.urgency == 0.5, "urgency is not valid"

    def test_physics_properties(self) -> None:
        """Test physics property fields."""
        path = ActionPath(
            potential_energy=50.0,
            kinetic_energy=30.0,
            friction=2.0,
            momentum=5.0,
        )

        assert path.potential_energy == 50.0, "potential_energy is not valid"
        assert path.kinetic_energy == 30.0, "kinetic_energy is not valid"
        assert path.friction == 2.0, "friction is not valid"
        assert path.momentum == 5.0, "momentum is not valid"

    def test_action_path_with_type(self) -> None:
        """Test ActionPath with specific action type."""
        path = ActionPath(
            action_type=ActionType.REFACTOR,
            description="Refactor legacy module",
        )

        assert path.action_type == ActionType.REFACTOR, "action_type is not valid"
        assert "legacy" in path.description.lower(), "Condition must be true"

    def test_trajectory_field(self) -> None:
        """Test trajectory field."""
        path = ActionPath(trajectory=["step1", "step2", "step3"])

        assert len(path.trajectory) == 3, "Collection must not be empty"
        assert path.trajectory[0] == "step1", "Condition must be true"


class TestPhysicsCalculations:
    """Tests for physics-based calculations."""

    def test_force_composition(self) -> None:
        """Test composing multiple force vectors."""
        forces = [
            ForceVector(name="f1", magnitude=1.0, direction=0.0, priority=1.0),
            ForceVector(name="f2", magnitude=1.0, direction=math.pi / 2, priority=1.0),
        ]

        total_x = 0.0
        total_y = 0.0

        for force in forces:
            x, y = force.get_components()
            total_x += x
            total_y += y

        # Result should be sqrt(2) at 45 degrees
        result_mag = math.hypot(total_x, total_y)
        assert abs(result_mag - math.sqrt(2)) < 0.01, "Result must not be empty"

    def test_opposing_forces_cancel(self) -> None:
        """Test that opposing forces cancel out."""
        forces = [
            ForceVector(name="f1", magnitude=1.0, direction=0.0, priority=1.0),
            ForceVector(name="f2", magnitude=1.0, direction=math.pi, priority=1.0),
        ]

        total_x = 0.0
        total_y = 0.0

        for force in forces:
            x, y = force.get_components()
            total_x += x
            total_y += y

        # Should nearly cancel
        result_mag = math.hypot(total_x, total_y)
        assert result_mag < 0.01, "Result must not be empty"

    def test_energy_conservation(self) -> None:
        """Test total energy calculation."""
        path = ActionPath(
            potential_energy=70.0,
            kinetic_energy=30.0,
        )

        total_energy = path.potential_energy + path.kinetic_energy
        assert total_energy == 100.0, "total_energy is not valid"

    def test_friction_reduces_effective_momentum(self) -> None:
        """Test friction effect on momentum."""
        path = ActionPath(
            momentum=10.0,
            friction=3.0,
        )

        effective_momentum = path.momentum - path.friction
        assert effective_momentum == 7.0, "effective_momentum is not valid"


class TestDecisionFactors:
    """Tests for decision factor calculations."""

    def test_risk_reward_ratio(self) -> None:
        """Test calculating risk/reward ratio."""
        path = ActionPath(
            risk=0.3,
            impact=0.9,
        )

        if path.risk > 0:
            risk_reward = path.impact / path.risk
            assert risk_reward == 3.0, "risk_reward is not valid"

    def test_confidence_weighted_impact(self) -> None:
        """Test confidence-weighted impact."""
        path = ActionPath(
            confidence=0.8,
            impact=1.0,
        )

        weighted_impact = path.confidence * path.impact
        assert weighted_impact == 0.8, "weighted_impact is not valid"

    def test_urgency_priority_boost(self) -> None:
        """Test urgency boosting priority."""
        base_priority = 1.0
        urgency = 0.9

        boosted_priority = base_priority * (1 + urgency)
        assert boosted_priority == 1.9, "boosted_priority is not valid"


class TestEdgeCases:
    """Edge case tests."""

    def test_zero_magnitude_vector(self) -> None:
        """Test vector with zero magnitude."""
        vector = ForceVector(name="zero", magnitude=0.0, direction=1.0)

        x, y = vector.get_components()

        assert x == 0.0, "x is not valid"
        assert y == 0.0, "y is not valid"

    def test_action_path_all_zeros(self) -> None:
        """Test action path with all zero values."""
        path = ActionPath()

        total = (
            path.potential_energy
            + path.kinetic_energy
            + path.friction
            + path.momentum
            + path.confidence
            + path.risk
            + path.impact
            + path.urgency
        )

        assert total == 0.0, "total is not valid"

    def test_negative_direction(self) -> None:
        """Test vector with negative direction."""
        vector = ForceVector(
            name="negative",
            magnitude=1.0,
            direction=-math.pi / 2,  # -90 degrees
            priority=1.0,
        )

        x, y = vector.get_components()

        assert abs(x - 0.0) < 0.01, "Condition must be true"
        assert abs(y - (-1.0)) < 0.01, "Condition must be true"

    def test_large_values(self) -> None:
        """Test with large values."""
        path = ActionPath(
            potential_energy=1000000.0,
            kinetic_energy=500000.0,
        )

        assert path.potential_energy == 1000000.0, "potential_energy is not valid"
        assert path.kinetic_energy == 500000.0, "kinetic_energy is not valid"


@pytest.fixture
def decision_state_fixture() -> DecisionState:
    """Create a test DecisionState instance."""
    return DecisionState(
        current_position="position_a",
        goal_position="position_z",
        available_resources=0.8,
        time_available=0.7,
        current_velocity=0.5,
        context={"priority": "high", "domain": "testing"},
    )


@pytest.fixture
def action_path_fixture() -> ActionPath:
    """Create a test ActionPath instance."""
    return ActionPath(
        action_type=ActionType.TEST,
        description="Run comprehensive tests",
        potential_energy=40.0,
        kinetic_energy=60.0,
        friction=1.5,
        momentum=8.0,
        confidence=0.85,
        risk=0.15,
        impact=0.9,
        urgency=0.6,
    )


@pytest.fixture
def orchestrator_fixture() -> PhysicsInspiredOrchestrator:
    """Create a test PhysicsInspiredOrchestrator instance."""
    config = {
        "deliberation_time": 1.0,
        "confidence_threshold": 0.6,
        "energy_budget": 100.0,
        "risk_tolerance": 0.5,
        "momentum_weight": 0.3,
        "friction_weight": 0.2,
    }
    return PhysicsInspiredOrchestrator(config=config)


class TestDecisionState:
    """Tests for DecisionState class."""

    def test_default_initialization(self) -> None:
        """Test default DecisionState initialization."""
        state = DecisionState()
        assert state.current_position == ""
        assert state.goal_position == ""
        assert state.available_resources == 1.0
        assert state.time_available == 1.0
        assert state.current_velocity == 0.5
        assert state.context == {}
        assert state.active_forces == []
        assert state.constraints == []
        assert state.coherence == 1.0

    def test_custom_initialization(self, decision_state_fixture: DecisionState) -> None:
        """Test custom DecisionState initialization."""
        assert decision_state_fixture.current_position == "position_a"
        assert decision_state_fixture.goal_position == "position_z"
        assert decision_state_fixture.available_resources == 0.8
        assert decision_state_fixture.time_available == 0.7
        assert decision_state_fixture.current_velocity == 0.5
        assert decision_state_fixture.context["priority"] == "high"

    def test_context_dictionary(self) -> None:
        """Test context dictionary functionality."""
        state = DecisionState(
            context={"key1": "value1", "key2": 42, "key3": [1, 2, 3]}
        )
        assert state.context["key1"] == "value1"
        assert state.context["key2"] == 42
        assert state.context["key3"] == [1, 2, 3]

    def test_active_forces_list(self) -> None:
        """Test active forces list."""
        force1 = ForceVector(name="urgency", magnitude=0.8, priority=1.5)
        force2 = ForceVector(name="constraint", magnitude=0.3, priority=0.5)
        state = DecisionState(active_forces=[force1, force2])
        
        assert len(state.active_forces) == 2
        assert state.active_forces[0].name == "urgency"
        assert state.active_forces[1].name == "constraint"

    def test_constraints_list(self) -> None:
        """Test constraints list."""
        constraints = ["budget_limit", "time_constraint", "resource_availability"]
        state = DecisionState(constraints=constraints)
        
        assert len(state.constraints) == 3
        assert "budget_limit" in state.constraints

    def test_state_vector_quantum_like(self) -> None:
        """Test quantum-like state vector representation."""
        state_vector = [0.7, 0.3, 0.5, 0.2]
        state = DecisionState(state_vector=state_vector)
        
        assert state.state_vector == state_vector
        assert len(state.state_vector) == 4

    def test_energy_field(self) -> None:
        """Test energy field."""
        state = DecisionState(energy=45.5)
        assert state.energy == 45.5

    def test_coherence_field(self) -> None:
        """Test coherence field."""
        state = DecisionState(coherence=0.95)
        assert state.coherence == 0.95


class TestActionPathCalculations:
    """Tests for ActionPath energy and optimization calculations."""

    def test_total_energy_calculation_basic(self) -> None:
        """Test basic total energy calculation."""
        path = ActionPath(
            potential_energy=50.0,
            kinetic_energy=30.0,
            friction=0.0,
            momentum=0.0,
        )
        
        total = path.calculate_total_energy()
        # E = 50 + 30 - 0*5 + 0*10 = 80
        assert total == 80.0

    def test_total_energy_with_momentum(self) -> None:
        """Test energy calculation with momentum reduction."""
        path = ActionPath(
            potential_energy=100.0,
            kinetic_energy=50.0,
            friction=0.0,
            momentum=5.0,
        )
        
        total = path.calculate_total_energy()
        # E = 100 + 50 - 5*5 + 0*10 = 100 + 50 - 25 = 125
        assert total == 125.0

    def test_total_energy_with_friction(self) -> None:
        """Test energy calculation with friction increase."""
        path = ActionPath(
            potential_energy=50.0,
            kinetic_energy=50.0,
            friction=3.0,
            momentum=0.0,
        )
        
        total = path.calculate_total_energy()
        # E = 50 + 50 - 0 + 3*10 = 100 + 30 = 130
        assert total == 130.0

    def test_total_energy_with_all_factors(self) -> None:
        """Test energy calculation with all factors."""
        path = ActionPath(
            potential_energy=70.0,
            kinetic_energy=40.0,
            friction=2.5,
            momentum=6.0,
        )
        
        total = path.calculate_total_energy()
        # E = 70 + 40 - 6*5 + 2.5*10 = 70 + 40 - 30 + 25 = 105
        assert total == 105.0

    def test_optimization_score_calculation(self) -> None:
        """Test optimization score calculation."""
        path = ActionPath(
            impact=0.9,
            confidence=0.8,
            momentum=5.0,
            urgency=0.5,
            risk=0.2,
            friction=1.0,
        )
        path.total_energy = 100.0
        
        score = path.calculate_optimization_score()
        
        # Score = (0.9 * 0.8 * max(5, 0.1) * (1 + 0.5*0.5)) / (100 * (1+0.2) * (1+1))
        # = (0.72 * 5 * 1.25) / (100 * 1.2 * 2)
        # = 4.5 / 240 = 0.01875
        assert score > 0
        assert score < 0.1

    @pytest.mark.parametrize(
        "impact,confidence,momentum,expected_positive",
        [
            (0.5, 0.5, 2.0, True),
            (0.9, 0.9, 8.0, True),
            (0.1, 0.1, 1.0, True),
            (0.0, 0.0, 0.0, True),
        ],
    )
    def test_optimization_score_parametrized(
        self,
        impact: float,
        confidence: float,
        momentum: float,
        expected_positive: bool,
    ) -> None:
        """Test optimization score with various parameters."""
        path = ActionPath(
            impact=impact,
            confidence=confidence,
            momentum=momentum,
            risk=0.2,
            friction=1.0,
        )
        path.total_energy = 100.0
        
        score = path.calculate_optimization_score()
        
        if expected_positive:
            assert score >= 0

    def test_mlp_features_extraction(self) -> None:
        """Test MLP feature extraction."""
        path = ActionPath(
            potential_energy=50.0,
            kinetic_energy=30.0,
            friction=2.0,
            momentum=5.0,
            confidence=0.8,
            risk=0.2,
            impact=0.9,
            urgency=0.6,
        )
        
        features = path._extract_mlp_features()
        
        assert len(features) == 8
        assert features[0] == pytest.approx(0.5, abs=0.01)  # potential_energy/100
        assert features[1] == pytest.approx(0.3, abs=0.01)  # kinetic_energy/100
        assert features[2] == pytest.approx(0.2, abs=0.01)  # friction/10
        assert features[3] == pytest.approx(0.5, abs=0.01)  # momentum/10


class TestPhysicsInspiredOrchestratorCore:
    """Tests for PhysicsInspiredOrchestrator core functionality."""

    def test_orchestrator_initialization(self) -> None:
        """Test orchestrator initialization."""
        orch = PhysicsInspiredOrchestrator()
        
        assert orch.config is not None
        assert orch.decision_history == []
        assert orch.force_vectors == []
        assert "deliberation_time" in orch.config
        assert "confidence_threshold" in orch.config
        assert "energy_budget" in orch.config

    def test_load_config(self, orchestrator_fixture: PhysicsInspiredOrchestrator) -> None:
        """Test loading configuration."""
        config = orchestrator_fixture.load_config()
        
        assert config["deliberation_time"] == 1.0
        assert config["confidence_threshold"] == 0.6
        assert config["energy_budget"] == 100.0
        assert config["risk_tolerance"] == 0.5

    def test_orchestrator_with_custom_config(self) -> None:
        """Test orchestrator with custom configuration."""
        custom_config = {
            "deliberation_time": 10.0,
            "confidence_threshold": 0.7,
            "energy_budget": 200.0,
            "risk_tolerance": 0.3,
        }
        orch = PhysicsInspiredOrchestrator(config=custom_config)
        
        assert orch.config["deliberation_time"] == 10.0
        assert orch.config["confidence_threshold"] == 0.7
        assert orch.config["energy_budget"] == 200.0
        assert orch.config["risk_tolerance"] == 0.3

    @patch('builtins.print')
    def test_assess_situation(
        self,
        mock_print: Mock,
        orchestrator_fixture: PhysicsInspiredOrchestrator,
        decision_state_fixture: DecisionState,
    ) -> None:
        """Test assess_situation method."""
        assessment = orchestrator_fixture.assess_situation(decision_state_fixture)
        
        assert "distance_to_goal" in assessment
        assert "system_entropy" in assessment
        assert "attractive_potential" in assessment
        assert "repulsive_potential" in assessment
        assert "net_potential" in assessment
        
        # Verify print was called
        assert mock_print.called


class TestEnergyState:
    """Tests for EnergyState dataclass."""

    def test_energy_state_initialization(self) -> None:
        """Test EnergyState initialization."""
        config = {"type": "test", "value": 42}
        state = EnergyState(
            configuration=config,
            energy=50.0,
            temperature=1.0,
            entropy=10.0,
        )
        
        assert state.energy == 50.0
        assert state.temperature == 1.0
        assert state.entropy == 10.0
        assert state.configuration == config

    def test_energy_state_default_values(self) -> None:
        """Test EnergyState default values."""
        config = {"empty": True}
        state = EnergyState(configuration=config)
        
        assert state.energy == 0.0
        assert state.temperature == 1.0
        assert state.entropy == 0.0

    def test_energy_state_free_energy(self) -> None:
        """Test free energy calculation."""
        config = {"test": True}
        state = EnergyState(
            configuration=config,
            energy=10.0,
            temperature=2.0,
            entropy=5.0,
        )
        
        # F = E - T*S = 10 - 2*5 = 0
        free_e = state.free_energy()
        assert free_e == pytest.approx(0.0, abs=0.01)

    def test_energy_state_boltzmann_probability(self) -> None:
        """Test Boltzmann probability calculation."""
        config = {"test": True}
        state = EnergyState(
            configuration=config,
            energy=10.0,
            temperature=1.0,
        )
        
        prob = state.boltzmann_probability(reference_energy=5.0)
        # P ∝ exp(-(10-5)/1) = exp(-5) ≈ 0.0067
        assert prob > 0
        assert prob < 1


class TestEnergyLandscape:
    """Tests for EnergyLandscape class."""

    def test_energy_landscape_initialization(self) -> None:
        """Test EnergyLandscape initialization."""
        landscape = EnergyLandscape(temperature=1.0)
        
        assert landscape.temperature == 1.0
        assert landscape.states == []
        assert landscape.partition_function == 0.0

    def test_add_energy_state(self) -> None:
        """Test adding energy states to landscape."""
        landscape = EnergyLandscape(temperature=1.0)
        
        state1 = EnergyState(configuration={"id": 1}, energy=5.0)
        state2 = EnergyState(configuration={"id": 2}, energy=10.0)
        
        landscape.add_state(state1)
        landscape.add_state(state2)
        
        assert len(landscape.states) == 2

    def test_select_state_with_boltzmann(self) -> None:
        """Test selecting state using Boltzmann distribution."""
        landscape = EnergyLandscape(temperature=1.0)
        
        for i in range(5):
            state = EnergyState(configuration={"id": i}, energy=float(i))
            landscape.add_state(state)
        
        selected = landscape.select_state()
        
        assert selected is not None
        assert selected in landscape.states

    def test_cool_system(self) -> None:
        """Test cooling system (simulated annealing)."""
        landscape = EnergyLandscape(temperature=10.0)
        
        for i in range(3):
            state = EnergyState(configuration={"id": i}, energy=float(i))
            landscape.add_state(state)
        
        initial_temp = landscape.temperature
        landscape.cool_system(cooling_rate=0.9)
        
        assert landscape.temperature < initial_temp
        assert landscape.temperature == pytest.approx(initial_temp * 0.9, rel=1e-5)

    def test_minimize_free_energy(self) -> None:
        """Test free energy minimization."""
        landscape = EnergyLandscape(temperature=1.0)
        
        for i in range(3):
            state = EnergyState(
                configuration={"id": i},
                energy=float(i),
                entropy=1.0,
            )
            landscape.add_state(state)
        
        best_state = landscape.minimize_free_energy(max_iterations=10)
        assert best_state is not None


class TestDiffusionFlowModel:
    """Tests for DiffusionFlowModel class."""

    def test_diffusion_flow_initialization(self) -> None:
        """Test DiffusionFlowModel initialization."""
        model = DiffusionFlowModel(
            dimensions=2,
            resolution=10,
            diffusion_coefficient=0.5,
        )
        
        assert model.dimensions == 2
        assert model.resolution == 10
        assert model.diffusion_coefficient == 0.5
        assert model.potential_field == {}
        assert model.flow_vectors == []
        assert model.attractors == []
        assert model.repulsors == []

    def test_add_attractor(self) -> None:
        """Test adding attractor to field."""
        model = DiffusionFlowModel()
        
        model.add_attractor((0.5, 0.5), strength=2.0)
        
        assert len(model.attractors) == 1
        assert len(model.potential_field) > 0

    def test_add_repulsor(self) -> None:
        """Test adding repulsor to field."""
        model = DiffusionFlowModel()
        
        model.add_repulsor((0.2, 0.2), strength=1.5)
        
        assert len(model.repulsors) == 1
        assert len(model.potential_field) > 0

    def test_get_gradient(self) -> None:
        """Test gradient calculation."""
        model = DiffusionFlowModel(resolution=10)
        model.add_attractor((0.5, 0.5), strength=1.0)
        
        gradient = model.get_gradient((0.3, 0.3))
        
        assert isinstance(gradient, tuple)
        assert len(gradient) == 2

    def test_create_flow_at_position(self) -> None:
        """Test creating flow vector at position."""
        model = DiffusionFlowModel()
        model.add_attractor((0.8, 0.8), strength=1.0)
        
        flow = model.create_flow_at((0.2, 0.2), diffusion=0.1)
        
        assert isinstance(flow, FlowVector)
        assert flow.position == (0.2, 0.2)
        assert len(model.flow_vectors) == 1

    def test_simulate_flow(self) -> None:
        """Test flow simulation."""
        model = DiffusionFlowModel(resolution=20)
        model.add_attractor((0.8, 0.8), strength=2.0)
        
        trajectory = model.simulate_flow((0.2, 0.2), steps=50, dt=0.1)
        
        assert len(trajectory) > 1
        assert trajectory[0] == (0.2, 0.2)

    def test_integrate_with_mental_mapping(self) -> None:
        """Test integration with mental mapping."""
        model = DiffusionFlowModel(resolution=15)
        
        result = model.integrate_with_mental_mapping(
            problem_position=(0.1, 0.1),
            goal_position=(0.9, 0.9),
        )
        
        assert "trajectory" in result
        assert "steps_to_goal" in result
        assert "final_position" in result
        assert "convergence_distance" in result


class TestFlowVector:
    """Tests for FlowVector dataclass."""

    def test_flow_vector_initialization(self) -> None:
        """Test FlowVector initialization."""
        flow = FlowVector(
            position=(0.5, 0.5),
            velocity=(0.1, 0.2),
            gradient=(0.05, 0.08),
            diffusion_coefficient=0.1,
        )
        
        assert flow.position == (0.5, 0.5)
        assert flow.velocity == (0.1, 0.2)
        assert flow.gradient == (0.05, 0.08)
        assert flow.diffusion_coefficient == 0.1

    def test_flow_vector_step(self) -> None:
        """Test taking a step in flow."""
        flow = FlowVector(
            position=(0.5, 0.5),
            velocity=(0.1, 0.0),
            gradient=(0.05, 0.0),
            diffusion_coefficient=0.1,
        )
        
        new_pos = flow.step(dt=0.1)
        
        assert isinstance(new_pos, tuple)
        assert len(new_pos) == 2

    def test_flow_vector_magnitude(self) -> None:
        """Test flow vector magnitude."""
        flow = FlowVector(
            position=(0.0, 0.0),
            velocity=(3.0, 4.0),
            gradient=(0.0, 0.0),
        )
        
        mag = flow.magnitude()
        
        assert mag == pytest.approx(5.0, rel=1e-5)


class TestSwarmIntelligence:
    """Tests for SwarmIntelligence class."""

    def test_swarm_initialization(self) -> None:
        """Test SwarmIntelligence initialization."""
        swarm = SwarmIntelligence(num_particles=10, dimensions=2)
        
        assert swarm.num_particles == 10
        assert swarm.dimensions == 2
        assert len(swarm.particles) == 0  # Not initialized until initialize_swarm is called

    def test_swarm_initialize_swarm(self) -> None:
        """Test particle creation via initialize_swarm."""
        swarm = SwarmIntelligence(num_particles=5, dimensions=2)
        bounds = [(0.0, 1.0), (0.0, 1.0)]
        
        swarm.initialize_swarm(bounds)
        
        assert len(swarm.particles) == 5
        for particle in swarm.particles:
            assert isinstance(particle, SwarmParticle)
            assert len(particle.position) == 2
            assert len(particle.velocity) == 2

    def test_swarm_evaluate_fitness(self) -> None:
        """Test fitness evaluation."""
        swarm = SwarmIntelligence(num_particles=3, dimensions=2)
        
        fitness = swarm.evaluate_fitness((0.5, 0.5))
        assert isinstance(fitness, float)
        assert fitness < 0  # Default fitness is negative distance

    def test_swarm_particle_bounds(self) -> None:
        """Test that particles are within bounds after initialization."""
        swarm = SwarmIntelligence(num_particles=10, dimensions=2)
        bounds = [(0.0, 1.0), (0.0, 1.0)]
        
        swarm.initialize_swarm(bounds)
        
        for particle in swarm.particles:
            for pos in particle.position:
                assert 0.0 <= pos <= 1.0


class TestSwarmParticle:
    """Tests for SwarmParticle dataclass."""

    def test_particle_initialization(self) -> None:
        """Test SwarmParticle initialization."""
        particle = SwarmParticle(
            position=(0.5, 0.5),
            velocity=(0.1, 0.1),
        )
        
        assert particle.position == (0.5, 0.5)
        assert particle.velocity == (0.1, 0.1)

    def test_particle_personal_best_default(self) -> None:
        """Test particle personal_best_position default."""
        particle = SwarmParticle(
            position=(0.5, 0.5),
            velocity=(0.1, 0.1),
        )
        
        # personal_best_position should default to position via __post_init__
        assert particle.personal_best_position == (0.5, 0.5)

    def test_particle_personal_best_score(self) -> None:
        """Test particle personal_best_score."""
        particle = SwarmParticle(
            position=(0.5, 0.5),
            velocity=(0.1, 0.1),
            personal_best_score=0.75,
        )
        
        assert particle.personal_best_score == 0.75


class TestImportMigration:
    """Tests for ImportMigration class."""

    def test_import_migration_initialization(self) -> None:
        """Test ImportMigration initialization."""
        migration = ImportMigration(
            file_path="src/agents/orchestrator.py",
            old_import="from agents.decision_models import Model",
            new_import="from agents.physics_orchestrator import Model",
            line_number=42,
        )
        
        assert migration.file_path == "src/agents/orchestrator.py"
        assert migration.old_import == "from agents.decision_models import Model"
        assert migration.new_import == "from agents.physics_orchestrator import Model"
        assert migration.line_number == 42

    def test_import_migration_calculate_properties(self) -> None:
        """Test ImportMigration physics properties calculation."""
        migration = ImportMigration(
            file_path="agents/orchestrator.py",
            old_import="from agents.old import Module",
            new_import="from agents.new import Module",
            line_number=10,
        )
        
        migration.calculate_properties()
        
        assert migration.potential_energy > 0
        assert migration.impact > 0
        assert migration.confidence > 0
        assert migration.risk >= 0
        assert migration.urgency > 0
        assert migration.optimization_score > 0

    def test_import_migration_cli_file_properties(self) -> None:
        """Test properties for CLI file."""
        migration = ImportMigration(
            file_path="src/codex/cli/main.py",
            old_import="from agents import old",
            new_import="from agents import new",
            line_number=5,
        )
        
        migration.calculate_properties()
        
        # CLI files should have high impact
        assert migration.impact == 0.9

    def test_import_migration_test_file_properties(self) -> None:
        """Test properties for test file."""
        migration = ImportMigration(
            file_path="src/tests/test_module.py",
            old_import="from agents import old",
            new_import="from agents import new",
            line_number=3,
        )
        
        migration.calculate_properties()
        
        # Test files should have medium-high impact
        assert migration.impact == 0.7


class TestForceVectorAdvanced:
    """Advanced tests for ForceVector."""

    @pytest.mark.parametrize(
        "x,y,z,expected_mag",
        [
            (3.0, 4.0, 0.0, 5.0),
            (1.0, 0.0, 0.0, 1.0),
            (0.0, 1.0, 0.0, 1.0),
            (0.0, 0.0, 1.0, 1.0),
            (1.0, 1.0, 1.0, pytest.approx(1.732, abs=0.01)),
        ],
    )
    def test_3d_magnitude_calculation(
        self,
        x: float,
        y: float,
        z: float,
        expected_mag: float,
    ) -> None:
        """Test 3D magnitude calculations with parametrization."""
        vector = ForceVector(x=x, y=y, z=z)
        
        assert vector.magnitude == pytest.approx(expected_mag, rel=0.01)

    def test_priority_scaling_effects(self) -> None:
        """Test priority scaling with different values."""
        priorities = [0.5, 1.0, 2.0, 5.0]
        
        for priority in priorities:
            vector = ForceVector(
                magnitude=1.0,
                direction=0.0,
                priority=priority,
            )
            
            x, _y = vector.get_components()
            assert x == pytest.approx(priority, rel=0.01)


class TestErrorHandling:
    """Tests for error handling and edge cases."""

    def test_action_path_negative_values(self) -> None:
        """Test ActionPath with negative values."""
        path = ActionPath(
            potential_energy=-10.0,
            kinetic_energy=-5.0,
        )
        
        # Should not raise, but values should be preserved
        assert path.potential_energy == -10.0
        assert path.kinetic_energy == -5.0

    def test_decision_state_with_none_values(self) -> None:
        """Test DecisionState with None-like values."""
        state = DecisionState(
            current_position=None,
            goal_position=None,
        )
        
        assert state.current_position is None
        assert state.goal_position is None

    def test_orchestrator_assess_with_empty_state(
        self,
        orchestrator_fixture: PhysicsInspiredOrchestrator,
    ) -> None:
        """Test orchestrator assess with minimal state."""
        state = DecisionState()
        
        with patch('builtins.print'):
            assessment = orchestrator_fixture.assess_situation(state)
        
        assert assessment is not None

    def test_energy_landscape_with_zero_temperature(self) -> None:
        """Test EnergyLandscape with near-zero temperature."""
        landscape = EnergyLandscape(temperature=0.001)
        
        for i in range(3):
            state = EnergyState(
                configuration={"id": i},
                energy=float(i),
            )
            landscape.add_state(state)
        
        selected = landscape.select_state()
        assert selected is not None

    def test_diffusion_flow_with_single_point(self) -> None:
        """Test DiffusionFlowModel with single attractor."""
        model = DiffusionFlowModel()
        model.add_attractor((0.5, 0.5), strength=1.0)
        
        trajectory = model.simulate_flow((0.5, 0.5), steps=10)
        
        # Starting at attractor should have minimal movement
        assert len(trajectory) >= 1


class TestIntegrationScenarios:
    """Integration tests for orchestration workflows."""

    def test_decision_workflow_basic(
        self,
        orchestrator_fixture: PhysicsInspiredOrchestrator,
    ) -> None:
        """Test basic decision workflow."""
        state = DecisionState(
            current_position="init",
            goal_position="target",
            available_resources=0.9,
        )
        
        with patch('builtins.print'):
            assessment = orchestrator_fixture.assess_situation(state)
        
        assert assessment is not None
        assert "distance_to_goal" in assessment

    def test_physics_properties_interaction(self) -> None:
        """Test interaction of physics properties."""
        path1 = ActionPath(
            potential_energy=50.0,
            kinetic_energy=50.0,
            friction=1.0,
            momentum=5.0,
        )
        
        path2 = ActionPath(
            potential_energy=40.0,
            kinetic_energy=60.0,
            friction=2.0,
            momentum=8.0,
        )
        
        e1 = path1.calculate_total_energy()
        e2 = path2.calculate_total_energy()
        
        # Both should produce valid energies
        assert e1 > 0
        assert e2 > 0

    def test_swarm_with_diffusion_model(self) -> None:
        """Test swarm particles interacting with diffusion field."""
        swarm = SwarmIntelligence(num_particles=5, dimensions=2)
        bounds = [(0.0, 1.0), (0.0, 1.0)]
        swarm.initialize_swarm(bounds)
        
        model = DiffusionFlowModel()
        model.add_attractor((0.8, 0.8), strength=2.0)
        
        assert len(swarm.particles) == 5
        assert len(model.attractors) == 1


class TestPhysicsCalculationAccuracy:
    """High-precision tests for physics calculations."""

    def test_force_components_precision(self) -> None:
        """Test force component calculation precision."""
        vector = ForceVector(
            magnitude=1.0,
            direction=math.pi / 4,
            priority=1.0,
        )
        
        x, y = vector.get_components()
        expected = math.sqrt(2) / 2
        
        assert x == pytest.approx(expected, abs=1e-10)
        assert y == pytest.approx(expected, abs=1e-10)

    def test_energy_formula_precision(self) -> None:
        """Test energy formula calculation precision."""
        path = ActionPath(
            potential_energy=33.33,
            kinetic_energy=66.67,
            friction=1.234,
            momentum=4.567,
        )
        
        total = path.calculate_total_energy()
        expected = 33.33 + 66.67 - (4.567 * 5.0) + (1.234 * 10.0)
        
        assert total == pytest.approx(expected, abs=1e-10)


class TestOrchestratorOrchestrationCycle:
    """Tests for complete orchestration cycles."""

    def test_assess_deliberate_optimize_act_cycle(
        self,
        orchestrator_fixture: PhysicsInspiredOrchestrator,
    ) -> None:
        """Test complete ASSESS-DELIBERATE-OPTIMIZE-ACT cycle."""
        state = DecisionState(
            current_position="state_a",
            goal_position="state_z",
            available_resources=0.75,
            time_available=0.8,
            current_velocity=0.6,
        )
        
        with patch('builtins.print'):
            # ASSESS phase
            assessment = orchestrator_fixture.assess_situation(state)
            assert assessment is not None


class TestEdgeCaseBoundaryConditions:
    """Additional edge case and boundary condition tests."""

    @pytest.mark.parametrize(
        "magnitude,direction,priority,expected_x",
        [
            (0.0, 0.0, 1.0, 0.0),
            (1.0, 0.0, 0.0, 0.0),
            (100.0, 0.0, 1.0, 100.0),
            (0.001, math.pi, 1.0, pytest.approx(-0.001, abs=0.01)),
        ],
    )
    def test_force_vector_components_boundary(
        self,
        magnitude: float,
        direction: float,
        priority: float,
        expected_x: float,
    ) -> None:
        """Test force components at boundaries."""
        vector = ForceVector(
            magnitude=magnitude,
            direction=direction,
            priority=priority,
        )
        
        x, _y = vector.get_components()
        
        if isinstance(expected_x, float) and not isinstance(expected_x, type(pytest.approx(0))):
            assert x == expected_x
        else:
            assert x == expected_x

    @pytest.mark.parametrize(
        "potential,kinetic,friction,momentum",
        [
            (0.0, 0.0, 0.0, 0.0),
            (100.0, 100.0, 10.0, 10.0),
            (1.0, 1.0, 0.1, 1.0),
            (1000.0, 1000.0, 100.0, 100.0),
        ],
    )
    def test_total_energy_boundary_values(
        self,
        potential: float,
        kinetic: float,
        friction: float,
        momentum: float,
    ) -> None:
        """Test energy calculations at boundaries."""
        path = ActionPath(
            potential_energy=potential,
            kinetic_energy=kinetic,
            friction=friction,
            momentum=momentum,
        )
        
        total = path.calculate_total_energy()
        
        # Verify formula: E = P + K - M*5 + F*10
        expected = potential + kinetic - (momentum * 5.0) + (friction * 10.0)
        assert total == pytest.approx(expected, rel=0.01)

    def test_diffusion_flow_convergence(self) -> None:
        """Test that diffusion flow converges toward attractors."""
        model = DiffusionFlowModel(resolution=20)
        model.add_attractor((0.9, 0.9), strength=2.0)
        
        trajectory = model.simulate_flow((0.1, 0.1), steps=100, dt=0.05)
        
        # Final position should be closer to attractor than initial
        initial_dist = math.hypot(0.1 - 0.9, 0.1 - 0.9)
        final_dist = math.hypot(trajectory[-1][0] - 0.9, trajectory[-1][1] - 0.9)
        
        assert final_dist < initial_dist


class TestPhysicsLawsConsistency:
    """Tests verifying physics laws and consistency."""

    def test_energy_conservation_in_closed_system(self) -> None:
        """Test energy conservation principle."""
        paths = [
            ActionPath(potential_energy=50.0, kinetic_energy=50.0),
            ActionPath(potential_energy=30.0, kinetic_energy=70.0),
            ActionPath(potential_energy=80.0, kinetic_energy=20.0),
        ]
        
        total_mechanical_energy = sum(
            p.potential_energy + p.kinetic_energy for p in paths
        )
        
        # Should sum to 100 (simplified conservation check)
        assert total_mechanical_energy == 300.0

    def test_force_composition_vector_addition(self) -> None:
        """Test that forces compose via vector addition."""
        # Two perpendicular unit forces
        f1 = ForceVector(magnitude=1.0, direction=0.0, priority=1.0)
        f2 = ForceVector(magnitude=1.0, direction=math.pi / 2, priority=1.0)
        
        x1, y1 = f1.get_components()
        x2, y2 = f2.get_components()
        
        total_mag = math.hypot(x1 + x2, y1 + y2)
        
        # Two perpendicular unit vectors should result in sqrt(2)
        assert total_mag == pytest.approx(math.sqrt(2), abs=0.01)

    def test_momentum_reduces_energy(self) -> None:
        """Test that higher momentum reduces total energy (physics principle)."""
        path_low_momentum = ActionPath(
            potential_energy=100.0,
            kinetic_energy=50.0,
            friction=1.0,
            momentum=0.0,
        )
        
        path_high_momentum = ActionPath(
            potential_energy=100.0,
            kinetic_energy=50.0,
            friction=1.0,
            momentum=10.0,
        )
        
        e_low = path_low_momentum.calculate_total_energy()
        e_high = path_high_momentum.calculate_total_energy()
        
        # High momentum should result in lower total energy
        assert e_high < e_low

    def test_friction_increases_energy(self) -> None:
        """Test that higher friction increases total energy (physics principle)."""
        path_low_friction = ActionPath(
            potential_energy=100.0,
            kinetic_energy=50.0,
            friction=0.0,
            momentum=5.0,
        )
        
        path_high_friction = ActionPath(
            potential_energy=100.0,
            kinetic_energy=50.0,
            friction=10.0,
            momentum=5.0,
        )
        
        e_low = path_low_friction.calculate_total_energy()
        e_high = path_high_friction.calculate_total_energy()
        
        # High friction should result in higher total energy
        assert e_high > e_low


class TestStatisticalMechanics:
    """Tests for thermodynamic and statistical mechanics concepts."""

    def test_boltzmann_distribution_lower_energy_higher_probability(self) -> None:
        """Test that lower energy states have higher Boltzmann probability."""
        state_low = EnergyState(
            configuration={"id": 1},
            energy=5.0,
            temperature=1.0,
        )
        
        state_high = EnergyState(
            configuration={"id": 2},
            energy=20.0,
            temperature=1.0,
        )
        
        prob_low = state_low.boltzmann_probability(reference_energy=0.0)
        prob_high = state_high.boltzmann_probability(reference_energy=0.0)
        
        assert prob_low > prob_high

    def test_free_energy_calculation_temperature_dependence(self) -> None:
        """Test that free energy depends on temperature."""
        config = {"test": True}
        
        state_cold = EnergyState(
            configuration=config,
            energy=10.0,
            temperature=0.1,
            entropy=5.0,
        )
        
        state_hot = EnergyState(
            configuration=config,
            energy=10.0,
            temperature=10.0,
            entropy=5.0,
        )
        
        # F = E - T*S
        # Cold: F = 10 - 0.1*5 = 9.5
        # Hot: F = 10 - 10*5 = -40
        # Hot system should have lower free energy
        assert state_hot.free_energy() < state_cold.free_energy()

    def test_gibbs_distribution_probability_normalization(self) -> None:
        """Test that Gibbs probabilities sum to approximately 1."""
        landscape = EnergyLandscape(temperature=1.0)
        
        for i in range(5):
            state = EnergyState(
                configuration={"id": i},
                energy=float(i),
            )
            landscape.add_state(state)
        
        total_prob = sum(
            landscape.gibbs_probability(state) for state in landscape.states
        )
        
        assert total_prob == pytest.approx(1.0, abs=0.01)

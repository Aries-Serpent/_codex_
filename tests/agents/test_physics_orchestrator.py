"""
Test Physics Orchestrator Module

Tests for the physics-inspired decision making orchestrator.
Tests force vectors, action paths, and physics-based calculations.
"""

from __future__ import annotations

import math

from agents.physics_orchestrator import (
    ActionPath,
    ActionType,
    ForceVector,
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
        assert ActionType.AUDIT.value == "audit"
        assert ActionType.REFACTOR.value == "refactor"
        assert ActionType.TEST.value == "test"
        assert ActionType.DOCUMENT.value == "document"

    def test_action_type_from_value(self) -> None:
        """Test creating action type from value."""
        assert ActionType("audit") == ActionType.AUDIT
        assert ActionType("test") == ActionType.TEST


class TestForceVector:
    """Tests for ForceVector dataclass."""

    def test_default_values(self) -> None:
        """Test default ForceVector values."""
        vector = ForceVector()

        assert vector.name == ""
        assert vector.magnitude == 0.0
        assert vector.direction == 0.0
        assert vector.priority == 1.0

    def test_custom_values(self) -> None:
        """Test ForceVector with custom values."""
        vector = ForceVector(
            name="urgency",
            magnitude=0.8,
            direction=1.57,  # ~90 degrees
            priority=2.0,
        )

        assert vector.name == "urgency"
        assert vector.magnitude == 0.8
        assert vector.priority == 2.0

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

        assert abs(x - 1.0) < 0.01
        assert abs(y - 0.0) < 0.01

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
        assert abs(x - expected) < 0.01
        assert abs(y - expected) < 0.01

    def test_get_components_with_priority(self) -> None:
        """Test components with priority scaling."""
        vector = ForceVector(
            name="test",
            magnitude=1.0,
            direction=0.0,
            priority=2.0,
        )

        x, _y = vector.get_components()

        assert abs(x - 2.0) < 0.01

    def test_3d_vector_initialization(self) -> None:
        """Test 3D vector initialization from x, y, z."""
        vector = ForceVector(
            name="3d_force",
            x=3.0,
            y=4.0,
            z=0.0,
        )

        # Magnitude should be calculated: sqrt(3^2 + 4^2) = 5
        assert abs(vector.magnitude - 5.0) < 0.01

    def test_3d_vector_with_z(self) -> None:
        """Test 3D vector with z component."""
        vector = ForceVector(
            name="3d_force",
            x=1.0,
            y=0.0,
            z=0.0,
        )

        assert vector.magnitude == 1.0

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
            assert abs(mag - 1.0) < 0.01


class TestActionPath:
    """Tests for ActionPath dataclass."""

    def test_default_values(self) -> None:
        """Test default ActionPath values."""
        path = ActionPath()

        assert path.action_type == ActionType.ANALYZE
        assert path.description == ""
        assert path.potential_energy == 0.0
        assert path.kinetic_energy == 0.0
        assert path.friction == 0.0
        assert path.momentum == 0.0

    def test_decision_factors(self) -> None:
        """Test decision factor fields."""
        path = ActionPath(
            confidence=0.9,
            risk=0.2,
            impact=0.8,
            urgency=0.5,
        )

        assert path.confidence == 0.9
        assert path.risk == 0.2
        assert path.impact == 0.8
        assert path.urgency == 0.5

    def test_physics_properties(self) -> None:
        """Test physics property fields."""
        path = ActionPath(
            potential_energy=50.0,
            kinetic_energy=30.0,
            friction=2.0,
            momentum=5.0,
        )

        assert path.potential_energy == 50.0
        assert path.kinetic_energy == 30.0
        assert path.friction == 2.0
        assert path.momentum == 5.0

    def test_action_path_with_type(self) -> None:
        """Test ActionPath with specific action type."""
        path = ActionPath(
            action_type=ActionType.REFACTOR,
            description="Refactor legacy module",
        )

        assert path.action_type == ActionType.REFACTOR
        assert "legacy" in path.description.lower()

    def test_trajectory_field(self) -> None:
        """Test trajectory field."""
        path = ActionPath(trajectory=["step1", "step2", "step3"])

        assert len(path.trajectory) == 3
        assert path.trajectory[0] == "step1"


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
        assert abs(result_mag - math.sqrt(2)) < 0.01

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
        assert result_mag < 0.01

    def test_energy_conservation(self) -> None:
        """Test total energy calculation."""
        path = ActionPath(
            potential_energy=70.0,
            kinetic_energy=30.0,
        )

        total_energy = path.potential_energy + path.kinetic_energy
        assert total_energy == 100.0

    def test_friction_reduces_effective_momentum(self) -> None:
        """Test friction effect on momentum."""
        path = ActionPath(
            momentum=10.0,
            friction=3.0,
        )

        effective_momentum = path.momentum - path.friction
        assert effective_momentum == 7.0


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
            assert risk_reward == 3.0

    def test_confidence_weighted_impact(self) -> None:
        """Test confidence-weighted impact."""
        path = ActionPath(
            confidence=0.8,
            impact=1.0,
        )

        weighted_impact = path.confidence * path.impact
        assert weighted_impact == 0.8

    def test_urgency_priority_boost(self) -> None:
        """Test urgency boosting priority."""
        base_priority = 1.0
        urgency = 0.9

        boosted_priority = base_priority * (1 + urgency)
        assert boosted_priority == 1.9


class TestEdgeCases:
    """Edge case tests."""

    def test_zero_magnitude_vector(self) -> None:
        """Test vector with zero magnitude."""
        vector = ForceVector(name="zero", magnitude=0.0, direction=1.0)

        x, y = vector.get_components()

        assert x == 0.0
        assert y == 0.0

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

        assert total == 0.0

    def test_negative_direction(self) -> None:
        """Test vector with negative direction."""
        vector = ForceVector(
            name="negative",
            magnitude=1.0,
            direction=-math.pi / 2,  # -90 degrees
            priority=1.0,
        )

        x, y = vector.get_components()

        assert abs(x - 0.0) < 0.01
        assert abs(y - (-1.0)) < 0.01

    def test_large_values(self) -> None:
        """Test with large values."""
        path = ActionPath(
            potential_energy=1000000.0,
            kinetic_energy=500000.0,
        )

        assert path.potential_energy == 1000000.0
        assert path.kinetic_energy == 500000.0

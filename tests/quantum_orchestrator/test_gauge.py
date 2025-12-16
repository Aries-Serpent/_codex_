"""
Comprehensive tests for gauge symmetries and conservation laws.

Tests verify:
- U(1) gauge invariance
- Translation symmetry and momentum conservation
- Time translation symmetry and energy conservation
- Noether currents
- Continuity equations
- Conservation enforcement
"""

import pytest
import numpy as np
from unittest.mock import Mock

from codex.quantum_orchestrator.orchestrator import (
    TaskState,
    DiracSpinor,
    TaskVector,
    OrchestratorState,
    PhysicsConstants,
)
from codex.quantum_orchestrator.qft.gauge import (
    SymmetryType,
    TransformationResult,
    U1GaugeTransform,
    TranslationSymmetry,
    TimeTranslationSymmetry,
    NoetherCurrent,
    GaugeChecker,
    ConservationEnforcer,
)


@pytest.fixture
def physics_constants():
    """Provide physics constants."""
    return PhysicsConstants(hbar=1.0, c=100.0, default_mass=1.0)


@pytest.fixture
def simple_task():
    """Create a simple task state."""
    spinor = DiracSpinor(components=np.array([0.8 + 0j, 0.6 + 0j, 0j, 0j]))
    return TaskState(
        task_id="task_1",
        name="Test Task",
        position=TaskVector(priority=0.5, complexity=1.0),
        spinor=spinor,
        velocity=np.array([0.1, 0.0, 0.0, 0.0, 0.0]),
        rest_mass=1.0,
    )


@pytest.fixture
def simple_state(simple_task):
    """Create a simple orchestrator state with one task."""
    return OrchestratorState(
        tasks={"task_1": simple_task},
        timestamp=0.0,
        constants=PhysicsConstants(),
    )


@pytest.fixture
def multi_task_state(physics_constants):
    """Create a state with multiple tasks."""
    tasks = {}
    for i in range(3):
        spinor = DiracSpinor(components=np.array([0.8 + 0j, 0.6 + 0j, 0j, 0j]))
        spinor.normalize()
        tasks[f"task_{i}"] = TaskState(
            task_id=f"task_{i}",
            name=f"Task {i}",
            position=TaskVector(priority=0.3 * i, complexity=1.0 + 0.5 * i),
            spinor=spinor,
            velocity=np.array([0.1 * i, 0.0, 0.0, 0.0, 0.0]),
            rest_mass=1.0 + 0.1 * i,
        )

    return OrchestratorState(
        tasks=tasks,
        timestamp=0.0,
        constants=physics_constants,
    )


# ============================================================================
# U(1) Gauge Transform Tests
# ============================================================================


def test_u1_gauge_global_transform(simple_state):
    """Test global U(1) gauge transformation."""
    gauge = U1GaugeTransform()
    theta = np.pi / 4

    transformed = gauge.apply_global(simple_state, theta)

    # Check transformation applied
    original_components = simple_state.tasks["task_1"].spinor.components
    transformed_components = transformed.tasks["task_1"].spinor.components

    expected = original_components * np.exp(1j * theta)
    np.testing.assert_allclose(transformed_components, expected, rtol=1e-10)


def test_u1_gauge_probability_invariance(simple_state):
    """Test that probabilities are invariant under U(1) transformation."""
    gauge = U1GaugeTransform()
    theta = np.pi / 3

    original_prob = simple_state.tasks["task_1"].spinor.total_probability
    transformed = gauge.apply_global(simple_state, theta)
    transformed_prob = transformed.tasks["task_1"].spinor.total_probability

    assert abs(transformed_prob - original_prob) < 1e-10


def test_u1_gauge_verify_invariance(simple_state):
    """Test U(1) gauge invariance verification."""
    gauge = U1GaugeTransform()

    result = gauge.verify_invariance(simple_state, theta=np.pi / 6)

    assert result.is_invariant
    assert result.deviation < 1e-10
    assert "theta" in result.details
    assert "max_deviation" in result.details


def test_u1_gauge_local_transform(multi_task_state):
    """Test local U(1) gauge transformation."""
    gauge = U1GaugeTransform()
    phase_map = {
        "task_0": np.pi / 4,
        "task_1": np.pi / 2,
        "task_2": np.pi,
    }

    transformed = gauge.apply_local(multi_task_state, phase_map)

    # Check each task got its own phase
    for task_id, theta in phase_map.items():
        original = multi_task_state.tasks[task_id].spinor.components
        transformed_comp = transformed.tasks[task_id].spinor.components
        expected = original * np.exp(1j * theta)
        np.testing.assert_allclose(transformed_comp, expected, rtol=1e-10)


def test_u1_gauge_multiple_phases(simple_state):
    """Test that multiple phase transformations compose correctly."""
    gauge = U1GaugeTransform()

    # Apply two transformations
    theta1 = np.pi / 4
    theta2 = np.pi / 6

    state1 = gauge.apply_global(simple_state, theta1)
    state2 = gauge.apply_global(state1, theta2)

    # Should equal single transformation with sum of phases
    state_direct = gauge.apply_global(simple_state, theta1 + theta2)

    components2 = state2.tasks["task_1"].spinor.components
    components_direct = state_direct.tasks["task_1"].spinor.components

    np.testing.assert_allclose(components2, components_direct, rtol=1e-10)


# ============================================================================
# Translation Symmetry Tests
# ============================================================================


def test_translation_symmetry_apply(multi_task_state):
    """Test spatial translation application."""
    trans = TranslationSymmetry()
    displacement = np.array([0.1, 0.2, 0.3, 0.4, 0.5])

    translated = trans.apply_translation(multi_task_state, displacement)

    # Check all positions shifted
    for task_id in multi_task_state.tasks:
        original_pos = multi_task_state.tasks[task_id].position.to_array()
        translated_pos = translated.tasks[task_id].position.to_array()

        expected = original_pos + displacement
        # dependency_depth (index 4) is an integer field, so handle separately
        np.testing.assert_allclose(translated_pos[:4], expected[:4], rtol=1e-10)
        # Integer field: check it increased by int(displacement[4])
        assert translated_pos[4] == original_pos[4] + int(displacement[4])


def test_translation_momentum_computation(multi_task_state):
    """Test total momentum computation."""
    trans = TranslationSymmetry()

    momentum = trans.compute_total_momentum(multi_task_state)

    # Verify it's the sum of individual momenta
    expected = np.zeros(5)
    for task in multi_task_state.tasks.values():
        expected += task.rest_mass * task.velocity

    np.testing.assert_allclose(momentum, expected, rtol=1e-10)


def test_translation_momentum_conservation(multi_task_state):
    """Test momentum conservation verification."""
    trans = TranslationSymmetry()

    # Create evolved state (with same total momentum)
    state_after = OrchestratorState(
        tasks=multi_task_state.tasks.copy(),
        timestamp=1.0,
        constants=multi_task_state.constants,
    )

    result = trans.verify_momentum_conservation(multi_task_state, state_after, tolerance=1e-6)

    assert result.is_invariant
    assert "momentum_before" in result.details
    assert "momentum_after" in result.details


# ============================================================================
# Time Translation Symmetry Tests
# ============================================================================


def test_time_translation_energy_computation(multi_task_state):
    """Test total energy computation."""
    time_trans = TimeTranslationSymmetry()

    energy = time_trans.compute_total_energy(multi_task_state)

    # Energy should be positive (includes rest energy)
    assert energy > 0


def test_time_translation_energy_conservation(multi_task_state):
    """Test energy conservation verification."""
    time_trans = TimeTranslationSymmetry()

    # Create state with same energy
    state_after = OrchestratorState(
        tasks=multi_task_state.tasks.copy(),
        timestamp=1.0,
        constants=multi_task_state.constants,
    )

    result = time_trans.verify_energy_conservation(multi_task_state, state_after, tolerance=1e-6)

    assert result.is_invariant
    assert "energy_before" in result.details
    assert "energy_after" in result.details


# ============================================================================
# Noether Current Tests
# ============================================================================


def test_noether_probability_current(simple_task):
    """Test probability current computation."""
    noether = NoetherCurrent()

    current = noether.probability_current(simple_task)

    # Current should be a 5D vector
    assert current.shape == (5,)


def test_noether_momentum_current(simple_task):
    """Test momentum current computation."""
    noether = NoetherCurrent()

    momentum_curr = noether.momentum_current(simple_task)

    # Should be proportional to velocity
    assert momentum_curr.shape == (5,)
    assert np.allclose(
        momentum_curr, simple_task.spinor.total_probability * simple_task.velocity, rtol=1e-6
    )


def test_noether_continuity_equation(multi_task_state):
    """Test continuity equation verification."""
    noether = NoetherCurrent()

    # Create slightly evolved state
    state_after = OrchestratorState(
        tasks=multi_task_state.tasks.copy(),
        timestamp=0.01,
        constants=multi_task_state.constants,
    )

    result = noether.verify_continuity(multi_task_state, state_after, dt=0.01, tolerance=1e-3)

    assert "max_violation" in result
    assert "is_conserved" in result
    assert "task_results" in result


# ============================================================================
# GaugeChecker Tests
# ============================================================================


def test_gauge_checker_check_all(multi_task_state):
    """Test comprehensive gauge check."""
    checker = GaugeChecker()

    results = checker.check_all(multi_task_state, tolerance=1e-6)

    assert "u1_invariance" in results
    assert "total_momentum" in results
    assert "total_energy" in results
    assert "all_passed" in results
    assert results["all_passed"]


def test_gauge_checker_verify_all(multi_task_state):
    """Test comprehensive conservation verification."""
    checker = GaugeChecker()

    # Create evolved state
    state_after = OrchestratorState(
        tasks=multi_task_state.tasks.copy(),
        timestamp=0.1,
        constants=multi_task_state.constants,
    )

    results = checker.verify_all(multi_task_state, state_after, dt=0.1, tolerance=1e-3)

    assert "momentum_conservation" in results
    assert "energy_conservation" in results
    assert "continuity" in results
    assert "all_passed" in results


# ============================================================================
# ConservationEnforcer Tests
# ============================================================================


def test_conservation_enforcer_probability(simple_state):
    """Test probability conservation enforcement."""
    enforcer = ConservationEnforcer(auto_repair=True)

    # Violate probability conservation
    simple_state.tasks["task_1"].spinor.components *= 2.0

    repaired, was_repaired = enforcer.enforce_probability_conservation(
        simple_state, tolerance=1e-10
    )

    assert was_repaired
    assert abs(repaired.tasks["task_1"].spinor.total_probability - 1.0) < 1e-10


def test_conservation_enforcer_no_repair_needed(simple_state):
    """Test enforcer when no repair is needed."""
    enforcer = ConservationEnforcer(auto_repair=True)

    # Normalize first
    simple_state.tasks["task_1"].spinor.normalize()

    repaired, was_repaired = enforcer.enforce_probability_conservation(
        simple_state, tolerance=1e-10
    )

    assert not was_repaired


def test_conservation_enforcer_logging(simple_state):
    """Test violation logging."""
    enforcer = ConservationEnforcer(auto_repair=True)

    # Violate conservation
    simple_state.tasks["task_1"].spinor.components *= 3.0

    enforcer.enforce_probability_conservation(simple_state)

    violations = enforcer.get_violations()
    assert len(violations) > 0
    assert violations[0]["type"] == "probability_violation"
    assert violations[0]["task_id"] == "task_1"


def test_conservation_enforcer_clear_log(simple_state):
    """Test clearing violation log."""
    enforcer = ConservationEnforcer(auto_repair=True)

    # Create violation
    simple_state.tasks["task_1"].spinor.components *= 2.0
    enforcer.enforce_probability_conservation(simple_state)

    assert len(enforcer.get_violations()) > 0

    enforcer.clear_violations()
    assert len(enforcer.get_violations()) == 0


def test_conservation_enforcer_no_auto_repair(simple_state):
    """Test enforcer with auto_repair disabled."""
    enforcer = ConservationEnforcer(auto_repair=False)

    # Violate conservation
    original_prob = simple_state.tasks["task_1"].spinor.total_probability
    simple_state.tasks["task_1"].spinor.components *= 2.0

    repaired, was_repaired = enforcer.enforce_probability_conservation(
        simple_state, tolerance=1e-10
    )

    # Should detect but not repair
    assert not was_repaired
    assert len(enforcer.get_violations()) > 0
    # Probability still violated
    assert abs(repaired.tasks["task_1"].spinor.total_probability - 1.0) > 0.1


# ============================================================================
# Integration Tests
# ============================================================================


def test_full_symmetry_workflow(multi_task_state):
    """Test complete symmetry checking workflow."""
    # Initialize all components
    gauge = U1GaugeTransform()
    trans = TranslationSymmetry()
    time_trans = TimeTranslationSymmetry()
    checker = GaugeChecker()
    enforcer = ConservationEnforcer()

    # 1. Check initial state
    initial_check = checker.check_all(multi_task_state)
    assert initial_check["all_passed"]

    # 2. Apply U(1) transformation
    transformed = gauge.apply_global(multi_task_state, np.pi / 4)
    u1_result = gauge.verify_invariance(multi_task_state)
    assert u1_result.is_invariant

    # 3. Apply translation
    displacement = np.array([0.1, 0.0, 0.0, 0.0, 0.0])
    translated = trans.apply_translation(multi_task_state, displacement)

    # 4. Enforce conservation
    repaired, was_repaired = enforcer.enforce_probability_conservation(multi_task_state)

    # 5. Final verification
    final_check = checker.check_all(repaired)
    assert final_check["all_passed"]


def test_symmetry_type_enum():
    """Test SymmetryType enum."""
    assert SymmetryType.U1_PHASE.value == "u1_phase"
    assert SymmetryType.TRANSLATION.value == "translation"
    assert SymmetryType.TIME_TRANSLATION.value == "time_translation"


def test_transformation_result_serialization():
    """Test TransformationResult to_dict."""
    result = TransformationResult(
        transformed_state=Mock(),
        is_invariant=True,
        deviation=1e-10,
        details={"test": "value"},
    )

    data = result.to_dict()
    assert data["is_invariant"] is True
    assert data["deviation"] == 1e-10
    assert data["details"]["test"] == "value"

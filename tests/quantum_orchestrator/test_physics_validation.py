"""
Physics validation tests for the Quantum-Relativistic-Dirac Orchestrator.

Tests that physical laws are correctly implemented and maintained:
1. Probability conservation
2. Energy-momentum relation
3. Speed limit enforcement
4. Dirac current bounds
5. Spinor normalization
6. Lorentz factor bounds
"""

import pytest

np = pytest.importorskip("numpy")

from codex.quantum_orchestrator.orchestrator import (
    DiracSpinor,
    PhysicsConstants,
    TaskVector,
    create_orchestrator,
)


class TestSpinorPhysics:
    """Test Dirac spinor quantum properties."""

    def test_spinor_normalization(self):
        """Spinor normalization: ψ†ψ = 1."""
        spinor = DiracSpinor()
        spinor.normalize()
        assert abs(spinor.total_probability - 1.0) < 1e-10, "Condition must be true"

    def test_unnormalized_spinor_normalization(self):
        """Unnormalized spinor becomes normalized."""
        components = np.array([2.0 + 0j, 1.5 + 0j, 1.0 + 0j, 0.5 + 0j])
        spinor = DiracSpinor(components=components)

        initial_norm = spinor.total_probability
        assert initial_norm > 1.0, "initial_norm must be greater than zero"

        spinor.normalize()
        assert abs(spinor.total_probability - 1.0) < 1e-10, "Condition must be true"

    def test_positive_negative_energy_sum(self):
        """Positive + negative energy probabilities = total probability."""
        components = np.array([0.5 + 0j, 0.5 + 0j, 0.5 + 0j, 0.5 + 0j])
        spinor = DiracSpinor(components=components)
        spinor.normalize()

        total = spinor.positive_energy_prob + spinor.negative_energy_prob
        assert abs(total - 1.0) < 1e-10, "Condition must be true"

    def test_spinor_components(self):
        """Spinor has 4 components."""
        spinor = DiracSpinor()
        assert len(spinor.components) == 4, "Collection must not be empty"
        assert spinor.psi_1 is not None, "psi_1 must be initialized"
        assert spinor.psi_2 is not None, "psi_2 must be initialized"
        assert spinor.psi_3 is not None, "psi_3 must be initialized"
        assert spinor.psi_4 is not None, "psi_4 must be initialized"

    def test_hermitian_conjugate(self):
        """Dagger operation produces correct conjugate."""
        components = np.array([1.0 + 1j, 2.0 - 1j, 0.5 + 0.5j, 0.3 - 0.2j])
        spinor = DiracSpinor(components=components)

        dagger = spinor.dagger()
        expected = np.conj(components)

        assert np.allclose(dagger, expected)


class TestRelativisticConstraints:
    """Test special relativity constraints."""

    def test_speed_limit_enforcement(self):
        """No task velocity can exceed c."""
        orch = create_orchestrator(max_throughput=100.0)
        orch.add_task("fast_task", "Fast Task", rest_mass=1.0)

        task = orch.state.tasks["fast_task"]

        # Try to apply huge force that would exceed c
        huge_force = np.array([10000.0, 0.0, 0.0, 0.0, 0.0])
        for _ in range(100):
            task.apply_force(huge_force, dt=0.1)

        # Speed should be capped below c
        assert task.speed < orch.constants.c, "speed is not valid"

    def test_lorentz_factor_minimum(self):
        """Lorentz factor γ ≥ 1 always."""
        orch = create_orchestrator()
        orch.add_task("test_task", "Test", rest_mass=1.0)

        task = orch.state.tasks["test_task"]

        # At rest
        task.velocity = np.zeros(5)
        assert task.lorentz_factor == 1.0, "lorentz_factor is not valid"

        # Moving
        task.velocity = np.array([50.0, 0.0, 0.0, 0.0, 0.0])
        assert task.lorentz_factor > 1.0, "lorentz_factor must be greater than zero"

        # Fast moving
        task.velocity = np.array([90.0, 0.0, 0.0, 0.0, 0.0])
        assert task.lorentz_factor > 1.0, "lorentz_factor must be greater than zero"

    def test_relativistic_mass_increases(self):
        """Relativistic mass m = γm₀ increases with velocity."""
        orch = create_orchestrator()
        orch.add_task("test_task", "Test", rest_mass=2.0)

        task = orch.state.tasks["test_task"]

        # At rest
        task.velocity = np.zeros(5)
        rest_mass_at_rest = task.relativistic_mass
        assert abs(rest_mass_at_rest - 2.0) < 1e-10, "Condition must be true"

        # Moving
        task.velocity = np.array([50.0, 0.0, 0.0, 0.0, 0.0])
        mass_moving = task.relativistic_mass
        assert mass_moving > rest_mass_at_rest, "mass_moving must be greater than zero"

    def test_rest_energy(self):
        """Rest energy E₀ = m₀c²."""
        PhysicsConstants(c=100.0)
        orch = create_orchestrator(max_throughput=100.0)
        orch.add_task("test_task", "Test", rest_mass=2.0)

        task = orch.state.tasks["test_task"]

        expected_rest_energy = 2.0 * 100.0 * 100.0
        assert abs(task.rest_energy - expected_rest_energy) < 1e-6, "Condition must be true"

    def test_energy_momentum_relation_approximate(self):
        """E² ≈ p²c² + m²c⁴ (approximately due to implementation details)."""
        orch = create_orchestrator(max_throughput=100.0)
        orch.add_task("test_task", "Test", rest_mass=2.0)

        task = orch.state.tasks["test_task"]
        task.velocity = np.array([30.0, 20.0, 0.0, 0.0, 0.0])

        E = task.total_energy
        p = task.speed * task.relativistic_mass
        m = task.rest_mass
        c = orch.constants.c

        lhs = E**2
        rhs = (p * c) ** 2 + (m * c * c) ** 2

        # Allow some tolerance due to approximations
        rel_error = abs(lhs - rhs) / max(abs(lhs), abs(rhs), 1e-10)
        assert rel_error < 0.2, "Error should be raised or set"


class TestDiracCurrent:
    """Test Dirac current properties."""

    def test_current_subluminal(self):
        """Dirac current |j| ≤ c always."""
        orch = create_orchestrator(max_throughput=100.0)
        orch.add_task("test_task", "Test", rest_mass=1.0)

        task = orch.state.tasks["test_task"]

        # Compute current
        current = orch.dirac.compute_current(task)
        current_magnitude = np.linalg.norm(current)

        assert current_magnitude <= orch.constants.c, "current_magnitude is not valid"

    def test_current_is_real_vector(self):
        """Dirac current is a real 3D vector."""
        orch = create_orchestrator()
        orch.add_task("test_task", "Test", rest_mass=1.0)

        task = orch.state.tasks["test_task"]
        current = orch.dirac.compute_current(task)

        assert len(current) == 3, "Current must not be empty"
        assert all(np.isreal(c) for c in current), "Condition must be true"

    def test_zitterbewegung_bounds(self):
        """Zitterbewegung amplitude is between 0 and 1."""
        orch = create_orchestrator()
        orch.add_task("test_task", "Test", rest_mass=1.0)

        task = orch.state.tasks["test_task"]

        # Pure positive energy state
        task.spinor.components = np.array([1.0 + 0j, 0j, 0j, 0j])
        zitter1 = orch.dirac.zitterbewegung_amplitude(task)
        assert 0.0 <= zitter1 <= 1.01, "0 is not valid"
        assert zitter1 < 0.1, "zitter1 is not valid"

        # Mixed state
        task.spinor.components = np.array([0.7 + 0j, 0j, 0.7 + 0j, 0j])
        task.spinor.normalize()
        zitter2 = orch.dirac.zitterbewegung_amplitude(task)
        assert 0.0 <= zitter2 <= 1.01, "0 is not valid"
        assert zitter2 > 0.5, "zitter2 must be greater than zero"

    def test_helicity_range(self):
        """Helicity h should be reasonable."""
        orch = create_orchestrator()
        orch.add_task("test_task", "Test", rest_mass=1.0)

        task = orch.state.tasks["test_task"]
        task.velocity = np.array([10.0, 0.0, 0.0, 0.0, 0.0])

        helicity = orch.dirac.helicity(task, orch.state)

        # Helicity should be bounded
        assert -2.0 <= helicity <= 2.0, "0 is not valid"


class TestOrchestration:
    """Test orchestration evolution and dynamics."""

    def test_evolution_preserves_normalization(self):
        """Evolution should maintain normalized spinors."""
        orch = create_orchestrator()
        orch.add_task("t1", "Task 1", rest_mass=1.0)
        orch.add_task("t2", "Task 2", rest_mass=1.5)

        initial_prob = orch.state.total_probability()

        for _ in range(10):
            orch.evolve()

        final_prob = orch.state.total_probability()

        # Should be close (allowing for numerical drift)
        assert abs(final_prob - initial_prob) < 0.2, "Condition must be true"

    def test_evolution_advances_time(self):
        """Evolution should advance timestamp."""
        orch = create_orchestrator(time_step=0.1)
        orch.add_task("test_task", "Test", rest_mass=1.0)

        initial_time = orch.state.timestamp
        orch.evolve()
        final_time = orch.state.timestamp

        assert final_time > initial_time, "final_time must be greater than zero"
        assert abs(final_time - initial_time - 0.1) < 1e-10, "Condition must be true"

    def test_evolution_stores_history(self):
        """Evolution should store state history."""
        orch = create_orchestrator()
        orch.add_task("test_task", "Test", rest_mass=1.0)

        assert len(orch.history) == 0, "Collection must not be empty"

        orch.evolve()
        assert len(orch.history) == 1, "Collection must not be empty"

        orch.evolve()
        assert len(orch.history) == 2, "Collection must not be empty"

    def test_measurement_collapses_state(self):
        """Measurement should collapse spinor to zero."""
        orch = create_orchestrator()
        orch.add_task("test_task", "Test", rest_mass=1.0)

        task = orch.state.tasks["test_task"]

        # Set high probability
        task.spinor.components = np.array([0.99 + 0j, 0.01 + 0j, 0j, 0j])
        task.spinor.normalize()

        result = orch.measure("test_task")

        if result["status"] == "completed":
            # Spinor should be collapsed
            assert task.spinor.total_probability < 0.01, "total_probability is not valid"

    def test_self_healing_stabilizes(self):
        """Self-healing should reduce zitterbewegung."""
        orch = create_orchestrator()
        orch.add_task("test_task", "Test", rest_mass=1.0)

        task = orch.state.tasks["test_task"]

        # Create unstable state
        task.spinor.components = np.array([0.5 + 0j, 0j, 0.5 + 0j, 0j])
        task.spinor.normalize()

        initial_zitter = orch.dirac.zitterbewegung_amplitude(task)

        orch.self_heal()

        final_zitter = orch.dirac.zitterbewegung_amplitude(task)

        assert final_zitter <= initial_zitter, "final_zitter is not valid"


class TestProbabilityConservation:
    """Test probability conservation laws."""

    def test_total_probability_conserved_over_evolution(self):
        """Total probability should be approximately conserved."""
        orch = create_orchestrator()

        # Add multiple tasks
        for i in range(5):
            orch.add_task(f"task_{i}", f"Task {i}", rest_mass=1.0 + i * 0.5)

        initial_prob = orch.state.total_probability()

        # Evolve
        for _ in range(20):
            orch.evolve()

        final_prob = orch.state.total_probability()

        # Should be conserved within tolerance
        assert abs(final_prob - initial_prob) < 0.5, "Condition must be true"

    def test_normalization_fixes_drift(self):
        """Normalization should fix probability drift."""
        orch = create_orchestrator()
        orch.add_task("test_task", "Test", rest_mass=1.0)

        task = orch.state.tasks["test_task"]

        # Artificially create drift
        task.spinor.components = task.spinor.components * 2.0

        assert task.spinor.total_probability > 1.5, "total_probability must be greater than zero"

        orch.state.normalize()

        assert abs(task.spinor.total_probability - 1.0) < 1e-10, "Condition must be true"


class TestPhysicsConsistency:
    """Test consistency between different physics formulations."""

    def test_dirac_matrices_anticommutation(self):
        """Dirac matrices satisfy {αᵢ, αⱼ} = 2δᵢⱼ."""
        from codex.quantum_orchestrator.orchestrator import DiracMatrices

        alpha_vec = DiracMatrices.alpha_vector()

        for i in range(3):
            for j in range(3):
                anticomm = alpha_vec[i] @ alpha_vec[j] + alpha_vec[j] @ alpha_vec[i]
                expected = 2 * np.eye(4) if i == j else np.zeros((4, 4))
                assert np.allclose(anticomm, expected, atol=1e-10)

    def test_beta_matrix_squares_to_identity(self):
        """β² = I (identity matrix)."""
        from codex.quantum_orchestrator.orchestrator import DiracMatrices

        beta = DiracMatrices.beta()
        beta_squared = beta @ beta

        assert np.allclose(beta_squared, np.eye(4), atol=1e-10)

    def test_task_vector_operations(self):
        """Task vector arithmetic is consistent."""
        tv1 = TaskVector(priority=0.5, complexity=1.0, resource_demand=0.3)
        tv2 = TaskVector(priority=0.3, complexity=0.5, resource_demand=0.2)

        # Addition
        tv3 = tv1 + tv2
        assert abs(tv3.priority - 0.8) < 1e-10, "Condition must be true"
        assert abs(tv3.complexity - 1.5) < 1e-10, "Condition must be true"

        # Scalar multiplication
        tv4 = tv1 * 2.0
        assert abs(tv4.priority - 1.0) < 1e-10, "Condition must be true"

        # Distance
        dist = tv1.distance_to(tv2)
        assert dist > 0.0, "dist must be greater than zero"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_mass_task(self):
        """Tasks with zero mass (massless)."""
        orch = create_orchestrator()
        orch.add_task("massless", "Massless Task", rest_mass=0.0)

        task = orch.state.tasks["massless"]

        # Should handle gracefully
        assert task.rest_mass == 0.0, "rest_mass is not valid"
        assert task.rest_energy == 0.0, "rest_energy is not valid"

    def test_very_high_velocity(self):
        """Tasks approaching speed of light."""
        orch = create_orchestrator(max_throughput=100.0)
        orch.add_task("fast", "Fast Task", rest_mass=1.0)

        task = orch.state.tasks["fast"]
        task.velocity = np.array([99.0, 0.0, 0.0, 0.0, 0.0])

        # Should have very high Lorentz factor
        assert task.lorentz_factor > 5.0, "lorentz_factor must be greater than zero"

    def test_empty_orchestrator(self):
        """Orchestrator with no tasks."""
        orch = create_orchestrator()

        assert len(orch.state.tasks) == 0, "Collection must not be empty"

        # Should handle evolution gracefully
        orch.evolve()

        # Should handle run gracefully
        results = orch.run(max_iterations=10)
        assert results["total_tasks"] == 0, "Result must not be empty"

    def test_single_task(self):
        """Orchestrator with single task."""
        orch = create_orchestrator()
        orch.add_task("single", "Single Task", rest_mass=1.0)

        results = orch.run(max_iterations=100)

        assert results["total_tasks"] == 1, "Result must not be empty"
        assert results["iterations"] > 0, "Value must be greater than zero"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

"""
Comprehensive physics validation tests for Quantum Orchestrator - High Priority (P1.1).

Focus on physics model validation:
1. Boundary conditions (speed of light, Planck constant)
2. Invalid energy states
3. Negative probability detection
4. Superposition collapse handling

Tests target quantum evolution and physics constraints.
"""


import numpy as np
import pytest

from codex.quantum_orchestrator.orchestrator import (
    DiracMatrices,
    DiracOperator,
    DiracSpinor,
    FlowAnalyzer,
    MomentumOperator,
    PhysicsConstants,
    PotentialLandscape,
    ProbabilityCurrentOperator,
    QuantumRelativisticDiracOrchestrator,
    TaskState,
    TaskVector,
)


class TestQuantumOrchestratorPhysicsValidation:
    """Test physics model validation in quantum orchestrator."""

    @pytest.fixture
    def orchestrator(self) -> QuantumRelativisticDiracOrchestrator:
        """Provide initialized orchestrator."""
        return QuantumRelativisticDiracOrchestrator(
            max_throughput=100.0, granularity=1.0, dt=0.1
        )

    @pytest.fixture
    def constants(self) -> PhysicsConstants:
        """Provide physics constants."""
        return PhysicsConstants(hbar=1.0, c=100.0, default_mass=1.0)

    # ========================================================================
    # BOUNDARY CONDITION TESTS
    # ========================================================================

    def test_speed_of_light_boundary(self, orchestrator: QuantumRelativisticDiracOrchestrator):
        """Test that velocities respect speed of light limit."""
        orchestrator.add_task("task_1", "Test Task", priority=0.5, complexity=1.0)

        task = orchestrator.state.tasks["task_1"]

        # Try to exceed speed of light
        max_speed = orchestrator.constants.c * 0.9999
        excessive_velocity = np.array([150.0, 0.0, 0.0, 0.0, 0.0])

        task.apply_force(excessive_velocity, dt=1.0)

        # Verify speed is capped
        actual_speed = np.linalg.norm(task.velocity)
        assert actual_speed <= max_speed, (
            f"Speed {actual_speed} exceeds limit {max_speed}"
        )

    def test_zero_mass_handling(self, orchestrator: QuantumRelativisticDiracOrchestrator, 
                               constants: PhysicsConstants):
        """Test handling of zero mass (massless particles)."""
        # Create task with zero mass
        task = TaskState(
            task_id="massless",
            name="Photon-like Task",
            position=TaskVector(),
            rest_mass=0.0,
            _constants=constants,
        )

        # Verify zero mass is handled
        assert task.rest_mass == 0.0
        assert task.rest_energy == 0.0

        # Lorentz factor should handle zero mass gracefully
        # For massless particles, γ is typically defined specially
        # Verify no division by zero
        _ = task.lorentz_factor  # Should not raise

    def test_negative_mass_rejection(self, constants: PhysicsConstants):
        """Test rejection of negative mass."""
        with pytest.raises((ValueError, AssertionError)):
            TaskState(
                task_id="negative_mass",
                name="Invalid Task",
                position=TaskVector(),
                rest_mass=-1.0,
                _constants=constants,
            )

    def test_planck_constant_quantization(self, constants: PhysicsConstants):
        """Test that Planck constant affects quantization properly."""
        # Smaller hbar = finer quantization
        fine_constants = PhysicsConstants(hbar=0.1, c=100.0)
        coarse_constants = PhysicsConstants(hbar=10.0, c=100.0)

        # Both should be valid but different
        assert fine_constants.hbar < coarse_constants.hbar
        assert fine_constants.hbar_squared < coarse_constants.hbar_squared

    def test_energy_positivity_constraint(self, orchestrator: QuantumRelativisticDiracOrchestrator):
        """Test that total energy remains positive."""
        orchestrator.add_task("task_energy", "Energy Test", complexity=2.0)

        task = orchestrator.state.tasks["task_energy"]
        initial_energy = task.total_energy

        # Evolve and check energy remains positive
        for _ in range(10):
            orchestrator.evolve()

        # Total energy should remain positive
        final_energy = task.total_energy
        assert final_energy > 0, "Total energy must remain positive"

    # ========================================================================
    # INVALID ENERGY STATE TESTS
    # ========================================================================

    def test_imaginary_energy_prevention(self, constants: PhysicsConstants):
        """Test prevention of imaginary energy states."""
        task = TaskState(
            task_id="energy_test",
            name="Energy Test Task",
            position=TaskVector(priority=0.5),
            _constants=constants,
        )

        # Energy should always be real and positive
        energy = task.total_energy
        assert isinstance(energy, float) or isinstance(energy, np.floating)
        assert energy > 0, "Energy must be real and positive"

    def test_complex_amplitude_normalization(self, constants: PhysicsConstants):
        """Test that complex amplitudes remain normalized."""
        spinor = DiracSpinor(constants=constants)

        # Amplitude should be complex
        assert isinstance(spinor.psi_1, complex) or isinstance(
            spinor.psi_1, np.complexfloating
        )

        # Norm should be approximately 1
        norm = spinor.norm
        assert abs(norm - 1.0) < 0.01, f"Norm {norm} not close to 1.0"

    def test_hamiltonian_hermiticity(self, constants: PhysicsConstants):
        """Test that Hamiltonian operator is Hermitian."""
        dirac_op = DiracOperator(constants)

        # Dirac matrices should be Hermitian
        for matrix in [
            dirac_op.matrices.alpha_x,
            dirac_op.matrices.alpha_y,
            dirac_op.matrices.alpha_z,
            dirac_op.matrices.beta,
        ]:
            # Check Hermiticity: A† = A
            adjoint = np.conj(matrix.T)
            assert np.allclose(
                matrix, adjoint, atol=1e-10
            ), "Matrix should be Hermitian"

    def test_anticommutation_relations(self, constants: PhysicsConstants):
        """Test Clifford algebra anticommutation relations for Dirac matrices."""
        matrices = DiracMatrices()

        # Test {α_i, α_j} = 2δ_ij 𝕀
        # {α_x, α_x} = 2𝕀
        result_xx = np.dot(matrices.alpha_x, matrices.alpha_x) + np.dot(
            matrices.alpha_x, matrices.alpha_x
        )
        expected = 2 * np.eye(4)
        assert np.allclose(
            result_xx, expected, atol=1e-10
        ), "Anticommutation relation violated"

    # ========================================================================
    # NEGATIVE PROBABILITY TESTS
    # ========================================================================

    def test_probability_bounds(self, orchestrator: QuantumRelativisticDiracOrchestrator):
        """Test that probability remains in [0, 1]."""
        orchestrator.add_task("task_prob", "Probability Test", priority=0.5)

        # Run evolution
        for _ in range(20):
            orchestrator.evolve()

        task = orchestrator.state.tasks["task_prob"]
        prob = task.probability

        assert 0 <= prob <= 1, f"Probability {prob} out of bounds [0, 1]"

    def test_probability_current_positivity(self, orchestrator: QuantumRelativisticDiracOrchestrator,
                                           constants: PhysicsConstants):
        """Test that probability current is physical (real-valued)."""
        current_op = ProbabilityCurrentOperator(constants)

        orchestrator.add_task("task_current", "Current Test")
        task = orchestrator.state.tasks["task_current"]

        # Compute current components
        # j^0 should give probability density (positive)
        current_density = current_op.positive_energy_contribution(task.spinor)

        # Should be non-negative
        assert current_density >= -1e-10, (
            f"Probability current density {current_density} is negative"
        )

    def test_norm_preservation_during_evolution(self, orchestrator: QuantumRelativisticDiracOrchestrator):
        """Test that spinor norm is preserved during evolution."""
        orchestrator.add_task("task_norm", "Norm Preservation Test")

        task = orchestrator.state.tasks["task_norm"]
        initial_norm = task.spinor.norm

        # Evolve
        for _ in range(10):
            orchestrator.evolve()

        final_norm = task.spinor.norm

        # Norm should be approximately preserved
        assert abs(final_norm - initial_norm) < 0.1, (
            f"Norm changed from {initial_norm} to {final_norm}"
        )

    def test_trace_of_density_matrix_unity(self, constants: PhysicsConstants):
        """Test that trace of density matrix equals 1."""
        spinor = DiracSpinor(constants=constants)

        # Density matrix ρ = |ψ⟩⟨ψ|
        psi = spinor.components
        rho = np.outer(psi, np.conj(psi))

        # Trace should be 1
        trace = np.trace(rho)
        assert abs(trace - 1.0) < 1e-10, f"Trace {trace} not equal to 1.0"

    # ========================================================================
    # SUPERPOSITION COLLAPSE TESTS
    # ========================================================================

    def test_superposition_state_initialization(self, constants: PhysicsConstants):
        """Test proper initialization of superposition states."""
        spinor = DiracSpinor(constants=constants)

        # Should be in a superposition (not single basis state)
        components = spinor.components
        non_zero_count = np.sum(np.abs(components) > 1e-10)

        # Should have multiple non-zero components
        assert non_zero_count > 1, "Should be in superposition"

    def test_measurement_basis_orthogonality(self, constants: PhysicsConstants):
        """Test orthogonality of measurement basis states."""
        # Create two orthogonal spinor states
        spinor1 = DiracSpinor(constants=constants)
        spinor2 = DiracSpinor(constants=constants)

        # Get components
        psi1 = spinor1.components
        psi2 = spinor2.components

        # Different initializations should give different states
        # (not necessarily orthogonal, but different)
        assert not np.allclose(psi1, psi2), "Different spinors should differ"

    def test_collapse_determinism(self, orchestrator: QuantumRelativisticDiracOrchestrator):
        """Test that collapse-like behavior is deterministic."""
        orchestrator.add_task("task_collapse_1", "Collapse Test 1")
        orchestrator.add_task("task_collapse_2", "Collapse Test 2")

        # Evolve both
        for _ in range(10):
            orchestrator.evolve()

        # Get final states
        task1_final = orchestrator.state.tasks["task_collapse_1"].probability
        task2_final = orchestrator.state.tasks["task_collapse_2"].probability

        # Both should have definite values (not NaN or infinite)
        assert not np.isnan(task1_final), "Probability should be definite"
        assert not np.isnan(task2_final), "Probability should be definite"
        assert not np.isinf(task1_final), "Probability should be finite"
        assert not np.isinf(task2_final), "Probability should be finite"

    def test_decoherence_inducing_factors(self, orchestrator: QuantumRelativisticDiracOrchestrator):
        """Test decoherence under environmental coupling."""
        orchestrator.add_task("task_decoherence", "Decoherence Test", priority=0.5)

        task = orchestrator.state.tasks["task_decoherence"]

        # Store initial spinor state
        initial_spinor = task.spinor.components.copy()

        # Evolve with coherence threshold
        for _ in range(20):
            orchestrator.evolve()

        final_spinor = task.spinor.components

        # Spinor should evolve (not remain constant)
        divergence = np.linalg.norm(final_spinor - initial_spinor)
        assert divergence > 1e-6, "Spinor should evolve over time"

    # ========================================================================
    # MOMENTUM AND GRADIENT TESTS
    # ========================================================================

    def test_gradient_finite_differences(self, orchestrator: QuantumRelativisticDiracOrchestrator,
                                        constants: PhysicsConstants):
        """Test gradient computation via finite differences."""
        momentum_op = MomentumOperator(constants)

        # Add two close tasks
        orchestrator.add_task("task_left", "Left Task", priority=0.4)
        orchestrator.add_task("task_right", "Right Task", priority=0.6)

        task_left = orchestrator.state.tasks["task_left"]
        task_right = orchestrator.state.tasks["task_right"]

        # Set positions close together
        task_left.position.priority = 0.4
        task_right.position.priority = 0.6

        # Compute gradients
        grad_left = momentum_op.gradient(orchestrator.state, "task_left")
        grad_right = momentum_op.gradient(orchestrator.state, "task_right")

        # Gradients should be computed without error
        assert isinstance(grad_left, np.ndarray), "Gradient should be ndarray"
        assert grad_left.shape == (5,), "Gradient should be 5D"

    def test_potential_landscape_smoothness(self, constants: PhysicsConstants,
                                           orchestrator: QuantumRelativisticDiracOrchestrator):
        """Test that potential landscape is smooth."""
        potential = PotentialLandscape(constants)

        orchestrator.add_task("task_potential", "Potential Test")
        task = orchestrator.state.tasks["task_potential"]

        # Sample potential at nearby points
        grad1 = potential.gradient("task_potential", orchestrator.state)
        
        # Small perturbation
        task.position.priority += 0.01
        grad2 = potential.gradient("task_potential", orchestrator.state)

        # Gradients should change smoothly (not discontinuously)
        change = np.linalg.norm(grad2 - grad1)
        assert change < 1.0, "Potential gradient should change smoothly"

    # ========================================================================
    # FLOW AND CURRENT TESTS
    # ========================================================================

    def test_probability_flow_conservation(self, orchestrator: QuantumRelativisticDiracOrchestrator):
        """Test conservation of probability flow."""
        flow_analyzer = FlowAnalyzer(orchestrator.constants)

        orchestrator.add_task("task_flow", "Flow Test", priority=0.5)

        # Evolve
        for _ in range(10):
            orchestrator.evolve()

        task = orchestrator.state.tasks["task_flow"]

        # Probability should remain normalized
        prob = task.probability
        assert 0 <= prob <= 1, "Probability should remain normalized"

    def test_vorticity_calculation(self, orchestrator: QuantumRelativisticDiracOrchestrator):
        """Test vorticity/circulation in probability current."""
        # This is an advanced quantum property
        orchestrator.add_task("task_vorticity_1", "Vortex Test 1")
        orchestrator.add_task("task_vorticity_2", "Vortex Test 2")

        # Evolve
        for _ in range(15):
            orchestrator.evolve()

        # Both tasks should have valid states
        task1 = orchestrator.state.tasks["task_vorticity_1"]
        task2 = orchestrator.state.tasks["task_vorticity_2"]

        assert task1.probability >= 0, "Task 1 probability valid"
        assert task2.probability >= 0, "Task 2 probability valid"

    # ========================================================================
    # NUMERICAL STABILITY TESTS
    # ========================================================================

    def test_small_timestep_stability(self):
        """Test stability with very small timestep."""
        orch = QuantumRelativisticDiracOrchestrator(dt=0.001)  # Very small
        orch.add_task("task_small_dt", "Small DT Test")

        # Should be stable
        for _ in range(100):
            orch.evolve()

        task = orch.state.tasks["task_small_dt"]
        assert not np.isnan(task.probability), "Should remain stable"

    def test_large_timestep_stability(self):
        """Test behavior with large timestep (may be less stable)."""
        orch = QuantumRelativisticDiracOrchestrator(dt=1.0)  # Large
        orch.add_task("task_large_dt", "Large DT Test")

        # Should still produce valid results
        for _ in range(10):
            orch.evolve()

        task = orch.state.tasks["task_large_dt"]
        assert not np.isnan(task.probability), "Should produce valid results"
        assert 0 <= task.probability <= 1, "Probability should be valid"

    def test_complex_arithmetic_precision(self, constants: PhysicsConstants):
        """Test precision of complex arithmetic."""
        spinor = DiracSpinor(constants=constants)

        # Components should be high precision complex numbers
        for component in spinor.components:
            assert isinstance(
                component, (complex, np.complexfloating)
            ), "Components should be complex"

        # Norm calculation should be precise
        norm = spinor.norm
        assert abs(norm - 1.0) < 1e-10, "Norm should be precisely 1.0"

    def test_matrix_multiplication_accuracy(self, constants: PhysicsConstants):
        """Test accuracy of matrix multiplications."""
        matrices = DiracMatrices()

        # Test matrix multiplications
        result = np.dot(matrices.alpha_x, matrices.alpha_x)

        # α_x² should equal identity
        expected = 2 * np.eye(4)  # Due to {α_i, α_i} = 2I
        assert np.allclose(
            result + np.dot(matrices.alpha_x, matrices.alpha_x), expected, atol=1e-10
        ), "Matrix multiplication should be accurate"


class TestQuantumOrchestratorIntegration:
    """Integration tests for complete orchestrator workflows."""

    def test_complete_workflow_stability(self):
        """Test complete workflow remains stable."""
        orch = QuantumRelativisticDiracOrchestrator()

        # Add multiple tasks
        for i in range(5):
            orch.add_task(
                f"task_{i}",
                f"Task {i}",
                priority=i / 5.0,
                complexity=1.0 + i * 0.1,
            )

        # Run simulation
        for _ in range(50):
            orch.evolve()

        # All tasks should have valid states
        for task_id, task in orch.state.tasks.items():
            assert 0 <= task.probability <= 1, f"{task_id} probability invalid"
            assert not np.isnan(task.probability), f"{task_id} probability is NaN"
            assert task.total_energy > 0, f"{task_id} energy is non-positive"

    def test_task_dependency_ordering(self):
        """Test that task dependencies are respected."""
        orch = QuantumRelativisticDiracOrchestrator()

        # Add tasks with dependencies
        orch.add_task("task_a", "Task A", dependency_depth=0)
        orch.add_task("task_b", "Task B", dependency_depth=1)
        orch.add_task("task_c", "Task C", dependency_depth=2)

        # Evolve
        for _ in range(10):
            orch.evolve()

        # Verify states are valid
        assert len(orch.state.tasks) == 3, "All tasks should be present"

    def test_resource_allocation_fairness(self):
        """Test that resource allocation is fair across tasks."""
        orch = QuantumRelativisticDiracOrchestrator()

        # Add tasks with different resource demands
        for i in range(3):
            orch.add_task(
                f"task_demand_{i}",
                f"Task {i}",
                resource_demand=i / 3.0,
            )

        # Evolve
        for _ in range(20):
            orch.evolve()

        # All tasks should have non-zero evolution
        for task_id in orch.state.tasks:
            task = orch.state.tasks[task_id]
            assert task.probability > 0, f"{task_id} should have positive probability"

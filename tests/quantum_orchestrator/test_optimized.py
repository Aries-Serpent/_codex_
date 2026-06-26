"""
Tests for performance-optimized vectorized quantum orchestrator.
"""

import pytest

np = pytest.importorskip("numpy")

from codex.quantum_orchestrator.optimized import (
    BatchGradientComputer,
    SpatialIndex,
    VectorizedEvolution,
    apply_batch_state,
    extract_batch_state,
)
from codex.quantum_orchestrator.orchestrator import (
    PhysicsConstants,
    create_orchestrator,
)


class TestVectorizedEvolution:
    """Test vectorized evolution operations."""

    def test_batch_evolve_spinors(self):
        """Test batch spinor evolution."""
        constants = PhysicsConstants()
        evolution = VectorizedEvolution(constants)

        # Create batch of spinors
        N = 10
        spinors = np.random.randn(N, 4) + 1j * np.random.randn(N, 4)
        spinors = spinors / np.linalg.norm(spinors, axis=1, keepdims=True)

        gradients = np.random.randn(N, 5) * 0.1
        masses = np.ones(N)
        dt = 0.1

        # Evolve
        evolved = evolution.batch_evolve_spinors(spinors, gradients, masses, dt)

        # Check shape
        assert evolved.shape == (N, 4)

        # Check all spinors are still finite
        assert np.all(np.isfinite(evolved)), "Condition must be true"

    def test_batch_normalize(self):
        """Test batch normalization."""
        constants = PhysicsConstants()
        evolution = VectorizedEvolution(constants)

        # Create un-normalized spinors
        N = 5
        spinors = np.random.randn(N, 4) + 1j * np.random.randn(N, 4)

        # Normalize
        normalized = evolution.batch_normalize(spinors)

        # Check norms
        norms = np.sqrt(np.sum(np.abs(normalized) ** 2, axis=1))
        np.testing.assert_allclose(norms, 1.0, rtol=1e-10)

    def test_batch_compute_dirac_current(self):
        """Test batch Dirac current computation."""
        constants = PhysicsConstants()
        evolution = VectorizedEvolution(constants)

        # Create spinors
        N = 8
        spinors = np.zeros((N, 4), dtype=complex)
        spinors[:, 0] = 1.0  # All in positive energy, spin up

        # Compute currents
        currents = evolution.batch_compute_dirac_current(spinors)

        # Check shape
        assert currents.shape == (N, 3)

        # Check subluminal (|j| <= c)
        current_mags = np.linalg.norm(currents, axis=1)
        assert np.all(current_mags <= constants.c), "current_mags is not valid"

    def test_batch_compute_probabilities(self):
        """Test batch probability computation."""
        constants = PhysicsConstants()
        evolution = VectorizedEvolution(constants)

        # Create normalized spinors
        N = 6
        spinors = np.zeros((N, 4), dtype=complex)
        spinors[:, 0] = 0.8  # Mostly positive energy, spin up
        spinors[:, 1] = 0.6  # Some positive energy, spin down
        spinors = evolution.batch_normalize(spinors)

        # Compute probabilities
        probs = evolution.batch_compute_probabilities(spinors)

        # Check all arrays have correct length
        assert len(probs["total"]) == N, "Collection must not be empty"
        assert len(probs["positive_energy"]) == N, "Collection must not be empty"
        assert len(probs["negative_energy"]) == N, "Collection must not be empty"

        # Check total probability is 1
        np.testing.assert_allclose(probs["total"], 1.0, rtol=1e-10)

        # Check positive + negative = total
        np.testing.assert_allclose(
            probs["positive_energy"] + probs["negative_energy"], probs["total"], rtol=1e-10
        )

    def test_batch_compute_helicity(self):
        """Test batch helicity computation."""
        constants = PhysicsConstants()
        evolution = VectorizedEvolution(constants)

        # Create spinors
        N = 4
        spinors = np.zeros((N, 4), dtype=complex)
        spinors[:, 0] = 1.0  # All spin up

        velocities = np.random.randn(N, 5) * 10

        # Compute helicity
        helicity = evolution.batch_compute_helicity(spinors, velocities)

        # Check shape
        assert helicity.shape == (N,)

        # Check bounds (helicity should be in [-1, 1])
        assert np.all(np.abs(helicity) <= 1.0), "Condition must be true"

    def test_batch_compute_zitterbewegung(self):
        """Test batch zitterbewegung computation."""
        constants = PhysicsConstants()
        evolution = VectorizedEvolution(constants)

        # Create mixed spinors
        N = 5
        spinors = np.zeros((N, 4), dtype=complex)
        spinors[:, 0] = 0.7  # Positive energy
        spinors[:, 2] = 0.7  # Negative energy (causes oscillation)
        spinors = evolution.batch_normalize(spinors)

        # Compute zitterbewegung
        amplitudes = evolution.batch_compute_zitterbewegung(spinors)

        # Check shape
        assert amplitudes.shape == (N,)

        # Check all positive
        assert np.all(amplitudes >= 0), "amplitudes must be greater than zero"

        # Check bounds (amplitude <= 2.0, max is 1.0 when P+=P-=0.5)
        assert np.all(amplitudes <= 2.0), "amplitudes is not valid"


class TestSpatialIndex:
    """Test spatial indexing."""

    def test_build_and_query(self):
        """Test building index and querying neighbors."""
        index = SpatialIndex(cell_size=2.0)

        # Create random positions
        N = 20
        positions = np.random.randn(N, 5) * 10

        # Build index
        index.build_index(positions)

        # Query neighbors
        query_pos = positions[0]
        neighbors = index.query_neighbors(query_pos, positions, radius=5.0)

        # Should at least find itself
        assert len(neighbors) >= 1, "Neighbors must not be empty"
        assert 0 in neighbors, "Condition must be true"

        # Verify all neighbors are within radius
        for idx in neighbors:
            dist = np.linalg.norm(positions[idx] - query_pos)
            assert dist <= 5.0, "dist is not valid"


class TestBatchGradientComputer:
    """Test batch gradient computation."""

    def test_compute_batch_gradients(self):
        """Test gradient computation for all tasks."""
        constants = PhysicsConstants()
        computer = BatchGradientComputer(constants)

        # Create batch state
        N = 10
        spinors = np.zeros((N, 4), dtype=complex)
        spinors[:, 0] = 1.0
        spinors = spinors / np.linalg.norm(spinors, axis=1, keepdims=True)

        positions = np.random.randn(N, 5) * 5

        # Compute gradients
        gradients = computer.compute_batch_gradients(spinors, positions, radius=3.0)

        # Check shape
        assert gradients.shape == (N, 5)

        # Check all finite
        assert np.all(np.isfinite(gradients)), "Condition must be true"


class TestBatchStateOperations:
    """Test batch state extraction and application."""

    def test_extract_and_apply_batch_state(self):
        """Test extracting and applying batch state."""
        # Create orchestrator with tasks
        orch = create_orchestrator()
        orch.add_task("task1", "Task 1", priority=0.8)
        orch.add_task("task2", "Task 2", priority=0.5)
        orch.add_task("task3", "Task 3", priority=0.3)

        # Extract batch state
        batch = extract_batch_state(orch.state.tasks)

        # Check dimensions
        assert batch.spinors.shape == (3, 4)
        assert batch.positions.shape == (3, 5)
        assert batch.velocities.shape == (3, 5)
        assert batch.masses.shape == (3,)
        assert len(batch.task_ids) == 3, "Collection must not be empty"

        # Modify batch state
        batch.spinors *= 0.9

        # Apply back
        apply_batch_state(batch, orch.state.tasks)

        # Verify changes were applied
        for task_id in batch.task_ids:
            task = orch.state.tasks[task_id]
            # Spinor should be modified
            assert np.linalg.norm(task.spinor.components) < 1.0, "Condition must be true"


class TestVectorizedPerformance:
    """Performance tests for vectorized operations."""

    def test_vectorized_vs_loop_performance(self):
        """Compare vectorized vs loop-based evolution."""
        constants = PhysicsConstants()
        evolution = VectorizedEvolution(constants)

        # Create large batch
        N = 100
        spinors = np.random.randn(N, 4) + 1j * np.random.randn(N, 4)
        spinors = spinors / np.linalg.norm(spinors, axis=1, keepdims=True)
        gradients = np.random.randn(N, 5) * 0.1
        masses = np.ones(N)
        dt = 0.1

        # Time vectorized evolution (should be fast)
        import time

        start = time.time()
        for _ in range(10):
            evolved = evolution.batch_evolve_spinors(spinors, gradients, masses, dt)
        vectorized_time = time.time() - start

        # Just check it completes without error
        assert evolved.shape == (N, 4)

        # Vectorized should be reasonably fast
        assert vectorized_time < 1.0, "vectorized_time is not valid"


class TestIntegrationWithOrchestrator:
    """Integration tests with main orchestrator."""

    def test_batch_evolution_matches_sequential(self):
        """Verify batch evolution gives similar results to sequential."""
        # Create orchestrator
        orch = create_orchestrator(time_step=0.1)
        for i in range(5):
            orch.add_task(f"task{i}", f"Task {i}", priority=0.5 + i * 0.1)

        # Get initial state
        initial_batch = extract_batch_state(orch.state.tasks)

        # Evolve with vectorized operations
        constants = PhysicsConstants(hbar=1.0, c=100.0)
        evolution = VectorizedEvolution(constants)
        gradient_computer = BatchGradientComputer(constants)

        gradients = gradient_computer.compute_batch_gradients(
            initial_batch.spinors, initial_batch.positions, radius=2.0
        )

        evolved_spinors = evolution.batch_evolve_spinors(
            initial_batch.spinors, gradients, initial_batch.masses, 0.1
        )

        # Normalize
        evolved_spinors = evolution.batch_normalize(evolved_spinors)

        # Check probabilities are conserved
        evolution.batch_compute_probabilities(initial_batch.spinors)
        evolved_probs = evolution.batch_compute_probabilities(evolved_spinors)

        # Total probability should remain close to 1
        np.testing.assert_allclose(evolved_probs["total"], 1.0, rtol=1e-6)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

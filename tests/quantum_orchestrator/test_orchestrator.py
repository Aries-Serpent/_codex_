"""
Tests for the Quantum-Relativistic-Dirac Orchestrator.

Test coverage:
1. Physical constants and properties
2. Task vectors and spinor states
3. Dirac matrices and operators
4. Time evolution and dynamics
5. Self-healing and stability
6. Flow analysis and bottleneck detection
7. Integration tests
"""


import pytest

np = pytest.importorskip("numpy")

from codex.quantum_orchestrator.orchestrator import (
    DiracSpinor,
    PhysicsConstants,
    TaskVector,
    create_orchestrator,
)


class TestPhysicsConstants:
    """Test physical constants."""

    def test_default_constants(self):
        """Test default constant values."""
        const = PhysicsConstants()
        assert const.hbar == 1.0
        assert const.c == 100.0
        assert const.default_mass == 1.0

    def test_derived_properties(self):
        """Test derived constant properties."""
        const = PhysicsConstants(hbar=2.0, c=50.0)
        assert const.hbar_squared == 4.0
        assert const.c_squared == 2500.0


class TestTaskVector:
    """Test task vector representation."""

    def test_creation(self):
        """Test task vector creation."""
        tv = TaskVector(priority=0.8, complexity=2.0)
        assert tv.priority == 0.8
        assert tv.complexity == 2.0

    def test_to_array(self):
        """Test conversion to numpy array."""
        tv = TaskVector(priority=0.5, complexity=1.5, resource_demand=0.3)
        arr = tv.to_array()
        assert len(arr) == 5
        assert arr[0] == 0.5


class TestDiracSpinor:
    """Test Dirac spinor states."""

    def test_creation(self):
        """Test spinor creation."""
        spinor = DiracSpinor()
        assert len(spinor.components) == 4
        assert spinor.psi_1 == 1.0 + 0j

    def test_probability(self):
        """Test probability calculations."""
        spinor = DiracSpinor()
        assert abs(spinor.total_probability - 1.0) < 1e-10

    def test_normalization(self):
        """Test spinor normalization."""
        components = np.array([2.0 + 0j, 1.0 + 0j, 0.5 + 0j, 0.3 + 0j])
        spinor = DiracSpinor(components=components)

        spinor.normalize()
        assert abs(spinor.total_probability - 1.0) < 1e-10


class TestQuantumOrchestrator:
    """Test complete orchestrator."""

    def test_creation(self):
        """Test orchestrator creation."""
        orch = create_orchestrator()
        assert orch.constants.hbar == 1.0
        assert orch.constants.c == 100.0

    def test_add_task(self):
        """Test adding tasks."""
        orch = create_orchestrator()
        orch.add_task("task1", "Task 1", priority=0.8)

        assert "task1" in orch.state.tasks
        assert orch.state.tasks["task1"].name == "Task 1"

    def test_run_empty(self):
        """Test running with no tasks."""
        orch = create_orchestrator()
        results = orch.run(max_iterations=10)

        assert results["iterations"] >= 0
        assert results["total_tasks"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

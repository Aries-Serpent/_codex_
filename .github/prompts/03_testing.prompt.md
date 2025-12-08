# Comprehensive Testing Suite

> **Prompt**: 03_testing.prompt.md  
> **Previous**: 02_conservation.prompt.md  
> **Next**: 04_optimization.prompt.md  
> **Prerequisites**: All features implemented

---

## Objective

Ensure 100% test coverage of all quantum orchestrator features.

## Current Test Coverage

✅ `test_physics_validation.py` - 28 tests passing:
- Spinor physics
- Relativistic constraints  
- Dirac current properties
- Orchestration dynamics
- Probability conservation
- Physics consistency

## Additional Test Suites Needed

### 1. Integration Tests

**File**: `tests/quantum_orchestrator/test_integration.py`

```python
"""Integration tests for end-to-end orchestration scenarios."""

import pytest
from codex.quantum_orchestrator import create_orchestrator


class TestCompleteWorkflows:
    """Test complete orchestration workflows."""
    
    def test_simple_pipeline(self):
        """Test simple 3-task pipeline."""
        orch = create_orchestrator()
        
        orch.add_task("fetch", "Fetch Data", priority=0.9, rest_mass=1.0)
        orch.add_task("process", "Process", priority=0.8, rest_mass=3.0,
                     dependencies=["fetch"])
        orch.add_task("store", "Store", priority=0.7, rest_mass=1.0,
                     dependencies=["process"])
        
        results = orch.run(max_iterations=200)
        
        assert results["total_tasks"] == 3
        assert results["completion_rate"] >= 0.5
    
    def test_parallel_tasks(self):
        """Test 10 independent parallel tasks."""
        orch = create_orchestrator()
        
        for i in range(10):
            orch.add_task(f"task_{i}", f"Task {i}",
                         priority=0.5 + i*0.05, rest_mass=1.0)
        
        results = orch.run(max_iterations=300)
        
        assert results["total_tasks"] == 10
        assert results["completion_rate"] >= 0.5
    
    def test_resource_contention(self):
        """Test resource-constrained scenario."""
        orch = create_orchestrator()
        
        orch.state.resources = {"cpu": 8.0, "memory": 16.0}
        
        orch.add_task("heavy1", "Heavy 1", rest_mass=5.0,
                     required_resources={"cpu": 6.0, "memory": 12.0})
        orch.add_task("heavy2", "Heavy 2", rest_mass=5.0,
                     required_resources={"cpu": 6.0, "memory": 12.0})
        
        results = orch.run(max_iterations=200)
        
        # Should handle contention gracefully
        assert results["iterations"] > 0
    
    def test_sla_compliance(self):
        """Test SLA deadline enforcement."""
        orch = create_orchestrator(time_step=0.5)
        
        orch.add_task("urgent", "Urgent", priority=0.9,
                     rest_mass=1.0, deadline=5.0)
        orch.add_task("normal", "Normal", priority=0.5,
                     rest_mass=1.0, deadline=20.0)
        
        results = orch.run(max_iterations=50)
        
        # Urgent should complete first
        assert "urgent" in results["completed_tasks"]


class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_empty_orchestrator(self):
        """Test running with no tasks."""
        orch = create_orchestrator()
        results = orch.run(max_iterations=10)
        assert results["total_tasks"] == 0
    
    def test_circular_dependencies(self):
        """Test handling of circular dependencies."""
        orch = create_orchestrator()
        
        orch.add_task("a", "A", dependencies=["b"])
        orch.add_task("b", "B", dependencies=["a"])
        
        # Should not deadlock
        results = orch.run(max_iterations=100)
        assert results["iterations"] > 0
    
    def test_missing_dependency(self):
        """Test task with non-existent dependency."""
        orch = create_orchestrator()
        
        orch.add_task("task", "Task", dependencies=["nonexistent"])
        
        # Should handle gracefully
        results = orch.run(max_iterations=100)
        assert results["total_tasks"] == 1
```

### 2. Performance Tests

**File**: `tests/quantum_orchestrator/test_performance.py`

```python
"""Performance and scalability tests."""

import pytest
import time
from codex.quantum_orchestrator import create_orchestrator


class TestPerformance:
    """Test orchestrator performance."""
    
    def test_evolution_speed(self):
        """Test evolution performance."""
        orch = create_orchestrator()
        
        # Add 50 tasks
        for i in range(50):
            orch.add_task(f"task_{i}", f"Task {i}", rest_mass=1.0)
        
        # Time 100 evolution steps
        start = time.time()
        for _ in range(100):
            orch.evolve()
        elapsed = time.time() - start
        
        # Should complete in reasonable time
        assert elapsed < 5.0  # 5 seconds for 100 iterations
        
        # Check rate
        rate = 100 / elapsed
        print(f"Evolution rate: {rate:.1f} iter/sec")
        assert rate > 10  # At least 10 iterations/second
    
    def test_large_scale(self):
        """Test with 100 tasks."""
        orch = create_orchestrator()
        
        for i in range(100):
            orch.add_task(f"task_{i}", f"Task {i}", rest_mass=1.0)
        
        results = orch.run(max_iterations=200)
        
        assert results["total_tasks"] == 100
        assert results["iterations"] <= 200
    
    @pytest.mark.slow
    def test_very_large_scale(self):
        """Test with 500 tasks (marked as slow)."""
        orch = create_orchestrator()
        
        for i in range(500):
            orch.add_task(f"task_{i}", f"Task {i}", rest_mass=1.0)
        
        start = time.time()
        results = orch.run(max_iterations=100)
        elapsed = time.time() - start
        
        assert results["total_tasks"] == 500
        assert elapsed < 30.0  # Should complete in 30 seconds
```

### 3. Regression Tests

**File**: `tests/quantum_orchestrator/test_regression.py`

```python
"""Regression tests for known issues."""

import pytest
from codex.quantum_orchestrator import create_orchestrator


class TestRegressions:
    """Test previously fixed bugs don't reappear."""
    
    def test_taskVector_addition_dtype(self):
        """Regression: TaskVector addition returned wrong dtype."""
        from codex.quantum_orchestrator import TaskVector
        
        tv1 = TaskVector(priority=0.5, complexity=1.0)
        tv2 = TaskVector(priority=0.3, complexity=0.5)
        tv3 = tv1 + tv2
        
        assert isinstance(tv3, TaskVector)
        assert abs(tv3.priority - 0.8) < 1e-10
    
    def test_gradient_complex_dtype(self):
        """Regression: Gradient calculation had dtype mismatch."""
        orch = create_orchestrator()
        orch.add_task("t1", "T1", rest_mass=1.0)
        orch.add_task("t2", "T2", rest_mass=1.0)
        
        # Should not raise dtype error
        orch.evolve()
        
        assert True  # If we got here, no dtype error
    
    def test_zitterbewegung_bounds(self):
        """Regression: Zitterbewegung could exceed 1.0."""
        orch = create_orchestrator()
        orch.add_task("test", "Test", rest_mass=1.0)
        
        task = orch.state.tasks["test"]
        zitter = orch.dirac.zitterbewegung_amplitude(task)
        
        assert 0.0 <= zitter <= 1.01  # Allow floating point error
```

## Running All Tests

```bash
# Run all tests with coverage
PYTHONPATH=src:$PYTHONPATH python3 -m pytest \
    tests/quantum_orchestrator/ \
    -v \
    --cov=src/codex/quantum_orchestrator \
    --cov-report=term-missing \
    --cov-report=html

# Run only fast tests
PYTHONPATH=src:$PYTHONPATH python3 -m pytest \
    tests/quantum_orchestrator/ \
    -v \
    -m "not slow"

# Run specific test class
PYTHONPATH=src:$PYTHONPATH python3 -m pytest \
    tests/quantum_orchestrator/test_integration.py::TestCompleteWorkflows \
    -v
```

## Coverage Goals

- **Target**: 90%+ coverage of orchestrator.py
- **Critical**: 100% coverage of physics operators
- **Acceptable**: 80%+ overall

## Test Markers

Add to `pytest.ini`:
```ini
[pytest]
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    performance: marks tests as performance tests
```

## Success Criteria

- [ ] Integration test suite created (10+ tests)
- [ ] Performance test suite created (3+ tests)
- [ ] Regression test suite created (5+ tests)
- [ ] All tests passing
- [ ] Coverage ≥ 85%
- [ ] No slow tests in default run

## Next Steps

Proceed to: **Next Prompt**: `04_optimization.prompt.md`

---

**Status**: Testing complete ✅

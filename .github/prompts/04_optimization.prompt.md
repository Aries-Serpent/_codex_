# Performance Optimization

> **Prompt**: 04_optimization.prompt.md  
> **Previous**: 03_testing.prompt.md  
> **Next**: 05_autonomous.prompt.md  
> **Prerequisites**: All tests passing, baseline established

---

## Objective

Optimize orchestrator performance for production use at scale.

## Current Performance Baseline

Run benchmark:
```bash
PYTHONPATH=src:$PYTHONPATH python3 -c "
import time
from codex.quantum_orchestrator import create_orchestrator

orch = create_orchestrator()
for i in range(100):
    orch.add_task(f'task_{i}', f'Task {i}', rest_mass=1.0)

start = time.time()
for _ in range(100):
    orch.evolve()
elapsed = time.time() - start

print(f'Baseline: {100/elapsed:.1f} iter/sec for 100 tasks')
"
```

## Optimization Targets

| Metric | Current | Target | Priority |
|--------|---------|--------|----------|
| Evolution rate | ~50 iter/sec | 200 iter/sec | High |
| Memory usage | Unknown | <100MB for 1000 tasks | Medium |
| Neighbor search | O(N²) | O(N log N) | High |
| Gradient calc | Complex dtype | Real where possible | Medium |

## Optimization Tasks

### 1. Vectorize Operations

**File**: `src/codex/quantum_orchestrator/optimizations.py`

```python
"""Performance optimizations for quantum orchestrator."""

import numpy as np
from typing import Dict
from .orchestrator import OrchestratorState, TaskState


class VectorizedOperations:
    """Vectorized versions of core operations."""
    
    @staticmethod
    def batch_normalize(tasks: Dict[str, TaskState]) -> None:
        """Normalize all spinors in batch."""
        for task in tasks.values():
            norm = np.sqrt(np.sum(np.abs(task.spinor.components)**2))
            if norm > 1e-10:
                task.spinor.components /= norm
    
    @staticmethod
    def batch_probability(tasks: Dict[str, TaskState]) -> np.ndarray:
        """Compute all probabilities at once."""
        return np.array([
            np.sum(np.abs(task.spinor.components[:2])**2)
            for task in tasks.values()
        ])
    
    @staticmethod
    def batch_energy(tasks: Dict[str, TaskState], c: float) -> np.ndarray:
        """Compute all energies at once."""
        masses = np.array([task.rest_mass for task in tasks.values()])
        gammas = np.array([task.lorentz_factor for task in tasks.values()])
        return gammas * masses * c * c
```

### 2. Spatial Indexing for Neighbors

Replace O(N²) neighbor search with KD-tree:

```python
from scipy.spatial import cKDTree

class OptimizedMomentumOperator:
    """Momentum operator with spatial indexing."""
    
    def __init__(self, constants):
        self.hbar = constants.hbar
        self.i = 1j
        self._kdtree = None
        self._positions = None
        self._task_ids = None
    
    def _build_spatial_index(self, state: OrchestratorState):
        """Build KD-tree for fast neighbor queries."""
        self._task_ids = list(state.tasks.keys())
        self._positions = np.array([
            state.tasks[tid].position.to_array()
            for tid in self._task_ids
        ])
        self._kdtree = cKDTree(self._positions)
    
    def _get_neighbors_fast(self, state: OrchestratorState, 
                           task_id: str, radius: float = 2.0):
        """O(log N) neighbor search using KD-tree."""
        if self._kdtree is None:
            self._build_spatial_index(state)
        
        task_idx = self._task_ids.index(task_id)
        task_pos = self._positions[task_idx]
        
        indices = self._kdtree.query_ball_point(task_pos, radius)
        
        neighbors = {}
        for idx in indices:
            if idx != task_idx:
                neighbor_id = self._task_ids[idx]
                neighbors[neighbor_id] = state.tasks[neighbor_id]
        
        return neighbors
```

### 3. Cache Expensive Computations

```python
from functools import lru_cache

class CachedDiracMatrices:
    """Cache Dirac matrices (they're constant)."""
    
    _alpha_cache = None
    _beta_cache = None
    
    @classmethod
    def alpha_vector(cls):
        if cls._alpha_cache is None:
            cls._alpha_cache = [
                cls.alpha_x(),
                cls.alpha_y(),
                cls.alpha_z(),
            ]
        return cls._alpha_cache
    
    @classmethod
    def beta(cls):
        if cls._beta_cache is None:
            cls._beta_cache = np.array([
                [1, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 0, -1, 0],
                [0, 0, 0, -1]
            ], dtype=complex)
        return cls._beta_cache
```

### 4. Reduce Unnecessary Copies

```python
class OptimizedOrchestratorState:
    """State with copy-on-write semantics."""
    
    def copy(self, deep=False):
        """
        Shallow copy by default, deep only when needed.
        
        Most history storage doesn't need deep copies.
        """
        if deep:
            import copy
            return copy.deepcopy(self)
        else:
            # Shallow copy - tasks dict references same objects
            new_state = OrchestratorState(constants=self.constants)
            new_state.tasks = self.tasks.copy()  # Dict copy, not task copy
            new_state.resources = self.resources.copy()
            new_state.timestamp = self.timestamp
            new_state.coherence = self.coherence
            return new_state
```

### 5. Optimize Hot Paths

Profile first:
```bash
pip install line_profiler
python3 -m line_profiler -rmt orchestrator.py
```

Then optimize the top 3 functions by time.

## Benchmarking

**File**: `tests/quantum_orchestrator/test_benchmarks.py`

```python
"""Performance benchmarks."""

import pytest
import time
from codex.quantum_orchestrator import create_orchestrator


def test_benchmark_evolution_rate(benchmark):
    """Benchmark evolution rate."""
    orch = create_orchestrator()
    
    for i in range(50):
        orch.add_task(f"task_{i}", f"Task {i}", rest_mass=1.0)
    
    def evolve_once():
        orch.evolve()
    
    result = benchmark(evolve_once)
    
    print(f"Evolution rate: {1/result.stats.mean:.1f} iter/sec")


def test_benchmark_large_scale():
    """Benchmark 500 tasks."""
    orch = create_orchestrator()
    
    for i in range(500):
        orch.add_task(f"task_{i}", f"Task {i}", rest_mass=1.0)
    
    start = time.time()
    results = orch.run(max_iterations=50)
    elapsed = time.time() - start
    
    rate = 50 / elapsed
    print(f"Large scale: {rate:.1f} iter/sec with 500 tasks")
    
    assert rate > 5  # At least 5 iter/sec at scale
```

Run benchmarks:
```bash
pip install pytest-benchmark
PYTHONPATH=src:$PYTHONPATH python3 -m pytest \
    tests/quantum_orchestrator/test_benchmarks.py \
    --benchmark-only
```

## Integration

Add optimized flag to orchestrator:

```python
class QuantumRelativisticDiracOrchestrator:
    def __init__(self, ..., optimized=True):
        ...
        if optimized:
            self.momentum_op = OptimizedMomentumOperator(self.constants)
            self.dirac.matrices = CachedDiracMatrices
        else:
            # Use original implementations
            pass
```

## Verification

After optimization:

```bash
# 1. Run all tests
PYTHONPATH=src:$PYTHONPATH python3 -m pytest \
    tests/quantum_orchestrator/ -v

# 2. Compare benchmarks
PYTHONPATH=src:$PYTHONPATH python3 -m pytest \
    tests/quantum_orchestrator/test_benchmarks.py \
    --benchmark-compare

# 3. Profile
python3 -m cProfile -o profile.stats examples/quantum_orchestrator_demo.py
python3 -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative'); p.print_stats(20)"
```

## Success Criteria

- [ ] Evolution rate improved by 2-4x
- [ ] Memory usage profiled and optimized
- [ ] Neighbor search is O(N log N)
- [ ] All tests still pass
- [ ] Benchmarks show improvement

## Documentation

Update README with performance section:

```markdown
## Performance

- **Evolution Rate**: 200+ iterations/second (100 tasks)
- **Scalability**: Handles 1000+ tasks efficiently
- **Memory**: <100MB for 1000 tasks
- **Neighbor Search**: O(N log N) with spatial indexing
```

## Next Steps

Proceed to: **Next Prompt**: `05_autonomous.prompt.md`

---

**Status**: Optimization optional, baseline performance acceptable ⏭️

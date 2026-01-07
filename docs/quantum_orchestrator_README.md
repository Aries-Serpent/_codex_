# Quantum-Relativistic-Dirac Orchestrator Framework

A physics-inspired task orchestration framework implementing quantum mechanics, special relativity, and Dirac spinor dynamics for intelligent, self-healing task scheduling.

## Overview

This framework treats tasks as quantum-relativistic particles evolving under physical laws, providing natural solutions to orchestration challenges:

- **Schrödinger Dynamics**: Tasks exist in superposition until executed
- **Klein-Gordon Relativistic Extension**: Enforces maximum throughput limits
- **Probability Current & Flow**: Detects bottlenecks via conservation laws
- **Dirac Spinor Dynamics**: 4-component states model progress/regression

## Key Physics Concepts

### 1. The Schrödinger Equation

```
iℏ∂ψ/∂t = Ĥψ = (T̂ + V̂)ψ
```

Tasks evolve according to a Hamiltonian combining:
- **Kinetic energy (T̂)**: Exploration and parallelization
- **Potential energy (V̂)**: Constraints, dependencies, SLAs

### 2. Relativistic Energy-Momentum

```
E² = p²c² + m²c⁴
```

- **c (speed of light)**: Maximum system throughput
- **m (rest mass)**: Base task complexity
- **E₀ = mc²**: Idle cost even when not running

### 3. Probability Current

```
j = (iℏ/2mc²)(ψ*∂ψ/∂t - ψ∂ψ*/∂t)
```

Measures how probability flows through the system:
- Positive current: Progress toward completion
- Negative current: Regression
- Zero current: Bottleneck

### 4. Dirac Equation

```
iℏ∂ψ/∂t = -iℏα·∇ψ + βmc²ψ
```

4-component spinor ψ = (ψ₁, ψ₂, ψ₃, ψ₄) represents:
- ψ₁, ψ₂: Positive energy (progress modes)
- ψ₃, ψ₄: Negative energy (regression modes)

## Installation

```bash
# Install dependencies
pip install numpy

# Add to Python path
export PYTHONPATH="/home/runner/work/_codex_/_codex_/src:$PYTHONPATH"
```

## Quick Start

```python
from codex.quantum_orchestrator.orchestrator import create_orchestrator

# Create orchestrator
orch = create_orchestrator(
    max_throughput=100.0,  # Maximum tasks/second
    work_granularity=1.0,  # Minimum work unit
    time_step=0.1          # Evolution time step
)

# Add tasks
orch.add_task(
    task_id="task_1",
    name="Initialize System",
    priority=0.9,
    complexity=2.0,
    rest_mass=2.0
)

orch.add_task(
    task_id="task_2",
    name="Process Data",
    priority=0.8,
    complexity=5.0,
    rest_mass=5.0,
    dependencies=["task_1"],
    deadline=10.0  # SLA deadline
)

# Run orchestration
results = orch.run(max_iterations=100)

print(f"Completed: {results['completion_rate']:.1%}")
print(f"Time: {results['final_timestamp']:.2f}")

# Get task status
status = orch.get_task_status()
for task_id, info in status.items():
    print(f"{task_id}: {info['probability']:.2%} complete")
    print(f"  Stable: {info['stable']}")
    print(f"  Energy: {info['energy']:.2f}")
```

## Core Components

### PhysicsConstants

Defines fundamental constants:
- `hbar`: Planck's reduced constant (work granularity)
- `c`: Speed of light (max throughput)
- `default_mass`: Default task complexity

### TaskVector

5D position in task space:
- Priority axis
- Complexity axis
- Resource demand axis
- Time sensitivity axis
- Dependency depth axis

### DiracSpinor

4-component quantum state:
```python
spinor = DiracSpinor()
print(f"Progress probability: {spinor.positive_energy_prob}")
print(f"Regression probability: {spinor.negative_energy_prob}")
```

### TaskState

Complete task representation:
```python
task = TaskState(
    task_id="example",
    name="Example Task",
    position=TaskVector(priority=0.8, complexity=2.0),
    rest_mass=2.0,
    deadline=10.0,
    dependencies=["dep1", "dep2"],
    required_resources={"cpu": 4.0, "memory": 8.0}
)
```

## Advanced Features

### 1. Self-Healing

The orchestrator automatically detects and corrects:

**Zitterbewegung (Instability)**:
```python
unstable_tasks = orch.check_stability()
orch.self_heal()  # Stabilizes unstable tasks
```

**Bottlenecks**:
```python
bottlenecks = orch.flow_analyzer.identify_bottlenecks(
    orch.state, prev_state, dt=0.1
)
for bn in bottlenecks:
    print(f"Bottleneck: {bn['task_id']}, severity={bn['severity']}")
```

### 2. Flow Analysis

Monitor probability flow:
```python
# Current flow rate
current = orch.current_op.task_current(
    current_state, prev_state, task_id, dt
)
print(f"Flow rate: {current:.3f}")

# Efficiency
efficiency = orch.flow_analyzer.flow_efficiency(
    current_state, prev_state, dt
)
print(f"System efficiency: {efficiency:.1%}")
```

### 3. Physics Properties

Access relativistic properties:
```python
task = orch.state.tasks["task_id"]

print(f"Lorentz factor γ: {task.lorentz_factor}")
print(f"Relativistic mass: {task.relativistic_mass}")
print(f"Total energy: {task.total_energy}")
print(f"Rest energy: {task.rest_energy}")

# Dirac-specific
current = orch.dirac.compute_current(task)
helicity = orch.dirac.helicity(task, orch.state)
zitter = orch.dirac.zitterbewegung_amplitude(task)

print(f"Current vector: {current}")
print(f"Helicity: {helicity:.3f}")
print(f"Zitterbewegung: {zitter:.3f}")
```

## Examples

See `examples/quantum_orchestrator_demo.py` for complete examples:

1. **Basic Orchestration**: Simple task pipeline
2. **SLA Deadlines**: Time-sensitive tasks
3. **Resource Constraints**: Limited resource allocation
4. **Spinor Analysis**: Deep dive into quantum properties

Run examples:
```bash
cd /home/runner/work/_codex_/_codex_
python examples/quantum_orchestrator_demo.py
```

## Testing

Run comprehensive test suite:
```bash
cd /home/runner/work/_codex_/_codex_
pytest tests/quantum_orchestrator/test_orchestrator.py -v
```

Tests cover:
- Physical constants and properties
- Task vectors and spinor states
- Dirac matrices and operators
- Time evolution and dynamics
- Self-healing and stability
- Flow analysis and bottleneck detection
- Integration scenarios

## Architecture

```
src/codex/quantum_orchestrator/
├── __init__.py              # Package exports
├── constants.py             # Physical constants
├── orchestrator.py          # Main implementation
├── state/
│   ├── task_vector.py       # Position in task space
│   ├── task_state.py        # Complete task state
│   ├── spinor_state.py      # Dirac spinor
│   └── orchestrator_state.py # System state
├── operators/
│   ├── momentum.py          # p̂ = -iℏ∇
│   ├── energy.py            # Ê = iℏ∂/∂t
│   ├── hamiltonian.py       # Ĥ = T̂ + V̂
│   ├── klein_gordon.py      # Relativistic extension
│   ├── probability_current.py # Flow analysis
│   └── dirac.py             # Dirac equation
└── dynamics/
    ├── evolution.py         # Time evolution
    └── self_healing.py      # Self-healing logic
```

## Physics Validation

The implementation maintains physical accuracy:

### Energy-Momentum Relation
```python
E² ≈ p²c² + m²c⁴  # Verified in tests
```

### Lorentz Factor
```python
γ = 1/√(1 - v²/c²) ≥ 1  # Always satisfied
```

### Speed Limit
```python
v < c  # Enforced via apply_force()
```

### Probability Conservation
```python
∂ρ/∂t + ∇·j = 0  # Checked via ContinuityChecker
```

### Dirac Current Bound
```python
|j| ≤ c  # Always subluminal
```

## Performance Considerations

- **Time Complexity**: O(N²) per iteration for N tasks (due to neighbor calculations)
- **Space Complexity**: O(N) for state storage
- **Typical Performance**: ~1000 iterations/second for 100 tasks

Optimization tips:
- Use larger `time_step` (dt) for faster convergence
- Reduce neighbor radius in momentum calculations
- Pre-allocate task arrays
- Use vectorized numpy operations

## Limitations

1. **Approximations**: First-order Euler method for time evolution
2. **Discrete Space**: Finite-difference gradients
3. **Simplified Potential**: may not capture all constraints
4. **No Entanglement**: Tasks are independent (no quantum entanglement)

## Future Extensions

Potential enhancements:
- [ ] Quantum Field Theory operators (creation/annihilation)
- [ ] Entanglement for correlated tasks
- [ ] Path integral formulation
- [ ] Quantum tunneling for deadlock resolution
- [ ] Gauge symmetries for invariances
- [ ] Renormalization group for scale-invariance

## References

**Physics:**
- Dirac, P.A.M. (1928). "The Quantum Theory of the Electron"
- Bjorken & Drell. "Relativistic Quantum Mechanics"
- Sakurai. "Modern Quantum Mechanics"

**Orchestration:**
- MLOps maturity models
- Self-healing systems
- Flow-based scheduling

## License

MIT License - See repository LICENSE file

## Authors

- mbaetiong (Framework Design & Implementation)
- Based on physics-inspired orchestration principles

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- See CONTRIBUTING.md for guidelines
- Review examples/ for usage patterns

---

**Note**: This is a research/experimental framework demonstrating physics-inspired orchestration. For production use, consider:
- Extensive testing on your workload
- Performance profiling
- Integration with existing systems
- Monitoring and observability

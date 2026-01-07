# Quantum Orchestrator CLI Documentation

## Overview

The Quantum Orchestrator CLI provides command-line access to the physics-inspired task orchestration framework. It implements quantum mechanics, special relativity, and quantum field theory concepts for task management.

## Installation

The CLI is integrated with the main Codex CLI and is available after installing the codex-ml package:

```bash
pip install -e .
```

## Quick Start

```bash
# View available commands
python -m codex.cli quantum --help

# Run a simple orchestration
python -m codex.cli quantum run --tasks 5 --steps 10

# Benchmark performance
python -m codex.cli quantum benchmark --tasks 100 --iterations 1000

# Inspect task quantum state
python -m codex.cli quantum inspect task_0

# Export metrics
python -m codex.cli quantum metrics --tasks 10
```

## Commands

### Core Commands

#### `run` - Run Orchestration

Executes the quantum orchestrator with test tasks, demonstrating the core physics-inspired dynamics.

**Options:**
- `--tasks INTEGER`: Number of test tasks to create (default: 5)
- `--steps INTEGER`: Number of evolution steps (default: 10)
- `--dt FLOAT`: Time step size (default: 0.1)
- `--output PATH`: Output file for results (JSON format)
- `--verbose`: Enable verbose output

**Examples:**
```bash
# Basic run with 10 tasks for 20 steps
python -m codex.cli quantum run --tasks 10 --steps 20

# Save results to file
python -m codex.cli quantum run --tasks 5 --output results.json

# Verbose mode
python -m codex.cli quantum run --tasks 3 --steps 5 --verbose
```

**Output:**
- Evolution progress showing time, total probability, and coherence
- Final state of all tasks with probability and energy
- Optional JSON export of full execution trajectory

---

#### `benchmark` - Performance Benchmark

Measures evolution speed and throughput for performance tuning and regression testing.

**Options:**
- `--tasks INTEGER`: Number of tasks to benchmark (default: 10)
- `--iterations INTEGER`: Number of iterations (default: 100)
- `--warmup INTEGER`: Warmup iterations (default: 10)

**Examples:**
```bash
# Standard benchmark
python -m codex.cli quantum benchmark --tasks 100 --iterations 1000

# Quick test
python -m codex.cli quantum benchmark --tasks 10 --iterations 100
```

**Output:**
- Total execution time
- Time per iteration (milliseconds)
- Throughput (iterations/sec, tasks/sec)

---

#### `inspect` - Inspect Quantum State

Shows detailed information about a specific task's quantum state.

**Arguments:**
- `TASK_ID`: ID of the task to inspect

**Options:**
- `--format [text|json]`: Output format (default: text)

**Examples:**
```bash
# Text format (default)
python -m codex.cli quantum inspect task_0

# JSON format
python -m codex.cli quantum inspect task_1 --format json
```

**Output (text format):**
- Task ID and name
- Position in 5D task space (priority, complexity, etc.)
- Probability and energy
- Dirac spinor components (ψ₁, ψ₂, ψ₃, ψ₄)
- Velocity and mass

**Output (JSON format):**
- Structured JSON with all task state information

---

#### `metrics` - Export Prometheus Metrics

Generates Prometheus-formatted metrics for monitoring and observability.

**Options:**
- `--tasks INTEGER`: Number of tasks in system (default: 5)
- `--output PATH`: Output file for metrics (default: stdout)

**Examples:**
```bash
# Print to stdout
python -m codex.cli quantum metrics --tasks 10

# Save to file
python -m codex.cli quantum metrics --output metrics.txt
```

**Metrics exported:**
- `quantum_orchestrator_tasks`: Total number of tasks
- `quantum_orchestrator_total_probability`: Total probability across all tasks
- `quantum_orchestrator_coherence`: System coherence
- `quantum_orchestrator_task_probability{task_id="..."}`: Per-task probability
- `quantum_orchestrator_task_energy{task_id="..."}`: Per-task energy
- `quantum_orchestrator_task_speed{task_id="..."}`: Per-task speed

---

### QFT Commands

Advanced commands using Quantum Field Theory extensions (second quantization, entanglement, path integrals).

#### `qft spawn` - Spawn Tasks

Uses creation operators from second quantization to dynamically spawn new tasks.

**Options:**
- `--count INTEGER`: Number of tasks to spawn (default: 3)
- `--mode TEXT`: Spawning mode (default: 'default')

**Examples:**
```bash
# Spawn 5 tasks
python -m codex.cli quantum qft spawn --count 5

# Spawn with specific mode
python -m codex.cli quantum qft spawn --count 10 --mode parallel
```

**Physics:**
- Implements creation operator â†
- For bosons: â†|n⟩ = √(n+1)|n+1⟩
- For fermions: â†|0⟩ = |1⟩, â†|1⟩ = 0 (Pauli exclusion)

---

#### `qft entangle` - Create Entanglement

Creates Bell state entanglement between two tasks for coordinated execution.

**Arguments:**
- `TASK_A`: First task ID
- `TASK_B`: Second task ID

**Options:**
- `--bell-state [phi_plus|phi_minus|psi_plus|psi_minus]`: Type of Bell state (default: phi_plus)

**Examples:**
```bash
# Create correlated entanglement
python -m codex.cli quantum qft entangle task_0 task_1

# Create singlet state (anti-correlated)
python -m codex.cli quantum qft entangle task_0 task_1 --bell-state psi_minus
```

**Bell States:**
- `phi_plus` (|Φ+⟩): Correlated - tasks succeed/fail together
- `phi_minus` (|Φ-⟩): Correlated with phase difference
- `psi_plus` (|Ψ+⟩): Anti-correlated - opposite outcomes
- `psi_minus` (|Ψ-⟩): Singlet state - maximum entanglement

**Use Cases:**
- Coordinated deployments (all succeed or all fail)
- Feature flags (flip together)
- A/B testing (mutually exclusive outcomes)
- Distributed consensus

---

#### `qft optimize` - Path Integral Optimization

Uses Feynman path integral formulation to find optimal execution strategies.

**Options:**
- `--paths INTEGER`: Number of paths to sample (default: 100)
- `--temperature FLOAT`: Annealing temperature (default: 1.0)
- `--task-count INTEGER`: Number of tasks in system (default: 5)

**Examples:**
```bash
# Standard optimization
python -m codex.cli quantum qft optimize --paths 1000

# Low temperature (more deterministic)
python -m codex.cli quantum qft optimize --paths 500 --temperature 0.5

# High temperature (more exploration)
python -m codex.cli quantum qft optimize --paths 500 --temperature 2.0
```

**Physics:**
- Samples multiple possible execution paths
- Computes action functional S = ∫L dt for each path
- Uses quantum annealing to find low-action (optimal) paths
- Temperature controls exploration vs exploitation

---

## Physical Concepts

### Task State Representation

Each task is represented as a 4-component Dirac spinor in 5D task space:

**Task Space Dimensions:**
1. Priority (0.0 - 1.0)
2. Complexity (arbitrary units)
3. Resource demand (0.0 - 1.0)
4. Time sensitivity (0.0 - 1.0)
5. Dependency depth (integer)

**Spinor Components:**
- ψ₁: Positive energy, spin up (primary progress)
- ψ₂: Positive energy, spin down (alternative progress)
- ψ₃: Negative energy, spin up (primary regression)
- ψ₄: Negative energy, spin down (alternative regression)

### Evolution Dynamics

Tasks evolve according to the Dirac equation:

```
iℏ∂ψ/∂t = (-iℏα·∇ + βmc²)ψ
```

Where:
- ℏ (hbar): Work granularity (default: 1.0)
- c: Maximum throughput (default: 100.0 tasks/time)
- m: Task complexity (rest mass)
- α, β: Dirac matrices

### Conservation Laws

The orchestrator respects fundamental conservation laws:

1. **Probability Conservation**: Σᵢ|ψᵢ|² = 1 for each task
2. **Momentum Conservation**: Total momentum conserved (from translation symmetry)
3. **Energy Conservation**: Total energy conserved in autonomous systems
4. **Continuity Equation**: ∂ρ/∂t + ∇·j = 0 (probability flow)

---

## Examples

### Example 1: Simple Workflow

```bash
# 1. Run orchestration
python -m codex.cli quantum run --tasks 5 --steps 20 --output run.json

# 2. Inspect a specific task
python -m codex.cli quantum inspect task_0 --format json

# 3. Export metrics for monitoring
python -m codex.cli quantum metrics --tasks 5 --output metrics.prom
```

### Example 2: QFT Workflow

```bash
# 1. Spawn additional tasks
python -m codex.cli quantum qft spawn --count 3

# 2. Create entanglement for coordinated execution
python -m codex.cli quantum qft entangle task_0 task_1 --bell-state phi_plus

# 3. Optimize execution path
python -m codex.cli quantum qft optimize --paths 1000 --temperature 0.5
```

### Example 3: Performance Testing

```bash
# 1. Benchmark small system
python -m codex.cli quantum benchmark --tasks 10 --iterations 100

# 2. Benchmark large system
python -m codex.cli quantum benchmark --tasks 1000 --iterations 10000

# 3. Compare results
# (Use output to identify performance regressions)
```

---

## Integration with Codex

The Quantum Orchestrator CLI is integrated with the main Codex CLI. Access it via:

```bash
# Using python module
python -m codex.cli quantum [COMMAND]

# If installed with entry point
codex quantum [COMMAND]
```

---

## Troubleshooting

### Import Errors

If you get module import errors:

```bash
# Install numpy if missing
pip install numpy

# Install with all dependencies
pip install -e ".[dev]"
```

### PyTorch Warnings

The sitecustomize warnings about PyTorch can be safely ignored if you're not using PyTorch features:

```bash
# Suppress warnings
PYTHONWARNINGS="ignore" python -m codex.cli quantum run --tasks 5
```

---

## Advanced Usage

### Custom Physics Constants

While the CLI uses default values, you can modify the underlying orchestrator by importing it programmatically:

```python
from codex.quantum_orchestrator import create_observable_orchestrator

# Create with custom constants
orchestrator = create_observable_orchestrator(
    max_throughput=200.0,  # Higher c (faster evolution)
    work_granularity=0.5,  # Lower ℏ (finer granularity)
    time_step=0.05,        # Smaller dt (more accurate)
)
```

### Monitoring Integration

Metrics can be exported to Prometheus for real-time monitoring:

```bash
# Export metrics periodically
while true; do
    python -m codex.cli quantum metrics --output /var/lib/prometheus/quantum_metrics.prom
    sleep 15
done
```

---

## References

- **Physics Background**: See `QUANTUM_ORCHESTRATOR_FRAMEWORK.md` for mathematical details
- **API Documentation**: See module docstrings in `src/codex/quantum_orchestrator/`
- **Tests**: See `tests/quantum_orchestrator/` for usage examples

---

## Support

For issues or questions:
1. Check the test suite for usage examples
2. Review the module docstrings
3. Open an issue on GitHub

---

## Version

- CLI Version: 0.3.0
- Phase C.4: Gauge Symmetries and CLI Commands
- Last Updated: Previous Cycle-12-08

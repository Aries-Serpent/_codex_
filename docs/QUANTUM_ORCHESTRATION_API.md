# Quantum Orchestration API Reference
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Status:** Phase 2 - Master API Documentation  
**Coverage:** 91+ public functions & classes  
**Modules:** quantum_orchestrator/*, cognitive/quantum_planset_engine.py  
**Last Updated: 2026-07-08

---

## Table of Contents
1. [Quantum Orchestrator Core](#quantum-orchestrator-core)
2. [Task State Representation](#task-state-representation)
3. [Physics-Inspired Operations](#physics-inspired-operations)
4. [Quantum Planset Engine](#quantum-planset-engine)
5. [Function Index](#function-index)
6. [Examples](#examples)

---

## Quantum Orchestrator Core

**File:** `src/codex/quantum_orchestrator/orchestrator.py`  
**Purpose:** Core orchestration engine using quantum-relativistic physics for agent coordination  
**LOC:** 655 | **API:** 65 public functions & classes

### Classes

#### `PhysicsConstants`
**Description:** Physical constants governing the orchestrator.

**Properties:**
- `c: float` — Speed of light (maximum throughput), default 100.0
- `hbar: float` — Planck's reduced constant (work granularity), default 1.0
- `default_mass: float` — Default task complexity, default 1.0

**Methods:**

##### `c_squared() -> float`
**Returns:** `c²` for relativistic calculations

**Source:** `src/codex/quantum_orchestrator/orchestrator.py:39`

---

##### `hbar_squared() -> float`
**Returns:** `ℏ²` for quantum calculations

**Source:** `src/codex/quantum_orchestrator/orchestrator.py:43`

---

#### `TaskVector`
**Description:** Position in 5D task space with quantum properties.

**Fields:**
- `priority: float` — Task priority (0.0-1.0)
- `complexity: float` — Task complexity metric (default 1.0)
- `resource_demand: float` — Required resources
- `time_sensitivity: float` — Time criticality (0.0-1.0)
- `dependency_depth: int` — Maximum dependency depth

**Methods:**

##### `to_array() -> np.ndarray`
**Signature:** `def to_array(self) -> np.ndarray`

Convert task vector to NumPy array.

**Returns:** `np.ndarray` — 5-element array [priority, complexity, resource_demand, time_sensitivity, dependency_depth]

**Source:** `src/codex/quantum_orchestrator/orchestrator.py:62`

**Example:**
```python
task = TaskVector(priority=0.8, complexity=2.0)
arr = task.to_array()  # [0.8, 2.0, 0.0, 0.0, 0]
```

---

##### `from_array(arr: np.ndarray) -> TaskVector`
**Signature:** `@classmethod def from_array(cls, arr: np.ndarray) -> TaskVector`

Create task vector from NumPy array.

**Parameters:**
- `arr: np.ndarray` — 5-element array

**Returns:** `TaskVector` — Reconstructed task vector

**Source:** `src/codex/quantum_orchestrator/orchestrator.py:73`

**Example:**
```python
arr = np.array([0.8, 2.0, 0.5, 0.3, 2])
task = TaskVector.from_array(arr)
```

---

##### `distance_to(other: TaskVector) -> float`
**Signature:** `def distance_to(self, other: TaskVector) -> float`

Calculate Euclidean distance to another vector.

**Parameters:**
- `other: TaskVector` — Target task vector

**Returns:** `float` — Euclidean distance

**Source:** `src/codex/quantum_orchestrator/orchestrator.py:87`

**Example:**
```python
task1 = TaskVector(priority=0.8, complexity=1.0)
task2 = TaskVector(priority=0.5, complexity=2.0)
dist = task1.distance_to(task2)  # Euclidean distance
```

---

#### `DiracSpinor`
**Description:** 4-component Dirac spinor representing task state with quantum properties.

**Components:**
- `psi_1: complex` — Positive energy, spin up (primary progress)
- `psi_2: complex` — Positive energy, spin down (alternative progress)
- `psi_3: complex` — Negative energy, spin up (primary regression)
- `psi_4: complex` — Negative energy, spin down (alternative regression)

**Methods:**

##### `psi_1() -> complex`
**Returns:** First spinor component (positive energy, spin up)

**Source:** `src/codex/quantum_orchestrator/orchestrator.py:115`

---

##### `to_array() -> np.ndarray`
**Signature:** `def to_array(self) -> np.ndarray`

Convert spinor to 4-element complex array.

**Returns:** `np.ndarray` — Complex array of 4 components

**Source:** `src/codex/quantum_orchestrator/orchestrator.py:145`

---

##### `norm() -> float`
**Signature:** `def norm(self) -> float`

Calculate probability density (spinor norm).

**Returns:** `float` — √(sum of |psi_i|² for all components)

**Source:** `src/codex/quantum_orchestrator/orchestrator.py:160`

---

#### `DiracMatrices`
**Description:** Dirac α and β matrices (4×4) for spinor transformations.

**Provides:** Pre-computed Dirac gamma matrices for relativistic quantum mechanics

**Methods:**

##### `alpha_1() -> np.ndarray`
**Returns:** 4×4 Dirac α₁ matrix

---

##### `alpha_2() -> np.ndarray`
**Returns:** 4×4 Dirac α₂ matrix

---

##### `alpha_3() -> np.ndarray`
**Returns:** 4×4 Dirac α₃ matrix

---

##### `beta() -> np.ndarray`
**Returns:** 4×4 Dirac β matrix

---

#### `TaskState`
**Description:** Complete task state combining quantum, classical, and spinor properties.

**Fields:**
- `task_vector: TaskVector` — Classical task position
- `quantum_state: DiracSpinor` — Quantum state
- `energy: float` — Total energy
- `momentum: np.ndarray` — Classical momentum vector
- `timestamp: float` — State timestamp

**Methods:**

##### `total_energy() -> float`
**Signature:** `def total_energy(self) -> float`

Calculate E = √((pc)² + (mc²)²) (relativistic energy-momentum relation)

**Returns:** `float` — Total energy

**Source:** `src/codex/quantum_orchestrator/orchestrator.py:220`

---

##### `probability_density() -> float`
**Signature:** `def probability_density(self) -> float`

Calculate probability density from quantum state.

**Returns:** `float` — |ψ|² (sum of squared amplitudes)

**Source:** `src/codex/quantum_orchestrator/orchestrator.py:235`

---

### Functions

#### `create_orchestrator(max_throughput: float, work_granularity: float) -> QuantumOrchestrator`
**Signature:** `def create_orchestrator(max_throughput: float, work_granularity: float) -> QuantumOrchestrator`

Factory function to create a new QuantumOrchestrator instance.

**Parameters:**
- `max_throughput: float` — Maximum task throughput (relates to c)
- `work_granularity: float` — Work unit size (relates to ℏ)

**Returns:** `QuantumOrchestrator` — Configured orchestrator

**Source:** `src/codex/quantum_orchestrator/orchestrator.py:300`

**Example:**
```python
from codex.quantum_orchestrator import create_orchestrator

# Create orchestrator with physics-inspired parameters
orch = create_orchestrator(max_throughput=100.0, work_granularity=1.0)
```

---

#### `propagate_state(state: TaskState, time_delta: float) -> TaskState`
**Signature:** `def propagate_state(state: TaskState, time_delta: float) -> TaskState`

Propagate task state forward in time using Schrödinger dynamics.

**Parameters:**
- `state: TaskState` — Initial task state
- `time_delta: float` — Time step for propagation

**Returns:** `TaskState` — Updated task state

**Source:** `src/codex/quantum_orchestrator/orchestrator.py:320`

---

#### `resolve_conflicts(states: list[TaskState], constants: PhysicsConstants) -> list[TaskState]`
**Signature:** `def resolve_conflicts(states: list[TaskState], constants: PhysicsConstants) -> list[TaskState]`

Resolve task conflicts using Klein-Gordon relativistic dynamics.

**Parameters:**
- `states: list[TaskState]` — Potentially conflicting task states
- `constants: PhysicsConstants` — Physical constants for simulation

**Returns:** `list[TaskState]` — Non-conflicting task states

**Source:** `src/codex/quantum_orchestrator/orchestrator.py:340`

---

#### `probability_current(state: TaskState) -> np.ndarray`
**Signature:** `def probability_current(state: TaskState) -> np.ndarray`

Calculate probability current 4-vector j^μ = (ρ, j).

**Parameters:**
- `state: TaskState` — Current task state

**Returns:** `np.ndarray` — 4-vector [energy density, j_x, j_y, j_z]

**Source:** `src/codex/quantum_orchestrator/orchestrator.py:360`

---

#### `compute_spin_expectation(spinor: DiracSpinor, axis: str) -> float`
**Signature:** `def compute_spin_expectation(spinor: DiracSpinor, axis: str) -> float`

Compute spin expectation value ⟨S_axis⟩.

**Parameters:**
- `spinor: DiracSpinor` — Quantum state
- `axis: str` — Spin axis ('x', 'y', or 'z')

**Returns:** `float` — Expectation value ⟨σ_axis⟩/2

**Source:** `src/codex/quantum_orchestrator/orchestrator.py:380`

---

#### `apply_pauli_rotation(spinor: DiracSpinor, axis: str, angle: float) -> DiracSpinor`
**Signature:** `def apply_pauli_rotation(spinor: DiracSpinor, axis: str, angle: float) -> DiracSpinor`

Apply Pauli rotation e^(-iσ_axis*angle/2).

**Parameters:**
- `spinor: DiracSpinor` — Input spinor
- `axis: str` — Rotation axis ('x', 'y', 'z')
- `angle: float` — Rotation angle in radians

**Returns:** `DiracSpinor` — Rotated spinor

**Source:** `src/codex/quantum_orchestrator/orchestrator.py:400`

---

## Task State Representation

### Quantum Properties of Tasks

The orchestrator represents each task with quantum properties that enable:

1. **Superposition** — Tasks in multiple states simultaneously
2. **Entanglement** — Task dependencies as quantum correlations
3. **Interference** — Task scheduling optimization via constructive/destructive interference
4. **Quantum Tunneling** — Bypassing resource barriers for high-priority tasks

### Energy-Momentum Relations

Tasks follow relativistic energy-momentum relation:

**E² = (pc)² + (mc²)²**

Where:
- **E** = Total task energy (deadline urgency + resource cost)
- **p** = Task momentum (priority × velocity)
- **c** = Speed of light (maximum throughput capacity)
- **m** = Task mass (complexity × load)

---

## Physics-Inspired Operations

### Schrödinger Dynamics

**iℏ ∂ψ/∂t = Ĥ ψ**

Task states evolve according to quantum mechanical principles, with:
- **ψ** = Task quantum state (DiracSpinor)
- **Ĥ** = Hamiltonian (total energy operator)
- **ℏ** = Work granularity

### Klein-Gordon Relativistic Extension

**□²φ + (m/ℏ)²φ = 0**

Conflicts are resolved using Klein-Gordon equation for relativistic corrections.

### Dirac Spinor Dynamics

4-component spinors capture:
- Positive energy states (forward time propagation)
- Negative energy states (backward time propagation, interpreted as antiparticles)
- Spin degrees of freedom

---

## Quantum Planset Engine

**File:** `src/codex/cognitive/quantum_planset_engine.py`  
**Purpose:** Quantum-inspired planning engine for agent coordination  
**LOC:** 1,379 | **API:** 26 public signatures

### Key Classes

#### `QuantumPlansetEngine`
**Description:** Main planning engine combining quantum mechanics with agent coordination.

**Methods:**

##### `plan(objectives: list[str], constraints: dict) -> Plan`
**Signature:** `def plan(self, objectives: list[str], constraints: dict) -> Plan`

Generate execution plan using quantum superposition and interference.

**Parameters:**
- `objectives: list[str]` — Goal states to achieve
- `constraints: dict` — Execution constraints (time, resources, etc)

**Returns:** `Plan` — Optimized execution plan

**Source:** `src/codex/cognitive/quantum_planset_engine.py:100`

---

##### `simulate(plan: Plan, duration: float) -> SimulationResults`
**Signature:** `def simulate(self, plan: Plan, duration: float) -> SimulationResults`

Simulate plan execution with quantum dynamics.

**Parameters:**
- `plan: Plan` — Execution plan to simulate
- `duration: float` — Simulation time window

**Returns:** `SimulationResults` — Simulation metrics and outcome probabilities

**Source:** `src/codex/cognitive/quantum_planset_engine.py:150`

---

##### `collapse_superposition(state: QuantumState) -> ConcreteState`
**Signature:** `def collapse_superposition(self, state: QuantumState) -> ConcreteState`

Collapse quantum superposition to concrete state.

**Parameters:**
- `state: QuantumState` — Superposed execution state

**Returns:** `ConcreteState` — Selected concrete state

**Source:** `src/codex/cognitive/quantum_planset_engine.py:200`

---

## Function Index

### All 91+ Functions at a Glance

| Function | Module | Purpose | Return Type |
|----------|--------|---------|------------|
| `create_orchestrator()` | quantum_orchestrator | Create orchestrator | `QuantumOrchestrator` |
| `c_squared()` | quantum_orchestrator | c² constant | `float` |
| `hbar_squared()` | quantum_orchestrator | ℏ² constant | `float` |
| `to_array()` | quantum_orchestrator | Convert to array | `np.ndarray` |
| `from_array()` | quantum_orchestrator | Create from array | `TaskVector` |
| `distance_to()` | quantum_orchestrator | Euclidean distance | `float` |
| `psi_1()` | quantum_orchestrator | First component | `complex` |
| `propagate_state()` | quantum_orchestrator | Time evolution | `TaskState` |
| `resolve_conflicts()` | quantum_orchestrator | Conflict resolution | `list[TaskState]` |
| `probability_current()` | quantum_orchestrator | j^μ current | `np.ndarray` |
| `compute_spin_expectation()` | quantum_orchestrator | ⟨S_axis⟩ | `float` |
| `apply_pauli_rotation()` | quantum_orchestrator | Spin rotation | `DiracSpinor` |
| `plan()` | quantum_planset | Generate plan | `Plan` |
| `simulate()` | quantum_planset | Run simulation | `SimulationResults` |
| `collapse_superposition()` | quantum_planset | State collapse | `ConcreteState` |

**Total Documented:** 15/91 (16%)  
**Next Phase:** Document remaining 76+ functions

---

## Examples

### Creating and Configuring Orchestrator

```python
from codex.quantum_orchestrator import create_orchestrator, PhysicsConstants

# Create with custom physics constants
constants = PhysicsConstants(c=150.0, hbar=2.0, default_mass=1.5)
orchestrator = create_orchestrator(max_throughput=150.0, work_granularity=2.0)
```

### Working with Task Vectors

```python
from codex.quantum_orchestrator import TaskVector

# Create task vector
task = TaskVector(
    priority=0.9,
    complexity=2.5,
    resource_demand=1.0,
    time_sensitivity=0.8,
    dependency_depth=3
)

# Convert to array and back
arr = task.to_array()  # [0.9, 2.5, 1.0, 0.8, 3]
restored = TaskVector.from_array(arr)

# Calculate distance to another task
other = TaskVector(priority=0.5, complexity=1.0)
dist = task.distance_to(other)
print(f"Task distance: {dist:.3f}")
```

### Working with Spinors

```python
from codex.quantum_orchestrator import DiracSpinor

# Create spinor state
spinor = DiracSpinor(
    psi_1=1.0 + 0j,
    psi_2=0.0 + 0j,
    psi_3=0.0 + 0j,
    psi_4=0.0 + 0j
)

# Calculate norm (probability density)
norm = spinor.norm()
print(f"Probability density: {norm:.3f}")

# Convert to array
arr = spinor.to_array()
```

### Planning with Quantum Engine

```python
from codex.cognitive.quantum_planset_engine import QuantumPlansetEngine

engine = QuantumPlansetEngine()

# Generate plan for objectives
objectives = [
    "Complete model training",
    "Validate metrics",
    "Deploy to production"
]

constraints = {
    "max_time": 3600.0,  # 1 hour
    "max_resources": 8,  # CPU cores
    "priority": "high"
}

plan = engine.plan(objectives, constraints)

# Simulate execution
results = engine.simulate(plan, duration=3600.0)
print(f"Success probability: {results.success_probability:.3f}")
```

---

## Coverage Status

**Functions Documented:** 15/65 in orchestrator (23%)  
**Functions Documented:** 0/26 in planset engine (0%)  
**Total Signatures:** 15/91 (16%)

**Next Phase:** Complete documentation of remaining 76+ quantum operations

---

**Generated:** 2026-07-08  
**Campaign:** WS1 API Documentation Expansion  
**Phase:** 2 - Master API References

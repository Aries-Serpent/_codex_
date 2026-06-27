"""
Complete Quantum-Relativistic-Dirac Orchestrator Implementation.

This module provides a consolidated implementation of the physics-inspired
orchestration framework, combining:
1. Schrödinger dynamics (iℏ∂ψ/∂t = Ĥψ)
2. Klein-Gordon relativistic extension
3. Probability current & flow analysis
4. Dirac spinor dynamics with 4-component states

The implementation is designed to be production-ready while maintaining
mathematical accuracy to the underlying physics.
"""

import math
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np

# ============================================================================
# SECTION 1: PHYSICAL CONSTANTS
# ============================================================================

# SPEED_LIMIT_FACTOR provides a small safety margin below speed of light
# to avoid numerical instability at c
SPEED_LIMIT_FACTOR = 0.9999


@dataclass
class PhysicsConstants:
    """Physical constants governing the orchestrator."""

    hbar: float = 1.0  # Planck's reduced constant (work granularity)
    c: float = 100.0  # Speed of light (maximum throughput)
    default_mass: float = 1.0  # Default task complexity

    @property
    def c_squared(self) -> float:
        return self.c**2

    @property
    def hbar_squared(self) -> float:
        return self.hbar**2


# ============================================================================
# SECTION 2: TASK STATE REPRESENTATION
# ============================================================================


@dataclass
class TaskVector:
    """Position in 5D task space."""

    priority: float = 0.0
    complexity: float = 1.0
    resource_demand: float = 0.0
    time_sensitivity: float = 0.0
    dependency_depth: int = 0

    def to_array(self) -> np.ndarray:
        return np.array(
            [
                self.priority,
                self.complexity,
                self.resource_demand,
                self.time_sensitivity,
                float(self.dependency_depth),
            ]
        )

    @classmethod
    def from_array(cls, arr: np.ndarray) -> "TaskVector":
        return cls(arr[0], arr[1], arr[2], arr[3], int(arr[4]))

    def __add__(self, other: "TaskVector") -> "TaskVector":
        """Vector addition."""
        if isinstance(other, TaskVector):
            return TaskVector.from_array(self.to_array() + other.to_array())
        return NotImplemented

    def __mul__(self, scalar: float) -> "TaskVector":
        """Scalar multiplication."""
        return TaskVector.from_array(self.to_array() * scalar)

    def distance_to(self, other: "TaskVector") -> float:
        """Euclidean distance to another vector."""
        return np.linalg.norm(self.to_array() - other.to_array())


@dataclass
class DiracSpinor:
    """
    4-component Dirac spinor representing task state.

    Components:
        psi_1: Positive energy, spin up (primary progress)
        psi_2: Positive energy, spin down (alternative progress)
        psi_3: Negative energy, spin up (primary regression)
        psi_4: Negative energy, spin down (alternative regression)
    """

    components: np.ndarray = field(default_factory=lambda: np.array([1.0 + 0j, 0j, 0j, 0j]))

    @property
    def psi_1(self) -> complex:
        return self.components[0]

    @property
    def psi_2(self) -> complex:
        return self.components[1]

    @property
    def psi_3(self) -> complex:
        return self.components[2]

    @property
    def psi_4(self) -> complex:
        return self.components[3]

    @property
    def positive_energy_prob(self) -> float:
        """Probability in positive energy states (progress)."""
        return abs(self.psi_1) ** 2 + abs(self.psi_2) ** 2

    @property
    def negative_energy_prob(self) -> float:
        """Probability in negative energy states (regression)."""
        return abs(self.psi_3) ** 2 + abs(self.psi_4) ** 2

    @property
    def total_probability(self) -> float:
        """Total probability (should be 1.0 when normalized)."""
        return sum(abs(c) ** 2 for c in self.components)

    def normalize(self) -> None:
        """Normalize the spinor to unit probability."""
        norm = np.sqrt(self.total_probability)
        if norm > 1e-10:
            self.components = self.components / norm

    def dagger(self) -> np.ndarray:
        """Hermitian conjugate ψ†."""
        return np.conj(self.components)


class DiracMatrices:
    """
    Dirac α and β matrices (4×4).

    These are the fundamental operators in the Dirac equation:
    iℏ∂ψ/∂t = -iℏα·∇ψ + βmc²ψ
    """

    @staticmethod
    def alpha_x() -> np.ndarray:
        """α₁ matrix (x-direction)."""
        return np.array([[0, 0, 0, 1], [0, 0, 1, 0], [0, 1, 0, 0], [1, 0, 0, 0]], dtype=complex)

    @staticmethod
    def alpha_y() -> np.ndarray:
        """α₂ matrix (y-direction)."""
        return np.array(
            [[0, 0, 0, -1j], [0, 0, 1j, 0], [0, -1j, 0, 0], [1j, 0, 0, 0]],
            dtype=complex,
        )

    @staticmethod
    def alpha_z() -> np.ndarray:
        """α₃ matrix (z-direction)."""
        return np.array([[0, 0, 1, 0], [0, 0, 0, -1], [1, 0, 0, 0], [0, -1, 0, 0]], dtype=complex)

    @staticmethod
    def beta() -> np.ndarray:
        """β matrix (mass coupling)."""
        return np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0], [0, 0, 0, -1]], dtype=complex)

    @classmethod
    def alpha_vector(cls) -> list[np.ndarray]:
        """Vector of α matrices [α₁, α₂, α₃]."""
        return [cls.alpha_x(), cls.alpha_y(), cls.alpha_z()]


@dataclass
class TaskState:
    """
    Complete task state with quantum, classical, and spinor properties.
    """

    task_id: str
    name: str
    position: TaskVector = field(default_factory=TaskVector)
    spinor: DiracSpinor = field(default_factory=DiracSpinor)
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(5))
    rest_mass: float = 1.0
    deadline: Optional[float] = None
    dependencies: list[str] = field(default_factory=list)
    required_resources: dict[str, float] = field(default_factory=dict)

    _constants: PhysicsConstants = field(default_factory=PhysicsConstants, repr=False)

    @property
    def amplitude(self) -> complex:
        """Simple amplitude for compatibility (uses first spinor component)."""
        return self.spinor.psi_1

    @amplitude.setter
    def amplitude(self, value: complex) -> None:
        """set amplitude (modifies first spinor component)."""
        self.spinor.components[0] = value
        self.spinor.normalize()

    @property
    def probability(self) -> float:
        """Total completion probability."""
        return self.spinor.positive_energy_prob

    @property
    def speed(self) -> float:
        """Scalar speed |v|."""
        return np.linalg.norm(self.velocity)

    @property
    def lorentz_factor(self) -> float:
        """γ = 1/√(1 - v²/c²)."""
        v = self.speed
        c = self._constants.c
        if v >= c:
            return float("inf")
        return 1.0 / math.sqrt(1.0 - (v / c) ** 2)

    @property
    def relativistic_mass(self) -> float:
        """m = γm₀."""
        return self.lorentz_factor * self.rest_mass

    @property
    def rest_energy(self) -> float:
        """E₀ = m₀c²."""
        return self.rest_mass * self._constants.c_squared

    @property
    def total_energy(self) -> float:
        """E = γm₀c²."""
        return self.lorentz_factor * self.rest_energy

    def apply_force(self, force: np.ndarray, dt: float) -> None:
        """Apply force with relativistic corrections."""
        gamma = self.lorentz_factor
        m = self.rest_mass
        if m > 0:
            acceleration = force / (gamma * m)
            self.velocity += acceleration * dt
            # Enforce speed limit with safety margin below speed of light
            speed = np.linalg.norm(self.velocity)
            if speed >= self._constants.c:
                self.velocity *= SPEED_LIMIT_FACTOR * self._constants.c / speed

    def update_position(self, dt: float) -> None:
        """Update position based on velocity."""
        new_pos = self.position.to_array() + self.velocity * dt
        self.position = TaskVector.from_array(new_pos)


# ============================================================================
# SECTION 3: QUANTUM OPERATORS
# ============================================================================


class MomentumOperator:
    """Momentum operator p̂ = -iℏ∇."""

    def __init__(self, constants: PhysicsConstants):
        self.hbar = constants.hbar
        self.i = 1j

    def gradient(self, state: "OrchestratorState", task_id: str) -> np.ndarray:
        """Compute ∇ψ at task position."""
        task = state.tasks[task_id]
        task_position = task.position.to_array()
        neighbors = self._get_neighbors(state, task_id)

        if not neighbors:
            return np.zeros(5)

        gradient = np.zeros(5, dtype=complex)  # Use complex dtype
        for _, neighbor in neighbors.items():
            delta_x = neighbor.position.to_array() - task_position
            delta_psi = neighbor.spinor.psi_1 - task.spinor.psi_1
            distance = np.linalg.norm(delta_x)
            if distance > 1e-10:
                gradient += (delta_psi / distance) * (delta_x / distance)

        result = gradient / len(neighbors) if neighbors else np.zeros(5, dtype=complex)
        return np.real(result)  # Return real part for position-space gradient

    def apply(self, state: "OrchestratorState", task_id: str) -> complex:
        """Apply p̂ = -iℏ∇."""
        grad = self.gradient(state, task_id)
        return -self.i * self.hbar * np.linalg.norm(grad)

    def _get_neighbors(
        self, state: "OrchestratorState", task_id: str, radius: float = 2.0
    ) -> dict[str, TaskState]:
        """Get neighboring tasks within radius."""
        task = state.tasks[task_id]
        task_pos = task.position.to_array()
        neighbors = {}
        for other_id, other_task in state.tasks.items():
            if other_id == task_id:
                continue
            distance = np.linalg.norm(other_task.position.to_array() - task_pos)
            if distance <= radius:
                neighbors[other_id] = other_task
        return neighbors


class DiracOperator:
    """
    Dirac operator: Ĥ = -iℏα·∇ + βmc².

    Implements the Dirac equation:
    iℏ∂ψ/∂t = -iℏα·∇ψ + βmc²ψ
    """

    def __init__(self, constants: PhysicsConstants):
        self.constants = constants
        self.hbar = constants.hbar
        self.c = constants.c
        self.matrices = DiracMatrices()
        self.momentum_op = MomentumOperator(constants)

    def apply(self, task: TaskState, gradient: np.ndarray) -> np.ndarray:
        """
        Apply Dirac Hamiltonian to spinor.

        Ĥψ = -iℏα·∇ψ + βmc²ψ

        Args:
            task: Task with spinor state
            gradient: Spatial gradient ∇ψ (5D, use first 3 components)

        Returns:
            Ĥψ (4-component spinor)
        """
        psi = task.spinor.components
        m = task.rest_mass
        c = self.c
        hbar = self.hbar

        # Kinetic term: -iℏα·∇ψ
        alpha_vec = self.matrices.alpha_vector()
        kinetic = np.zeros(4, dtype=complex)
        for i in range(min(3, len(gradient))):  # Use first 3 gradient components
            kinetic += -1j * hbar * alpha_vec[i] @ psi * gradient[i]

        # Mass term: βmc²ψ
        beta = self.matrices.beta()
        mass_term = beta @ psi * m * c * c

        # Total Hamiltonian
        return kinetic + mass_term

    def compute_current(self, task: TaskState) -> np.ndarray:
        """
        Compute Dirac current: j = cψ†αψ.

        This gives the probability current for the task.
        Always subluminal: |j| ≤ c.

        Returns:
            3D current vector
        """
        psi = task.spinor.components
        psi_dagger = task.spinor.dagger()
        alpha_vec = self.matrices.alpha_vector()

        current = np.zeros(3)
        for i in range(3):
            current[i] = self.c * np.real(psi_dagger @ alpha_vec[i] @ psi)

        return current

    def zitterbewegung_amplitude(self, task: TaskState) -> float:
        """
        Compute zitterbewegung amplitude.

        Measures rapid oscillation between positive/negative energy states.
        High amplitude indicates instability.

        Amplitude = 2√(P₊ · P₋)

        Returns:
            Oscillation amplitude (0-1)
        """
        P_plus = task.spinor.positive_energy_prob
        P_minus = task.spinor.negative_energy_prob
        return 2 * math.sqrt(P_plus * P_minus)

    def helicity(self, task: TaskState, state: "OrchestratorState") -> float:
        """
        Compute helicity: h = S·p/|p|.

        Projection of spin onto momentum direction.
        h > 0: Efficient (spin aligned with motion)
        h < 0: Inefficient (spin opposite to motion)

        Returns:
            Helicity value
        """
        # Simplified helicity based on spinor and velocity
        v = task.velocity
        v_mag = np.linalg.norm(v)
        if v_mag < 1e-10:
            return 0.0

        # Spin expectation (difference between up and down components)
        spin_z = abs(task.spinor.psi_1) ** 2 - abs(task.spinor.psi_2) ** 2

        # Project onto velocity direction
        return spin_z * np.sign(v[0]) if len(v) > 0 else 0.0


# ============================================================================
# SECTION 4: POTENTIAL LANDSCAPE
# ============================================================================


class PotentialLandscape:
    """Potential energy V(x,t) defining task constraints."""

    def __init__(self, constants: PhysicsConstants):
        self.constants = constants
        self.sla_weight = 10.0
        self.dependency_weight = 5.0
        self.resource_weight = 3.0

    def evaluate(self, task_id: str, state: "OrchestratorState") -> float:
        """Evaluate potential at task position."""
        task = state.tasks[task_id]
        V = 0.0

        # SLA potential
        if task.deadline is not None:
            time_remaining = task.deadline - state.timestamp
            if time_remaining <= 0:
                V += 1000 * task.rest_energy
            else:
                V += -self.sla_weight * task.rest_energy / time_remaining

        # Dependency barriers
        unmet_deps = sum(1 for dep_id in task.dependencies if not state.is_complete(dep_id))
        V += unmet_deps * self.dependency_weight * task.rest_energy

        # Resource scarcity
        for resource_id, required in task.required_resources.items():
            available = state.resources.get(resource_id, 0)
            if available < required:
                V += self.resource_weight * task.rest_energy * (required - available) / required

        return V

    def gradient(self, task_id: str, state: "OrchestratorState") -> np.ndarray:
        """Compute ∇V via finite differences."""
        epsilon = 0.01
        grad = np.zeros(5)
        base_V = self.evaluate(task_id, state)

        for dim in range(5):
            # Perturb position
            state_copy = state.copy()
            pos_array = state_copy.tasks[task_id].position.to_array()
            pos_array[dim] += epsilon
            state_copy.tasks[task_id].position = TaskVector.from_array(pos_array)

            V_plus = self.evaluate(task_id, state_copy)
            grad[dim] = (V_plus - base_V) / epsilon

        return grad


# ============================================================================
# SECTION 5: PROBABILITY CURRENT & FLOW ANALYSIS
# ============================================================================


class ProbabilityCurrentOperator:
    """Probability current: j = (iℏ/2mc²)(ψ*∂ψ/∂t - ψ∂ψ*/∂t)."""

    def __init__(self, constants: PhysicsConstants):
        self.constants = constants
        self.hbar = constants.hbar
        self.c = constants.c

    def task_current(
        self,
        current_state: "OrchestratorState",
        previous_state: "OrchestratorState",
        task_id: str,
        dt: float,
    ) -> float:
        """Compute probability current for a task."""
        if task_id not in current_state.tasks or task_id not in previous_state.tasks:
            return 0.0

        task = current_state.tasks[task_id]
        prev_task = previous_state.tasks[task_id]

        psi = task.spinor.psi_1
        psi_prev = prev_task.spinor.psi_1
        psi_star = np.conj(psi)
        psi_star_prev = np.conj(psi_prev)

        dpsi_dt = (psi - psi_prev) / dt
        dpsi_star_dt = (psi_star - psi_star_prev) / dt

        prefactor = 1j * self.hbar / (2 * task.rest_mass * self.c**2)
        current = prefactor * (psi_star * dpsi_dt - psi * dpsi_star_dt)

        return float(np.real(current))


class FlowAnalyzer:
    """Analyze probability flow and detect bottlenecks."""

    def __init__(self, constants: PhysicsConstants):
        self.constants = constants
        self.current_op = ProbabilityCurrentOperator(constants)

    def identify_bottlenecks(
        self,
        current_state: "OrchestratorState",
        previous_state: "OrchestratorState",
        dt: float,
        threshold: float = 0.01,
    ) -> list[dict[str, Any]]:
        """Identify tasks where probability accumulates but doesn't flow."""
        bottlenecks = []

        for task_id, task in current_state.tasks.items():
            if task_id not in previous_state.tasks:
                continue

            prob = task.probability
            prev_prob = previous_state.tasks[task_id].probability
            current = self.current_op.task_current(current_state, previous_state, task_id, dt)

            is_high_prob = prob > 0.3
            is_low_current = abs(current) < threshold
            is_accumulating = prob > prev_prob

            if is_high_prob and is_low_current and is_accumulating:
                bottlenecks.append(
                    {
                        "task_id": task_id,
                        "probability": prob,
                        "current": current,
                        "severity": prob / max(abs(current), 0.001),
                    }
                )

        bottlenecks.sort(key=lambda x: x["severity"], reverse=True)  # type: ignore[arg-type,return-value]
        return bottlenecks


# ============================================================================
# SECTION 6: ORCHESTRATOR STATE
# ============================================================================


@dataclass
class OrchestratorState:
    """Complete state of the orchestrator system."""

    tasks: dict[str, TaskState] = field(default_factory=dict)
    resources: dict[str, float] = field(default_factory=dict)
    timestamp: float = 0.0
    coherence: float = 1.0
    constants: PhysicsConstants = field(default_factory=PhysicsConstants, repr=False)
    _previous_state: Optional["OrchestratorState"] = field(default=None, repr=False)

    def copy(self) -> "OrchestratorState":
        """Deep copy of state."""
        import copy

        return copy.deepcopy(self)

    def normalize(self) -> None:
        """Normalize all task spinors."""
        for task in self.tasks.values():
            task.spinor.normalize()

    def is_complete(self, task_id: str) -> bool:
        """Check if task is complete."""
        if task_id not in self.tasks:
            return True
        return self.tasks[task_id].probability < 0.01

    def total_probability(self) -> float:
        """Total probability across all tasks."""
        return sum(task.probability for task in self.tasks.values())


# ============================================================================
# SECTION 7: COMPLETE ORCHESTRATOR
# ============================================================================


class QuantumRelativisticDiracOrchestrator:
    """
    Complete Quantum-Relativistic-Dirac Orchestrator.

    Implements:
    - Schrödinger dynamics
    - Klein-Gordon relativistic extension
    - Probability current analysis
    - Dirac spinor evolution with 4-component states
    """

    def __init__(
        self,
        max_throughput: float = 100.0,
        granularity: float = 1.0,
        dt: float = 0.1,
        coherence_threshold: float = 0.7,
    ):
        self.constants = PhysicsConstants(hbar=granularity, c=max_throughput)
        self.dt = dt
        self.coherence_threshold = coherence_threshold

        # Operators
        self.dirac = DiracOperator(self.constants)
        self.momentum_op = MomentumOperator(self.constants)
        self.potential = PotentialLandscape(self.constants)
        self.current_op = ProbabilityCurrentOperator(self.constants)
        self.flow_analyzer = FlowAnalyzer(self.constants)

        # State
        self.state = OrchestratorState(constants=self.constants)
        self.history: list[OrchestratorState] = []

    def add_task(self, task_id: str, name: str, **kwargs) -> None:
        """
        Add a new task to the orchestrator.

        Args:
            task_id: Unique identifier for the task
            name: Human-readable task name
            **kwargs: Additional task properties including:
                priority: float (0-1)
                complexity: float
                resource_demand: float (0-1)
                time_sensitivity: float (0-1)
                dependency_depth: int
                rest_mass: float
                deadline: Optional[float]
                dependencies: list[str]
                required_resources: dict[str, float]
        """
        # Extract position-related kwargs for TaskVector
        position_kwargs = {
            "priority": kwargs.pop("priority", 0.0),
            "complexity": kwargs.pop("complexity", 1.0),
            "resource_demand": kwargs.pop("resource_demand", 0.0),
            "time_sensitivity": kwargs.pop("time_sensitivity", 0.0),
            "dependency_depth": kwargs.pop("dependency_depth", 0),
        }

        position = TaskVector(**position_kwargs)

        task = TaskState(
            task_id=task_id,
            name=name,
            position=position,
            _constants=self.constants,
            **kwargs,
        )
        self.state.tasks[task_id] = task

    def evolve(self) -> None:
        """Single evolution step using Dirac dynamics."""
        # Store history
        self.history.append(self.state.copy())
        self.state._previous_state = self.history[-1]

        # Evolve each task
        for task_id, task in self.state.tasks.items():
            # Compute gradient
            gradient = self.momentum_op.gradient(self.state, task_id)

            # Apply Dirac Hamiltonian to spinor
            H_psi = self.dirac.apply(task, gradient)

            # Evolve spinor: ψ(t+dt) = ψ(t) - (i/ℏ)Ĥψ·dt
            task.spinor.components = (
                task.spinor.components - (1j / self.constants.hbar) * H_psi * self.dt
            )

            # Evolve classical position
            task.update_position(self.dt)

            # Apply force from potential
            force = -self.potential.gradient(task_id, self.state)
            task.apply_force(force, self.dt)

        # Normalize
        self.state.normalize()

        # Update timestamp
        self.state.timestamp += self.dt

    def check_stability(self) -> list[str]:
        """Check for unstable tasks (high zitterbewegung)."""
        unstable = []
        for task_id, task in self.state.tasks.items():
            amplitude = self.dirac.zitterbewegung_amplitude(task)
            if amplitude > 0.5:
                unstable.append(task_id)
        return unstable

    def stabilize_task(self, task_id: str) -> None:
        """Stabilize a task with high zitterbewegung."""
        task = self.state.tasks[task_id]
        # Project onto positive energy states
        P_plus = task.spinor.positive_energy_prob
        P_minus = task.spinor.negative_energy_prob

        if P_plus > P_minus:
            # Suppress negative energy components
            task.spinor.components[2] *= 0.5
            task.spinor.components[3] *= 0.5
        else:
            # Suppress positive energy components (allow regression)
            task.spinor.components[0] *= 0.5
            task.spinor.components[1] *= 0.5

        task.spinor.normalize()

    def self_heal(self) -> None:
        """Self-healing with stability checks."""
        # Check for unstable tasks
        unstable_tasks = self.check_stability()
        for task_id in unstable_tasks:
            self.stabilize_task(task_id)

        # Check for bottlenecks
        if len(self.history) >= 1:
            bottlenecks = self.flow_analyzer.identify_bottlenecks(
                self.state, self.history[-1], self.dt
            )
            for bottleneck in bottlenecks[:3]:
                # Boost priority
                task = self.state.tasks[bottleneck["task_id"]]
                task.position.priority *= 1.2
                # Boost positive energy components
                task.spinor.components[0] *= 1.1
                task.spinor.components[1] *= 1.1

        # Renormalize
        self.state.normalize()

    def measure(self, task_id: str) -> dict[str, Any]:
        """Collapse wave function (execute task)."""
        task = self.state.tasks[task_id]
        probability = task.probability
        outcome = np.random.random() < probability

        if outcome:
            task.spinor.components = np.array([0j, 0j, 0j, 0j])
            return {"status": "completed", "task_id": task_id}
        return {"status": "pending", "task_id": task_id}

    def run(self, max_iterations: int = 1000) -> dict[str, Any]:
        """
        Main orchestration loop.

        Returns:
            Summary statistics
        """
        iteration = 0
        completed_tasks = []

        for iteration in range(max_iterations):
            # Evolve
            self.evolve()

            # Self-heal if needed
            if iteration % 10 == 0:
                self.self_heal()

            # Measure ready tasks
            for task_id in list(self.state.tasks.keys()):
                task = self.state.tasks[task_id]
                if task.probability > 0.9:
                    result = self.measure(task_id)
                    if result["status"] == "completed":
                        completed_tasks.append(task_id)

            # Check convergence
            if all(self.state.is_complete(tid) for tid in self.state.tasks):
                break

        return {
            "iterations": iteration + 1,
            "completed_tasks": completed_tasks,
            "final_timestamp": self.state.timestamp,
            "total_tasks": len(self.state.tasks),
            "completion_rate": (
                len(completed_tasks) / len(self.state.tasks) if self.state.tasks else 0.0
            ),
        }

    def get_task_status(self) -> dict[str, dict[str, Any]]:
        """Get status of all tasks."""
        status = {}
        for task_id, task in self.state.tasks.items():
            current = self.dirac.compute_current(task)
            helicity = self.dirac.helicity(task, self.state)
            zitter = self.dirac.zitterbewegung_amplitude(task)

            status[task_id] = {
                "probability": task.probability,
                "position": task.position.to_array().tolist(),
                "velocity": task.velocity.tolist(),
                "energy": task.total_energy,
                "current": current.tolist(),
                "helicity": helicity,
                "zitterbewegung": zitter,
                "stable": zitter < 0.5,
            }
        return status

    def verify_conservation(self) -> dict[str, Any]:
        """
        Verify continuity equation: ∂ρ/∂t + ∇·j = 0.

        Returns probability conservation status.

        Returns:
            Dictionary with conservation check results:
                is_conserved: bool
                violation: float (magnitude of violation)
                P_current: float (current total probability)
                P_previous: float (previous total probability)
                dP_dt: float (rate of probability change)
        """
        if not self.history:
            return {
                "is_conserved": True,
                "violation": 0.0,
                "P_current": self.state.total_probability(),
                "P_previous": self.state.total_probability(),
                "dP_dt": 0.0,
            }

        prev_state = self.history[-1]
        dt = self.dt

        # Total probability change
        P_current = self.state.total_probability()
        P_previous = prev_state.total_probability()
        dP_dt = (P_current - P_previous) / dt

        # Total current (simplified - sum of all task currents)
        total_current = 0.0
        for task_id in self.state.tasks:
            if task_id in prev_state.tasks:
                current = self.current_op.task_current(self.state, prev_state, task_id, dt)
                total_current += current

        # Continuity violation: should be ~0
        violation = abs(dP_dt + total_current)
        is_conserved = violation < 0.01

        return {
            "is_conserved": is_conserved,
            "violation": violation,
            "P_current": P_current,
            "P_previous": P_previous,
            "dP_dt": dP_dt,
            "total_current": total_current,
        }


# ============================================================================
# SECTION 8: CONVENIENCE INTERFACE
# ============================================================================


def create_orchestrator(
    max_throughput: float = 100.0, work_granularity: float = 1.0, time_step: float = 0.1
) -> QuantumRelativisticDiracOrchestrator:
    """
    Create a quantum orchestrator with default settings.

    Args:
        max_throughput: Maximum system throughput (c)
        work_granularity: Minimum work unit (ℏ)
        time_step: Evolution time step

    Returns:
        Configured orchestrator instance
    """
    return QuantumRelativisticDiracOrchestrator(
        max_throughput=max_throughput, granularity=work_granularity, dt=time_step
    )

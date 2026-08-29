"""
Feynman Path Integral for Orchestration Optimization.

Implements path integral formulation for finding optimal task execution paths.
"""

import copy
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np

from ..orchestrator import (
    OrchestratorState,
    PhysicsConstants,
    QuantumRelativisticDiracOrchestrator,
)


@dataclass
class ExecutionPath:
    """A single execution path through orchestrator state space."""

    states: list[OrchestratorState] = field(default_factory=list)
    action: float = 0.0
    phase: complex = 1.0 + 0j
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def amplitude(self) -> complex:
        """e^{iS/ℏ} — quantum amplitude from action."""
        hbar = 1.0
        return np.exp(1j * self.action / hbar) * self.phase

    @property
    def probability(self) -> float:
        """|amplitude|² — contribution to final probability."""
        return float(np.abs(self.amplitude) ** 2)

    @property
    def length(self) -> int:
        """Number of states in path."""
        return len(self.states)

    @property
    def duration(self) -> float:
        """Total time duration of path."""
        if len(self.states) < 2:
            return 0.0
        return self.states[-1].timestamp - self.states[0].timestamp

    def to_dict(self) -> dict[str, Any]:
        """Serialize path for logging/API."""
        return {
            "length": self.length,
            "action": self.action,
            "amplitude": abs(self.amplitude),
            "probability": self.probability,
            "duration": self.duration,
            "metadata": self.metadata,
        }


class ActionFunctional:
    """Computes the action S = ∫L dt for execution paths."""

    def __init__(self, constants: PhysicsConstants):
        self.constants = constants
        self.kinetic_weight = 1.0
        self.priority_weight = 1.0
        self.deadline_weight = 10.0
        self.dependency_weight = 5.0

    def lagrangian(
        self,
        state: OrchestratorState,
        prev_state: Optional[OrchestratorState] = None,
        dt: float = 0.1,
    ) -> float:
        """Compute Lagrangian L = T - V at a state."""
        T = 0.0
        V = 0.0

        for _, task in state.tasks.items():
            # Kinetic energy
            v_squared = np.sum(task.velocity**2)
            T += 0.5 * task.rest_mass * v_squared * self.kinetic_weight

            # Priority potential
            V += (1.0 - task.position.priority) * task.rest_mass * self.priority_weight

            # Deadline potential
            if hasattr(task, "deadline") and task.deadline is not None:
                time_remaining = task.deadline - state.timestamp
                if time_remaining <= 0:
                    V += 1000 * task.rest_mass * self.deadline_weight
                elif time_remaining < 1.0:
                    V += task.rest_mass * self.deadline_weight / time_remaining

            # Dependency potential
            if hasattr(task, "dependencies"):
                unmet_deps = sum(
                    1
                    for dep in task.dependencies
                    if dep in state.tasks and state.tasks[dep].probability > 0.01
                )
                V += unmet_deps * task.rest_mass * self.dependency_weight

        return T - V

    def compute_action(self, path: ExecutionPath, dt: float = 0.1) -> float:
        """Compute action S = ∫L dt for entire path."""
        if len(path.states) < 2:
            return 0.0

        action = 0.0
        for i in range(1, len(path.states)):
            L = self.lagrangian(path.states[i], path.states[i - 1], dt)
            action += L * dt

        return action


class PathSampler:
    """Sample possible execution paths through state space."""

    def __init__(
        self,
        orchestrator: QuantumRelativisticDiracOrchestrator,
        n_paths: int = 100,
    ):
        self.orchestrator = orchestrator
        self.n_paths = n_paths
        self._rng = np.random.default_rng()

    def sample_paths(
        self,
        initial_state: OrchestratorState,
        n_steps: int,
        perturbation_scale: float = 0.1,
    ) -> list[ExecutionPath]:
        """Sample multiple paths from initial state."""
        paths = []

        for path_idx in range(self.n_paths):
            path = self._sample_single_path(
                initial_state,
                n_steps,
                perturbation_scale,
                seed=path_idx,
            )
            path.metadata["path_index"] = path_idx
            paths.append(path)

        return paths

    def _sample_single_path(
        self,
        initial_state: OrchestratorState,
        n_steps: int,
        perturbation_scale: float,
        seed: int = 0,
    ) -> ExecutionPath:
        """Sample a single perturbed path."""
        path = ExecutionPath()
        current_state = copy.deepcopy(initial_state)
        path.states.append(copy.deepcopy(current_state))

        temp_orch = copy.deepcopy(self.orchestrator)
        temp_orch.state = current_state
        temp_orch.history = []

        rng = np.random.default_rng(seed)

        for _ in range(n_steps):
            for task in temp_orch.state.tasks.values():
                perturbation = rng.normal(0, perturbation_scale, size=5)
                task.velocity = task.velocity + perturbation

                speed = np.linalg.norm(task.velocity)
                if speed >= temp_orch.constants.c:
                    task.velocity *= 0.9 * temp_orch.constants.c / speed

            temp_orch.evolve()
            path.states.append(copy.deepcopy(temp_orch.state))

        return path


# Base perturbation scale applied to path sampling.  Multiplied by temperature so
# higher T explores state space more broadly; at T=1.0 behaviour is unchanged.
_BASE_PERTURBATION_SCALE: float = 0.1


class PathIntegralOptimizer:
    """Find optimal execution path using path integral formulation."""

    def __init__(
        self,
        orchestrator: QuantumRelativisticDiracOrchestrator,
        n_paths: int = 100,
        temperature: float = 1.0,
    ):
        self.orchestrator = orchestrator
        self.constants = orchestrator.constants
        self.n_paths = n_paths
        self.temperature = temperature

        self.action_functional = ActionFunctional(self.constants)
        self.sampler = PathSampler(orchestrator, n_paths)

        self.optimizations_run = 0
        self.total_paths_evaluated = 0
        self.best_action_history: list[float] = []
        self._on_path_found: list[Callable[[ExecutionPath], None]] = []

    def find_optimal_path(
        self,
        initial_state: OrchestratorState,
        n_steps: int = 50,
        dt: float = 0.1,
        temperature: Optional[float] = None,
    ) -> ExecutionPath:
        """Find the path of least action.

        Args:
            initial_state: Starting orchestrator state.
            n_steps: Number of simulation steps per path.
            dt: Time step size for action computation.
            temperature: Annealing temperature controlling path perturbation scale.
                Higher values explore more; lower values exploit known-good regions.
                Defaults to the value set at construction time.
        """
        t = temperature if temperature is not None else self.temperature
        # Temperature controls the perturbation scale of path sampling.
        # Scale defaults to 0.1; multiply by temperature so higher T = more exploration.
        perturbation_scale = _BASE_PERTURBATION_SCALE * t
        paths = self.sampler.sample_paths(
            initial_state, n_steps, perturbation_scale=perturbation_scale
        )

        for path in paths:
            path.action = self.action_functional.compute_action(path, dt)

        best_path = min(paths, key=lambda p: p.action)
        best_path.metadata["optimization_type"] = "minimum_action"

        self.optimizations_run += 1
        self.total_paths_evaluated += len(paths)
        self.best_action_history.append(best_path.action)

        for hook in self._on_path_found:
            hook(best_path)

        return best_path

    def compute_propagator(
        self,
        initial_state: OrchestratorState,
        n_steps: int = 50,
        dt: float = 0.1,
    ) -> complex:
        """Compute quantum propagator K = Σ_paths e^{iS/ℏ}."""
        paths = self.sampler.sample_paths(initial_state, n_steps)

        total_amplitude = 0j
        for path in paths:
            path.action = self.action_functional.compute_action(path, dt)
            total_amplitude += path.amplitude

        return total_amplitude / self.n_paths

    def path_distribution(
        self,
        initial_state: OrchestratorState,
        n_steps: int = 50,
        dt: float = 0.1,
    ) -> dict[str, Any]:
        """Get distribution of path actions and probabilities."""
        paths = self.sampler.sample_paths(initial_state, n_steps)

        actions = []
        for path in paths:
            path.action = self.action_functional.compute_action(path, dt)
            actions.append(path.action)

        actions = np.array(actions)

        return {
            "mean_action": float(np.mean(actions)),
            "std_action": float(np.std(actions)),
            "min_action": float(np.min(actions)),
            "max_action": float(np.max(actions)),
            "n_paths": len(paths),
        }

    def on_path_found(self, callback: Callable[[ExecutionPath], None]) -> None:
        """Register callback for when optimal path is found."""
        self._on_path_found.append(callback)

    def get_metrics(self) -> dict[str, Any]:
        """Get optimization metrics."""
        return {
            "optimizations_run": self.optimizations_run,
            "total_paths_evaluated": self.total_paths_evaluated,
            "best_actions": self.best_action_history[-10:] if self.best_action_history else [],
        }


class QuantumAnnealingScheduler:
    """Quantum annealing for schedule optimization."""

    def __init__(
        self,
        orchestrator: QuantumRelativisticDiracOrchestrator,
        n_paths: int = 50,
    ):
        self.orchestrator = orchestrator
        self.action_functional = ActionFunctional(orchestrator.constants)
        self.sampler = PathSampler(orchestrator, n_paths)

        self.initial_temperature = 1.0
        self.final_temperature = 0.01
        self.cooling_rate = 0.95

        self.annealing_history: list[dict[str, Any]] = []

    def anneal_step(
        self,
        state: OrchestratorState,
        temperature: float,
        n_steps: int = 10,
    ) -> OrchestratorState:
        """Single annealing step at given temperature."""
        perturbation = temperature * 0.5
        paths = self.sampler.sample_paths(state, n_steps, perturbation)

        for path in paths:
            path.action = self.action_functional.compute_action(path, self.orchestrator.dt)

        actions = np.array([p.action for p in paths])

        if temperature > 0:
            weights = np.exp(-actions / temperature)
            weights = weights / np.sum(weights)
        else:
            weights = np.zeros(len(paths))
            weights[np.argmin(actions)] = 1.0

        selected_idx = np.random.choice(len(paths), p=weights)
        selected_path = paths[selected_idx]

        return selected_path.states[-1] if selected_path.states else state

    def optimize_schedule(
        self,
        initial_state: OrchestratorState,
        n_iterations: int = 100,
        initial_temperature: Optional[float] = None,
        final_temperature: Optional[float] = None,
    ) -> tuple[OrchestratorState, list[float]]:
        """Optimize task schedule via quantum annealing."""
        T_initial = initial_temperature or self.initial_temperature
        T_final = final_temperature or self.final_temperature

        state = copy.deepcopy(initial_state)
        action_history = []

        for i in range(n_iterations):
            progress = i / max(n_iterations - 1, 1)
            temperature = T_initial * np.exp(-progress * np.log(T_initial / T_final))

            state = self.anneal_step(state, temperature)

            action = self.action_functional.lagrangian(state)
            action_history.append(action)

            self.annealing_history.append(
                {
                    "iteration": i,
                    "temperature": temperature,
                    "action": action,
                }
            )

        return state, action_history

    def get_annealing_curve(self) -> list[dict[str, Any]]:
        """Get annealing progress curve."""
        return self.annealing_history


class AdaptivePathOptimizer:
    """Adaptive optimizer that adjusts sampling based on landscape."""

    def __init__(
        self,
        orchestrator: QuantumRelativisticDiracOrchestrator,
        n_paths: int = 100,
    ):
        self.base_optimizer = PathIntegralOptimizer(orchestrator, n_paths)
        self.orchestrator = orchestrator

        self.perturbation_scale = 0.1
        self.convergence_threshold = 0.001
        self.stagnation_patience = 10

        self.best_action_ever = float("inf")
        self.stagnation_count = 0

    def optimize_adaptive(
        self,
        initial_state: OrchestratorState,
        n_steps: int = 50,
        max_rounds: int = 10,
    ) -> ExecutionPath:
        """Adaptive optimization with automatic tuning."""
        best_path = None
        previous_best_action = float("inf")

        for round_idx in range(max_rounds):
            self.base_optimizer.sampler.n_paths = max(20, 100 - round_idx * 10)

            paths = self.base_optimizer.sampler.sample_paths(
                initial_state, n_steps, self.perturbation_scale
            )

            for path in paths:
                path.action = self.base_optimizer.action_functional.compute_action(
                    path, self.orchestrator.dt
                )

            current_best = min(paths, key=lambda p: p.action)

            if best_path is None or current_best.action < best_path.action:
                best_path = current_best
                self.stagnation_count = 0
            else:
                self.stagnation_count += 1

            improvement = previous_best_action - current_best.action
            if abs(improvement) < self.convergence_threshold:
                break

            if self.stagnation_count > self.stagnation_patience // 2:
                self.perturbation_scale *= 1.5
            elif improvement > 0:
                self.perturbation_scale *= 0.9

            previous_best_action = current_best.action

            if self.stagnation_count >= self.stagnation_patience:
                self.perturbation_scale = 0.2
                self.stagnation_count = 0

        if best_path:
            best_path.metadata["optimization_type"] = "adaptive"
            best_path.metadata["rounds"] = round_idx + 1

        return best_path  # type: ignore[return-value]


def compare_paths(path_a: ExecutionPath, path_b: ExecutionPath) -> dict[str, Any]:
    """Compare two execution paths."""
    return {
        "action_diff": path_a.action - path_b.action,
        "length_diff": path_a.length - path_b.length,
        "duration_diff": path_a.duration - path_b.duration,
        "better_path": "a" if path_a.action < path_b.action else "b",
        "action_ratio": path_a.action / path_b.action if path_b.action != 0 else float("inf"),
    }


def visualize_action_landscape(
    optimizer: PathIntegralOptimizer,
    initial_state: OrchestratorState,
    n_samples: int = 100,
) -> dict[str, Any]:
    """Sample the action landscape for visualization."""
    paths = optimizer.sampler.sample_paths(initial_state, n_steps=20)

    actions = []
    for path in paths[:n_samples]:
        path.action = optimizer.action_functional.compute_action(path, 0.1)
        actions.append(path.action)

    actions = np.array(actions)
    hist, bin_edges = np.histogram(actions, bins=20)

    return {
        "actions": actions.tolist(),
        "histogram": hist.tolist(),
        "bin_edges": bin_edges.tolist(),
        "statistics": {
            "mean": float(np.mean(actions)),
            "std": float(np.std(actions)),
            "min": float(np.min(actions)),
            "max": float(np.max(actions)),
            "median": float(np.median(actions)),
        },
    }

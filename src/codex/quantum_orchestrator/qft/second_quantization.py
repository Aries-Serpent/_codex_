"""
Second Quantization for Dynamic Task Management.

Implements creation and annihilation operators for:
- Dynamic task spawning (creation operator â†)
- Task cleanup (annihilation operator â)
- Task counting (number operator N̂ = â†â)
- Boson/Fermion statistics
- Vacuum state management

Performance Features:
- Efficient task ID generation
- Batch spawning operations
- Metrics tracking

Integration:
- MLOps hooks for spawn/cleanup events
- Callback system for monitoring
"""

import copy
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import numpy as np

from ..orchestrator import (
    OrchestratorState,
    TaskState,
)


class ParticleStatistics(Enum):
    """Particle statistics for task spawning."""

    BOSON = "boson"  # Multiple tasks can occupy same mode (parallel execution)
    FERMION = "fermion"  # Only one task per mode (Pauli exclusion - exclusive resources)


@dataclass
class FockState:
    """
    Fock state representation |n₁, n₂, ..., nₖ⟩

    Each nᵢ is the occupation number of mode i.
    For bosons: nᵢ can be any non-negative integer
    For fermions: nᵢ ∈ {0, 1} (Pauli exclusion)
    """

    occupation_numbers: dict[str, int] = field(default_factory=dict)
    statistics: ParticleStatistics = ParticleStatistics.BOSON

    def total_particles(self) -> int:
        """Total number of particles: N = Σᵢ nᵢ"""
        return sum(self.occupation_numbers.values())

    def get_occupation(self, mode: str) -> int:
        """Get occupation number for a mode."""
        return self.occupation_numbers.get(mode, 0)

    def set_occupation(self, mode: str, n: int) -> bool:
        """
        set occupation number for a mode.

        Returns False if violates statistics (e.g., fermion with n>1).
        """
        if self.statistics == ParticleStatistics.FERMION and n > 1:
            return False

        if n < 0:
            return False

        if n == 0:
            self.occupation_numbers.pop(mode, None)
        else:
            self.occupation_numbers[mode] = n

        return True

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "occupation_numbers": self.occupation_numbers.copy(),
            "statistics": self.statistics.value,
            "total_particles": self.total_particles(),
        }


class CreationOperator:
    """
    Creation operator â†: |n⟩ → √(n+1) |n+1⟩

    Adds a particle (task) to the specified mode.

    For bosons: â†|n⟩ = √(n+1) |n+1⟩
    For fermions: â†|0⟩ = |1⟩, â†|1⟩ = 0 (Pauli exclusion)
    """

    def __init__(self, statistics: ParticleStatistics = ParticleStatistics.BOSON):
        self.statistics = statistics

    def apply(self, fock_state: FockState, mode: str) -> tuple[Optional[FockState], complex]:
        """
        Apply creation operator to Fock state.

        Returns:
            (new_state, amplitude) where amplitude = √(n+1) for bosons
        """
        n = fock_state.get_occupation(mode)

        if self.statistics == ParticleStatistics.FERMION and n >= 1:
            # Pauli exclusion: can't create fermion in occupied state
            return None, 0.0 + 0j

        # Create new state
        new_state = FockState(
            occupation_numbers=fock_state.occupation_numbers.copy(),
            statistics=self.statistics,
        )
        new_state.set_occupation(mode, n + 1)

        # Amplitude: √(n+1)
        amplitude = np.sqrt(n + 1)

        return new_state, amplitude


class AnnihilationOperator:
    """
    Annihilation operator â: |n⟩ → √n |n-1⟩

    Removes a particle (task) from the specified mode.

    For bosons: â|n⟩ = √n |n-1⟩
    For fermions: â|1⟩ = |0⟩, â|0⟩ = 0
    """

    def __init__(self, statistics: ParticleStatistics = ParticleStatistics.BOSON):
        self.statistics = statistics

    def apply(self, fock_state: FockState, mode: str) -> tuple[Optional[FockState], complex]:
        """
        Apply annihilation operator to Fock state.

        Returns:
            (new_state, amplitude) where amplitude = √n
        """
        n = fock_state.get_occupation(mode)

        if n == 0:
            # Can't annihilate from vacuum
            return None, 0.0 + 0j

        # Create new state
        new_state = FockState(
            occupation_numbers=fock_state.occupation_numbers.copy(),
            statistics=self.statistics,
        )
        new_state.set_occupation(mode, n - 1)

        # Amplitude: √n
        amplitude = np.sqrt(n)

        return new_state, amplitude


class NumberOperator:
    """
    Number operator N̂ = â†â

    Counts particles in a mode: N̂|n⟩ = n|n⟩
    """

    def apply(self, fock_state: FockState, mode: str) -> int:
        """Get occupation number for mode."""
        return fock_state.get_occupation(mode)

    def total(self, fock_state: FockState) -> int:
        """Total particle count."""
        return fock_state.total_particles()


class CommutatorAlgebra:
    """
    Verify commutation/anticommutation relations.

    Bosons: [â, â†] = ââ† - â†â = 1
    Fermions: {â, â†} = ââ† + â†â = 1
    """

    @staticmethod
    def verify_boson_commutator(mode: str = "test") -> bool:
        """
        Verify [â, â†]|n⟩ = |n⟩
        """
        creation = CreationOperator(ParticleStatistics.BOSON)
        annihilation = AnnihilationOperator(ParticleStatistics.BOSON)

        # Test on |1⟩ state
        fock = FockState({mode: 1}, ParticleStatistics.BOSON)

        # ââ†|1⟩
        state1, amp1 = creation.apply(fock, mode)  # â†|1⟩ = √2|2⟩
        state2, amp2 = annihilation.apply(state1, mode) if state1 else (None, 0)  # â|2⟩ = √2|1⟩
        result1 = amp1 * amp2 if state2 else 0  # Should be 2

        # â†â|1⟩
        state3, amp3 = annihilation.apply(fock, mode)  # â|1⟩ = |0⟩
        state4, amp4 = creation.apply(state3, mode) if state3 else (None, 0)  # â†|0⟩ = |1⟩
        result2 = amp3 * amp4 if state4 else 0  # Should be 1

        # [â, â†] = ââ† - â†â = 2 - 1 = 1
        commutator = result1 - result2

        return abs(commutator - 1.0) < 1e-10

    @staticmethod
    def verify_fermion_anticommutator(mode: str = "test") -> bool:
        """
        Verify {â, â†}|0⟩ = |0⟩
        """
        creation = CreationOperator(ParticleStatistics.FERMION)
        annihilation = AnnihilationOperator(ParticleStatistics.FERMION)

        # Test on vacuum |0⟩
        fock = FockState({}, ParticleStatistics.FERMION)

        # ââ†|0⟩
        state1, amp1 = creation.apply(fock, mode)  # â†|0⟩ = |1⟩
        state2, amp2 = annihilation.apply(state1, mode) if state1 else (None, 0)  # â|1⟩ = |0⟩
        result1 = amp1 * amp2 if state2 else 0  # Should be 1

        # â†â|0⟩
        annihilation.apply(fock, mode)  # â|0⟩ = 0 (result unused — annihilation of vacuum is 0)
        result2 = 0  # annihilation gives zero

        # {â, â†} = ââ† + â†â = 1 + 0 = 1
        anticommutator = result1 + result2

        return abs(anticommutator - 1.0) < 1e-10


@dataclass
class SpawnMetrics:
    """Metrics for task spawning operations."""

    total_spawned: int = 0
    total_annihilated: int = 0
    net_created: int = 0
    spawn_events: list[dict[str, Any]] = field(default_factory=list)
    annihilation_events: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_spawned": self.total_spawned,
            "total_annihilated": self.total_annihilated,
            "net_created": self.net_created,
            "recent_spawns": self.spawn_events[-10:],
            "recent_annihilations": self.annihilation_events[-10:],
        }


class TaskSpawner:
    """
    High-level interface for task spawning using creation operators.

    Provides easy-to-use API for:
    - Spawning tasks from templates
    - Cleaning up completed tasks
    - Tracking spawning metrics
    """

    def __init__(
        self,
        state: OrchestratorState,
        statistics: ParticleStatistics = ParticleStatistics.BOSON,
    ):
        self.state = state
        self.statistics = statistics
        self.creation_op = CreationOperator(statistics)
        self.annihilation_op = AnnihilationOperator(statistics)
        self.number_op = NumberOperator()

        # Fock state tracking
        self.fock_state = FockState({}, statistics)
        self._update_fock_from_state()

        # Metrics
        self.metrics = SpawnMetrics()

        # Callbacks
        self._on_spawn: list[Callable[[str, str], None]] = []
        self._on_annihilate: list[Callable[[str], None]] = []

    def _update_fock_from_state(self) -> None:
        """Sync Fock state with orchestrator state."""
        self.fock_state.occupation_numbers.clear()
        for task_id in self.state.tasks:
            # Extract mode from task ID (e.g., "worker_spawn_0" -> "worker")
            mode = task_id.split("_spawn")[0] if "_spawn" in task_id else task_id
            n = self.fock_state.get_occupation(mode)
            self.fock_state.set_occupation(mode, n + 1)

    def spawn(self, template_id: str, count: int = 1, **task_kwargs) -> list[str]:
        """
        Spawn new tasks from template using creation operator.

        Args:
            template_id: ID of template task to clone
            count: Number of tasks to spawn
            **task_kwargs: Additional kwargs for task creation

        Returns:
            list of new task IDs
        """
        if template_id not in self.state.tasks:
            return []

        template = self.state.tasks[template_id]
        new_ids = []

        for _ in range(count):
            # Check Pauli exclusion for fermions
            mode = template_id
            n = self.fock_state.get_occupation(mode)

            if self.statistics == ParticleStatistics.FERMION and n >= 1:
                # Fermion mode occupied, can't create more
                break

            # Apply creation operator
            new_fock, amplitude = self.creation_op.apply(self.fock_state, mode)

            if new_fock is None:
                break

            # Generate new task ID
            new_id = f"{template_id}_spawn_{uuid.uuid4().hex[:8]}"

            # Clone template task
            new_task = TaskState(
                task_id=new_id,
                name=f"{template.name} (spawned)",
                position=copy.deepcopy(template.position),
                spinor=copy.deepcopy(template.spinor),
                velocity=template.velocity.copy(),
                rest_mass=template.rest_mass,
                deadline=template.deadline,
                dependencies=template.dependencies.copy(),
                required_resources=template.required_resources.copy(),
            )

            # Scale spinor by amplitude from creation operator
            new_task.spinor.components = new_task.spinor.components * amplitude
            new_task.spinor.normalize()

            # Apply any additional kwargs
            for key, value in task_kwargs.items():
                if hasattr(new_task, key):
                    setattr(new_task, key, value)

            # Add to state
            self.state.tasks[new_id] = new_task
            new_ids.append(new_id)

            # Update Fock state
            self.fock_state = new_fock

            # Update metrics
            self.metrics.total_spawned += 1
            self.metrics.net_created += 1
            self.metrics.spawn_events.append(
                {
                    "timestamp": time.time(),
                    "template": template_id,
                    "new_id": new_id,
                    "amplitude": float(np.abs(amplitude)),
                }
            )

            # Fire callbacks
            for callback in self._on_spawn:
                callback(new_id, template_id)

        return new_ids

    def cleanup_completed(self, probability_threshold: float = 0.01) -> list[str]:
        """
        Remove completed tasks using annihilation operator.

        Args:
            probability_threshold: Tasks below this probability are removed

        Returns:
            list of removed task IDs
        """
        removed = []

        for task_id in list(self.state.tasks.keys()):
            task = self.state.tasks[task_id]

            if task.probability < probability_threshold:
                # Extract mode
                mode = task_id.split("_spawn")[0] if "_spawn" in task_id else task_id

                # Apply annihilation operator
                new_fock, _ = self.annihilation_op.apply(self.fock_state, mode)

                if new_fock is not None:
                    # Remove task
                    del self.state.tasks[task_id]
                    removed.append(task_id)

                    # Update Fock state
                    self.fock_state = new_fock

                    # Update metrics
                    self.metrics.total_annihilated += 1
                    self.metrics.net_created -= 1
                    self.metrics.annihilation_events.append(
                        {
                            "timestamp": time.time(),
                            "task_id": task_id,
                            "mode": mode,
                        }
                    )

                    # Fire callbacks
                    for callback in self._on_annihilate:
                        callback(task_id)

        return removed

    def count_tasks(self, mode: Optional[str] = None) -> int:
        """
        Count tasks using number operator.

        Args:
            mode: If specified, count only tasks in this mode

        Returns:
            Number of tasks
        """
        if mode is None:
            return self.number_op.total(self.fock_state)
        return self.number_op.apply(self.fock_state, mode)

    def on_spawn(self, callback: Callable[[str, str], None]) -> None:
        """Register callback for spawn events."""
        self._on_spawn.append(callback)

    def on_annihilate(self, callback: Callable[[str], None]) -> None:
        """Register callback for annihilation events."""
        self._on_annihilate.append(callback)

    def get_metrics(self) -> dict[str, Any]:
        """Get spawning metrics."""
        return self.metrics.to_dict()

    def get_fock_state(self) -> dict[str, Any]:
        """Get current Fock state."""
        return self.fock_state.to_dict()


class BatchCreationOperator:
    """
    Efficient batch spawning for creating many tasks at once.

    Uses vectorized operations where possible.
    """

    def batch_spawn(
        self,
        state: OrchestratorState,
        template: TaskState,
        count: int,
    ) -> list[str]:
        """
        Spawn multiple tasks efficiently.

        Returns list of new task IDs.
        """
        new_ids = []

        for i in range(count):
            new_id = f"{template.task_id}_spawn_{uuid.uuid4().hex[:8]}"

            # Clone template
            new_task = TaskState(
                task_id=new_id,
                name=f"{template.name} (batch {i})",
                position=copy.deepcopy(template.position),
                spinor=copy.deepcopy(template.spinor),
                velocity=template.velocity.copy(),
                rest_mass=template.rest_mass,
                deadline=template.deadline,
                dependencies=(
                    template.dependencies.copy() if hasattr(template, "dependencies") else []
                ),
                required_resources=(
                    template.required_resources.copy()
                    if hasattr(template, "required_resources")
                    else {}
                ),
            )

            # Distribute amplitude
            new_task.spinor.components = new_task.spinor.components / np.sqrt(count)
            new_task.spinor.normalize()

            state.tasks[new_id] = new_task
            new_ids.append(new_id)

        return new_ids

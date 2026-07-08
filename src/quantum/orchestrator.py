"""
Physics-inspired orchestrator for intelligent task scheduling.

Cross-references:
    - src/agent/core.py
    - src/codex_ml/exec/codex_exec.py
    - agents/advanced_physics_calculators.py
"""

from __future__ import annotations

import logging
import math
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class TaskPriority(Enum):
    """Task priority levels mapped to energy states."""

    CRITICAL = 0.1  # Low energy = high priority
    HIGH = 0.5
    MEDIUM = 1.0
    LOW = 2.0
    BACKGROUND = 5.0  # High energy = low priority


@dataclass
class ThermodynamicTask:
    """
    Task with thermodynamic properties.

    Physics: Each task has energy, entropy, and temperature.

    Attributes:
        name: Task identifier
        task_func: Callable to execute
        energy: Computational cost
        priority: Priority level (affects energy)
        temperature: Execution urgency
        entropy: Uncertainty in outcome
        dependencies: List of task names this depends on
        attention_weight: Attention weight for priority modulation (default 1.0)

    Example:
        >>> task = ThermodynamicTask(
        ...     name="load_plugins",
        ...     task_func=lambda: print("Loading..."),
        ...     energy=0.5,
        ...     priority=TaskPriority.CRITICAL
        ... )
    """

    name: str
    task_func: Callable[[], Any]
    energy: float = 1.0
    priority: TaskPriority = TaskPriority.MEDIUM
    temperature: float = 1.0
    entropy: float = 0.0
    dependencies: list[str] = field(default_factory=list)
    attention_weight: float = 1.0

    def calculate_free_energy(self) -> float:
        """
        Calculate Gibbs free energy: G = E - TS.

        With attention modulation: G' = (E / w) - TS
        where w is the attention weight (higher w = lower effective energy).

        Lower free energy = higher execution priority.

        Returns:
            Free energy value
        """
        # Attention modulation: higher weight reduces effective energy
        weight = max(self.attention_weight, 0.01)  # Prevent division by zero
        effective_energy = self.energy / weight

        return effective_energy - self.temperature * self.entropy

    def __lt__(self, other: ThermodynamicTask) -> bool:
        """Compare tasks by free energy for priority queue."""
        return self.calculate_free_energy() < other.calculate_free_energy()

    def __le__(self, other: ThermodynamicTask) -> bool:
        """Less than or equal comparison for tasks."""
        return self.calculate_free_energy() <= other.calculate_free_energy()

    def __ge__(self, other: ThermodynamicTask) -> bool:
        """Greater than or equal comparison for tasks."""
        return self.calculate_free_energy() >= other.calculate_free_energy()

    def __gt__(self, other: ThermodynamicTask) -> bool:
        """Greater than comparison for tasks."""
        return self.calculate_free_energy() > other.calculate_free_energy()


@dataclass
class ThermodynamicOrchestrator:
    """
    Orchestrator using thermodynamic principles for task scheduling.

    Cross-references:
        - src/agent/core.py:AgentCore
        - agents/advanced_physics_calculators.py
        - src/common/error_handling.py

    Example:
        >>> orchestrator = ThermodynamicOrchestrator(
        ...     global_temperature=1.0,
        ...     max_energy_per_cycle=10.0
        ... )
        >>> task = ThermodynamicTask(name="task1", task_func=lambda: None)
        >>> orchestrator.register_task(task)
        >>> results = orchestrator.execute_thermodynamic_cycle()
    """

    tasks: list[ThermodynamicTask] = field(default_factory=list)
    global_temperature: float = 1.0
    max_energy_per_cycle: float = 10.0

    def register_task(self, task: ThermodynamicTask) -> None:
        """
        Add task to orchestration queue.

        Args:
            task: Task to register
        """
        self.tasks.append(task)
        logger.info(f"Registered task '{task.name}' with G={task.calculate_free_energy():.2f}")

    def execute_thermodynamic_cycle(self) -> dict[str, Any]:
        """
        Execute tasks following thermodynamic principles.

        Physics:
            - Minimize free energy
            - Respect energy budget
            - Achieve thermal equilibrium
            - Respect dependency ordering

        Returns:
            Dictionary with execution results
        """
        results: dict[str, Any] = {
            "executed": [],
            "skipped": [],
            "failed": [],
            "total_energy_used": 0.0,
            "final_temperature": self.global_temperature,
        }

        # Track completed tasks
        completed = set()
        remaining = list(self.tasks)

        energy_budget = self.max_energy_per_cycle

        while remaining and energy_budget > 0:
            # Find tasks whose dependencies are satisfied
            ready = [t for t in remaining if all(dep in completed for dep in t.dependencies)]

            if not ready:
                # No tasks can run (unresolvable dependencies)
                for task in remaining:
                    results["skipped"].append(
                        {
                            "name": task.name,
                            "reason": "unresolved_dependencies",
                            "missing": [d for d in task.dependencies if d not in completed],
                        }
                    )
                break

            # Sort ready tasks by free energy (lowest first)
            ready.sort(key=lambda t: t.calculate_free_energy())
            task = ready[0]
            remaining.remove(task)

            # Check if we have enough energy
            if task.energy > energy_budget:
                results["skipped"].append(
                    {
                        "name": task.name,
                        "reason": "insufficient_energy",
                        "required": task.energy,
                        "available": energy_budget,
                    }
                )
                continue

            # Execute task
            try:
                result = task.task_func()

                results["executed"].append(
                    {
                        "name": task.name,
                        "energy": task.energy,
                        "free_energy": task.calculate_free_energy(),
                        "result": result,
                    }
                )

                energy_budget -= task.energy
                results["total_energy_used"] += task.energy
                completed.add(task.name)

            except (ValueError, TypeError, RuntimeError) as exc:
                results["failed"].append({"name": task.name, "error": str(exc)})
                logger.error(f"Task '{task.name}' failed: <ERROR_TYPE>")

        # Calculate final system temperature (cooling after work)
        if results["total_energy_used"] > 0:
            results["final_temperature"] = self.global_temperature * (
                1.0 - results["total_energy_used"] / self.max_energy_per_cycle
            )

        return results

    def optimize_task_order(self) -> list[str]:
        """
        Find optimal execution order minimizing total free energy.

        Uses simulated annealing (thermodynamic optimization).

        Returns:
            List of task names in optimal order
        """
        import random

        if not self.tasks:
            return []

        current_order = list(range(len(self.tasks)))
        current_energy = self._calculate_total_free_energy(current_order)

        best_order = current_order.copy()
        best_energy = current_energy

        # Simulated annealing parameters
        temperature = 100.0
        cooling_rate = 0.95
        iterations = 1000

        for _ in range(iterations):
            # Generate neighbor by swapping two tasks
            new_order = current_order.copy()
            i, j = random.sample(
                range(len(new_order)), 2
            )  # nosec B311 — non-cryptographic ML sampling/shuffling
            new_order[i], new_order[j] = new_order[j], new_order[i]

            new_energy = self._calculate_total_free_energy(new_order)
            delta_energy = new_energy - current_energy

            # Accept if better, or probabilistically if worse
            if delta_energy < 0 or random.random() < math.exp(
                -delta_energy / temperature
            ):  # nosec B311 — non-cryptographic ML sampling/shuffling
                current_order = new_order
                current_energy = new_energy

                if current_energy < best_energy:
                    best_order = current_order.copy()
                    best_energy = current_energy

            temperature *= cooling_rate

        # Return task names in optimized order
        return [self.tasks[i].name for i in best_order]

    def _calculate_total_free_energy(self, order: list[int]) -> float:
        """
        Calculate total free energy for given task order.

        Args:
            order: List of task indices

        Returns:
            Total free energy including dependency penalties
        """
        total = sum(self.tasks[i].calculate_free_energy() for i in order)

        # Add penalty for dependency violations
        task_indices = {self.tasks[i].name: pos for pos, i in enumerate(order)}
        penalty = 0.0

        for i in order:
            task = self.tasks[i]
            task_pos = task_indices[task.name]

            for dep in task.dependencies:
                if dep in task_indices:
                    dep_pos = task_indices[dep]
                    if dep_pos > task_pos:
                        # Dependency violation penalty
                        penalty += 10.0

        return total + penalty


def calculate_thermodynamic_load_priority(
    tasks: list[ThermodynamicTask], current_temperature: float = 1.0
) -> list[tuple[str, float]]:
    """
    Calculate task priority using Boltzmann distribution.

    Args:
        tasks: List of tasks to prioritize
        current_temperature: System temperature

    Returns:
        List of (task_name, priority) tuples sorted by priority
    """
    priorities = []

    for task in tasks:
        # Use free energy for priority
        free_energy = task.calculate_free_energy()
        priority = math.exp(-free_energy / current_temperature)
        priorities.append((task.name, priority))

    priorities.sort(key=lambda x: x[1], reverse=True)
    return priorities

"""
MLOps integration bridge for quantum orchestrator.

Provides observability, metrics export, logging, and distributed orchestration
capabilities for production MLOps environments.
"""

import json
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

import numpy as np

from .orchestrator import QuantumRelativisticDiracOrchestrator


class MetricType(Enum):
    """Types of metrics exported."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class Metric:
    """A single metric observation."""

    name: str
    value: float
    metric_type: MetricType
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_prometheus(self) -> str:
        """Export in Prometheus format."""
        label_str = ",".join(f'{k}="{v}"' for k, v in self.labels.items())
        if label_str:
            return f"{self.name}{{{label_str}}} {self.value} {int(self.timestamp * 1000)}"
        return f"{self.name} {self.value} {int(self.timestamp * 1000)}"


class MetricsCollector:
    """
    Collects and exports metrics from quantum orchestrator.

    Tracks:
    - Task completion rates
    - Physics property distributions
    - Evolution performance
    - Stability indicators
    """

    def __init__(self, orchestrator: QuantumRelativisticDiracOrchestrator):
        self.orchestrator = orchestrator
        self.metrics: list[Metric] = []
        self.start_time = time.time()

    def collect_orchestrator_metrics(self) -> list[Metric]:
        """Collect current orchestrator metrics."""
        metrics = []
        state = self.orchestrator.state

        # Basic counts
        metrics.append(
            Metric(
                "quantum_orchestrator_tasks_total",
                len(state.tasks),
                MetricType.GAUGE,
            )
        )

        metrics.append(
            Metric(
                "quantum_orchestrator_timestamp",
                state.timestamp,
                MetricType.GAUGE,
            )
        )

        metrics.append(
            Metric(
                "quantum_orchestrator_coherence",
                state.coherence,
                MetricType.GAUGE,
            )
        )

        # Task state distributions
        completed = sum(1 for t in state.tasks.values() if abs(t.spinor.total_probability) < 0.01)

        metrics.append(
            Metric(
                "quantum_orchestrator_tasks_completed",
                completed,
                MetricType.COUNTER,
            )
        )

        # Physics metrics per task
        for task_id, task in state.tasks.items():
            labels = {"task_id": task_id}

            metrics.append(
                Metric(
                    "quantum_task_probability",
                    task.spinor.total_probability,
                    MetricType.GAUGE,
                    labels,
                )
            )

            metrics.append(
                Metric(
                    "quantum_task_energy",
                    task.total_energy,
                    MetricType.GAUGE,
                    labels,
                )
            )

            current = self.orchestrator.dirac.compute_current(task)
            metrics.append(
                Metric(
                    "quantum_task_current_magnitude",
                    float(np.linalg.norm(current)),
                    MetricType.GAUGE,
                    labels,
                )
            )

            metrics.append(
                Metric(
                    "quantum_task_velocity",
                    task.speed,
                    MetricType.GAUGE,
                    labels,
                )
            )

        self.metrics.extend(metrics)
        return metrics

    def export_prometheus(self) -> str:
        """Export all metrics in Prometheus format."""
        recent_metrics = [m for m in self.metrics if time.time() - m.timestamp < 60]
        return "\n".join(m.to_prometheus() for m in recent_metrics)

    def export_json(self) -> str:
        """Export metrics as JSON."""
        data = [
            {
                "name": m.name,
                "value": m.value,
                "type": m.metric_type.value,
                "labels": m.labels,
                "timestamp": m.timestamp,
            }
            for m in self.metrics
        ]
        return json.dumps(data, indent=2)


class LoggingAdapter:
    """
    Logging adapter for quantum orchestrator events.

    Integrates with standard Python logging and provides structured
    event logging for MLOps observability.
    """

    def __init__(
        self,
        orchestrator: QuantumRelativisticDiracOrchestrator,
        logger: Optional[logging.Logger] = None,
    ):
        self.orchestrator = orchestrator
        self.logger = logger or logging.getLogger("quantum_orchestrator")
        self.event_count = 0

    def log_evolution_step(self) -> None:
        """Log details of evolution step."""
        state = self.orchestrator.state

        self.logger.debug(
            "Evolution step",
            extra={
                "timestamp": state.timestamp,
                "task_count": len(state.tasks),
                "coherence": state.coherence,
                "event_id": self.event_count,
            },
        )
        self.event_count += 1

    def log_task_completion(self, task_id: str) -> None:
        """Log task completion event."""
        self.logger.info(
            f"Task completed: {task_id}",
            extra={
                "task_id": task_id,
                "timestamp": self.orchestrator.state.timestamp,
                "event_type": "completion",
                "event_id": self.event_count,
            },
        )
        self.event_count += 1

    def log_stability_issue(self, task_id: str, severity: str) -> None:
        """Log stability issues."""
        task = self.orchestrator.state.tasks.get(task_id)
        if not task:
            return

        self.logger.warning(
            f"Stability issue detected: {task_id}",
            extra={
                "task_id": task_id,
                "severity": severity,
                "zitterbewegung": self.orchestrator.dirac.zitterbewegung_amplitude(task),
                "helicity": self.orchestrator.dirac.helicity(task, self.orchestrator.state),
                "event_type": "stability_issue",
                "event_id": self.event_count,
            },
        )
        self.event_count += 1

    def log_conservation_violation(self, violation: float) -> None:
        """Log conservation law violations."""
        self.logger.warning(
            f"Conservation violation detected: {violation:.6f}",
            extra={
                "violation": violation,
                "event_type": "conservation_violation",
                "event_id": self.event_count,
            },
        )
        self.event_count += 1

    def log_physics_properties(self) -> None:
        """Log current physics properties."""
        state = self.orchestrator.state

        total_energy = sum(t.total_energy for t in state.tasks.values())
        total_probability = state.total_probability()

        self.logger.info(
            "Physics state",
            extra={
                "total_energy": total_energy,
                "total_probability": total_probability,
                "timestamp": state.timestamp,
                "event_type": "physics_state",
                "event_id": self.event_count,
            },
        )
        self.event_count += 1


class DistributedCoordinator:
    """
    Coordinator for distributed quantum orchestration.

    Allows multiple orchestrator instances to coordinate task execution
    across distributed environments.
    """

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.peer_nodes: list[str] = []
        self.task_assignments: dict[str, str] = {}  # task_id -> node_id

    def register_peer(self, peer_id: str) -> None:
        """Register a peer orchestrator node."""
        if peer_id not in self.peer_nodes:
            self.peer_nodes.append(peer_id)

    def assign_task(self, task_id: str, node_id: str) -> None:
        """Assign a task to a specific node."""
        self.task_assignments[task_id] = node_id

    def get_local_tasks(self, all_task_ids: list[str]) -> list[str]:
        """Get tasks assigned to this node."""
        return [
            task_id
            for task_id in all_task_ids
            if self.task_assignments.get(task_id, self.node_id) == self.node_id
        ]

    def partition_tasks(
        self,
        task_ids: list[str],
        strategy: str = "round_robin",
    ) -> dict[str, list[str]]:
        """
        Partition tasks across nodes.

        Args:
            task_ids: All task IDs to partition
            strategy: Partitioning strategy (round_robin, hash, custom)

        Returns:
            Dictionary mapping node_id to list of task_ids
        """
        if strategy == "round_robin":
            return self._partition_round_robin(task_ids)
        if strategy == "hash":
            return self._partition_hash(task_ids)
        raise ValueError(f"Unknown strategy: {strategy}")

    def _partition_round_robin(self, task_ids: list[str]) -> dict[str, list[str]]:
        """Round-robin task distribution."""
        all_nodes = [self.node_id] + self.peer_nodes
        partitions: dict[str, list[str]] = {node: [] for node in all_nodes}

        for i, task_id in enumerate(task_ids):
            node = all_nodes[i % len(all_nodes)]
            partitions[node].append(task_id)

        return partitions

    def _partition_hash(self, task_ids: list[str]) -> dict[str, list[str]]:
        """Hash-based task distribution."""
        all_nodes = [self.node_id] + self.peer_nodes
        partitions: dict[str, list[str]] = {node: [] for node in all_nodes}

        for task_id in task_ids:
            node_idx = hash(task_id) % len(all_nodes)
            node = all_nodes[node_idx]
            partitions[node].append(task_id)

        return partitions


class ObservableOrchestrator:
    """
    Wrapper that adds observability to quantum orchestrator.

    Combines metrics, logging, and distributed coordination.
    """

    def __init__(
        self,
        orchestrator: QuantumRelativisticDiracOrchestrator,
        enable_metrics: bool = True,
        enable_logging: bool = True,
        node_id: Optional[str] = None,
    ):
        self.orchestrator = orchestrator

        # Observability components
        self.metrics = MetricsCollector(orchestrator) if enable_metrics else None
        self.logging = LoggingAdapter(orchestrator) if enable_logging else None
        self.coordinator = DistributedCoordinator(node_id) if node_id else None

        # Hooks
        self._pre_evolve_hooks: list[Callable] = []
        self._post_evolve_hooks: list[Callable] = []
        self._task_completion_hooks: list[Callable] = []

    def add_pre_evolve_hook(self, hook: Callable) -> None:
        """Add hook to run before each evolution step."""
        self._pre_evolve_hooks.append(hook)

    def add_post_evolve_hook(self, hook: Callable) -> None:
        """Add hook to run after each evolution step."""
        self._post_evolve_hooks.append(hook)

    def add_task_completion_hook(self, hook: Callable[[str], None]) -> None:
        """Add hook to run when tasks complete."""
        self._task_completion_hooks.append(hook)

    def evolve(self) -> None:
        """Evolve with observability."""
        # Pre-evolve hooks
        for hook in self._pre_evolve_hooks:
            hook()

        # Track completed tasks before evolution
        completed_before = {
            tid
            for tid, task in self.orchestrator.state.tasks.items()
            if abs(task.spinor.total_probability) < 0.01
        }

        # Perform evolution
        self.orchestrator.evolve()

        # Track new completions
        completed_after = {
            tid
            for tid, task in self.orchestrator.state.tasks.items()
            if abs(task.spinor.total_probability) < 0.01
        }
        new_completions = completed_after - completed_before

        # Log and notify
        if self.logging:
            self.logging.log_evolution_step()

            for task_id in new_completions:
                self.logging.log_task_completion(task_id)

        # Collect metrics
        if self.metrics:
            self.metrics.collect_orchestrator_metrics()

        # Task completion hooks
        for task_id in new_completions:
            for hook in self._task_completion_hooks:
                hook(task_id)

        # Post-evolve hooks
        for hook in self._post_evolve_hooks:
            hook()

    def run(self, max_iterations: int = 1000) -> dict[str, Any]:
        """Run with observability."""
        start_time = time.time()

        if self.logging:
            self.logging.logger.info("Starting quantum orchestration run")

        # Run orchestrator using observable evolve (so hooks are called)
        iteration = 0
        for _ in range(max_iterations):
            # Use observable evolve (triggers hooks)
            self.evolve()

            # Check convergence
            if self._has_converged():
                break

        elapsed_time = time.time() - start_time

        if self.logging:
            self.logging.logger.info(f"Orchestration run completed in {elapsed_time:.2f}s")

        # Build results
        results = {
            "elapsed_time": elapsed_time,
            "iterations": iteration + 1,  # At least 1 if loop entered
            "timestamp": self.orchestrator.state.timestamp,
            "coherence": self.orchestrator.state.coherence,
        }

        if self.metrics:
            results["metrics_collected"] = len(self.metrics.metrics)

        return results

    def _has_converged(self) -> bool:
        """Check if orchestration has converged."""
        # All tasks completed
        return all(
            abs(task.spinor.total_probability) < 0.01
            for task in self.orchestrator.state.tasks.values()
        )

    def get_metrics_report(self) -> str:
        """Get metrics in Prometheus format."""
        if not self.metrics:
            return "# Metrics disabled"
        return self.metrics.export_prometheus()

    def get_health_status(self) -> dict[str, Any]:
        """Get health status of orchestrator."""
        state = self.orchestrator.state

        # Check for issues
        issues = []

        if state.coherence < 0.5:
            issues.append("Low coherence")

        # Check for high zitterbewegung
        unstable_tasks = []
        for task_id, task in state.tasks.items():
            amp = self.orchestrator.dirac.zitterbewegung_amplitude(task)
            if amp > 0.5:
                unstable_tasks.append(task_id)

        if unstable_tasks:
            issues.append(f"{len(unstable_tasks)} unstable tasks")

        # Determine status
        if not issues:
            status = "healthy"
        elif len(issues) == 1:
            status = "degraded"
        else:
            status = "unhealthy"

        return {
            "status": status,
            "issues": issues,
            "task_count": len(state.tasks),
            "coherence": state.coherence,
            "timestamp": state.timestamp,
            "unstable_tasks": unstable_tasks,
        }


def create_observable_orchestrator(
    max_throughput: float = 100.0,
    work_granularity: float = 1.0,
    time_step: float = 0.1,
    enable_metrics: bool = True,
    enable_logging: bool = True,
    node_id: Optional[str] = None,
) -> ObservableOrchestrator:
    """
    Factory function for creating observable orchestrator.

    Args:
        max_throughput: Maximum tasks per time unit (speed of light)
        work_granularity: Minimum work unit (Planck constant)
        time_step: Evolution time step
        enable_metrics: Enable metrics collection
        enable_logging: Enable structured logging
        node_id: Node ID for distributed coordination

    Returns:
        ObservableOrchestrator instance
    """
    from .orchestrator import create_orchestrator

    base_orchestrator = create_orchestrator(
        max_throughput=max_throughput,
        work_granularity=work_granularity,
        time_step=time_step,
    )

    return ObservableOrchestrator(
        orchestrator=base_orchestrator,
        enable_metrics=enable_metrics,
        enable_logging=enable_logging,
        node_id=node_id,
    )

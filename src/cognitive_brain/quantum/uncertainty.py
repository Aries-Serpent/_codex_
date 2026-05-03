"""
Uncertainty Optimizer for Adaptive Test Coverage.

This module implements quantum-inspired uncertainty principles for adaptive
test prioritization and coverage optimization. Based on Heisenberg's uncertainty
principle, it balances test thoroughness with execution time.

Mathematical Foundation:
    ΔE · Δt ≥ ℏ/2
    Where:
    - ΔE: Energy uncertainty (test thoroughness)
    - Δt: Time uncertainty (execution speed)
    - ℏ: Reduced Planck constant (minimum uncertainty)

Usage:
    optimizer = UncertaintyOptimizer(config, monitor)
    priority = optimizer.calculate_priority(test_id, history)
    schedule = optimizer.optimize_test_schedule(test_suite, time_budget)
"""

import math
from dataclasses import dataclass
from typing import Optional

from .base import QuantumFeature
from .coherence_monitor import CoherenceMonitor
from .config import QuantumConfig


@dataclass
class ExecutionMetrics:
    """Metrics for a single test execution."""

    test_id: str
    execution_time: float  # seconds
    failure_rate: float  # 0.0 to 1.0
    last_failure_time: Optional[float]  # timestamp or None
    coverage_contribution: float  # 0.0 to 1.0
    complexity_score: float  # 0.0 to 1.0


# Alias for backward compatibility with tests
TestExecutionMetrics = ExecutionMetrics


@dataclass
class ExecutionPriority:
    """Priority calculation result for a test execution."""

    test_id: str
    priority_score: float  # 0.0 to 1.0
    uncertainty: float  # 0.0 to 1.0
    recommended_action: str  # "run", "skip", "defer"
    reasoning: str


class UncertaintyOptimizer:
    """
    Quantum-inspired uncertainty optimizer for adaptive test coverage.

    This class applies uncertainty principles to balance test thoroughness
    with execution speed, prioritizing high-value tests while skipping
    low-value ones.

    Attributes:
        config: Quantum configuration
        monitor: Coherence monitor for tracking metrics
        h_bar: Reduced Planck constant (normalized to 1.0 for simplicity)
        uncertainty_threshold: Minimum uncertainty threshold (default: 0.1)
    """

    def __init__(
        self,
        config: QuantumConfig,
        monitor: Optional[CoherenceMonitor] = None,
        h_bar: float = 1.0,
        uncertainty_threshold: float = 0.1,
    ):
        """
        Initialize the uncertainty optimizer.

        Args:
            config: Quantum configuration
            monitor: Optional coherence monitor
            h_bar: Reduced Planck constant (default: 1.0)
            uncertainty_threshold: Minimum uncertainty (default: 0.1)
        """
        self.config = config
        self.monitor = monitor
        self.h_bar = h_bar
        self.uncertainty_threshold = uncertainty_threshold
        self.test_history: dict[str, ExecutionMetrics] = {}

    def update_test_metrics(self, metrics: ExecutionMetrics) -> None:
        """
        Update metrics for a test.

        Args:
            metrics: Test metrics to update
        """
        self.test_history[metrics.test_id] = metrics

        if self.monitor:
            self.monitor.record_metric(QuantumFeature.UNCERTAINTY.value, "test_update", 1.0)

    def calculate_priority(self, test_id: str, current_time: float) -> ExecutionPriority:
        """
        Calculate priority for a test using uncertainty principles.

        The priority score balances:
        1. Failure risk (higher = more important)
        2. Coverage value (higher = more important)
        3. Execution cost (higher = less important)
        4. Recency of last failure (more recent = more important)

        Args:
            test_id: Unique test identifier
            current_time: Current timestamp

        Returns:
            ExecutionPriority with score, uncertainty, and recommendation
        """
        if test_id not in self.test_history:
            # Unknown test - high uncertainty, medium priority
            return ExecutionPriority(
                test_id=test_id,
                priority_score=0.5,
                uncertainty=1.0,
                recommended_action="run",
                reasoning="New test with no history",
            )

        metrics = self.test_history[test_id]

        # Calculate energy uncertainty (thoroughness)
        # Higher failure rate + coverage = higher energy
        energy_uncertainty = (
            0.4 * metrics.failure_rate
            + 0.3 * metrics.coverage_contribution
            + 0.3 * metrics.complexity_score
        )

        # Calculate time uncertainty (speed)
        # Longer execution = higher time uncertainty
        time_uncertainty = min(metrics.execution_time / 60.0, 1.0)  # Normalize to 60s

        # Apply uncertainty principle: ΔE · Δt ≥ ℏ/2
        uncertainty_product = energy_uncertainty * time_uncertainty
        min_uncertainty = self.h_bar / 2.0

        if uncertainty_product < min_uncertainty:
            # Adjust to satisfy uncertainty principle
            scale_factor = min_uncertainty / (uncertainty_product + 1e-9)
            energy_uncertainty *= math.sqrt(scale_factor)
            time_uncertainty *= math.sqrt(scale_factor)

        # Calculate recency factor
        recency_factor = 0.5  # Default
        if metrics.last_failure_time is not None:
            time_since_failure = current_time - metrics.last_failure_time
            # Exponential decay: more recent = higher priority
            recency_factor = math.exp(-time_since_failure / 86400.0)  # 1 day decay

        # Calculate final priority score
        # High priority: high risk, high coverage, recent failures
        # Low priority: low risk, low coverage, old/no failures, long execution
        priority_score = (
            0.35 * energy_uncertainty
            + 0.25 * recency_factor
            + 0.25 * (1.0 - time_uncertainty)
            + 0.15 * metrics.failure_rate
        )

        # Calculate overall uncertainty using math.hypot for numerical stability
        uncertainty = math.hypot(energy_uncertainty, time_uncertainty)

        # Determine recommended action
        if priority_score > 0.7:
            action = "run"
            reasoning = "High priority: significant risk or value"
        elif priority_score > 0.4:
            action = "defer"
            reasoning = "Medium priority: consider time budget"
        else:
            action = "skip"
            reasoning = "Low priority: minimal risk and value"

        # Track metrics
        if self.monitor:
            self.monitor.record_metric(
                QuantumFeature.UNCERTAINTY.value, "priority_calculation", priority_score
            )

        return ExecutionPriority(
            test_id=test_id,
            priority_score=priority_score,
            uncertainty=uncertainty,
            recommended_action=action,
            reasoning=reasoning,
        )

    def optimize_test_schedule(
        self, test_ids: list[str], time_budget: float, current_time: float
    ) -> tuple[list[str], dict[str, ExecutionPriority]]:
        """
        Optimize test schedule given a time budget.

        Uses greedy algorithm to maximize value within time constraints.

        Args:
            test_ids: List of test identifiers to consider
            time_budget: Maximum time budget in seconds
            current_time: Current timestamp

        Returns:
            Tuple of (selected_tests, priority_map)
        """
        # Calculate priorities for all tests
        priorities = {
            test_id: self.calculate_priority(test_id, current_time) for test_id in test_ids
        }

        # Sort by priority (highest first)
        sorted_tests = sorted(
            test_ids, key=lambda tid: priorities[tid].priority_score, reverse=True
        )

        # Greedy selection within time budget
        selected = []
        remaining_time = time_budget

        for test_id in sorted_tests:
            if test_id not in self.test_history:
                # Unknown test - assume 10s execution time
                exec_time = 10.0
            else:
                exec_time = self.test_history[test_id].execution_time

            if remaining_time >= exec_time:
                selected.append(test_id)
                remaining_time -= exec_time
            else:
                # Update recommendation to "skip" due to time constraint
                priorities[test_id] = ExecutionPriority(
                    test_id=test_id,
                    priority_score=priorities[test_id].priority_score,
                    uncertainty=priorities[test_id].uncertainty,
                    recommended_action="skip",
                    reasoning=f"Excluded due to time budget ({remaining_time:.1f}s remaining)",
                )

        # Track optimization metrics
        if self.monitor:
            self.monitor.record_metric(
                QuantumFeature.UNCERTAINTY.value, "tests_selected", len(selected)
            )
            self.monitor.record_metric(
                QuantumFeature.UNCERTAINTY.value,
                "time_utilization",
                (time_budget - remaining_time) / time_budget if time_budget > 0 else 0.0,
            )

        return selected, priorities

    def compute_uncertainty_bound(
        self, energy_uncertainty: float, time_uncertainty: float
    ) -> float:
        """
        Compute the uncertainty bound (ΔE · Δt).

        Args:
            energy_uncertainty: Energy (thoroughness) uncertainty
            time_uncertainty: Time (speed) uncertainty

        Returns:
            Uncertainty product (should be ≥ ℏ/2)
        """
        return energy_uncertainty * time_uncertainty

    def get_statistics(self) -> dict[str, float]:
        """
        Get statistics about the optimizer.

        Returns:
            Dictionary with statistics
        """
        if not self.test_history:
            return {
                "total_tests": 0,
                "avg_execution_time": 0.0,
                "avg_failure_rate": 0.0,
                "avg_coverage": 0.0,
            }

        total = len(self.test_history)
        avg_time = sum(m.execution_time for m in self.test_history.values()) / total
        avg_failure = sum(m.failure_rate for m in self.test_history.values()) / total
        avg_coverage = sum(m.coverage_contribution for m in self.test_history.values()) / total

        return {
            "total_tests": total,
            "avg_execution_time": avg_time,
            "avg_failure_rate": avg_failure,
            "avg_coverage": avg_coverage,
        }

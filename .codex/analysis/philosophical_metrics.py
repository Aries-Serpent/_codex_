"""
Philosophical Metrics Dashboard

Implements measurement equations from the philosophical framework for:
- Rhizomaticity (Deleuze)
- Session Satisfaction (Whitehead)
- Rate of Becoming (Process Philosophy)
- Deterritorialization Force (Deleuze)

Reference: .codex/docs/PHILOSOPHICAL_FRAMEWORK.md#philosophical-metrics

These metrics provide quantitative assessment of how well the codebase
aligns with philosophical principles.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

LOGGER = logging.getLogger(__name__)


@dataclass
class PhilosophicalMetrics:
    """Container for all philosophical metrics."""

    rhizomaticity: float = 0.0  # 0.0 to 1.0
    session_satisfaction: float = 0.0  # 0.0+
    rate_of_becoming: float = 0.0  # events per hour
    deterritorialization_force: float = 0.0  # can be negative
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "rhizomaticity": self.rhizomaticity,
            "session_satisfaction": self.session_satisfaction,
            "rate_of_becoming": self.rate_of_becoming,
            "deterritorialization_force": self.deterritorialization_force,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class PhilosophicalMetricsCalculator:
    """
    Calculator for philosophical metrics.

    Provides measurement equations from the philosophical framework.

    Example:
        >>> calc = PhilosophicalMetricsCalculator()
        >>> rhizomaticity = calc.calculate_rhizomaticity(nodes=10, connections=25)
        >>> print(f"Rhizomaticity: {rhizomaticity:.2%}")
        >>> satisfaction = calc.calculate_satisfaction(
        ...     prehensions=5, realizations=2, definiteness=0.8
        ... )
        >>> print(f"Satisfaction: {satisfaction:.2f}")
    """

    @staticmethod
    def calculate_rhizomaticity(nodes: int, connections: int) -> float:
        """
        Calculate rhizomaticity score (Deleuze).

        Rhizomaticity = Connections / Max_Possible_Connections

        Where:
        - 0.0 = Tree structure (minimal connections)
        - 1.0 = Fully connected rhizome

        Goal: R > 0.5 (more rhizomatic than tree-like)

        Reference: .codex/docs/PHILOSOPHICAL_FRAMEWORK.md#rhizomaticity-score

        Args:
            nodes: Number of nodes in the network
            connections: Number of connections between nodes

        Returns:
            Rhizomaticity score (0.0 to 1.0)
        """
        if nodes <= 1:
            return 0.0

        max_connections = (nodes * (nodes - 1)) / 2
        if max_connections == 0:
            return 0.0

        rhizomaticity = connections / max_connections
        return min(1.0, rhizomaticity)

    @staticmethod
    def calculate_satisfaction(
        prehensions: int, realizations: int, definiteness: float
    ) -> float:
        """
        Calculate session satisfaction (Whitehead).

        Satisfaction = (Prehensions + Realizations) × Definiteness

        Where:
        - Prehensions = Past sessions incorporated
        - Realizations = Potentials actualized
        - Definiteness = Completion percentage (0.0-1.0)

        Reference: .codex/docs/PHILOSOPHICAL_FRAMEWORK.md#session-satisfaction

        Args:
            prehensions: Number of past sessions incorporated
            realizations: Number of potentials actualized
            definiteness: Completion percentage (0.0 to 1.0)

        Returns:
            Satisfaction score (0.0+)
        """
        if not 0.0 <= definiteness <= 1.0:
            raise ValueError(f"Definiteness must be 0.0-1.0, got {definiteness}")

        return (prehensions + realizations) * definiteness

    @staticmethod
    def calculate_becoming_rate(events: int, time_hours: float) -> float:
        """
        Calculate rate of becoming (Process Philosophy).

        Rate of Becoming = Events / Time

        Process Philosophy: Reality is rate of change

        Classification:
        - > 20 events/hour: INTENSE BECOMING
        - 10-20: ACTIVE BECOMING
        - 5-10: MODERATE BECOMING
        - < 5: SLOW BECOMING

        Reference: .codex/docs/PHILOSOPHICAL_FRAMEWORK.md#rate-of-becoming

        Args:
            events: Number of events
            time_hours: Time period in hours

        Returns:
            Rate of becoming (events per hour)
        """
        if time_hours <= 0:
            raise ValueError(f"Time must be positive, got {time_hours}")

        return events / time_hours

    @staticmethod
    def classify_becoming_rate(rate: float) -> str:
        """
        Classify rate of becoming into categories.

        Args:
            rate: Rate of becoming (events per hour)

        Returns:
            Classification string
        """
        if rate > 20:
            return "INTENSE BECOMING"
        if rate >= 10:
            return "ACTIVE BECOMING"
        if rate >= 5:
            return "MODERATE BECOMING"
        return "SLOW BECOMING"

    @staticmethod
    def calculate_deterritorialization_force(
        rigidity: float, innovation: float
    ) -> float:
        """
        Calculate deterritorialization force (Deleuze).

        F_deterr = Innovation_Pressure - Rigidity

        Where:
        - Positive: Deterritorialization needed (break rigid patterns)
        - Negative: Reterritorialization occurring (forming new patterns)
        - Zero: Equilibrium

        Reference: .codex/docs/PHILOSOPHICAL_FRAMEWORK.md#deterritorialization-force

        Args:
            rigidity: Rigidity score (0.0 to 1.0)
            innovation: Innovation pressure score (0.0 to 1.0)

        Returns:
            Deterritorialization force (-1.0 to 1.0)
        """
        if not 0.0 <= rigidity <= 1.0:
            raise ValueError(f"Rigidity must be 0.0-1.0, got {rigidity}")
        if not 0.0 <= innovation <= 1.0:
            raise ValueError(f"Innovation must be 0.0-1.0, got {innovation}")

        return innovation - rigidity

    @staticmethod
    def interpret_deterr_force(force: float) -> str:
        """
        Interpret deterritorialization force.

        Args:
            force: Deterritorialization force

        Returns:
            Interpretation string
        """
        if force > 0.3:
            return "HIGH deterritorialization needed - break rigid patterns"
        if force > 0.1:
            return "MODERATE deterritorialization - some flexibility needed"
        if force > -0.1:
            return "EQUILIBRIUM - balanced state"
        if force > -0.3:
            return "MODERATE reterritorialization - forming new patterns"
        return "HIGH reterritorialization - strong pattern formation"


class PhilosophicalMetricsDashboard:
    """
    Dashboard for tracking and reporting philosophical metrics over time.

    Example:
        >>> dashboard = PhilosophicalMetricsDashboard()
        >>> metrics = dashboard.calculate_current_metrics(
        ...     nodes=10, connections=25,
        ...     prehensions=5, realizations=2, definiteness=0.8,
        ...     events=100, time_hours=5.0,
        ...     rigidity=0.6, innovation=0.8
        ... )
        >>> dashboard.add_metrics(metrics)
        >>> report = dashboard.generate_report()
        >>> print(report)
    """

    def __init__(self) -> None:
        self.calculator = PhilosophicalMetricsCalculator()
        self.metrics_history: List[PhilosophicalMetrics] = []
        LOGGER.info("PhilosophicalMetricsDashboard initialized")

    def calculate_current_metrics(
        self,
        nodes: int = 0,
        connections: int = 0,
        prehensions: int = 0,
        realizations: int = 0,
        definiteness: float = 0.0,
        events: int = 0,
        time_hours: float = 1.0,
        rigidity: float = 0.0,
        innovation: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PhilosophicalMetrics:
        """
        Calculate all current philosophical metrics.

        Args:
            nodes: Number of nodes (for rhizomaticity)
            connections: Number of connections (for rhizomaticity)
            prehensions: Past sessions incorporated (for satisfaction)
            realizations: Potentials actualized (for satisfaction)
            definiteness: Completion percentage (for satisfaction)
            events: Number of events (for becoming rate)
            time_hours: Time period in hours (for becoming rate)
            rigidity: Rigidity score (for deterritorialization force)
            innovation: Innovation pressure (for deterritorialization force)
            metadata: Optional metadata

        Returns:
            PhilosophicalMetrics object
        """
        rhizomaticity = self.calculator.calculate_rhizomaticity(nodes, connections)

        satisfaction = self.calculator.calculate_satisfaction(
            prehensions, realizations, definiteness
        )

        rate_of_becoming = (
            self.calculator.calculate_becoming_rate(events, time_hours)
            if time_hours > 0
            else 0.0
        )

        deterr_force = self.calculator.calculate_deterritorialization_force(
            rigidity, innovation
        )

        metrics = PhilosophicalMetrics(
            rhizomaticity=rhizomaticity,
            session_satisfaction=satisfaction,
            rate_of_becoming=rate_of_becoming,
            deterritorialization_force=deterr_force,
            metadata=metadata or {},
        )

        LOGGER.debug(
            f"Calculated metrics: R={rhizomaticity:.2%}, "
            f"S={satisfaction:.2f}, B={rate_of_becoming:.2f}/hr, "
            f"F={deterr_force:.2f}"
        )

        return metrics

    def add_metrics(self, metrics: PhilosophicalMetrics) -> None:
        """Add metrics to the history."""
        self.metrics_history.append(metrics)
        LOGGER.debug(f"Added metrics to history (total: {len(self.metrics_history)})")

    def get_latest_metrics(self) -> Optional[PhilosophicalMetrics]:
        """Get the most recent metrics."""
        return self.metrics_history[-1] if self.metrics_history else None

    def get_metrics_trend(self, metric_name: str, count: int = 10) -> List[float]:
        """
        Get trend data for a specific metric.

        Args:
            metric_name: Name of the metric (e.g., "rhizomaticity")
            count: Number of recent values to return

        Returns:
            List of metric values (most recent first)
        """
        recent = self.metrics_history[-count:] if count else self.metrics_history

        values = []
        for m in recent:
            if hasattr(m, metric_name):
                values.append(getattr(m, metric_name))

        return values

    def generate_report(self) -> str:
        """
        Generate a human-readable report of philosophical metrics.

        Returns:
            Formatted report string
        """
        if not self.metrics_history:
            return "No metrics recorded yet."

        latest = self.metrics_history[-1]

        report_lines = [
            "═" * 60,
            "PHILOSOPHICAL METRICS DASHBOARD",
            "═" * 60,
            "",
            f"Timestamp: {latest.timestamp.isoformat()}",
            "",
            "─" * 60,
            "1. RHIZOMATICITY (Deleuze)",
            "─" * 60,
            f"Score: {latest.rhizomaticity:.2%}",
            f"Interpretation: {'✅ Rhizomatic' if latest.rhizomaticity > 0.5 else '⚠️ Tree-like'}",
            "Goal: > 50% (more connections than tree structure)",
            "",
            "─" * 60,
            "2. SESSION SATISFACTION (Whitehead)",
            "─" * 60,
            f"Score: {latest.session_satisfaction:.2f}",
            f"Interpretation: {'✅ High satisfaction' if latest.session_satisfaction > 5.0 else '⚠️ Low satisfaction'}",
            "",
            "─" * 60,
            "3. RATE OF BECOMING (Process Philosophy)",
            "─" * 60,
            f"Rate: {latest.rate_of_becoming:.2f} events/hour",
            f"Classification: {self.calculator.classify_becoming_rate(latest.rate_of_becoming)}",
            "",
            "─" * 60,
            "4. DETERRITORIALIZATION FORCE (Deleuze)",
            "─" * 60,
            f"Force: {latest.deterritorialization_force:+.2f}",
            f"Interpretation: {self.calculator.interpret_deterr_force(latest.deterritorialization_force)}",
            "",
            "═" * 60,
        ]

        # Add trend analysis if we have multiple datapoints
        if len(self.metrics_history) > 1:
            report_lines.extend(
                [
                    "",
                    "TREND ANALYSIS",
                    "─" * 60,
                    f"Total measurements: {len(self.metrics_history)}",
                ]
            )

            # Calculate average metrics
            avg_rhizo = sum(m.rhizomaticity for m in self.metrics_history) / len(
                self.metrics_history
            )
            avg_satisf = sum(
                m.session_satisfaction for m in self.metrics_history
            ) / len(self.metrics_history)

            report_lines.extend(
                [
                    f"Average Rhizomaticity: {avg_rhizo:.2%}",
                    f"Average Satisfaction: {avg_satisf:.2f}",
                    "",
                ]
            )

        return "\n".join(report_lines)

    def export_metrics(self, output_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Export metrics history to a dictionary (or file).

        Args:
            output_path: Optional path to save JSON file

        Returns:
            Dictionary with all metrics history
        """
        data = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_measurements": len(self.metrics_history),
            "metrics": [m.to_dict() for m in self.metrics_history],
        }

        if output_path:
            import json

            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)
            LOGGER.info(f"Exported metrics to {output_path}")

        return data

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the metrics dashboard."""
        if not self.metrics_history:
            return {"total_measurements": 0}

        latest = self.metrics_history[-1]

        return {
            "total_measurements": len(self.metrics_history),
            "latest_timestamp": latest.timestamp.isoformat(),
            "current_rhizomaticity": latest.rhizomaticity,
            "current_satisfaction": latest.session_satisfaction,
            "current_becoming_rate": latest.rate_of_becoming,
            "current_deterr_force": latest.deterritorialization_force,
        }

"""Code metrics aggregation and analysis."""

import statistics
from dataclasses import dataclass
from typing import Any


@dataclass
class CodeMetrics:
    """Aggregated code quality metrics for a code entity."""

    cyclomatic_complexity: int
    cognitive_complexity: float
    lines_of_code: int
    comment_lines: int
    maintainability_index: float

    @property
    def quality_tier(self) -> str:
        """Compute quality grade (A-F) from maintainability index."""
        if self.maintainability_index >= 85:
            return "A"
        if self.maintainability_index >= 70:
            return "B"
        if self.maintainability_index >= 55:
            return "C"
        if self.maintainability_index >= 40:
            return "D"
        return "F"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "cyclomatic_complexity": self.cyclomatic_complexity,
            "cognitive_complexity": self.cognitive_complexity,
            "lines_of_code": self.lines_of_code,
            "comment_lines": self.comment_lines,
            "maintainability_index": self.maintainability_index,
            "quality_tier": self.quality_tier,
        }


class MetricsAggregator:
    """Aggregate and correlate metrics from multiple sources."""

    def __init__(self) -> None:
        self.metrics: dict[str, CodeMetrics] = {}

    def store_metrics(self, entity_id: str, metrics: CodeMetrics) -> None:
        """Store metrics for an entity."""
        self.metrics[entity_id] = metrics

    def aggregate(self, metrics_list: list[CodeMetrics]) -> CodeMetrics:
        """Aggregate multiple metrics into summary.

        Args:
            metrics_list: list of CodeMetrics objects

        Returns:
            Aggregated CodeMetrics
        """
        if not metrics_list:
            return CodeMetrics(0, 0.0, 0, 0, 100.0)

        return CodeMetrics(
            cyclomatic_complexity=sum(m.cyclomatic_complexity for m in metrics_list),
            cognitive_complexity=sum(m.cognitive_complexity for m in metrics_list),
            lines_of_code=sum(m.lines_of_code for m in metrics_list),
            comment_lines=sum(m.comment_lines for m in metrics_list),
            maintainability_index=statistics.mean(m.maintainability_index for m in metrics_list),
        )

    def correlate_complexity_coverage(
        self,
        complexity_metrics: list[float],
        coverage_metrics: list[float],
    ) -> float:
        """Compute correlation between complexity and test coverage.

        Args:
            complexity_metrics: list of complexity values
            coverage_metrics: list of coverage values

        Returns:
            Pearson correlation coefficient (-1.0 to 1.0)

        Raises:
            ValueError: If lists have different lengths or fewer than 2 items
        """
        if len(complexity_metrics) < 2 or len(coverage_metrics) < 2:
            raise ValueError(
                f"At least 2 data points required for correlation, got {len(complexity_metrics)} and {len(coverage_metrics)}"  # noqa: E501
            )

        if len(complexity_metrics) != len(coverage_metrics):
            raise ValueError(
                f"complexity_metrics and coverage_metrics must have the same length: "
                f"got {len(complexity_metrics)} and {len(coverage_metrics)}"
            )
        mean_cc = statistics.mean(complexity_metrics)
        mean_cov = statistics.mean(coverage_metrics)

        numerator = sum(
            (c - mean_cc) * (v - mean_cov)
            for c, v in zip(complexity_metrics, coverage_metrics, strict=False)
        )

        denom_cc = (sum((c - mean_cc) ** 2 for c in complexity_metrics)) ** 0.5
        denom_cov = (sum((c - mean_cov) ** 2 for c in coverage_metrics)) ** 0.5

        if denom_cc * denom_cov == 0:
            return 0.0

        return numerator / (denom_cc * denom_cov)

    def summary(self) -> dict[str, Any]:
        """Get summary statistics of all metrics."""
        if not self.metrics:
            return {}

        ccs = [m.cyclomatic_complexity for m in self.metrics.values()]
        locs = [m.lines_of_code for m in self.metrics.values()]
        mis = [m.maintainability_index for m in self.metrics.values()]

        return {
            "total_entities": len(self.metrics),
            "total_lines_of_code": sum(locs),
            "average_cyclomatic_complexity": statistics.mean(ccs),
            "max_cyclomatic_complexity": max(ccs),
            "average_maintainability_index": statistics.mean(mis),
        }

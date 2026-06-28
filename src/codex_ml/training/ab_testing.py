"""A/B testing framework for model evaluation and gradual rollout.

This module provides infrastructure for running A/B tests on models and
determining statistical significance of performance differences.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = ["ABTestConfig", "ABTestManager", "ModelVariant"]


@dataclass
class ModelVariant:
    """Model variant in an A/B test.

    Attributes:
        name: Variant name (e.g., "v1.0", "v2.0")
        model_path: Path to model checkpoint
        traffic_percentage: Percentage of traffic allocated (0-100)
        results: list of result dictionaries
    """

    name: str
    model_path: str
    traffic_percentage: float = 0.0
    results: list[dict[str, float]] = field(default_factory=list)

    def record_result(self, metrics: dict[str, float]):
        """Record a result for this variant.

        Args:
            metrics: Dictionary of metric values
        """
        self.results.append(metrics)

    def get_average_metric(self, metric_name: str) -> float:
        """Get average value for a metric.

        Args:
            metric_name: Name of the metric

        Returns:
            Average value across all results
        """
        if not self.results:
            return 0.0

        values = [r.get(metric_name, 0.0) for r in self.results]
        return sum(values) / len(values)

    def get_sample_count(self) -> int:
        """Get number of samples for this variant."""
        return len(self.results)


@dataclass
class ABTestConfig:
    """Configuration for an A/B test.

    Attributes:
        experiment_name: Name of the experiment
        control_variant: Name of control variant (baseline)
        treatment_variants: list of treatment variant names
        traffic_split: Dictionary mapping variant to traffic percentage
        primary_metric: Primary metric for winner selection
        min_samples: Minimum samples required per variant
        confidence_level: Confidence level for significance testing (0-1)
    """

    experiment_name: str
    control_variant: str
    treatment_variants: list[str]
    traffic_split: dict[str, float]
    primary_metric: str = "accuracy"
    min_samples: int = 100
    confidence_level: float = 0.95


class ABTestManager:
    """Manager for A/B testing experiments."""

    def __init__(self, config: ABTestConfig):
        """Initialize A/B test manager.

        Args:
            config: A/B test configuration
        """
        self.config = config
        self.variants: dict[str, ModelVariant] = {}

        # Initialize control variant
        self.variants[config.control_variant] = ModelVariant(
            name=config.control_variant,
            model_path=f"models/{config.control_variant}/model.pt",
            traffic_percentage=config.traffic_split.get(config.control_variant, 0.0),
        )

        # Initialize treatment variants
        for treatment in config.treatment_variants:
            self.variants[treatment] = ModelVariant(
                name=treatment,
                model_path=f"models/{treatment}/model.pt",
                traffic_percentage=config.traffic_split.get(treatment, 0.0),
            )

        self.start_time = datetime.now(UTC).isoformat()
        logger.info(f"Started A/B test: {config.experiment_name}")

    def record_result(self, variant_name: str, metrics: dict[str, float]):
        """Record a result for a variant.

        Args:
            variant_name: Name of the variant
            metrics: Dictionary of metric values
        """
        if variant_name not in self.variants:
            raise ValueError(f"Unknown variant: {variant_name}")

        self.variants[variant_name].record_result(metrics)

    def get_variant_metrics(self, variant_name: str) -> dict[str, float]:
        """Get average metrics for a variant.

        Args:
            variant_name: Name of the variant

        Returns:
            Dictionary of average metric values
        """
        variant = self.variants[variant_name]

        if not variant.results:
            return {}

        # Get all metric names
        metric_names: set[Any] = set()
        for result in variant.results:
            metric_names.update(result.keys())

        # Calculate averages
        return {metric: variant.get_average_metric(metric) for metric in metric_names}

    def is_significant(self, alpha: float = 0.05) -> bool:
        """Check if results are statistically significant.

        Args:
            alpha: Significance level (default: 0.05 for 95% confidence)

        Returns:
            True if difference is statistically significant
        """
        # Check minimum samples
        for variant in self.variants.values():
            if variant.get_sample_count() < self.config.min_samples:
                logger.info(
                    f"Insufficient samples for {variant.name}: "
                    f"{variant.get_sample_count()} < {self.config.min_samples}"
                )
                return False

        # Simplified significance test
        # In production, use proper statistical tests (t-test, chi-square, etc.)
        control = self.variants[self.config.control_variant]
        control_metric = control.get_average_metric(self.config.primary_metric)

        for treatment_name in self.config.treatment_variants:
            treatment = self.variants[treatment_name]
            treatment_metric = treatment.get_average_metric(self.config.primary_metric)

            # Simple threshold-based check
            # In production, calculate p-value using t-test
            relative_diff = abs(treatment_metric - control_metric) / max(control_metric, 0.001)

            if relative_diff > 0.02:  # 2% difference threshold
                logger.info(
                    f"Significant difference detected: "
                    f"{treatment_name}={treatment_metric:.3f} vs "
                    f"{self.config.control_variant}={control_metric:.3f}"
                )
                return True

        return False

    def get_winner(self) -> str:
        """Determine the winning variant based on primary metric.

        Returns:
            Name of winning variant
        """
        best_variant = None
        best_metric = float("-inf")

        for variant_name, variant in self.variants.items():
            metric_value = variant.get_average_metric(self.config.primary_metric)

            if metric_value > best_metric:
                best_metric = metric_value
                best_variant = variant_name

        logger.info(f"Winner: {best_variant} with {self.config.primary_metric}={best_metric:.3f}")
        return best_variant  # type: ignore[return-value]

    def get_comparison_report(self) -> dict[str, Any]:
        """Generate comparison report across all variants.

        Returns:
            Dictionary with comparison results
        """
        report: dict[str, Any] = {
            "experiment_name": self.config.experiment_name,
            "start_time": self.start_time,
            "variants": {},
            "winner": None,
            "is_significant": False,
        }

        # Collect variant metrics
        for variant_name, variant in self.variants.items():
            report["variants"][variant_name] = {
                "traffic_percentage": variant.traffic_percentage,
                "sample_count": variant.get_sample_count(),
                "metrics": self.get_variant_metrics(variant_name),
            }

        # Determine winner if significant
        if self.is_significant():
            report["is_significant"] = True
            report["winner"] = self.get_winner()

        return report

    def gradual_rollout(self, winner_variant: str, steps: int = 5):
        """Gradually rollout winning variant.

        Args:
            winner_variant: Name of variant to roll out
            steps: Number of rollout steps (default: 5)
        """
        if winner_variant not in self.variants:
            raise ValueError(f"Unknown variant: {winner_variant}")

        logger.info(f"Starting gradual rollout of {winner_variant} in {steps} steps")

        # Calculate traffic increments
        control_traffic = self.variants[self.config.control_variant].traffic_percentage
        increment = control_traffic / steps

        for step in range(1, steps + 1):
            new_winner_traffic = increment * step
            new_control_traffic = control_traffic - (increment * step)

            logger.info(
                f"Step {step}/{steps}: "
                f"{winner_variant}={new_winner_traffic:.1f}%, "
                f"{self.config.control_variant}={new_control_traffic:.1f}%"
            )

            # In production, update traffic routing here
            # time.sleep(rollout_interval)

        logger.info(f"Gradual rollout complete: {winner_variant} at 100%")

    def save_results(self, output_path: Path | str):
        """Save experiment results to file.

        Args:
            output_path: Path to save results JSON
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        report = self.get_comparison_report()
        output_path.write_text(json.dumps(report, indent=2))

        logger.info(f"Saved A/B test results to {output_path}")

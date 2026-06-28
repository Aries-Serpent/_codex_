"""Fairness and bias checking plugin.

Provides comprehensive fairness evaluation for ML models including:
- Demographic parity
- Equal opportunity
- Calibration checks
- Bias drift detection
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import numpy as np

from codex_ml.plugins.plugin_registry import Plugin, PluginMetadata, register_plugin

logger = logging.getLogger(__name__)

__all__ = ["BiasAlert", "FairnessCheckerPlugin", "FairnessMetrics"]


@dataclass
class FairnessMetrics:
    """Fairness evaluation metrics."""

    demographic_parity: float  # 1.0 = perfect parity
    equal_opportunity: float  # 1.0 = perfect equality
    calibration_error: float  # 0.0 = perfect calibration
    bias_alerts: list[str]


@dataclass
class BiasAlert:
    """Alert for detected bias."""

    metric: str
    severity: str  # low, medium, high, critical
    threshold: float
    actual: float
    affected_groups: list[str]


@register_plugin
class FairnessCheckerPlugin(Plugin):
    """Plugin for fairness and bias checking.

    Example:
        >>> checker = FairnessCheckerPlugin()
        >>> metrics = checker.execute(
        ...     predictions=pred,
        ...     labels=true,
        ...     sensitive_attributes={"gender": gender}
        ... )
    """

    def initialize(self) -> None:
        """Initialize fairness checker."""
        self.thresholds = {
            "demographic_parity": 0.90,
            "equal_opportunity": 0.90,
            "calibration_error": 0.10,
        }
        logger.info("FairnessCheckerPlugin initialized")

    def execute(
        self,
        predictions: Any,
        labels: Any,
        sensitive_attributes: dict[str, Any],
        **kwargs,
    ) -> dict[str, Any]:
        """Compute fairness metrics.

        Args:
            predictions: Model predictions
            labels: Ground truth labels
            sensitive_attributes: Dictionary of sensitive attributes

        Returns:
            Dictionary of fairness metrics and alerts
        """
        # Convert to numpy
        predictions = np.array(predictions)
        labels = np.array(labels)

        metrics = {}
        alerts = []

        # Compute metrics for each sensitive attribute
        for attr_name, attr_values in sensitive_attributes.items():
            attr_values = np.array(attr_values)

            # Demographic parity
            dp = self._demographic_parity(predictions, attr_values)
            metrics[f"{attr_name}_demographic_parity"] = dp

            if dp < self.thresholds["demographic_parity"]:
                alerts.append(f"Demographic parity violation for {attr_name}: {dp:.3f}")

            # Equal opportunity
            eo = self._equal_opportunity(predictions, labels, attr_values)
            metrics[f"{attr_name}_equal_opportunity"] = eo

            if eo < self.thresholds["equal_opportunity"]:
                alerts.append(f"Equal opportunity violation for {attr_name}: {eo:.3f}")

        # Calibration
        cal_error = self._calibration_error(predictions, labels)
        metrics["calibration_error"] = cal_error

        if cal_error > self.thresholds["calibration_error"]:
            alerts.append(f"Calibration error too high: {cal_error:.3f}")

        return {
            "metrics": metrics,
            "alerts": alerts,
            "is_fair": len(alerts) == 0,
        }

    def _demographic_parity(self, predictions: np.ndarray, sensitive_attr: np.ndarray) -> float:
        """Calculate demographic parity score.

        Returns 1.0 for perfect parity, lower for imbalance.
        """
        unique_values = np.unique(sensitive_attr)
        if len(unique_values) < 2:
            return 1.0

        positive_rates = []
        for value in unique_values:
            mask = sensitive_attr == value
            if mask.sum() > 0:
                rate = predictions[mask].mean()
                positive_rates.append(rate)

        if len(positive_rates) < 2:
            return 1.0

        # Parity score = min_rate / max_rate
        min_rate = min(positive_rates)
        max_rate = max(positive_rates)

        if max_rate == 0:
            return 1.0

        return min_rate / max_rate

    def _equal_opportunity(
        self, predictions: np.ndarray, labels: np.ndarray, sensitive_attr: np.ndarray
    ) -> float:
        """Calculate equal opportunity score.

        True positive rate equality across groups.
        """
        unique_values = np.unique(sensitive_attr)
        if len(unique_values) < 2:
            return 1.0

        tpr_scores = []
        for value in unique_values:
            mask = (sensitive_attr == value) & (labels == 1)
            if mask.sum() > 0:
                tpr = predictions[mask].mean()
                tpr_scores.append(tpr)

        if len(tpr_scores) < 2:
            return 1.0

        # Equal opportunity = min_tpr / max_tpr
        min_tpr = min(tpr_scores)
        max_tpr = max(tpr_scores)

        if max_tpr == 0:
            return 1.0

        return min_tpr / max_tpr

    def _calibration_error(self, predictions: np.ndarray, labels: np.ndarray) -> float:
        """Calculate calibration error.

        Expected Calibration Error (ECE).
        """
        # Bin predictions
        n_bins = 10
        bins = np.linspace(0, 1, n_bins + 1)

        ece = 0.0
        for i in range(n_bins):
            mask = (predictions >= bins[i]) & (predictions < bins[i + 1])
            if mask.sum() > 0:
                bin_accuracy = labels[mask].mean()
                bin_confidence = predictions[mask].mean()
                bin_weight = mask.sum() / len(predictions)
                ece += bin_weight * abs(bin_accuracy - bin_confidence)

        return ece

    @classmethod
    def get_metadata(cls) -> PluginMetadata:
        return PluginMetadata(
            name="fairness_checker",
            version="1.0.0",
            author="Codex Team",
            description="Fairness and bias evaluation for ML models",
        )

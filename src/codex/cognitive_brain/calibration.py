"""Confidence Calibration Module.

Implements Brier score tracking and confidence calibration for decision accuracy.
Target: Brier score <0.15 (±5% calibration error)
"""

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np


class ConfidenceCalibrator:
    """Track and calibrate confidence scores to minimize Brier score.

    Brier Score = mean((forecast - outcome)^2)
    - Target <0.15 indicates good calibration
    - 0 = perfect calibration, 1 = worst calibration
    """

    def __init__(self, storage_path: Optional[Path] = None):
        """Initialize calibrator.

        Args:
            storage_path: Path to store calibration metrics
        """
        self.storage_path = storage_path or Path(".codex/reasoning/calibration.json")

        # Per-category calibration tracking
        self.confidence_bins: Dict[str, Dict[float, List[float]]] = defaultdict(
            lambda: defaultdict(list)
        )
        self.outcomes_by_category: Dict[str, List[bool]] = defaultdict(list)
        self.confidences_by_category: Dict[str, List[float]] = defaultdict(list)

        # Overall metrics
        self.total_predictions = 0
        self.brier_history: List[float] = []

        # Load historical data
        self._load_metrics()

    def update(self, confidence: float, outcome: bool) -> None:
        """Update calibration data with new prediction.

        Args:
            confidence: Predicted confidence (0-1)
            outcome: Actual outcome (True=success, False=failure)
        """
        self.confidences_by_category["overall"].append(confidence)
        self.outcomes_by_category["overall"].append(outcome)
        self.total_predictions += 1

        # Calculate current Brier score
        if len(self.outcomes_by_category["overall"]) >= 10:
            brier = self._calculate_brier_score(
                self.confidences_by_category["overall"],
                self.outcomes_by_category["overall"],
            )
            self.brier_history.append(brier)

    def update_category(
        self, category: str, confidence: float, outcome: bool
    ) -> None:
        """Update calibration for specific decision category.

        Args:
            category: Decision category
            confidence: Predicted confidence
            outcome: Actual outcome
        """
        if category not in self.outcomes_by_category:
            self.outcomes_by_category[category] = []
            self.confidences_by_category[category] = []

        self.confidences_by_category[category].append(confidence)
        self.outcomes_by_category[category].append(outcome)

        # Bin the confidence
        confidence_bin = int(confidence * 10) / 10  # 0.0-0.1, 0.1-0.2, etc
        self.confidence_bins[category][confidence_bin].append(float(outcome))

    def calibrate_confidence(self, raw_confidence: float, category: str = "overall") -> float:
        """Calibrate raw confidence score.

        Adjusts confidence to minimize calibration error.

        Args:
            raw_confidence: Raw confidence from reasoning layer
            category: Decision category for targeted calibration

        Returns:
            Calibrated confidence score
        """
        if category not in self.confidences_by_category:
            return raw_confidence

        # Calculate per-bin accuracy
        bin_accuracy = self._calculate_bin_accuracy(category, raw_confidence)

        # Apply calibration adjustment
        calibrated = raw_confidence * bin_accuracy / (raw_confidence + 1e-6)
        calibrated = max(0.0, min(1.0, calibrated))  # Clamp to [0, 1]

        return calibrated

    def _calculate_bin_accuracy(self, category: str, confidence: float) -> float:
        """Calculate accuracy for confidence bin."""
        confidence_bin = int(confidence * 10) / 10

        if (
            category not in self.confidence_bins
            or confidence_bin not in self.confidence_bins[category]
        ):
            return 0.5  # Neutral if no data

        outcomes = self.confidence_bins[category][confidence_bin]
        if not outcomes:
            return 0.5

        return float(np.mean(outcomes))

    def _calculate_brier_score(
        self, confidences: List[float], outcomes: List[bool]
    ) -> float:
        """Calculate Brier score (mean squared error).

        Args:
            confidences: List of predicted confidences
            outcomes: List of actual outcomes (True/False)

        Returns:
            Brier score (0-1, lower is better)
        """
        if not confidences or len(confidences) != len(outcomes):
            return 1.0

        outcomes_float = np.array([float(o) for o in outcomes])
        confidences_array = np.array(confidences)

        squared_errors = (confidences_array - outcomes_float) ** 2
        brier = float(np.mean(squared_errors))

        return brier

    def get_metrics(self) -> Dict[str, Any]:
        """Get current calibration metrics.

        Returns:
            Metrics dict with Brier scores, accuracy, and bin data
        """
        overall_brier = 0.0
        if self.confidences_by_category.get("overall"):
            overall_brier = self._calculate_brier_score(
                self.confidences_by_category["overall"],
                self.outcomes_by_category["overall"],
            )

        # Category-specific metrics
        category_metrics: Dict[str, Dict[str, Any]] = {}
        for category in self.confidences_by_category:
            if category == "overall":
                continue

            brier = self._calculate_brier_score(
                self.confidences_by_category[category],
                self.outcomes_by_category[category],
            )

            accuracy = np.mean(self.outcomes_by_category[category])
            category_metrics[category] = {
                "brier_score": float(brier),
                "accuracy": float(accuracy),
                "sample_count": len(self.outcomes_by_category[category]),
            }

        return {
            "total_predictions": self.total_predictions,
            "overall_brier_score": float(overall_brier),
            "brier_score_trend": [float(b) for b in self.brier_history[-20:]],
            "target_brier_met": overall_brier < 0.15,
            "category_metrics": category_metrics,
            "confidence_bin_data": {
                cat: {float(k): float(np.mean(v)) for k, v in bins.items()}
                for cat, bins in self.confidence_bins.items()
            },
        }

    def _load_metrics(self) -> None:
        """Load historical calibration data."""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                self.confidences_by_category = defaultdict(
                    list, data.get("confidences_by_category", {})
                )
                self.outcomes_by_category = defaultdict(
                    list, data.get("outcomes_by_category", {})
                )
                self.total_predictions = data.get("total_predictions", 0)
                self.brier_history = data.get("brier_history", [])
        except Exception:
            pass  # Silently ignore load errors

    def save_metrics(self) -> None:
        """Save calibration metrics to disk."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "total_predictions": self.total_predictions,
            "confidences_by_category": dict(self.confidences_by_category),
            "outcomes_by_category": dict(self.outcomes_by_category),
            "brier_history": self.brier_history,
        }

        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2)

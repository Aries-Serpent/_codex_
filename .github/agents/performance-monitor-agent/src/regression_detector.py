"""
Regression Detector for Performance Agent
Detects performance regressions automatically
"""
import random
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

RANDOM_SEED = 47

@dataclass
class PerformanceBaseline:
    """Performance baseline snapshot"""
    timestamp: datetime
    metric_name: str
    value: float
    commit_sha: str

class RegressionDetector:
    """Detect performance regressions"""

    def __init__(self, seed: int = RANDOM_SEED):
        self.seed = seed
        self._rng = random.Random(seed)
        self.baselines: dict[str, PerformanceBaseline] = {}
        self.measurements: list[PerformanceBaseline] = []
        self.regression_threshold = 0.10  # 10% degradation
        self.initialized = True

    def set_baseline(
        self,
        metric_name: str,
        value: float,
        commit_sha: str = "baseline"
    ) -> None:
        """Set performance baseline"""
        baseline = PerformanceBaseline(
            timestamp=datetime.now(),
            metric_name=metric_name,
            value=value,
            commit_sha=commit_sha
        )
        self.baselines[metric_name] = baseline

    def measure(
        self,
        metric_name: str,
        value: float,
        commit_sha: str = "current"
    ) -> None:
        """Record performance measurement"""
        measurement = PerformanceBaseline(
            timestamp=datetime.now(),
            metric_name=metric_name,
            value=value,
            commit_sha=commit_sha
        )
        self.measurements.append(measurement)

    def detect_regression(self, metric_name: str) -> Optional[dict[str, Any]]:
        """Detect if metric has regressed"""
        if metric_name not in self.baselines:
            return None

        baseline = self.baselines[metric_name]
        recent_measurements = [
            m for m in self.measurements
            if m.metric_name == metric_name
        ]

        if not recent_measurements:
            return None

        current = recent_measurements[-1]

        # For latency/response time: higher is worse
        # For throughput: lower is worse
        if "latency" in metric_name.lower() or "time" in metric_name.lower():
            regression_ratio = (current.value - baseline.value) / baseline.value
            regressed = regression_ratio > self.regression_threshold
        else:  # Throughput-like metrics
            regression_ratio = (baseline.value - current.value) / baseline.value
            regressed = regression_ratio > self.regression_threshold

        if regressed:
            return {
                "metric": metric_name,
                "baseline_value": baseline.value,
                "current_value": current.value,
                "degradation_percent": abs(regression_ratio) * 100,
                "baseline_commit": baseline.commit_sha,
                "current_commit": current.commit_sha,
                "regressed": True
            }

        return None

    def check_all_metrics(self) -> list[dict[str, Any]]:
        """Check all metrics for regressions"""
        regressions = []
        for metric_name in self.baselines.keys():
            regression = self.detect_regression(metric_name)
            if regression:
                regressions.append(regression)
        return regressions

    def get_metrics(self) -> dict[str, Any]:
        """Get detector metrics"""
        return {
            "seed": self.seed,
            "baselines_count": len(self.baselines),
            "measurements_count": len(self.measurements),
            "regression_threshold": self.regression_threshold,
            "detected_regressions": len(self.check_all_metrics()),
            "regressions": self.check_all_metrics(),
            "initialized": self.initialized
        }


def create_detector(seed: int = RANDOM_SEED) -> RegressionDetector:
    """Factory function to create regression detector"""
    return RegressionDetector(seed=seed)

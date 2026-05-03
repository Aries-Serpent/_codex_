"""
ML Model Performance Tracker (PS-19c).

Track model metrics, detect regressions, and maintain performance history.

Usage:
    python scripts/monitoring/ml_model_tracker.py --status
    python scripts/monitoring/ml_model_tracker.py --json
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


@dataclass
class ModelMetrics:
    """Metrics for a single model evaluation."""

    model_name: str
    accuracy: float = 0.0
    latency_ms: float = 0.0
    throughput_rps: float = 0.0
    memory_mb: float = 0.0
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(tz=timezone.utc).isoformat()


@dataclass
class ModelPerformanceTracker:
    """Track and compare model performance over time."""

    history: list[ModelMetrics] = field(default_factory=list)
    thresholds: dict[str, float] = field(
        default_factory=lambda: {
            "accuracy_min": 0.85,
            "latency_max_ms": 100.0,
            "memory_max_mb": 512.0,
        }
    )

    def record(self, metrics: ModelMetrics) -> None:
        """Record a new set of metrics."""
        self.history.append(metrics)

    def check_regression(self, current: ModelMetrics) -> dict:
        """Check if current metrics show regression vs thresholds."""
        issues = []
        if current.accuracy < self.thresholds["accuracy_min"]:
            issues.append(
                f"Accuracy {current.accuracy:.3f} below threshold "
                f"{self.thresholds['accuracy_min']}"
            )
        if current.latency_ms > self.thresholds["latency_max_ms"]:
            issues.append(
                f"Latency {current.latency_ms:.1f}ms exceeds threshold "
                f"{self.thresholds['latency_max_ms']}ms"
            )
        if current.memory_mb > self.thresholds["memory_max_mb"]:
            issues.append(
                f"Memory {current.memory_mb:.0f}MB exceeds threshold "
                f"{self.thresholds['memory_max_mb']}MB"
            )
        return {
            "model": current.model_name,
            "status": "regression" if issues else "healthy",
            "issues": issues,
            "metrics": asdict(current),
        }

    def get_summary(self) -> dict:
        """Get performance summary."""
        if not self.history:
            return {"status": "no_data", "models": 0}
        models = {}
        for m in self.history:
            if m.model_name not in models:
                models[m.model_name] = []
            models[m.model_name].append(m)
        return {
            "status": "tracking",
            "total_records": len(self.history),
            "unique_models": len(models),
            "models": list(models.keys()),
            "thresholds": self.thresholds,
        }


def main() -> int:
    """CLI entry point."""
    tracker = ModelPerformanceTracker()

    # Example: record default RAG model metrics
    rag_metrics = ModelMetrics(
        model_name="all-MiniLM-L6-v2",
        accuracy=0.92,
        latency_ms=45.0,
        throughput_rps=22.0,
        memory_mb=256.0,
    )
    tracker.record(rag_metrics)

    if "--json" in sys.argv:
        data = {
            "summary": tracker.get_summary(),
            "regression_check": tracker.check_regression(rag_metrics),
        }
        print(json.dumps(data, indent=2, default=str))
        return 0

    if "--status" in sys.argv:
        check = tracker.check_regression(rag_metrics)
        print(f"Model: {check['model']}")
        print(f"Status: {check['status']}")
        if check["issues"]:
            for issue in check["issues"]:
                print(f"  ⚠️ {issue}")
        else:
            print("  ✅ All metrics within thresholds")
        return 0

    summary = tracker.get_summary()
    print("ML Model Performance Tracker")
    print(f"  Models: {summary['unique_models']}")
    print(f"  Records: {summary['total_records']}")
    print(f"  Status: {summary['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

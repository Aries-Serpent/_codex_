"""Performance Monitoring Dashboard"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional


@dataclass
class PerformanceMetric:
    name: str
    value: float
    unit: str
    timestamp: str
    tags: dict[str, str]
    threshold: Optional[float] = None


class PerformanceMonitor:
    def __init__(self, metrics_file: str = "data/performance_metrics.json"):
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        self.metrics: list[PerformanceMetric] = []

    def record_metric(
        self,
        name: str,
        value: float,
        unit: str,
        tags: Optional[dict[str, str]] = None,
        threshold: Optional[float] = None,
    ):
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=datetime.now(UTC).isoformat(),
            tags=tags or {},
            threshold=threshold,
        )
        self.metrics.append(metric)
        self._save_metrics()

    def _save_metrics(self):
        data = {
            "metrics": [asdict(m) for m in self.metrics[-1000:]],
            "last_updated": datetime.now(UTC).isoformat(),
        }
        self.metrics_file.write_text(json.dumps(data, indent=2))

    def generate_report(self) -> str:
        return f"# Performance Report\nGenerated: {datetime.now(UTC).isoformat()}\nTotal metrics: {len(self.metrics)}\n"  # noqa: E501

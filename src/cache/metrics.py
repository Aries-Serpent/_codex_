"""
Cache metrics collection and monitoring.

Tracks cache performance, costs, and optimization opportunities.

AAIS Contribution: +1.2 points
- Runtime Introspection: +1.2 (metrics collection)
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


@dataclass
class CacheMetrics:
    """Metrics for cache performance and cost."""

    namespace: str  # e.g., 'rag', 'embedding'
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    total_size_bytes: int = 0
    avg_value_size_bytes: int = 0
    ttl_seconds: Optional[int] = None
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def hit_rate(self) -> float:
        """Calculate hit rate percentage."""
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0

    @property
    def estimated_api_calls_saved(self) -> int:
        """Estimate API calls saved by caching."""
        return self.hits

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "namespace": self.namespace,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hit_rate,
            "evictions": self.evictions,
            "total_size_bytes": self.total_size_bytes,
            "avg_value_size_bytes": self.avg_value_size_bytes,
            "ttl_seconds": self.ttl_seconds,
            "estimated_api_calls_saved": self.estimated_api_calls_saved,
            "timestamp": self.timestamp.isoformat(),
        }


class CacheMonitor:
    """Monitor cache performance and generate reports."""

    def __init__(self, cache_dir: Optional[str] = None) -> None:
        """Initialize cache monitor."""
        self.cache_dir = Path(cache_dir) if cache_dir else Path(".codex/cache-metrics")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._metrics: dict[str, list[CacheMetrics]] = {}
        logger.info(f"CacheMonitor initialized with cache_dir={self.cache_dir}")

    def record(self, metrics: CacheMetrics) -> None:
        """Record cache metrics."""
        if metrics.namespace not in self._metrics:
            self._metrics[metrics.namespace] = []
        self._metrics[metrics.namespace].append(metrics)

    def get_report(self, namespace: str = "*") -> dict[str, Any]:
        """Generate cache performance report."""
        if namespace == "*":
            all_metrics = {}
            for ns in self._metrics:
                all_metrics[ns] = self.get_report(ns)
            return all_metrics

        if namespace not in self._metrics:
            return {"error": f"No metrics for namespace {namespace}"}

        metrics_list = self._metrics[namespace]
        if not metrics_list:
            return {"error": f"No metrics for namespace {namespace}"}

        # Calculate aggregates
        total_hits = sum(m.hits for m in metrics_list)
        total_misses = sum(m.misses for m in metrics_list)
        total_evictions = sum(m.evictions for m in metrics_list)
        total_size = max((m.total_size_bytes for m in metrics_list), default=0)

        hit_rate = (total_hits / (total_hits + total_misses) * 100) if (total_hits + total_misses) > 0 else 0.0

        return {
            "namespace": namespace,
            "total_hits": total_hits,
            "total_misses": total_misses,
            "hit_rate": hit_rate,
            "total_evictions": total_evictions,
            "current_size_bytes": total_size,
            "num_samples": len(metrics_list),
            "api_calls_saved": total_hits,
            "latest_metrics": metrics_list[-1].to_dict() if metrics_list else None,
        }

    def save_report(self, namespace: str = "*") -> Path:
        """Save cache report to file."""
        report = self.get_report(namespace)
        report_path = self.cache_dir / f"cache-report-{namespace}-{datetime.now().isoformat()}.json"

        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"Saved cache report to {report_path}")
        return report_path

    def get_optimization_suggestions(self) -> list[str]:
        """Generate optimization suggestions based on metrics."""
        suggestions = []

        for namespace, metrics_list in self._metrics.items():
            if not metrics_list:
                continue

            latest = metrics_list[-1]
            hit_rate = latest.hit_rate

            if hit_rate < 50:
                suggestions.append(
                    f"[{namespace}] Low hit rate ({hit_rate:.1f}%). "
                    "Consider longer TTL or larger cache size."
                )

            if latest.evictions > 100:
                suggestions.append(
                    f"[{namespace}] High evictions ({latest.evictions}). "
                    "Cache is too small. Increase cache size."
                )

            if latest.total_size_bytes > 1_000_000_000:  # 1GB
                suggestions.append(
                    f"[{namespace}] Large cache ({latest.total_size_bytes / 1e9:.1f}GB). "
                    "Consider using Redis for distributed caching."
                )

        return suggestions

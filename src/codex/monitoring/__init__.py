"""Monitoring module - re-exports from aries_serpent_core."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aries_serpent_core.monitoring import (
        Counter as Counter,
        Histogram as Histogram,
        PerformanceMonitor as PerformanceMonitor,
        PerformanceSnapshot as PerformanceSnapshot,
        PerformanceThresholds as PerformanceThresholds,
        metrics as metrics,
    )
else:
    try:
        from aries_serpent_core.monitoring import (
            Counter,
            Histogram,
            PerformanceMonitor,
            PerformanceSnapshot,
            PerformanceThresholds,
            metrics,
        )
    except ImportError:
        # Fallback implementations if not available.
        class Counter:
            def __init__(self, name, description="", unit=None):
                self.name = name
                self.description = description
                self.unit = unit
                self.value = 0

            def increment(self, amount=1):
                self.value += amount

            def snapshot(self):
                return {"name": self.name, "value": self.value}

        class Histogram:
            """Histogram metric for monitoring."""

            def __init__(self, name, help_text="", buckets=None):
                self.name = name
                self.help_text = help_text
                self.buckets = buckets or []
                self._values = []

            def observe(self, value):
                self._values.append(value)

            def snapshot(self):
                return {"name": self.name, "count": len(self._values), "sum": sum(self._values)}

        class PerformanceSnapshot:
            """Performance metrics snapshot."""

            def __init__(self):
                self.metrics = {}

        class PerformanceMonitor:
            def __init__(self, *args, **kwargs):
                self._snapshots = []

        class PerformanceThresholds:
            def __init__(self, *args, **kwargs):
                pass

        class _FallbackMetricsRegistry:
            def __init__(self):
                self._metrics = {}

            def register(self, metric):
                self._metrics[metric.name] = metric

            def get(self, name):
                return self._metrics.get(name)

            def emit_counter(self, name, amount=1):
                metric = self.get(name)
                if metric is None:
                    raise KeyError(name)
                if isinstance(metric, Counter):
                    metric.increment(amount)
                    return
                raise TypeError(f"Metric '{name}' is not a counter")

            def registered(self):
                return self._metrics.values()

        metrics = _FallbackMetricsRegistry()

__all__ = [
    "Counter",
    "Histogram",
    "PerformanceMonitor",
    "PerformanceSnapshot",
    "PerformanceThresholds",
    "metrics",
]

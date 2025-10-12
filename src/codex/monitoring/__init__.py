"""Minimal monitoring registry used by Zendesk integrations."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from statistics import mean


@dataclass
class _Metric:
    """Base representation for a metric instrument."""

    name: str
    description: str
    unit: str | None = None

    def snapshot(self) -> dict[str, object]:  # pragma: no cover - simple accessors
        return {
            "name": self.name,
            "description": self.description,
            "unit": self.unit,
        }


@dataclass
class Counter(_Metric):
    """Monotonic counter tracking increment operations."""

    value: int = 0

    def increment(self, amount: int = 1) -> None:
        self.value += amount

    def snapshot(self) -> dict[str, object]:  # pragma: no cover - simple accessors
        data = super().snapshot()
        data["value"] = self.value
        return data


@dataclass
class Histogram(_Metric):
    """Histogram collecting observed numeric values."""

    _observations: list[float] = field(default_factory=list)

    def observe(self, value: float) -> None:
        self._observations.append(float(value))

    def snapshot(self) -> dict[str, object]:  # pragma: no cover - simple accessors
        data = super().snapshot()
        if not self._observations:
            stats: dict[str, float] = {"count": 0, "sum": 0.0}
        else:
            stats = {
                "count": len(self._observations),
                "sum": float(sum(self._observations)),
                "avg": float(mean(self._observations)),
            }
        data.update(stats)
        return data


class _MetricRegistry:
    """In-memory registry for metric instruments."""

    def __init__(self) -> None:
        self._metrics: dict[str, _Metric] = {}

    def register(self, metric: _Metric) -> None:
        self._metrics[metric.name] = metric

    def get(self, name: str) -> _Metric | None:
        return self._metrics.get(name)

    def registered(self) -> Iterable[_Metric]:  # pragma: no cover - simple iterator
        return self._metrics.values()

    def emit_counter(self, name: str, amount: int = 1) -> None:
        metric = self.get(name)
        if isinstance(metric, Counter):
            metric.increment(amount)
            return
        raise KeyError(name)


metrics = _MetricRegistry()

__all__ = ["Counter", "Histogram", "metrics"]

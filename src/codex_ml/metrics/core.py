"""Lightweight metric registry for codex tooling.

This module provides a small registry abstraction that can be reused by
standalone tools (for example, metrics evaluation scripts) without pulling in
heavier ML dependencies. Two basic metrics are included by default:

- ``accuracy``: proportion of matching labels and predictions
- ``mse``: mean squared error over numeric labels and predictions

The registry is intentionally minimal and should remain dependency-light to
keep tooling runnable in constrained environments.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass

Number = float | int


@dataclass
class Metric:
    """Definition for a metric.

    Attributes:
        name: Unique name used to reference the metric.
        func: Callable accepting sequences of labels and predictions.
        description: Human-friendly description of the metric.
    """

    name: str
    func: Callable[[Sequence[Number], Sequence[Number]], float]
    description: str = ""


class MetricRegistry:
    """Simple registry that stores callable metrics by name."""

    def __init__(self) -> None:
        self._metrics: MutableMapping[str, Metric] = {}

    def register(self, metric: Metric) -> None:
        self._metrics[metric.name] = metric

    def get(self, name: str) -> Metric:
        if name not in self._metrics:
            raise KeyError(f"Unknown metric: {name}")
        return self._metrics[name]

    def list_metrics(self) -> list[str]:
        return sorted(self._metrics.keys())

    def compute(
        self,
        names: Iterable[str],
        labels: Sequence[Number],
        predictions: Sequence[Number],
    ) -> dict[str, float | None]:
        results: dict[str, float | None] = {}
        for name in names:
            metric = self.get(name)
            if len(labels) == 0:
                results[name] = None
            else:
                results[name] = metric.func(labels, predictions)
        return results


_REGISTRY: MetricRegistry | None = None


def _accuracy(labels: Sequence[Number], predictions: Sequence[Number]) -> float:
    matched = 0
    total = min(len(labels), len(predictions))
    for truth, pred in zip(labels, predictions, strict=False):
        if truth == pred:
            matched += 1
    return matched / total if total else 0.0


def _mse(labels: Sequence[Number], predictions: Sequence[Number]) -> float:
    total = min(len(labels), len(predictions))
    if total == 0:
        return 0.0
    squared_error = 0.0
    for truth, pred in zip(labels, predictions, strict=False):
        diff = float(truth) - float(pred)
        squared_error += diff * diff
    return squared_error / total


def _init_default_registry() -> MetricRegistry:
    registry = MetricRegistry()
    registry.register(
        Metric(
            name="accuracy",
            func=_accuracy,
            description="Proportion of matching labels and predictions.",
        )
    )
    registry.register(
        Metric(
            name="mse",
            func=_mse,
            description="Mean squared error over numeric targets.",
        )
    )
    return registry


def get_registry() -> MetricRegistry:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = _init_default_registry()
    return _REGISTRY


def list_metrics() -> list[str]:
    return get_registry().list_metrics()


def compute_metrics(
    metric_names: Iterable[str], labels: Sequence[Number], predictions: Sequence[Number]
) -> Mapping[str, float | None]:
    registry = get_registry()
    return registry.compute(metric_names, labels, predictions)

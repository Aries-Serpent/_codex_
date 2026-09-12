"""Lazy adapters for existing Codex ML evaluation APIs."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from importlib import import_module
from typing import TypeAlias

from .contracts import MetricInput

MetricLoader: TypeAlias = Callable[[str], Callable[..., object]]


def _codex_metric_loader(name: str) -> Callable[..., object]:
    module = import_module("codex_ml.metrics")
    loader = getattr(module, "get_metric")
    return loader(name)


class CodexMetricAdapter:
    """Adapt a lazily resolved ``codex_ml`` metric to the scalar contract."""

    def __init__(self, name: str, *, loader: MetricLoader | None = None) -> None:
        if not name.strip():
            raise ValueError("metric name must not be empty")
        self.name = name
        self._loader = loader or _codex_metric_loader
        self._metric: Callable[..., object] | None = None

    def __call__(
        self,
        predictions: Sequence[MetricInput],
        references: Sequence[MetricInput],
    ) -> float:
        if self._metric is None:
            self._metric = self._loader(self.name)
        return float(self._metric(predictions, references))


__all__ = ["CodexMetricAdapter", "MetricLoader"]

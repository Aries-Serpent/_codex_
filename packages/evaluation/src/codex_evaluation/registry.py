"""Small explicit registry for scalar metric contracts."""

from __future__ import annotations

from collections.abc import Iterator, Mapping

from .contracts import Metric


class MetricRegistrationError(ValueError):
    """Raised for an invalid or conflicting metric registration."""


class MetricRegistry(Mapping[str, Metric]):
    """An instance-local metric registry with deterministic iteration."""

    def __init__(self) -> None:
        self._metrics: dict[str, Metric] = {}

    def register(self, name: str, metric: Metric, *, replace: bool = False) -> None:
        normalized = name.strip()
        if not normalized:
            raise MetricRegistrationError("metric name must not be empty")
        if not callable(metric):
            raise MetricRegistrationError(f"metric {normalized!r} must be callable")
        if normalized in self._metrics and not replace:
            raise MetricRegistrationError(f"metric {normalized!r} is already registered")
        self._metrics[normalized] = metric

    def __getitem__(self, name: str) -> Metric:
        try:
            return self._metrics[name]
        except KeyError as exc:
            raise KeyError(f"unknown metric: {name}") from exc

    def __iter__(self) -> Iterator[str]:
        return iter(sorted(self._metrics))

    def __len__(self) -> int:
        return len(self._metrics)


__all__ = ["MetricRegistrationError", "MetricRegistry"]

"""Stable, dependency-free evaluation contracts."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Protocol, TypeAlias, runtime_checkable

MetricInput: TypeAlias = object


@dataclass(frozen=True, slots=True)
class EvaluationBatch:
    """A validated batch passed to scalar evaluation metrics."""

    predictions: Sequence[MetricInput]
    references: Sequence[MetricInput]
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        predictions = tuple(self.predictions)
        references = tuple(self.references)
        if len(predictions) != len(references):
            raise ValueError("predictions and references must have the same length")
        object.__setattr__(self, "predictions", predictions)
        object.__setattr__(self, "references", references)
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    @property
    def sample_count(self) -> int:
        return len(self.predictions)


@runtime_checkable
class Metric(Protocol):
    """Structural contract for a named scalar metric."""

    def __call__(
        self,
        predictions: Sequence[MetricInput],
        references: Sequence[MetricInput],
    ) -> float: ...


@dataclass(frozen=True, slots=True)
class EvaluationReport:
    """Immutable scalar metric output for one evaluation batch."""

    sample_count: int
    metrics: Mapping[str, float]
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.sample_count < 0:
            raise ValueError("sample_count must be non-negative")
        object.__setattr__(self, "metrics", MappingProxyType(dict(self.metrics)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@runtime_checkable
class Evaluator(Protocol):
    """Structural contract implemented by evaluation engines."""

    def evaluate(self, batch: EvaluationBatch) -> EvaluationReport: ...


__all__ = ["EvaluationBatch", "EvaluationReport", "Evaluator", "Metric", "MetricInput"]

"""Stable, dependency-free evaluation contracts."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Protocol, TypeAlias, runtime_checkable

MetricInput: TypeAlias = object
DistributionValue: TypeAlias = int | float


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


@dataclass(frozen=True, slots=True)
class DriftBatch:
    """A pair of aligned distributions used for deterministic drift checks."""

    reference: Sequence[DistributionValue]
    current: Sequence[DistributionValue]
    feature_name: str = "feature"
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        reference = tuple(float(value) for value in self.reference)
        current = tuple(float(value) for value in self.current)
        if not reference or not current:
            raise ValueError("drift distributions must not be empty")
        if len(reference) != len(current):
            raise ValueError("reference and current distributions must have the same length")
        if any(not math.isfinite(value) or value < 0 for value in (*reference, *current)):
            raise ValueError("drift distributions must contain finite, non-negative values")
        if sum(reference) <= 0 or sum(current) <= 0:
            raise ValueError("drift distributions must each have a positive total")
        if not self.feature_name.strip():
            raise ValueError("feature_name must not be empty")
        object.__setattr__(self, "reference", reference)
        object.__setattr__(self, "current", current)
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@dataclass(frozen=True, slots=True)
class DriftReport:
    """Immutable result from one drift evaluation."""

    method: str
    score: float
    threshold: float
    drifted: bool
    feature_name: str = "feature"
    details: Mapping[str, object] = field(default_factory=dict)
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.method.strip():
            raise ValueError("method must not be empty")
        if not math.isfinite(self.score) or self.score < 0:
            raise ValueError("score must be finite and non-negative")
        if not math.isfinite(self.threshold) or self.threshold < 0:
            raise ValueError("threshold must be finite and non-negative")
        object.__setattr__(self, "details", MappingProxyType(dict(self.details)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


@runtime_checkable
class DriftEvaluator(Protocol):
    """Structural contract for dependency-free drift evaluators."""

    def evaluate(self, batch: DriftBatch) -> DriftReport: ...


__all__ = [
    "DistributionValue",
    "DriftBatch",
    "DriftEvaluator",
    "DriftReport",
    "EvaluationBatch",
    "EvaluationReport",
    "Evaluator",
    "Metric",
    "MetricInput",
]

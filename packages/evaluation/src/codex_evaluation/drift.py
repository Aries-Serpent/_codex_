"""Dependency-free distribution drift evaluators."""

from __future__ import annotations

import math
from collections.abc import Sequence

from .contracts import DistributionValue, DriftBatch, DriftReport


def _normalise(
    values: Sequence[DistributionValue],
    *,
    epsilon: float,
) -> tuple[float, ...]:
    smoothed = tuple(float(value) + epsilon for value in values)
    total = math.fsum(smoothed)
    return tuple(value / total for value in smoothed)


class PopulationStabilityIndex:
    """Evaluate Population Stability Index (PSI) for aligned distributions."""

    method = "psi"

    def __init__(self, *, threshold: float = 0.2, epsilon: float = 1e-8) -> None:
        if not math.isfinite(threshold) or threshold < 0:
            raise ValueError("threshold must be finite and non-negative")
        if not math.isfinite(epsilon) or epsilon <= 0:
            raise ValueError("epsilon must be finite and positive")
        self.threshold = float(threshold)
        self.epsilon = float(epsilon)

    def evaluate(self, batch: DriftBatch) -> DriftReport:
        reference = _normalise(batch.reference, epsilon=self.epsilon)
        current = _normalise(batch.current, epsilon=self.epsilon)
        bin_scores = tuple(
            (observed - expected) * math.log(observed / expected)
            for expected, observed in zip(reference, current)
        )
        score = math.fsum(bin_scores)
        return DriftReport(
            method=self.method,
            score=score,
            threshold=self.threshold,
            drifted=score > self.threshold,
            feature_name=batch.feature_name,
            details={
                "bin_scores": bin_scores,
                "current_distribution": current,
                "reference_distribution": reference,
            },
            metadata=batch.metadata,
        )


class KullbackLeiblerDivergence:
    """Evaluate ``KL(current || reference)`` for aligned distributions."""

    method = "kl"

    def __init__(self, *, threshold: float = 0.5, epsilon: float = 1e-8) -> None:
        if not math.isfinite(threshold) or threshold < 0:
            raise ValueError("threshold must be finite and non-negative")
        if not math.isfinite(epsilon) or epsilon <= 0:
            raise ValueError("epsilon must be finite and positive")
        self.threshold = float(threshold)
        self.epsilon = float(epsilon)

    def evaluate(self, batch: DriftBatch) -> DriftReport:
        reference = _normalise(batch.reference, epsilon=self.epsilon)
        current = _normalise(batch.current, epsilon=self.epsilon)
        bin_scores = tuple(
            observed * math.log(observed / expected)
            for expected, observed in zip(reference, current)
        )
        # Floating-point cancellation can produce a tiny negative value for equal
        # distributions. Divergence is mathematically non-negative.
        score = max(0.0, math.fsum(bin_scores))
        return DriftReport(
            method=self.method,
            score=score,
            threshold=self.threshold,
            drifted=score > self.threshold,
            feature_name=batch.feature_name,
            details={
                "bin_scores": bin_scores,
                "current_distribution": current,
                "reference_distribution": reference,
            },
            metadata=batch.metadata,
        )


__all__ = ["KullbackLeiblerDivergence", "PopulationStabilityIndex"]

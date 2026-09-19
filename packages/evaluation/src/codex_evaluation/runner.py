"""Framework-neutral evaluation orchestration."""

from __future__ import annotations

import math
from collections.abc import Mapping

from .contracts import EvaluationBatch, EvaluationReport, Metric


class EvaluationError(RuntimeError):
    """Raised when a metric violates the scalar evaluation contract."""


class EvaluationRunner:
    """Evaluate a batch with explicitly supplied metrics."""

    def __init__(self, metrics: Mapping[str, Metric]) -> None:
        self._metrics = dict(metrics)

    def evaluate(self, batch: EvaluationBatch) -> EvaluationReport:
        values: dict[str, float] = {}
        for name, metric in self._metrics.items():
            raw_value = metric(batch.predictions, batch.references)
            if isinstance(raw_value, bool):
                raise EvaluationError(f"metric {name!r} returned bool, expected a scalar")
            try:
                value = float(raw_value)
            except (TypeError, ValueError) as exc:
                raise EvaluationError(f"metric {name!r} did not return a scalar") from exc
            if not math.isfinite(value):
                raise EvaluationError(f"metric {name!r} returned a non-finite value")
            values[name] = value
        return EvaluationReport(batch.sample_count, values, batch.metadata)


__all__ = ["EvaluationError", "EvaluationRunner"]

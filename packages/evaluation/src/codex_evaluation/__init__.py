"""Public API for the standalone Codex evaluation boundary."""

from .__about__ import __version__
from .adapters import CodexMetricAdapter, MetricLoader
from .contracts import EvaluationBatch, EvaluationReport, Evaluator, Metric, MetricInput
from .registry import MetricRegistrationError, MetricRegistry
from .runner import EvaluationError, EvaluationRunner

__all__ = [
    "CodexMetricAdapter",
    "EvaluationBatch",
    "EvaluationError",
    "EvaluationReport",
    "EvaluationRunner",
    "Evaluator",
    "Metric",
    "MetricInput",
    "MetricLoader",
    "MetricRegistrationError",
    "MetricRegistry",
    "__version__",
]

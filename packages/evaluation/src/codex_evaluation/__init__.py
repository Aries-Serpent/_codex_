"""Public API for the standalone Codex evaluation boundary."""

from .__about__ import __version__
from .adapters import (
    CodexMetricAdapter,
    DatasetLoader,
    EvaluateMetricAdapter,
    FrameworkMetricLoader,
    HuggingFaceDatasetAdapter,
    MetricLoader,
    OptionalDependencyError,
)
from .contracts import (
    DistributionValue,
    DriftBatch,
    DriftEvaluator,
    DriftReport,
    EvaluationBatch,
    EvaluationReport,
    Evaluator,
    Metric,
    MetricInput,
)
from .drift import KullbackLeiblerDivergence, PopulationStabilityIndex
from .registry import MetricRegistrationError, MetricRegistry
from .runner import EvaluationError, EvaluationRunner

__all__ = [
    "CodexMetricAdapter",
    "DatasetLoader",
    "DistributionValue",
    "DriftBatch",
    "DriftEvaluator",
    "DriftReport",
    "EvaluateMetricAdapter",
    "EvaluationBatch",
    "EvaluationError",
    "EvaluationReport",
    "EvaluationRunner",
    "Evaluator",
    "FrameworkMetricLoader",
    "HuggingFaceDatasetAdapter",
    "KullbackLeiblerDivergence",
    "Metric",
    "MetricInput",
    "MetricLoader",
    "MetricRegistrationError",
    "MetricRegistry",
    "OptionalDependencyError",
    "PopulationStabilityIndex",
    "__version__",
]

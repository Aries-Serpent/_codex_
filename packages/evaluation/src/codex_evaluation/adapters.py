"""Lazy adapters for optional dataset and evaluation frameworks."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from importlib import import_module
from typing import TypeAlias

from .contracts import MetricInput

MetricLoader: TypeAlias = Callable[[str], Callable[..., object]]
DatasetLoader: TypeAlias = Callable[..., object]
FrameworkMetricLoader: TypeAlias = Callable[[str], object]


class OptionalDependencyError(ImportError):
    """Raised only when an adapter's optional backend is requested."""


def _codex_metric_loader(name: str) -> Callable[..., object]:
    module = import_module("codex_ml.metrics")
    loader = getattr(module, "get_metric")
    return loader(name)


def _datasets_loader(*args: object, **kwargs: object) -> object:
    try:
        module = import_module("datasets")
        loader = getattr(module, "load_dataset")
    except (ImportError, AttributeError) as exc:
        raise OptionalDependencyError(
            "dataset support requires the 'hf' extra: "
            "pip install codex-ml-evaluation[hf]"
        ) from exc
    return loader(*args, **kwargs)


def _evaluate_metric_loader(name: str) -> object:
    try:
        module = import_module("evaluate")
        loader = getattr(module, "load")
    except (ImportError, AttributeError) as exc:
        raise OptionalDependencyError(
            "framework metric support requires the 'framework' extra: "
            "pip install codex-ml-evaluation[framework]"
        ) from exc
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


class HuggingFaceDatasetAdapter:
    """Load a Hugging Face dataset lazily and convert one split to a batch."""

    def __init__(self, *, loader: DatasetLoader | None = None) -> None:
        self._loader = loader or _datasets_loader

    def load(
        self,
        path: str,
        *,
        split: str = "test",
        prediction_field: str = "prediction",
        reference_field: str = "reference",
        **kwargs: object,
    ):
        from .contracts import EvaluationBatch

        if not path.strip():
            raise ValueError("dataset path must not be empty")
        if not prediction_field.strip() or not reference_field.strip():
            raise ValueError("dataset field names must not be empty")
        dataset = self._loader(path, split=split, **kwargs)
        try:
            rows = list(dataset)  # type: ignore[arg-type]
            predictions = [row[prediction_field] for row in rows]
            references = [row[reference_field] for row in rows]
        except (KeyError, TypeError) as exc:
            raise ValueError(
                f"dataset rows must expose {prediction_field!r} and {reference_field!r}"
            ) from exc
        return EvaluationBatch(
            predictions,
            references,
            {"dataset": path, "split": split},
        )


class EvaluateMetricAdapter:
    """Adapt a lazily loaded ``evaluate`` metric to the scalar contract."""

    def __init__(
        self,
        name: str,
        *,
        result_key: str | None = None,
        loader: FrameworkMetricLoader | None = None,
    ) -> None:
        if not name.strip():
            raise ValueError("metric name must not be empty")
        self.name = name
        self.result_key = result_key or name
        self._loader = loader or _evaluate_metric_loader
        self._metric: object | None = None

    def __call__(
        self,
        predictions: Sequence[MetricInput],
        references: Sequence[MetricInput],
    ) -> float:
        if self._metric is None:
            self._metric = self._loader(self.name)
        compute = getattr(self._metric, "compute", None)
        if not callable(compute):
            raise TypeError(f"framework metric {self.name!r} does not expose compute()")
        result = compute(predictions=list(predictions), references=list(references))
        if not isinstance(result, Mapping):
            raise TypeError(f"framework metric {self.name!r} did not return a mapping")
        try:
            return float(result[self.result_key])
        except KeyError as exc:
            raise KeyError(
                f"framework metric {self.name!r} did not return {self.result_key!r}"
            ) from exc


__all__ = [
    "CodexMetricAdapter",
    "DatasetLoader",
    "EvaluateMetricAdapter",
    "FrameworkMetricLoader",
    "HuggingFaceDatasetAdapter",
    "MetricLoader",
    "OptionalDependencyError",
]

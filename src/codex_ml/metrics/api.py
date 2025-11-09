"""Public metrics facade for codex_ml."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Dict

from .metric_implementations import (
    BLEUScore,
    F1Score,
    MetricBase,
    MetricRegistry,
    RecallScore,
    TokenAccuracy,
)

__all__ = [
    "MetricBase",
    "MetricRegistry",
    "F1Score",
    "RecallScore",
    "BLEUScore",
    "TokenAccuracy",
    "get_metric",
    "register_metric",
    "list_metrics",
    "summarize_ndjson_logs",
]


_GLOBAL_REGISTRY = MetricRegistry()
_GLOBAL_REGISTRY.register("f1", F1Score, average="weighted")
_GLOBAL_REGISTRY.register("f1_weighted", F1Score, average="weighted")
_GLOBAL_REGISTRY.register("f1_macro", F1Score, average="macro")
_GLOBAL_REGISTRY.register("f1_micro", F1Score, average="micro")
_GLOBAL_REGISTRY.register("recall", RecallScore, average="weighted")
_GLOBAL_REGISTRY.register("recall_macro", RecallScore, average="macro")
_GLOBAL_REGISTRY.register("recall_micro", RecallScore, average="micro")
_GLOBAL_REGISTRY.register("token_accuracy", TokenAccuracy)
_GLOBAL_REGISTRY.register("bleu", BLEUScore)


def register_metric(name: str, metric_cls: type[MetricBase], **default_kwargs: Any) -> None:
    """Register a metric implementation with optional default keyword arguments."""

    _GLOBAL_REGISTRY.register(name, metric_cls, **default_kwargs)


def get_metric(name: str, **overrides: Any) -> MetricBase:
    """Instantiate a metric from the global registry."""

    return _GLOBAL_REGISTRY.create(name, **overrides)


def list_metrics() -> list[str]:
    """Return the list of known metric names."""

    return _GLOBAL_REGISTRY.list()


def _extract_numeric(record: Mapping[str, Any], prefix: str = "") -> Dict[str, float]:
    metrics: Dict[str, float] = {}
    for key, value in record.items():
        namespaced = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
        if isinstance(value, Mapping):
            metrics.update(_extract_numeric(value, namespaced))
        elif isinstance(value, (int, float)):
            metrics[namespaced] = float(value)
    return metrics


def summarize_ndjson_logs(log_file: str | Path) -> Dict[str, float]:
    """Parse an NDJSON metrics log and compute mean values for numeric fields."""

    path = Path(log_file)
    if not path.exists():
        raise FileNotFoundError(f"metrics log not found: {path}")

    aggregates: Dict[str, list[float]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for index, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                payload = json.loads(text)
            except json.JSONDecodeError as exc:  # pragma: no cover - validation path
                raise ValueError(f"invalid JSON on line {index}: {exc.msg}") from exc
            if not isinstance(payload, Mapping):
                raise ValueError(f"expected JSON object on line {index}")
            numeric = _extract_numeric(payload)
            if not numeric:
                continue
            for key, value in numeric.items():
                aggregates.setdefault(key, []).append(value)

    return {key: sum(values) / len(values) for key, values in aggregates.items() if values}

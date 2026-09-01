"""
Metric Implementations Module

This module provides functionality for metric implementations.

Usage:
    from metrics.metric_implementations import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


import json  # noqa: E402
import math  # noqa: E402
from abc import ABC, abstractmethod  # noqa: E402
from collections import Counter  # noqa: E402
from collections.abc import Iterable, Mapping, Sequence  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

try:  # pragma: no cover - optional dependency
    import torch
except (IOError, OSError, ModuleNotFoundError, ImportError):  # pragma: no cover - environments without torch
    torch = None


def _to_flat_list(values: Any) -> list[Any]:
    """Convert tensors or iterables into a flat list for metric computation."""

    if torch is not None and isinstance(values, torch.Tensor):  # pragma: no branch
        return values.detach().cpu().flatten().tolist()
    if isinstance(values, Sequence) and not isinstance(values, (str, bytes)):
        flattened: list[Any] = []
        for item in values:
            if isinstance(item, Sequence) and not isinstance(item, (str, bytes)):
                flattened.extend(_to_flat_list(item))
            else:
                flattened.append(item)
        return flattened
    if isinstance(values, Iterable) and not isinstance(values, (str, bytes)):
        return [item for item in values]
    return [values]


class MetricBase(ABC):
    """Abstract base class for stateful metrics."""

    name: str

    def __init__(self, name: str) -> None:
        self.name = name
        # Note: reset() is not called here to avoid calling overridden methods
        # before subclass initialization is complete. Subclasses should initialize
        # their state in their own __init__ methods.

    @abstractmethod
    def update(self, predictions: Any, targets: Any) -> None:
        """Update internal state with a batch of predictions and targets."""

    @abstractmethod
    def compute(self) -> dict[str, float]:
        """Return the computed metric values."""

    def reset(self) -> None:
        """Reset internal accumulators."""


class _ClassificationStats:
    def __init__(self) -> None:
        self.tp: Counter[int] = Counter()
        self.fp: Counter[int] = Counter()
        self.fn: Counter[int] = Counter()
        self.support: Counter[int] = Counter()

    def update(self, preds: Iterable[int], targets: Iterable[int]) -> None:
        for pred, target in zip(preds, targets, strict=False):
            pred_i = int(pred)
            target_i = int(target)
            if pred_i == target_i:
                self.tp[target_i] += 1
            else:
                self.fp[pred_i] += 1
                self.fn[target_i] += 1
            self.support[target_i] += 1

    def precision(self, label: int) -> float:
        denom = self.tp[label] + self.fp[label]
        if denom == 0:
            return 0.0
        return self.tp[label] / denom

    def recall(self, label: int) -> float:
        denom = self.tp[label] + self.fn[label]
        if denom == 0:
            return 0.0
        return self.tp[label] / denom

    def labels(self) -> list[int]:
        observed = (
            set(self.support.keys())
            | set(self.tp.keys())
            | set(self.fp.keys())
            | set(self.fn.keys())
        )
        if not observed:
            return [1]
        return sorted(observed)

    def total(self) -> int:
        return sum(self.support.values())


def _average(values: list[float], weights: list[int] | None) -> float:
    if not values:
        return 0.0
    if weights and sum(weights) > 0:
        weighted_sum = sum(v * w for v, w in zip(values, weights, strict=False))
        return weighted_sum / sum(weights)
    return sum(values) / len(values)


class F1Score(MetricBase):
    """Weighted/macro/micro F1 score for classification tasks."""

    def __init__(self, num_classes: int | None = None, average: str = "weighted") -> None:
        self.num_classes = num_classes
        self.average = average
        self._stats = _ClassificationStats()
        super().__init__("f1_score")

    def reset(self) -> None:
        self._stats = _ClassificationStats()

    def update(self, predictions: Any, targets: Any) -> None:
        preds = [int(p) for p in _to_flat_list(predictions)]
        labels = [int(t) for t in _to_flat_list(targets)]
        self._stats.update(preds, labels)

    def compute(self) -> dict[str, float]:
        labels = self._stats.labels()
        precisions = [self._stats.precision(label) for label in labels]
        recalls = [self._stats.recall(label) for label in labels]
        f1_scores = []
        supports = [self._stats.support[label] for label in labels]
        for precision, recall in zip(precisions, recalls, strict=False):
            denom = precision + recall
            f1_scores.append(0.0 if denom == 0 else 2 * precision * recall / denom)

        match self.average:
            case "micro":
                tp = sum(self._stats.tp[label] for label in labels)
                fp = sum(self._stats.fp[label] for label in labels)
                fn = sum(self._stats.fn[label] for label in labels)
                if tp == 0:
                    score = 0.0
                else:
                    precision = tp / max(tp + fp, 1)
                    recall = tp / max(tp + fn, 1)
                    denom_small = precision + recall
                    score = 0.0 if denom_small == 0 else 2 * precision * recall / denom_small
                return {self.name: score}
            case "macro":
                return {self.name: _average(f1_scores, None)}
            case "weighted":
                return {self.name: _average(f1_scores, supports)}
            case "binary":
                positive = 1 if self.num_classes in {None, 2} else labels[-1]
                try:
                    idx = labels.index(positive)
                except ValueError as e:
                    type(e).__name__
                    logger.debug("ValueError: <ERROR_TYPE>")
                    logger.warning("ValueError: <ERROR_TYPE>", exc_info=True)
                    return {self.name: 0.0}
                return {self.name: f1_scores[idx]}
            case _:
                raise ValueError(f"unsupported averaging strategy: {self.average}")

        raise RuntimeError("unreachable: compute() exhausted all averaging strategies")


class RecallScore(MetricBase):
    """Recall metric supporting multiple averaging strategies."""

    def __init__(self, num_classes: int | None = None, average: str = "weighted") -> None:
        self.num_classes = num_classes
        self.average = average
        self._stats = _ClassificationStats()
        super().__init__("recall_score")

    def reset(self) -> None:
        self._stats = _ClassificationStats()

    def update(self, predictions: Any, targets: Any) -> None:
        preds = [int(p) for p in _to_flat_list(predictions)]
        labels = [int(t) for t in _to_flat_list(targets)]
        self._stats.update(preds, labels)

    def compute(self) -> dict[str, float]:
        labels = self._stats.labels()
        recalls = [self._stats.recall(label) for label in labels]
        supports = [self._stats.support[label] for label in labels]
        score: float = 0.0

        match self.average:
            case "micro":
                tp = sum(self._stats.tp[label] for label in labels)
                fn = sum(self._stats.fn[label] for label in labels)
                denom = tp + fn
                score = 0.0 if denom == 0 else tp / denom
            case "macro":
                score = _average(recalls, None)
            case "weighted":
                score = _average(recalls, supports)
            case "binary":
                positive = 1 if self.num_classes in {None, 2} else labels[-1]
                try:
                    idx = labels.index(positive)
                except ValueError as e:
                    type(e).__name__
                    logger.debug("ValueError: <ERROR_TYPE>")
                    logger.warning("ValueError: <ERROR_TYPE>", exc_info=True)
                    score = 0.0
                else:
                    score = recalls[idx]
            case _:
                raise ValueError(f"unsupported averaging strategy: {self.average}")

        return {self.name: score}


class TokenAccuracy(MetricBase):
    """Token-level accuracy across arbitrary sequence lengths."""

    def __init__(self) -> None:
        self._correct = 0
        self._total = 0
        super().__init__("token_accuracy")

    def reset(self) -> None:
        self._correct = 0
        self._total = 0

    def update(self, predictions: Any, targets: Any) -> None:
        preds = _to_flat_list(predictions)
        labels = _to_flat_list(targets)
        total = min(len(preds), len(labels))
        correct = sum(int(preds[i] == labels[i]) for i in range(total))
        self._correct += correct
        self._total += total

    def compute(self) -> dict[str, float]:
        # If no samples have been processed, return 0.0 accuracy.
        # This behavior is tested in the empty input test case.
        if self._total == 0:
            return {self.name: 0.0}
        return {self.name: self._correct / self._total}


class BLEUScore(MetricBase):
    """Corpus-level BLEU score supporting arbitrary n-gram orders."""

    def __init__(self, n_gram: int = 4, smoothing: float = 1e-9) -> None:
        if n_gram < 1:
            raise ValueError("n_gram must be >= 1")
        self.n_gram = n_gram
        self.smoothing = smoothing
        self._matches = [0] * self.n_gram
        self._totals = [0] * self.n_gram
        self._pred_length = 0
        self._ref_length = 0
        super().__init__("bleu_score")

    def reset(self) -> None:
        self._matches = [0] * self.n_gram
        self._totals = [0] * self.n_gram
        self._pred_length = 0
        self._ref_length = 0

    def _ngrams(self, tokens: Sequence[Any], n: int) -> Counter[tuple[Any, ...]]:
        if len(tokens) < n:
            return Counter()
        return Counter(tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1))

    def update(self, predictions: Any, targets: Any) -> None:
        pred_sequences = _to_sequences(predictions)
        target_sequences = _to_sequences(targets)
        for pred, target in zip(pred_sequences, target_sequences, strict=False):
            pred_tokens = list(pred)
            target_tokens = list(target)
            self._pred_length += len(pred_tokens)
            self._ref_length += len(target_tokens)
            for n in range(1, self.n_gram + 1):
                pred_counts = self._ngrams(pred_tokens, n)
                target_counts = self._ngrams(target_tokens, n)
                matches = sum(
                    min(count, target_counts[gram]) for gram, count in pred_counts.items()
                )
                total = sum(pred_counts.values())
                self._matches[n - 1] += matches
                self._totals[n - 1] += total

    def compute(self) -> dict[str, float]:
        precisions = []
        for matches, total in zip(self._matches, self._totals, strict=False):
            if total == 0:
                precisions.append(0.0)
            else:
                precisions.append(matches / total)

        if not precisions or any(p <= 0 for p in precisions):
            return {self.name: 0.0, "brevity_penalty": 0.0}

        log_precision = sum(math.log(p + self.smoothing) for p in precisions) / self.n_gram
        geo_mean = math.exp(log_precision)
        if self._pred_length == 0:
            return {self.name: 0.0, "brevity_penalty": 0.0}
        brevity_penalty = 1.0
        if self._pred_length < self._ref_length:
            brevity_penalty = math.exp(1 - (self._ref_length / max(self._pred_length, 1)))
        bleu = brevity_penalty * geo_mean
        return {self.name: bleu, "brevity_penalty": brevity_penalty}


def _to_sequences(batch: Any) -> list[list[Any]]:
    if torch is not None and isinstance(batch, torch.Tensor):  # pragma: no branch
        if batch.ndim == 1:
            return [batch.detach().cpu().tolist()]
        return [row.detach().cpu().tolist() for row in batch]
    if isinstance(batch, Mapping):
        candidate = batch.get("input_ids") or batch.get("predictions")
        if candidate is not None:
            return _to_sequences(candidate)
    if isinstance(batch, Sequence) and batch and not isinstance(batch[0], (str, bytes, int, float)):
        return [list(seq) for seq in batch]
    if isinstance(batch, Sequence) and not isinstance(batch, (str, bytes)):
        return [list(batch)]
    return [[batch]]


@dataclass
class MetricSpec:
    """Configuration schema for the metric registry."""

    name: str
    factory: type[MetricBase]
    default_kwargs: dict[str, Any] | None = None


class MetricRegistry:
    """Simple factory/registry for metric implementations."""

    def __init__(self) -> None:
        self._registry: dict[str, MetricSpec] = {}

    def register(self, name: str, metric_cls: type[MetricBase], **default_kwargs: Any) -> None:
        key = name.strip().lower()
        if not key:
            raise ValueError("metric name must be non-empty")
        spec = MetricSpec(name=key, factory=metric_cls, default_kwargs=default_kwargs or None)
        self._registry[key] = spec

    def create(self, name: str, **overrides: Any) -> MetricBase:
        key = name.strip().lower()
        if key not in self._registry:
            raise KeyError(f"metric not registered: {name}")
        spec = self._registry[key]
        kwargs = dict(spec.default_kwargs or {})
        kwargs.update(overrides)
        return spec.factory(**kwargs)

    def list(self) -> list[str]:
        return sorted(self._registry.keys())


DEFAULT_METRICS = MetricRegistry()
DEFAULT_METRICS.register("f1", F1Score)
DEFAULT_METRICS.register("recall", RecallScore)
DEFAULT_METRICS.register("token_accuracy", TokenAccuracy)
DEFAULT_METRICS.register("bleu", BLEUScore)


def load_metrics_from_file(path: str | Path) -> dict[str, Any]:
    """Load metric instantiation parameters from a JSON file."""

    payload_path = Path(path)
    if not payload_path.exists():
        raise FileNotFoundError(f"metric specification file not found: {path}")
    data = json.loads(payload_path.read_text(encoding="utf-8"))
    if not isinstance(data, Mapping):
        raise ValueError("metric specification must be a mapping of metric_name -> kwargs")
    return dict(data)


__all__ = [
    "DEFAULT_METRICS",
    "BLEUScore",
    "F1Score",
    "MetricBase",
    "MetricRegistry",
    "RecallScore",
    "TokenAccuracy",
    "load_metrics_from_file",
]

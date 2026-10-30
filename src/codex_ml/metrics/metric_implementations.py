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
except (
    IOError,
    OSError,
    ModuleNotFoundError,
    ImportError,
):  # pragma: no cover - environments without torch
    torch = None  # type: ignore[assignment]


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
        """Discard accumulated classification counts without changing averaging options.

        Returns:
            None. Subsequent computation uses an empty observation set.
        """
        self._stats = _ClassificationStats()

    def update(self, predictions: Any, targets: Any) -> None:
        """Accumulate integer class predictions and corresponding target labels.

        Args:
            predictions: Class IDs, nested sequences, or optional torch tensors.
                Tensors are detached, moved to CPU, and flattened.
            targets: Labels in the same representation. Only paired entries up
                to the shorter flattened length contribute; logits are not decoded.

        Raises:
            TypeError: If an entry cannot be converted to an integer.
            ValueError: If an entry is not a valid integer representation.
        """
        preds = [int(p) for p in _to_flat_list(predictions)]
        labels = [int(t) for t in _to_flat_list(targets)]
        self._stats.update(preds, labels)

    def compute(self) -> dict[str, float]:
        """Return accumulated F1 as a mapping under ``f1_score`` without resetting.

        Supports micro, macro, support-weighted, and binary averaging. Binary
        selects label 1 when num_classes is None or 2, otherwise the greatest
        observed label. Missing positive labels and empty state produce zero.
        Other modes use observed labels, not a range derived from num_classes.

        Raises:
            ValueError: If the configured averaging strategy is unsupported.
        """
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
        """Clear true-positive, false-positive, false-negative, and support counts.

        Returns:
            None. The configured class count and averaging mode are retained.
        """
        self._stats = _ClassificationStats()

    def update(self, predictions: Any, targets: Any) -> None:
        """Add paired predicted and target integer IDs to the running counts.

        Args:
            predictions: Scalar IDs, nested sequences, or optional torch tensors;
                tensor inputs are detached and flattened on CPU, not argmaxed.
            targets: Corresponding labels. Unpaired trailing entries are ignored.

        Raises:
            TypeError: If a flattened entry cannot be converted to int.
            ValueError: If a flattened entry has an invalid integer value.
        """
        preds = [int(p) for p in _to_flat_list(predictions)]
        labels = [int(t) for t in _to_flat_list(targets)]
        self._stats.update(preds, labels)

    def compute(self) -> dict[str, float]:
        """Return ``recall_score`` for all updates, preserving accumulated state.

        Micro pools counts; macro averages observed labels; weighted uses target
        support. Binary chooses label 1 for num_classes None or 2, otherwise the
        greatest observed label. Empty state or an absent positive label gives
        zero; num_classes does not add unobserved classes to other averages.

        Raises:
            ValueError: If average is not micro, macro, weighted, or binary.
        """
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
        """Set matched-token and compared-token totals to zero.

        Returns:
            None. A subsequent compute returns zero until pairs are added.
        """
        self._correct = 0
        self._total = 0

    def update(self, predictions: Any, targets: Any) -> None:
        """Count equal token pairs after flattening predictions and targets.

        Args:
            predictions: Token values, nested sequences, or optional torch tensors.
            targets: Reference values; comparison stops at the shorter flattened
                length. No padding or ignore-index filtering is performed.

        Returns:
            None. Counts accumulate across calls; tensor inputs are detached
            and copied to CPU before comparison.
        """
        preds = _to_flat_list(predictions)
        labels = _to_flat_list(targets)
        total = min(len(preds), len(labels))
        correct = sum(int(preds[i] == labels[i]) for i in range(total))
        self._correct += correct
        self._total += total

    def compute(self) -> dict[str, float]:
        # If no samples have been processed, return 0.0 accuracy.
        # This behavior is tested in the empty input test case.
        """Return ``token_accuracy`` as correct pairs divided by compared pairs.

        Empty state yields 0.0. Reading the result does not reset either count.

        Example:
            >>> metric = TokenAccuracy()
            >>> metric.update([1, 2, 3], [1, 0])
            >>> metric.compute()
            {'token_accuracy': 0.5}
        """
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
        """Clear corpus n-gram matches, candidate totals, and both token lengths.

        Returns:
            None. The n-gram order and smoothing configuration remain unchanged.
        """
        self._matches = [0] * self.n_gram
        self._totals = [0] * self.n_gram
        self._pred_length = 0
        self._ref_length = 0

    def _ngrams(self, tokens: Sequence[Any], n: int) -> Counter[tuple[Any, ...]]:
        if len(tokens) < n:
            return Counter()
        return Counter(tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1))

    def update(self, predictions: Any, targets: Any) -> None:
        """Accumulate clipped n-gram counts for paired candidate/reference sequences.

        Args:
            predictions: Token sequences, optional torch tensors, or a mapping
                containing input_ids or predictions. No text tokenization occurs.
            targets: One reference sequence per candidate; extra sequences on
                either side are ignored. Use nested lists for word-token batches.

        Returns:
            None. Corpus lengths and counts accumulate until reset.

        Raises:
            TypeError: If tokens cannot be hashed as n-gram tuple keys.
        """
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
        """Return corpus ``bleu_score`` and ``brevity_penalty`` without resetting.

        Any zero n-gram precision, including an order with no candidates, returns
        both values as zero. Smoothing is added only inside the logarithm after
        this check: it does not rescue zero matches. Positive smoothing can make
        a perfect score slightly exceed 1.0.

        Raises:
            ValueError: If a configured smoothing value makes a logarithm invalid.
        """
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
        """Store or replace a metric factory under a normalized name.

        Args:
            name: Registry key, stripped of whitespace and lowercased.
            metric_cls: Metric class to instantiate later; not validated here.
            **default_kwargs: Constructor defaults, overridden by create.

        Raises:
            ValueError: If name is empty after stripping.
        """
        key = name.strip().lower()
        if not key:
            raise ValueError("metric name must be non-empty")
        spec = MetricSpec(name=key, factory=metric_cls, default_kwargs=default_kwargs or None)
        self._registry[key] = spec

    def create(self, name: str, **overrides: Any) -> MetricBase:
        """Construct a fresh metric using stored defaults and caller overrides.

        Args:
            name: Case-insensitive registry key with surrounding whitespace ignored.
            **overrides: Constructor arguments taking precedence over defaults.

        Returns:
            The registered factory's new metric instance.

        Raises:
            KeyError: If the normalized name has not been registered.
            TypeError: If the factory rejects the merged constructor arguments.
            ValueError: If the metric constructor rejects an option.
        """
        key = name.strip().lower()
        if key not in self._registry:
            raise KeyError(f"metric not registered: {name}")
        spec = self._registry[key]
        kwargs = dict(spec.default_kwargs or {})
        kwargs.update(overrides)
        return spec.factory(**kwargs)

    def list(self) -> list[str]:
        """Return a sorted new list of normalized registered metric names.

        The list is a snapshot; mutating it does not modify the registry.
        """
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

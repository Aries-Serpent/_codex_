"""Lightweight classification metrics used by the registry."""
from __future__ import annotations

from typing import Hashable, Sequence


def _coerce_sequences(preds: Sequence[Hashable], targets: Sequence[Hashable]) -> tuple[list[Hashable], list[Hashable]]:
    preds_list = list(preds)
    targets_list = list(targets)
    if len(preds_list) != len(targets_list):
        raise ValueError(
            f"Predictions and targets length mismatch: {len(preds_list)} != {len(targets_list)}"
        )
    return preds_list, targets_list


def _per_class_counts(
    preds: Sequence[Hashable], targets: Sequence[Hashable]
) -> dict[Hashable, dict[str, int]]:
    preds_list, targets_list = _coerce_sequences(preds, targets)
    classes: set[Hashable] = set(preds_list) | set(targets_list)
    if not classes:
        return {}

    stats: dict[Hashable, dict[str, int]] = {
        label: {"tp": 0, "fp": 0, "fn": 0} for label in classes
    }
    for pred, target in zip(preds_list, targets_list):
        if pred == target:
            stats[target]["tp"] += 1
        else:
            stats[pred]["fp"] += 1
            stats[target]["fn"] += 1
    return stats


def classification_accuracy(preds: Sequence[Hashable], targets: Sequence[Hashable]) -> float:
    preds_list, targets_list = _coerce_sequences(preds, targets)
    total = len(targets_list)
    if total == 0:
        return 0.0
    correct = sum(1 for pred, target in zip(preds_list, targets_list) if pred == target)
    return float(correct / total)


def precision_macro(preds: Sequence[Hashable], targets: Sequence[Hashable]) -> float:
    stats = _per_class_counts(preds, targets)
    if not stats:
        return 0.0
    values: list[float] = []
    for counts in stats.values():
        denom = counts["tp"] + counts["fp"]
        values.append(counts["tp"] / denom if denom else 0.0)
    return float(sum(values) / len(values))


def recall_macro(preds: Sequence[Hashable], targets: Sequence[Hashable]) -> float:
    stats = _per_class_counts(preds, targets)
    if not stats:
        return 0.0
    values: list[float] = []
    for counts in stats.values():
        denom = counts["tp"] + counts["fn"]
        values.append(counts["tp"] / denom if denom else 0.0)
    return float(sum(values) / len(values))


def f1_macro(preds: Sequence[Hashable], targets: Sequence[Hashable]) -> float:
    stats = _per_class_counts(preds, targets)
    if not stats:
        return 0.0
    values: list[float] = []
    for counts in stats.values():
        denom = (2 * counts["tp"]) + counts["fp"] + counts["fn"]
        values.append((2 * counts["tp"]) / denom if denom else 0.0)
    return float(sum(values) / len(values))


__all__ = [
    "classification_accuracy",
    "precision_macro",
    "recall_macro",
    "f1_macro",
]

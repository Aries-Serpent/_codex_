"""Utility helpers for offline-friendly classification metrics."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Tuple

import numpy as np

ArrayPair = Tuple[np.ndarray, np.ndarray]


def _aligned_arrays(preds: Iterable[Any], targets: Iterable[Any]) -> ArrayPair:
    """Return numpy arrays trimmed to the shortest length.

    Inputs may be generators, numpy arrays, torch tensors, or any iterable. We
    coerce to ``object`` dtype to support numeric and string class labels without
    additional dependencies.
    """

    pred_list = list(preds)
    target_list = list(targets)
    if not pred_list or not target_list:
        return (np.array([], dtype=object), np.array([], dtype=object))
    limit = min(len(pred_list), len(target_list))
    return (
        np.asarray(pred_list[:limit], dtype=object),
        np.asarray(target_list[:limit], dtype=object),
    )


def _unique_labels(preds: np.ndarray, targets: np.ndarray) -> np.ndarray:
    if preds.size == 0 or targets.size == 0:
        return np.array([], dtype=object)
    return np.unique(np.concatenate([preds, targets]))


def accuracy(preds: Iterable[Any], targets: Iterable[Any]) -> float:
    """Macro accuracy (fraction of matching labels)."""

    pred_arr, target_arr = _aligned_arrays(preds, targets)
    if pred_arr.size == 0:
        return 0.0
    return float(np.mean(pred_arr == target_arr))


def precision(preds: Iterable[Any], targets: Iterable[Any]) -> float:
    """Macro precision across all observed labels."""

    pred_arr, target_arr = _aligned_arrays(preds, targets)
    labels = _unique_labels(pred_arr, target_arr)
    if pred_arr.size == 0 or labels.size == 0:
        return 0.0
    scores: list[float] = []
    for label in labels:
        true_positive = float(np.sum((pred_arr == label) & (target_arr == label)))
        false_positive = float(np.sum((pred_arr == label) & (target_arr != label)))
        denom = true_positive + false_positive
        scores.append((true_positive / denom) if denom else 0.0)
    return float(np.mean(scores)) if scores else 0.0


def recall(preds: Iterable[Any], targets: Iterable[Any]) -> float:
    """Macro recall across all observed labels."""

    pred_arr, target_arr = _aligned_arrays(preds, targets)
    labels = _unique_labels(pred_arr, target_arr)
    if pred_arr.size == 0 or labels.size == 0:
        return 0.0
    scores: list[float] = []
    for label in labels:
        true_positive = float(np.sum((pred_arr == label) & (target_arr == label)))
        false_negative = float(np.sum((pred_arr != label) & (target_arr == label)))
        denom = true_positive + false_negative
        scores.append((true_positive / denom) if denom else 0.0)
    return float(np.mean(scores)) if scores else 0.0


def f1_macro(preds: Iterable[Any], targets: Iterable[Any]) -> float:
    """Macro-averaged F1 score derived from the macro precision/recall pair."""

    pred_arr, target_arr = _aligned_arrays(preds, targets)
    labels = _unique_labels(pred_arr, target_arr)
    if pred_arr.size == 0 or labels.size == 0:
        return 0.0
    scores: list[float] = []
    for label in labels:
        true_positive = float(np.sum((pred_arr == label) & (target_arr == label)))
        false_positive = float(np.sum((pred_arr == label) & (target_arr != label)))
        false_negative = float(np.sum((pred_arr != label) & (target_arr == label)))
        denom = (2 * true_positive) + false_positive + false_negative
        scores.append(((2 * true_positive) / denom) if denom else 0.0)
    return float(np.mean(scores)) if scores else 0.0


__all__ = ["accuracy", "precision", "recall", "f1_macro"]

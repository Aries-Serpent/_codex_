"""
Classification Metrics v1.0.0
Accuracy, precision, recall, F1, streaming accuracy

Author: mbaetiong
Generated: 2025-11-19 04:20:17
"""

from __future__ import annotations

from typing import Any

import numpy as np
import torch

from .base import BaseMetric


def _to_numpy(arr: Any) -> np.ndarray:
    if torch.is_tensor(arr):
        return arr.detach().cpu().numpy()
    return np.asarray(arr)


def accuracy(preds: Any, labels: Any, ignore_index: int | None = None) -> float:
    p = _to_numpy(preds)
    y = _to_numpy(labels)
    if p.shape != y.shape:
        raise ValueError(f"Shape mismatch preds{p.shape} vs labels{y.shape}")
    if ignore_index is not None:
        mask = y != ignore_index
        denom = max(1, int(mask.sum()))
        return float(((p == y) & mask).sum() / denom)
    denom = max(1, y.size)
    return float((p == y).sum() / denom)


def precision(preds: Any, labels: Any, positive: int = 1) -> float:
    p = _to_numpy(preds).astype(int)
    y = _to_numpy(labels).astype(int)
    tp = int(((p == positive) & (y == positive)).sum())
    fp = int(((p == positive) & (y != positive)).sum())
    denom = max(1, tp + fp)
    return float(tp / denom)


def recall(preds: Any, labels: Any, positive: int = 1) -> float:
    p = _to_numpy(preds).astype(int)
    y = _to_numpy(labels).astype(int)
    tp = int(((p == positive) & (y == positive)).sum())
    fn = int(((p != positive) & (y == positive)).sum())
    denom = max(1, tp + fn)
    return float(tp / denom)


def f1(preds: Any, labels: Any, positive: int = 1) -> float:
    prec = precision(preds, labels, positive=positive)
    rec = recall(preds, labels, positive=positive)
    denom = max(1e-12, (prec + rec))
    return float(2 * prec * rec / denom)


class StreamingAccuracy(BaseMetric):
    def __init__(self, ignore_index: int | None = None) -> None:
        self.ignore_index = ignore_index
        self._correct = 0
        self._total = 0

    def update(self, preds: Any, labels: Any, **kwargs) -> None:
        p = _to_numpy(preds)
        y = _to_numpy(labels)
        if self.ignore_index is not None:
            mask = y != self.ignore_index
            self._correct += int(((p == y) & mask).sum())
            self._total += int(mask.sum())
        else:
            self._correct += int((p == y).sum())
            self._total += int(y.size)

    def compute(self) -> float:
        if self._total <= 0:
            return 0.0
        return float(self._correct / self._total)

    def reset(self) -> None:
        self._correct = 0
        self._total = 0

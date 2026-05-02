"""
Streaming Metrics v1.0.0
StreamingLoss for accumulating loss values

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


class StreamingLoss(BaseMetric):
    """Streaming average over scalar losses."""

    def __init__(self) -> None:
        self._sum = 0.0
        self._count = 0

    def update(self, preds: Any, labels: Any, **kwargs) -> None:
        # Expect a scalar loss passed via kwargs or preds
        loss = kwargs.get("loss")
        if loss is None:
            # fallback: mean over preds if tensor/array
            arr = _to_numpy(preds)
            loss = float(arr.mean()) if arr.size > 0 else 0.0
        self._sum += float(loss)
        self._count += 1

    def compute(self) -> float:
        if self._count <= 0:
            return 0.0
        return float(self._sum / self._count)

    def reset(self) -> None:
        self._sum = 0.0
        self._count = 0

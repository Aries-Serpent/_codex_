"""
Accuracy Metric Adapter

Computes classification accuracy from predictions and references.
Supports both token-level and sequence-level accuracy.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

import os  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from codex_ml.evaluation.runner import MetricAdapter  # noqa: E402

try:
    import torch
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    torch = None  # type: ignore[assignment]


class AccuracyMetric(MetricAdapter):
    """
    Accuracy metric adapter.

    Computes accuracy as: correct / total

    Args:
        name: Metric name (default: 'accuracy')
        ignore_index: Index to ignore in computation (e.g., padding token)

    Example:
        metric = AccuracyMetric()
        metric.add_batch([1, 2, 3], [1, 2, 2])  # 2/3 correct
        results = metric.compute()  # {'accuracy': 0.6667}
    """

    def __init__(self, name: str = "accuracy", ignore_index: int = -100):
        super().__init__(name)
        self.ignore_index = ignore_index
        self._correct = 0
        self._total = 0

    def add_batch(self, predictions: Any, references: Any) -> None:
        """Accumulate batch results."""
        # Convert to lists if tensors
        if torch and isinstance(predictions, torch.Tensor):
            predictions = predictions.detach().cpu().tolist()
        if torch and isinstance(references, torch.Tensor):
            references = references.detach().cpu().tolist()

        # Flatten if nested
        pred_flat = self._flatten(predictions)
        ref_flat = self._flatten(references)

        # Compute correct
        for pred, ref in zip(pred_flat, ref_flat, strict=False):
            if ref != self.ignore_index:
                self._total += 1
                if pred == ref:
                    self._correct += 1

    def compute(self) -> dict[str, float]:
        """Compute final accuracy."""
        if self._total == 0:
            return {self.name: 0.0}

        accuracy = self._correct / self._total
        return {self.name: accuracy}

    def reset(self) -> None:
        """Reset accumulated results."""
        super().reset()
        self._correct = 0
        self._total = 0

    @staticmethod
    def _flatten(nested: Any) -> list[Any]:
        """Flatten nested lists/tensors."""
        if isinstance(nested, (int, float)):
            return [nested]

        if isinstance(nested, (list, tuple)):
            flat = []
            for item in nested:
                if isinstance(item, (list, tuple)):
                    flat.extend(AccuracyMetric._flatten(item))
                else:
                    flat.append(item)
            return flat

        return [nested]

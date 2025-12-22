"""
Perplexity Metric Adapter

Computes perplexity for language models.
Perplexity = exp(average negative log-likelihood)
"""

from typing import Any, Dict
import logging
logger = logging.getLogger(__name__)
import math

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from codex_ml.evaluation.runner import MetricAdapter

try:
    import torch
    import torch.nn.functional as F
except ImportError as e:
   logger.debug(f"ImportError: {e}")
    logger.warning(f"ImportError: {e}", exc_info=True)
    torch = None
    F = None


class PerplexityMetric(MetricAdapter):
    """
    Perplexity metric adapter for language models.

    Computes perplexity as exp(average_loss).

    Args:
        name: Metric name (default: 'perplexity')
        ignore_index: Index to ignore in computation (e.g., padding token)

    Example:
        metric = PerplexityMetric()
        # Predictions should be logits, references should be token IDs
        metric.add_batch(logits, token_ids)
        results = metric.compute()  # {'perplexity': 25.3, 'loss': 3.23}
    """

    def __init__(self, name: str = "perplexity", ignore_index: int = -100):
        super().__init__(name)
        self.ignore_index = ignore_index
        self._total_loss = 0.0
        self._total_tokens = 0

    def add_batch(self, predictions: Any, references: Any) -> None:
        """
        Accumulate batch results.

        Args:
            predictions: Model logits (unnormalized scores)
            references: Target token IDs
        """
        if torch is None:
            # Fallback: assume predictions are already losses
            if isinstance(predictions, (int, float)):
                self._total_loss += predictions
                self._total_tokens += 1
            return

        # Convert to tensors if needed
        if not isinstance(predictions, torch.Tensor):
            predictions = torch.tensor(predictions)
        if not isinstance(references, torch.Tensor):
            references = torch.tensor(references)

        # Flatten if needed
        if predictions.dim() == 3:  # (batch, seq_len, vocab_size)
            predictions = predictions.view(-1, predictions.size(-1))
        if references.dim() == 2:  # (batch, seq_len)
            references = references.view(-1)

        # Compute cross-entropy loss
        loss = F.cross_entropy(
            predictions, references, ignore_index=self.ignore_index, reduction="sum"
        )

        # Count non-ignored tokens
        valid_tokens = (references != self.ignore_index).sum().item()

        self._total_loss += loss.item()
        self._total_tokens += valid_tokens

    def compute(self) -> Dict[str, float]:
        """Compute final perplexity."""
        if self._total_tokens == 0:
            return {self.name: float("inf"), "loss": float("inf")}

        avg_loss = self._total_loss / self._total_tokens
        perplexity = math.exp(avg_loss) if avg_loss < 100 else float("inf")

        return {
            self.name: perplexity,
            "loss": avg_loss,
        }

    def reset(self) -> None:
        """Reset accumulated results."""
        super().reset()
        self._total_loss = 0.0
        self._total_tokens = 0

"""
BLEU Metric Adapter

Computes BLEU score for machine translation and text generation.
Uses sacrebleu library if available, otherwise provides basic implementation.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

import os  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from codex_ml.evaluation.runner import MetricAdapter  # noqa: E402

try:
    import sacrebleu

    HAS_SACREBLEU = True
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    HAS_SACREBLEU = False


class BleuMetric(MetricAdapter):
    """
    BLEU metric adapter.

    Computes BLEU score for generated text vs. references.
    Requires sacrebleu package for full functionality.

    Args:
        name: Metric name (default: 'bleu')
        max_order: Maximum n-gram order (default: 4 for BLEU-4)

    Example:
        metric = BleuMetric()
        metric.add_batch(
            predictions=["the cat sat on the mat"],
            references=["the cat is on the mat"]
        )
        results = metric.compute()  # {'bleu': 0.45, ...}
    """

    def __init__(self, name: str = "bleu", max_order: int = 4):
        super().__init__(name)
        self.max_order = max_order
        if max_order != 4:
            logger.warning(
                f"max_order={max_order} specified, but sacrebleu uses n-gram order 4 by default. "
                "Custom max_order values are not supported in current sacrebleu versions."
            )

    def add_batch(self, predictions: Any, references: Any) -> None:
        """Accumulate batch results."""
        # Ensure lists of strings
        if isinstance(predictions, str):
            predictions = [predictions]
        if isinstance(references, str):
            references = [references]

        super().add_batch(predictions, references)

    def compute(self) -> dict[str, float]:
        """Compute BLEU score."""
        if not self._predictions:
            return {self.name: 0.0}

        if HAS_SACREBLEU:
            return self._compute_sacrebleu()
        return self._compute_basic()

    def _compute_sacrebleu(self) -> dict[str, float]:
        """Compute BLEU using sacrebleu library."""
        try:
            # sacrebleu expects predictions and list of references
            # Each prediction should have one or more references
            refs_list = [[ref] for ref in self._references]

            # Note: max_ngram_order is not supported in newer sacrebleu versions
            # The library uses n-gram order 4 by default
            bleu = sacrebleu.corpus_bleu(self._predictions, refs_list)

            return {
                self.name: bleu.score / 100.0,  # Convert to 0-1 scale
                f"{self.name}_score": bleu.score,
                f"{self.name}_precisions": bleu.precisions,
            }
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.debug("Exception caught, returning", exc_info=True)
            return {f"{self.name}_error": str(e)}  # type: ignore[dict-item]

    def _compute_basic(self) -> dict[str, float]:
        """Basic BLEU approximation without sacrebleu."""
        # This is a simplified approximation
        # For production, install sacrebleu
        total_score = 0.0

        for pred, ref in zip(self._predictions, self._references, strict=False):
            pred_tokens = pred.split()
            ref_tokens = ref.split()

            # Simple word overlap as proxy
            if len(pred_tokens) == 0:
                continue

            overlap = len(set(pred_tokens) & set(ref_tokens))
            score = overlap / len(pred_tokens) if pred_tokens else 0.0
            total_score += score

        avg_score = total_score / len(self._predictions) if self._predictions else 0.0

        return {
            self.name: avg_score,
            f"{self.name}_warning": "sacrebleu not installed, using basic approximation",  # type: ignore[dict-item]
        }

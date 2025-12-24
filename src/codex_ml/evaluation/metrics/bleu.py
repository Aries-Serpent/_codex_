"""
BLEU Metric Adapter

Computes BLEU score for machine translation and text generation.
Uses sacrebleu library if available, otherwise provides basic implementation.
"""

from typing import Any
import logging
logger = logging.getLogger(__name__)

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from codex_ml.evaluation.runner import MetricAdapter

try:
    import sacrebleu

    HAS_SACREBLEU = True
except ImportError as e:
    logger.debug(f"ImportError: {e}")
    logger.warning(f"ImportError: {e}", exc_info=True)
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
        else:
            return self._compute_basic()

    def _compute_sacrebleu(self) -> dict[str, float]:
        """Compute BLEU using sacrebleu library."""
        try:
            # sacrebleu expects predictions and list of references
            # Each prediction should have one or more references
            refs_list = [[ref] for ref in self._references]

            bleu = sacrebleu.corpus_bleu(
                self._predictions, refs_list, max_ngram_order=self.max_order
            )

            return {
                self.name: bleu.score / 100.0,  # Convert to 0-1 scale
                f"{self.name}_score": bleu.score,
                f"{self.name}_precisions": bleu.precisions,
            }
        except Exception as e:
            logger.debug(f"Exception: {e}")
            logger.debug("Exception caught, returning", exc_info=True)
            return {f"{self.name}_error": str(e)}

    def _compute_basic(self) -> dict[str, float]:
        """Basic BLEU approximation without sacrebleu."""
        # This is a simplified approximation
        # For production, install sacrebleu
        total_score = 0.0

        for pred, ref in zip(self._predictions, self._references):
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
            f"{self.name}_warning": "sacrebleu not installed, using basic approximation",
        }

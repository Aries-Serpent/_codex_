"""
ROUGE Metric Adapter

Computes ROUGE scores for summarization and text generation.
Uses rouge-score library if available, otherwise provides basic implementation.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

import os  # noqa: E402
import sys  # noqa: E402

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from codex_ml.evaluation.runner import MetricAdapter  # noqa: E402

try:
    from rouge_score import rouge_scorer

    HAS_ROUGE = True
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    HAS_ROUGE = False


class RougeMetric(MetricAdapter):
    """
    ROUGE metric adapter.

    Computes ROUGE scores for summarization tasks.
    Supports ROUGE-1, ROUGE-2, ROUGE-L.

    Args:
        name: Metric name (default: 'rouge')
        rouge_types: list of ROUGE types to compute (default: ['rouge1', 'rougeL'])
        use_stemmer: Whether to use Porter stemmer

    Example:
        metric = RougeMetric(['rouge1', 'rouge2', 'rougeL'])
        metric.add_batch(
            predictions=["the cat sat"],
            references=["the cat is sitting"]
        )
        results = metric.compute()  # {'rouge1': 0.67, 'rouge2': 0.5, 'rougeL': 0.67}
    """

    def __init__(
        self,
        rouge_types: list[str] | None = None,
        name: str = "rouge",
        use_stemmer: bool = True,
    ):
        super().__init__(name)
        self.rouge_types = rouge_types or ["rouge1", "rougeL"]
        self.use_stemmer = use_stemmer

        if HAS_ROUGE:
            self.scorer = rouge_scorer.RougeScorer(self.rouge_types, use_stemmer=use_stemmer)
        else:
            self.scorer = None

    def add_batch(self, predictions: Any, references: Any) -> None:
        """Accumulate batch results."""
        # Ensure lists of strings
        if isinstance(predictions, str):
            predictions = [predictions]
        if isinstance(references, str):
            references = [references]

        super().add_batch(predictions, references)

    def compute(self) -> dict[str, float]:
        """Compute ROUGE scores."""
        if not self._predictions:
            return {rouge_type: 0.0 for rouge_type in self.rouge_types}

        if HAS_ROUGE:
            return self._compute_rouge_score()
        return self._compute_basic()

    def _compute_rouge_score(self) -> dict[str, float]:
        """Compute ROUGE using rouge-score library."""
        try:
            aggregated_scores: dict[str, list[float]] = {
                rouge_type: [] for rouge_type in self.rouge_types
            }

            for pred, ref in zip(self._predictions, self._references, strict=False):
                scores = self.scorer.score(ref, pred)

                for rouge_type in self.rouge_types:
                    # Use F-measure (balanced precision and recall)
                    aggregated_scores[rouge_type].append(scores[rouge_type].fmeasure)

            # Average over all samples
            results = {}
            for rouge_type in self.rouge_types:
                avg_score = sum(aggregated_scores[rouge_type]) / len(aggregated_scores[rouge_type])
                results[rouge_type] = avg_score

            return results
        except (ValueError, TypeError, RuntimeError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.debug("Exception caught, returning", exc_info=True)
            return {f"{self.name}_error": str(e)}  # type: ignore[dict-item]

    def _compute_basic(self) -> dict[str, float]:
        """Basic ROUGE approximation without rouge-score."""
        # This is a simplified approximation
        # For production, install rouge-score
        total_score = 0.0

        for pred, ref in zip(self._predictions, self._references, strict=False):
            pred_tokens = set(pred.split())
            ref_tokens = set(ref.split())

            if len(pred_tokens) == 0 or len(ref_tokens) == 0:
                continue

            # Simple F1 as proxy for ROUGE
            precision = len(pred_tokens & ref_tokens) / len(pred_tokens)
            recall = len(pred_tokens & ref_tokens) / len(ref_tokens)

            if precision + recall > 0:
                f1 = 2 * (precision * recall) / (precision + recall)
                total_score += f1

        avg_score = total_score / len(self._predictions) if self._predictions else 0.0

        results = {rouge_type: avg_score for rouge_type in self.rouge_types}
        results[f"{self.name}_warning"] = "rouge-score not installed, using basic approximation"  # type: ignore[assignment]

        return results

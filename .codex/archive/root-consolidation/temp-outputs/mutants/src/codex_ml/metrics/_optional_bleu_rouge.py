"""
Optional BLEU/ROUGE metrics (gated by extras).

This module provides BLEU and ROUGE metrics that require optional dependencies
(nltk, rouge-score). If these dependencies are not installed, the metrics
will gracefully return None or raise informative errors.

Usage:
    from codex_ml.metrics._optional_bleu_rouge import patch_registry

    BUILTIN = {}
    patch_registry(BUILTIN)  # adds 'bleu','rouge_l' if deps present
"""

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _import_bleu_rouge() -> tuple[Any, Any, Any]:
    """
    Attempt to import BLEU/ROUGE dependencies.

    Returns:
        Tuple of (sentence_bleu, SmoothingFunction, rouge_scorer) or (None, None, None)
    """
    try:
        from nltk.translate.bleu_score import (
            SmoothingFunction,
            sentence_bleu,
        )
        from rouge_score import rouge_scorer

        return sentence_bleu, SmoothingFunction, rouge_scorer
    except (ImportError, AttributeError):
        logger.warning("Exception occurred", exc_info=True)
        return None, None, None


def bleu(predictions: list[str], targets: list[str]) -> Optional[float]:
    """
    Compute BLEU score for predictions vs targets.

    Args:
        predictions: List of predicted strings
        targets: List of target/reference strings

    Returns:
        BLEU score as float, or None if dependencies unavailable
    """
    sentence_bleu, SmoothingFunction, _ = _import_bleu_rouge()
    if not sentence_bleu:
        return None

    if not predictions or not targets:
        return 0.0

    # Average BLEU across all pairs
    scores = []
    chencherry = SmoothingFunction()

    for pred, targ in zip(predictions, targets, strict=False):
        score = sentence_bleu([targ.split()], pred.split(), smoothing_function=chencherry.method1)
        scores.append(score)

    return float(sum(scores) / len(scores)) if scores else 0.0


def rouge_l(predictions: list[str], targets: list[str]) -> Optional[float]:
    """
    Compute ROUGE-L F1 score for predictions vs targets.

    Args:
        predictions: List of predicted strings
        targets: List of target/reference strings

    Returns:
        ROUGE-L F1 score as float, or None if dependencies unavailable
    """
    _, _, rouge_scorer_class = _import_bleu_rouge()
    if not rouge_scorer_class:
        return None

    if not predictions or not targets:
        return 0.0

    # Average ROUGE-L across all pairs
    scorer = rouge_scorer_class(["rougeL"], use_stemmer=True)
    scores = []

    for pred, targ in zip(predictions, targets, strict=False):
        result = scorer.score(targ, pred)
        scores.append(result["rougeL"].fmeasure)

    return float(sum(scores) / len(scores)) if scores else 0.0


def patch_registry(reg: dict[str, object]) -> dict[str, object]:
    """
    Patch a registry dictionary with BLEU/ROUGE metrics if dependencies are available.

    Args:
        reg: Dictionary to patch (typically a metrics registry)

    Returns:
        The patched registry (same object, modified in place)
    """
    sb, _sm, rs = _import_bleu_rouge()
    if not (sb and rs):
        # Dependencies not available, don't add metrics
        return reg

    reg.setdefault("bleu", bleu)
    reg.setdefault("rouge_l", rouge_l)

    return reg

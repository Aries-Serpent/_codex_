"""Lightweight metric registry with deterministic implementations.

Metrics are registered via the ``@register_metric`` decorator and
looked up with :func:`get_metric`.  Each metric callable follows the
simple convention::

    metric(preds, targets, **kwargs) -> float | dict | None

where ``preds`` and ``targets`` are sequences of strings or integers.
Metrics should be side-effect free and deterministic.
"""

from __future__ import annotations

import math
import re
from typing import Callable, Dict, Optional, Sequence

METRICS: Dict[str, Callable[..., object]] = {}


def register_metric(name: str) -> Callable[[Callable[..., object]], Callable[..., object]]:
    """Register ``fn`` under ``name`` in the global metric registry."""

    def deco(fn: Callable[..., object]) -> Callable[..., object]:
        METRICS[name] = fn
        return fn

    return deco


def get_metric(name: str) -> Callable[..., object]:
    """Return the metric callable registered under ``name``."""

    if name not in METRICS:
        raise KeyError(name)
    return METRICS[name]


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------


def _norm_str(
    s: str,
    *,
    lowercase: bool = True,
    strip: bool = True,
    remove_punct: bool = False,
) -> str:
    s = str(s)
    if lowercase:
        s = s.lower()
    if strip:
        s = s.strip()
    if remove_punct:
        s = re.sub(r"[\W_]+", " ", s)
    return " ".join(s.split())


# ---------------------------------------------------------------------------
# Built in metrics
# ---------------------------------------------------------------------------


@register_metric("accuracy@token")
def token_accuracy(
    preds: Sequence[int], targets: Sequence[int], *, ignore_index: int = -100
) -> float:
    """Token-level accuracy.

    Parameters
    ----------
    preds, targets:
        Sequences of token ids.
    ignore_index:
        Target value to ignore when computing accuracy.
    """

    correct = 0
    total = 0
    for p, t in zip(preds, targets):
        if int(t) == ignore_index:
            continue
        total += 1
        correct += int(p) == int(t)
    return float(correct / total) if total else 0.0


@register_metric("ppl")
def perplexity(nll: Sequence[float]) -> float:
    """Compute perplexity from a sequence of negative log-likelihoods."""

    if not nll:
        return float("inf")
    avg = sum(float(x) for x in nll) / len(nll)
    try:
        return float(math.exp(avg))
    except OverflowError:  # pragma: no cover - extremely large losses
        return float("inf")


@register_metric("exact_match")
def exact_match(
    preds: Sequence[str], targets: Sequence[str], *, remove_punct: bool = False
) -> float:
    """Deterministic, whitespace-insensitive exact match."""

    matches = 0
    for p, t in zip(preds, targets):
        if _norm_str(p, remove_punct=remove_punct) == _norm_str(t, remove_punct=remove_punct):
            matches += 1
    return float(matches / max(1, len(preds)))


@register_metric("f1")
def f1_score(preds: Sequence[str], targets: Sequence[str]) -> float:
    """Token-level F1 computed over whitespace-separated tokens."""

    tp = fp = fn = 0
    for p, t in zip(preds, targets):
        ps = set(_norm_str(p).split())
        ts = set(_norm_str(t).split())
        tp += len(ps & ts)
        fp += len(ps - ts)
        fn += len(ts - ps)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    return 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0


@register_metric("dist-1")
def dist1(preds: Sequence[str], targets: Sequence[str] | None = None) -> float:
    return _distinct_ngrams(preds, 1)


@register_metric("dist-2")
def dist2(preds: Sequence[str], targets: Sequence[str] | None = None) -> float:
    return _distinct_ngrams(preds, 2)


def _distinct_ngrams(preds: Sequence[str], n: int) -> float:
    tokens = [tok for p in preds for tok in _norm_str(p).split()]
    if n == 1:
        ngrams = tokens
    else:
        ngrams = [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]
    total = len(ngrams)
    return len(set(ngrams)) / total if total else 0.0


@register_metric("bleu")
def bleu(preds: Sequence[str], targets: Sequence[str]) -> Optional[float]:
    """Corpus BLEU via NLTK if available; returns ``None`` otherwise."""

    try:  # pragma: no cover - optional dependency
        from nltk.translate.bleu_score import SmoothingFunction, corpus_bleu
    except Exception:  # pragma: no cover - dependency missing
        return None
    cand = [p.split() for p in preds]
    ref = [[t.split()] for t in targets]
    smoothie = SmoothingFunction().method3
    try:
        return float(corpus_bleu(ref, cand, smoothing_function=smoothie))
    except Exception:  # pragma: no cover - numerical issue
        return None


@register_metric("rougeL")
def rouge_l(preds: Sequence[str], targets: Sequence[str]) -> Optional[float]:
    """ROUGE-L F-measure via ``rouge_score``; returns ``None`` if unavailable."""

    try:  # pragma: no cover - optional dependency
        from rouge_score import rouge_scorer
    except Exception:  # pragma: no cover
        return None
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    scores = [scorer.score(t, p)["rougeL"].fmeasure for p, t in zip(preds, targets)]
    return float(sum(scores) / len(scores)) if scores else None


@register_metric("chrf")
def chrf(preds: Sequence[str], targets: Sequence[str]) -> Optional[float]:
    """chrF metric via sacrebleu; returns ``None`` on failure."""

    try:  # pragma: no cover - optional dependency
        from sacrebleu.metrics import CHRF
    except Exception:  # pragma: no cover
        return None
    scorer = CHRF()
    try:
        return float(scorer.corpus_score(preds, [targets]).score)
    except Exception:  # pragma: no cover - numerical issue
        return None


__all__ = ["register_metric", "get_metric", "METRICS"]

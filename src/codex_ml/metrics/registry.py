from __future__ import annotations

import math
import re
from collections import Counter
from typing import Callable, Dict, List, Optional, Sequence

METRICS: Dict[str, Callable] = {}


def register_metric(name: str) -> Callable[[Callable], Callable]:
    """Decorator to register a metric callable under ``name``."""

    def decorator(fn: Callable) -> Callable:
        METRICS[name] = fn
        return fn

    return decorator


def get_metric(name: str) -> Callable:
    """Retrieve a metric callable by name."""
    if name not in METRICS:
        raise KeyError(f"Unknown metric: {name}")
    return METRICS[name]


def _normalize(s: str) -> str:
    s = re.sub(r"[^\w\s]", "", str(s).lower())
    return " ".join(s.split())


@register_metric("accuracy@token")
def token_accuracy(preds: Sequence[int], targets: Sequence[int]) -> float:
    correct = 0
    total = 0
    for p, t in zip(preds, targets):
        total += 1
        try:
            correct += int(p) == int(t)
        except Exception:
            correct += str(p) == str(t)
    return float(correct / total) if total else 0.0


@register_metric("ppl")
def perplexity(nll_sum: float, n_tokens: int) -> float:
    """Convert negative log-likelihood sum to perplexity."""
    if n_tokens <= 0:
        return float("inf")
    return float(math.exp(nll_sum / n_tokens))


@register_metric("exact_match")
def exact_match(preds: Sequence[str], targets: Sequence[str]) -> float:
    matches = 0
    for p, t in zip(preds, targets):
        matches += _normalize(p) == _normalize(t)
    return float(matches / len(preds)) if preds else 0.0


@register_metric("f1")
def f1(preds: Sequence[str], targets: Sequence[str]) -> float:
    scores: List[float] = []
    for p, t in zip(preds, targets):
        p_tok = _normalize(p).split()
        t_tok = _normalize(t).split()
        if not p_tok and not t_tok:
            scores.append(1.0)
            continue
        common = Counter(p_tok) & Counter(t_tok)
        tp = sum(common.values())
        precision = tp / len(p_tok) if p_tok else 0.0
        recall = tp / len(t_tok) if t_tok else 0.0
        if precision + recall:
            scores.append(2 * precision * recall / (precision + recall))
        else:
            scores.append(0.0)
    return float(sum(scores) / len(scores)) if scores else 0.0


def _dist_n(preds: Sequence[str], n: int) -> float:
    tokens = []
    for p in preds:
        tokens.extend(_normalize(p).split())
    if len(tokens) < n or n <= 0:
        return 0.0
    ngrams = [tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]
    unique = len(set(ngrams))
    return float(unique / len(ngrams)) if ngrams else 0.0


@register_metric("dist-1")
def dist_1(preds: Sequence[str], targets: Sequence[str]) -> float:  # noqa: ARG001
    return _dist_n(preds, 1)


@register_metric("dist-2")
def dist_2(preds: Sequence[str], targets: Sequence[str]) -> float:  # noqa: ARG001
    return _dist_n(preds, 2)


@register_metric("bleu")
def bleu(preds: Sequence[str], targets: Sequence[str]) -> Optional[float]:
    try:
        from nltk.translate.bleu_score import SmoothingFunction, corpus_bleu
    except Exception:  # pragma: no cover - dependency missing
        return None
    pred_tok = [_normalize(p).split() for p in preds]
    targ_tok = [[_normalize(t).split()] for t in targets]
    if not pred_tok:
        return None
    smoothie = SmoothingFunction().method3
    try:
        score = corpus_bleu(targ_tok, pred_tok, smoothing_function=smoothie)
        return float(score)
    except Exception:  # pragma: no cover - unexpected runtime error
        return None


@register_metric("rougeL")
def rouge_l(preds: Sequence[str], targets: Sequence[str]) -> Optional[float]:
    try:
        from rouge_score import rouge_scorer
    except Exception:  # pragma: no cover - dependency missing
        return None
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    scores = [
        scorer.score(_normalize(t), _normalize(p))["rougeL"].fmeasure
        for p, t in zip(preds, targets)
    ]
    if not scores:
        return None
    return float(sum(scores) / len(scores))


@register_metric("chrF")
def chrf(preds: Sequence[str], targets: Sequence[str]) -> Optional[float]:
    try:
        from nltk.translate.chrf_score import corpus_chrf
    except Exception:  # pragma: no cover - dependency missing
        return None
    try:
        score = corpus_chrf(targets, preds)
        return float(score)
    except Exception:  # pragma: no cover
        return None

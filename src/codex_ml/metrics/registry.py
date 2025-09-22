"""Lightweight metric registry with deterministic implementations.

Metrics are registered via the @register_metric decorator and looked up
with get_metric. Each metric callable follows the convention:

    metric(preds, targets, **kwargs) -> float | dict | None

where preds and targets are sequences (strings or integers). Metrics
must be deterministic and side-effect free.
"""

from __future__ import annotations

import json
import math
import os
import re
from collections import Counter
from pathlib import Path
from typing import Callable, Optional, Sequence

from codex_ml.registry.base import Registry

metric_registry = Registry("metric", entry_point_group="codex_ml.metrics")


def register_metric(
    name: str, *, override: bool = False
) -> Callable[[Callable[..., object]], Callable[..., object]]:
    """Register ``fn`` under ``name`` in the metric registry."""

    return metric_registry.register(name, override=override)


def get_metric(name: str) -> Callable[..., object]:
    """Return the metric callable registered under name."""

    return metric_registry.get(name)


def list_metrics() -> list[str]:
    return metric_registry.list()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _resolve_metric_resource(
    name: str,
    path: str | os.PathLike[str] | None,
    *,
    filename: str,
    specific_env: str | None = None,
) -> Path:
    candidates = []
    if path:
        provided = Path(path).expanduser()
        target = provided / filename if provided.is_dir() else provided
        if target.exists():
            return target
        raise FileNotFoundError(
            f"Offline metric resource '{name}' expected at {target}. Provide an existing file or directory."
        )

    if specific_env:
        env_value = os.environ.get(specific_env)
        if env_value:
            env_path = Path(env_value).expanduser()
            if env_path.is_dir():
                env_path = env_path / filename
            candidates.append(env_path)

    offline_root = os.environ.get("CODEX_ML_OFFLINE_METRICS_DIR")
    if offline_root:
        offline_path = Path(offline_root).expanduser()
        candidates.append(offline_path / filename if offline_path.is_dir() else offline_path)

    repo_root = _repo_root()
    candidates.append(repo_root / "data" / "offline" / filename)
    candidates.append(repo_root / "artifacts" / "metrics" / filename)

    checked: list[str] = []
    for candidate in candidates:
        resolved = candidate.expanduser()
        checked.append(str(resolved))
        if resolved.exists():
            return resolved

    checked_msg = ", ".join(checked) if checked else "<no candidates>"
    raise FileNotFoundError(
        f"Offline metric resource '{name}' not found. Checked: {checked_msg}. Provide `weights_path` or "
        "set CODEX_ML_OFFLINE_METRICS_DIR / {specific_env or 'CODEX_ML_WEIGHTED_ACCURACY_PATH'} to point to the file."
    )


# ---------------------------------------------------------------------------
# Normalization helpers
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
# Built-in metrics
# ---------------------------------------------------------------------------


@register_metric("accuracy@token")
def token_accuracy(
    preds: Sequence[int], targets: Sequence[int], *, ignore_index: int = -100
) -> float:
    """Token-level accuracy with optional ignore_index."""
    correct = 0
    total = 0
    for p, t in zip(preds, targets):
        ti = int(t)
        if ti == ignore_index:
            continue
        total += 1
        correct += int(p) == ti
    return float(correct / total) if total else 0.0


@register_metric("ppl")
def perplexity(nll_or_sum, n_tokens: Optional[int] = None) -> float:
    """Perplexity from negative log-likelihood.

    Backward compatible signatures:
    - perplexity([nll_i...]) -> exp(mean(nll))
    - perplexity(nll_sum, n_tokens) -> exp(nll_sum / n_tokens)
    """
    # Variant A: list/sequence of NLL
    if n_tokens is None:
        seq = list(nll_or_sum)
        if not seq:
            return float("inf")
        avg = sum(float(x) for x in seq) / len(seq)
        try:
            return float(math.exp(avg))
        except OverflowError:  # pragma: no cover
            return float("inf")
    # Variant B: sum and count
    total = float(nll_or_sum)
    count = int(n_tokens or 0)
    if count <= 0:
        return float("inf")
    try:
        return float(math.exp(total / count))
    except OverflowError:  # pragma: no cover
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
def f1(preds: Sequence[str], targets: Sequence[str]) -> float:
    """Average per-example F1 over whitespace tokens (bag-of-words)."""
    scores = []
    for p, t in zip(preds, targets):
        p_tok = _norm_str(p).split()
        t_tok = _norm_str(t).split()
        if not p_tok and not t_tok:
            scores.append(1.0)
            continue
        common = Counter(p_tok) & Counter(t_tok)
        tp = sum(common.values())
        precision = tp / len(p_tok) if p_tok else 0.0
        recall = tp / len(t_tok) if t_tok else 0.0
        scores.append(
            2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        )
    return float(sum(scores) / len(scores)) if scores else 0.0


def _distinct_ngrams(preds: Sequence[str], n: int) -> float:
    toks = [tok for p in preds for tok in _norm_str(p, remove_punct=True).split()]
    if n <= 1:
        ngrams = toks
    else:
        ngrams = [" ".join(toks[i : i + n]) for i in range(max(0, len(toks) - n + 1))]
    total = len(ngrams)
    return float(len(set(ngrams)) / total) if total else 0.0


@register_metric("dist-1")
def dist_1(preds: Sequence[str], targets: Sequence[str] | None = None) -> float:  # noqa: ARG001
    return _distinct_ngrams(preds, 1)


@register_metric("dist-2")
def dist_2(preds: Sequence[str], targets: Sequence[str] | None = None) -> float:  # noqa: ARG001
    return _distinct_ngrams(preds, 2)


@register_metric("bleu")
def bleu(preds: Sequence[str], targets: Sequence[str]) -> Optional[float]:
    """Corpus BLEU via NLTK if available; returns None otherwise."""
    try:  # pragma: no cover - optional dependency
        from nltk.translate.bleu_score import SmoothingFunction, corpus_bleu
    except Exception:  # pragma: no cover
        return None
    cand = [_norm_str(p, remove_punct=True).split() for p in preds]
    ref = [[_norm_str(t, remove_punct=True).split()] for t in targets]
    if not cand:
        return None
    smoothie = SmoothingFunction().method3
    try:
        return float(corpus_bleu(ref, cand, smoothing_function=smoothie))
    except Exception:  # pragma: no cover - numerical issue
        return None


@register_metric("rougeL")
def rouge_l(preds: Sequence[str], targets: Sequence[str]) -> Optional[float]:
    """ROUGE-L F-measure via rouge_score; returns None if unavailable."""
    try:  # pragma: no cover - optional dependency
        from rouge_score import rouge_scorer
    except Exception:  # pragma: no cover
        return None
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    scores = [
        scorer.score(_norm_str(t, remove_punct=False), _norm_str(p, remove_punct=False))[
            "rougeL"
        ].fmeasure
        for p, t in zip(preds, targets)
    ]
    return float(sum(scores) / len(scores)) if scores else None


@register_metric("offline:weighted-accuracy")
def weighted_accuracy(
    preds: Sequence[str | int],
    targets: Sequence[str | int],
    *,
    weights_path: str | os.PathLike[str] | None = None,
) -> float:
    """Weighted accuracy that loads class weights from a local JSON fixture."""

    weights_file = _resolve_metric_resource(
        "offline:weighted-accuracy",
        weights_path,
        filename="weighted_accuracy.json",
        specific_env="CODEX_ML_WEIGHTED_ACCURACY_PATH",
    )
    try:
        weights = json.loads(weights_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:  # pragma: no cover - malformed fixture
        raise ValueError(f"Invalid weight specification in {weights_file}: {exc}") from exc

    total = 0.0
    correct = 0.0
    for pred, target in zip(preds, targets):
        label = str(target)
        weight = float(weights.get(label, 1.0))
        total += weight
        if str(pred) == label:
            correct += weight
    return float(correct / total) if total else 0.0


@register_metric("chrf")
def chrf(preds: Sequence[str], targets: Sequence[str]) -> Optional[float]:
    """chrF metric via sacrebleu (preferred) or NLTK; None on failure."""
    # Try sacrebleu first
    try:  # pragma: no cover - optional dependency
        from sacrebleu.metrics import CHRF

        scorer = CHRF()
        return float(scorer.corpus_score(preds, [targets]).score)
    except Exception:
        pass
    # Fallback to nltk
    try:  # pragma: no cover - optional dependency
        from nltk.translate.chrf_score import corpus_chrf

        return float(corpus_chrf(targets, preds))
    except Exception:  # pragma: no cover
        return None


__all__ = ["metric_registry", "register_metric", "get_metric", "list_metrics"]

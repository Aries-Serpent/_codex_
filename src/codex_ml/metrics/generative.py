"""Lightweight generative metrics (BLEU/ROUGE-L) without heavy deps."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Sequence

from .registry import register_metric


def _normalise_text(value: object) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, bytes):  # pragma: no cover - defensive
        return value.decode("utf-8", errors="ignore").strip()
    return str(value).strip()


def _tokenise(text: object) -> list[str]:
    value = _normalise_text(text)
    return value.split()


def _ngram_counts(tokens: list[str], order: int) -> Counter[tuple[str, ...]]:
    if order <= 0:
        return Counter()
    if len(tokens) < order:
        return Counter()
    return Counter(tuple(tokens[i : i + order]) for i in range(len(tokens) - order + 1))


def _prepare_pairs(
    preds: Sequence[object],
    targets: Sequence[object],
) -> list[tuple[list[str], list[str]]]:
    prepared: list[tuple[list[str], list[str]]] = []
    for pred, tgt in zip(preds, targets, strict=False):
        prepared.append((_tokenise(pred), _tokenise(tgt)))
    return prepared


@register_metric("bleu", override=True)
def bleu(
    preds: Sequence[object],
    targets: Sequence[object],
    *,
    max_order: int = 4,
    smooth: bool = True,
) -> float:
    """Compute a BLEU score using uniform n-gram weighting."""

    pairs = _prepare_pairs(preds, targets)
    if not pairs:
        return 0.0

    precisions: list[float] = []
    for order in range(1, max_order + 1):
        matches = 0
        possible = 0
        for pred_tokens, tgt_tokens in pairs:
            pred_counts = _ngram_counts(pred_tokens, order)
            tgt_counts = _ngram_counts(tgt_tokens, order)
            overlap = pred_counts & tgt_counts
            matches += sum(overlap.values())
            possible += sum(pred_counts.values())
        if possible == 0:
            continue
        if matches == 0:
            precisions.append(1e-9 if smooth else 0.0)
        else:
            precisions.append(matches / possible)

    if not precisions:
        return 0.0

    if all(p <= 1e-9 for p in precisions):
        return 0.0

    if any(p <= 0.0 for p in precisions):
        return 0.0

    weight = 1.0 / len(precisions)
    log_precision = sum(weight * math.log(p) for p in precisions)
    geo_mean = math.exp(log_precision)

    pred_len = sum(len(pred_tokens) for pred_tokens, _ in pairs)
    target_len = sum(len(tgt_tokens) for _, tgt_tokens in pairs)
    if pred_len == 0:
        return 0.0

    brevity_penalty = 1.0 if pred_len > target_len else math.exp(1.0 - target_len / pred_len)

    return float(brevity_penalty * geo_mean)


def _lcs_length(a: list[str], b: list[str]) -> int:
    if not a or not b:
        return 0
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i, token_a in enumerate(a, start=1):
        for j, token_b in enumerate(b, start=1):
            if token_a == token_b:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[-1][-1]


@register_metric("rougeL", override=True)
def rouge_l(preds: Sequence[object], targets: Sequence[object]) -> float:
    """Compute the ROUGE-L F1 score using longest common subsequence."""

    pairs = _prepare_pairs(preds, targets)
    if not pairs:
        return 0.0

    scores = []
    for pred_tokens, tgt_tokens in pairs:
        lcs = _lcs_length(pred_tokens, tgt_tokens)
        if lcs == 0:
            scores.append(0.0)
            continue
        precision = lcs / max(len(pred_tokens), 1)
        recall = lcs / max(len(tgt_tokens), 1)
        if precision + recall == 0:
            scores.append(0.0)
        else:
            scores.append((2 * precision * recall) / (precision + recall))

    return float(sum(scores) / len(scores))


# Create an alias so both "rougeL" and "rouge_l" resolve to the same implementation
from .registry import alias_metric  # noqa: E402

alias_metric("rouge_l", "rougeL", override=True)


__all__ = ["bleu", "rouge_l"]

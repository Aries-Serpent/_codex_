"""Fallback evaluation metrics for synthetic data.

Provides basic evaluation metrics (token accuracy, perplexity proxy, exact match)
for use when full evaluation dependencies are unavailable.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from .metrics import exact_match_strict, token_stats

IGNORE_INDEX = -1


@dataclass(frozen=True)
class SyntheticSummary:
    token_accuracy: float
    perplexity_proxy: float
    exact_match: float
    avg_length: float
    samples: int

    def as_dict(self) -> dict[str, float]:
        return {
            "token_accuracy": self.token_accuracy,
            "perplexity_proxy": self.perplexity_proxy,
            "exact_match": self.exact_match,
            "avg_length": self.avg_length,
            "samples": float(self.samples),
        }


def _encode_tokens(
    sequences: Sequence[str],
    vocab: dict[str, int] | None = None,
    *,
    allow_new_tokens: bool = True,
) -> tuple[list[list[int]], dict[str, int]]:
    if vocab is None:
        vocab = {}
    elif allow_new_tokens is False:
        # Preserve the caller's vocabulary when new tokens are disallowed so
        # that we can raise a helpful error without mutating ``vocab``.
        vocab = dict(vocab)
    encoded: list[list[int]] = []
    for text in sequences:
        ids: list[int] = []
        for token in str(text).split():
            idx = vocab.get(token)
            if idx is None:
                if not allow_new_tokens:
                    raise KeyError(f"Token {token!r} not found in vocabulary")
                idx = len(vocab)
                vocab[token] = idx
            ids.append(idx)
        encoded.append(ids)
    return encoded, vocab


def _perplexity_proxy(predicted: Sequence[int], targets: Sequence[int]) -> float:
    counter = Counter(pid for pid in predicted if pid != IGNORE_INDEX)
    total = sum(counter.values())
    if total == 0:
        return float("inf")
    smoothing = 1.0 / (total + max(len(counter), 1))
    nll = 0.0
    seen = 0
    for tid in targets:
        if tid == IGNORE_INDEX:
            continue
        prob = counter.get(tid, 0) / total
        if prob <= 0.0:
            prob = smoothing
        nll += -math.log(prob)
        seen += 1
    if seen == 0:
        return float("inf")
    return float(math.exp(nll / seen))


def synthetic_alignment(predictions: Iterable[str], references: Iterable[str]) -> SyntheticSummary:
    preds = list(predictions)
    refs = list(references)
    if len(preds) != len(refs):
        raise ValueError("predictions and references must have the same length")
    pred_ids, vocab = _encode_tokens(preds)
    ref_ids, _ = _encode_tokens(refs, vocab)
    flat_pred: list[int] = []
    flat_ref: list[int] = []
    total_tokens = 0
    for pred_seq, ref_seq in zip(pred_ids, ref_ids, strict=False):
        length = max(len(pred_seq), len(ref_seq))
        total_tokens += length
        padded_pred = pred_seq + [IGNORE_INDEX] * (length - len(pred_seq))
        padded_ref = ref_seq + [IGNORE_INDEX] * (length - len(ref_seq))
        flat_pred.extend(padded_pred)
        flat_ref.extend(padded_ref)
    stats = token_stats(flat_pred, flat_ref, ignore_index=IGNORE_INDEX)
    exact = 0.0
    if preds:
        matches = sum(
            1 for pred, ref in zip(preds, refs, strict=False) if exact_match_strict(pred, ref)
        )
        exact = matches / len(preds)
    perplexity = _perplexity_proxy(flat_pred, flat_ref)
    avg_length = total_tokens / len(preds) if preds else 0.0
    return SyntheticSummary(
        token_accuracy=stats["accuracy"],
        perplexity_proxy=perplexity,
        exact_match=exact,
        avg_length=avg_length,
        samples=len(preds),
    )

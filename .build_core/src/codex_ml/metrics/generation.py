"""
Generation Metrics v1.0.0
BLEU, ROUGE-L (minimal, no external deps)

Author: mbaetiong
Generated: 2025-11-19 04:20:17
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Sequence


def _tokenize(s: str) -> list[str]:
    return [t for t in s.strip().split() if t]


def compute_brevity_penalty(
    hypotheses: Sequence[str],
    norm_refs: Sequence[Sequence[str]],
    tokenize: Callable[[str], Iterable[str]] = _tokenize,
) -> float:
    """Compute BLEU brevity penalty aligning hypotheses and references."""

    if len(hypotheses) != len(norm_refs):
        raise ValueError("hypotheses and references length must match")

    hyp_len = sum(len(list(tokenize(h))) for h in hypotheses)
    ref_len = 0

    # P1 fix: zip hypotheses with their reference sets so each hypothesis uses
    # its own length instead of relying on norm_refs.index(refs).
    for hyp, refs in zip(hypotheses, norm_refs, strict=False):
        cand_len = len(list(tokenize(hyp)))
        if not refs:
            best = 0
        else:
            ref_candidates = (
                (abs(len(list(tokenize(r))) - cand_len), len(list(tokenize(r)))) for r in refs
            )
            best = min(ref_candidates)[1]
        ref_len += best

    if hyp_len == 0:
        return 0.0
    if hyp_len > ref_len:
        return 1.0
    return math.exp(1.0 - ref_len / hyp_len)


def compute_corpus_bleu(
    hypotheses: Sequence[str],
    norm_refs: Sequence[Sequence[str]],
    tokenize: Callable[[str], Iterable[str]] = _tokenize,
) -> float:
    """Minimal BLEU-like helper to exercise compute_brevity_penalty in tests."""

    if len(hypotheses) != len(norm_refs):
        raise ValueError("hypotheses and references length must match")

    bp = compute_brevity_penalty(hypotheses, norm_refs, tokenize=tokenize)

    total_matches = 0
    total_tokens = 0
    for hyp, refs in zip(hypotheses, norm_refs, strict=False):
        hyp_tokens = list(tokenize(hyp))
        total_tokens += len(hyp_tokens)
        ref_token_set: set[str] = set()
        for r in refs:
            ref_token_set.update(list(tokenize(r)))
        total_matches += sum(1 for tok in hyp_tokens if tok in ref_token_set)

    if total_tokens == 0 or total_matches == 0:
        return 0.0
    precision = total_matches / total_tokens
    return bp * precision


def _ngram_counts(tokens: list[str], n: int) -> dict[tuple[str, ...], int]:
    counts: dict[tuple[str, ...], int] = {}
    if n <= 0 or len(tokens) < n:
        return counts
    for i in range(len(tokens) - n + 1):
        ngram = tuple(tokens[i : i + n])
        counts[ngram] = counts.get(ngram, 0) + 1
    return counts


def bleu(
    hypotheses: Sequence[str],
    references: Sequence[Sequence[str]] | Sequence[str],
    max_n: int = 4,
    smooth: float = 1e-9,
) -> float:
    """
    Minimal BLEU implementation (corpus-level) without external deps.

    hypotheses: list of hypothesis strings (len = M)
    references: either a list of reference strings (len = M), or a list of lists of references per hypothesis
    """  # noqa: E501
    # Normalize references input
    norm_refs: list[list[str]] = []
    if len(references) > 0 and isinstance(references[0], str):
        # single reference per hypothesis
        norm_refs = [[r] for r in references]  # type: ignore[list-item]
    else:
        norm_refs = references  # type: ignore[assignment]

    if len(hypotheses) != len(norm_refs):
        raise ValueError("hypotheses and references length must match")

    precisions: list[float] = []
    for n in range(1, max_n + 1):
        num = 0
        den = 0
        for hyp, refs in zip(hypotheses, norm_refs, strict=False):
            htoks = _tokenize(hyp)
            hcounts = _ngram_counts(htoks, n)
            if not hcounts:
                continue
            # merge reference max counts
            ref_max: dict[tuple[str, ...], int] = {}
            for r in refs:
                rc = _ngram_counts(_tokenize(r), n)
                for k, v in rc.items():
                    ref_max[k] = max(ref_max.get(k, 0), v)
            # clipped counts
            clipped = 0
            total = 0
            for k, hv in hcounts.items():
                clipped += min(hv, ref_max.get(k, 0))
                total += hv
            num += clipped
            den += total
        precisions.append((num + smooth) / (max(1, den) + smooth))
    # geometric mean of precisions
    geo = math.exp(sum(math.log(p) for p in precisions) / max(1, len(precisions)))
    bp = compute_brevity_penalty(hypotheses, norm_refs, tokenize=_tokenize)
    return float(bp * geo)


def rouge_l(hypotheses: Sequence[str], references: Sequence[str]) -> float:
    """Simple ROUGE-L (LCS-based) averaged over pairs."""

    def lcs(a: list[str], b: list[str]) -> int:
        m, n = len(a), len(b)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m):
            for j in range(n):
                if a[i] == b[j]:
                    dp[i + 1][j + 1] = dp[i][j] + 1
                else:
                    dp[i + 1][j + 1] = max(dp[i][j + 1], dp[i + 1][j])
        return dp[m][n]

    scores = []
    for h, r in zip(hypotheses, references, strict=False):
        ht, rt = _tokenize(h), _tokenize(r)
        if not ht or not rt:
            scores.append(0.0)
            continue
        lcs_len = lcs(ht, rt)
        prec = lcs_len / len(ht)
        rec = lcs_len / len(rt)
        denom = prec + rec if (prec + rec) > 0 else 1e-12
        f = 2 * prec * rec / denom
        scores.append(f)
    return float(sum(scores) / max(1, len(scores)))

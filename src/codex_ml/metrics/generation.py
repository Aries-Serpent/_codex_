"""
Generation Metrics v1.0.0
BLEU, ROUGE-L (minimal, no external deps)

Author: mbaetiong
Generated: 2025-11-19 04:20:17
"""
from __future__ import annotations
from typing import List, Sequence


def _tokenize(s: str) -> List[str]:
    return [t for t in s.strip().split() if t]


def _ngram_counts(tokens: List[str], n: int) -> dict[tuple[str, ...], int]:
    counts: dict[tuple[str, ...], int] = {}
    if n <= 0 or len(tokens) < n:
        return counts
    for i in range(len(tokens) - n + 1):
        ngram = tuple(tokens[i : i + n])
        counts[ngram] = counts.get(ngram, 0) + 1
    return counts


def bleu(hypotheses: Sequence[str], references: Sequence[Sequence[str]] | Sequence[str], max_n: int = 4, smooth: float = 1e-9) -> float:
    """
    Minimal BLEU implementation (corpus-level) without external deps.

    hypotheses: list of hypothesis strings (len = M)
    references: either a list of reference strings (len = M), or a list of lists of references per hypothesis
    """
    # Normalize references input
    norm_refs: list[list[str]] = []
    if len(references) > 0 and isinstance(references[0], str):  # type: ignore[index]
        # single reference per hypothesis
        norm_refs = [[r] for r in references]  # type: ignore[list-item]
    else:
        norm_refs = references  # type: ignore[assignment]

    assert len(hypotheses) == len(norm_refs), "hypotheses and references length must match"

    precisions: list[float] = []
    for n in range(1, max_n + 1):
        num = 0
        den = 0
        for hyp, refs in zip(hypotheses, norm_refs):
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
    import math

    geo = math.exp(sum(math.log(p) for p in precisions) / max(1, len(precisions)))
    # brevity penalty
    hyp_len = sum(len(_tokenize(h)) for h in hypotheses)
    ref_len = 0
    for hyp, refs in zip(hypotheses, norm_refs):
        # choose ref length closest to hyp length for this hypothesis
        cand = len(_tokenize(hyp))
        best = min((abs(len(_tokenize(r)) - cand), len(_tokenize(r))) for r in refs)[1] if refs else 0
        ref_len += best
    bp = 1.0 if hyp_len > ref_len else (math.exp(1 - ref_len / max(1, hyp_len)) if hyp_len > 0 else 0.0)
    return float(bp * geo)


def rouge_l(hypotheses: Sequence[str], references: Sequence[str]) -> float:
    """Simple ROUGE-L (LCS-based) averaged over pairs."""
    def lcs(a: List[str], b: List[str]) -> int:
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
    for h, r in zip(hypotheses, references):
        ht, rt = _tokenize(h), _tokenize(r)
        if not ht or not rt:
            scores.append(0.0)
            continue
        l = lcs(ht, rt)
        prec = l / len(ht)
        rec = l / len(rt)
        denom = prec + rec if (prec + rec) > 0 else 1e-12
        f = 2 * prec * rec / denom
        scores.append(f)
    return float(sum(scores) / max(1, len(scores)))

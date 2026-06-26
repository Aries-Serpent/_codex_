"""Tests for BLEU brevity penalty alignment (P1 regression)."""

import math

from codex_ml.metrics.generation import (
    compute_brevity_penalty,
    compute_corpus_bleu,
)


def buggy_compute_brevity_penalty(hypotheses, norm_refs):
    """Replicate the old norm_refs.index(refs) misalignment for comparison."""

    hyp_len = sum(len(h.split()) for h in hypotheses)
    ref_len = 0
    for refs in norm_refs:
        idx = norm_refs.index(refs)
        cand = len(hypotheses[idx].split())
        best = 0 if not refs else min((abs(len(r.split()) - cand), len(r.split())) for r in refs)[1]
        ref_len += best
    if hyp_len == 0:
        return 0.0
    if hyp_len > ref_len:
        return 1.0
    return math.exp(1.0 - ref_len / hyp_len)


def manual_brevity_penalty(hypotheses, norm_refs):
    """Manual helper aligning hypotheses and references by index."""

    hyp_len = sum(len(h.split()) for h in hypotheses)
    ref_len = 0
    for hyp, refs in zip(hypotheses, norm_refs):
        cand = len(hyp.split())
        best = 0 if not refs else min((abs(len(r.split()) - cand), len(r.split())) for r in refs)[1]
        ref_len += best
    if hyp_len == 0:
        return 0.0
    if hyp_len > ref_len:
        return 1.0
    return math.exp(1.0 - ref_len / hyp_len)


def test_brevity_penalty_alignment_differs_from_buggy_case():
    """Buggy brevity penalty diverges when reference lists are reused."""

    hyps = ["a b", "c d e f g h i j k"]  # lengths 2 and 9
    shared_refs = ["a b", "c d e f g h i j k l"]  # reference lengths 2 and 10
    # Both entries intentionally reuse an equal reference list so index() always
    # resolves to the first hypothesis.
    norm_refs = [shared_refs, list(shared_refs)]

    buggy_bp = buggy_compute_brevity_penalty(hyps, norm_refs)
    expected_bp = manual_brevity_penalty(hyps, norm_refs)
    fixed_bp = compute_brevity_penalty(hyps, norm_refs)

    assert buggy_bp != expected_bp, "buggy_bp is not valid"
    assert math.isclose(fixed_bp, expected_bp, rel_tol=1e-12)


def test_compute_corpus_bleu_uses_fixed_brevity_penalty():
    """compute_corpus_bleu relies on the fixed brevity penalty implementation."""

    hyps = ["the cat sat", "a quick fox"]
    norm_refs = [["the cat sat on the mat"], ["a quick brown fox"]]

    expected_bp = manual_brevity_penalty(hyps, norm_refs)
    # Compute unigram precision manually (matching compute_corpus_bleu logic).
    total_match = 0
    total_hyp = 0
    for hyp, refs in zip(hyps, norm_refs):
        hyp_tokens = hyp.split()
        total_hyp += len(hyp_tokens)
        ref_tokens = set()
        for r in refs:
            ref_tokens.update(r.split())
        total_match += sum(1 for tok in hyp_tokens if tok in ref_tokens)
    precision = total_match / total_hyp if total_hyp else 0.0
    expected_bleu_like = expected_bp * precision

    computed = compute_corpus_bleu(hyps, norm_refs)
    assert math.isclose(computed, expected_bleu_like, rel_tol=1e-12)


def test_empty_hypotheses_returns_zero():
    assert compute_brevity_penalty([], []) == 0.0
    assert compute_corpus_bleu([], []) == 0.0

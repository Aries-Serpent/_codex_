"""
Test Synthetic Alignment

Test module for synthetic alignment.
"""

from __future__ import annotations

import pytest

from codex_ml.eval.fallback import synthetic_alignment


def test_synthetic_alignment_handles_reference_only_tokens() -> None:
    """Fallback evaluation should tolerate reference tokens unseen in predictions."""

    summary = synthetic_alignment(["foo"], ["bar"])

    assert summary.samples == 1, "samples is not valid"
    assert summary.token_accuracy == pytest.approx(0.0), "token_accuracy is not valid"
    assert summary.exact_match == pytest.approx(0.0), "exact_match is not valid"
    assert summary.perplexity_proxy == pytest.approx(2.0), "perplexity_proxy is not valid"
    assert summary.avg_length == pytest.approx(1.0), "Length must be greater than zero"

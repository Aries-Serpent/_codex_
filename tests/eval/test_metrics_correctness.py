"""
Test Metrics Correctness

Test module for metrics correctness.
"""

import pytest

from codex_ml.metrics import metrics_deprecated as M


def test_perplexity_known_value():
    nll = [0.0, 0.0]
    targets = [0, 1]
    assert M.perplexity(nll, targets, from_logits=False) == pytest.approx(1.0)


def test_token_accuracy_known_value():
    preds = [1, 2, 3]
    targets = [1, 0, 3]
    assert M.token_accuracy(preds, targets) == pytest.approx(2 / 3)


def test_bleu_known_value():
    pytest.importorskip("nltk")
    # Use longer text for reliable BLEU computation (short texts give 0.0 due to 4-gram requirements)
    text = "the quick brown fox jumps over the lazy dog"
    score = M.bleu([text], [text], lowercase=False)
    # Ensure score is not None (dependencies available)
    assert score is not None, "BLEU returned None - check if sacrebleu/nltk is properly installed"
    # With longer text, perfect match should give high score
    assert score >= 0.9, f"Expected high BLEU for perfect match, got {score}"


def test_rouge_l_known_value():
    pytest.importorskip("rouge_score")
    result = M.rouge_l(["a b"], ["a b"], lowercase=False)
    assert result is not None, "result must be initialized"
    assert result["rougeL_f"] == pytest.approx(1.0), "Result must not be empty"

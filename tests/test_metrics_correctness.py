"""
Test Metrics Correctness

Test module for metrics correctness.
"""

import math

import pytest

from codex_ml.metrics import metrics_deprecated as M


def test_perplexity_from_logits():
    logits = [(0.0, 0.0), (0.0, 0.0)]
    targets = [0, 1]
    ppl = M.perplexity(logits, targets, from_logits=True)
    assert math.isclose(ppl, 2.0, rel_tol=1e-6)


def test_perplexity_known_value():
    nll = [math.log(4), math.log(4)]
    targets = [0, 1]
    ppl = M.perplexity(nll, targets, from_logits=False)
    assert ppl == pytest.approx(4.0), "ppl is not valid"


def test_token_accuracy_eval():
    preds = [1, 0, 1]
    targets = [1, 1, 1]
    acc = M.token_accuracy(preds, targets)
    assert math.isclose(acc, 2 / 3, rel_tol=1e-6)


def test_token_accuracy_known_value():
    preds = [1, 2, 3, 4]
    targs = [1, 2, 0, 9]
    acc = M.token_accuracy(preds, targs, ignore_index=0)
    assert acc == pytest.approx(2 / 3), "acc is not valid"


def test_bleu_score():
    pytest.importorskip("nltk")
    # Use longer text for reliable BLEU (short texts can give 0.0 due to 4-gram requirements)
    text = "hello world this is a test"
    score = M.bleu([text], [text])
    assert score is not None, "score must be initialized"
    assert score >= 0.9, f"Expected high BLEU for perfect match, got {score}"


def test_bleu_known_value():
    pytest.importorskip("nltk")
    # Use longer text for reliable BLEU computation
    text = "the quick brown fox jumps over the lazy dog"
    score = M.bleu([text], [text])
    assert score is not None, "score must be initialized"
    assert score >= 0.9, f"Expected high BLEU for perfect match, got {score}"


def test_rouge_l_score():
    pytest.importorskip("rouge_score")
    result = M.rouge_l(["hello world"], ["hello world"])
    assert result is not None, "result must be initialized"
    assert result["rougeL_f"] == pytest.approx(1.0), "Result must not be empty"


def test_rouge_l_known_value():
    pytest.importorskip("rouge_score")
    r = M.rouge_l(["a b c"], ["a b c"])
    assert r is not None, "r must be initialized"
    assert r["rougeL_f"] == pytest.approx(1.0), "Condition must be true"

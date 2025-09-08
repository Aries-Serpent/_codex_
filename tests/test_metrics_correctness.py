import math

import pytest

from codex_ml.eval import metrics


def test_perplexity_from_logits():
    logits = [(0.0, 0.0), (0.0, 0.0)]
    targets = [0, 1]
    ppl = metrics.perplexity(logits, targets, from_logits=True)
    assert math.isclose(ppl, 2.0, rel_tol=1e-6)


def test_token_accuracy_eval():
    preds = [1, 0, 1]
    targets = [1, 1, 1]
    acc = metrics.token_accuracy(preds, targets)
    assert math.isclose(acc, 2 / 3, rel_tol=1e-6)


def test_bleu_score():
    pytest.importorskip("nltk")
    score = metrics.bleu(["hello world"], ["hello world"])
    assert score == pytest.approx(1.0)


def test_rouge_l_score():
    pytest.importorskip("rouge_score")
    result = metrics.rouge_l(["hello world"], ["hello world"])
    assert result is not None
    assert result["rougeL_f"] == pytest.approx(1.0)

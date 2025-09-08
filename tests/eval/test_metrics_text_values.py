import math

import pytest

from codex_ml.eval.metrics import bleu, perplexity, rouge_l, token_accuracy


def test_basic_perplexity_and_accuracy():
    nll = [0.0, 0.0]
    targets = [0, 1]
    ppl = perplexity(nll, targets, from_logits=False)
    assert math.isclose(ppl, 1.0)

    preds = [1, 2, 3]
    acc = token_accuracy(preds, [1, 0, 3])
    assert acc == pytest.approx(2 / 3)


def test_bleu_and_rouge_identical(monkeypatch):
    pytest.importorskip("nltk")
    pytest.importorskip("rouge_score")
    cand = ["the cat is on the mat"]
    ref = ["the cat is on the mat"]
    b = bleu(cand, ref)
    assert b is not None and math.isclose(b, 1.0)
    r = rouge_l(cand, ref)
    assert r is not None and math.isclose(r["rougeL_f"], 1.0)

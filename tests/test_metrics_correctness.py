import math

import pytest

from codex_ml.eval import metrics as M


def test_perplexity_known_value():
    nll = [math.log(4), math.log(4)]
    targets = [0, 1]
    ppl = M.perplexity(nll, targets, from_logits=False)
    assert ppl == pytest.approx(4.0)


def test_token_accuracy_known_value():
    preds = [1, 2, 3, 4]
    targs = [1, 2, 0, 9]
    acc = M.token_accuracy(preds, targs, ignore_index=0)
    assert acc == pytest.approx(2 / 3)


def test_bleu_known_value():
    pytest.importorskip("nltk")
    score = M.bleu(["the cat sat"], ["the cat sat"])
    assert score == pytest.approx(1.0)


def test_rouge_l_known_value():
    pytest.importorskip("rouge_score")
    r = M.rouge_l(["a b c"], ["a b c"])
    assert r is not None
    assert r["rougeL_f"] == pytest.approx(1.0)

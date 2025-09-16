import math

import pytest

from codex_ml.eval import metrics as M


def test_token_accuracy_and_stats():
    pred = [1, 2, 3, 4]
    targ = [1, 9, 3, 4]
    stats = M.token_stats(pred, targ)
    assert stats["total"] == 4
    assert stats["correct"] == 3
    assert stats["accuracy"] == pytest.approx(0.75)
    assert M.token_accuracy(pred, targ) == pytest.approx(0.75)


def test_token_accuracy_respects_ignore_index():
    pred = [1, 2, 3]
    targ = [1, -100, 9]
    assert M.token_accuracy(pred, targ, ignore_index=-100) == pytest.approx(0.5)


def test_accuracy_metric():
    pred = [1, 0, 1, 1]
    targ = [1, 0, 0, 1]
    assert M.accuracy(pred, targ) == pytest.approx(0.75)


def test_perplexity_known_value():
    nlls = [0.0, math.log(4.0)]
    targets = [0, 1]
    ppl = M.perplexity(nlls, targets, from_logits=False)
    assert ppl == pytest.approx(2.0)


def test_perplexity_errors_on_shape():
    with pytest.raises(M.MetricError):
        M.perplexity([[0.1, 0.9]], [0, 1])


def test_f1_scores():
    preds = [1, 0, 1, 1]
    targets = [1, 0, 0, 1]
    micro = M.micro_f1(preds, targets)
    macro = M.macro_f1(preds, targets)
    assert micro == pytest.approx(0.75)
    assert 0.0 <= macro <= 1.0


def test_bleu_and_rouge_optional():
    score = M.bleu(["the cat sat"], ["the cat sat"])
    rouge = M.rouge_l(["the cat sat"], ["the cat sat"])
    if score is not None:
        assert score == pytest.approx(1.0)
    if rouge is not None:
        assert rouge["rougeL_f"] == pytest.approx(1.0)


def test_exact_match():
    assert M.exact_match_strict("foo  bar", "foo bar") == 1.0
    assert M.exact_match_strict("foo", "bar") == 0.0

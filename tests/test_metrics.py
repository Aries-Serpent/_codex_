# BEGIN: CODEX_TEST_METRICS
import math

import pytest

from codex_ml.eval import metrics as M


def test_token_accuracy_basic():
    pred = [1, 2, 3, 4, 5]
    targ = [1, 9, 3, 0, 5]
    assert M.token_accuracy(pred, targ) == pytest.approx(3 / 5)


def test_token_accuracy_ignore_index():
    pred = [1, 2, 3]
    targ = [1, -100, 9]
    assert M.token_accuracy(pred, targ, ignore_index=-100) == pytest.approx(1 / 2)


def test_exact_match_strict():
    assert M.exact_match_strict("foo  bar", "foo bar") == 1.0
    assert M.exact_match_strict("a", "b") == 0.0


def test_perplexity_from_logits_monotonic():
    # higher logit on correct class => lower ppl
    logits_low = [[0.8, 0.2], [0.8, 0.2]]  # correct class prob 0.2
    logits_high = [[0.2, 0.8], [0.2, 0.8]]  # correct class prob 0.8
    targets = [1, 1]
    ppl_low = M.perplexity(logits_low, targets, from_logits=True)
    ppl_high = M.perplexity(logits_high, targets, from_logits=True)
    assert ppl_high < ppl_low


def test_perplexity_expected_value():
    logits = [[0.0, math.log(9)]] * 2  # correct class prob 0.9
    targets = [1, 1]
    ppl = M.perplexity(logits, targets, from_logits=True)
    assert ppl == pytest.approx(1 / 0.9)


def test_bleu_and_rouge_optional():
    # should not crash if deps missing; return None
    score = M.bleu(["a b"], ["a b"])
    r = M.rouge_l(["a b"], ["a b"])
    assert (score is None) or (0.0 <= score <= 1.0)
    assert (r is None) or ("rougeL_f" in r)


def test_bleu_and_rouge_exact_values():
    pytest.importorskip("nltk")
    pytest.importorskip("rouge_score")
    cand = ["the cat sat"]
    refs = ["the cat sat"]
    assert M.bleu(cand, refs) == pytest.approx(1.0)
    rouge = M.rouge_l(cand, refs)
    assert rouge is not None
    assert rouge["rougeL_f"] == pytest.approx(1.0)


def test_token_accuracy_perfect_match():
    pred = [1, 2, 3]
    targ = [1, 2, 3]
    assert M.token_accuracy(pred, targ) == pytest.approx(1.0)


def test_perplexity_known_value():
    nll = [0.0, math.log(4)]
    targets = [0, 0]
    assert M.perplexity(nll, targets, from_logits=False) == pytest.approx(2.0)


def test_bleu_known_value():
    pytest.importorskip("nltk")
    score = M.bleu(["the cat"], ["the cat"])
    assert score == pytest.approx(1.0)


def test_rouge_l_known_value():
    pytest.importorskip("rouge_score")
    res = M.rouge_l(["hello world"], ["hello world"])
    assert res and res["rougeL_f"] == pytest.approx(1.0)
# END: CODEX_TEST_METRICS

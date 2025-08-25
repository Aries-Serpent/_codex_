# BEGIN: CODEX_TEST_METRICS
import math
import pytest
from codex_ml.eval import metrics as M

def test_token_accuracy_basic():
    pred = [1,2,3,4,5]
    targ = [1,9,3,0,5]
    assert M.token_accuracy(pred, targ) == pytest.approx(3/5)

def test_token_accuracy_ignore_index():
    pred = [1,2,3]
    targ = [1,-100,9]
    assert M.token_accuracy(pred, targ, ignore_index=-100) == pytest.approx(1/2)

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

def test_bleu_and_rouge_optional():
    # should not crash if deps missing; return None
    score = M.bleu(["a b"], ["a b"])
    r = M.rouge_l(["a b"], ["a b"])
    assert (score is None) or (0.0 <= score <= 1.0)
    assert (r is None) or ("rougeL_f" in r)
# END: CODEX_TEST_METRICS

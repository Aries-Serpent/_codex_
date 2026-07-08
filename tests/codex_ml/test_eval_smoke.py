"""
Test Eval Smoke

Test module for eval smoke.
"""

from codex_ml.eval import evaluator


def test_evaluate_constant_nonzero_for_match():
    preds = [1, 2, 3]
    targs = [1, 99, 3]
    score = evaluator.evaluate_constant(preds, targs)
    assert 0.0 < score < 1.0, "0 is not valid"

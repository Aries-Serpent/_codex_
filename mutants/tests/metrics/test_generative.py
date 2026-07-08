"""
Test Generative

Test module for generative.
"""

from codex_ml.metrics.generative import bleu, rouge_l


def test_bleu_and_rouge_l_basic():
    predictions = ["the cat is on the mat", "hello there general"]
    targets = ["the cat sat on the mat", "hello there"]

    bleu_score = bleu(predictions, targets)
    rouge_score = rouge_l(predictions, targets)

    assert 0.0 <= bleu_score <= 1.0, "0 is not valid"
    assert 0.0 <= rouge_score <= 1.0, "0 is not valid"
    assert bleu_score < 1.0, "bleu_score is not valid"
    assert rouge_score < 1.0, "rouge_score is not valid"


def test_bleu_zero_when_no_overlap():
    predictions = ["abc def", "ghi"]
    targets = ["uvw xyz", "jkl"]

    # When there's no overlap, BLEU should be 0 or very close to 0
    bleu_score = bleu(predictions, targets)
    rouge_score = rouge_l(predictions, targets)

    assert bleu_score == 0.0 or bleu_score < 1e-6, f"Expected BLEU to be 0.0, got {bleu_score}"
    assert rouge_score == 0.0, "rouge_score is not valid"

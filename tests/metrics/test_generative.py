from codex_ml.metrics.generative import bleu, rouge_l


def test_bleu_and_rouge_l_basic():
    predictions = ["the cat is on the mat", "hello there general"]
    targets = ["the cat sat on the mat", "hello there"]

    bleu_score = bleu(predictions, targets)
    rouge_score = rouge_l(predictions, targets)

    assert 0.0 <= bleu_score <= 1.0
    assert 0.0 <= rouge_score <= 1.0
    assert bleu_score < 1.0
    assert rouge_score < 1.0


def test_bleu_zero_when_no_overlap():
    predictions = ["abc def", "ghi"]
    targets = ["uvw xyz", "jkl"]

    assert bleu(predictions, targets) == 0.0
    assert rouge_l(predictions, targets) == 0.0

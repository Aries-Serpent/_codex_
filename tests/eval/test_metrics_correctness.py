import pytest

from codex_ml.eval import metrics as M


def test_perplexity_known_value():
    nll = [0.0, 0.0]
    targets = [0, 1]
    assert M.perplexity(nll, targets, from_logits=False) == pytest.approx(1.0)


def test_token_accuracy_known_value():
    preds = [1, 2, 3]
    targets = [1, 0, 3]
    assert M.token_accuracy(preds, targets) == pytest.approx(2 / 3)


def test_bleu_known_value():
    pytest.importorskip("nltk")
    score = M.bleu(["the cat sat"], ["the cat sat"], lowercase=False)
    assert score == pytest.approx(1.0)


def test_rouge_l_known_value():
    pytest.importorskip("rouge_score")
    result = M.rouge_l(["a b"], ["a b"], lowercase=False)
    assert result is not None
    assert result["rougeL_f"] == pytest.approx(1.0)

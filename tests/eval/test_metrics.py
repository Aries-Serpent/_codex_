import math

from codex_ml.eval.metrics import perplexity, token_accuracy


def test_perplexity_from_logits():
    logits = [[1.0, 0.0], [0.0, 1.0]]
    targets = [0, 1]
    ppl = perplexity(logits, targets, from_logits=True)
    expected = math.exp(-(math.log(math.e / (math.e + 1)) + math.log(math.e / (math.e + 1))) / 2)
    assert abs(ppl - expected) < 1e-3


def test_token_accuracy():
    preds = [1, 2, 3, 4]
    targets = [1, 0, 3, 5]
    acc = token_accuracy(preds, targets)
    assert acc == 0.5

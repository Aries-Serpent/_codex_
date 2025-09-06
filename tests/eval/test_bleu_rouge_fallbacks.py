import sys

from codex_ml.metrics.registry import get_metric


def test_bleu_rouge_fallbacks(monkeypatch):
    monkeypatch.setitem(sys.modules, "nltk", None)
    monkeypatch.setitem(sys.modules, "rouge_score", None)
    bleu = get_metric("bleu")
    rouge = get_metric("rougeL")
    assert bleu(["a"], ["a"]) is None
    assert rouge(["a"], ["a"]) is None

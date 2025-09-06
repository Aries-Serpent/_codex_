import builtins

from codex_ml.metrics.registry import get_metric


def test_bleu_rouge_fallbacks(monkeypatch):
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name.startswith("nltk") or name.startswith("rouge_score"):
            raise ImportError("missing optional dependency")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    bleu = get_metric("bleu")
    rouge = get_metric("rougeL")
    assert bleu(["a"], ["a"]) is None
    assert rouge(["a"], ["a"]) is None

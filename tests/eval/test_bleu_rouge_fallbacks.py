import builtins
import json

from codex_ml.eval.eval_runner import evaluate_datasets
from codex_ml.metrics.registry import get_metric


def test_bleu_rouge_fallbacks(monkeypatch, tmp_path):
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

    out = tmp_path
    evaluate_datasets(["toy_copy_task"], ["bleu", "rougeL"], out)
    nd = out / "metrics.ndjson"
    rows = [json.loads(line) for line in nd.read_text().splitlines()]
    assert len(rows) == 2
    assert all(r["value"] is None for r in rows)

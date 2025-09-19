import json
from pathlib import Path

import pytest

pytest.importorskip("transformers")
pytest.importorskip("torch")

from codex_ml.eval.evaluator import run_evaluator
from codex_ml.safety.filters import SafetyFilters


def test_eval_and_error_logging(monkeypatch):
    metrics = run_evaluator("sshleifer/tiny-gpt2", ["hello world"])
    assert "perplexity" in metrics
    err_path = Path(".codex/errors.ndjson")
    if err_path.exists():
        err_path.unlink()
    monkeypatch.setenv("CODEX_SAFETY_CLASSIFIER", "missing:hook")
    filt = SafetyFilters.from_defaults()
    filt.is_allowed("hi")
    data = json.loads(err_path.read_text().strip().splitlines()[-1])
    assert data["step"] == "safety_classifier"

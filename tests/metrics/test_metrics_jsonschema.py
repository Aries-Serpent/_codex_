from pathlib import Path
import json
import pytest


jsonschema = pytest.importorskip("jsonschema", reason="jsonschema not installed")
from jsonschema import Draft7Validator  # type: ignore


METRICS_SCHEMA = {
    "type": "object",
    "properties": {
        "phase": {"type": "string"},
        "prefix": {"type": "string"},
        "epoch": {"type": "integer"},
        "cfg_hash": {"type": "string"},
        "config_id": {"type": "string"},
        "metrics": {"type": "object", "additionalProperties": {"type": ["number", "integer"]}},
        "timestamp": {"type": "string"},
        "notes": {"type": "string"},
    },
    "required": ["phase", "prefix", "epoch", "cfg_hash", "config_id", "metrics", "timestamp"],
    "additionalProperties": True,
}


def test_metrics_history_matches_schema(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from src.codex_ml.train_loop import record_metrics

    record_metrics(prefix="train", epoch=0, metrics={"loss": 1.0}, config_id="cfg-1")
    record_metrics(prefix="train", epoch=1, metrics={"loss": 0.9, "acc": 0.1}, config_id="cfg-1")

    history_path = Path("artifacts") / "metrics.json"
    assert history_path.exists()
    history = json.loads(history_path.read_text(encoding="utf-8"))
    assert isinstance(history, list) and len(history) >= 2

    validator = Draft7Validator(METRICS_SCHEMA)
    for entry in history:
        validator.validate(entry)


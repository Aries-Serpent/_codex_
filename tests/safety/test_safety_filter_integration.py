import json
from types import SimpleNamespace

from codex_ml.data.loaders import stream_paths
from codex_ml.safety.filters import REDACT_TOKEN


def _cfg(enabled: bool):
    return SimpleNamespace(data=SimpleNamespace(safety_filter_enabled=enabled))


def test_loader_redacts_when_enabled(tmp_path):
    path = tmp_path / "data.jsonl"
    path.write_text(json.dumps({"prompt": "my credit card", "completion": "credit card"}) + "\n")
    cfg = _cfg(True)
    items = list(stream_paths([path], cfg=cfg))
    assert items[0].prompt == "my " + REDACT_TOKEN
    assert items[0].completion == REDACT_TOKEN


def test_loader_no_redact_when_disabled(tmp_path):
    path = tmp_path / "data.jsonl"
    path.write_text(json.dumps({"prompt": "my credit card", "completion": "credit card"}) + "\n")
    cfg = _cfg(False)
    items = list(stream_paths([path], cfg=cfg))
    assert items[0].prompt == "my credit card"
    assert items[0].completion == "credit card"

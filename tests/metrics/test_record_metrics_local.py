from pathlib import Path
import json


def test_record_metrics_writes_json_and_ndjson(tmp_path: Path, monkeypatch):
    # Ensure artifacts directory is under tmp_path to avoid polluting repo artifacts
    monkeypatch.chdir(tmp_path)
    from src.codex_ml.train_loop import record_metrics

    ndjson = record_metrics(prefix="train", epoch=0, metrics={"loss": 1.0}, config_id="cfg")
    assert ndjson.exists()
    lines = ndjson.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    assert "\"loss\": 1.0" in lines[0]
    # JSON history file also written
    history_path = ndjson.parent / "metrics.json"
    assert history_path.exists()
    data = json.loads(history_path.read_text(encoding="utf-8"))
    assert isinstance(data, list) and data and data[0]["metrics"]["loss"] == 1.0


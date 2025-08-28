from codex_ml import train_loop


def test_record_metrics_ndjson(tmp_path, monkeypatch):
    monkeypatch.setattr(train_loop, "ART_DIR", tmp_path)
    train_loop.record_metrics("p", 0, {"a": 1}, "cfg")
    train_loop.record_metrics("p", 1, {"a": 2}, "cfg")
    lines = (tmp_path / "metrics.ndjson").read_text().strip().splitlines()
    assert len(lines) == 2
    data = [__import__("json").loads(line) for line in lines]
    assert data[0]["epoch"] == 0
    assert data[1]["epoch"] == 1

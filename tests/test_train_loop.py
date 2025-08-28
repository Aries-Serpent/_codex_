import json
import sys

import pytest


@pytest.fixture
def artifacts(tmp_path):
    d = tmp_path / "artifacts" / "metrics"
    d.mkdir(parents=True)
    return d


def test_record_metrics_writes_json(tmp_path, artifacts, monkeypatch):
    from codex_ml import train_loop

    monkeypatch.setattr(train_loop, "ART_DIR", artifacts, raising=False)

    train_loop.record_metrics(
        phase="eval",
        epoch=1,
        metrics={"accuracy": 1.0},
        cfg_hash="deadbeef",
        notes="unit-test",
    )

    metrics_json = artifacts / "metrics.json"
    metrics_ndjson = artifacts / "metrics.ndjson"
    assert metrics_json.exists() and metrics_ndjson.exists()

    data = json.loads(metrics_json.read_text())
    assert isinstance(data, list) and data[-1]["metrics"]["accuracy"] == 1.0


def test_record_metrics_error_path(monkeypatch, tmp_path, artifacts):
    from codex_ml import train_loop

    monkeypatch.setattr(train_loop, "ART_DIR", artifacts, raising=False)

    def bad_dumps(*a, **k):
        raise OSError("disk full")

    monkeypatch.setattr(json, "dumps", bad_dumps)

    with pytest.raises(OSError):
        train_loop.record_metrics(
            phase="eval",
            epoch=0,
            metrics={"x": 1},
            cfg_hash="deadbeef",
        )


def test_cli_parsing_smoke(monkeypatch, tmp_path, capsys):
    from codex_ml import train_loop

    monkeypatch.chdir(tmp_path)

    argv_backup = sys.argv[:]
    try:
        sys.argv = ["prog", "--epochs", "1", "--grad-accum", "1"]
        train_loop.main()
    finally:
        sys.argv = argv_backup


def test_empty_dataset_path(monkeypatch):
    from codex_ml import train_loop

    assert isinstance(train_loop.demo_epoch(epoch=0), dict)


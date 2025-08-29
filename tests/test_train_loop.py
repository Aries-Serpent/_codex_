# BEGIN: CODEX_TEST_TRAIN_LOOP
import json
import sys
from datetime import datetime

import pytest

from codex_ml import train_loop


@pytest.mark.parametrize("initial", ["not-json", "{}"])
def test_record_metrics_recovers_from_bad_file(tmp_path, monkeypatch, initial):
    monkeypatch.setattr(train_loop, "ART_DIR", tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / "metrics.json").write_text(initial, encoding="utf-8")
    train_loop.record_metrics("phase", 1, {"a": 1}, "cfg")
    data = json.loads((tmp_path / "metrics.json").read_text(encoding="utf-8"))
    assert isinstance(data, list) and data[0]["phase"] == "phase"
    nd = (tmp_path / "metrics.ndjson").read_text(encoding="utf-8").strip()
    assert nd


def test_ts_format():
    ts = train_loop._ts()
    assert ts.endswith("Z")
    datetime.fromisoformat(ts[:-1])


def test_main_creates_metrics_files(tmp_path, monkeypatch):
    monkeypatch.setattr(train_loop, "ART_DIR", tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(
        sys, "argv", ["train_loop", "--epochs", "1", "--grad-accum", "2"]
    )
    train_loop.main()
    data = json.loads((tmp_path / "metrics.json").read_text(encoding="utf-8"))
    assert data[0]["metrics"]["grad_accum"] == 2
    assert (tmp_path / "metrics.ndjson").exists()


def test_record_metrics_unserializable(tmp_path, monkeypatch):
    class Bad:
        pass
    monkeypatch.setattr(train_loop, "ART_DIR", tmp_path)
    with pytest.raises(TypeError):
        train_loop.record_metrics("phase", 1, {"bad": Bad()}, "cfg")
# END: CODEX_TEST_TRAIN_LOOP

from __future__ import annotations

import contextlib
import importlib
import sys
from pathlib import Path
from types import SimpleNamespace


def test_start_run_no_mlflow(monkeypatch):
    mod = importlib.import_module("codex_ml.tracking.mlflow_utils")
    monkeypatch.setitem(sys.modules, "mlflow", None)
    with mod.start_run("exp") as run:
        assert run is None


def test_seed_snapshot(tmp_path, monkeypatch):
    mod = importlib.import_module("codex_ml.tracking.mlflow_utils")
    called = {}

    def fake_log(path, **_: object):
        called["path"] = Path(path)

    monkeypatch.setattr(mod, "log_artifacts", fake_log)
    out = mod.seed_snapshot({"a": 1}, tmp_path)
    assert out.exists()
    assert called["path"] == out


def test_start_run_sets_tracking(monkeypatch, tmp_path):
    mod = importlib.import_module("codex_ml.tracking.mlflow_utils")
    called = []
    fake = SimpleNamespace(
        set_tracking_uri=lambda uri: called.append(("uri", uri)),
        set_experiment=lambda exp: called.append(("exp", exp)),
        start_run=lambda: contextlib.nullcontext("run"),
    )
    monkeypatch.setitem(sys.modules, "mlflow", fake)
    with mod.start_run("e", tracking_uri=str(tmp_path)) as run:
        assert run == "run"
    assert ("uri", str(tmp_path)) in called and ("exp", "e") in called

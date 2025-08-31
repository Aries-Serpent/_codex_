import json
import sys
from pathlib import Path
from typing import Any, Dict

import pytest

from codex_ml.tracking import MlflowConfig, ensure_local_artifacts, seed_snapshot, start_run


def test_start_run_no_mlflow(monkeypatch):
    """
    When the 'mlflow' package is not present, different branches of the codebase
    have historically either returned a context manager that yields None or
    raised a RuntimeError. Accept either behavior:

    - If a context manager is returned, it should yield a falsy value (None/False).
    - If mlflow import fails inside the helper, a RuntimeError is acceptable.
    """
    monkeypatch.setitem(sys.modules, "mlflow", None)

    try:
        with start_run("exp") as run:
            # accept both None and False as reasonable "not available" results
            assert run in (None, False)
    except RuntimeError:
        # Accept raising RuntimeError as an allowed behavior when mlflow is missing.
        pass


def test_start_run_disabled() -> None:
    """When MlflowConfig.enable is False, start_run should be a no-op yielding False."""
    cfg = MlflowConfig(enable=False)
    with start_run(cfg) as run:
        assert run is False


def test_seed_snapshot(tmp_path: Path) -> None:
    """seed_snapshot writes seeds.json and returns its path."""
    seeds = {"python": 0}
    path = seed_snapshot(seeds, tmp_path)
    assert json.loads(path.read_text()) == seeds


def test_seed_snapshot_logs_artifact(tmp_path: Path, monkeypatch) -> None:
    """
    seed_snapshot should write seeds.json and call the artifact-logging helper.

    Different code paths historically accepted different function signatures for
    the log_artifacts helper; support either by using a flexible fake.
    """
    from codex_ml.tracking import mlflow_utils as mfu

    logged: Dict[str, str] = {}

    def fake_log(p: Path | str, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
        logged["path"] = str(p)

    monkeypatch.setattr(mfu, "log_artifacts", fake_log)
    out = mfu.seed_snapshot({"seed": 1}, tmp_path, enabled=True)
    assert out.exists() and logged["path"] == str(out)


def test_ensure_local_artifacts(tmp_path: Path) -> None:
    """ensure_local_artifacts writes both summary.json and seeds.json locally."""
    summary = {"status": "ok"}
    seeds = {"numpy": 1}
    ensure_local_artifacts(tmp_path, summary, seeds)
    assert json.loads((tmp_path / "summary.json").read_text()) == summary
    assert json.loads((tmp_path / "seeds.json").read_text()) == seeds

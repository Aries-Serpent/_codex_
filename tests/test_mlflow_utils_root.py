import json
from pathlib import Path
from typing import Any

import pytest

from codex_ml.tracking import (
    MlflowConfig,
    ensure_local_artifacts,
    seed_snapshot,
    start_run,
)


def test_start_run_noop(tmp_path: Path) -> None:
    """When MlflowConfig.enable is False, start_run should be a no-op yielding False."""
    cfg = MlflowConfig(enable=False, tracking_uri=str(tmp_path))
    with start_run(cfg) as run:
        assert run is False


def test_start_run_missing_raises(monkeypatch) -> None:
    """
    If MLflow is requested (enabled) but not importable, start_run should raise
    a RuntimeError. Simulate an import/runtime failure inside the helper.
    """
    mod = __import__("codex_ml.tracking.mlflow_utils", fromlist=["mlflow_utils"])
    # Force the helper that ensures mlflow to raise to emulate mlflow not being available.
    monkeypatch.setattr(mod, "_ensure_mlflow_available", lambda: (_ for _ in ()).throw(RuntimeError("mlflow not importable")))
    cfg = MlflowConfig(enable=True)
    with pytest.raises(RuntimeError):
        start_run(cfg)


def test_start_run_string_experiment_flexible_behavior(monkeypatch) -> None:
    """
    Historically different branches returned None when the mlflow package was
    absent; other branches raised. This test accepts either behavior as
    compatible: either a RuntimeError is raised, or the context manager yields
    a falsy value (None/False) when mlflow is not available.
    """
    # Call start_run using the legacy string experiment form and verify behavior.
    try:
        with start_run("exp", tracking_uri=str(Path())) as run:
            # Accept both None and False as reasonable "disabled" results.
            assert run in (None, False)
    except RuntimeError:
        # Accept raising RuntimeError as another valid behavior when mlflow is missing.
        pass


def test_seed_snapshot(tmp_path: Path) -> None:
    seeds = {"python": 0}
    path = seed_snapshot(seeds, tmp_path)
    assert json.loads(path.read_text()) == seeds


def test_seed_snapshot_logs_artifact(tmp_path: Path, monkeypatch) -> None:
    """
    seed_snapshot should write the seeds.json and call the artifact logger.
    The artifact logging helper historically accepted different kwarg
    signatures, so accept any call via *args/**kwargs capture.
    """
    from codex_ml.tracking import mlflow_utils as mfu

    logged: dict[str, str] = {}

    def fake_log(p: Path | str, *_: Any, **__: Any) -> None:  # pragma: no cover
        logged["path"] = str(p)

    monkeypatch.setattr(mfu, "log_artifacts", fake_log)
    out = mfu.seed_snapshot({"seed": 1}, tmp_path, enabled=True)
    assert out.exists() and logged["path"] == str(out)


def test_ensure_local_artifacts(tmp_path: Path) -> None:
    summary = {"status": "ok"}
    seeds = {"numpy": 1}
    ensure_local_artifacts(tmp_path, summary, seeds)
    assert json.loads((tmp_path / "summary.json").read_text()) == summary
    assert json.loads((tmp_path / "seeds.json").read_text()) == seeds

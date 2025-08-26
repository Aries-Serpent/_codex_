from __future__ import annotations

import json
from pathlib import Path

import pytest

from codex_ml.tracking import (
    MlflowConfig,
    ensure_local_artifacts,
    seed_snapshot,
    start_run,
)


def test_start_run_noop(tmp_path: Path) -> None:
    cfg = MlflowConfig(enable=False)
    with start_run(cfg) as run:
        assert run is False


def test_start_run_missing_mlflow_raises() -> None:
    cfg = MlflowConfig(enable=True)
    with pytest.raises(RuntimeError):
        with start_run(cfg):
            pass


def test_seed_snapshot(tmp_path: Path) -> None:
    seeds = {"python": 0}
    path = seed_snapshot(seeds, tmp_path)
    assert json.loads(path.read_text()) == seeds


def test_ensure_local_artifacts(tmp_path: Path) -> None:
    summary = {"status": "ok"}
    seeds = {"numpy": 1}
    ensure_local_artifacts(tmp_path, summary, seeds)
    assert json.loads((tmp_path / "summary.json").read_text()) == summary
    assert json.loads((tmp_path / "seeds.json").read_text()) == seeds

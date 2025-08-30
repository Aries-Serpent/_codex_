from __future__ import annotations

import json
from pathlib import Path

from codex_ml.tracking import ensure_local_artifacts, seed_snapshot, start_run


def test_start_run_noop(tmp_path: Path) -> None:
    with start_run("exp", tracking_uri=str(tmp_path)) as run:
        assert run is None


def test_seed_snapshot(tmp_path: Path) -> None:
    seeds = {"python": 0}
    path = seed_snapshot(seeds, tmp_path)
    assert json.loads(path.read_text()) == seeds


def test_seed_snapshot_logs_artifact(tmp_path: Path, monkeypatch) -> None:
    from codex_ml.tracking import mlflow_utils as mfu

    logged: dict[str, str] = {}

    def fake_log(
        p: Path, *, enabled: bool | None = None
    ) -> None:  # pragma: no cover - monkeypatched
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

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import pytest


@dataclass
class _Snapshot:
    S_proxy: float
    rho_dev_proxy: float
    curvature_proxy: float
    lambda_auto_index: float
    src_loc: int
    tests_loc: int
    test_density: float
    modules: int
    import_edges: int
    scc_cycles: int
    cycle_nodes: int


def test_metrics_collector_enforces_local_mlflow(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from codex_addons.metrics import collector

    recorded: dict[str, object] = {}

    class _DummyRun:
        def __enter__(self) -> "_DummyRun":  # pragma: no cover - trivial
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:  # pragma: no cover - trivial
            return False

    class _DummyMlflow:
        def set_tracking_uri(self, uri: str) -> None:  # pragma: no cover - trivial
            recorded["uri"] = uri

        def start_run(self, run_name: str | None = None) -> _DummyRun:  # pragma: no cover
            recorded["run_name"] = run_name
            return _DummyRun()

        def log_params(self, params: dict[str, object]) -> None:  # pragma: no cover
            recorded["params"] = params

        def log_metrics(self, metrics: dict[str, float]) -> None:  # pragma: no cover
            recorded["metrics"] = metrics

    monkeypatch.setenv("MLFLOW_TRACKING_URI", "http://example.com")
    monkeypatch.delenv("CODEX_MLFLOW_LOCAL_DIR", raising=False)
    monkeypatch.setattr(collector, "_try_mlflow", lambda: _DummyMlflow())

    snapshot = _Snapshot(
        S_proxy=1.0,
        rho_dev_proxy=1.0,
        curvature_proxy=1.0,
        lambda_auto_index=1.0,
        src_loc=1,
        tests_loc=1,
        test_density=1.0,
        modules=1,
        import_edges=1,
        scc_cycles=0,
        cycle_nodes=0,
    )

    monkeypatch.setattr(collector, "_scan_repo", lambda root: (snapshot, {"dummy": 1}))
    monkeypatch.setattr(collector, "_ensure_db", lambda db: None)
    monkeypatch.setattr(collector, "_insert_run", lambda db, run: 1)
    monkeypatch.setattr(collector, "_insert_metrics", lambda db, run_id, metrics: None)
    monkeypatch.setattr(collector, "_get_prev_S", lambda db, session_id: None)

    artifacts_dir = tmp_path / "artifacts"
    collector.main(["--root", str(tmp_path), "--artifacts", str(artifacts_dir)])

    assert recorded["uri"].startswith("file:")
    assert os.environ["MLFLOW_TRACKING_URI"].startswith("file:")
    local_dir = Path(os.environ["CODEX_MLFLOW_LOCAL_DIR"])
    assert local_dir.is_absolute()
    assert local_dir.is_dir()
    assert local_dir.parent == artifacts_dir

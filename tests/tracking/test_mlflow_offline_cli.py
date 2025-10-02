import importlib
import json
import sys
import types

import pytest


def _install_stub_mlflow(monkeypatch: pytest.MonkeyPatch) -> types.ModuleType:
    module = types.ModuleType("mlflow")

    class _DummyRun:
        def __enter__(self):  # pragma: no cover - trivial
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:  # pragma: no cover - trivial
            return False

    def set_tracking_uri(uri: str) -> None:
        module.tracking_uri = uri

    def set_experiment(name: str) -> None:
        module.experiment = name

    def start_run(run_name: str | None = None):
        module.run_name = run_name
        return _DummyRun()

    def set_tags(tags) -> None:
        module.tags = dict(tags)

    def log_metric(name: str, value: float, step: int) -> None:
        metrics = getattr(module, "metrics", [])
        metrics.append((name, value, step))
        module.metrics = metrics

    def log_params(params):
        module.params = dict(params)

    def log_artifact(path: str) -> None:
        module.artifact = path

    def log_artifacts(path: str) -> None:  # pragma: no cover - compatibility
        module.artifacts_path = path

    def end_run() -> None:  # pragma: no cover - trivial
        module.ended = True

    module.set_tracking_uri = set_tracking_uri
    module.set_experiment = set_experiment
    module.start_run = start_run
    module.set_tags = set_tags
    module.log_metric = log_metric
    module.log_params = log_params
    module.log_artifact = log_artifact
    module.log_artifacts = log_artifacts
    module.end_run = end_run

    monkeypatch.setitem(sys.modules, "mlflow", module)
    return module


def test_mlflow_offline_smoke_enforces_file_uri(tmp_path, monkeypatch):
    monkeypatch.delenv("CODEX_MLFLOW_LOCAL_DIR", raising=False)
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    monkeypatch.delenv("MLFLOW_ALLOW_REMOTE", raising=False)

    _install_stub_mlflow(monkeypatch)
    module = importlib.import_module("examples.mlflow_offline")
    module = importlib.reload(module)

    output = tmp_path / "offline"
    uri = module.run_smoke(output)

    assert uri.startswith("file:")
    run_dir = output / "offline-smoke"
    summary_path = run_dir / "tracking_summary.ndjson"
    metrics_path = run_dir / "metrics.ndjson"
    assert summary_path.exists()
    assert metrics_path.exists()

    summary_lines = [json.loads(line) for line in summary_path.read_text().splitlines() if line]
    assert summary_lines
    extra = summary_lines[-1]["extra"]
    assert extra["effective_uri"] == uri
    assert extra["fallback_reason"] in {"", "non_local_uri"}

    metrics_lines = [json.loads(line) for line in metrics_path.read_text().splitlines() if line]
    assert metrics_lines
    record = metrics_lines[-1]
    assert record["metric"] == "loss"


def test_mlflow_offline_smoke_rejects_remote_without_override(tmp_path, monkeypatch):
    monkeypatch.delenv("CODEX_MLFLOW_LOCAL_DIR", raising=False)
    monkeypatch.delenv("MLFLOW_TRACKING_URI", raising=False)
    monkeypatch.delenv("MLFLOW_ALLOW_REMOTE", raising=False)

    _install_stub_mlflow(monkeypatch)
    module = importlib.import_module("examples.mlflow_offline")
    module = importlib.reload(module)

    with pytest.raises(SystemExit):
        module.run_smoke(tmp_path / "offline", tracking_uri="https://example.com/mlflow")

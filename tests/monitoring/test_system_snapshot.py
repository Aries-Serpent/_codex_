from __future__ import annotations

from types import SimpleNamespace

from codex_ml.monitoring import system_metrics


def test_system_snapshot_resilient(monkeypatch):
    monkeypatch.setattr(system_metrics, "HAS_PSUTIL", False, raising=False)
    monkeypatch.setattr(system_metrics, "_CONFIG", SimpleNamespace(use_psutil=False), raising=False)
    snap = system_metrics.system_snapshot()
    assert "cpu" in snap and snap["cpu"]
    assert snap["errors"] == []


def test_system_snapshot_handles_failures(monkeypatch):
    def boom(*args, **kwargs):  # noqa: ARG001
        raise RuntimeError("boom")

    monkeypatch.setattr(system_metrics, "_sample_cpu_psutil", boom, raising=False)
    monkeypatch.setattr(system_metrics, "_CONFIG", SimpleNamespace(use_psutil=True), raising=False)
    monkeypatch.setattr(system_metrics, "HAS_PSUTIL", True, raising=False)
    monkeypatch.setattr(system_metrics, "psutil", object(), raising=False)
    snap = system_metrics.system_snapshot()
    assert snap["errors"]
    assert snap["errors"][0]["component"] == "cpu"

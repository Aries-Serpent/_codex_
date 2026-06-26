"""
Test System Snapshot

Test module for system snapshot.
"""

from __future__ import annotations

from types import SimpleNamespace

from codex_ml.monitoring import system_metrics


def test_system_snapshot_resilient(monkeypatch):
    monkeypatch.setattr(system_metrics, "HAS_PSUTIL", False, raising=False)
    monkeypatch.setattr(system_metrics, "_CONFIG", SimpleNamespace(use_psutil=False), raising=False)
    snap = system_metrics.system_snapshot()
    assert snap.get("cpu"), "Condition must be true"
    assert snap["errors"] == [], "Error should be raised or set"


def test_system_snapshot_handles_failures(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(system_metrics, "_sample_cpu_psutil", boom, raising=False)
    monkeypatch.setattr(system_metrics, "_CONFIG", SimpleNamespace(use_psutil=True), raising=False)
    monkeypatch.setattr(system_metrics, "HAS_PSUTIL", True, raising=False)
    monkeypatch.setattr(system_metrics, "psutil", object(), raising=False)
    snap = system_metrics.system_snapshot()
    assert snap["errors"], "Error should be raised or set"
    assert snap["errors"][0]["component"] == "cpu", "Error should be raised or set"

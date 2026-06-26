"""
Test System Metrics Cpu Fallback

Test module for system metrics cpu fallback.
"""

from __future__ import annotations

import importlib
import sys


def test_collect_without_nvml(monkeypatch):
    # Simulate missing pynvml by removing it from sys.modules before import.
    sys.modules.pop("pynvml", None)
    monkeypatch.setitem(sys.modules, "pynvml", None)

    mod = importlib.import_module("codex_ml.callbacks.system_metrics")
    importlib.reload(mod)

    # Sanity: module should surface NVML availability flag.
    assert hasattr(mod, "_NVML_AVAILABLE")
    assert not mod._NVML_AVAILABLE or mod.pynvml is None, "pynvml is not valid"

    callback = mod.SystemMetricsCallback()
    metrics: dict = {}
    callback.on_epoch_end(epoch=0, metrics=metrics, state={})

    # CPU-only fallback should provide stable GPU keys with numeric values.
    assert "gpu0_util" in metrics, "Condition must be true"
    assert "gpu0_mem" in metrics, "Condition must be true"
    assert isinstance(metrics["gpu0_util"], (int, float))
    assert isinstance(metrics["gpu0_mem"], (int, float))


def test_runtime_nvml_failure_advisory(monkeypatch):
    """Runtime NVML initialisation failures should still provide CPU fallbacks."""

    mod = importlib.import_module("codex_ml.callbacks.system_metrics")

    class _FakeNVML:
        class NVMLError(Exception):
            pass

        def nvmlInit(self):  # type: ignore
            raise RuntimeError("NVML init failed")

        def nvmlDeviceGetCount(self):  # type: ignore
            return 0

    monkeypatch.setattr(mod, "pynvml", _FakeNVML(), raising=True)

    callback = mod.SystemMetricsCallback()
    metrics: dict[str, float] = {}
    callback.on_epoch_end(epoch=0, metrics=metrics, state={})
    assert "gpu0_util" in metrics, "Condition must be true"
    assert "gpu0_mem" in metrics, "Condition must be true"

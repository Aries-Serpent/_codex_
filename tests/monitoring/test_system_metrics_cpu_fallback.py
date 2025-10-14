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
    assert not mod._NVML_AVAILABLE or mod.pynvml is None

    callback = mod.SystemMetricsCallback()
    metrics: dict = {}
    callback.on_epoch_end(epoch=0, metrics=metrics, state={})

    # CPU-only fallback should provide stable GPU keys with numeric values.
    assert "gpu0_util" in metrics
    assert "gpu0_mem" in metrics
    assert isinstance(metrics["gpu0_util"], (int, float))
    assert isinstance(metrics["gpu0_mem"], (int, float))

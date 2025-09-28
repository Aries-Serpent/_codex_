from __future__ import annotations

import importlib

from codex_ml.monitoring.microhelpers import get_gpu_stats, sample


def test_sample_shape_never_raises():
    s = sample()
    assert set(s.keys()) == {"ts", "proc", "sys", "gpu"}
    assert isinstance(s["proc"], dict)
    assert isinstance(s["sys"], dict)
    assert isinstance(s["gpu"], list)


def test_gpu_stats_dont_crash_without_nvml(monkeypatch):
    # Simulate missing pynvml symbols
    mod = importlib.import_module("codex_ml.monitoring.microhelpers")
    for name in [
        "nvmlInit",
        "nvmlShutdown",
        "nvmlDeviceGetCount",
        "nvmlDeviceGetHandleByIndex",
        "nvmlDeviceGetName",
        "nvmlDeviceGetUtilizationRates",
        "nvmlDeviceGetMemoryInfo",
        "nvmlDeviceGetTemperature",
        "NVML_TEMPERATURE_GPU",
        "NVMLError",
    ]:
        monkeypatch.setitem(mod.__dict__, name, None)
    assert isinstance(get_gpu_stats(), list)


# WHY: Ensures guards & shapes are stable even without optional deps.

"""Unit tests for monitoring system metrics feature toggles."""

from __future__ import annotations

import builtins
import importlib
from types import SimpleNamespace

import pytest

from codex_ml.monitoring import system_metrics


def test_structured_warning_on_psutil_import_failure(caplog) -> None:
    """Reloading the module without psutil logs a structured warning."""

    original_import = builtins.__import__

    def _fake_import(name: str, *args, **kwargs):
        if name == "psutil":
            raise ImportError("simulated psutil failure")
        return original_import(name, *args, **kwargs)

    mp = pytest.MonkeyPatch()
    mp.setenv("CODEX_MONITORING_ENABLE_PSUTIL", "1")
    mp.setenv("CODEX_MONITORING_DISABLE_GPU", "1")
    mp.setattr(builtins, "__import__", _fake_import)

    caplog.set_level("WARNING")

    try:
        reloaded = importlib.reload(system_metrics)
        assert not reloaded.HAS_PSUTIL
        payload = reloaded.sample_system_metrics()
        assert "cpu_percent" in payload
        structured = [r for r in caplog.records if r.__dict__.get("dependency") == "psutil"]
        assert (
            structured
            and structured[0].__dict__.get("event") == "system_metrics.dependency_missing"
        )
    finally:
        mp.undo()
        importlib.reload(system_metrics)


def test_config_disable_gpu_polling(monkeypatch) -> None:
    """Explicit config disables NVML polling even when the stub is available."""

    stub = SimpleNamespace(
        nvmlInit=lambda: None,
        nvmlDeviceGetCount=lambda: 1,
        nvmlDeviceGetHandleByIndex=lambda idx: idx,
        nvmlDeviceGetUtilizationRates=lambda handle: SimpleNamespace(gpu=50.0),
        nvmlDeviceGetMemoryInfo=lambda handle: SimpleNamespace(used=1024.0, total=2048.0),
        nvmlDeviceGetTemperature=lambda handle, _: 65.0,
        nvmlDeviceGetPowerUsage=lambda handle: 55000.0,
        nvmlShutdown=lambda: None,
        NVML_TEMPERATURE_GPU=0,
    )

    monkeypatch.setattr(system_metrics, "pynvml", stub)
    monkeypatch.setattr(system_metrics, "HAS_NVML", True)
    monkeypatch.setattr(system_metrics, "psutil", None)
    monkeypatch.setattr(system_metrics, "HAS_PSUTIL", False)
    monkeypatch.setattr(system_metrics, "_FALLBACK_CPU_COUNT", 4)
    monkeypatch.setattr(
        system_metrics,
        "_CONFIG",
        system_metrics.SystemMetricsConfig(use_psutil=False, poll_gpu=True, use_nvml=True),
    )
    monkeypatch.setattr(system_metrics, "_NVML_DISABLED", False)

    payload = system_metrics.sample_system_metrics()
    assert payload.get("gpus")
    assert payload.get("gpu_count") == 1

    system_metrics.configure_system_metrics(poll_gpu=False)
    payload_disabled = system_metrics.sample_system_metrics()
    assert "gpus" not in payload_disabled
    assert system_metrics.current_system_metrics_config().poll_gpu is False

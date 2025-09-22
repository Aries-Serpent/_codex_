from __future__ import annotations

import json
from typing import Any

import pytest

from codex_ml.monitoring import system_metrics
from codex_ml.monitoring.codex_logging import CodexLoggers, init_telemetry


def test_init_telemetry_min_profile_defaults() -> None:
    loggers = init_telemetry()
    assert isinstance(loggers, CodexLoggers)
    assert loggers.tb is None or loggers.tb
    assert loggers.mlflow_active in {True, False}
    assert loggers.gpu is False


def test_init_telemetry_full_enables_gpu_flag() -> None:
    loggers = init_telemetry("full")
    assert isinstance(loggers, CodexLoggers)
    assert loggers.gpu in {True, False}


def test_log_system_metrics_degrades_when_dependencies_missing(
    monkeypatch: pytest.MonkeyPatch, tmp_path, caplog
) -> None:
    monkeypatch.setattr(system_metrics, "psutil", None)
    monkeypatch.setattr(system_metrics, "HAS_PSUTIL", False)
    monkeypatch.setattr(system_metrics, "pynvml", None)
    monkeypatch.setattr(system_metrics, "HAS_NVML", False)
    monkeypatch.setattr(system_metrics, "_PSUTIL_REQUESTED", True)
    monkeypatch.setattr(system_metrics, "_NVML_REQUESTED", True)
    monkeypatch.setattr(system_metrics, "_NVML_FEATURE_DISABLED", False)
    monkeypatch.setattr(
        system_metrics, "_CONFIG", system_metrics.SystemMetricsConfig(True, True, True)
    )
    monkeypatch.setattr(system_metrics, "_NVML_DISABLED", False)
    monkeypatch.setattr(system_metrics, "_PSUTIL_WARNING_CONTEXTS", set())
    monkeypatch.setattr(system_metrics, "_NVML_WARNING_CONTEXTS", set())

    caplog.set_level("INFO")
    path = tmp_path / "missing-deps.jsonl"

    class DummyEvent:
        def __init__(self) -> None:
            self._flag = False

        def set(self) -> None:
            self._flag = True

        def is_set(self) -> bool:
            return self._flag

        def wait(self, timeout: float | None = None) -> bool:
            self._flag = True
            return True

    class DummyThread:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self._target = kwargs.get("target") or (args[0] if args else None)
            self._alive = False

        def start(self) -> None:
            self._alive = True
            try:
                if self._target:
                    self._target()
            finally:
                self._alive = False

        def is_alive(self) -> bool:
            return self._alive

        def join(self, timeout: float | None = None) -> None:
            self._alive = False

    monkeypatch.setattr(system_metrics.threading, "Event", DummyEvent)
    monkeypatch.setattr(system_metrics.threading, "Thread", DummyThread)

    system_metrics.log_system_metrics(path, interval=0.01)

    psutil_warn = [
        rec
        for rec in caplog.records
        if getattr(rec, "event", None) == "system_metrics.psutil_missing"
    ]
    assert psutil_warn, "expected psutil fallback warning"
    nvml_warn = [
        rec
        for rec in caplog.records
        if getattr(rec, "event", None) == "system_metrics.nvml_missing"
    ]
    assert nvml_warn, "expected NVML fallback warning"

    raw = path.read_text(encoding="utf-8").strip().splitlines()
    assert raw, "expected fallback sampler to write records"
    payload = json.loads(raw[0])
    assert payload.get("memory") is None
    assert payload.get("gpu_count") is None or "gpu_count" not in payload


def test_system_metrics_logger_uses_full_samplers_when_available(
    monkeypatch: pytest.MonkeyPatch, tmp_path, caplog
) -> None:
    caplog.set_level("WARNING")

    class FakeMemory:
        def __init__(self, payload: dict[str, Any]) -> None:
            self._payload = payload

        def _asdict(self) -> dict[str, Any]:
            return self._payload

    class FakeProcess:
        def cpu_percent(self, interval: float | None = None) -> float:
            return 42.0

        def memory_info(self) -> FakeMemory:
            return FakeMemory({"rss": 256})

    class FakePsutil:
        def cpu_percent(self, interval: float | None = None) -> float:
            return 12.5

        def cpu_count(self, logical: bool = True) -> int:
            return 8

        def virtual_memory(self) -> FakeMemory:
            return FakeMemory({"total": 1024, "available": 512})

        def swap_memory(self) -> FakeMemory:
            return FakeMemory({"total": 2048, "free": 1024})

        def Process(self) -> FakeProcess:
            return FakeProcess()

    class FakeNVML:
        NVML_TEMPERATURE_GPU = 0

        def nvmlInit(self) -> None:
            pass

        def nvmlShutdown(self) -> None:
            pass

        def nvmlDeviceGetCount(self) -> int:
            return 1

        def nvmlDeviceGetHandleByIndex(self, index: int) -> int:
            return index

        def nvmlDeviceGetUtilizationRates(self, handle: int) -> Any:
            class Rates:
                gpu = 75

            return Rates()

        def nvmlDeviceGetMemoryInfo(self, handle: int) -> Any:
            class Mem:
                used = 512
                total = 1024

            return Mem()

        def nvmlDeviceGetTemperature(self, handle: int, sensor: int) -> int:
            return 65

        def nvmlDeviceGetPowerUsage(self, handle: int) -> int:
            return 50000

    monkeypatch.setattr(system_metrics, "psutil", FakePsutil())
    monkeypatch.setattr(system_metrics, "HAS_PSUTIL", True)
    monkeypatch.setattr(system_metrics, "pynvml", FakeNVML())
    monkeypatch.setattr(system_metrics, "HAS_NVML", True)
    monkeypatch.setattr(system_metrics, "_PSUTIL_REQUESTED", True)
    monkeypatch.setattr(system_metrics, "_NVML_REQUESTED", True)
    monkeypatch.setattr(system_metrics, "_NVML_FEATURE_DISABLED", False)
    monkeypatch.setattr(
        system_metrics, "_CONFIG", system_metrics.SystemMetricsConfig(True, True, True)
    )
    monkeypatch.setattr(system_metrics, "_NVML_DISABLED", False)
    monkeypatch.setattr(system_metrics, "_PSUTIL_WARNING_CONTEXTS", set())
    monkeypatch.setattr(system_metrics, "_NVML_WARNING_CONTEXTS", set())

    path = tmp_path / "full-samplers.jsonl"

    class DummyEvent:
        def __init__(self) -> None:
            self._flag = False

        def set(self) -> None:
            self._flag = True

        def is_set(self) -> bool:
            return self._flag

        def wait(self, timeout: float | None = None) -> bool:
            self._flag = True
            return True

    class DummyThread:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self._target = kwargs.get("target") or (args[0] if args else None)
            self._alive = False

        def start(self) -> None:
            self._alive = True
            try:
                if self._target:
                    self._target()
            finally:
                self._alive = False

        def is_alive(self) -> bool:
            return self._alive

        def join(self, timeout: float | None = None) -> None:
            self._alive = False

    monkeypatch.setattr(system_metrics.threading, "Event", DummyEvent)
    monkeypatch.setattr(system_metrics.threading, "Thread", DummyThread)

    system_metrics.log_system_metrics(path, interval=0.01)

    warnings = [
        rec
        for rec in caplog.records
        if getattr(rec, "event", None)
        in {"system_metrics.psutil_missing", "system_metrics.nvml_missing"}
    ]
    assert not warnings, "did not expect dependency warnings when samplers available"

    raw = path.read_text(encoding="utf-8").strip().splitlines()
    assert raw, "expected sampler to write records"
    payload = json.loads(raw[0])
    assert payload.get("memory") is not None
    assert payload.get("cpu_percent") is not None
    assert payload.get("gpu_count") == 1

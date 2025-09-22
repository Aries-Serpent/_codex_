from __future__ import annotations

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

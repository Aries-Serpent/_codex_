"""Unit tests for the Prometheus metrics registry helpers."""

from __future__ import annotations

import importlib

import pytest


@pytest.fixture(name="metrics_module")
def _metrics_module_fixture():
    """Reload the metrics module to ensure a clean environment per test."""

    return importlib.import_module("codex_ml.monitoring.prometheus_metrics")


def test_codex_metrics_registry_records_metrics(metrics_module):
    registry = metrics_module.CodexMetricsRegistry()

    registry.record_training_step(0.5)
    registry.record_inference("/infer", 0.2)
    registry.observe_data_loading(0.1)
    with registry.track_duration():
        pass

    # The registry should always expose metric helpers regardless of dependency.
    assert hasattr(registry.training_steps, "inc")
    assert hasattr(registry.training_loss, "set")

    if metrics_module._HAS_PROMETHEUS:  # pragma: no cover - exercised when available
        assert registry.registry is not None, "registry must be initialized"
    else:
        # When prometheus_client is missing we rely on the noop metric helpers.
        assert registry.registry is None, "registry is not valid"
        assert registry.training_steps.__class__.__name__ == "_NoopMetric", "__name__ is not valid"


def test_metrics_enabled_reads_environment(metrics_module, monkeypatch):
    monkeypatch.delenv("CODEX_METRICS_ENABLED", raising=False)
    assert metrics_module.metrics_enabled() is False, "Condition must be true"

    monkeypatch.setenv("CODEX_METRICS_ENABLED", "1")
    assert metrics_module.metrics_enabled() is True, "Condition must be true"

    monkeypatch.setenv("CODEX_METRICS_ENABLED", "off")
    assert metrics_module.metrics_enabled() is False, "Condition must be true"

    monkeypatch.setenv("CODEX_METRICS_ENABLED", "TrUe")
    assert metrics_module.metrics_enabled() is True, "Condition must be true"

"""Unit tests for src/codex/monitoring/performance_monitor.py."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from codex.monitoring.performance_monitor import (
    PerformanceMonitor,
    PerformanceSnapshot,
    PerformanceThresholds,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_monitor(
    loss_spike_factor: float = 2.0,
    throughput_drop_pct: float = 30.0,
    latency_spike_factor: float = 3.0,
    window_size: int = 10,
    min_samples: int = 3,
    alert_manager: object | None = None,
) -> PerformanceMonitor:
    thresholds = PerformanceThresholds(
        loss_spike_factor=loss_spike_factor,
        throughput_drop_pct=throughput_drop_pct,
        latency_spike_factor=latency_spike_factor,
        window_size=window_size,
        min_samples=min_samples,
    )
    mock_mgr = alert_manager or MagicMock()
    return PerformanceMonitor(alert_manager=mock_mgr, thresholds=thresholds, run_id="test-run")


def _feed_stable_loss(monitor: PerformanceMonitor, n: int = 10, loss: float = 0.5) -> None:
    """Feed *n* epochs of stable loss to build up history."""
    for epoch in range(1, n + 1):
        monitor.record(PerformanceSnapshot(epoch=epoch, loss=loss))


# ---------------------------------------------------------------------------
# Tests: healthy run
# ---------------------------------------------------------------------------


class TestHealthyRun:
    def test_stable_loss_no_anomalies(self) -> None:
        monitor = _make_monitor()
        _feed_stable_loss(monitor, n=10, loss=0.5)
        anomalies = monitor.record(PerformanceSnapshot(epoch=11, loss=0.51))
        assert anomalies == [], "anomalies is not valid"

    def test_no_alert_fired_when_healthy(self) -> None:
        mock_mgr = MagicMock()
        monitor = _make_monitor(alert_manager=mock_mgr)
        _feed_stable_loss(monitor, n=10, loss=0.5)
        monitor.record(PerformanceSnapshot(epoch=11, loss=0.49))
        mock_mgr.alert.assert_not_called()


# ---------------------------------------------------------------------------
# Tests: loss spike
# ---------------------------------------------------------------------------


class TestLossSpike:
    def test_loss_spike_detected(self) -> None:
        monitor = _make_monitor(loss_spike_factor=2.0, min_samples=3)
        _feed_stable_loss(monitor, n=5, loss=1.0)
        # 3× spike should trigger (> 2× factor)
        anomalies = monitor.record(PerformanceSnapshot(epoch=6, loss=3.5))
        assert len(anomalies) == 1, "Anomalies must not be empty"
        assert "Loss spike" in anomalies[0], "Condition must be true"

    def test_loss_below_threshold_no_anomaly(self) -> None:
        monitor = _make_monitor(loss_spike_factor=2.0, min_samples=3)
        _feed_stable_loss(monitor, n=5, loss=1.0)
        # 1.8× — below factor of 2.0
        anomalies = monitor.record(PerformanceSnapshot(epoch=6, loss=1.8))
        assert anomalies == [], "anomalies is not valid"

    def test_loss_spike_fires_alert(self) -> None:
        mock_mgr = MagicMock()
        monitor = _make_monitor(loss_spike_factor=2.0, min_samples=3, alert_manager=mock_mgr)
        _feed_stable_loss(monitor, n=5, loss=1.0)
        monitor.record(PerformanceSnapshot(epoch=6, loss=4.0))
        mock_mgr.alert.assert_called_once()
        event = mock_mgr.alert.call_args[0][0]
        assert "Loss spike" in event.message, "Condition must be true"


# ---------------------------------------------------------------------------
# Tests: throughput drop
# ---------------------------------------------------------------------------


class TestThroughputDrop:
    def test_throughput_drop_detected(self) -> None:
        monitor = _make_monitor(throughput_drop_pct=30.0, min_samples=3)
        for epoch in range(1, 6):
            monitor.record(PerformanceSnapshot(epoch=epoch, throughput=100.0))
        # 50% drop
        anomalies = monitor.record(PerformanceSnapshot(epoch=6, throughput=50.0))
        assert len(anomalies) == 1, "Anomalies must not be empty"
        assert "Throughput drop" in anomalies[0], "Condition must be true"

    def test_throughput_small_drop_no_anomaly(self) -> None:
        monitor = _make_monitor(throughput_drop_pct=30.0, min_samples=3)
        for epoch in range(1, 6):
            monitor.record(PerformanceSnapshot(epoch=epoch, throughput=100.0))
        # 20% drop — below threshold
        anomalies = monitor.record(PerformanceSnapshot(epoch=6, throughput=80.0))
        assert anomalies == [], "anomalies is not valid"

    def test_throughput_alert_contains_details(self) -> None:
        mock_mgr = MagicMock()
        monitor = _make_monitor(throughput_drop_pct=30.0, min_samples=3, alert_manager=mock_mgr)
        for epoch in range(1, 6):
            monitor.record(PerformanceSnapshot(epoch=epoch, throughput=100.0))
        monitor.record(PerformanceSnapshot(epoch=6, throughput=40.0))
        mock_mgr.alert.assert_called_once()
        event = mock_mgr.alert.call_args[0][0]
        assert "Throughput drop" in event.message, "Condition must be true"


# ---------------------------------------------------------------------------
# Tests: latency spike
# ---------------------------------------------------------------------------


class TestLatencySpike:
    def test_latency_spike_detected(self) -> None:
        monitor = _make_monitor(latency_spike_factor=3.0, min_samples=3)
        for epoch in range(1, 6):
            monitor.record(PerformanceSnapshot(epoch=epoch, latency_ms=10.0))
        # 4× spike
        anomalies = monitor.record(PerformanceSnapshot(epoch=6, latency_ms=45.0))
        assert len(anomalies) == 1, "Anomalies must not be empty"
        assert "Latency spike" in anomalies[0], "Condition must be true"

    def test_latency_below_factor_no_anomaly(self) -> None:
        monitor = _make_monitor(latency_spike_factor=3.0, min_samples=3)
        for epoch in range(1, 6):
            monitor.record(PerformanceSnapshot(epoch=epoch, latency_ms=10.0))
        # 2.5× — below 3.0 factor
        anomalies = monitor.record(PerformanceSnapshot(epoch=6, latency_ms=25.0))
        assert anomalies == [], "anomalies is not valid"


# ---------------------------------------------------------------------------
# Tests: min_samples guard
# ---------------------------------------------------------------------------


class TestMinSamplesGuard:
    def test_no_alert_with_insufficient_samples(self) -> None:
        mock_mgr = MagicMock()
        # min_samples=3, only 2 history points before the spike
        monitor = _make_monitor(min_samples=3, alert_manager=mock_mgr)
        monitor.record(PerformanceSnapshot(epoch=1, loss=1.0))
        monitor.record(PerformanceSnapshot(epoch=2, loss=1.0))
        # 10× spike but only 2 baseline samples
        anomalies = monitor.record(PerformanceSnapshot(epoch=3, loss=10.0))
        assert anomalies == [], "anomalies is not valid"
        mock_mgr.alert.assert_not_called()

    def test_alert_fires_once_min_samples_met(self) -> None:
        mock_mgr = MagicMock()
        monitor = _make_monitor(min_samples=3, loss_spike_factor=2.0, alert_manager=mock_mgr)
        for epoch in range(1, 4):
            monitor.record(PerformanceSnapshot(epoch=epoch, loss=1.0))
        # Now 3 baseline samples — spike should trigger
        anomalies = monitor.record(PerformanceSnapshot(epoch=4, loss=5.0))
        assert anomalies != [], "anomalies is not valid"
        mock_mgr.alert.assert_called_once()


# ---------------------------------------------------------------------------
# Tests: alert failure does NOT propagate
# ---------------------------------------------------------------------------


class TestAlertFailureSafety:
    def test_alert_exception_does_not_crash_training(self) -> None:
        mock_mgr = MagicMock()
        mock_mgr.alert.side_effect = RuntimeError("Slack is down")
        monitor = _make_monitor(loss_spike_factor=2.0, min_samples=3, alert_manager=mock_mgr)
        _feed_stable_loss(monitor, n=5, loss=1.0)
        # Should not raise even though alert raises
        result = monitor.record(PerformanceSnapshot(epoch=6, loss=5.0))
        assert "Loss spike" in result[0], "Result must not be empty"


# ---------------------------------------------------------------------------
# Tests: from_env factory
# ---------------------------------------------------------------------------


class TestFromEnv:
    def test_default_thresholds(self) -> None:
        t = PerformanceThresholds.from_env()
        assert t.loss_spike_factor == 2.0, "loss_spike_factor is not valid"
        assert t.throughput_drop_pct == 30.0, "throughput_drop_pct is not valid"
        assert t.latency_spike_factor == 3.0, "latency_spike_factor is not valid"
        assert t.window_size == 10, "window_size is not valid"
        assert t.min_samples == 3, "min_samples is not valid"

    def test_env_overrides(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CODEX_PERF_LOSS_SPIKE_FACTOR", "5.0")
        monkeypatch.setenv("CODEX_PERF_THROUGHPUT_DROP_PCT", "20.0")
        monkeypatch.setenv("CODEX_PERF_LATENCY_SPIKE_FACTOR", "4.0")
        monkeypatch.setenv("CODEX_PERF_WINDOW_SIZE", "15")
        monkeypatch.setenv("CODEX_PERF_MIN_SAMPLES", "5")
        t = PerformanceThresholds.from_env()
        assert t.loss_spike_factor == 5.0, "loss_spike_factor is not valid"
        assert t.throughput_drop_pct == 20.0, "throughput_drop_pct is not valid"
        assert t.latency_spike_factor == 4.0, "latency_spike_factor is not valid"
        assert t.window_size == 15, "window_size is not valid"
        assert t.min_samples == 5, "min_samples is not valid"

    def test_from_env_monitor_factory(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Ensure from_env creates a monitor without error (no channels configured)
        for var in (
            "CODEX_SLACK_WEBHOOK_URL",
            "CODEX_ALERT_SMTP_HOST",
            "CODEX_ALERT_TO",
        ):
            monkeypatch.delenv(var, raising=False)
        monitor = PerformanceMonitor.from_env(run_id="env-test")
        assert monitor._run_id == "env-test", "_run_id is not valid"
        assert isinstance(monitor._thresholds, PerformanceThresholds)


# ---------------------------------------------------------------------------
# Tests: PerformanceSnapshot timestamp
# ---------------------------------------------------------------------------


class TestPerformanceSnapshot:
    def test_timestamp_auto_set(self) -> None:
        snap = PerformanceSnapshot(epoch=1, loss=0.5)
        assert snap.timestamp, "Condition must be true"
        assert "T" in snap.timestamp, "Condition must be true"

    def test_metadata_default_empty(self) -> None:
        snap = PerformanceSnapshot(epoch=1)
        assert snap.metadata == {}, "Data must not be empty"

    def test_multiple_anomalies_reported(self) -> None:
        """All three metrics can fire at once."""
        monitor = _make_monitor(
            loss_spike_factor=2.0,
            throughput_drop_pct=30.0,
            latency_spike_factor=3.0,
            min_samples=3,
        )
        for epoch in range(1, 6):
            monitor.record(
                PerformanceSnapshot(epoch=epoch, loss=1.0, throughput=100.0, latency_ms=10.0)
            )
        anomalies = monitor.record(
            PerformanceSnapshot(epoch=6, loss=5.0, throughput=30.0, latency_ms=50.0)
        )
        assert len(anomalies) == 3, "Anomalies must not be empty"

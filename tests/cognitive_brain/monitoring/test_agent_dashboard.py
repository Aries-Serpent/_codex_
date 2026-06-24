"""
Phase 5 Agent Dashboard Tests

Tests for:
- AgentDashboard.record_decision()
- AgentDashboard.record_error()
- AgentDashboard.get_health() — healthy, degraded, critical
- AgentDashboard.trigger_self_correction()
- AgentDashboard.reset()
- AgentHealthMetrics fields
- Trend computation
- Prometheus no-op stubs
"""

from cognitive_brain.monitoring.agent_dashboard import (
    _PROMETHEUS_AVAILABLE,
    AgentDashboard,
    AgentHealthMetrics,
)

# ---------------------------------------------------------------------------
# TestAgentDashboardRecord
# ---------------------------------------------------------------------------


class TestAgentDashboardRecord:
    def test_record_decision_appends(self):
        d = AgentDashboard()
        d.record_decision("approve", coherence=0.814, latency_ms=12.0)
        assert len(d._records) == 1

    def test_record_decision_fields(self):
        d = AgentDashboard()
        d.record_decision("reject", coherence=0.700, latency_ms=25.0)
        r = d._records[0]
        assert r.decision == "reject"
        assert r.coherence == 0.700
        assert r.latency_ms == 25.0
        assert r.error is False

    def test_record_error_sets_error_flag(self):
        d = AgentDashboard()
        d.record_error("assessment_error")
        assert d._records[-1].error is True

    def test_record_decision_error_flag(self):
        d = AgentDashboard()
        d.record_decision("error_decision", coherence=0.0, latency_ms=0.0, error=True)
        assert d._records[0].error is True

    def test_window_size_respected(self):
        d = AgentDashboard(window_size=5)
        for i in range(10):
            d.record_decision("approve", coherence=0.8, latency_ms=10.0)
        assert len(d._records) == 5


# ---------------------------------------------------------------------------
# TestAgentDashboardHealth
# ---------------------------------------------------------------------------


class TestAgentDashboardHealth:
    def test_empty_dashboard_healthy(self):
        d = AgentDashboard()
        health = d.get_health()
        assert health.health_status == "healthy"

    def test_healthy_records_healthy(self):
        d = AgentDashboard()
        for _ in range(5):
            d.record_decision("approve", coherence=0.814, latency_ms=10.0)
        health = d.get_health()
        assert health.health_status == "healthy"
        assert health.coherence_current == 0.814

    def test_degraded_coherence(self):
        d = AgentDashboard()
        for _ in range(5):
            d.record_decision("approve", coherence=0.700, latency_ms=10.0)
        health = d.get_health()
        assert health.health_status == "degraded"

    def test_critical_coherence(self):
        d = AgentDashboard()
        for _ in range(5):
            d.record_decision("approve", coherence=0.500, latency_ms=10.0)
        health = d.get_health()
        assert health.health_status == "critical"

    def test_high_latency_degraded(self):
        d = AgentDashboard()
        for _ in range(5):
            d.record_decision("approve", coherence=0.814, latency_ms=80.0)
        health = d.get_health()
        assert health.health_status in ("degraded", "critical")

    def test_very_high_latency_critical(self):
        d = AgentDashboard()
        for _ in range(5):
            d.record_decision("approve", coherence=0.814, latency_ms=200.0)
        health = d.get_health()
        assert health.health_status == "critical"

    def test_coherence_avg_computed(self):
        d = AgentDashboard()
        d.record_decision("approve", coherence=0.800, latency_ms=10.0)
        d.record_decision("approve", coherence=0.900, latency_ms=10.0)
        health = d.get_health()
        assert 0.84 <= health.coherence_avg <= 0.86

    def test_latency_p99_computed(self):
        d = AgentDashboard()
        for _ in range(100):
            d.record_decision("approve", coherence=0.8, latency_ms=10.0)
        d.record_decision("approve", coherence=0.8, latency_ms=200.0)
        health = d.get_health()
        assert health.latency_p99_ms >= 10.0

    def test_prometheus_available_field(self):
        d = AgentDashboard()
        health = d.get_health()
        assert isinstance(health.prometheus_available, bool)

    def test_health_metrics_type(self):
        d = AgentDashboard()
        d.record_decision("approve", coherence=0.8, latency_ms=10.0)
        health = d.get_health()
        assert isinstance(health, AgentHealthMetrics)


# ---------------------------------------------------------------------------
# TestAgentDashboardSelfCorrection
# ---------------------------------------------------------------------------


class TestAgentDashboardSelfCorrection:
    def test_self_correction_on_critical(self):
        d = AgentDashboard()
        for _ in range(5):
            d.record_decision("approve", coherence=0.500, latency_ms=10.0)
        health = d.get_health()
        actions = d.trigger_self_correction(health)
        assert "enabled_classical_fallback" in actions
        assert d.classical_fallback_active is True

    def test_self_correction_on_high_latency(self):
        d = AgentDashboard()
        for _ in range(5):
            d.record_decision("approve", coherence=0.814, latency_ms=200.0)
        health = d.get_health()
        actions = d.trigger_self_correction(health)
        assert "enabled_lightweight_mode" in actions
        assert d.lightweight_mode_active is True

    def test_self_correction_no_action_on_healthy(self):
        d = AgentDashboard()
        for _ in range(5):
            d.record_decision("approve", coherence=0.814, latency_ms=10.0)
        health = d.get_health()
        actions = d.trigger_self_correction(health)
        assert actions == []
        assert d.classical_fallback_active is False

    def test_self_correction_log_updated(self):
        d = AgentDashboard()
        for _ in range(5):
            d.record_decision("approve", coherence=0.500, latency_ms=10.0)
        health = d.get_health()
        d.trigger_self_correction(health)
        assert len(d.self_correction_log) == 1

    def test_self_correction_log_read_only_copy(self):
        d = AgentDashboard()
        log = d.self_correction_log
        log.append({"injected": True})
        assert len(d.self_correction_log) == 0


# ---------------------------------------------------------------------------
# TestAgentDashboardReset
# ---------------------------------------------------------------------------


class TestAgentDashboardReset:
    def test_reset_clears_records(self):
        d = AgentDashboard()
        d.record_decision("approve", coherence=0.8, latency_ms=10.0)
        d.reset()
        assert len(d._records) == 0

    def test_reset_clears_flags(self):
        d = AgentDashboard()
        for _ in range(5):
            d.record_decision("approve", coherence=0.500, latency_ms=200.0)
        health = d.get_health()
        d.trigger_self_correction(health)
        d.reset()
        assert d.classical_fallback_active is False
        assert d.lightweight_mode_active is False

    def test_reset_clears_log(self):
        d = AgentDashboard()
        for _ in range(5):
            d.record_decision("approve", coherence=0.500, latency_ms=10.0)
        health = d.get_health()
        d.trigger_self_correction(health)
        d.reset()
        assert len(d.self_correction_log) == 0


# ---------------------------------------------------------------------------
# TestTrendComputation
# ---------------------------------------------------------------------------


class TestTrendComputation:
    def test_trend_stable(self):
        values = [0.8, 0.8, 0.8, 0.8]
        assert AgentDashboard._compute_trend(values) == "stable"

    def test_trend_improving(self):
        values = [0.7, 0.75, 0.80, 0.85]
        assert AgentDashboard._compute_trend(values) == "improving"

    def test_trend_degrading(self):
        values = [0.85, 0.80, 0.75, 0.70]
        assert AgentDashboard._compute_trend(values) == "degrading"

    def test_trend_single_value_stable(self):
        assert AgentDashboard._compute_trend([0.8]) == "stable"

    def test_trend_empty_stable(self):
        assert AgentDashboard._compute_trend([]) == "stable"


# ---------------------------------------------------------------------------
# TestPrometheusNoOp
# ---------------------------------------------------------------------------


class TestPrometheusNoOp:
    def test_prometheus_available_is_bool(self):
        assert isinstance(_PROMETHEUS_AVAILABLE, bool)

    def test_record_does_not_raise_without_prometheus(self):
        d = AgentDashboard()
        # Should never raise regardless of prometheus availability
        d.record_decision("approve", coherence=0.8, latency_ms=10.0)
        d.record_error("test_error")

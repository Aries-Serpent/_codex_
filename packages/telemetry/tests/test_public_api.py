from __future__ import annotations

from codex_ml_telemetry import (
    REQUEST_LATENCY,
    HealthReport,
    HealthStatus,
    MetricsRegistry,
    render_prometheus,
    track_time,
)


def test_health_report_is_json_compatible() -> None:
    report = HealthReport(
        status=HealthStatus.HEALTHY,
        checks={"prometheus": "ok"},
        message="ready",
        timestamp="2026-09-12T05:53:23Z",
    )

    assert report.to_dict() == {
        "status": "healthy",
        "timestamp": "2026-09-12T05:53:23Z",
        "checks": {"prometheus": "ok"},
        "message": "ready",
    }


def test_registry_exposes_stable_metrics() -> None:
    metrics = MetricsRegistry(namespace="test_codex_ml")

    metrics.model_accuracy.labels(model="stub").set(1.0)
    metrics.http_requests.labels(method="GET", endpoint="/health", status="200").inc()
    metrics.http_errors.labels(method="GET", endpoint="/health", error_type="none").inc(0)
    metrics.http_latency.labels(method="GET", endpoint="/health").observe(0.01)
    metrics.active_requests.set(0)
    metrics.active_models.set(1)


def test_prometheus_rendering_is_text() -> None:
    metrics = MetricsRegistry(namespace="render_test")
    rendered = render_prometheus(metrics.registry)

    assert isinstance(rendered, str)
    assert rendered


def test_track_time_preserves_return_value() -> None:
    @track_time(REQUEST_LATENCY)
    def operation() -> str:
        return "ok"

    assert operation() == "ok"

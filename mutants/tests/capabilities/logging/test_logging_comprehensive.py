"""Comprehensive tests for logging and monitoring capability.

Tests cover:
- Centralized metrics sink
- Prometheus/OTel exporters
- Log rotation and retention
- PII scrubbing
- Alerting rules
"""

from __future__ import annotations

import json
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

import pytest

pytest.importorskip("hypothesis")


pytest.importorskip("hypothesis", reason="hypothesis required for property tests")

from hypothesis import given, settings
from hypothesis import strategies as st

# --- Centralized Metrics Sink Tests ---


class MetricsSink:
    """Centralized metrics collection sink."""

    def __init__(self):
        self.metrics: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.tags: dict[str, str] = {}

    def set_global_tags(self, tags: dict[str, str]) -> None:
        """Set global tags for all metrics."""
        self.tags = tags

    def record(self, name: str, value: float, tags: dict[str, str] | None = None) -> None:
        """Record a metric value."""
        record = {
            "name": name,
            "value": value,
            "timestamp": time.time(),
            "tags": {**self.tags, **(tags or {})},
        }
        self.metrics[name].append(record)

    def get_metric(self, name: str) -> list[dict[str, Any]]:
        """Get all records for a metric."""
        return self.metrics.get(name, [])

    def get_latest(self, name: str) -> dict[str, Any] | None:
        """Get latest record for a metric."""
        records = self.metrics.get(name, [])
        return records[-1] if records else None

    def clear(self) -> None:
        """Clear all metrics."""
        self.metrics.clear()


class TestMetricsSink:
    """Tests for centralized metrics sink."""

    def test_record_metric(self):
        """Record a metric value."""
        sink = MetricsSink()
        sink.record("cpu_usage", 0.75)
        records = sink.get_metric("cpu_usage")
        assert len(records) == 1, "Records must not be empty"
        assert records[0]["value"] == 0.75, "Value must be initialized"

    def test_record_with_tags(self):
        """Record metric with tags."""
        sink = MetricsSink()
        sink.record("request_count", 100, tags={"endpoint": "/api/v1"})
        record = sink.get_latest("request_count")
        assert record["tags"]["endpoint"] == "/api/v1", "rec is not valid"

    def test_global_tags(self):
        """Global tags should be applied to all metrics."""
        sink = MetricsSink()
        sink.set_global_tags({"service": "codex", "env": "prod"})
        sink.record("latency", 0.5)
        record = sink.get_latest("latency")
        assert record["tags"]["service"] == "codex", "rec is not valid"
        assert record["tags"]["env"] == "prod", "rec is not valid"

    def test_multiple_records(self):
        """Multiple records should be stored."""
        sink = MetricsSink()
        sink.record("counter", 1)
        sink.record("counter", 2)
        sink.record("counter", 3)
        records = sink.get_metric("counter")
        assert len(records) == 3, "Records must not be empty"

    def test_clear_metrics(self):
        """Clear should remove all metrics."""
        sink = MetricsSink()
        sink.record("test", 1.0)
        sink.clear()
        assert len(sink.get_metric("test")) == 0, "Collection must not be empty"


# --- Prometheus Exporter Tests ---


class PrometheusExporter:
    """Export metrics in Prometheus format."""

    def __init__(self, sink: MetricsSink):
        self.sink = sink

    def export(self) -> str:
        """Export metrics in Prometheus text format."""
        lines = []
        for name, records in self.sink.metrics.items():
            if not records:
                continue
            latest = records[-1]
            tags_str = ""
            if latest["tags"]:
                tags_parts = [f'{k}="{v}"' for k, v in latest["tags"].items()]
                tags_str = "{" + ",".join(tags_parts) + "}"
            lines.append(f"{name}{tags_str} {latest['value']}")
        return "\n".join(lines)

    def get_metric_families(self) -> list[str]:
        """Get list of metric families."""
        return list(self.sink.metrics.keys())


class TestPrometheusExporter:
    """Tests for Prometheus exporter."""

    def test_export_simple_metric(self):
        """Export simple metric."""
        sink = MetricsSink()
        sink.record("requests_total", 100)
        exporter = PrometheusExporter(sink)
        output = exporter.export()
        assert "requests_total 100" in output, "Condition must be true"

    def test_export_metric_with_tags(self):
        """Export metric with labels."""
        sink = MetricsSink()
        sink.record("http_requests", 50, tags={"method": "GET"})
        exporter = PrometheusExporter(sink)
        output = exporter.export()
        assert 'method="GET"' in output, "Condition must be true"

    def test_metric_families(self):
        """Get metric families."""
        sink = MetricsSink()
        sink.record("cpu", 0.5)
        sink.record("memory", 0.7)
        exporter = PrometheusExporter(sink)
        families = exporter.get_metric_families()
        assert "cpu" in families, "Condition must be true"
        assert "memory" in families, "Condition must be true"


# --- OTel Exporter Tests ---


class OTelSpan:
    """OpenTelemetry span representation."""

    def __init__(self, name: str, trace_id: str, span_id: str):
        self.name = name
        self.trace_id = trace_id
        self.span_id = span_id
        self.attributes: dict[str, Any] = {}
        self.events: list[dict[str, Any]] = []
        self.start_time: float = time.time()
        self.end_time: float | None = None

    def set_attribute(self, key: str, value: Any) -> None:
        """Set span attribute."""
        self.attributes[key] = value

    def add_event(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        """Add span event."""
        self.events.append({"name": name, "timestamp": time.time(), "attributes": attributes or {}})

    def end(self) -> None:
        """End the span."""
        self.end_time = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "attributes": self.attributes,
            "events": self.events,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }


class TestOTelSpan:
    """Tests for OTel span."""

    def test_create_span(self):
        """Create a span."""
        span = OTelSpan("test_operation", "trace123", "span456")
        assert span.name == "test_operation", "name is not valid"
        assert span.trace_id == "trace123", "trace_id is not valid"

    def test_set_attributes(self):
        """Set span attributes."""
        span = OTelSpan("op", "t1", "s1")
        span.set_attribute("http.method", "GET")
        span.set_attribute("http.status_code", 200)
        assert span.attributes["http.method"] == "GET", "Condition must be true"
        assert span.attributes["http.status_code"] == 200, "Condition must be true"

    def test_add_events(self):
        """Add span events."""
        span = OTelSpan("op", "t1", "s1")
        span.add_event("request_started")
        span.add_event("request_completed", {"bytes": 1024})
        assert len(span.events) == 2, "Collection must not be empty"

    def test_end_span(self):
        """End span sets end time."""
        span = OTelSpan("op", "t1", "s1")
        assert span.end_time is None, "end_time is not valid"
        span.end()
        assert span.end_time is not None, "end_time must be initialized"


# --- Log Rotation Tests ---


class LogRotator:
    """Log file rotation manager."""

    def __init__(self, max_size_mb: float = 10, max_files: int = 5):
        self.max_size_bytes = int(max_size_mb * 1024 * 1024)
        self.max_files = max_files

    def should_rotate(self, current_size: int) -> bool:
        """Check if rotation is needed."""
        return current_size >= self.max_size_bytes

    def get_rotated_files(self, base_path: Path) -> list[Path]:
        """Get list of rotated files."""
        pattern = f"{base_path.stem}.*{base_path.suffix}"
        return sorted(base_path.parent.glob(pattern))

    def cleanup_old_files(self, files: list[Path]) -> list[Path]:
        """Return files to delete based on retention policy."""
        if len(files) <= self.max_files:
            return []
        return files[: len(files) - self.max_files]


class TestLogRotation:
    """Tests for log rotation."""

    def test_should_rotate_when_size_exceeded(self):
        """Should rotate when size exceeds limit."""
        rotator = LogRotator(max_size_mb=1)  # 1MB
        assert not rotator.should_rotate(500 * 1024), "Condition must be true"
        assert rotator.should_rotate(1.5 * 1024 * 1024), "rotat is not valid"

    def test_cleanup_old_files(self):
        """Cleanup should remove excess files."""
        rotator = LogRotator(max_files=3)
        files = [Path(f"log.{i}.txt") for i in range(5)]
        to_delete = rotator.cleanup_old_files(files)
        assert len(to_delete) == 2, "To_delete must not be empty"


# --- PII Scrubbing Tests ---


PII_PATTERNS = [
    (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[EMAIL]"),
    (r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[PHONE]"),
    (r"\b\d{3}[-]?\d{2}[-]?\d{4}\b", "[SSN]"),
    (r"\b(?:\d{4}[-]?){3}\d{4}\b", "[CARD]"),
    (r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "[IP]"),
]


def scrub_pii(text: str) -> tuple[str, list[str]]:
    """Scrub PII from text and return scrubbed text and found patterns."""
    found = []
    result = text
    for pattern, replacement in PII_PATTERNS:
        matches = re.findall(pattern, text)
        if matches:
            found.append(replacement)
            result = re.sub(pattern, replacement, result)
    return result, found


class TestPIIScrubbing:
    """Tests for PII scrubbing."""

    def test_scrub_email(self):
        """Scrub email addresses."""
        text = "Contact: john.doe@example.com for help"
        scrubbed, _found = scrub_pii(text)
        assert "[EMAIL]" in scrubbed, "Condition must be true"
        assert "john.doe@example.com" not in scrubbed, "Condition must be true"

    def test_scrub_phone(self):
        """Scrub phone numbers."""
        text = "Call 123-456-7890 for support"
        scrubbed, _found = scrub_pii(text)
        assert "[PHONE]" in scrubbed, "Condition must be true"
        assert "123-456-7890" not in scrubbed, "Condition must be true"

    def test_scrub_ip(self):
        """Scrub IP addresses."""
        text = "Client IP: 192.168.1.100"
        scrubbed, _found = scrub_pii(text)
        assert "[IP]" in scrubbed, "Condition must be true"
        assert "192.168.1.100" not in scrubbed, "Condition must be true"

    def test_no_pii(self):
        """Text without PII should be unchanged."""
        text = "This is a normal log message"
        scrubbed, found = scrub_pii(text)
        assert scrubbed == text, "scrubbed is not valid"
        assert len(found) == 0, "Found must not be empty"

    @given(st.text(min_size=3, max_size=15, alphabet="abcdefghijklmnopqrstuvwxyz0123456789"))
    @settings(max_examples=20)
    def test_scrub_valid_email_format(self, local_part: str):
        """Property: properly formatted emails should be scrubbed."""
        if not local_part or not local_part[0].isalpha():
            return
        email = f"{local_part}@example.com"
        text = f"Contact: {email}"
        scrubbed, _ = scrub_pii(text)
        assert email not in scrubbed, "Condition must be true"


# --- Alerting Tests ---


class AlertRule:
    """Alerting rule definition."""

    def __init__(self, name: str, metric: str, threshold: float, operator: str = "gt"):
        self.name = name
        self.metric = metric
        self.threshold = threshold
        self.operator = operator
        self.duration_seconds = 0

    def evaluate(self, value: float) -> bool:
        """Evaluate if alert should fire."""
        if self.operator == "gt":
            return value > self.threshold
        if self.operator == "lt":
            return value < self.threshold
        if self.operator == "eq":
            return value == self.threshold
        if self.operator == "gte":
            return value >= self.threshold
        if self.operator == "lte":
            return value <= self.threshold
        return False


class AlertManager:
    """Manage alerting rules and notifications."""

    def __init__(self):
        self.rules: list[AlertRule] = []
        self.active_alerts: dict[str, dict[str, Any]] = {}

    def add_rule(self, rule: AlertRule) -> None:
        """Add alerting rule."""
        self.rules.append(rule)

    def check_metrics(self, metrics: dict[str, float]) -> list[str]:
        """Check metrics against rules and return fired alerts."""
        fired = []
        for rule in self.rules:
            if rule.metric in metrics and rule.evaluate(metrics[rule.metric]):
                fired.append(rule.name)
                self.active_alerts[rule.name] = {
                    "metric": rule.metric,
                    "value": metrics[rule.metric],
                    "threshold": rule.threshold,
                }
        return fired

    def resolve_alert(self, name: str) -> bool:
        """Resolve an active alert."""
        if name in self.active_alerts:
            del self.active_alerts[name]
            return True
        return False


class TestAlerting:
    """Tests for alerting system."""

    def test_alert_fires_on_threshold(self):
        """Alert should fire when threshold exceeded."""
        rule = AlertRule("high_cpu", "cpu_usage", 0.8, "gt")
        assert rule.evaluate(0.9), "Condition must be true"
        assert not rule.evaluate(0.7), "Condition must be true"

    def test_alert_manager_checks(self):
        """Alert manager should check all rules."""
        manager = AlertManager()
        manager.add_rule(AlertRule("high_cpu", "cpu", 0.8, "gt"))
        manager.add_rule(AlertRule("low_memory", "memory", 0.1, "lt"))
        fired = manager.check_metrics({"cpu": 0.9, "memory": 0.5})
        assert "high_cpu" in fired, "Condition must be true"
        assert "low_memory" not in fired, "Condition must be true"

    def test_resolve_alert(self):
        """Resolving alert should clear it."""
        manager = AlertManager()
        manager.add_rule(AlertRule("test", "metric", 10, "gt"))
        manager.check_metrics({"metric": 15})
        assert "test" in manager.active_alerts, "Condition must be true"
        manager.resolve_alert("test")
        assert "test" not in manager.active_alerts, "Condition must be true"


# --- Structured Logging Tests ---


class StructuredLogger:
    """Structured JSON logger."""

    def __init__(self, name: str):
        self.name = name
        self.context: dict[str, Any] = {}
        self.logs: list[dict[str, Any]] = []

    def set_context(self, **kwargs) -> None:
        """Set logging context."""
        self.context.update(kwargs)

    def log(self, level: str, message: str, **extra) -> dict[str, Any]:
        """Log a structured message."""
        record = {
            "timestamp": time.time(),
            "level": level,
            "logger": self.name,
            "message": message,
            **self.context,
            **extra,
        }
        self.logs.append(record)
        return record

    def info(self, message: str, **extra) -> dict[str, Any]:
        return self.log("INFO", message, **extra)

    def error(self, message: str, **extra) -> dict[str, Any]:
        return self.log("ERROR", message, **extra)

    def warning(self, message: str, **extra) -> dict[str, Any]:
        return self.log("WARNING", message, **extra)

    def to_json(self) -> str:
        """Export logs as JSON."""
        return json.dumps(self.logs)


class TestStructuredLogging:
    """Tests for structured logging."""

    def test_basic_logging(self):
        """Basic log message."""
        logger = StructuredLogger("test")
        record = logger.info("Hello world")
        assert record["level"] == "INFO", "rec is not valid"
        assert record["message"] == "Hello world", "rec is not valid"

    def test_logging_with_context(self):
        """Logging with context."""
        logger = StructuredLogger("test")
        logger.set_context(request_id="123", user_id="456")
        record = logger.info("Request processed")
        assert record["request_id"] == "123", "rec is not valid"
        assert record["user_id"] == "456", "rec is not valid"

    def test_logging_with_extra(self):
        """Logging with extra fields."""
        logger = StructuredLogger("test")
        record = logger.error("Failed", error_code=500, stack="...")
        assert record["error_code"] == 500, "Error should be raised or set"
        assert record["stack"] == "...", "rec is not valid"

    def test_export_json(self):
        """Export logs as JSON."""
        logger = StructuredLogger("test")
        logger.info("Log 1")
        logger.info("Log 2")
        output = logger.to_json()
        parsed = json.loads(output)
        assert len(parsed) == 2, "Parsed must not be empty"


# --- Log Level Tests ---


class TestLogLevels:
    """Tests for log level filtering."""

    LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}

    def test_level_ordering(self):
        """Log levels should be correctly ordered."""
        assert self.LEVELS["DEBUG"] < self.LEVELS["INFO"], "Condition must be true"
        assert self.LEVELS["INFO"] < self.LEVELS["WARNING"], "Condition must be true"
        assert self.LEVELS["WARNING"] < self.LEVELS["ERROR"], "Error should be raised or set"
        assert self.LEVELS["ERROR"] < self.LEVELS["CRITICAL"], "Error should be raised or set"

    def test_filter_by_level(self):
        """Filter logs by minimum level."""
        logs = [
            {"level": "DEBUG", "msg": "debug"},
            {"level": "INFO", "msg": "info"},
            {"level": "ERROR", "msg": "error"},
        ]
        min_level = self.LEVELS["INFO"]
        filtered = [entry for entry in logs if self.LEVELS.get(entry["level"], 0) >= min_level]
        assert len(filtered) == 2, "Filtered must not be empty"
        assert all(entry["level"] != "DEBUG" for entry in filtered), "Condition must be true"

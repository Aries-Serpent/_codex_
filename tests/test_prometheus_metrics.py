"""
Test Prometheus Metrics

Test module for prometheus metrics.
"""

#!/usr/bin/env python3
"""Tests for Prometheus metrics collection."""
import sys
from pathlib import Path

import pytest

# Add src to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from codex_ml.monitoring.metrics import (
    MetricsCollector,
    get_metrics_collector,
    record_latency,
    record_request,
)


@pytest.fixture(autouse=True)
def clear_prometheus_registry():
    """Clear Prometheus registry between tests to prevent collision."""
    pytest.importorskip("prometheus_client", reason="prometheus_client not installed")
    from prometheus_client import REGISTRY

    # Get collectors before test
    collectors_before = list(REGISTRY._collector_to_names.keys())

    yield

    # Clean up collectors added during test
    collectors_after = list(REGISTRY._collector_to_names.keys())
    for collector in collectors_after:
        if collector not in collectors_before:
            try:
                REGISTRY.unregister(collector)
            except (IOError, OSError) as _err:
                _ = None  # Already unregistered


def test_metrics_collector_initializes():
    """Test that MetricsCollector can be initialized."""
    collector = MetricsCollector()
    assert collector is not None, "collector must be initialized"


def test_metrics_collector_available_property():
    """Test that available property returns boolean."""
    collector = MetricsCollector()
    assert isinstance(collector.available, bool)


def test_metrics_collector_record_request_no_error():
    """Test that recording request doesn't raise errors."""
    collector = MetricsCollector()
    # Should not raise even if prometheus not available
    collector.record_request("GET", "/test", 200)


def test_metrics_collector_record_latency_no_error():
    """Test that recording latency doesn't raise errors."""
    collector = MetricsCollector()
    # Should not raise even if prometheus not available
    collector.record_latency(0.5, "GET", "/test")


def test_metrics_collector_record_error_no_error():
    """Test that recording error doesn't raise errors."""
    collector = MetricsCollector()
    # Should not raise even if prometheus not available
    collector.record_error("ValueError", "/test")


def test_metrics_collector_active_requests():
    """Test that active requests methods don't raise errors."""
    collector = MetricsCollector()

    collector.inc_active_requests()
    collector.dec_active_requests()


def test_get_metrics_collector_singleton():
    """Test that get_metrics_collector returns same instance."""
    collector1 = get_metrics_collector()
    collector2 = get_metrics_collector()

    assert collector1 is collector2, "collector1 is not valid"


def test_record_request_convenience_function():
    """Test the convenience function for recording requests."""
    record_request("POST", "/api/v1/test", 201)


def test_record_latency_convenience_function():
    """Test the convenience function for recording latency."""
    record_latency(1.23, "POST", "/api/v1/test")


def test_metrics_collector_defaults():
    """Test that methods work with default parameters."""
    collector = MetricsCollector()

    collector.record_request()
    collector.record_latency(0.1)


def test_metrics_graceful_without_prometheus():
    """Test that metrics work gracefully without prometheus_client installed."""
    # Even if prometheus_client is not installed, these should not raise
    collector = MetricsCollector()

    collector.record_request("GET", "/health", 200)
    collector.record_latency(0.05, "GET", "/health")
    collector.record_error("TestError", "/test")
    collector.inc_active_requests()
    collector.dec_active_requests()

    # Should complete without exceptions
    assert True, "True is not valid"

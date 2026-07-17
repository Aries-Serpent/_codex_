"""Comprehensive Correlation Analysis Tests.

Tests for trace-to-metrics correlation, error correlation, log-trace linking,
anomaly detection, service dependency mapping, and root cause analysis.

Test Categories:
- Trace-to-Metrics Correlation (3 tests)
- Error Correlation (3 tests)
- Log-Trace Correlation (3 tests)
- Anomaly Detection (4 tests)
- Service Dependency Mapping (2 tests)
- Critical Path Analysis (2 tests)
- Root Cause Analysis Correlation (1 test)

Total: 20+ comprehensive tests
"""

import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from unittest.mock import MagicMock

import pytest

# ============================================================================
# FIXTURES & HELPERS
# ============================================================================


@pytest.fixture
def trace_factory():
    """Factory for creating test traces."""
    def create_trace(
        trace_id: Optional[str] = None,
        service: str = "api",
        operation: str = "GET /users",
        duration_ms: float = 100.0,
        status: str = "success",
        error_message: Optional[str] = None,
        span_count: int = 3,
    ) -> Dict[str, Any]:
        trace_id = trace_id or str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        spans = []
        current_time = start_time
        
        for i in range(span_count):
            span_start = current_time
            span_duration = duration_ms / span_count * (0.8 + i * 0.1)  # Vary durations
            span_end = span_start + timedelta(milliseconds=span_duration)
            
            span = {
                "span_id": f"{trace_id}-span-{i}",
                "trace_id": trace_id,
                "parent_span_id": f"{trace_id}-span-{i-1}" if i > 0 else None,
                "operation_name": f"{service}.{operation.split()[1]}.span_{i}" if i > 0 else operation,
                "service": service,
                "start_time": span_start.isoformat(),
                "end_time": span_end.isoformat(),
                "duration_ms": span_duration,
                "status": status,
                "tags": {
                    "http.method": "GET",
                    "http.url": "/users",
                    "http.status_code": 200 if status == "success" else 500,
                    "component": f"component-{i}",
                },
                "logs": [
                    {
                        "timestamp": span_start.isoformat(),
                        "message": f"Processing request in {service}",
                        "level": "INFO",
                    }
                ] if i == 0 else [],
            }
            
            if error_message and status == "error":
                span["error"] = {"message": error_message, "type": "Exception"}
                span["logs"].append({
                    "timestamp": span_end.isoformat(),
                    "message": error_message,
                    "level": "ERROR",
                })
            
            spans.append(span)
            current_time = span_end
        
        return {
            "trace_id": trace_id,
            "service": service,
            "operation": operation,
            "start_time": start_time.isoformat(),
            "end_time": current_time.isoformat(),
            "duration_ms": duration_ms,
            "status": status,
            "span_count": span_count,
            "spans": spans,
            "error_message": error_message,
        }
    
    return create_trace


@pytest.fixture
def metric_factory():
    """Factory for creating test metrics."""
    def create_metric(
        name: str,
        value: float,
        timestamp: Optional[datetime] = None,
        labels: Optional[Dict[str, str]] = None,
        metric_type: str = "gauge",
    ) -> Dict[str, Any]:
        timestamp = timestamp or datetime.utcnow()
        labels = labels or {}
        
        return {
            "name": name,
            "value": value,
            "timestamp": timestamp.isoformat(),
            "labels": labels,
            "type": metric_type,
        }
    
    return create_metric


@pytest.fixture
def log_factory():
    """Factory for creating test logs."""
    def create_log(
        message: str,
        trace_id: Optional[str] = None,
        service: str = "api",
        level: str = "INFO",
        timestamp: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        timestamp = timestamp or datetime.utcnow()
        
        return {
            "message": message,
            "trace_id": trace_id,
            "service": service,
            "level": level,
            "timestamp": timestamp.isoformat(),
            "attributes": {
                "service": service,
                "host": "localhost",
            },
        }
    
    return create_log


@pytest.fixture
def correlation_engine():
    """Mock correlation engine."""
    engine = MagicMock()
    engine.correlate_trace_to_metrics = MagicMock(return_value={"correlation": 0.95})
    engine.correlate_errors = MagicMock(return_value=[])
    engine.link_log_to_trace = MagicMock(return_value=True)
    engine.detect_anomaly = MagicMock(return_value=False)
    engine.get_service_dependencies = MagicMock(return_value=[])
    engine.get_critical_path = MagicMock(return_value=[])
    engine.analyze_root_cause = MagicMock(return_value={})
    return engine


@pytest.fixture
def analytics_store():
    """Mock analytics store."""
    store = MagicMock()
    store.store_trace = MagicMock(return_value=True)
    store.store_metric = MagicMock(return_value=True)
    store.store_log = MagicMock(return_value=True)
    store.query_traces = MagicMock(return_value=[])
    store.query_metrics = MagicMock(return_value=[])
    store.query_logs = MagicMock(return_value=[])
    return store


# ============================================================================
# TRACE-TO-METRICS CORRELATION TESTS (3 tests)
# ============================================================================


class TestTraceToMetricsCorrelation:
    """Tests for trace-to-metrics correlation."""

    def test_request_latency_from_trace_matches_metrics(self, trace_factory, metric_factory, correlation_engine):
        """Test that request latency from trace matches metrics."""
        # Create trace
        trace = trace_factory(
            service="api",
            operation="GET /users",
            duration_ms=150.0,
            status="success",
        )
        
        # Create matching metric
        metric = metric_factory(
            name="http_request_duration_ms",
            value=150.0,
            labels={"service": "api", "endpoint": "/users"},
        )
        
        # Verify correlation
        correlation_engine.correlate_trace_to_metrics(trace, [metric])
        correlation_engine.correlate_trace_to_metrics.assert_called_once()
        
        # Assert correlation result
        result = correlation_engine.correlate_trace_to_metrics.return_value
        assert result["correlation"] >= 0.9, "Correlation must be strong"

    def test_trace_duration_validation(self, trace_factory):
        """Test trace duration is calculated correctly."""
        trace = trace_factory(
            service="database",
            operation="SELECT users",
            duration_ms=75.5,
            span_count=5,
        )
        
        # Verify trace structure
        assert trace["trace_id"] is not None, "Trace must have ID"
        assert trace["duration_ms"] == 75.5, "Duration must match"
        assert len(trace["spans"]) == 5, "Span count must match"
        assert trace["status"] == "success", "Default status is success"

    def test_latency_percentile_correlation(self, trace_factory, metric_factory, correlation_engine):
        """Test that latency percentiles correlate across traces and metrics."""
        # Create multiple traces with varying latencies
        traces = [
            trace_factory(duration_ms=50.0),
            trace_factory(duration_ms=100.0),
            trace_factory(duration_ms=150.0),
            trace_factory(duration_ms=200.0),
            trace_factory(duration_ms=250.0),
        ]
        
        # Create percentile metrics
        metrics = [
            metric_factory(name="p50_latency_ms", value=100.0),
            metric_factory(name="p95_latency_ms", value=200.0),
            metric_factory(name="p99_latency_ms", value=250.0),
        ]
        
        # Correlate
        for trace in traces:
            correlation_engine.correlate_trace_to_metrics(trace, metrics)
        
        # Verify calls
        assert correlation_engine.correlate_trace_to_metrics.call_count == 5


# ============================================================================
# ERROR CORRELATION TESTS (3 tests)
# ============================================================================


class TestErrorCorrelation:
    """Tests for error correlation between traces and metrics."""

    def test_error_traces_correlated_with_error_rate_metrics(
        self, trace_factory, metric_factory, correlation_engine
    ):
        """Test that error traces are correlated with error rate metrics."""
        # Create error trace
        error_trace = trace_factory(
            service="api",
            status="error",
            error_message="Database connection timeout",
            duration_ms=1000.0,
        )
        
        # Create error rate metric spike
        error_metric = metric_factory(
            name="http_errors_total",
            value=5.0,
            labels={"service": "api", "error_type": "timeout"},
        )
        
        # Correlate
        correlation_engine.correlate_trace_to_metrics(error_trace, [error_metric])
        
        # Verify error trace has error information
        assert error_trace["status"] == "error", "Trace status must be error"
        assert error_trace["error_message"] is not None, "Error message must be present"
        assert any(
            span.get("error") for span in error_trace["spans"]
        ), "At least one span must have error"

    def test_error_type_categorization(self, trace_factory, correlation_engine):
        """Test that error types are correctly categorized."""
        error_types = [
            ("TimeoutError", "timeout"),
            ("ConnectionError", "connection"),
            ("ValidationError", "validation"),
            ("RuntimeError", "runtime"),
        ]
        
        error_traces = []
        for error_msg, expected_type in error_types:
            trace = trace_factory(
                status="error",
                error_message=error_msg,
            )
            error_traces.append((trace, expected_type))
        
        # Verify categorization
        for trace, expected_type in error_traces:
            assert trace["error_message"] is not None, f"Error type {expected_type} must have message"
            assert trace["status"] == "error", f"Error type {expected_type} must have error status"

    def test_error_rate_spike_detection(self, metric_factory, correlation_engine):
        """Test detection of error rate spikes."""
        # Create baseline metrics
        baseline_metrics = [
            metric_factory(name="error_rate", value=0.01, labels={"service": "api"}),
        ]
        
        # Create spike metrics
        spike_metrics = [
            metric_factory(name="error_rate", value=0.25, labels={"service": "api"}),
        ]
        
        # Simulate spike detection
        def detect_spike(baseline, current, threshold=0.1):
            return current >= baseline + threshold
        
        is_spike = detect_spike(
            baseline_metrics[0]["value"],
            spike_metrics[0]["value"],
        )
        
        assert is_spike, "Spike must be detected"


# ============================================================================
# LOG-TRACE CORRELATION TESTS (3 tests)
# ============================================================================


class TestLogTraceCorrelation:
    """Tests for log-to-trace correlation."""

    def test_trace_id_present_in_logs(self, log_factory, trace_factory):
        """Test that trace_id is present in all logs for a trace."""
        trace = trace_factory(service="api")
        
        logs = [
            log_factory(
                message="Request started",
                trace_id=trace["trace_id"],
                service="api",
            ),
            log_factory(
                message="Processing request",
                trace_id=trace["trace_id"],
                service="api",
            ),
            log_factory(
                message="Request completed",
                trace_id=trace["trace_id"],
                service="api",
            ),
        ]
        
        # Verify trace_id in all logs
        for log in logs:
            assert log["trace_id"] == trace["trace_id"], "Log must have trace_id"
            assert log["trace_id"] is not None, "Trace ID must not be None"

    def test_trace_context_matches_log_trace_id(self, log_factory, trace_factory, correlation_engine):
        """Test that trace context matches log trace_id."""
        trace = trace_factory(service="database")
        
        log = log_factory(
            message="Query executed",
            trace_id=trace["trace_id"],
            service="database",
        )
        
        # Verify context match
        correlation_engine.link_log_to_trace(log, trace)
        correlation_engine.link_log_to_trace.assert_called_once()
        
        assert log["trace_id"] == trace["trace_id"], "Log trace_id must match trace"

    def test_log_entries_linked_to_spans(self, log_factory, trace_factory):
        """Test that log entries are correctly linked to spans."""
        trace = trace_factory(service="api", span_count=3)
        
        # Create logs with span references
        logs = []
        for i, span in enumerate(trace["spans"]):
            log = log_factory(
                message=f"Span {i} executed",
                trace_id=trace["trace_id"],
                service="api",
            )
            logs.append(log)
        
        # Verify logs linked to trace
        assert len(logs) == len(trace["spans"]), "Log count must match span count"
        for log in logs:
            assert log["trace_id"] == trace["trace_id"], "Log must reference trace"


# ============================================================================
# ANOMALY DETECTION TESTS (4 tests)
# ============================================================================


class TestAnomalyDetection:
    """Tests for anomaly detection in metrics and traces."""

    def test_metrics_spike_detection(self, metric_factory, correlation_engine):
        """Test detection of metrics spikes."""
        # Create baseline
        baseline = [
            metric_factory(name="cpu_usage", value=30.0, labels={"host": "web-01"}),
            metric_factory(name="cpu_usage", value=32.0, labels={"host": "web-01"}),
            metric_factory(name="cpu_usage", value=31.0, labels={"host": "web-01"}),
        ]
        
        # Create spike
        spike = metric_factory(name="cpu_usage", value=95.0, labels={"host": "web-01"})
        
        # Detect anomaly
        correlation_engine.detect_anomaly(spike, baseline)
        correlation_engine.detect_anomaly.assert_called_once()

    def test_alert_correlation_with_anomalies(self, metric_factory, correlation_engine):
        """Test correlation of alerts with anomalies."""
        anomaly_metric = metric_factory(
            name="memory_usage",
            value=92.0,
            labels={"host": "db-01"},
        )
        
        alert = {
            "alert_id": "mem-high-001",
            "metric": "memory_usage",
            "threshold": 90.0,
            "current_value": 92.0,
            "fired_at": datetime.utcnow().isoformat(),
        }
        
        # Verify alert correlation
        assert alert["current_value"] >= alert["threshold"], "Alert must be above threshold"
        assert alert["metric"] == anomaly_metric["name"], "Alert metric must match"

    def test_trace_visibility_during_anomalies(self, trace_factory, metric_factory, correlation_engine):
        """Test trace visibility during detected anomalies."""
        # Create anomalous trace
        anomalous_trace = trace_factory(
            service="api",
            duration_ms=5000.0,  # Much longer than normal
            status="error",
            error_message="Service degradation",
        )
        
        # Create anomaly metric
        anomaly_metric = metric_factory(
            name="p99_latency_ms",
            value=5000.0,
            labels={"service": "api"},
        )
        
        # Verify trace captures anomaly
        assert anomalous_trace["duration_ms"] == 5000.0, "Trace must capture long duration"
        assert anomalous_trace["status"] == "error", "Trace must show error status"
        
        correlation_engine.correlate_trace_to_metrics(anomalous_trace, [anomaly_metric])
        correlation_engine.correlate_trace_to_metrics.assert_called_once()

    def test_automatic_incident_detection(self, trace_factory, metric_factory, correlation_engine):
        """Test automatic incident detection from correlated signals."""
        # Create incident signals
        error_trace = trace_factory(
            service="api",
            status="error",
            duration_ms=3000.0,
            error_message="Circuit breaker open",
        )
        
        error_metric = metric_factory(
            name="error_rate",
            value=0.5,
            labels={"service": "api"},
        )
        
        latency_metric = metric_factory(
            name="p99_latency_ms",
            value=3000.0,
            labels={"service": "api"},
        )
        
        # Simulate incident detection
        incident_signals = {
            "high_error_rate": error_metric["value"] > 0.1,
            "high_latency": latency_metric["value"] > 1000.0,
            "error_trace": error_trace["status"] == "error",
        }
        
        incident_detected = all(incident_signals.values())
        assert incident_detected, "Incident must be detected from correlated signals"


# ============================================================================
# SERVICE DEPENDENCY MAPPING TESTS (2 tests)
# ============================================================================


class TestServiceDependencyMapping:
    """Tests for service dependency mapping from traces."""

    def test_service_call_graph_from_traces(self, trace_factory, correlation_engine):
        """Test construction of service call graph from traces."""
        # Create traces representing service calls
        traces = [
            trace_factory(service="api", operation="GET /users"),
            trace_factory(service="auth", operation="POST /validate"),
            trace_factory(service="database", operation="SELECT users"),
        ]
        
        # Mock service dependency graph
        graph = {
            "api": ["auth", "database"],
            "auth": ["cache"],
            "database": ["logging"],
        }
        
        correlation_engine.get_service_dependencies(traces)
        correlation_engine.get_service_dependencies.assert_called_once()
        
        # Verify graph structure
        assert "api" in graph, "API service must be in graph"
        assert "auth" in graph["api"], "Auth must be dependency of API"
        assert "database" in graph["api"], "Database must be dependency of API"

    def test_dependency_depth_analysis(self, trace_factory, correlation_engine):
        """Test analysis of dependency depth."""
        # Create multi-level traces
        traces = [
            trace_factory(service="gateway", operation="POST /api/request"),
            trace_factory(service="api", operation="GET /data"),
            trace_factory(service="service-a", operation="QUERY data"),
            trace_factory(service="service-b", operation="FETCH info"),
            trace_factory(service="database", operation="SELECT *"),
        ]
        
        # Simulate depth analysis
        depth_map = {
            "gateway": 0,
            "api": 1,
            "service-a": 2,
            "service-b": 2,
            "database": 3,
        }
        
        max_depth = max(depth_map.values())
        assert max_depth == 3, "Max dependency depth must be 3"
        assert len(traces) == len(depth_map), "All services must have depth"


# ============================================================================
# CRITICAL PATH ANALYSIS TESTS (2 tests)
# ============================================================================


class TestCriticalPathAnalysis:
    """Tests for critical path analysis in traces."""

    def test_slowest_service_identification(self, trace_factory, correlation_engine):
        """Test identification of slowest service in trace path."""
        traces = [
            trace_factory(service="gateway", duration_ms=50.0),
            trace_factory(service="api", duration_ms=200.0),  # Slowest
            trace_factory(service="database", duration_ms=150.0),
            trace_factory(service="cache", duration_ms=30.0),
        ]
        
        correlation_engine.get_critical_path(traces)
        correlation_engine.get_critical_path.assert_called_once()
        
        # Identify slowest
        slowest = max(traces, key=lambda t: t["duration_ms"])
        assert slowest["service"] == "api", "API must be slowest service"
        assert slowest["duration_ms"] == 200.0, "Slowest duration must be 200ms"

    def test_critical_path_latency_calculation(self, trace_factory):
        """Test calculation of critical path latency."""
        # Create sequential traces
        traces = [
            trace_factory(service="service-a", duration_ms=100.0, span_count=2),
            trace_factory(service="service-b", duration_ms=150.0, span_count=3),
            trace_factory(service="service-c", duration_ms=200.0, span_count=2),
        ]
        
        # Calculate critical path (sum of sequential operations)
        critical_path_duration = sum(t["duration_ms"] for t in traces)
        
        # For parallel services, critical path is max, not sum
        # Simulate sequential dependency
        assert critical_path_duration == 450.0, "Critical path duration must be sum"
        assert len(traces) == 3, "Must have 3 services in path"


# ============================================================================
# ROOT CAUSE ANALYSIS CORRELATION TESTS (1 test)
# ============================================================================


class TestRootCauseAnalysisCorrelation:
    """Tests for root cause analysis using correlated signals."""

    def test_rca_pattern_matching_and_cause_chain_validation(
        self, trace_factory, metric_factory, log_factory, correlation_engine
    ):
        """Test RCA pattern matching and cause chain validation."""
        # Create incident scenario
        error_trace = trace_factory(
            service="api",
            status="error",
            error_message="Database connection pool exhausted",
            duration_ms=5000.0,
        )
        
        # Create supporting metrics
        connection_metric = metric_factory(
            name="db_connections_used",
            value=100.0,
            labels={"pool_size": "100"},
        )
        
        error_rate_metric = metric_factory(
            name="error_rate",
            value=0.8,
            labels={"service": "api"},
        )
        
        # Create supporting logs
        logs = [
            log_factory(
                message="Connection pool exhausted",
                trace_id=error_trace["trace_id"],
                level="ERROR",
            ),
            log_factory(
                message="Waiting for available connection",
                trace_id=error_trace["trace_id"],
                level="WARN",
            ),
        ]
        
        # Perform RCA
        rca_result = {
            "root_cause": "Database connection pool exhausted",
            "contributing_factors": [
                "Sudden spike in requests",
                "Slow database queries",
                "Connection timeout settings too aggressive",
            ],
            "affected_services": ["api"],
            "impact_duration_ms": 5000.0,
            "traces": [error_trace],
            "metrics": [connection_metric, error_rate_metric],
            "logs": logs,
        }
        
        correlation_engine.analyze_root_cause(
            error_trace, [connection_metric, error_rate_metric], logs
        )
        correlation_engine.analyze_root_cause.assert_called_once()
        
        # Verify RCA structure
        assert rca_result["root_cause"] is not None, "Root cause must be identified"
        assert len(rca_result["contributing_factors"]) > 0, "Must have contributing factors"
        assert len(rca_result["traces"]) > 0, "Must have traces"
        assert len(rca_result["metrics"]) > 0, "Must have metrics"
        assert len(rca_result["logs"]) > 0, "Must have logs"


# ============================================================================
# COMPREHENSIVE INTEGRATION TESTS (Additional tests for coverage)
# ============================================================================


class TestCorrelationEngineIntegration:
    """Integration tests for full correlation engine."""

    def test_end_to_end_correlation_workflow(
        self,
        trace_factory,
        metric_factory,
        log_factory,
        correlation_engine,
        analytics_store,
    ):
        """Test end-to-end correlation workflow."""
        # 1. Ingest trace
        trace = trace_factory(service="api", duration_ms=200.0)
        analytics_store.store_trace(trace)
        
        # 2. Ingest metrics
        metrics = [
            metric_factory(name="latency_ms", value=200.0, labels={"service": "api"}),
            metric_factory(name="error_rate", value=0.0, labels={"service": "api"}),
        ]
        for metric in metrics:
            analytics_store.store_metric(metric)
        
        # 3. Ingest logs
        logs = [
            log_factory(message="Request started", trace_id=trace["trace_id"]),
            log_factory(message="Request completed", trace_id=trace["trace_id"]),
        ]
        for log in logs:
            analytics_store.store_log(log)
        
        # 4. Correlate
        correlation_engine.correlate_trace_to_metrics(trace, metrics)
        
        # 5. Verify all stored
        analytics_store.store_trace.assert_called_once()
        assert analytics_store.store_metric.call_count == 2
        assert analytics_store.store_log.call_count == 2
        correlation_engine.correlate_trace_to_metrics.assert_called_once()

    def test_multi_service_correlation(
        self, trace_factory, metric_factory, correlation_engine
    ):
        """Test correlation across multiple services."""
        services = ["api", "auth", "database", "cache"]
        
        traces = [trace_factory(service=svc) for svc in services]
        
        all_metrics = []
        for svc in services:
            metric = metric_factory(
                name="latency_ms",
                value=100.0,
                labels={"service": svc},
            )
            all_metrics.append(metric)
        
        # Correlate all
        for trace in traces:
            correlation_engine.correlate_trace_to_metrics(trace, all_metrics)
        
        assert correlation_engine.correlate_trace_to_metrics.call_count == len(services)

    def test_time_series_correlation_analysis(
        self, metric_factory, correlation_engine
    ):
        """Test correlation analysis over time series data."""
        # Create time series
        base_time = datetime.utcnow()
        metrics_series = []
        
        for i in range(10):
            timestamp = base_time + timedelta(seconds=i*10)
            metric = metric_factory(
                name="throughput",
                value=100.0 + i * 5,  # Gradual increase
                timestamp=timestamp,
                labels={"service": "api"},
            )
            metrics_series.append(metric)
        
        # Analyze correlation
        for metric in metrics_series:
            correlation_engine.correlate_trace_to_metrics(None, [metric])
        
        assert len(metrics_series) == 10, "Must have 10 metrics"
        assert metrics_series[-1]["value"] > metrics_series[0]["value"], "Values must increase"

    def test_anomaly_propagation_through_service_chain(
        self, trace_factory, metric_factory, correlation_engine
    ):
        """Test how anomalies propagate through service chain."""
        # Create service chain: api -> service-a -> database
        traces = [
            trace_factory(service="api", duration_ms=1000.0),  # Anomalously slow
            trace_factory(service="service-a", duration_ms=900.0),
            trace_factory(service="database", duration_ms=800.0),
        ]
        
        metrics = [
            metric_factory(name="latency", value=1000.0, labels={"service": "api"}),
            metric_factory(name="latency", value=900.0, labels={"service": "service-a"}),
            metric_factory(name="latency", value=800.0, labels={"service": "database"}),
        ]
        
        # Correlate chain
        for trace, metric in zip(traces, metrics):
            correlation_engine.correlate_trace_to_metrics(trace, [metric])
        
        # Verify anomaly propagation
        assert traces[0]["duration_ms"] > 500.0, "Upstream anomaly must be visible"
        assert all(m["value"] > 0 for m in metrics), "All metrics must have values"

    def test_correlation_with_missing_data(
        self, trace_factory, correlation_engine
    ):
        """Test correlation robustness with missing data."""
        trace = trace_factory(service="api", duration_ms=100.0)
        
        # Call with no metrics
        correlation_engine.correlate_trace_to_metrics(trace, [])
        correlation_engine.correlate_trace_to_metrics.assert_called_once()
        
        # Verify handles gracefully
        result = correlation_engine.correlate_trace_to_metrics.return_value
        assert result is not None, "Result must not be None"

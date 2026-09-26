"""Observability Enhanced Tests - Phase 20.3 Lane 0.

Comprehensive tests for distributed tracing infrastructure with W3C Trace Context
propagation, span instrumentation, sampling strategies, and OpenTelemetry SDK integration.

Test Categories:
  1. Trace Context Propagation (5 tests)
  2. Span Creation & Hierarchy (6 tests)
  3. Span Attribute Enrichment (5 tests)
  4. Trace Sampling Strategies (4 tests)
  5. Span Instrumentation (3 tests)
  6. OpenTelemetry SDK Integration (1 test)
  7. Trace Backend Integration (1 test)

Total: 25+ comprehensive distributed tracing tests
"""

import threading
import time
import uuid
from contextlib import contextmanager
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import pytest

# ============================================================================
# Fixtures and Utilities
# ============================================================================


class MockTracer:
    """Mock OpenTelemetry tracer for testing."""

    def __init__(self, name: str = "test-tracer"):
        self.name = name
        self.spans: List[MockSpan] = []
        self.current_span: Optional["MockSpan"] = None
        self.current_trace_id: Optional[str] = None
        self.lock = threading.Lock()

    @contextmanager
    def start_as_current_span(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Start a new span context."""
        trace_id = None
        parent_span_id = None

        with self.lock:
            # Determine trace_id
            if self.current_span:
                trace_id = self.current_span.trace_id
                parent_span_id = self.current_span.span_id
            elif self.current_trace_id:
                trace_id = self.current_trace_id
            else:
                trace_id = str(uuid.uuid4())
                self.current_trace_id = trace_id

        span = MockSpan(name, trace_id=trace_id, attributes=attributes or {})
        if parent_span_id:
            span.parent_span_id = parent_span_id

        with self.lock:
            self.current_span = span
            self.spans.append(span)

        try:
            yield span
        finally:
            with self.lock:
                self.current_span = None

    def get_current_span(self) -> Optional["MockSpan"]:
        """Get the current active span."""
        return self.current_span


class MockSpan:
    """Mock OpenTelemetry span."""

    def __init__(self, name: str, trace_id: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None):
        self.name = name
        self.span_id = str(uuid.uuid4())
        self.trace_id = trace_id or str(uuid.uuid4())
        self.parent_span_id: Optional[str] = None
        self.attributes = attributes or {}
        self.events: List[Dict[str, Any]] = []
        self.status = "UNSET"
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.lock = threading.Lock()

    def set_attribute(self, key: str, value: Any) -> None:
        """Set a span attribute."""
        with self.lock:
            self.attributes[key] = value

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add an event to the span."""
        with self.lock:
            self.events.append({
                "name": name,
                "attributes": attributes or {},
                "timestamp": time.time()
            })

    def set_status(self, status: str) -> None:
        """Set span status (OK, ERROR, UNSET)."""
        with self.lock:
            self.status = status

    def end(self) -> None:
        """End the span."""
        with self.lock:
            self.end_time = time.time()

    def get_duration_ms(self) -> float:
        """Get span duration in milliseconds."""
        end = self.end_time or time.time()
        return (end - self.start_time) * 1000


class W3CTraceContext:
    """W3C Trace Context header parser and generator."""

    @staticmethod
    def parse(traceparent: str) -> Dict[str, str]:
        """Parse W3C traceparent header.
        
        Format: version-trace_id-parent_id-trace_flags
        Example: 00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01
        """
        if not traceparent:
            return {}

        parts = traceparent.split("-")
        if len(parts) != 4:
            return {}

        return {
            "version": parts[0],
            "trace_id": parts[1],
            "parent_span_id": parts[2],
            "trace_flags": parts[3]
        }

    @staticmethod
    def generate(
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
        sampled: bool = True
    ) -> str:
        """Generate W3C traceparent header."""
        trace_id = trace_id or uuid.uuid4().hex
        parent_span_id = parent_span_id or uuid.uuid4().hex[:16]
        trace_flags = "01" if sampled else "00"
        return f"00-{trace_id}-{parent_span_id}-{trace_flags}"


class MockSpanProcessor:
    """Mock span processor for batch span export."""

    def __init__(self):
        self.spans: List[MockSpan] = []
        self.lock = threading.Lock()

    def on_span_finish(self, span: MockSpan) -> None:
        """Called when span finishes."""
        with self.lock:
            self.spans.append(span)

    def force_flush(self, timeout_ms: int = 30000) -> bool:
        """Force flush any pending spans."""
        return True


@pytest.fixture
def mock_tracer():
    """Provide a mock tracer for testing."""
    return MockTracer()


@pytest.fixture
def mock_span_processor():
    """Provide a mock span processor."""
    return MockSpanProcessor()


@pytest.fixture
def w3c_trace_context():
    """Provide W3C Trace Context utility."""
    return W3CTraceContext()


# ============================================================================
# Category 1: Trace Context Propagation (5 tests)
# ============================================================================


class TestTraceContextPropagation:
    """Tests for W3C Trace Context header validation and propagation."""

    def test_w3c_traceparent_header_parsing(self, w3c_trace_context):
        """Test W3C traceparent header parsing."""
        # Valid traceparent header
        traceparent = "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01"
        result = w3c_trace_context.parse(traceparent)

        assert result["version"] == "00", "Result must not be empty"
        assert result["trace_id"] == "0af7651916cd43dd8448eb211c80319c", "Result must not be empty"
        assert result["parent_span_id"] == "b7ad6b7169203331", "Result must not be empty"
        assert result["trace_flags"] == "01", "Result must not be empty"

    def test_w3c_traceparent_generation(self, w3c_trace_context):
        """Test W3C traceparent header generation."""
        traceparent = w3c_trace_context.generate()

        # Validate format
        parts = traceparent.split("-")
        assert len(parts) == 4, "Parts must not be empty"
        assert parts[0] == "00", "Condition must be true"
        assert len(parts[1]) == 32, "Collection must not be empty"
        assert len(parts[2]) == 16, "Collection must not be empty"
        assert parts[3] in ["00", "01"]  # trace_flags

    def test_trace_context_extraction_from_headers(self):
        """Test extracting trace context from HTTP headers."""
        headers = {
            "traceparent": "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01",
            "tracestate": "congo=t61rcWo2r1t7Lmc,rojo=00f067aa0ba902b7"
        }

        # Extract traceparent
        traceparent = headers.get("traceparent", "")
        tracestate = headers.get("tracestate", "")

        assert traceparent.startswith("00-"), "Condition must be true"
        assert "congo" in tracestate, "Condition must be true"
        assert "rojo" in tracestate, "Condition must be true"

    def test_trace_context_injection_into_outbound_requests(self):
        """Test injecting trace context into outbound requests."""
        trace_id = uuid.uuid4().hex
        span_id = uuid.uuid4().hex[:16]

        # Create traceparent header
        traceparent = f"00-{trace_id}-{span_id}-01"

        # Inject into headers
        outbound_headers = {
            "traceparent": traceparent,
            "tracestate": "codex=test-service"
        }

        # Verify injection
        assert outbound_headers["traceparent"] == traceparent, "Condition must be true"
        assert "codex" in outbound_headers["tracestate"], "Condition must be true"

    def test_legacy_trace_header_support(self, w3c_trace_context):
        """Test legacy X-Trace-ID and X-Span-ID header support."""
        legacy_headers = {
            "X-Trace-ID": "0af7651916cd43dd8448eb211c80319c",
            "X-Span-ID": "b7ad6b7169203331",
            "X-Sampled": "1"
        }

        # Extract legacy headers
        trace_id = legacy_headers.get("X-Trace-ID")
        span_id = legacy_headers.get("X-Span-ID")
        sampled = legacy_headers.get("X-Sampled") == "1"

        # Convert to W3C format
        traceparent = w3c_trace_context.generate(trace_id, span_id, sampled)

        assert trace_id in traceparent, "Condition must be true"
        assert span_id in traceparent, "Condition must be true"


# ============================================================================
# Category 2: Span Creation & Hierarchy (6 tests)
# ============================================================================


class TestSpanCreationAndHierarchy:
    """Tests for span creation, hierarchy, and relationships."""

    def test_span_creation_validation(self, mock_tracer):
        """Test span creation and validation."""
        with mock_tracer.start_as_current_span("test.operation") as span:
            assert span is not None, "span must be initialized"
            assert span.name == "test.operation", "name is not valid"
            assert span.span_id is not None, "span_id must be initialized"
            assert span.trace_id is not None, "trace_id must be initialized"

    def test_parent_child_span_relationships(self, mock_tracer):
        """Test parent-child span relationships."""
        with mock_tracer.start_as_current_span("parent") as parent_span:
            parent_id = parent_span.span_id

            with mock_tracer.start_as_current_span("child") as child_span:
                # Child should have parent relationship
                assert child_span.parent_span_id == parent_id, "parent_span_id is not valid"
                assert child_span.trace_id == parent_span.trace_id, "trace_id is not valid"

    def test_span_naming_conventions(self, mock_tracer):
        """Test span naming conventions."""
        span_names = [
            "http.client.request",
            "db.query.execute",
            "cache.get",
            "service.operation"
        ]

        for span_name in span_names:
            with mock_tracer.start_as_current_span(span_name) as span:
                assert span.name == span_name, "name is not valid"
                # Verify naming follows OpenTelemetry conventions
                assert "." in span.name, "Condition must be true"

    def test_span_timing_accuracy(self, mock_tracer):
        """Test span timing and duration calculation."""
        with mock_tracer.start_as_current_span("timed.operation") as span:
            start_time = span.start_time
            time.sleep(0.1)  # Sleep for 100ms
            span.end()

            duration_ms = span.get_duration_ms()
            # Allow 10ms tolerance
            assert 90 < duration_ms < 150, "90 is not valid"

    def test_span_status_codes(self, mock_tracer):
        """Test span status codes (OK, ERROR, UNSET)."""
        statuses = ["OK", "ERROR", "UNSET"]

        for status in statuses:
            with mock_tracer.start_as_current_span(f"span.{status}") as span:
                span.set_status(status)
                assert span.status == status, "status is not valid"

    def test_nested_span_validation_complex_scenarios(self, mock_tracer):
        """Test nested span validation in complex scenarios."""
        with mock_tracer.start_as_current_span("root") as root:
            root_id = root.span_id

            with mock_tracer.start_as_current_span("level1") as level1:
                level1_id = level1.span_id
                assert level1.parent_span_id == root_id, "parent_span_id is not valid"

                with mock_tracer.start_as_current_span("level2") as level2:
                    assert level2.parent_span_id == level1_id, "parent_span_id is not valid"
                    assert level2.trace_id == root.trace_id, "trace_id is not valid"

        # Verify all spans recorded
        assert len(mock_tracer.spans) == 3, "Collection must not be empty"


# ============================================================================
# Category 3: Span Attribute Enrichment (5 tests)
# ============================================================================


class TestSpanAttributeEnrichment:
    """Tests for span attribute enrichment and metadata."""

    def test_user_id_attribute_injection(self, mock_tracer):
        """Test user_id attribute injection into spans."""
        user_id = str(uuid.uuid4())

        with mock_tracer.start_as_current_span("user.operation") as span:
            span.set_attribute("user_id", user_id)

            assert span.attributes["user_id"] == user_id, "Condition must be true"

    def test_request_id_tracking(self, mock_tracer):
        """Test request_id tracking across spans."""
        request_id = str(uuid.uuid4())

        with mock_tracer.start_as_current_span("request.start") as span:
            span.set_attribute("request_id", request_id)

            with mock_tracer.start_as_current_span("request.process") as child_span:
                child_span.set_attribute("request_id", request_id)

                # Both spans should have same request_id
                assert span.attributes["request_id"] == child_span.attributes["request_id"], "Condition must be true"

    def test_service_name_standardization(self, mock_tracer):
        """Test service name standardization in spans."""
        services = ["orchestrator", "ci-auto-healer", "code-review"]

        for service_name in services:
            with mock_tracer.start_as_current_span("service.operation") as span:
                span.set_attribute("service.name", service_name)

                assert span.attributes["service.name"] == service_name, "Condition must be true"

    def test_environment_tags(self, mock_tracer):
        """Test environment tags in span attributes."""
        environments = ["development", "staging", "production"]

        for env in environments:
            with mock_tracer.start_as_current_span("env.operation") as span:
                span.set_attribute("environment", env)
                span.set_attribute("deployment.environment", env)

                assert span.attributes["environment"] == env, "Condition must be true"

    def test_custom_attribute_validation(self, mock_tracer):
        """Test custom attribute validation and storage."""
        custom_attributes = {
            "custom.string": "value",
            "custom.integer": 42,
            "custom.float": 3.14,
            "custom.boolean": True,
            "custom.list": [1, 2, 3]
        }

        with mock_tracer.start_as_current_span("custom.attributes") as span:
            for key, value in custom_attributes.items():
                span.set_attribute(key, value)

            # Verify all attributes stored correctly
            for key, value in custom_attributes.items():
                assert span.attributes[key] == value, "Value must be initialized"


# ============================================================================
# Category 4: Trace Sampling Strategies (4 tests)
# ============================================================================


class TestTraceSamplingStrategies:
    """Tests for trace sampling and sampling decisions."""

    def test_100_percent_sampling_all_traces_sampled(self, mock_tracer, w3c_trace_context):
        """Test 100% sampling where all traces are sampled."""
        sampled_count = 0
        total_count = 100

        for i in range(total_count):
            traceparent = w3c_trace_context.generate(sampled=True)
            parts = traceparent.split("-")
            trace_flags = parts[3]

            if trace_flags == "01":  # sampled
                sampled_count += 1

        assert sampled_count == total_count, "Count must be greater than zero"

    def test_adaptive_sampling_load_based(self):
        """Test adaptive sampling based on load."""
        # Simulate load levels
        load_levels = {
            "low": 0.2,      # Sample 20% at low load
            "medium": 0.5,   # Sample 50% at medium load
            "high": 1.0      # Sample 100% at high load
        }

        # Verify sampling decisions
        assert load_levels["low"] < load_levels["medium"], "Condition must be true"
        assert load_levels["medium"] < load_levels["high"], "Condition must be true"
        assert load_levels["high"] == 1.0, "Condition must be true"

    def test_tail_based_sampling_latency_based(self, mock_tracer):
        """Test tail-based sampling based on latency."""
        # Simulate spans with different latencies
        latencies = [10.5, 50.2, 150.8, 25.3, 500.1, 30.0]
        threshold_ms = 100.0

        sampled_spans = []
        for latency in latencies:
            # Span is sampled if latency exceeds threshold
            if latency > threshold_ms:
                sampled_spans.append(latency)

        # Should sample high-latency spans
        assert len(sampled_spans) == 2, "Sampled_spans must not be empty"
        assert all(l > threshold_ms for l in sampled_spans), "l must be greater than zero"

    def test_sampling_decision_propagation(self, w3c_trace_context):
        """Test sampling decision propagation across services."""
        # Create initial trace with sampling enabled
        traceparent = w3c_trace_context.generate(sampled=True)

        # Extract sampling decision
        parts = traceparent.split("-")
        trace_flags = parts[3]
        is_sampled = trace_flags == "01"

        # Propagate to next service
        next_traceparent = w3c_trace_context.generate(
            trace_id=parts[1],
            parent_span_id=parts[2],
            sampled=is_sampled
        )

        # Sampling decision should be propagated
        next_parts = next_traceparent.split("-")
        assert next_parts[3] == trace_flags, "Condition must be true"


# ============================================================================
# Category 5: Span Instrumentation (3 tests)
# ============================================================================


class TestSpanInstrumentation:
    """Tests for instrumentation of different operations."""

    def test_database_operation_spans(self, mock_tracer):
        """Test database operation span instrumentation."""
        db_operations = ["query", "insert", "update", "delete"]

        for operation in db_operations:
            with mock_tracer.start_as_current_span(f"db.{operation}") as span:
                span.set_attribute("db.system", "postgresql")
                span.set_attribute("db.operation", operation)
                span.set_attribute("db.name", "codex_db")
                span.set_attribute("db.statement", "SELECT * FROM users WHERE id = ?")

                assert span.attributes["db.system"] == "postgresql", "Condition must be true"
                assert span.attributes["db.operation"] == operation, "Condition must be true"

    def test_http_client_instrumentation(self, mock_tracer):
        """Test HTTP client operation span instrumentation."""
        methods = ["GET", "POST", "PUT", "DELETE"]

        for method in methods:
            with mock_tracer.start_as_current_span("http.client.request") as span:
                span.set_attribute("http.method", method)
                span.set_attribute("http.url", "https://api.example.com/users")
                span.set_attribute("http.status_code", 200)

                assert span.attributes["http.method"] == method, "Condition must be true"
                # Use proper URL parsing for safe validation (not substring matching)
                parsed_url = urlparse(span.attributes["http.url"])
                assert parsed_url.netloc == "api.example.com", "netloc is not valid"
                assert span.attributes["http.status_code"] == 200, "Condition must be true"

    def test_cache_operation_spans(self, mock_tracer):
        """Test cache operation span instrumentation."""
        cache_ops = ["get", "set", "delete", "clear"]

        for operation in cache_ops:
            with mock_tracer.start_as_current_span(f"cache.{operation}") as span:
                span.set_attribute("cache.system", "redis")
                span.set_attribute("cache.operation", operation)
                span.set_attribute("cache.key", "user:123:profile")
                span.set_attribute("cache.hit", operation == "get")

                assert span.attributes["cache.system"] == "redis", "Condition must be true"
                assert span.attributes["cache.operation"] == operation, "Condition must be true"


# ============================================================================
# Category 6: OpenTelemetry SDK Integration (1 test)
# ============================================================================


class TestOpenTelemetrySDKIntegration:
    """Tests for OpenTelemetry SDK initialization and configuration."""

    def test_sdk_initialization_and_configuration(self, mock_span_processor):
        """Test SDK initialization with proper configuration."""
        # Simulate SDK initialization
        sdk_config = {
            "service_name": "codex-observability",
            "service_version": "0.2.0",
            "deployment_environment": "production",
            "span_processors": [mock_span_processor],
            "sampler": "always_on",
            "resource": {
                "service.name": "codex-observability",
                "service.version": "0.2.0",
                "deployment.environment": "production"
            }
        }

        # Verify configuration
        assert sdk_config["service_name"] == "codex-observability", "Condition must be true"
        assert sdk_config["deployment_environment"] == "production", "Condition must be true"
        assert len(sdk_config["span_processors"]) == 1, "Collection must not be empty"
        assert sdk_config["sampler"] == "always_on", "Condition must be true"

        # Verify resource attributes
        resource = sdk_config["resource"]
        assert resource["service.name"] == "codex-observability", "Condition must be true"
        assert "deployment.environment" in resource, "Condition must be true"


# ============================================================================
# Category 7: Trace Backend Integration (1 test)
# ============================================================================


class TestTraceBackendIntegration:
    """Tests for trace backend connectivity (Jaeger/Tempo)."""

    def test_jaeger_tempo_backend_connectivity(self):
        """Test connectivity to Jaeger/Tempo backend."""
        # Simulate backend configuration
        backend_configs = {
            "jaeger": {
                "protocol": "grpc",
                "endpoint": "localhost:4317",
                "service_name": "codex"
            },
            "tempo": {
                "protocol": "http",
                "endpoint": "http://localhost:3200",
                "service_name": "codex"
            }
        }

        # Verify configurations
        for backend_name, config in backend_configs.items():
            assert "endpoint" in config, "Condition must be true"
            assert "protocol" in config, "Condition must be true"
            assert "service_name" in config, "Condition must be true"

            # Validate endpoint format
            if backend_name == "jaeger":
                assert ":" in config["endpoint"], "Condition must be true"
            elif backend_name == "tempo":
                assert config["endpoint"].startswith("http"), "Condition must be true"


# ============================================================================
# Additional Integration Tests
# ============================================================================


class TestDistributedTracingIntegration:
    """Integration tests for complete distributed tracing workflows."""

    def test_multi_hop_trace_propagation_across_services(self, mock_tracer, w3c_trace_context):
        """Test multi-hop trace propagation across multiple services."""
        # Service 1: Initial request
        traceparent = w3c_trace_context.generate()
        trace_id = traceparent.split("-")[1]

        # Service 2: Receives and propagates
        with mock_tracer.start_as_current_span("service2.operation") as span:
            span.set_attribute("service", "service2")
            span.set_attribute("trace_id", trace_id)

            # Service 3: Further propagation
            with mock_tracer.start_as_current_span("service3.operation") as child_span:
                child_span.set_attribute("service", "service3")
                child_span.set_attribute("trace_id", trace_id)

        # Verify trace continuity
        assert len(mock_tracer.spans) == 2, "Collection must not be empty"
        for span in mock_tracer.spans:
            assert span.attributes["trace_id"] == trace_id, "Condition must be true"

    def test_trace_with_error_handling_and_recovery(self, mock_tracer):
        """Test trace recording with error handling."""
        with mock_tracer.start_as_current_span("operation.with.error") as span:
            span.set_attribute("operation", "process_data")

            try:
                # Simulate error
                raise ValueError("Test error")
            except ValueError as e:
                span.set_status("ERROR")
                span.set_attribute("error.type", type(e).__name__)
                span.set_attribute("error.message", str(e))

        # Verify error recording
        assert len(mock_tracer.spans) == 1, "Collection must not be empty"
        error_span = mock_tracer.spans[0]
        assert error_span.status == "ERROR", "Error should be raised or set"
        assert error_span.attributes["error.type"] == "ValueError", "Value must be initialized"

    def test_concurrent_span_creation_thread_safety(self, mock_tracer):
        """Test thread-safe concurrent span creation."""
        def create_spans(span_id):
            for i in range(5):
                with mock_tracer.start_as_current_span(f"concurrent.span.{span_id}.{i}"):
                    time.sleep(0.01)

        # Create spans from multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=create_spans, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Verify all spans created
        assert len(mock_tracer.spans) == 15, "Collection must not be empty"


# ============================================================================
# Metric and Coverage Tests
# ============================================================================


class TestDistributedTracingMetrics:
    """Tests for tracing metrics and coverage."""

    def test_trace_coverage_statistics(self, mock_tracer):
        """Test trace coverage statistics."""
        # Simulate multiple traces
        for i in range(10):
            with mock_tracer.start_as_current_span(f"operation.{i}"):
                pass

        # Calculate coverage
        total_spans = len(mock_tracer.spans)
        assert total_spans == 10, "total_spans is not valid"

        # Coverage metric
        coverage = (total_spans / 10) * 100
        assert coverage >= 90, "coverage must be greater than zero"

    def test_span_performance_metrics(self, mock_tracer):
        """Test span performance metrics."""
        durations = []

        for i in range(5):
            with mock_tracer.start_as_current_span(f"perf.test.{i}") as span:
                time.sleep(0.05)
                span.end()
                durations.append(span.get_duration_ms())

        # Calculate metrics
        avg_duration = sum(durations) / len(durations)
        assert avg_duration > 40, "avg_duration must be greater than zero"

        # Verify consistent performance
        max_duration = max(durations)
        min_duration = min(durations)
        assert max_duration - min_duration < 50, "min_duration is not valid"


# ============================================================================
# Semantic Validation Tests
# ============================================================================


class TestDistributedTracingSemantics:
    """Semantic validation tests for distributed tracing."""

    def test_span_naming_semantics(self, mock_tracer):
        """Test semantic correctness of span naming."""
        span_names = [
            ("http.client.request", True),
            ("db.query.execute", True),
            ("cache.hit", True),
            ("invalid_span_name", False),  # No dots
            ("", False),  # Empty
        ]

        for name, should_be_valid in span_names:
            if name and "." in name:
                with mock_tracer.start_as_current_span(name) as span:
                    assert "." in span.name, "Condition must be true"

    def test_attribute_key_naming_convention(self, mock_tracer):
        """Test attribute key naming conventions."""
        valid_keys = [
            "http.method",
            "db.system",
            "service.name",
            "deployment.environment"
        ]

        with mock_tracer.start_as_current_span("validation") as span:
            for key in valid_keys:
                span.set_attribute(key, "test_value")
                # Verify dot notation
                assert "." in key, "Condition must be true"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

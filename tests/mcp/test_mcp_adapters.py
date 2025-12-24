"""Tests for MCP adapter components."""

from __future__ import annotations

import pytest


class TestMockBackend:
    """Test suite for MockBackend adapter."""

    @pytest.fixture
    def backend(self):
        """Create a mock backend for testing."""
        from src.mcp.adapters.mock_backend import MockBackend

        return MockBackend(simulated_latency_ms=0)

    @pytest.mark.asyncio
    async def test_connect(self, backend):
        """Test connection to mock backend."""
        result = await backend.connect()

        assert result is True
        assert backend.is_connected is True

    @pytest.mark.asyncio
    async def test_disconnect(self, backend):
        """Test disconnection from mock backend."""
        await backend.connect()
        await backend.disconnect()

        assert backend.is_connected is False

    @pytest.mark.asyncio
    async def test_health_check_connected(self, backend):
        """Test health check when connected."""
        await backend.connect()
        healthy = await backend.health_check()

        assert healthy is True

    @pytest.mark.asyncio
    async def test_health_check_disconnected(self, backend):
        """Test health check when disconnected."""
        healthy = await backend.health_check()

        assert healthy is False

    @pytest.mark.asyncio
    async def test_query_returns_results(self, backend):
        """Test querying mock backend."""
        await backend.connect()

        # Upsert some vectors first
        await backend.upsert([
            {"id": "vec1", "values": [0.1, 0.2, 0.3], "metadata": {"text": "hello"}},
            {"id": "vec2", "values": [0.4, 0.5, 0.6], "metadata": {"text": "world"}},
        ])

        result = await backend.query("test query", top_k=5)

        assert result.success is True
        assert "matches" in result.data
        assert len(result.data["matches"]) <= 5

    @pytest.mark.asyncio
    async def test_query_when_disconnected(self, backend):
        """Test query fails when not connected."""
        result = await backend.query("test")

        assert result.success is False
        assert result.error == "Not connected"

    @pytest.mark.asyncio
    async def test_upsert_vectors(self, backend):
        """Test upserting vectors."""
        await backend.connect()

        result = await backend.upsert([
            {"id": "vec1", "values": [0.1, 0.2]},
            {"id": "vec2", "values": [0.3, 0.4]},
        ])

        assert result.success is True
        assert result.data["upserted_count"] == 2
        assert backend.get_vector_count() == 2

    @pytest.mark.asyncio
    async def test_call_count(self, backend):
        """Test call counting."""
        await backend.connect()

        await backend.query("q1")
        await backend.query("q2")
        await backend.upsert([{"id": "1", "values": []}])

        assert backend.get_call_count() == 3

    @pytest.mark.asyncio
    async def test_reset(self, backend):
        """Test resetting mock backend."""
        await backend.connect()
        await backend.upsert([{"id": "1", "values": [0.1]}])

        backend.reset()

        assert backend.get_call_count() == 0
        assert backend.get_vector_count() == 0

    def test_adapter_name(self, backend):
        """Test adapter name."""
        assert backend.adapter_name == "mock"


class TestMCPMetrics:
    """Test suite for MCPMetrics."""

    @pytest.fixture
    def metrics(self):
        """Create metrics instance for testing."""
        from src.mcp.metrics.mcp_metrics import MCPMetrics

        return MCPMetrics()

    def test_record_query(self, metrics):
        """Test recording query metrics."""
        metrics.record_query(
            adapter="mock",
            duration_ms=100,
            success=True,
            result_count=5,
        )

        summary = metrics.get_summary()
        assert "counters" in summary
        assert "histograms" in summary

    def test_record_upsert(self, metrics):
        """Test recording upsert metrics."""
        metrics.record_upsert(
            adapter="pinecone",
            duration_ms=200,
            success=True,
            vector_count=100,
        )

        summary = metrics.get_summary()
        assert summary is not None

    def test_record_error(self, metrics):
        """Test recording error metrics."""
        metrics.record_error(adapter="mock", error_type="connection")
        metrics.record_error(adapter="mock", error_type="timeout")

        # Verify errors are counted
        summary = metrics.get_summary()
        assert "counters" in summary

    def test_set_connection_status(self, metrics):
        """Test setting connection status gauge."""
        metrics.set_connection_status("mock", True)
        metrics.set_connection_status("pinecone", False)

        summary = metrics.get_summary()
        assert "gauges" in summary


class TestMetricCollector:
    """Test suite for MetricCollector."""

    @pytest.fixture
    def collector(self):
        """Create a collector for testing."""
        from src.mcp.metrics.mcp_metrics import MetricCollector

        return MetricCollector()

    def test_increment_counter(self, collector):
        """Test incrementing counters."""
        collector.increment("requests")
        collector.increment("requests")
        collector.increment("requests", value=3)

        assert collector.get_counter("requests") == 5

    def test_counter_with_labels(self, collector):
        """Test counters with labels."""
        collector.increment("requests", labels={"method": "GET"})
        collector.increment("requests", labels={"method": "POST"})
        collector.increment("requests", labels={"method": "GET"})

        assert collector.get_counter("requests", {"method": "GET"}) == 2
        assert collector.get_counter("requests", {"method": "POST"}) == 1

    def test_set_gauge(self, collector):
        """Test setting gauges."""
        collector.set_gauge("connections", 5)
        assert collector.get_gauge("connections") == 5

        collector.set_gauge("connections", 3)
        assert collector.get_gauge("connections") == 3

    def test_observe_histogram(self, collector):
        """Test histogram observations."""
        collector.observe("latency", 100)
        collector.observe("latency", 200)
        collector.observe("latency", 150)

        summary = collector.get_histogram_summary("latency")

        assert summary is not None
        assert summary.count == 3
        assert summary.min_value == 100
        assert summary.max_value == 200
        assert summary.avg_value == 150

    def test_reset(self, collector):
        """Test resetting collector."""
        collector.increment("test")
        collector.set_gauge("gauge", 10)

        collector.reset()

        assert collector.get_counter("test") == 0
        assert collector.get_gauge("gauge") == 0

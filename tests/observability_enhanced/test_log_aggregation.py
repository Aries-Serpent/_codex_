"""Comprehensive log aggregation infrastructure tests.

Test categories:
1. Log Collection Infrastructure (4 tests)
2. Log Parsing & Field Extraction (4 tests)
3. Log Enrichment (3 tests)
4. Log Retention Policies (3 tests)
5. Full-Text Search (2 tests)
6. Log Filtering & Querying (2 tests)
7. Structured Logging (1 test)
8. Log Cardinality Management (1 test)

Total: 20+ tests
"""

import io
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pytest  # noqa: E402

# ============================================================================
# Log Aggregation Infrastructure Classes
# ============================================================================


@dataclass
class LogEntry:
    """Represents a single log entry."""

    timestamp: datetime
    level: str
    message: str
    source: str
    fields: dict[str, Any] = field(default_factory=dict)


@dataclass
class LogCollector:
    """Collects logs from multiple sources."""

    sources: dict[str, Any] = field(default_factory=dict)
    _logs: list[LogEntry] = field(default_factory=list)
    _lock: Any = field(default_factory=lambda: __import__("threading").Lock())

    def add_source(self, name: str, source: Any) -> None:
        """Add a log source."""
        self.sources[name] = source

    def collect_from_stdout(self) -> list[str]:
        """Collect logs from stdout."""
        if "stdout" not in self.sources:
            return []
        return self.sources["stdout"].getvalue().splitlines()

    def collect_from_stderr(self) -> list[str]:
        """Collect logs from stderr."""
        if "stderr" not in self.sources:
            return []
        return self.sources["stderr"].getvalue().splitlines()

    def collect_from_file(self, filepath: Path) -> list[str]:
        """Collect logs from file."""
        if filepath.exists():
            return filepath.read_text().splitlines()
        return []

    def aggregate(self) -> list[str]:
        """Aggregate logs from all sources."""
        all_logs = []
        all_logs.extend(self.collect_from_stdout())
        all_logs.extend(self.collect_from_stderr())
        return all_logs


@dataclass
class LogParser:
    """Parses logs and extracts fields."""

    def parse_json(self, log_line: str) -> dict[str, Any]:
        """Parse JSON log line."""
        try:
            return json.loads(log_line)
        except json.JSONDecodeError:
            return {}

    def parse_keyvalue(self, log_line: str) -> dict[str, str]:
        """Parse key=value log line."""
        result = {}
        pattern = r'(\w+)=(["\']?)(.+?)\2(?:\s|$)'
        for match in re.finditer(pattern, log_line):
            key, _, value = match.groups()
            result[key] = value
        return result

    def parse_unstructured(self, log_line: str) -> dict[str, str]:
        """Extract basic fields from unstructured log."""
        parts = log_line.split()
        return {
            "raw": log_line,
            "word_count": len(parts),
            "length": len(log_line),
        }

    def standardize_fields(self, parsed: dict[str, Any]) -> dict[str, Any]:
        """Standardize field names and types."""
        standardized = {}
        for key, value in parsed.items():
            # Normalize field names
            normalized_key = key.lower().replace("-", "_")
            standardized[normalized_key] = value
        return standardized


@dataclass
class LogEnricher:
    """Enriches logs with additional context."""

    service_name: str = "default-service"
    pod_id: str = "pod-1"
    container_id: str = "container-1"
    hostname: str = "localhost"

    def enrich(self, log_entry: LogEntry) -> LogEntry:
        """Enrich log entry with context."""
        enriched_fields = {
            **log_entry.fields,
            "service_name": self.service_name,
            "pod_id": self.pod_id,
            "container_id": self.container_id,
            "hostname": self.hostname,
        }
        return LogEntry(
            timestamp=log_entry.timestamp,
            level=log_entry.level,
            message=log_entry.message,
            source=log_entry.source,
            fields=enriched_fields,
        )

    def standardize_timestamp(self, log_entry: LogEntry) -> LogEntry:
        """Ensure timestamp is timezone-aware UTC."""
        if log_entry.timestamp.tzinfo is None:
            # Assume UTC if naive
            ts = log_entry.timestamp.replace(tzinfo=timezone.utc)
        else:
            # Convert to UTC
            ts = log_entry.timestamp.astimezone(timezone.utc)
        return LogEntry(
            timestamp=ts,
            level=log_entry.level,
            message=log_entry.message,
            source=log_entry.source,
            fields=log_entry.fields,
        )


@dataclass
class RetentionPolicy:
    """Log retention policy."""

    name: str
    retention_days: int
    archive_after_days: int
    compress: bool = True

    def should_archive(self, log_age_days: int) -> bool:
        """Check if log should be archived."""
        return log_age_days >= self.archive_after_days

    def should_delete(self, log_age_days: int) -> bool:
        """Check if log should be deleted."""
        return log_age_days >= self.retention_days


@dataclass
class LogStore:
    """In-memory log storage with search capability."""

    logs: list[dict[str, Any]] = field(default_factory=list)
    _index: dict[str, set[int]] = field(default_factory=dict)

    def add_log(self, log_entry: dict[str, Any]) -> None:
        """Add log to store."""
        idx = len(self.logs)
        self.logs.append(log_entry)
        # Index message tokens for full-text search
        for word in log_entry.get("message", "").split():
            if word.lower() not in self._index:
                self._index[word.lower()] = set()
            self._index[word.lower()].add(idx)

    def search(self, query: str) -> list[dict[str, Any]]:
        """Full-text search logs."""
        query_words = query.lower().split()
        if not query_words:
            return []

        # Find logs containing all query words
        result_indices = set(range(len(self.logs)))
        for word in query_words:
            result_indices &= self._index.get(word, set())

        return [self.logs[i] for i in sorted(result_indices)]

    def filter_by_level(self, level: str) -> list[dict[str, Any]]:
        """Filter logs by level."""
        return [log for log in self.logs if log.get("level") == level]

    def filter_by_service(self, service_name: str) -> list[dict[str, Any]]:
        """Filter logs by service name."""
        return [
            log
            for log in self.logs
            if log.get("fields", {}).get("service_name") == service_name
        ]

    def filter_by_time_range(
        self, start: datetime, end: datetime
    ) -> list[dict[str, Any]]:
        """Filter logs by time range."""
        result = []
        for log in self.logs:
            ts_str = log.get("timestamp", "")
            if ts_str:
                try:
                    ts = datetime.fromisoformat(ts_str)
                    if start <= ts <= end:
                        result.append(log)
                except (ValueError, AttributeError):
                    pass
        return result


class CardinalityLimiter:
    """Manages high-cardinality field limits."""

    def __init__(self, max_cardinality: int = 10000):
        """Initialize cardinality limiter."""
        self.max_cardinality = max_cardinality
        self.field_cardinality: dict[str, set[Any]] = {}

    def check_cardinality(self, field_name: str, value: Any) -> bool:
        """Check if adding value would exceed cardinality limit."""
        if field_name not in self.field_cardinality:
            self.field_cardinality[field_name] = set()

        cardinality_set = self.field_cardinality[field_name]
        if value not in cardinality_set:
            if len(cardinality_set) >= self.max_cardinality:
                return False
            cardinality_set.add(value)
        return True

    def get_field_cardinality(self, field_name: str) -> int:
        """Get current cardinality of field."""
        return len(self.field_cardinality.get(field_name, set()))


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def log_collector():
    """Create a log collector with mock sources."""
    collector = LogCollector()
    collector.add_source("stdout", io.StringIO())
    collector.add_source("stderr", io.StringIO())
    return collector


@pytest.fixture
def log_parser():
    """Create a log parser."""
    return LogParser()


@pytest.fixture
def log_enricher():
    """Create a log enricher."""
    return LogEnricher(
        service_name="test-service",
        pod_id="test-pod-123",
        container_id="test-container-456",
        hostname="test-host",
    )


@pytest.fixture
def log_store():
    """Create a log store."""
    return LogStore()


@pytest.fixture
def retention_policy():
    """Create a retention policy."""
    return RetentionPolicy(
        name="default", retention_days=30, archive_after_days=7, compress=True
    )


@pytest.fixture
def cardinality_limiter():
    """Create a cardinality limiter."""
    return CardinalityLimiter(max_cardinality=10000)


@pytest.fixture
def sample_log_entry():
    """Create a sample log entry."""
    return LogEntry(
        timestamp=datetime.now(timezone.utc),
        level="INFO",
        message="Test log message",
        source="test_app",
        fields={"request_id": "req-123", "user_id": "user-456"},
    )


@pytest.fixture
def sample_logs():
    """Create sample logs for testing."""
    now = datetime.now(timezone.utc)
    return [
        {
            "timestamp": (now - timedelta(hours=1)).isoformat(),
            "level": "INFO",
            "message": "User login successful",
            "source": "auth_service",
            "fields": {"user_id": "user-1", "service_name": "auth"},
        },
        {
            "timestamp": (now - timedelta(hours=0.5)).isoformat(),
            "level": "ERROR",
            "message": "Database connection failed",
            "source": "db_service",
            "fields": {"error_code": "CONN_TIMEOUT", "service_name": "database"},
        },
        {
            "timestamp": now.isoformat(),
            "level": "WARNING",
            "message": "High memory usage detected",
            "source": "monitoring",
            "fields": {"memory_percent": "85", "service_name": "monitoring"},
        },
    ]


# ============================================================================
# Log Collection Infrastructure Tests (4 tests)
# ============================================================================


class TestLogCollection:
    """Tests for log collection from multiple sources."""

    def test_collect_from_stdout(self, log_collector):
        """Test collecting logs from stdout."""
        stdout_source = log_collector.sources["stdout"]
        stdout_source.write("INFO: Application started\n")
        stdout_source.write("INFO: Processing request\n")

        logs = log_collector.collect_from_stdout()
        assert len(logs) == 2
        assert "Application started" in logs[0]
        assert "Processing request" in logs[1]

    def test_collect_from_stderr(self, log_collector):
        """Test collecting logs from stderr."""
        stderr_source = log_collector.sources["stderr"]
        stderr_source.write("ERROR: Configuration error\n")
        stderr_source.write("ERROR: Startup failed\n")

        logs = log_collector.collect_from_stderr()
        assert len(logs) == 2
        assert "Configuration error" in logs[0]
        assert "Startup failed" in logs[1]

    def test_collect_from_file(self, log_collector, tmp_path):
        """Test collecting logs from file."""
        log_file = tmp_path / "app.log"
        log_file.write_text("INFO: Log line 1\nINFO: Log line 2\nWARN: Log line 3\n")

        logs = log_collector.collect_from_file(log_file)
        assert len(logs) == 3
        assert "Log line 1" in logs[0]
        assert "Log line 3" in logs[2]

    def test_multi_source_aggregation(self, log_collector):
        """Test aggregating logs from multiple sources."""
        log_collector.sources["stdout"].write("STDOUT: Message 1\n")
        log_collector.sources["stderr"].write("STDERR: Message 2\n")

        aggregated = log_collector.aggregate()
        assert len(aggregated) == 2
        assert any("STDOUT" in log for log in aggregated)
        assert any("STDERR" in log for log in aggregated)


# ============================================================================
# Log Parsing & Field Extraction Tests (4 tests)
# ============================================================================


class TestLogParsing:
    """Tests for log parsing and field extraction."""

    def test_parse_json_logs(self, log_parser):
        """Test parsing JSON log format."""
        json_log = '{"level": "INFO", "message": "Test", "request_id": "123"}'
        parsed = log_parser.parse_json(json_log)

        assert parsed["level"] == "INFO"
        assert parsed["message"] == "Test"
        assert parsed["request_id"] == "123"

    def test_parse_keyvalue_logs(self, log_parser):
        """Test parsing key=value log format."""
        kv_log = 'level=INFO message="Test message" request_id=123'
        parsed = log_parser.parse_keyvalue(kv_log)

        assert parsed.get("level") == "INFO"
        assert parsed.get("message") == "Test message"
        assert parsed.get("request_id") == "123"

    def test_parse_unstructured_logs(self, log_parser):
        """Test extracting data from unstructured logs."""
        unstructured = "This is a simple log message with multiple words"
        parsed = log_parser.parse_unstructured(unstructured)

        assert parsed["raw"] == unstructured
        assert parsed["word_count"] == 9
        assert parsed["length"] == len(unstructured)

    def test_field_standardization(self, log_parser):
        """Test field standardization."""
        data = {"Request-ID": "123", "USER-Name": "alice", "error_code": "ERR_001"}
        standardized = log_parser.standardize_fields(data)

        assert "request_id" in standardized
        assert "user_name" in standardized
        assert standardized["error_code"] == "ERR_001"


# ============================================================================
# Log Enrichment Tests (3 tests)
# ============================================================================


class TestLogEnrichment:
    """Tests for log enrichment."""

    def test_service_enrichment(self, log_enricher, sample_log_entry):
        """Test adding service_name tag to logs."""
        enriched = log_enricher.enrich(sample_log_entry)

        assert enriched.fields["service_name"] == "test-service"
        assert enriched.fields["pod_id"] == "test-pod-123"
        assert enriched.fields["container_id"] == "test-container-456"

    def test_timestamp_standardization(self, log_enricher):
        """Test timestamp standardization to UTC."""
        # Create naive datetime
        naive_dt = datetime(2024, 1, 1, 12, 0, 0)
        log_entry = LogEntry(
            timestamp=naive_dt,
            level="INFO",
            message="Test",
            source="test",
        )

        standardized = log_enricher.standardize_timestamp(log_entry)
        assert standardized.timestamp.tzinfo is not None
        assert standardized.timestamp.tzinfo == timezone.utc

    def test_hostname_enrichment(self, log_enricher, sample_log_entry):
        """Test hostname field enrichment."""
        enriched = log_enricher.enrich(sample_log_entry)

        assert enriched.fields["hostname"] == "test-host"


# ============================================================================
# Log Retention Policy Tests (3 tests)
# ============================================================================


class TestLogRetentionPolicies:
    """Tests for log retention policies."""

    def test_retention_policy_archive_trigger(self, retention_policy):
        """Test retention policy archive trigger logic."""
        # Log younger than archive threshold
        assert not retention_policy.should_archive(5)

        # Log older than archive threshold
        assert retention_policy.should_archive(7)
        assert retention_policy.should_archive(10)

    def test_retention_policy_deletion(self, retention_policy):
        """Test retention policy deletion logic."""
        # Log within retention window
        assert not retention_policy.should_delete(15)

        # Log exceeding retention window
        assert retention_policy.should_delete(30)
        assert retention_policy.should_delete(40)

    def test_custom_retention_policies(self):
        """Test different retention policy configurations."""
        short_term = RetentionPolicy(
            name="short_term", retention_days=7, archive_after_days=1
        )
        long_term = RetentionPolicy(
            name="long_term", retention_days=365, archive_after_days=30
        )

        # Short-term: archive after 1 day
        assert short_term.should_archive(1)

        # Long-term: archive after 30 days
        assert not long_term.should_archive(15)
        assert long_term.should_archive(30)


# ============================================================================
# Full-Text Search Tests (2 tests)
# ============================================================================


class TestFullTextSearch:
    """Tests for full-text log search."""

    def test_search_accuracy(self, log_store, sample_logs):
        """Test full-text search accuracy."""
        for log in sample_logs:
            log_store.add_log(log)

        # Search for single term
        results = log_store.search("login")
        assert len(results) == 1
        assert "login" in results[0]["message"].lower()

        # Search for multiple terms
        results = log_store.search("database connection")
        assert len(results) == 1
        assert "Database connection" in results[0]["message"]

    def test_search_performance_at_scale(self, log_store):
        """Test search performance with large log volume."""
        now = datetime.now(timezone.utc)

        # Add 1000 logs
        for i in range(1000):
            log_store.add_log(
                {
                    "timestamp": (now - timedelta(hours=i % 24)).isoformat() + "Z",
                    "level": "INFO",
                    "message": f"Log message {i} with important data",
                    "source": "perf_test",
                    "fields": {"index": str(i)},
                }
            )

        # Search should be fast
        import time

        start = time.time()
        results = log_store.search("important")
        elapsed = time.time() - start

        assert len(results) == 1000
        assert elapsed < 0.5  # Should complete in less than 500ms


# ============================================================================
# Log Filtering & Querying Tests (2 tests)
# ============================================================================


class TestLogFiltering:
    """Tests for log filtering and querying."""

    def test_filter_expression_validation(self, log_store, sample_logs):
        """Test log filtering by various expressions."""
        for log in sample_logs:
            log_store.add_log(log)

        # Filter by level
        errors = log_store.filter_by_level("ERROR")
        assert len(errors) == 1
        assert "Database connection failed" in errors[0]["message"]

        # Filter by service
        auth_logs = log_store.filter_by_service("auth")
        assert len(auth_logs) == 1

    def test_query_result_accuracy(self, log_store, sample_logs):
        """Test query result accuracy."""
        for log in sample_logs:
            log_store.add_log(log)

        now = datetime.now(timezone.utc)
        start = now - timedelta(hours=2)
        end = now

        # Time range query
        results = log_store.filter_by_time_range(start, end)
        assert len(results) == 3  # All logs in range


# ============================================================================
# Structured Logging Tests (1 test)
# ============================================================================


class TestStructuredLogging:
    """Tests for structured logging."""

    def test_json_format_validation(self, log_parser):
        """Test structured JSON log format validation."""
        json_logs = [
            '{"timestamp":"2024-01-01T00:00:00Z","level":"INFO","message":"msg1","request_id":"123"}',
            '{"timestamp":"2024-01-01T00:01:00Z","level":"ERROR","message":"msg2","error_code":"ERR_001"}',
        ]

        for log_line in json_logs:
            parsed = log_parser.parse_json(log_line)
            assert "timestamp" in parsed
            assert "level" in parsed
            assert "message" in parsed
            assert isinstance(parsed, dict)


# ============================================================================
# Log Cardinality Management Tests (1 test)
# ============================================================================


class TestCardinalityManagement:
    """Tests for log cardinality management."""

    def test_high_cardinality_field_limits(self, cardinality_limiter):
        """Test high-cardinality field limits."""
        # Add values up to limit
        for i in range(100):
            result = cardinality_limiter.check_cardinality("user_id", f"user-{i}")
            assert result is True

        assert cardinality_limiter.get_field_cardinality("user_id") == 100

        # Limit to 100 for testing
        limiter = CardinalityLimiter(max_cardinality=100)
        for i in range(100):
            assert limiter.check_cardinality("request_id", f"req-{i}") is True

        # Next value should be rejected
        assert limiter.check_cardinality("request_id", "req-100") is False
        assert limiter.get_field_cardinality("request_id") == 100


# ============================================================================
# Integration Tests
# ============================================================================


class TestLogAggregationIntegration:
    """Integration tests for complete log aggregation workflow."""

    def test_end_to_end_log_aggregation(
        self, log_collector, log_parser, log_enricher, log_store
    ):
        """Test complete end-to-end log aggregation workflow."""
        # Collect
        log_collector.sources["stdout"].write("level=INFO message='Test' request_id=123\n")
        logs = log_collector.collect_from_stdout()
        assert len(logs) == 1

        # Parse
        parsed = log_parser.parse_keyvalue(logs[0])
        assert "level" in parsed

        # Create entry
        entry = LogEntry(
            timestamp=datetime.now(timezone.utc),
            level=parsed.get("level", "INFO"),
            message=parsed.get("message", ""),
            source="stdout",
            fields=parsed,
        )

        # Enrich
        enriched = log_enricher.enrich(entry)
        assert enriched.fields["service_name"] is not None

        # Store
        log_dict = {
            "timestamp": enriched.timestamp.isoformat() + "Z",
            "level": enriched.level,
            "message": enriched.message,
            "source": enriched.source,
            "fields": enriched.fields,
        }
        log_store.add_log(log_dict)

        # Query
        results = log_store.filter_by_level("INFO")
        assert len(results) >= 1

    def test_multiple_services_aggregation(self, log_store):
        """Test aggregation of logs from multiple services."""
        services = ["auth", "database", "cache", "api"]
        now = datetime.now(timezone.utc)

        for service in services:
            log_store.add_log(
                {
                    "timestamp": now.isoformat() + "Z",
                    "level": "INFO",
                    "message": f"{service} service online",
                    "source": service,
                    "fields": {"service_name": service},
                }
            )

        # Verify all services logged
        for service in services:
            results = log_store.filter_by_service(service)
            assert len(results) == 1

    def test_log_lifecycle_management(self, retention_policy):
        """Test complete log lifecycle from creation to deletion."""
        # New log (0 days old)
        assert not retention_policy.should_archive(0)
        assert not retention_policy.should_delete(0)

        # Log after 5 days
        assert not retention_policy.should_archive(5)
        assert not retention_policy.should_delete(5)

        # Log after 7 days (archive threshold)
        assert retention_policy.should_archive(7)
        assert not retention_policy.should_delete(7)

        # Log after 30 days (retention threshold)
        assert retention_policy.should_archive(30)
        assert retention_policy.should_delete(30)


# ============================================================================
# Error Handling Tests
# ============================================================================


class TestErrorHandling:
    """Tests for error handling in log aggregation."""

    def test_invalid_json_handling(self, log_parser):
        """Test handling of invalid JSON logs."""
        invalid_json = '{invalid json'
        parsed = log_parser.parse_json(invalid_json)
        assert parsed == {}

    def test_missing_required_fields(self, log_parser):
        """Test handling of logs with missing required fields."""
        incomplete_log = '{"message": "test"}'
        parsed = log_parser.parse_json(incomplete_log)
        assert "message" in parsed
        assert "level" not in parsed

    def test_empty_log_handling(self, log_store):
        """Test handling of empty logs."""
        log_store.add_log(
            {
                "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
                "level": "INFO",
                "message": "",
                "source": "test",
            }
        )

        results = log_store.search("nonexistent")
        assert len(results) == 0


# ============================================================================
# Performance Tests
# ============================================================================


class TestPerformance:
    """Performance tests for log aggregation."""

    def test_bulk_log_ingestion(self, log_store):
        """Test bulk ingestion of logs."""
        now = datetime.now(timezone.utc)

        # Ingest 10000 logs
        import time

        start = time.time()
        for i in range(10000):
            log_store.add_log(
                {
                    "timestamp": (now - timedelta(seconds=i)).isoformat() + "Z",
                    "level": "INFO" if i % 2 == 0 else "ERROR",
                    "message": f"Log message {i}",
                    "source": "perf_test",
                    "fields": {"index": str(i)},
                }
            )
        elapsed = time.time() - start

        assert len(log_store.logs) == 10000
        assert elapsed < 5.0  # Should complete in < 5 seconds

    def test_concurrent_log_operations(self, cardinality_limiter):
        """Test concurrent cardinality checking."""
        import concurrent.futures

        def check_values(thread_id):
            for i in range(100):
                cardinality_limiter.check_cardinality(
                    f"field_{thread_id}", f"value_{i}"
                )

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(check_values, i) for i in range(4)]
            concurrent.futures.wait(futures)

        # Verify operations completed
        total_cardinality = sum(
            cardinality_limiter.get_field_cardinality(f"field_{i}")
            for i in range(4)
        )
        assert total_cardinality == 400


# ============================================================================
# Configuration Tests
# ============================================================================


class TestConfiguration:
    """Tests for log aggregation configuration."""

    def test_retention_policy_configuration(self):
        """Test retention policy configuration options."""
        policies = [
            RetentionPolicy("dev", 7, 1, compress=False),
            RetentionPolicy("staging", 30, 7, compress=True),
            RetentionPolicy("production", 365, 90, compress=True),
        ]

        assert len(policies) == 3
        assert policies[0].retention_days == 7
        assert policies[1].retention_days == 30
        assert policies[2].retention_days == 365

    def test_enricher_configuration(self):
        """Test log enricher configuration."""
        enricher = LogEnricher(
            service_name="api-service",
            pod_id="pod-xyz",
            container_id="container-abc",
            hostname="api-host-1",
        )

        assert enricher.service_name == "api-service"
        assert enricher.pod_id == "pod-xyz"
        assert enricher.container_id == "container-abc"

    def test_cardinality_limiter_configuration(self):
        """Test cardinality limiter configuration."""
        limiter = CardinalityLimiter(max_cardinality=50000)
        assert limiter.max_cardinality == 50000


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

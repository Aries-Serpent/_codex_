"""
Tests for codex.archive.logging_config module.

This module contains tests for structured logging helpers.
"""

import json


class TestStructuredLogRecord:
    """Tests for StructuredLogRecord dataclass."""

    def test_basic_creation(self):
        """Test StructuredLogRecord basic creation."""
        from codex.archive.logging_config import StructuredLogRecord

        record = StructuredLogRecord(
            level="INFO",
            message="Test message",
            timestamp="2024-01-01T00:00:00.000000Z",
            component="test_component",
            extra={"key": "value"},
        )

        assert record.level == "INFO", "level is not valid"
        assert record.message == "Test message", "message is not valid"
        assert record.timestamp == "2024-01-01T00:00:00.000000Z", "timestamp is not valid"
        assert record.component == "test_component", "component is not valid"
        assert record.extra == {"key": "value"}, "Value must be initialized"

    def test_to_dict(self):
        """Test to_dict method."""
        from codex.archive.logging_config import StructuredLogRecord

        record = StructuredLogRecord(
            level="WARNING",
            message="Warning message",
            timestamp="2024-01-01T12:00:00.000000Z",
            component="warning_component",
            extra={"warning_type": "deprecation"},
        )

        result = record.to_dict()

        assert result["level"] == "WARNING", "Result must not be empty"
        assert result["message"] == "Warning message", "Result must not be empty"
        assert result["timestamp"] == "2024-01-01T12:00:00.000000Z", "Result must not be empty"
        assert result["component"] == "warning_component", "Result must not be empty"
        assert result["warning_type"] == "deprecation", "Result must not be empty"

    def test_to_json(self):
        """Test to_json method."""
        from codex.archive.logging_config import StructuredLogRecord

        record = StructuredLogRecord(
            level="ERROR",
            message="Error occurred",
            timestamp="2024-01-01T00:00:00.000000Z",
            component="error_handler",
            extra={"code": 500},
        )

        result = record.to_json()

        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed["level"] == "ERROR", "Error should be raised or set"
        assert parsed["message"] == "Error occurred", "Error should be raised or set"

    def test_to_text_with_extra(self):
        """Test to_text method with extra fields."""
        from codex.archive.logging_config import StructuredLogRecord

        record = StructuredLogRecord(
            level="DEBUG",
            message="Debug info",
            timestamp="2024-01-01T00:00:00.000000Z",
            component="debugger",
            extra={"trace_id": "abc123"},
        )

        result = record.to_text()

        assert "[DEBUG]" in result, "Result must not be empty"
        assert "Debug info" in result, "Result must not be empty"
        assert "trace_id=abc123" in result, "Result must not be empty"

    def test_to_text_without_extra(self):
        """Test to_text method without extra fields."""
        from codex.archive.logging_config import StructuredLogRecord

        record = StructuredLogRecord(
            level="INFO",
            message="Simple message",
            timestamp="2024-01-01T00:00:00.000000Z",
            component="simple",
            extra={},
        )

        result = record.to_text()

        assert "[INFO]" in result, "Result must not be empty"
        assert "Simple message" in result, "Result must not be empty"
        assert "--" not in result, "Result must not be empty"


class TestModuleConstants:
    """Tests for module-level constants."""

    def test_iso_format(self):
        """Test ISO_FORMAT constant."""
        from codex.archive.logging_config import ISO_FORMAT

        assert "%Y-%m-%dT%H:%M:%S" in ISO_FORMAT, "Condition must be true"

    def test_standard_fields(self):
        """Test _STANDARD_FIELDS constant."""
        from codex.archive.logging_config import _STANDARD_FIELDS

        assert "name" in _STANDARD_FIELDS, "Condition must be true"
        assert "msg" in _STANDARD_FIELDS, "Condition must be true"
        assert "levelname" in _STANDARD_FIELDS, "Condition must be true"

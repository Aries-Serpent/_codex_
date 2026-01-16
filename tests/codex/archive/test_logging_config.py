"""
Tests for codex.archive.logging_config module.

This module contains tests for structured logging helpers.
"""

import pytest
import json
from unittest.mock import patch, MagicMock


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
            extra={"key": "value"}
        )
        
        assert record.level == "INFO"
        assert record.message == "Test message"
        assert record.timestamp == "2024-01-01T00:00:00.000000Z"
        assert record.component == "test_component"
        assert record.extra == {"key": "value"}

    def test_to_dict(self):
        """Test to_dict method."""
        from codex.archive.logging_config import StructuredLogRecord
        
        record = StructuredLogRecord(
            level="WARNING",
            message="Warning message",
            timestamp="2024-01-01T12:00:00.000000Z",
            component="warning_component",
            extra={"warning_type": "deprecation"}
        )
        
        result = record.to_dict()
        
        assert result["level"] == "WARNING"
        assert result["message"] == "Warning message"
        assert result["timestamp"] == "2024-01-01T12:00:00.000000Z"
        assert result["component"] == "warning_component"
        assert result["warning_type"] == "deprecation"

    def test_to_json(self):
        """Test to_json method."""
        from codex.archive.logging_config import StructuredLogRecord
        
        record = StructuredLogRecord(
            level="ERROR",
            message="Error occurred",
            timestamp="2024-01-01T00:00:00.000000Z",
            component="error_handler",
            extra={"code": 500}
        )
        
        result = record.to_json()
        
        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed["level"] == "ERROR"
        assert parsed["message"] == "Error occurred"

    def test_to_text_with_extra(self):
        """Test to_text method with extra fields."""
        from codex.archive.logging_config import StructuredLogRecord
        
        record = StructuredLogRecord(
            level="DEBUG",
            message="Debug info",
            timestamp="2024-01-01T00:00:00.000000Z",
            component="debugger",
            extra={"trace_id": "abc123"}
        )
        
        result = record.to_text()
        
        assert "[DEBUG]" in result
        assert "Debug info" in result
        assert "trace_id=abc123" in result

    def test_to_text_without_extra(self):
        """Test to_text method without extra fields."""
        from codex.archive.logging_config import StructuredLogRecord
        
        record = StructuredLogRecord(
            level="INFO",
            message="Simple message",
            timestamp="2024-01-01T00:00:00.000000Z",
            component="simple",
            extra={}
        )
        
        result = record.to_text()
        
        assert "[INFO]" in result
        assert "Simple message" in result
        assert "--" not in result


class TestModuleConstants:
    """Tests for module-level constants."""

    def test_iso_format(self):
        """Test ISO_FORMAT constant."""
        from codex.archive.logging_config import ISO_FORMAT
        
        assert "%Y-%m-%dT%H:%M:%S" in ISO_FORMAT

    def test_standard_fields(self):
        """Test _STANDARD_FIELDS constant."""
        from codex.archive.logging_config import _STANDARD_FIELDS
        
        assert "name" in _STANDARD_FIELDS
        assert "msg" in _STANDARD_FIELDS
        assert "levelname" in _STANDARD_FIELDS

"""
Test Codex Structured Logging Module

Tests for the structured logging module.
Tests JSON logging, session management, and formatters.
"""

from __future__ import annotations

import json
import logging
import os
from unittest.mock import MagicMock, patch

from codex_ml.codex_structured_logging import (
    JsonFormatter,
    _json_safe,
    _prepare_session_payload,
    _utc_iso,
    get_session_id,
    init_json_logging,
    set_session_id,
)


class TestJsonSafe:
    """Tests for _json_safe function."""

    def test_string_passthrough(self) -> None:
        """Test string values pass through."""
        assert _json_safe("hello") == "hello", "Condition must be true"

    def test_int_passthrough(self) -> None:
        """Test int values pass through."""
        assert _json_safe(42) == 42, "Condition must be true"

    def test_float_passthrough(self) -> None:
        """Test float values pass through."""
        assert _json_safe(3.14) == 3.14, "Condition must be true"

    def test_bool_passthrough(self) -> None:
        """Test bool values pass through."""
        assert _json_safe(True) is True, "Condition must be true"
        assert _json_safe(False) is False, "Condition must be true"

    def test_none_passthrough(self) -> None:
        """Test None values pass through."""
        assert _json_safe(None) is None, "Condition must be true"

    def test_dict_conversion(self) -> None:
        """Test dict values are recursively converted."""
        input_dict = {"key": "value", "nested": {"a": 1}}
        result = _json_safe(input_dict)

        assert result == {"key": "value", "nested": {"a": 1}}

    def test_list_conversion(self) -> None:
        """Test list values are recursively converted."""
        input_list = ["a", 1, {"key": "value"}]
        result = _json_safe(input_list)

        assert result == ["a", 1, {"key": "value"}]

    def test_custom_object_to_string(self) -> None:
        """Test custom objects are converted to string."""

        class CustomClass:
            def __str__(self) -> str:
                return "custom_value"

        obj = CustomClass()
        result = _json_safe(obj)

        assert result == "custom_value", "Result must not be empty"

    def test_bytes_to_string(self) -> None:
        """Test bytes are converted to string."""
        result = _json_safe(b"hello")

        assert result == "b'hello'", "Result must not be empty"


class TestPrepareSessionPayload:
    """Tests for _prepare_session_payload function."""

    def test_simple_payload(self) -> None:
        """Test simple payload preparation."""
        data = {"key": "value", "number": 42}
        result = _prepare_session_payload(data)

        assert result == {"key": "value", "number": 42}

    def test_nested_payload(self) -> None:
        """Test nested payload preparation."""
        data = {"outer": {"inner": "value"}}
        result = _prepare_session_payload(data)

        assert result == {"outer": {"inner": "value"}}, "Result must not be empty"

    def test_non_string_keys(self) -> None:
        """Test non-string keys are converted."""
        data = {123: "value"}  # type: ignore
        result = _prepare_session_payload(data)

        assert "123" in result, "Result must not be empty"
        assert result["123"] == "value", "Result must not be empty"


class TestUtcIso:
    """Tests for _utc_iso function."""

    def test_returns_string(self) -> None:
        """Test that _utc_iso returns a string."""
        result = _utc_iso()
        assert isinstance(result, str)

    def test_ends_with_z(self) -> None:
        """Test that result ends with Z (UTC indicator)."""
        result = _utc_iso()
        assert result.endswith("Z"), "Result must not be empty"

    def test_with_timestamp(self) -> None:
        """Test with explicit timestamp."""
        # Known timestamp: 2024-01-15 12:00:00 UTC
        ts = 1705320000.0
        result = _utc_iso(ts)

        assert "2024-01-15" in result, "Result must not be empty"
        assert result.endswith("Z"), "Result must not be empty"

    def test_milliseconds_format(self) -> None:
        """Test that milliseconds are included."""
        result = _utc_iso()
        # Format: YYYY-MM-DDTHH:MM:SS.mmmZ
        parts = result.split(".")
        assert len(parts) == 2, "Parts must not be empty"
        assert parts[1].endswith("Z"), "Condition must be true"


class TestJsonFormatter:
    """Tests for JsonFormatter class."""

    def test_basic_formatting(self) -> None:
        """Test basic log record formatting."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        parsed = json.loads(result)

        assert parsed["message"] == "Test message", "Condition must be true"
        assert parsed["log.level"] == "INFO", "Condition must be true"
        assert parsed["log.logger"] == "test_logger", "Condition must be true"

    def test_includes_timestamp(self) -> None:
        """Test that timestamp is included."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        parsed = json.loads(result)

        assert "timestamp" in parsed, "Condition must be true"
        assert parsed["timestamp"].endswith("Z"), "Condition must be true"

    def test_includes_process_info(self) -> None:
        """Test that process info is included."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        parsed = json.loads(result)

        assert "process.pid" in parsed, "Condition must be true"
        assert "thread.name" in parsed, "Condition must be true"

    def test_dict_message(self) -> None:
        """Test formatting with dict message."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg={"custom_field": "custom_value"},
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        parsed = json.loads(result)

        assert "custom_field" in parsed, "Condition must be true"
        assert parsed["custom_field"] == "custom_value", "Value must be initialized"

    def test_exception_info(self) -> None:
        """Test formatting with exception info."""
        formatter = JsonFormatter()

        try:
            raise ValueError("Test error")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Error occurred",
            args=(),
            exc_info=exc_info,
        )

        result = formatter.format(record)
        parsed = json.loads(result)

        assert "error.kind" in parsed, "Error should be raised or set"
        assert "error.message" in parsed, "Error should be raised or set"
        assert "error.stack" in parsed, "Error should be raised or set"
        assert parsed["error.kind"] == "ValueError", "Value must be initialized"


class TestSessionId:
    """Tests for session ID management."""

    def test_get_session_id_generates(self) -> None:
        """Test that get_session_id generates an ID."""
        # Clear any cached session ID
        with patch.dict(os.environ, {}, clear=True):
            with patch("codex_ml.codex_structured_logging._session_id_ctx") as mock_ctx:
                mock_ctx.get.return_value = None
                mock_ctx.set = MagicMock()

                result = get_session_id()

                assert result is not None, "result must be initialized"
                assert len(result) > 0, "Result must not be empty"

    def test_set_session_id_returns_resolved(self) -> None:
        """Test that set_session_id returns resolved ID."""
        with patch("codex_ml.codex_structured_logging._session_id_ctx"):
            with patch("codex_ml.codex_structured_logging._session_logger_ctx"):
                with patch("codex_ml.codex_structured_logging.SessionLogger"):
                    result = set_session_id("test-session-id")

                    assert result == "test-session-id", "Result must not be empty"


class TestInitJsonLogging:
    """Tests for init_json_logging function."""

    def test_returns_logger(self) -> None:
        """Test that init_json_logging returns a logger."""
        with patch("codex_ml.codex_structured_logging.set_session_id"):
            result = init_json_logging()

            assert isinstance(result, logging.Logger)
            assert result.name == "codex", "Result must not be empty"

    def test_uses_env_level(self) -> None:
        """Test that log level is read from environment."""
        with patch.dict(os.environ, {"TEST_LOG_LEVEL": "DEBUG"}):
            with patch("codex_ml.codex_structured_logging.set_session_id"):
                result = init_json_logging(level_env="TEST_LOG_LEVEL")

                assert result is not None, "result must be initialized"


class TestEdgeCases:
    """Edge case tests."""

    def test_json_safe_with_tuple(self) -> None:
        """Test _json_safe with tuple."""
        result = _json_safe((1, 2, 3))
        assert result == [1, 2, 3]

    def test_json_safe_with_nested_complex(self) -> None:
        """Test _json_safe with deeply nested structure."""
        input_data = {"level1": {"level2": {"level3": ["a", "b", {"c": 1}]}}}
        result = _json_safe(input_data)

        assert result["level1"]["level2"]["level3"][2]["c"] == 1, "Result must not be empty"

    def test_formatter_unicode_handling(self) -> None:
        """Test formatter handles unicode correctly."""
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Unicode: 日本語 émojis 🎉",
            args=(),
            exc_info=None,
        )

        result = formatter.format(record)
        parsed = json.loads(result)

        assert "日本語" in parsed["message"], "Condition must be true"
        assert "🎉" in parsed["message"], "Condition must be true"

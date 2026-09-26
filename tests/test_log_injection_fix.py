"""
Comprehensive tests for log injection vulnerability remediation (CWE-117).

Tests cover:
- Sanitization of exception type names in logging
- Prevention of newline injection in log messages
- Prevention of control character injection
- ANSI escape code removal
- Proper parameterized logging
- Integration with existing logging infrastructure
"""

import logging
from io import StringIO
from unittest.mock import patch

import pytest
from codex.logging_safe import (
    SafeLogger,
    _sanitize_value,
    create_safe_json_log,
    create_safe_logger,
    sanitize_for_log,
)


class TestSanitizeValue:
    """Test core sanitization function."""

    def test_sanitize_newline_injection(self):
        """Newlines should be removed to prevent log forging."""
        malicious = "normal\nFAKE_LOG_ENTRY injected"
        result = _sanitize_value(malicious)
        assert "\n" not in result, "Result must not be empty"
        assert "normalFAKE_LOG_ENTRY" in result, "Result must not be empty"

    def test_sanitize_carriage_return(self):
        """Carriage returns should be removed."""
        malicious = "text\rmalicious\rcontent"
        result = _sanitize_value(malicious)
        assert "\r" not in result, "Result must not be empty"

    def test_sanitize_tab_characters(self):
        """Tab characters should be removed."""
        malicious = "text\twith\ttabs"
        result = _sanitize_value(malicious)
        assert "\t" not in result, "Result must not be empty"
        assert "textwith" in result, "Result must not be empty"

    def test_sanitize_null_bytes(self):
        """Null bytes should be removed."""
        malicious = "text\x00null\x00bytes"
        result = _sanitize_value(malicious)
        assert "\x00" not in result, "Result must not be empty"

    def test_sanitize_bell_character(self):
        """Bell character should be removed."""
        malicious = "text\x07bell\x07sound"
        result = _sanitize_value(malicious)
        assert "\x07" not in result, "Result must not be empty"

    def test_sanitize_ansi_escape_codes(self):
        """ANSI escape codes should be removed."""
        # Red text: \x1b[31m
        malicious = "\x1b[31mRED TEXT\x1b[0m"
        result = _sanitize_value(malicious)
        assert "\x1b" not in result, "Result must not be empty"
        assert "RED TEXT" in result, "Result must not be empty"

    def test_sanitize_multiple_escapes(self):
        """Multiple escape codes should be removed."""
        malicious = "\x1b[1;31mBOLD RED\x1b[0m normal"
        result = _sanitize_value(malicious)
        assert "\x1b" not in result, "Result must not be empty"
        assert "BOLD RED" in result, "Result must not be empty"

    def test_truncation(self):
        """Very long values should be truncated."""
        long_value = "a" * 2000
        result = _sanitize_value(long_value, max_length=500)
        assert len(result) <= 515, "Result must not be empty"
        assert "[truncated]" in result, "Result must not be empty"

    def test_none_value(self):
        """None should be converted to string 'None'."""
        result = _sanitize_value(None)
        assert result == "None", "Result must not be empty"

    def test_safe_content_unchanged(self):
        """Safe content should pass through unchanged."""
        safe = "normal log message 123"
        result = _sanitize_value(safe)
        assert result == safe, "Result must not be empty"

    def test_numeric_conversion(self):
        """Numbers should be converted to strings."""
        result = _sanitize_value(42)
        assert result == "42", "Result must not be empty"
        assert isinstance(result, str)

    def test_boolean_conversion(self):
        """Booleans should be converted to strings."""
        result = _sanitize_value(True)
        assert result == "True", "Result must not be empty"


class TestLogInjectionPrevention:
    """Test prevention of actual log injection attacks."""

    def test_fake_log_entry_injection(self):
        """Attacker cannot inject fake log entries with newlines."""
        malicious_user_input = 'admin\nINFO Fake entry: user=root authorized'
        result = _sanitize_value(malicious_user_input)

        # The newline should be removed (entries concatenated)
        assert "\n" not in result, "Result must not be empty"
        # After sanitization, the text should be concatenated without newline
        assert "adminINFO" in result, "Result must not be empty"

    def test_log_level_spoofing_attempt(self):
        """Attacker cannot spoof log levels."""
        malicious = "action\nERROR Critical system failure detected"
        result = _sanitize_value(malicious)
        # After sanitization, the text is concatenated
        assert "actionERROR" in result, "Result must not be empty"
        # But the newline that would create a new log entry is removed
        assert result.count("\n") == 0, "Result must not be empty"

    def test_control_character_DOS_prevention(self):
        """Control characters that could break log parsers are removed."""
        # Bell (ASCII 7) repeated could cause DoS on terminals
        malicious = "text\x07\x07\x07DoS"
        result = _sanitize_value(malicious)
        assert "\x07" not in result, "Result must not be empty"

    def test_color_code_bypass_attempt(self):
        """Color codes cannot be used to hide log entries."""
        # ANSI codes to create invisible text: \x1b[30;40m (black on black)
        malicious = "visible\x1b[30;40mhidden\x1b[0m"
        result = _sanitize_value(malicious)
        assert "\x1b" not in result, "Result must not be empty"
        # Should see both parts of the message
        assert "visible" in result, "Result must not be empty"
        assert "hidden" in result, "Result must not be empty"


class TestSafeLogger:
    """Test SafeLogger wrapper class."""

    def test_safe_logger_creation(self):
        """SafeLogger should wrap a standard logger."""
        base_logger = logging.getLogger("test")
        safe = SafeLogger(base_logger)
        assert safe._logger is base_logger, "_logger is not valid"

    def test_safe_logger_debug_sanitizes(self):
        """Debug messages should sanitize arguments."""
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        base_logger = logging.getLogger("test.debug")
        base_logger.addHandler(handler)
        base_logger.setLevel(logging.DEBUG)

        safe = SafeLogger(base_logger)
        safe.debug("Message: %s", "test\ninjection")

        output = stream.getvalue()
        assert "testinjection" in output, "Condition must be true"
        # Log handler adds a newline, so check that the injection newline is gone
        lines = output.split('\n')
        assert len(lines) <= 2, "Lines must not be empty"

    def test_safe_logger_info_sanitizes(self):
        """Info messages should sanitize arguments."""
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        base_logger = logging.getLogger("test.info")
        base_logger.addHandler(handler)
        base_logger.setLevel(logging.INFO)

        safe = SafeLogger(base_logger)
        safe.info("Message: %s", "safe\ninjected")

        output = stream.getvalue()
        assert "safeinjected" in output, "Condition must be true"

    def test_safe_logger_warning_sanitizes(self):
        """Warning messages should sanitize arguments."""
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        base_logger = logging.getLogger("test.warning")
        base_logger.addHandler(handler)
        base_logger.setLevel(logging.WARNING)

        safe = SafeLogger(base_logger)
        safe.warning("Warning: %s", "danger\nfake")

        output = stream.getvalue()
        assert "dangerfake" in output, "Condition must be true"

    def test_safe_logger_error_sanitizes(self):
        """Error messages should sanitize arguments."""
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        base_logger = logging.getLogger("test.error")
        base_logger.addHandler(handler)
        base_logger.setLevel(logging.ERROR)

        safe = SafeLogger(base_logger)
        safe.error("Error: %s", "fail\ninjected")

        output = stream.getvalue()
        assert "failinjected" in output, "Condition must be true"

    def test_safe_logger_preserves_numeric_args(self):
        """Numeric arguments should pass through unchanged."""
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        base_logger = logging.getLogger("test.numeric")
        base_logger.addHandler(handler)
        base_logger.setLevel(logging.INFO)

        safe = SafeLogger(base_logger)
        safe.info("Count: %d, Ratio: %f", 42, 3.14)

        output = stream.getvalue()
        assert "42" in output, "Condition must be true"
        assert "3.14" in output, "Condition must be true"

    def test_safe_logger_with_extra_fields(self):
        """Extra fields should be sanitized."""
        base_logger = logging.getLogger("test.extra")
        safe = SafeLogger(base_logger)

        # Create a mock to capture the extra fields
        with patch.object(base_logger, 'info') as mock_info:
            safe.info("Message", extra={"user": "test\nfake", "action": "login"})

            # Check that extra was passed and sanitized
            call_args = mock_info.call_args
            if call_args and 'extra' in call_args[1]:
                extra = call_args[1]['extra']
                assert "\n" not in extra.get("user", "")


class TestCreateSafeLogger:
    """Test create_safe_logger function."""

    def test_create_safe_logger(self):
        """Function should create a SafeLogger instance."""
        logger = create_safe_logger(__name__)
        assert isinstance(logger, SafeLogger)

    def test_create_safe_logger_names(self):
        """Logger names should be unique per module."""
        logger1 = create_safe_logger("module1")
        logger2 = create_safe_logger("module2")

        assert logger1._logger.name == "module1", "name is not valid"
        assert logger2._logger.name == "module2", "name is not valid"


class TestSanitizeForLog:
    """Test the sanitize_for_log convenience function."""

    def test_sanitize_for_log(self):
        """Function should sanitize values for logging."""
        result = sanitize_for_log("text\ninjection")
        assert "\n" not in result, "Result must not be empty"
        assert "textinjection" in result, "Result must not be empty"

    def test_sanitize_for_log_with_exception_type(self):
        """Should handle exception type names safely."""
        try:
            raise ValueError("test error")
        except Exception as e:
            result = sanitize_for_log(type(e).__name__)
            assert result == "ValueError", "Result must not be empty"
            assert "\n" not in result, "Result must not be empty"


class TestCreateSafeJsonLog:
    """Test JSON log creation."""

    def test_create_safe_json_log_simple(self):
        """Should create valid JSON with sanitized content."""
        result = create_safe_json_log("User login", user="admin\nfake")
        assert '"message": "User login"' in result, "Result must not be empty"
        assert "adminfake" in result, "Result must not be empty"

    def test_create_safe_json_log_multiple_fields(self):
        """Should handle multiple fields."""
        result = create_safe_json_log(
            "Action",
            user="alice\nfalse",
            action="login\nEVERYONE",
            timestamp="2026-07-08T00:00:00Z"
        )

        # Verify it's valid JSON
        import json
        parsed = json.loads(result)
        assert parsed["message"] == "Action", "Condition must be true"
        assert "alicefalse" in parsed["user"], "Condition must be true"
        assert "loginEVERYONE" in parsed["action"], "Condition must be true"

        # No injected newlines
        for key, value in parsed.items():
            if isinstance(value, str):
                assert "\n" not in value, "Value must be initialized"


class TestRealWorldScenarios:
    """Test real-world log injection scenarios."""

    def test_exception_type_logging(self):
        """Logging exception types should be safe."""
        try:
            raise RuntimeError("Something failed")
        except Exception as e:
            result = _sanitize_value(type(e).__name__)
            assert result == "RuntimeError", "Result must not be empty"

    def test_http_header_injection(self):
        """HTTP headers in logs should not contain injection."""
        # Attacker might send: User-Agent: Mozilla\nBCC: attacker@evil.com
        malicious_header = "Mozilla\nBCC: attacker@evil.com"
        result = _sanitize_value(malicious_header)
        assert "\n" not in result, "Result must not be empty"
        # The text is concatenated without the newline
        assert "MozillaBCC" in result, "Result must not be empty"

    def test_sql_error_message_injection(self):
        """SQL error messages should not allow injection."""
        # Database error with newline: "Syntax error\nDROP TABLE users"
        error_msg = "Syntax error\nDROP TABLE users;"
        result = _sanitize_value(error_msg)
        assert "\n" not in result, "Result must not be empty"
        # The text is concatenated without the newline
        assert "Syntax errorDROP" in result, "Result must not be empty"

    def test_user_input_in_log(self):
        """User-provided input in logs should be sanitized."""
        user_input = "normal text"
        result = _sanitize_value(user_input)
        assert result == user_input, "Result must not be empty"

        malicious_input = "normal\x1b[31mred\nfake\x07bell"
        result = _sanitize_value(malicious_input)
        assert "\n" not in result, "Result must not be empty"
        assert "\x1b" not in result, "Result must not be empty"
        assert "\x07" not in result, "Result must not be empty"


class TestBackwardCompatibility:
    """Test compatibility with existing logging patterns."""

    def test_safe_logger_proxies_attributes(self):
        """SafeLogger should proxy other attributes to base logger."""
        base_logger = logging.getLogger("test.proxy")
        safe = SafeLogger(base_logger)

        # Should be able to access logger properties
        assert safe.level == base_logger.level, "level is not valid"
        assert safe.name == base_logger.name, "name is not valid"

    def test_safe_logger_with_handlers(self):
        """SafeLogger should work with multiple handlers."""
        stream1 = StringIO()
        stream2 = StringIO()

        base_logger = logging.getLogger("test.handlers")
        handler1 = logging.StreamHandler(stream1)
        handler2 = logging.StreamHandler(stream2)
        base_logger.addHandler(handler1)
        base_logger.addHandler(handler2)
        base_logger.setLevel(logging.INFO)

        safe = SafeLogger(base_logger)
        safe.info("Message: %s", "test\ninjection")

        # Both handlers should receive the sanitized message
        assert "testinjection" in stream1.getvalue(), "Value must be initialized"
        assert "testinjection" in stream2.getvalue(), "Value must be initialized"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

"""
Tests for codex.archive.config module.

This module contains tests for configuration helpers.
"""


class TestCoerceBool:
    """Tests for _coerce_bool function."""

    def test_bool_input(self):
        """Test _coerce_bool with bool input."""
        from codex.archive.config import _coerce_bool

        assert _coerce_bool(True) is True, "Condition must be true"
        assert _coerce_bool(False) is False, "Condition must be true"

    def test_none_input(self):
        """Test _coerce_bool with None input."""
        from codex.archive.config import _coerce_bool

        assert _coerce_bool(None) is False, "Condition must be true"
        assert _coerce_bool(None, default=True) is True

    def test_int_input(self):
        """Test _coerce_bool with int input."""
        from codex.archive.config import _coerce_bool

        assert _coerce_bool(1) is True, "Condition must be true"
        assert _coerce_bool(0) is False, "Condition must be true"
        assert _coerce_bool(42) is True, "Condition must be true"

    def test_string_true_values(self):
        """Test _coerce_bool with true string values."""
        from codex.archive.config import _coerce_bool

        for val in ["1", "true", "TRUE", "yes", "YES", "on", "ON", "enabled"]:
            assert _coerce_bool(val) is True, f"Expected True for '{val}'"

    def test_string_false_values(self):
        """Test _coerce_bool with false string values."""
        from codex.archive.config import _coerce_bool

        for val in ["0", "false", "FALSE", "no", "NO", "off", "OFF", "disabled"]:
            assert _coerce_bool(val) is False, f"Expected False for '{val}'"

    def test_string_unknown(self):
        """Test _coerce_bool with unknown string returns default."""
        from codex.archive.config import _coerce_bool

        assert _coerce_bool("unknown") is False, "Condition must be true"
        assert _coerce_bool("unknown", default=True) is True


class TestCoerceInt:
    """Tests for _coerce_int function."""

    def test_int_input(self):
        """Test _coerce_int with int input."""
        from codex.archive.config import _coerce_int

        assert _coerce_int(42, default=0) == 42
        assert _coerce_int(-10, default=0) == -10

    def test_bool_input(self):
        """Test _coerce_int with bool input."""
        from codex.archive.config import _coerce_int

        assert _coerce_int(True, default=0) == 1
        assert _coerce_int(False, default=0) == 0

    def test_string_input(self):
        """Test _coerce_int with string input."""
        from codex.archive.config import _coerce_int

        assert _coerce_int("42", default=0) == 42
        assert _coerce_int(" 100 ", default=0) == 100

    def test_string_invalid(self):
        """Test _coerce_int with invalid string returns default."""
        from codex.archive.config import _coerce_int

        assert _coerce_int("not_a_number", default=99) == 99

    def test_other_type(self):
        """Test _coerce_int with other types returns default."""
        from codex.archive.config import _coerce_int

        assert _coerce_int([1, 2, 3], default=50) == 50
        assert _coerce_int(None, default=25) == 25


class TestCoerceFloat:
    """Tests for _coerce_float function."""

    def test_float_input(self):
        """Test _coerce_float with float input."""
        from codex.archive.config import _coerce_float

        assert _coerce_float(3.14, default=0.0) == 3.14

    def test_int_input(self):
        """Test _coerce_float with int input."""
        from codex.archive.config import _coerce_float

        assert _coerce_float(42, default=0.0) == 42.0

    def test_string_input(self):
        """Test _coerce_float with string input."""
        from codex.archive.config import _coerce_float

        assert _coerce_float("3.14", default=0.0) == 3.14
        assert _coerce_float(" 2.5 ", default=0.0) == 2.5

    def test_string_invalid(self):
        """Test _coerce_float with invalid string returns default."""
        from codex.archive.config import _coerce_float

        assert _coerce_float("not_a_float", default=1.5) == 1.5


class TestModuleConstants:
    """Tests for module-level constants."""

    def test_env_bool_true(self):
        """Test _ENV_BOOL_TRUE constant."""
        from codex.archive.config import _ENV_BOOL_TRUE

        assert "1" in _ENV_BOOL_TRUE, "Condition must be true"
        assert "true" in _ENV_BOOL_TRUE, "Condition must be true"
        assert "yes" in _ENV_BOOL_TRUE, "Condition must be true"

    def test_env_bool_false(self):
        """Test _ENV_BOOL_FALSE constant."""
        from codex.archive.config import _ENV_BOOL_FALSE

        assert "0" in _ENV_BOOL_FALSE, "Condition must be true"
        assert "false" in _ENV_BOOL_FALSE, "Condition must be true"
        assert "no" in _ENV_BOOL_FALSE, "Condition must be true"

    def test_supported_backends(self):
        """Test _SUPPORTED_BACKENDS constant."""
        from codex.archive.config import _SUPPORTED_BACKENDS

        assert "sqlite" in _SUPPORTED_BACKENDS, "Condition must be true"
        assert "postgres" in _SUPPORTED_BACKENDS, "Condition must be true"

    def test_logger_exists(self):
        """Test logger is configured."""
        from codex.archive.config import logger

        assert logger is not None, "logger must be initialized"
        assert logger.name == "codex.archive.config", "name is not valid"

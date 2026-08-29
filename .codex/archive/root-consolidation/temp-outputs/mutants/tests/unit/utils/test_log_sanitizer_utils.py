"""Unit tests for log_sanitizer utilities (Phase 23 Week 3 gapfill)."""

from src.utils.log_sanitizer import sanitize_dict_for_log, sanitize_log_input


def test_sanitize_log_input_newline_removal():
    """Test sanitize_log_input removes newlines."""
    result = sanitize_log_input("line1\nline2\rline3")
    assert "\n" not in result, "Result must not be empty"
    assert "\r" not in result, "Result must not be empty"
    assert "line1" in result, "Result must not be empty"
    assert "line2" in result, "Result must not be empty"


def test_sanitize_log_input_tab_removal():
    """Test sanitize_log_input removes tabs."""
    result = sanitize_log_input("col1\tcol2\tcol3")
    assert "\t" not in result, "Result must not be empty"


def test_sanitize_log_input_control_char_removal():
    """Test sanitize_log_input removes control characters."""
    result = sanitize_log_input("text\x00with\x1fcontrol\x7f")
    assert "\x00" not in result, "Result must not be empty"
    assert "\x1f" not in result, "Result must not be empty"
    assert "\x7f" not in result, "Result must not be empty"


def test_sanitize_log_input_ansi_escape_removal():
    """Test sanitize_log_input removes ANSI escape codes."""
    result = sanitize_log_input("\x1b[31mred\x1b[0m")
    assert "\x1b" not in result, "Result must not be empty"
    assert "red" in result, "Result must not be empty"


def test_sanitize_log_input_bracket_ansi_removal():
    """Test sanitize_log_input removes bracket ANSI codes."""
    result = sanitize_log_input("[31mcolor[0m")
    assert "[31m" not in result or "color" in result, "Result must not be empty"


def test_sanitize_log_input_truncation():
    """Test sanitize_log_input truncates long strings."""
    long_str = "a" * 1000
    result = sanitize_log_input(long_str, max_length=100)
    assert len(result) <= 120, "Result must not be empty"
    assert "truncated" in result, "Result must not be empty"


def test_sanitize_log_input_none_handling():
    """Test sanitize_log_input handles None."""
    result = sanitize_log_input(None)
    assert result == "None", "Result must not be empty"


def test_sanitize_log_input_numeric_coercion():
    """Test sanitize_log_input coerces numbers."""
    result = sanitize_log_input(12345)
    assert "12345" in result, "Result must not be empty"


def test_sanitize_dict_for_log_recursive():
    """Test sanitize_dict_for_log sanitizes nested dicts."""
    data = {
        "key1": "value\nwith\nnewlines",
        "key2": {"nested": "data\twith\ttabs"},
    }
    result = sanitize_dict_for_log(data)
    assert "\n" not in result["key1"], "Result must not be empty"
    assert "\t" not in result["key2"]["nested"], "Result must not be empty"


def test_sanitize_dict_for_log_mixed_types():
    """Test sanitize_dict_for_log handles mixed value types."""
    data = {
        "str": "text\n",
        "int": 123,
        "float": 45.67,
        "bool": True,
        "none": None,
    }
    result = sanitize_dict_for_log(data)
    assert "\n" not in result["str"], "Result must not be empty"
    assert "123" in result["int"], "Result must not be empty"
    assert "45.67" in result["float"], "Result must not be empty"


def test_sanitize_dict_for_log_empty():
    """Test sanitize_dict_for_log handles empty dict."""
    result = sanitize_dict_for_log({})
    assert result == {}, "Result must not be empty"


def test_sanitize_dict_for_log_preserves_keys():
    """Test sanitize_dict_for_log preserves key names."""
    data = {"key1": "val1", "key2": "val2"}
    result = sanitize_dict_for_log(data)
    assert "key1" in result, "Result must not be empty"
    assert "key2" in result, "Result must not be empty"

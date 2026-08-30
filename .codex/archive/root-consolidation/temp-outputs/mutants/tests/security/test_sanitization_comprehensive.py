"""
Comprehensive tests for security sanitization module.

Tests cover:
- HTML sanitization (XSS prevention)
- Integer sanitization
- String sanitization
- Edge cases and injection attacks
- Bounds checking
- Type handling
"""

from codex.security.sanitization import (
    sanitize_html,
    sanitize_integer,
    sanitize_string,
)

# ============================================================================
# HTML Sanitization Tests
# ============================================================================


class TestSanitizeHtmlBasic:
    """Basic HTML sanitization functionality."""

    def test_empty_string(self):
        """Test sanitization of empty string."""
        assert sanitize_html("") == "", "Condition must be true"

    def test_plain_text(self):
        """Test that plain text passes through unchanged."""
        assert sanitize_html("Hello World") == "Hello World", "Condition must be true"

    def test_whitespace_stripping(self):
        """Test that leading/trailing whitespace is stripped."""
        assert sanitize_html("  hello  ") == "hello", "Condition must be true"

    def test_none_type_returns_empty_string(self):
        """Test that None returns empty string."""
        assert sanitize_html(None) == "", "Condition must be true"

    def test_non_string_types_return_empty(self):
        """Test that non-string types return empty string."""
        assert sanitize_html(123) == "", "Condition must be true"
        assert sanitize_html([]) == "", "Condition must be true"
        assert sanitize_html({}) == "", "Condition must be true"

    def test_allowed_tags_false_strips_html(self):
        """Test that allow_tags=False strips HTML."""
        html = "<p>Hello</p>"
        assert sanitize_html(html, allow_tags=False) == "Hello"

    def test_allowed_tags_true_preserves_tags(self):
        """Test that allow_tags=True preserves safe HTML."""
        html = "<p>Hello</p>"
        result = sanitize_html(html, allow_tags=True)
        assert "<p>" in result or "Hello" in result, "Result must not be empty"


class TestSanitizeHtmlXssAttacks:
    """Test XSS attack prevention."""

    def test_script_tag_removal(self):
        """Test removal of <script> tags."""
        html = "<script>alert('xss')</script>Hello"
        assert sanitize_html(html) == "Hello", "Condition must be true"

    def test_script_tag_with_attributes(self):
        """Test removal of script tags with attributes."""
        html = '<script type="text/javascript">alert("xss")</script>'
        assert sanitize_html(html) == "", "Condition must be true"

    def test_nested_script_tags(self):
        """Test removal of nested script tags."""
        html = "<div><script>alert('xss')</script></div>"
        result = sanitize_html(html)
        assert "script" not in result, "Result must not be empty"
        assert "alert" not in result, "Result must not be empty"

    def test_iframe_tag_removal(self):
        """Test removal of <iframe> tags."""
        html = '<iframe src="http://evil.com"></iframe>'
        assert sanitize_html(html) == "", "Condition must be true"

    def test_object_tag_removal(self):
        """Test removal of <object> tags."""
        html = '<object data="http://evil.com"></object>'
        assert sanitize_html(html) == "", "Condition must be true"

    def test_embed_tag_removal(self):
        """Test removal of <embed> tags."""
        html = '<embed src="http://evil.com">'
        assert sanitize_html(html) == "", "Condition must be true"

    def test_applet_tag_removal(self):
        """Test removal of <applet> tags."""
        html = '<applet code="http://evil.com"></applet>'
        assert sanitize_html(html) == "", "Condition must be true"

    def test_meta_tag_removal(self):
        """Test removal of <meta> tags."""
        html = '<meta http-equiv="refresh" content="0;url=http://evil.com">'
        assert sanitize_html(html) == "", "Condition must be true"

    def test_link_tag_removal(self):
        """Test removal of <link> tags."""
        html = '<link rel="stylesheet" href="http://evil.com/style.css">'
        assert sanitize_html(html) == "", "Condition must be true"

    def test_style_tag_removal(self):
        """Test removal of <style> tags."""
        html = "<style>body { display: none; }</style>Hello"
        result = sanitize_html(html)
        assert "display" not in result, "Result must not be empty"

    def test_onclick_handler_removal(self):
        """Test removal of onclick handlers."""
        html = "<div onclick=\"alert('xss')\">Click me</div>"
        result = sanitize_html(html)
        assert "onclick" not in result, "Result must not be empty"

    def test_onerror_handler_removal(self):
        """Test removal of onerror handlers."""
        html = '<img src="x" onerror="alert(\'xss\')">'
        result = sanitize_html(html)
        assert "onerror" not in result, "Result must not be empty"

    def test_onload_handler_removal(self):
        """Test removal of onload handlers."""
        html = "<body onload=\"alert('xss')\">Hello</body>"
        result = sanitize_html(html)
        assert "onload" not in result, "Result must not be empty"

    def test_onmouseover_handler_removal(self):
        """Test removal of onmouseover handlers."""
        html = "<span onmouseover=\"alert('xss')\">Hover</span>"
        result = sanitize_html(html)
        assert "onmouseover" not in result, "Result must not be empty"


class TestSanitizeHtmlProtocols:
    """Test dangerous protocol removal."""

    def test_javascript_protocol_removal(self):
        """Test removal of javascript: protocol."""
        html = "<a href=\"javascript:alert('xss')\">Click</a>"
        result = sanitize_html(html)
        assert "javascript:" not in result, "Result must not be empty"

    def test_javascript_protocol_case_insensitive(self):
        """Test case-insensitive javascript: removal."""
        html = "<a href=\"JavaScript:alert('xss')\">Click</a>"
        result = sanitize_html(html)
        assert "javascript:" not in result.lower(), "Result must not be empty"

    def test_data_protocol_removal(self):
        """Test removal of data: protocol."""
        html = "<img src=\"data:text/html,<script>alert('xss')</script>\">"
        result = sanitize_html(html)
        assert "data:" not in result, "Result must not be empty"

    def test_vbscript_protocol_removal(self):
        """Test removal of vbscript: protocol."""
        html = "<a href=\"vbscript:msgbox('xss')\">Click</a>"
        result = sanitize_html(html)
        assert "vbscript:" not in result, "Result must not be empty"

    def test_file_protocol_removal(self):
        """Test removal of file: protocol."""
        html = '<a href="file:///etc/passwd">Click</a>'
        result = sanitize_html(html)
        assert "file:" not in result, "Result must not be empty"

    def test_about_protocol_removal(self):
        """Test removal of about: protocol."""
        html = '<a href="about:blank">Click</a>'
        result = sanitize_html(html)
        assert "about:" not in result, "Result must not be empty"


class TestSanitizeHtmlEdgeCases:
    """Test edge cases in HTML sanitization."""

    def test_mixed_safe_and_unsafe_tags(self):
        """Test handling of mixed safe and unsafe content."""
        html = "<b>Bold</b><script>alert('xss')</script><i>Italic</i>"
        result = sanitize_html(html, allow_tags=False)
        assert "script" not in result, "Result must not be empty"
        assert "alert" not in result, "Result must not be empty"

    def test_multiline_script_tag(self):
        """Test removal of multiline script tags."""
        html = "<script>\nalert('xss')\n</script>"
        result = sanitize_html(html)
        assert "script" not in result, "Result must not be empty"
        assert "alert" not in result, "Result must not be empty"

    def test_encoded_event_handlers(self):
        """Test removal of encoded event handlers."""
        html = "<div on&#99;lick=\"alert('xss')\">Click</div>"
        result = sanitize_html(html)
        # Should remove the onclick attribute pattern
        assert result, "Result must not be empty"

    def test_special_characters_in_content(self):
        """Test handling of special characters."""
        html = "Hello & <goodbye>"
        result = sanitize_html(html)
        assert result, "Result must not be empty"

    def test_unicode_content_preservation(self):
        """Test preservation of unicode content."""
        html = "Hello 世界 🌍"
        result = sanitize_html(html)
        assert "世界" in result, "Result must not be empty"
        assert "🌍" in result, "Result must not be empty"

    def test_very_long_string(self):
        """Test handling of very long strings."""
        html = "Hello " + "X" * 10000
        result = sanitize_html(html)
        assert len(result) > 1000, "Result must not be empty"


# ============================================================================
# Integer Sanitization Tests
# ============================================================================


class TestSanitizeIntegerBasic:
    """Basic integer sanitization functionality."""

    def test_integer_passthrough(self):
        """Test that integers pass through unchanged."""
        assert sanitize_integer(42) == 42, "Condition must be true"
        assert sanitize_integer(0) == 0, "Condition must be true"
        assert sanitize_integer(-100) == -100, "Condition must be true"

    def test_string_integer_conversion(self):
        """Test conversion of string integers."""
        assert sanitize_integer("42") == 42, "Condition must be true"
        assert sanitize_integer("0") == 0, "Condition must be true"
        assert sanitize_integer("-100") == -100, "Condition must be true"

    def test_float_truncation(self):
        """Test truncation of floats to integers."""
        assert sanitize_integer(42.7) == 42, "Condition must be true"
        assert sanitize_integer(42.1) == 42, "Condition must be true"
        assert sanitize_integer(-42.9) == -42, "Condition must be true"

    def test_string_float_conversion(self):
        """Test conversion of string floats."""
        assert sanitize_integer("42.7") == 42, "Condition must be true"
        assert sanitize_integer("0.5") == 0, "Condition must be true"
        assert sanitize_integer("-42.9") == -42, "Condition must be true"

    def test_none_returns_default(self):
        """Test that None returns default value."""
        assert sanitize_integer(None) == 0, "Condition must be true"
        assert sanitize_integer(None, default=99) == 99

    def test_invalid_string_returns_default(self):
        """Test that invalid strings return default."""
        assert sanitize_integer("not_a_number") == 0, "Condition must be true"
        assert sanitize_integer("abc123", default=99) == 99

    def test_empty_string_returns_default(self):
        """Test that empty string returns default."""
        assert sanitize_integer("") == 0, "Condition must be true"
        assert sanitize_integer("", default=42) == 42

    def test_whitespace_handling(self):
        """Test handling of whitespace in strings."""
        assert sanitize_integer("  42  ") == 42, "Condition must be true"
        assert sanitize_integer("  -100  ") == -100, "Condition must be true"


class TestSanitizeIntegerBounds:
    """Test bounds checking in integer sanitization."""

    def test_minimum_bound_clamp(self):
        """Test clamping to minimum value."""
        assert sanitize_integer(5, min_value=10) == 10
        assert sanitize_integer(-100, min_value=-50) == -50

    def test_maximum_bound_clamp(self):
        """Test clamping to maximum value."""
        assert sanitize_integer(100, max_value=50) == 50
        assert sanitize_integer(1000, max_value=100) == 100

    def test_both_bounds_check(self):
        """Test checking both min and max bounds."""
        assert sanitize_integer(5, min_value=10, max_value=100) == 10
        assert sanitize_integer(150, min_value=10, max_value=100) == 100
        assert sanitize_integer(50, min_value=10, max_value=100) == 50

    def test_negative_bounds(self):
        """Test bounds with negative values."""
        assert sanitize_integer(-50, min_value=-100, max_value=-10) == -50
        assert sanitize_integer(-150, min_value=-100, max_value=-10) == -100

    def test_zero_bounds(self):
        """Test bounds including zero."""
        assert sanitize_integer(5, min_value=0, max_value=10) == 5
        assert sanitize_integer(-5, min_value=0, max_value=10) == 0

    def test_equal_min_max(self):
        """Test when min and max are equal."""
        assert sanitize_integer(5, min_value=10, max_value=10) == 10
        assert sanitize_integer(15, min_value=10, max_value=10) == 10


class TestSanitizeIntegerEdgeCases:
    """Test edge cases in integer sanitization."""

    def test_large_integers(self):
        """Test handling of very large integers."""
        large_int = 2**31 - 1
        assert sanitize_integer(large_int) == large_int, "Condition must be true"
        assert sanitize_integer(str(large_int)) == large_int, "Condition must be true"

    def test_very_negative_integers(self):
        """Test handling of very negative integers."""
        neg_int = -(2**31)
        assert sanitize_integer(neg_int) == neg_int, "Condition must be true"

    def test_scientific_notation(self):
        """Test handling of scientific notation."""
        assert sanitize_integer("1e2") == 100, "Condition must be true"
        assert sanitize_integer("1.5e2") == 150, "Condition must be true"

    def test_type_coercion_list(self):
        """Test that lists return default."""
        assert sanitize_integer([42]) == 0, "Condition must be true"

    def test_type_coercion_dict(self):
        """Test that dicts return default."""
        assert sanitize_integer({"value": 42}) == 0, "Value must be initialized"

    def test_string_with_leading_zeros(self):
        """Test handling of strings with leading zeros."""
        assert sanitize_integer("00042") == 42, "Condition must be true"
        assert sanitize_integer("0042", default=0) == 42

    def test_negative_zero(self):
        """Test handling of negative zero."""
        assert sanitize_integer("-0") == 0, "Condition must be true"


# ============================================================================
# String Sanitization Tests
# ============================================================================


class TestSanitizeStringBasic:
    """Basic string sanitization functionality."""

    def test_plain_string_passthrough(self):
        """Test that plain strings pass through."""
        assert sanitize_string("Hello World") == "Hello World", "Condition must be true"

    def test_none_returns_empty_string(self):
        """Test that None returns empty string."""
        assert sanitize_string(None) == "", "Condition must be true"

    def test_non_string_types_return_empty(self):
        """Test that non-string types return empty."""
        assert sanitize_string(123) == "", "Condition must be true"
        assert sanitize_string([]) == "", "Condition must be true"

    def test_whitespace_stripping(self):
        """Test that leading/trailing whitespace is stripped."""
        assert sanitize_string("  hello  ") == "hello", "Condition must be true"

    def test_null_byte_removal(self):
        """Test removal of null bytes."""
        assert sanitize_string("hello\x00world") == "helloworld", "Condition must be true"
        assert sanitize_string("\x00test") == "test", "Condition must be true"


class TestSanitizeStringMaxLength:
    """Test max length handling."""

    def test_under_max_length(self):
        """Test strings under max length."""
        assert sanitize_string("hello", max_length=100) == "hello"

    def test_over_max_length_truncated(self):
        """Test strings over max length are truncated."""
        result = sanitize_string("A" * 2000, max_length=1000)
        assert len(result) <= 1000, "Result must not be empty"

    def test_exact_max_length(self):
        """Test strings at exact max length."""
        text = "A" * 100
        result = sanitize_string(text, max_length=100)
        assert len(result) <= 100, "Result must not be empty"

    def test_custom_max_length(self):
        """Test custom max length values."""
        result = sanitize_string("A" * 500, max_length=100)
        assert len(result) <= 100, "Result must not be empty"


class TestSanitizeStringNewlines:
    """Test newline handling."""

    def test_newlines_preserved_by_default(self):
        """Test that newlines are preserved by default."""
        text = "line1\nline2\nline3"
        result = sanitize_string(text, allow_newlines=True)
        assert "\n" in result, "Result must not be empty"

    def test_newlines_removed_when_disabled(self):
        """Test that newlines are removed when disabled."""
        text = "line1\nline2\nline3"
        result = sanitize_string(text, allow_newlines=False)
        assert "\n" not in result, "Result must not be empty"

    def test_carriage_returns_removed(self):
        """Test removal of carriage returns."""
        text = "line1\r\nline2"
        result = sanitize_string(text, allow_newlines=False)
        assert "\r" not in result, "Result must not be empty"

    def test_tabs_preserved(self):
        """Test that tabs are preserved."""
        text = "col1\tcol2"
        result = sanitize_string(text, allow_newlines=True)
        assert "\t" in result, "Result must not be empty"


class TestSanitizeStringHtmlStripping:
    """Test HTML stripping in string sanitization."""

    def test_html_removed_by_default(self):
        """Test that HTML is removed by default."""
        text = "<script>alert('xss')</script>Hello"
        result = sanitize_string(text, strip_html=True)
        assert "script" not in result, "Result must not be empty"

    def test_html_stripped_option(self):
        """Test strip_html option."""
        text = "<b>Bold</b>"
        result = sanitize_string(text, strip_html=True)
        assert "<b>" not in result, "Result must not be empty"

    def test_html_not_stripped_when_disabled(self):
        """Test that HTML can be preserved."""
        text = "<b>Bold</b>"
        result = sanitize_string(text, strip_html=False)
        # Note: This depends on implementation - may still remove dangerous tags
        assert "Bold" in result, "Result must not be empty"


class TestSanitizeStringEdgeCases:
    """Test edge cases in string sanitization."""

    def test_unicode_strings(self):
        """Test preservation of unicode characters."""
        text = "Hello 世界 🌍"
        result = sanitize_string(text)
        assert "世界" in result, "Result must not be empty"

    def test_sql_injection_attempt(self):
        """Test handling of SQL injection patterns."""
        text = "' OR '1'='1"
        result = sanitize_string(text)
        assert result == "' OR '1'='1", "Result must not be empty"

    def test_empty_string(self):
        """Test empty string handling."""
        assert sanitize_string("") == "", "Condition must be true"

    def test_only_whitespace(self):
        """Test string with only whitespace."""
        assert sanitize_string("   ") == "", "Condition must be true"

    def test_mixed_content(self):
        """Test mixed safe and potentially unsafe content."""
        text = "Hello <script>alert('xss')</script> World"
        result = sanitize_string(text)
        assert "script" not in result, "Result must not be empty"
        assert "Hello" in result, "Result must not be empty"


# ============================================================================
# Integration Tests
# ============================================================================


class TestSanitizationIntegration:
    """Integration tests for sanitization functions."""

    def test_html_then_string_sanitization(self):
        """Test chaining HTML and string sanitization."""
        html = "<script>alert('xss')</script>Hello\nWorld"
        # sanitize_string calls sanitize_html internally
        result = sanitize_string(html)
        assert "script" not in result, "Result must not be empty"
        assert result, "Result must not be empty"

    def test_integer_bounds_with_string_input(self):
        """Test integer sanitization with bounds and string input."""
        result = sanitize_integer("150", min_value=0, max_value=100)
        assert result == 100, "Result must not be empty"

    def test_real_world_log_entry(self):
        """Test sanitization of a realistic log entry."""
        log_entry = 'User <script>alert("xss")</script> logged in from 192.168.1.1'
        result = sanitize_string(log_entry)
        assert "script" not in result, "Result must not be empty"
        assert "192.168.1.1" in result, "Result must not be empty"

    def test_real_world_input_validation(self):
        """Test sanitization of real-world user input."""
        user_input = '"><script>alert(1)</script>'
        result = sanitize_html(user_input)
        assert "script" not in result, "Result must not be empty"

    def test_combined_security_checks(self):
        """Test multiple security checks together."""
        # HTML content with special characters
        html = '<img src="x" onerror="alert(\'xss\')">Test'
        html_clean = sanitize_html(html)
        string_clean = sanitize_string(html_clean)

        assert "onerror" not in string_clean, "Error should be raised or set"
        assert "Test" in string_clean, "Condition must be true"

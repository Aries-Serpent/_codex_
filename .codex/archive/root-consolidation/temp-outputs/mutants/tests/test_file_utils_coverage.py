"""
Comprehensive tests for codex.file_utils module.

Tests cover safe file reading utilities with proper error handling and logging.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from codex.file_utils import (
    migrate_from_ignore,
    read_text_safe,
    read_text_safe_fallback,
)


class TestReadTextSafe:
    """Test read_text_safe function."""

    def test_read_text_safe_basic_utf8(self):
        """Test reading basic UTF-8 file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            content = "Hello, World!"
            path.write_text(content, encoding="utf-8")

            result = read_text_safe(path)
            assert result == content, "Result must not be empty"

    def test_read_text_safe_empty_file(self):
        """Test reading empty file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "empty.txt"
            path.write_text("", encoding="utf-8")

            result = read_text_safe(path)
            assert result == "", "Result must not be empty"

    def test_read_text_safe_unicode_content(self):
        """Test reading file with unicode content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "unicode.txt"
            content = "Hello 世界 🌍 مرحبا"
            path.write_text(content, encoding="utf-8")

            result = read_text_safe(path)
            assert result == content, "Result must not be empty"

    def test_read_text_safe_multiline(self):
        """Test reading multiline file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "multiline.txt"
            lines = ["Line 1", "Line 2", "Line 3"]
            content = "\n".join(lines)
            path.write_text(content, encoding="utf-8")

            result = read_text_safe(path)
            assert result == content, "Result must not be empty"

    def test_read_text_safe_different_encoding(self):
        """Test reading file with different encoding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "latin1.txt"
            content = "Café"
            path.write_text(content, encoding="latin-1")

            result = read_text_safe(path, encoding="latin-1")
            assert result == content, "Result must not be empty"

    def test_read_text_safe_max_bytes_limit(self):
        """Test reading with max_bytes limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "large.txt"
            content = "0123456789" * 10  # 100 bytes
            path.write_text(content, encoding="utf-8")

            result = read_text_safe(path, max_bytes=20)
            assert len(result) <= 20, "Result must not be empty"
            assert result.startswith("01234567"), "Result must not be empty"

    def test_read_text_safe_max_bytes_partial_char(self):
        """Test max_bytes with partial character."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            content = "Hello"
            path.write_text(content, encoding="utf-8")

            result = read_text_safe(path, max_bytes=3)
            assert len(result) == 3, "Result must not be empty"

    def test_read_text_safe_file_not_found(self):
        """Test error when file doesn't exist."""
        nonexistent = Path("/nonexistent/file.txt")
        with pytest.raises(FileNotFoundError):
            read_text_safe(nonexistent)

    def test_read_text_safe_permission_error(self):
        """Test error on permission denied."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            path.write_text("content")

            with patch("pathlib.Path.read_text", side_effect=PermissionError):
                with pytest.raises(PermissionError):
                    read_text_safe(path)

    def test_read_text_safe_unicode_decode_error_strict(self):
        """Test UnicodeDecodeError with errors='strict'."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "binary.bin"
            # Write invalid UTF-8 sequence
            path.write_bytes(b"\xff\xfe")

            with pytest.raises(UnicodeDecodeError):
                read_text_safe(path, errors="strict")

    def test_read_text_safe_unicode_decode_error_replace(self):
        """Test UnicodeDecodeError with errors='replace'."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "binary.bin"
            # Write invalid UTF-8 sequence
            path.write_bytes(b"Valid\xff\xfetext")

            result = read_text_safe(path, errors="replace")
            # Should contain replacement character
            assert "Valid" in result, "Result must not be empty"
            assert "text" in result, "Result must not be empty"

    @patch("codex.file_utils.logger")
    def test_read_text_safe_logs_replacement_character(self, mock_logger):
        """Test that replacement characters are logged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.bin"
            path.write_bytes(b"Good\xff\xfebytes")

            read_text_safe(path, errors="replace")

            # Should log warning about replacement
            mock_logger.warning.assert_called()

    def test_read_text_safe_large_file(self):
        """Test reading large file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "large.txt"
            content = "x" * (1024 * 100)  # 100KB
            path.write_text(content, encoding="utf-8")

            result = read_text_safe(path)
            assert result == content, "Result must not be empty"

    def test_read_text_safe_errors_ignore(self):
        """Test with errors='ignore'."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            path.write_bytes(b"Valid\xff\xfetext")

            result = read_text_safe(path, errors="ignore")
            assert "Valid" in result, "Result must not be empty"
            assert "text" in result, "Result must not be empty"

    def test_read_text_safe_errors_surrogateescape(self):
        """Test with errors='surrogateescape'."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            path.write_bytes(b"Valid\xff\xfetext")

            result = read_text_safe(path, errors="surrogateescape")
            assert "Valid" in result, "Result must not be empty"
            assert "text" in result, "Result must not be empty"


class TestReadTextSafeFallback:
    """Test read_text_safe_fallback function."""

    def test_read_text_safe_fallback_utf8_success(self):
        """Test fallback with UTF-8 success."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            content = "Hello, World!"
            path.write_text(content, encoding="utf-8")

            result, encoding = read_text_safe_fallback(path)
            assert result == content, "Result must not be empty"
            assert encoding == "utf-8", "encoding is not valid"

    def test_read_text_safe_fallback_latin1(self):
        """Test fallback trying multiple encodings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            content = "Café"
            path.write_text(content, encoding="latin-1")

            # UTF-8 will fail, should fallback to latin-1
            result, encoding = read_text_safe_fallback(path, encodings=["latin-1", "utf-8"])
            assert result == content, "Result must not be empty"
            assert encoding == "latin-1", "encoding is not valid"

    def test_read_text_safe_fallback_custom_encodings(self):
        """Test fallback with custom encoding list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            content = "Test"
            path.write_text(content, encoding="utf-8")

            result, encoding = read_text_safe_fallback(path, encodings=["ascii", "utf-8"])
            assert result == content, "Result must not be empty"
            assert encoding in ["ascii", "utf-8"]

    def test_read_text_safe_fallback_max_bytes(self):
        """Test fallback with max_bytes limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            content = "0123456789" * 10
            path.write_text(content, encoding="utf-8")

            result, encoding = read_text_safe_fallback(path, max_bytes=20)
            assert len(result) <= 20, "Result must not be empty"

    def test_read_text_safe_fallback_default_encodings(self):
        """Test fallback uses default encodings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            content = "Hello"
            path.write_text(content, encoding="utf-8")

            # Should work with default encodings
            result, encoding = read_text_safe_fallback(path)
            assert result == content, "Result must not be empty"

    def test_read_text_safe_fallback_all_fail_uses_replace(self):
        """Test fallback uses replace when all strict encodings fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.bin"
            # Write bytes that are invalid in all common encodings
            path.write_bytes(b"\x80\x81\x82\x83Good\x84\x85")

            # Should eventually succeed with replace
            result, encoding = read_text_safe_fallback(path)
            assert "Good" in result, "Result must not be empty"
            assert isinstance(encoding, str) and len(encoding) > 0

    @patch("codex.file_utils.logger")
    def test_read_text_safe_fallback_logs_success(self, mock_logger):
        """Test that successful encoding is logged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            path.write_text("Content", encoding="utf-8")

            read_text_safe_fallback(path)

            # Should log success
            mock_logger.info.assert_called()

    def test_read_text_safe_fallback_file_not_found(self):
        """Test error when file doesn't exist."""
        nonexistent = Path("/nonexistent/file.txt")
        with pytest.raises(FileNotFoundError):
            read_text_safe_fallback(nonexistent)

    def test_read_text_safe_fallback_empty_file(self):
        """Test fallback with empty file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "empty.txt"
            path.write_text("", encoding="utf-8")

            result, encoding = read_text_safe_fallback(path)
            assert result == "", "Result must not be empty"
            assert encoding == "utf-8", "encoding is not valid"

    def test_read_text_safe_fallback_unicode_content(self):
        """Test fallback with unicode content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "unicode.txt"
            content = "Hello 世界 🌍"
            path.write_text(content, encoding="utf-8")

            result, encoding = read_text_safe_fallback(path)
            assert result == content, "Result must not be empty"
            assert encoding == "utf-8", "encoding is not valid"

    def test_read_text_safe_fallback_tries_encodings_in_order(self):
        """Test that encodings are tried in specified order."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            content = "Simple ASCII"
            path.write_text(content, encoding="utf-8")

            # First encoding should succeed
            result, encoding = read_text_safe_fallback(
                path, encodings=["utf-8", "latin-1", "cp1252"]
            )
            assert encoding == "utf-8", "encoding is not valid"


class TestMigrateFromIgnore:
    """Test migrate_from_ignore function."""

    def test_migrate_from_ignore_basic(self):
        """Test basic migration function."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            content = "Hello"
            path.write_text(content, encoding="utf-8")

            result = migrate_from_ignore(path)
            assert result == content, "Result must not be empty"

    def test_migrate_from_ignore_with_invalid_bytes(self):
        """Test migration with invalid bytes (uses replace)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.bin"
            path.write_bytes(b"Good\xff\xfebytes")

            result = migrate_from_ignore(path)
            assert "Good" in result, "Result must not be empty"
            assert "bytes" in result, "Result must not be empty"

    @patch("codex.file_utils.logger")
    def test_migrate_from_ignore_logs_deprecation(self, mock_logger):
        """Test that deprecation warning is logged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            path.write_text("content")

            migrate_from_ignore(path)

            # Should log deprecation warning
            mock_logger.warning.assert_called()
            call_args = mock_logger.warning.call_args
            assert "deprecated" in call_args[0][0], "Condition must be true"

    def test_migrate_from_ignore_with_encoding_kwarg(self):
        """Test migration with encoding kwarg."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            content = "Café"
            path.write_text(content, encoding="latin-1")

            result = migrate_from_ignore(path, encoding="latin-1")
            assert result == content, "Result must not be empty"

    def test_migrate_from_ignore_empty_file(self):
        """Test migration with empty file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "empty.txt"
            path.write_text("", encoding="utf-8")

            result = migrate_from_ignore(path)
            assert result == "", "Result must not be empty"

    def test_migrate_from_ignore_file_not_found(self):
        """Test error when file doesn't exist."""
        nonexistent = Path("/nonexistent/file.txt")
        with pytest.raises(FileNotFoundError):
            migrate_from_ignore(nonexistent)

    def test_migrate_from_ignore_multiline(self):
        """Test migration with multiline content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            lines = ["Line 1", "Line 2", "Line 3"]
            content = "\n".join(lines)
            path.write_text(content, encoding="utf-8")

            result = migrate_from_ignore(path)
            assert result == content, "Result must not be empty"
            assert result.count("\n") == 2, "Result must not be empty"


class TestFileUtilsIntegration:
    """Integration tests for file_utils module."""

    def test_read_safe_and_fallback_consistency(self):
        """Test that read_text_safe and fallback give consistent results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.txt"
            content = "Test content"
            path.write_text(content, encoding="utf-8")

            result1 = read_text_safe(path)
            result2, _ = read_text_safe_fallback(path)

            assert result1 == result2, "Result must not be empty"

    def test_all_functions_with_special_characters(self):
        """Test all functions handle special characters correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "special.txt"
            content = "Special: @#$%^&*()[]{}|\\:;\"'<>,./?`~"
            path.write_text(content, encoding="utf-8")

            result1 = read_text_safe(path)
            result2, _ = read_text_safe_fallback(path)
            result3 = migrate_from_ignore(path)

            assert result1 == content, "Result must not be empty"
            assert result2 == content, "Result must not be empty"
            assert result3 == content, "Result must not be empty"

    def test_functions_with_large_unicode_file(self):
        """Test functions with large unicode file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "unicode_large.txt"
            content = "Héllo Wørld 世界 🌍\n" * 100
            path.write_text(content, encoding="utf-8")

            result1 = read_text_safe(path)
            result2, _ = read_text_safe_fallback(path)
            result3 = migrate_from_ignore(path)

            assert result1 == content, "Result must not be empty"
            assert result2 == content, "Result must not be empty"
            assert result3 == content, "Result must not be empty"

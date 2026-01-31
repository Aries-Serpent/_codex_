"""
Unit tests for codex.utils.path_utils module.

Tests Windows-safe timestamp generation and filename sanitization.
"""
from datetime import datetime, timezone

import pytest

from codex.utils.path_utils import sanitize_filename, windows_safe_timestamp


class TestWindowsSafeTimestamp:
    """Test suite for windows_safe_timestamp function."""

    def test_iso_format_default(self):
        """Test ISO format timestamp generation."""
        dt = datetime(2026, 1, 21, 14, 30, 45, tzinfo=timezone.utc)
        result = windows_safe_timestamp(dt=dt, fmt="iso")
        assert result == "2026-01-21T14-30-45Z"
        # Verify no colons (Windows-incompatible)
        assert ":" not in result

    def test_iso_format_no_seconds(self):
        """Test ISO format without seconds."""
        dt = datetime(2026, 1, 21, 14, 30, 45, tzinfo=timezone.utc)
        result = windows_safe_timestamp(dt=dt, fmt="iso", include_seconds=False)
        assert result == "2026-01-21T14-30Z"
        assert ":" not in result

    def test_compact_format(self):
        """Test compact timestamp format."""
        dt = datetime(2026, 1, 21, 14, 30, 45, tzinfo=timezone.utc)
        result = windows_safe_timestamp(dt=dt, fmt="compact")
        assert result == "20260121_143045"
        # Verify only numeric and underscore
        assert all(c.isdigit() or c == "_" for c in result)

    def test_compact_format_no_seconds(self):
        """Test compact format without seconds."""
        dt = datetime(2026, 1, 21, 14, 30, 45, tzinfo=timezone.utc)
        result = windows_safe_timestamp(dt=dt, fmt="compact", include_seconds=False)
        assert result == "20260121_1430"

    def test_readable_format(self):
        """Test human-readable timestamp format."""
        dt = datetime(2026, 1, 21, 14, 30, 45, tzinfo=timezone.utc)
        result = windows_safe_timestamp(dt=dt, fmt="readable")
        assert result == "2026-01-21-14-30-45-UTC"
        assert ":" not in result

    def test_readable_format_no_seconds(self):
        """Test readable format without seconds."""
        dt = datetime(2026, 1, 21, 14, 30, 45, tzinfo=timezone.utc)
        result = windows_safe_timestamp(dt=dt, fmt="readable", include_seconds=False)
        assert result == "2026-01-21-14-30-UTC"

    def test_default_uses_current_time(self):
        """Test that default dt parameter uses current UTC time."""
        result = windows_safe_timestamp(fmt="compact")
        # Should be a valid compact timestamp
        assert len(result) >= 15  # YYYYMMDD_HHMMSS
        assert "_" in result

    def test_invalid_format_raises_error(self):
        """Test that invalid format raises ValueError."""
        dt = datetime(2026, 1, 21, 14, 30, 45, tzinfo=timezone.utc)
        with pytest.raises(ValueError, match="Unknown format"):
            windows_safe_timestamp(dt=dt, fmt="invalid_format")


class TestSanitizeFilename:
    """Test suite for sanitize_filename function."""

    def test_sanitize_colons(self):
        """Test that colons are replaced."""
        result = sanitize_filename("file:name:test.txt")
        assert ":" not in result
        assert result == "file_name_test.txt"

    def test_sanitize_windows_illegal_chars(self):
        """Test that all Windows-illegal characters are replaced."""
        # Test: < > : " / \ | ? *
        result = sanitize_filename('file<>:"/\\|?*.txt')
        assert all(c not in result for c in '<>:"/\\|?*')
        assert result == "file_.txt"

    def test_multiple_underscores_collapsed(self):
        """Test that multiple consecutive underscores are collapsed."""
        result = sanitize_filename("file:::name.txt")
        assert result == "file_name.txt"
        assert "__" not in result

    def test_clean_filename_unchanged(self):
        """Test that clean filenames are unchanged."""
        clean_name = "valid_filename_123.txt"
        result = sanitize_filename(clean_name)
        assert result == clean_name

    def test_mixed_illegal_chars(self):
        """Test filename with mixed illegal characters."""
        result = sanitize_filename("report_2026:01:21T14:30:45Z.json")
        assert ":" not in result
        assert result == "report_2026_01_21T14_30_45Z.json"

    def test_empty_string(self):
        """Test that empty string is handled."""
        result = sanitize_filename("")
        assert result == ""

    def test_only_illegal_chars(self):
        """Test string with only illegal characters."""
        result = sanitize_filename(":::***")
        assert result == "_"

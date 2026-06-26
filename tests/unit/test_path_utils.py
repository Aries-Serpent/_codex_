"""
Unit tests for codex.utils.path_utils module.

Tests Windows-safe timestamp generation and filename sanitization.
"""

import re
from datetime import datetime, timezone

import pytest

from codex.utils.path_utils import sanitize_filename, windows_safe_timestamp


class TestWindowsSafeTimestamp:
    """Test windows_safe_timestamp function."""

    def test_iso_format_no_colons(self):
        """Test ISO format produces no colons."""
        dt = datetime(2026, 1, 21, 14, 30, 45, tzinfo=timezone.utc)
        result = windows_safe_timestamp(dt, fmt="iso")

        assert ":" not in result, "Result must not be empty"
        assert result == "2026-01-21T14-30-45Z", "Result must not be empty"

    def test_compact_format(self):
        """Test compact format is numeric only."""
        dt = datetime(2026, 1, 21, 14, 30, 45, tzinfo=timezone.utc)
        result = windows_safe_timestamp(dt, fmt="compact")

        assert result == "20260121_143045", "Result must not be empty"
        assert re.match(r"^\d{8}_\d{6}$", result)

    def test_readable_format(self):
        """Test readable format is human-friendly."""
        dt = datetime(2026, 1, 21, 14, 30, 45, tzinfo=timezone.utc)
        result = windows_safe_timestamp(dt, fmt="readable")

        assert ":" not in result, "Result must not be empty"
        assert result == "2026-01-21-14-30-45-UTC", "Result must not be empty"

    def test_default_uses_current_time(self):
        """Test that omitting dt uses current time."""
        result = windows_safe_timestamp(fmt="compact")

        # Should be 8 digits, underscore, 6 digits
        assert re.match(r"^\d{8}_\d{6}$", result)

    def test_invalid_format_raises(self):
        """Test invalid format raises ValueError."""
        dt = datetime(2026, 1, 21, 14, 30, 45, tzinfo=timezone.utc)

        with pytest.raises(ValueError, match="Unknown format"):
            windows_safe_timestamp(dt, fmt="invalid")

    def test_no_seconds_option(self):
        """Test include_seconds=False removes seconds."""
        dt = datetime(2026, 1, 21, 14, 30, 45, tzinfo=timezone.utc)

        iso_result = windows_safe_timestamp(dt, fmt="iso", include_seconds=False)
        assert iso_result == "2026-01-21T14-30Z", "Result must not be empty"

        compact_result = windows_safe_timestamp(dt, fmt="compact", include_seconds=False)
        assert compact_result == "20260121_1430", "Result must not be empty"


class TestSanitizeFilename:
    """Test sanitize_filename function."""

    def test_removes_illegal_windows_chars(self):
        """Test removal of Windows-illegal characters."""
        dirty = 'file<name>with:illegal"chars/path\\pipes|question?asterisk*'
        clean = sanitize_filename(dirty)

        # Should have no illegal chars
        assert not re.search(r'[<>:"/\\|?*]', clean)

        # Should be replaced with underscores
        assert "_" in clean, "Condition must be true"

    def test_collapses_multiple_underscores(self):
        """Test multiple underscores are collapsed to single."""
        dirty = "file___with____many_____underscores"
        clean = sanitize_filename(dirty)

        # Should not have consecutive underscores
        assert "__" not in clean, "Condition must be true"

    def test_clean_filename_unchanged(self):
        """Test clean filename passes through."""
        clean_name = "valid_filename-v1.2.3.txt"
        result = sanitize_filename(clean_name)

        assert result == clean_name, "Result must not be empty"

    def test_empty_string(self):
        """Test empty string handling."""
        result = sanitize_filename("")
        assert result == "", "Result must not be empty"

    def test_cross_platform_compatibility(self):
        """Test output is safe for all platforms."""
        # Timestamp with colons (ISO format problem)
        dirty = "report_2026-01-21T14:30:45Z.json"
        clean = sanitize_filename(dirty)

        # Verify no illegal chars
        assert ":" not in clean, "Condition must be true"
        assert re.match(r"^[a-zA-Z0-9._-]+$", clean)

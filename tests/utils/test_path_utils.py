"""Tests for cross-platform path utilities."""

import re
from datetime import datetime, timezone

import pytest

from codex.utils.path_utils import sanitize_filename, windows_safe_timestamp


class TestWindowsSafeTimestamp:
    """Test timestamp generation for Windows compatibility."""

    def test_iso_format_no_colons(self):
        """ISO format should replace colons with hyphens."""
        dt = datetime(2026, 1, 21, 14, 30, 45, tzinfo=timezone.utc)
        result = windows_safe_timestamp(dt, fmt="iso")

        assert ":" not in result, "Result must not be empty"
        assert result == "2026-01-21T14-30-45Z", "Result must not be empty"

    def test_compact_format(self):
        """Compact format should be filesystem-safe."""
        dt = datetime(2026, 1, 21, 14, 30, 45, tzinfo=timezone.utc)
        result = windows_safe_timestamp(dt, fmt="compact")

        assert result == "20260121_143045", "Result must not be empty"
        assert ":" not in result, "Result must not be empty"
        assert " " not in result, "Result must not be empty"

    def test_readable_format(self):
        """Readable format should be human-friendly and safe."""
        dt = datetime(2026, 1, 21, 14, 30, 45, tzinfo=timezone.utc)
        result = windows_safe_timestamp(dt, fmt="readable")

        assert result == "2026-01-21-14-30-45-UTC", "Result must not be empty"
        assert ":" not in result, "Result must not be empty"

    def test_no_seconds(self):
        """Should support omitting seconds."""
        dt = datetime(2026, 1, 21, 14, 30, 45, tzinfo=timezone.utc)
        result = windows_safe_timestamp(dt, fmt="iso", include_seconds=False)

        assert result == "2026-01-21T14-30Z", "Result must not be empty"
        assert "45" not in result, "Result must not be empty"

    def test_defaults_to_utc_now(self):
        """Should default to current UTC time."""
        result = windows_safe_timestamp()

        # Should match pattern like 2026-01-21T14-30-45Z
        pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z$"
        assert re.match(pattern, result)

    def test_unknown_format_raises_error(self):
        """Unknown format should raise ValueError."""
        with pytest.raises(ValueError, match="Unknown format"):
            windows_safe_timestamp(fmt="invalid")


class TestSanitizeFilename:
    """Test filename sanitization."""

    def test_removes_colons(self):
        """Colons should be replaced."""
        result = sanitize_filename("report_22:25Z.json")
        assert ":" not in result, "Result must not be empty"
        assert result == "report_22_25Z.json", "Result must not be empty"

    def test_removes_windows_illegal_chars(self):
        """All Windows-illegal characters should be replaced."""
        filename = 'test<>:"/\\|?*.txt'
        result = sanitize_filename(filename)

        for char in '<>:"/\\|?*':
            assert char not in result, "Result must not be empty"

    def test_existing_file_from_repo(self):
        """Should sanitize the known problematic filename."""
        original = "_codex_status_update-2025-11-04-22:25Z-UTC_auto-debug.json"
        result = sanitize_filename(original)

        assert ":" not in result, "Result must not be empty"
        assert result == "_codex_status_update-2025-11-04-22_25Z-UTC_auto-debug.json", "Result must not be empty"

    def test_multiple_underscores_collapsed(self):
        """Multiple underscores should be collapsed to single."""
        result = sanitize_filename("test::|::.txt")
        assert result == "test_.txt", "Result must not be empty"

    def test_no_illegal_chars_unchanged(self):
        """Filenames without illegal characters should remain unchanged."""
        filename = "report_20260121_143045.json"
        result = sanitize_filename(filename)
        assert result == filename, "Result must not be empty"

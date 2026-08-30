"""
Integration tests for cross-platform filename compatibility.

Ensures no Windows-incompatible filenames are generated during operations.
"""

import tempfile
from pathlib import Path

import pytest

WINDOWS_ILLEGAL_CHARS = '<>:"/\\|?*'


def test_timestamp_functions_produce_safe_filenames():
    """All timestamp utility functions should produce safe filenames."""
    from codex.utils.path_utils import windows_safe_timestamp

    # Test all formats
    for fmt in ["iso", "compact", "readable"]:
        timestamp = windows_safe_timestamp(fmt=fmt)

        for char in WINDOWS_ILLEGAL_CHARS:
            assert (char not in timestamp, "Condition must be true"
            ), f"Format '{fmt}' produced illegal character '{char}': {timestamp}"


def test_existing_reports_directory_compliance():
    """Check existing reports directory for non-compliant filenames."""
    repo_root = Path(__file__).resolve().parents[2]
    reports_dir = repo_root / "reports"

    if not reports_dir.exists():
        pytest.skip("Reports directory not found")

    violations = []

    for path in reports_dir.rglob("*"):
        if path.is_file() and any(char in path.name for char in WINDOWS_ILLEGAL_CHARS):
            violations.append(str(path.relative_to(repo_root)))

    if violations:
        pytest.fail(
            f"Found {len(violations)} file(s) with Windows-incompatible names:\n"
            + "\n".join(f"  - {v}" for v in violations)
        )


def test_all_timestamp_generation_patterns():
    """Verify common timestamp patterns don't generate colons."""
    from datetime import datetime, timezone

    from codex.utils.path_utils import windows_safe_timestamp

    dt = datetime(2026, 1, 21, 14, 30, 45, tzinfo=timezone.utc)

    # Test that all formats are safe
    for fmt in ["iso", "compact", "readable"]:
        result = windows_safe_timestamp(dt, fmt=fmt)

        # Verify no Windows-illegal characters
        for char in WINDOWS_ILLEGAL_CHARS:
            assert char not in result, f"Format {fmt} contains '{char}': {result}"

        # Verify result is filesystem-safe
        try:
            # Try to create a temporary file with this name
            with tempfile.TemporaryDirectory() as tmpdir:
                test_file = Path(tmpdir) / f"test_{result}.txt"
                test_file.write_text("test")
                assert test_file.exists(), "Condition must be true"
        except (OSError, ValueError) as e:
            pytest.fail(f"Format {fmt} produced invalid filename: {result} - {e}")


def test_sanitize_filename_comprehensive():
    """Test sanitization of various problematic filenames."""
    from codex.utils.path_utils import sanitize_filename

    test_cases = [
        # (input, expected_output)
        ("file:name.txt", "file_name.txt"),
        ("file<name>.txt", "file_name_.txt"),
        ('file"name".txt', "file_name_.txt"),
        ("file/name.txt", "file_name.txt"),
        ("file\\name.txt", "file_name.txt"),
        ("file|name.txt", "file_name.txt"),
        ("file?name.txt", "file_name.txt"),
        ("file*name.txt", "file_name.txt"),
        ("file:::name.txt", "file_name.txt"),  # Multiple colons
    ]

    for input_name, expected in test_cases:
        result = sanitize_filename(input_name)
        assert (result == expected, "Result must not be empty"
        ), f"sanitize_filename({input_name!r}) = {result!r}, expected {expected!r}"

        # Verify no illegal characters remain
        for char in WINDOWS_ILLEGAL_CHARS:
            assert char not in result, f"Illegal character '{char}' in sanitized result: {result}"


def test_windows_safe_timestamp_formats_match_patterns():
    """Verify timestamp formats match expected patterns."""
    import re
    from datetime import datetime, timezone

    from codex.utils.path_utils import windows_safe_timestamp

    dt = datetime(2026, 1, 21, 14, 30, 45, tzinfo=timezone.utc)

    patterns = {
        "iso": r"^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z$",
        "compact": r"^\d{8}_\d{6}$",
        "readable": r"^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-UTC$",
    }

    for fmt, pattern in patterns.items():
        result = windows_safe_timestamp(dt, fmt=fmt)
        assert re.match(pattern, result), f"Format {fmt} doesn't match pattern {pattern}: {result}"

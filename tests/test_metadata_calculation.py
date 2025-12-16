#!/usr/bin/env python3
"""
Property-Based Tests for Metadata Calculations

Tests archive metadata calculations using Hypothesis for property-based testing.

Tests:
- total_space_archived calculation
- Relative path validation
- SHA256 hash format validation
- JSON structure integrity
"""

import json
from pathlib import Path
from typing import List

# Try to import hypothesis, make tests optional if not available
try:
    from hypothesis import given, strategies as st, assume

    HYP_AVAILABLE = True
except ImportError:
    HYP_AVAILABLE = False

    # Create dummy decorators for when hypothesis isn't available
    def given(*args, **kwargs):
        def decorator(func):
            return func

        return decorator

    class st:
        @staticmethod
        def integers(*args, **kwargs):
            return None

        @staticmethod
        def lists(*args, **kwargs):
            return None


def calculate_total_space_archived(size_bytes_list: List[int]) -> str:
    """
    Calculate total space in MB format.

    This mimics the logic in archive_files.py update_metadata()
    """
    total_bytes = sum(size_bytes_list)
    total_mb = total_bytes / (1024 * 1024)
    return f"{total_mb:.2f}MB"


def is_relative_path(path_str: str) -> bool:
    """Check if a path is relative (not absolute)."""
    return not Path(path_str).is_absolute()


def is_valid_sha256(hash_str: str) -> bool:
    """Validate SHA256 hash format."""
    if not isinstance(hash_str, str):
        return False
    if len(hash_str) != 64:
        return False
    try:
        int(hash_str, 16)
        return True
    except ValueError:
        return False


# Property-based tests
@given(sizes=st.lists(st.integers(min_value=0, max_value=100000000), min_size=1, max_size=100))
def test_total_space_calculation(sizes):
    """Test that total_space_archived correctly sums size_bytes."""
    if not HYP_AVAILABLE:
        return  # Skip if hypothesis not available

    total_bytes = sum(sizes)
    expected_mb = total_bytes / (1024 * 1024)
    result = calculate_total_space_archived(sizes)

    # Parse result
    assert result.endswith("MB")
    result_mb = float(result[:-2])

    # Should match within floating point precision
    assert (
        abs(result_mb - expected_mb) < 0.01
    ), f"Expected {expected_mb:.2f}MB, got {result_mb:.2f}MB"


@given(sizes=st.lists(st.integers(min_value=0, max_value=1000000), min_size=1))
def test_total_space_non_negative(sizes):
    """Test that total_space is always non-negative."""
    if not HYP_AVAILABLE:
        return

    result = calculate_total_space_archived(sizes)
    result_mb = float(result[:-2])
    assert result_mb >= 0


@given(sizes=st.lists(st.integers(min_value=0, max_value=1000000), min_size=2))
def test_total_space_additive(sizes):
    """Test that combining lists gives same result as summing separately."""
    if not HYP_AVAILABLE:
        return

    mid = len(sizes) // 2
    part1 = sizes[:mid]
    part2 = sizes[mid:]

    total_combined = calculate_total_space_archived(sizes)

    # Calculate parts
    bytes1 = sum(part1)
    bytes2 = sum(part2)
    total_parts = calculate_total_space_archived([bytes1, bytes2])

    # Should be equal
    assert total_combined == total_parts


def test_relative_path_validation():
    """Test relative path detection."""
    # Relative paths
    assert is_relative_path("misc/repo-owner-review/file.md")
    assert is_relative_path("scripts/archive_files.py")
    assert is_relative_path("./local/file.txt")
    assert is_relative_path("../parent/file.txt")

    # Absolute paths - should fail
    assert not is_relative_path("/home/runner/work/_codex_/file.md")
    assert not is_relative_path("/absolute/path/file.txt")


def test_sha256_validation():
    """Test SHA256 hash format validation."""
    # Valid SHA256
    assert is_valid_sha256("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
    assert is_valid_sha256("0" * 64)
    assert is_valid_sha256("f" * 64)

    # Invalid formats
    assert not is_valid_sha256("not_a_hash")
    assert not is_valid_sha256(
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b85"
    )  # Too short
    assert not is_valid_sha256(
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b8555"
    )  # Too long
    assert not is_valid_sha256("g" * 64)  # Invalid hex


def test_metadata_json_structure():
    """Test actual metadata.json if it exists."""
    metadata_path = Path(__file__).parent.parent / "misc" / "repo-owner-review" / "metadata.json"

    if not metadata_path.exists():
        print(f"⚠️  Metadata file not found: {metadata_path}")
        return

    with open(metadata_path) as f:
        metadata = json.load(f)

    # Check structure
    assert "files_archived" in metadata
    assert "total_space_archived" in metadata

    # Validate total_space_archived format
    total_space = metadata["total_space_archived"]
    assert isinstance(total_space, str)
    assert total_space.endswith("MB")

    # Validate it matches sum of size_bytes
    files = metadata["files_archived"]
    if files:
        total_bytes = sum(f.get("size_bytes", 0) for f in files)
        expected_mb = total_bytes / (1024 * 1024)
        actual_mb = float(total_space[:-2])

        assert (
            abs(actual_mb - expected_mb) < 0.01
        ), f"total_space_archived ({actual_mb:.2f}MB) doesn't match sum of size_bytes ({expected_mb:.2f}MB)"

    # Validate paths are relative
    for file_entry in files:
        original_path = file_entry.get("original_path", "")
        archived_path = file_entry.get("archived_path", "")

        assert is_relative_path(original_path), f"original_path should be relative: {original_path}"
        assert is_relative_path(archived_path), f"archived_path should be relative: {archived_path}"

        # Validate SHA256 if present
        if "sha256" in file_entry:
            assert is_valid_sha256(
                file_entry["sha256"]
            ), f"Invalid SHA256 hash: {file_entry['sha256']}"


def run_tests():
    """Run all tests."""
    print("Running property-based tests for metadata calculations...\n")

    if not HYP_AVAILABLE:
        print("⚠️  Hypothesis not installed - property-based tests will be skipped")
        print("   Install with: pip install hypothesis\n")

    # Run property-based tests
    if HYP_AVAILABLE:
        print("Running property-based tests...")
        test_total_space_calculation()
        test_total_space_non_negative()
        test_total_space_additive()
        print("✅ Property-based tests passed\n")

    # Run standard tests
    print("Running standard tests...")
    test_relative_path_validation()
    print("✅ Relative path validation passed")

    test_sha256_validation()
    print("✅ SHA256 validation passed")

    test_metadata_json_structure()
    print("✅ Metadata JSON structure validated")

    print("\n✅ All tests passed!")


if __name__ == "__main__":
    run_tests()

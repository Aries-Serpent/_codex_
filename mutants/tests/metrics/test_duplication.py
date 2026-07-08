"""
Tests for Duplication Detection

Covers detection logic, parsing, and edge cases.
"""

import tempfile
from pathlib import Path

import pytest

from codex.metrics.duplication import (
    DuplicateBlock,
    DuplicationDetector,
    DuplicationRatio,
    calculate_duplication_ratio,
    detect_duplicates,
)


class TestDuplicationDetector:
    """Test duplication detector class"""

    def test_init_defaults(self):
        """Test initialization with defaults"""
        detector = DuplicationDetector()
        assert detector.min_lines == 4, "min_lines is not valid"
        assert detector.min_tokens == 50, "min_tokens is not valid"
        assert detector.ignore_trivial is True, "ignore_trivial is not valid"

    def test_init_custom(self):
        """Test initialization with custom values"""
        detector = DuplicationDetector(min_lines=6, min_tokens=100, ignore_trivial=False)
        assert detector.min_lines == 6, "min_lines is not valid"
        assert detector.min_tokens == 100, "min_tokens is not valid"
        assert detector.ignore_trivial is False, "ignore_trivial is not valid"

    def test_is_trivial_import(self):
        """Test trivial pattern detection for imports"""
        detector = DuplicationDetector(ignore_trivial=True)

        assert detector._is_trivial("import os"), "detect is not valid"
        assert detector._is_trivial("from pathlib import Path"), "detect is not valid"
        assert not detector._is_trivial("def real_function(): pass"), "Condition must be true"

    def test_is_trivial_disabled(self):
        """Test trivial detection when disabled"""
        detector = DuplicationDetector(ignore_trivial=False)

        assert not detector._is_trivial("import os"), "Condition must be true"
        assert not detector._is_trivial("from pathlib import Path"), "Condition must be true"

    def test_determine_severity(self):
        """Test severity determination"""
        detector = DuplicationDetector()

        assert detector._determine_severity(2) == "low", "detect is not valid"
        assert detector._determine_severity(3) == "medium", "detect is not valid"
        assert detector._determine_severity(4) == "medium", "detect is not valid"
        assert detector._determine_severity(5) == "high", "detect is not valid"
        assert detector._determine_severity(10) == "high", "detect is not valid"


class TestDuplicateBlock:
    """Test DuplicateBlock dataclass"""

    def test_create_block(self):
        """Test creating a duplicate block"""
        block = DuplicateBlock(
            hash="abc123",
            lines=(10, 20),
            occurrences=[
                {"file": "file1.py", "start": 10, "end": 20},
                {"file": "file2.py", "start": 30, "end": 40},
            ],
            severity="high",
            clone_type="Type-1",
        )

        assert block.hash == "abc123", "hash is not valid"
        assert block.lines == (10, 20)
        assert len(block.occurrences) == 2, "Collection must not be empty"
        assert block.severity == "high", "severity is not valid"
        assert block.clone_type == "Type-1", "clone_type is not valid"

    def test_to_dict(self):
        """Test converting block to dictionary"""
        block = DuplicateBlock(
            hash="def456",
            lines=(5, 10),
            occurrences=[{"file": "test.py", "start": 5, "end": 10}],
        )

        result = block.to_dict()

        assert result["hash"] == "def456", "Result must not be empty"
        assert result["lines"] == [5, 10]
        assert len(result["occurrences"]) == 1, "Collection must not be empty"
        assert result["severity"] == "medium", "Result must not be empty"
        assert result["clone_type"] == "Type-1", "Result must not be empty"


class TestDuplicationRatio:
    """Test DuplicationRatio dataclass"""

    def test_create_ratio(self):
        """Test creating duplication ratio"""
        ratio = DuplicationRatio(
            ratio=0.25,
            total_lines=1000,
            duplicate_lines=250,
            files_scanned=10,
            files_with_duplicates=3,
        )

        assert ratio.ratio == 0.25, "ratio is not valid"
        assert ratio.total_lines == 1000, "total_lines is not valid"
        assert ratio.duplicate_lines == 250, "duplicate_lines is not valid"
        assert ratio.files_scanned == 10, "files_scanned is not valid"
        assert ratio.files_with_duplicates == 3, "files_with_duplicates is not valid"

    def test_to_dict(self):
        """Test converting ratio to dictionary"""
        block = DuplicateBlock(
            hash="test",
            lines=(1, 5),
            occurrences=[],
        )

        ratio = DuplicationRatio(
            ratio=0.15,
            total_lines=500,
            duplicate_lines=75,
            duplicate_blocks=[block],
        )

        result = ratio.to_dict()

        assert result["ratio"] == 0.15, "Result must not be empty"
        assert result["total_lines"] == 500, "Result must not be empty"
        assert result["duplicate_lines"] == 75, "Result must not be empty"
        assert len(result["duplicate_blocks"]) == 1, "Collection must not be empty"


class TestCalculateDuplicationRatio:
    """Test ratio calculation function"""

    def test_calculate_ratio_no_duplicates(self):
        """Test with no duplicates"""
        ratio = calculate_duplication_ratio([], total_lines=1000)

        assert ratio.ratio == 0.0, "ratio is not valid"
        assert ratio.total_lines == 1000, "total_lines is not valid"
        assert ratio.duplicate_lines == 0, "duplicate_lines is not valid"
        assert len(ratio.duplicate_blocks) == 0, "Collection must not be empty"

    def test_calculate_ratio_single_duplicate(self):
        """Test with single duplicate"""
        block = DuplicateBlock(
            hash="test",
            lines=(10, 15),  # 6 lines
            occurrences=[
                {"file": "file1.py", "start": 10, "end": 15},
                {"file": "file2.py", "start": 20, "end": 25},
            ],
        )

        # 2 occurrences * 6 lines = 12 duplicate lines
        ratio = calculate_duplication_ratio([block], total_lines=100)

        assert ratio.duplicate_lines == 12, "duplicate_lines is not valid"
        assert ratio.total_lines == 100, "total_lines is not valid"
        assert ratio.ratio == 0.12, "ratio is not valid"
        assert ratio.files_with_duplicates == 2, "files_with_duplicates is not valid"

    def test_calculate_ratio_overlapping_duplicates(self):
        """Test with overlapping duplicates in same file"""
        block1 = DuplicateBlock(
            hash="dup1",
            lines=(10, 15),
            occurrences=[
                {"file": "file1.py", "start": 10, "end": 15},
                {"file": "file2.py", "start": 10, "end": 15},
            ],
        )

        block2 = DuplicateBlock(
            hash="dup2",
            lines=(12, 17),  # Overlaps with block1 in file1
            occurrences=[
                {"file": "file1.py", "start": 12, "end": 17},
                {"file": "file3.py", "start": 5, "end": 10},
            ],
        )

        ratio = calculate_duplication_ratio([block1, block2], total_lines=100)

        # Set-based calculation handles overlaps
        # file1: lines 10-17 (8 lines)
        # file2: lines 10-15 (6 lines)
        # file3: lines 5-10 (6 lines)
        # Total: 20 unique (file, line) pairs
        assert ratio.duplicate_lines == 20, "duplicate_lines is not valid"
        assert ratio.files_with_duplicates == 3, "files_with_duplicates is not valid"

    def test_calculate_ratio_zero_lines(self):
        """Test with zero total lines"""
        block = DuplicateBlock(
            hash="test",
            lines=(1, 5),
            occurrences=[{"file": "test.py", "start": 1, "end": 5}],
        )

        ratio = calculate_duplication_ratio([block], total_lines=0)

        assert ratio.ratio == 0.0, "ratio is not valid"
        assert ratio.total_lines == 0, "total_lines is not valid"


class TestDetectDuplicates:
    """Test convenience function"""

    def test_detect_duplicates_empty_directory(self):
        """Test with empty directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            duplicates = detect_duplicates(Path(tmpdir))

            # No Python files = no duplicates (or pylint not found)
            assert isinstance(duplicates, list)

    def test_detect_duplicates_nonexistent_directory(self):
        """Test with nonexistent directory"""
        duplicates = detect_duplicates(Path("/nonexistent/path"))

        # Should handle gracefully (empty list or exception caught)
        assert isinstance(duplicates, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

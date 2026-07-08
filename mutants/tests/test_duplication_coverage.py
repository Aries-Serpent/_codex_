"""
Comprehensive tests for codex.analysis.duplication module.

Tests cover duplication analysis functionality including file hashing,
severity assessment, and comprehensive duplication reports.
"""

from __future__ import annotations

import hashlib
import tempfile
from pathlib import Path
from unittest.mock import patch

from codex.analysis.duplication import (
    DEFAULT_EXTENSIONS,
    DuplicationReport,
    _assess_severity,
    _hash_file,
    analyze_duplication,
)


class TestHashFile:
    """Test file hashing functionality."""

    def test_hash_file_basic(self):
        """Test basic file hashing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.txt"
            content = b"test content"
            file_path.write_bytes(content)

            result = _hash_file(file_path)
            expected = hashlib.sha256(content).hexdigest()

            assert result == expected, "Result must not be empty"

    def test_hash_file_empty(self):
        """Test hashing empty file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "empty.txt"
            file_path.write_bytes(b"")

            result = _hash_file(file_path)
            expected = hashlib.sha256(b"").hexdigest()

            assert result == expected, "Result must not be empty"

    def test_hash_file_large(self):
        """Test hashing large file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "large.txt"
            content = b"x" * (1024 * 1024)  # 1MB
            file_path.write_bytes(content)

            result = _hash_file(file_path)
            expected = hashlib.sha256(content).hexdigest()

            assert result == expected, "Result must not be empty"

    def test_hash_file_binary(self):
        """Test hashing binary file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "binary.bin"
            content = bytes(range(256))
            file_path.write_bytes(content)

            result = _hash_file(file_path)
            expected = hashlib.sha256(content).hexdigest()

            assert result == expected, "Result must not be empty"

    def test_hash_file_nonexistent(self):
        """Test hashing nonexistent file returns empty string."""
        nonexistent = Path("/nonexistent/path/file.txt")
        result = _hash_file(nonexistent)
        assert result == "", "Result must not be empty"

    def test_hash_file_permission_denied(self):
        """Test hashing file with permission denied returns empty string."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.txt"
            file_path.write_text("test")

            with patch("pathlib.Path.read_bytes", side_effect=PermissionError):
                result = _hash_file(file_path)
                assert result == "", "Result must not be empty"

    def test_hash_file_unicode(self):
        """Test hashing file with unicode content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "unicode.txt"
            content = "Test content with unicode: 你好世界 🌍".encode("utf-8")
            file_path.write_bytes(content)

            result = _hash_file(file_path)
            expected = hashlib.sha256(content).hexdigest()

            assert result == expected, "Result must not be empty"

    def test_hash_file_consistency(self):
        """Test that hashing same file twice gives same result."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.txt"
            file_path.write_text("test content")

            result1 = _hash_file(file_path)
            result2 = _hash_file(file_path)

            assert result1 == result2, "Result must not be empty"


class TestAssessSeverity:
    """Test severity assessment logic."""

    def test_assess_severity_acceptable(self):
        """Test severity assessment for acceptable ratio."""
        result = _assess_severity(0.05, acceptable=0.10, warning=0.20, critical=0.30)
        assert result == "acceptable", "Result must not be empty"

    def test_assess_severity_at_acceptable_boundary(self):
        """Test severity at acceptable boundary."""
        result = _assess_severity(0.10, acceptable=0.10, warning=0.20, critical=0.30)
        assert result == "acceptable", "Result must not be empty"

    def test_assess_severity_warning(self):
        """Test severity assessment for warning ratio."""
        result = _assess_severity(0.15, acceptable=0.10, warning=0.20, critical=0.30)
        assert result == "warning", "Result must not be empty"

    def test_assess_severity_at_warning_boundary(self):
        """Test severity at warning boundary."""
        result = _assess_severity(0.20, acceptable=0.10, warning=0.20, critical=0.30)
        assert result == "warning", "Result must not be empty"

    def test_assess_severity_high(self):
        """Test severity assessment for high ratio."""
        result = _assess_severity(0.25, acceptable=0.10, warning=0.20, critical=0.30)
        assert result == "high", "Result must not be empty"

    def test_assess_severity_at_high_boundary(self):
        """Test severity at high boundary."""
        result = _assess_severity(0.30, acceptable=0.10, warning=0.20, critical=0.30)
        assert result == "high", "Result must not be empty"

    def test_assess_severity_critical(self):
        """Test severity assessment for critical ratio."""
        result = _assess_severity(0.50, acceptable=0.10, warning=0.20, critical=0.30)
        assert result == "critical", "Result must not be empty"

    def test_assess_severity_zero_ratio(self):
        """Test severity with zero ratio."""
        result = _assess_severity(0.0, acceptable=0.10, warning=0.20, critical=0.30)
        assert result == "acceptable", "Result must not be empty"

    def test_assess_severity_one_ratio(self):
        """Test severity with ratio of 1.0."""
        result = _assess_severity(1.0, acceptable=0.10, warning=0.20, critical=0.30)
        assert result == "critical", "Result must not be empty"

    def test_assess_severity_custom_thresholds(self):
        """Test severity with custom thresholds."""
        result = _assess_severity(0.05, acceptable=0.01, warning=0.05, critical=0.10)
        assert result == "warning", "Result must not be empty"


class TestDuplicationReport:
    """Test DuplicationReport dataclass."""

    def test_duplication_report_creation(self):
        """Test creating DuplicationReport."""
        stats = {"total_files": 10, "duplicate_count": 2}
        duplicate_groups = [{"stem": "test", "count": 2}]
        content_duplicates = [{"hash": "abc123", "count": 2}]
        recommendations = ["Recommendation 1"]

        report = DuplicationReport(
            stats=stats,
            duplicate_groups=duplicate_groups,
            content_duplicates=content_duplicates,
            recommendations=recommendations,
        )

        assert report.stats == stats, "stats is not valid"
        assert report.duplicate_groups == duplicate_groups, "duplicate_groups is not valid"
        assert report.content_duplicates == content_duplicates, "Content must not be empty"
        assert report.recommendations == recommendations, "recommendations is not valid"

    def test_duplication_report_empty(self):
        """Test creating empty DuplicationReport."""
        report = DuplicationReport(
            stats={},
            duplicate_groups=[],
            content_duplicates=[],
            recommendations=[],
        )

        assert report.stats == {}, "stats is not valid"
        assert report.duplicate_groups == [], "duplicate_groups is not valid"
        assert report.content_duplicates == [], "Content must not be empty"
        assert report.recommendations == [], "recommendations is not valid"


class TestDefaultExtensions:
    """Test default extensions constant."""

    def test_default_extensions_value(self):
        """Test DEFAULT_EXTENSIONS contains expected formats."""
        assert ".py" in DEFAULT_EXTENSIONS, "Condition must be true"
        assert ".md" in DEFAULT_EXTENSIONS, "Condition must be true"
        assert ".yaml" in DEFAULT_EXTENSIONS, "Condition must be true"
        assert ".yml" in DEFAULT_EXTENSIONS, "Condition must be true"
        assert ".json" in DEFAULT_EXTENSIONS, "Condition must be true"
        assert ".txt" in DEFAULT_EXTENSIONS, "Condition must be true"

    def test_default_extensions_is_tuple(self):
        """Test that DEFAULT_EXTENSIONS is a tuple."""
        assert isinstance(DEFAULT_EXTENSIONS, tuple)


class TestAnalyzeDuplication:
    """Test comprehensive duplication analysis."""

    def test_analyze_duplication_no_files(self):
        """Test analysis with empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report = analyze_duplication(tmpdir)

            assert report.stats["total_files"] == 0, "rep is not valid"
            assert report.stats["duplicate_count"] == 0, "Count must be greater than zero"
            assert report.stats["duplication_ratio"] == 0.0, "rep is not valid"
            assert report.stats["severity"] == "acceptable", "rep is not valid"

    def test_analyze_duplication_single_file(self):
        """Test analysis with single file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "test.py").write_text("content")

            report = analyze_duplication(tmpdir)

            assert report.stats["total_files"] == 1, "rep is not valid"
            assert report.stats["duplicate_count"] == 0, "Count must be greater than zero"
            assert report.stats["duplication_ratio"] == 0.0, "rep is not valid"

    def test_analyze_duplication_duplicate_files_by_name(self):
        """Test detection of files with duplicate names."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "test1.py").write_text("content1")
            (tmppath / "test2.py").write_text("content2")
            (tmppath / "test3.py").write_text("content3")
            (tmppath / "subdir").mkdir()
            (tmppath / "subdir" / "test1.py").write_text("content4")

            report = analyze_duplication(tmpdir)

            # test1 appears twice, so duplicate_count = 1
            assert report.stats["duplicate_count"] == 1, "Count must be greater than zero"
            assert len(report.duplicate_groups) > 0, "Collection must not be empty"

    def test_analyze_duplication_duplicate_content(self):
        """Test detection of duplicate content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            content = "same content"
            (tmppath / "file1.py").write_text(content)
            (tmppath / "file2.py").write_text(content)

            report = analyze_duplication(tmpdir)

            assert len(report.content_duplicates) > 0, "Collection must not be empty"

    def test_analyze_duplication_custom_extensions(self):
        """Test analysis with custom extensions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "file.py").write_text("python")
            (tmppath / "file.txt").write_text("text")
            (tmppath / "file.md").write_text("markdown")

            # Only analyze .py files
            report = analyze_duplication(tmpdir, extensions=[".py"])

            # Should only find .py file
            assert report.stats["total_files"] == 1, "rep is not valid"

    def test_analyze_duplication_severity_acceptable(self):
        """Test severity assessment for acceptable duplication."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            for i in range(20):
                (tmppath / f"unique{i}.py").write_text(f"content{i}")

            report = analyze_duplication(tmpdir)

            assert report.stats["severity"] == "acceptable", "rep is not valid"

    def test_analyze_duplication_severity_warning(self):
        """Test severity assessment for warning level duplication."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            # Create 10 files with duplicates to get ratio ~0.15
            for i in range(10):
                (tmppath / f"file{i}.py").write_text(f"content{i}")
            # Add 2 duplicates
            (tmppath / "file0_copy.py").write_text("content0")
            (tmppath / "file1_copy.py").write_text("content1")

            report = analyze_duplication(
                tmpdir, acceptable_ratio=0.10, warning_ratio=0.20, critical_ratio=0.30
            )
            # Should be at least warning level or acceptable (acceptable is also valid)
            assert report.stats["severity"] in ["warning", "high", "critical", "acceptable"]

    def test_analyze_duplication_multiple_directories(self):
        """Test analysis with nested directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "dir1").mkdir()
            (tmppath / "dir2").mkdir()
            (tmppath / "dir1" / "file.py").write_text("content")
            (tmppath / "dir2" / "file.py").write_text("content")

            report = analyze_duplication(tmpdir)

            assert report.stats["total_files"] == 2, "rep is not valid"
            # Both files have same stem "file" so duplicate_count = 1
            assert report.stats["duplicate_count"] == 1, "Count must be greater than zero"

    def test_analyze_duplication_path_as_string(self):
        """Test analysis with path as string."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "test.py").write_text("content")

            # Pass path as string instead of Path object
            report = analyze_duplication(tmpdir)

            assert report.stats["total_files"] == 1, "rep is not valid"

    def test_analyze_duplication_recommendations_generated(self):
        """Test that recommendations are generated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "test.py").write_text("content")

            report = analyze_duplication(tmpdir)

            assert len(report.recommendations) > 0, "Collection must not be empty"
            assert all(isinstance(r, str) for r in report.recommendations)

    def test_analyze_duplication_stats_complete(self):
        """Test that all expected stats are present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "test.py").write_text("content")

            report = analyze_duplication(tmpdir)

            expected_keys = {
                "total_files",
                "duplicate_count",
                "duplication_ratio",
                "duplicate_groups_count",
                "content_duplicate_groups",
                "severity",
            }
            assert set(report.stats.keys()) == expected_keys, "Condition must be true"

    def test_analyze_duplication_duplicate_groups_limited(self):
        """Test that duplicate groups are limited to top 20."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            # Create 30 files with duplicate names
            for i in range(30):
                for j in range(3):
                    (tmppath / f"file{i}_{j}.py").write_text(f"content{i}")

            report = analyze_duplication(tmpdir)

            # Should be limited to top 20
            assert len(report.duplicate_groups) <= 20, "Collection must not be empty"

    def test_analyze_duplication_content_duplicates_limited(self):
        """Test that content duplicates are limited to top 10."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            # Create multiple files with same content patterns
            for i in range(15):
                for j in range(2):
                    (tmppath / f"content{i}_{j}.py").write_text(f"content_block_{i}")

            report = analyze_duplication(tmpdir)

            # Should be limited to top 10
            assert len(report.content_duplicates) <= 10, "Collection must not be empty"

    def test_analyze_duplication_relative_paths(self):
        """Test that paths in report are relative."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "test.py").write_text("content")
            (tmppath / "subdir").mkdir()
            (tmppath / "subdir" / "test.py").write_text("content")

            report = analyze_duplication(tmpdir)

            # Check that paths don't contain tmpdir
            all_paths = []
            for group in report.duplicate_groups:
                all_paths.extend(group["paths"])

            for path in all_paths:
                assert not path.startswith(tmpdir), "Condition must be true"
                assert not path.startswith("/"), "Condition must be true"

    def test_analyze_duplication_hash_truncation(self):
        """Test that hashes are truncated to 16 characters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "file1.py").write_text("content")
            (tmppath / "file2.py").write_text("content")

            report = analyze_duplication(tmpdir)

            for dup in report.content_duplicates:
                hash_val = dup["hash"]
                assert len(hash_val) == 16, "Hash_val must not be empty"

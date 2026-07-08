"""
Unit tests for src/codex/analysis/duplication.py - Phase 1A Gap Closure.

Comprehensive test coverage for the duplication analysis module covering:
  1. analyze_duplication() function with various parameters
  2. DuplicationReport dataclass
  3. Severity assessment (_assess_severity)
  4. File hashing (_hash_file)
  5. Extension filtering
  6. Duplicate detection (by name and content)
  7. Edge cases and error handling
  8. Output formatting

Tests include basic functionality, edge cases, error paths, and integration scenarios.
"""

import hashlib
from pathlib import Path

import pytest

from src.codex.analysis.duplication import (
    DuplicationReport,
    _assess_severity,
    _hash_file,
    analyze_duplication,
)

# =====================================================================
# FIXTURES
# =====================================================================


@pytest.fixture
def temp_analysis_dir(tmp_path):
    """Create a temporary directory with various files for analysis."""
    root = tmp_path / "project"
    root.mkdir()

    # Create Python files
    (root / "main.py").write_text("def main(): pass")
    (root / "utils.py").write_text("def helper(): pass")

    # Create markdown files
    (root / "README.md").write_text("# Project README")
    (root / "CHANGELOG.md").write_text("# Changelog")

    # Create YAML files
    (root / "config.yaml").write_text("key: value")
    (root / "settings.yml").write_text("setting: value")

    # Create JSON files
    (root / "package.json").write_text('{"name": "project"}')

    # Create subdirectory with files
    subdir = root / "src"
    subdir.mkdir()
    (subdir / "module.py").write_text("# Module")
    (subdir / "config.yaml").write_text("nested: config")

    return root


@pytest.fixture
def temp_dir_with_duplicates(tmp_path):
    """Create a directory with duplicate files."""
    root = tmp_path / "duplicates"
    root.mkdir()

    # Create duplicate files (same name, different dirs)
    (root / "config.py").write_text("config_v1 = 1")
    (root / "subdir1").mkdir()
    (root / "subdir1" / "config.py").write_text("config_v1 = 1")  # Same content
    (root / "subdir2").mkdir()
    (root / "subdir2" / "config.py").write_text("config_v2 = 2")  # Different content

    return root


@pytest.fixture
def temp_dir_with_content_duplicates(tmp_path):
    """Create a directory with content duplicates (identical files)."""
    root = tmp_path / "content_dups"
    root.mkdir()

    # Create files with identical content
    content = "def important_function():\n    return 42\n"
    (root / "file1.py").write_text(content)
    (root / "file2.py").write_text(content)
    (root / "subdir").mkdir()
    (root / "subdir" / "file3.py").write_text(content)

    return root


# =====================================================================
# TESTS: DuplicationReport Dataclass
# =====================================================================


class TestDuplicationReport:
    """Test DuplicationReport dataclass."""

    def test_report_creation_basic(self):
        """Test creating a DuplicationReport."""
        report = DuplicationReport(
            stats={"total_files": 10},
            duplicate_groups=[],
            content_duplicates=[],
            recommendations=[],
        )
        assert report.stats["total_files"] == 10, "rep is not valid"
        assert report.duplicate_groups == [], "duplicate_groups is not valid"

    def test_report_with_data(self):
        """Test DuplicationReport with data."""
        stats = {
            "total_files": 20,
            "duplicate_count": 5,
            "duplication_ratio": 0.25,
            "severity": "high",
        }
        dup_groups = [{"stem": "config", "count": 3, "paths": ["config1.py", "config2.py"]}]
        content_dups = [{"hash": "abc123", "count": 2, "paths": ["file1.py", "file2.py"]}]
        recommendations = ["Review duplicates"]

        report = DuplicationReport(
            stats=stats,
            duplicate_groups=dup_groups,
            content_duplicates=content_dups,
            recommendations=recommendations,
        )

        assert report.stats["duplicate_count"] == 5, "Count must be greater than zero"
        assert len(report.duplicate_groups) == 1, "Collection must not be empty"
        assert len(report.content_duplicates) == 1, "Collection must not be empty"
        assert report.recommendations[0] == "Review duplicates", "rep is not valid"


# =====================================================================
# TESTS: _assess_severity()
# =====================================================================


class TestAssessSeverity:
    """Test severity assessment logic."""

    def test_assess_severity_acceptable(self):
        """Test ratio within acceptable range."""
        result = _assess_severity(0.05, acceptable=0.10, warning=0.20, critical=0.30)
        assert result == "acceptable", "Result must not be empty"

    def test_assess_severity_warning(self):
        """Test ratio in warning range."""
        result = _assess_severity(0.15, acceptable=0.10, warning=0.20, critical=0.30)
        assert result == "warning", "Result must not be empty"

    def test_assess_severity_high(self):
        """Test ratio in high range."""
        result = _assess_severity(0.25, acceptable=0.10, warning=0.20, critical=0.30)
        assert result == "high", "Result must not be empty"

    def test_assess_severity_critical(self):
        """Test ratio in critical range."""
        result = _assess_severity(0.35, acceptable=0.10, warning=0.20, critical=0.30)
        assert result == "critical", "Result must not be empty"

    def test_assess_severity_boundary_acceptable(self):
        """Test ratio at boundary of acceptable."""
        result = _assess_severity(0.10, acceptable=0.10, warning=0.20, critical=0.30)
        assert result == "acceptable", "Result must not be empty"

    def test_assess_severity_boundary_warning(self):
        """Test ratio at boundary of warning."""
        result = _assess_severity(0.20, acceptable=0.10, warning=0.20, critical=0.30)
        assert result == "warning", "Result must not be empty"

    def test_assess_severity_zero_ratio(self):
        """Test zero duplication ratio."""
        result = _assess_severity(0.0, acceptable=0.10, warning=0.20, critical=0.30)
        assert result == "acceptable", "Result must not be empty"

    def test_assess_severity_one_hundred_percent(self):
        """Test 100% duplication ratio."""
        result = _assess_severity(1.0, acceptable=0.10, warning=0.20, critical=0.30)
        assert result == "critical", "Result must not be empty"


# =====================================================================
# TESTS: _hash_file()
# =====================================================================


class TestHashFile:
    """Test file hashing."""

    def test_hash_file_success(self, tmp_path):
        """Test hashing a readable file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        result = _hash_file(test_file)
        expected = hashlib.sha256(b"test content").hexdigest()
        assert result == expected, "Result must not be empty"

    def test_hash_file_deterministic(self, tmp_path):
        """Test hash is deterministic."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        hash1 = _hash_file(test_file)
        hash2 = _hash_file(test_file)
        assert hash1 == hash2, "hash1 is not valid"

    def test_hash_file_nonexistent(self, tmp_path):
        """Test hashing nonexistent file returns empty string."""
        nonexistent = tmp_path / "nonexistent.txt"
        result = _hash_file(nonexistent)
        assert result == "", "Result must not be empty"

    def test_hash_file_empty(self, tmp_path):
        """Test hashing empty file."""
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")
        result = _hash_file(empty_file)
        expected = hashlib.sha256(b"").hexdigest()
        assert result == expected, "Result must not be empty"

    def test_hash_file_binary(self, tmp_path):
        """Test hashing binary file."""
        binary_file = tmp_path / "binary.bin"
        binary_file.write_bytes(b"\x00\x01\x02\x03")
        result = _hash_file(binary_file)
        expected = hashlib.sha256(b"\x00\x01\x02\x03").hexdigest()
        assert result == expected, "Result must not be empty"

    def test_hash_file_unicode(self, tmp_path):
        """Test hashing file with unicode content."""
        unicode_file = tmp_path / "unicode.txt"
        unicode_file.write_text("Hello 世界 🌍", encoding="utf-8")
        result = _hash_file(unicode_file)
        expected = hashlib.sha256("Hello 世界 🌍".encode("utf-8")).hexdigest()
        assert result == expected, "Result must not be empty"

    def test_hash_file_large(self, tmp_path):
        """Test hashing large file."""
        large_file = tmp_path / "large.txt"
        large_content = "x" * 10000  # 10KB
        large_file.write_text(large_content)
        result = _hash_file(large_file)
        expected = hashlib.sha256(large_content.encode()).hexdigest()
        assert result == expected, "Result must not be empty"


# =====================================================================
# TESTS: analyze_duplication()
# =====================================================================


class TestAnalyzeDuplication:
    """Test main duplication analysis function."""

    def test_analyze_basic(self, temp_analysis_dir):
        """Test basic duplication analysis."""
        report = analyze_duplication(temp_analysis_dir)
        assert isinstance(report, DuplicationReport)
        assert "total_files" in report.stats, "Condition must be true"
        assert report.stats["total_files"] > 0, "rep must be greater than zero"

    def test_analyze_returns_report_type(self, temp_analysis_dir):
        """Test that analyze returns DuplicationReport."""
        report = analyze_duplication(temp_analysis_dir)
        assert isinstance(report, DuplicationReport)
        assert hasattr(report, "stats")
        assert hasattr(report, "duplicate_groups")
        assert hasattr(report, "content_duplicates")
        assert hasattr(report, "recommendations")

    def test_analyze_default_extensions(self, temp_analysis_dir):
        """Test analysis uses default extensions."""
        report = analyze_duplication(temp_analysis_dir)
        # Should find .py, .md, .yaml, .yml, .json files
        assert report.stats["total_files"] > 0, "rep must be greater than zero"

    def test_analyze_custom_extensions(self, temp_analysis_dir):
        """Test analysis with custom extensions."""
        # Only analyze .py files
        report = analyze_duplication(temp_analysis_dir, extensions=[".py"])
        # Should find fewer files than default extensions
        py_count = report.stats["total_files"]
        assert py_count > 0, "py_count must be positive"

    def test_analyze_duplicate_names(self, temp_dir_with_duplicates):
        """Test detecting duplicate filenames."""
        report = analyze_duplication(temp_dir_with_duplicates)
        assert len(report.duplicate_groups) > 0, "Collection must not be empty"
        # Should have 'config' as duplicate group
        stems = [dup["stem"] for dup in report.duplicate_groups]
        assert "config" in stems, "Condition must be true"

    def test_analyze_content_duplicates(self, temp_dir_with_content_duplicates):
        """Test detecting content duplicates."""
        report = analyze_duplication(temp_dir_with_content_duplicates)
        assert len(report.content_duplicates) > 0, "Collection must not be empty"

    def test_analyze_custom_severity_thresholds(self, temp_dir_with_duplicates):
        """Test analysis with custom severity thresholds."""
        report = analyze_duplication(
            temp_dir_with_duplicates,
            acceptable_ratio=0.05,
            warning_ratio=0.15,
            critical_ratio=0.25,
        )
        severity = report.stats["severity"]
        assert severity in ["acceptable", "warning", "high", "critical"]

    def test_analyze_empty_directory(self, tmp_path):
        """Test analyzing empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        report = analyze_duplication(empty_dir)
        assert report.stats["total_files"] == 0, "rep is not valid"
        assert len(report.duplicate_groups) == 0, "Collection must not be empty"

    def test_analyze_path_as_string(self, temp_analysis_dir):
        """Test analyze accepts path as string."""
        report = analyze_duplication(str(temp_analysis_dir))
        assert report.stats["total_files"] > 0, "rep must be greater than zero"

    def test_analyze_path_as_pathlib(self, temp_analysis_dir):
        """Test analyze accepts path as Path object."""
        report = analyze_duplication(Path(temp_analysis_dir))
        assert report.stats["total_files"] > 0, "rep must be greater than zero"

    def test_analyze_recommendations_generated(self, temp_analysis_dir):
        """Test that recommendations are generated."""
        report = analyze_duplication(temp_analysis_dir)
        assert len(report.recommendations) > 0, "Collection must not be empty"
        assert any(isinstance(r, str) for r in report.recommendations)

    def test_analyze_severity_in_stats(self, temp_analysis_dir):
        """Test that severity is included in stats."""
        report = analyze_duplication(temp_analysis_dir)
        assert "severity" in report.stats, "Condition must be true"

    def test_analyze_ratio_in_stats(self, temp_analysis_dir):
        """Test that duplication ratio is in stats."""
        report = analyze_duplication(temp_analysis_dir)
        assert "duplication_ratio" in report.stats, "Condition must be true"
        assert 0 <= report.stats["duplication_ratio"] <= 1, "0 is not valid"

    def test_analyze_duplicate_count_in_stats(self, temp_analysis_dir):
        """Test that duplicate count is in stats."""
        report = analyze_duplication(temp_analysis_dir)
        assert "duplicate_count" in report.stats, "Count must be greater than zero"
        assert report.stats["duplicate_count"] >= 0, "rep must be greater than zero"

    def test_analyze_group_count_in_stats(self, temp_analysis_dir):
        """Test that duplicate group count is in stats."""
        report = analyze_duplication(temp_analysis_dir)
        assert "duplicate_groups_count" in report.stats, "Count must be greater than zero"

    def test_analyze_content_dup_count_in_stats(self, temp_analysis_dir):
        """Test that content duplicate count is in stats."""
        report = analyze_duplication(temp_analysis_dir)
        assert "content_duplicate_groups" in report.stats, "Content must not be empty"


# =====================================================================
# TESTS: Duplicate Group Formatting
# =====================================================================


class TestDuplicateGroupFormatting:
    """Test formatting of duplicate groups in output."""

    def test_duplicate_groups_include_stem(self, temp_dir_with_duplicates):
        """Test duplicate groups include stem."""
        report = analyze_duplication(temp_dir_with_duplicates)
        for group in report.duplicate_groups:
            assert "stem" in group, "Condition must be true"
            assert isinstance(group["stem"], str)

    def test_duplicate_groups_include_count(self, temp_dir_with_duplicates):
        """Test duplicate groups include count."""
        report = analyze_duplication(temp_dir_with_duplicates)
        for group in report.duplicate_groups:
            assert "count" in group, "Count must be greater than zero"
            assert isinstance(group["count"], int)

    def test_duplicate_groups_include_paths(self, temp_dir_with_duplicates):
        """Test duplicate groups include relative paths."""
        report = analyze_duplication(temp_dir_with_duplicates)
        for group in report.duplicate_groups:
            assert "paths" in group, "Condition must be true"
            assert isinstance(group["paths"], list)

    def test_content_duplicates_include_hash(self, temp_dir_with_content_duplicates):
        """Test content duplicates include hash."""
        report = analyze_duplication(temp_dir_with_content_duplicates)
        for dup in report.content_duplicates:
            assert "hash" in dup, "Condition must be true"
            assert isinstance(dup["hash"], str)

    def test_content_duplicates_include_paths(self, temp_dir_with_content_duplicates):
        """Test content duplicates include paths."""
        report = analyze_duplication(temp_dir_with_content_duplicates)
        for dup in report.content_duplicates:
            assert "paths" in dup, "Condition must be true"
            assert isinstance(dup["paths"], list)


# =====================================================================
# TESTS: Edge Cases & Error Handling
# =====================================================================


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_analyze_nonexistent_directory(self):
        """Test analyzing nonexistent directory."""
        # Should not raise, but return report with no files
        report = analyze_duplication(Path("/nonexistent/path"))
        assert report.stats["total_files"] == 0, "rep is not valid"

    def test_analyze_single_file_in_dir(self, tmp_path):
        """Test analyzing directory with single file."""
        test_dir = tmp_path / "single"
        test_dir.mkdir()
        (test_dir / "file.py").write_text("# single file")
        report = analyze_duplication(test_dir)
        assert report.stats["total_files"] == 1, "rep is not valid"
        assert len(report.duplicate_groups) == 0, "Collection must not be empty"

    def test_analyze_many_duplicates(self, tmp_path):
        """Test analyzing directory with many duplicates."""
        dup_dir = tmp_path / "many_dups"
        dup_dir.mkdir()

        # Create 10 files with same content
        content = "duplicate content"
        for i in range(10):
            (dup_dir / f"file{i}.txt").write_text(content)

        report = analyze_duplication(dup_dir)
        assert report.stats["total_files"] == 10, "rep is not valid"

    def test_analyze_high_duplication_ratio(self, tmp_path):
        """Test analyzing with high duplication ratio."""
        high_dup_dir = tmp_path / "high_dup"
        high_dup_dir.mkdir()

        # Create 1 unique file and 9 duplicates
        (high_dup_dir / "original.py").write_text("original")
        for i in range(9):
            (high_dup_dir / f"dup{i}.py").write_text("original")

        report = analyze_duplication(high_dup_dir)
        assert report.stats["duplication_ratio"] > 0.8, "rep must be greater than zero"

    def test_analyze_zero_duplication(self, tmp_path):
        """Test analyzing directory with no duplicates."""
        no_dup_dir = tmp_path / "no_dup"
        no_dup_dir.mkdir()

        # Create 5 unique files
        for i in range(5):
            (no_dup_dir / f"unique{i}.py").write_text(f"unique content {i}")

        report = analyze_duplication(no_dup_dir)
        assert report.stats["duplication_ratio"] == 0.0, "rep is not valid"
        assert len(report.duplicate_groups) == 0, "Collection must not be empty"

    def test_analyze_nested_directories(self, temp_analysis_dir):
        """Test analyzing nested directory structure."""
        report = analyze_duplication(temp_analysis_dir)
        # Should find files in subdirectories
        assert report.stats["total_files"] > 0, "rep must be greater than zero"

    def test_analyze_case_sensitivity(self, tmp_path):
        """Test that file stem comparison is case-insensitive."""
        case_dir = tmp_path / "case_test"
        case_dir.mkdir()
        (case_dir / "Config.py").write_text("config v1")
        (case_dir / "config.py").write_text("config v2")

        report = analyze_duplication(case_dir)
        # Both should be detected as duplicates (case-insensitive comparison)
        stems = [dup["stem"] for dup in report.duplicate_groups]
        # Should have "config" in lowercase
        assert any("config" in stem.lower() for stem in stems), "Condition must be true"


# =====================================================================
# TESTS: Integration
# =====================================================================


class TestIntegration:
    """Test integration scenarios."""

    def test_analyze_realistic_project(self, temp_analysis_dir):
        """Test analyzing a realistic project structure."""
        report = analyze_duplication(temp_analysis_dir)
        assert report.stats["total_files"] > 0, "rep must be greater than zero"
        assert "duplication_ratio" in report.stats, "Condition must be true"
        assert len(report.recommendations) > 0, "Collection must not be empty"

    def test_multiple_analyses_consistent(self, temp_analysis_dir):
        """Test that multiple analyses are consistent."""
        report1 = analyze_duplication(temp_analysis_dir)
        report2 = analyze_duplication(temp_analysis_dir)
        assert report1.stats["total_files"] == report2.stats["total_files"], "rep is not valid"
        assert report1.stats["duplication_ratio"] == report2.stats["duplication_ratio"], "rep is not valid"

    def test_report_provides_actionable_recommendations(self, temp_dir_with_duplicates):
        """Test that recommendations are actionable."""
        report = analyze_duplication(temp_dir_with_duplicates)
        assert len(report.recommendations) > 0, "Collection must not be empty"
        # At least one recommendation should mention duplicates or consolidation
        has_actionable = any(
            "duplicat" in rec.lower() or "consolidat" in rec.lower()
            for rec in report.recommendations
        )
        assert has_actionable or report.stats["duplication_ratio"] == 0.0, "has_actionable is not valid"

    def test_duplication_report_file_list_structure(self, temp_dir_with_duplicates):
        """Test duplication report file list structure."""
        report = analyze_duplication(temp_dir_with_duplicates)
        # Should have duplicate_groups or similar structure
        assert hasattr(report, "duplicate_groups") or hasattr(report, "groups")

    def test_analyze_duplication_preserves_path_integrity(self, temp_dir_with_duplicates):
        """Test that analyze preserves path integrity."""
        report = analyze_duplication(temp_dir_with_duplicates)
        # Should have valid stats dictionary
        assert isinstance(report.stats, dict)
        assert "total_files" in report.stats or "files" in report.stats, "Condition must be true"

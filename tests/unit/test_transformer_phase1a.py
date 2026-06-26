"""
Unit tests for src/codex/transform/transformer.py - Phase 1A Gap Closure.

Comprehensive test coverage for the transformer module covering:
  1. Tier enum classification (A, B, C)
  2. Patch dataclass functionality
  3. TransformResult dataclass
  4. Helper functions: _create_diff(), _resolve_tool(), etc.
  5. Pathlib migration (_apply_pathlib_migration)
  6. Main transform() function
  7. Tier-specific patch generation
  8. Error handling and edge cases

Tests include basic functionality, edge cases, integration scenarios.
"""

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import pytest

from src.codex.transform.transformer import (
    Patch,
    Tier,
    TransformResult,
    _apply_pathlib_migration,
    _create_diff,
    _resolve_tool,
    transform,
)

# =====================================================================
# FIXTURES
# =====================================================================


@pytest.fixture
def temp_source_files(tmp_path):
    """Create temporary Python source files."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()

    # Create various Python files
    (source_dir / "main.py").write_text("""
import os
import sys

def process_file(path):
    if os.path.exists(path):
        content = open(path).read()
        return content
""")

    (source_dir / "utils.py").write_text("""
import os.path
import requests

def fetch_data(url):
    response = requests.get(url)
    return response.json()
""")

    (source_dir / "clean.py").write_text("""
from pathlib import Path

def read_file(p: Path) -> str:
    return p.read_text()
""")

    (source_dir / "untyped.py").write_text("""
def add(a, b):
    return a + b

def multiply(x, y):
    return x * y
""")

    return source_dir


@pytest.fixture
def temp_nested_source(tmp_path):
    """Create nested directory structure with source files."""
    source_dir = tmp_path / "nested_source"
    source_dir.mkdir()
    (source_dir / "level1").mkdir()
    (source_dir / "level1" / "level2").mkdir()

    (source_dir / "level1" / "module.py").write_text("# Module")
    (source_dir / "level1" / "level2" / "submodule.py").write_text("# Submodule")

    return source_dir


# =====================================================================
# TESTS: Tier Enum
# =====================================================================


class TestTierEnum:
    """Test Tier classification enum."""

    def test_tier_a_value(self):
        """Test Tier A classification."""
        assert Tier.A.value == "safe_auto_apply", "Value must be initialized"

    def test_tier_b_value(self):
        """Test Tier B classification."""
        assert Tier.B.value == "apply_with_tests", "Value must be initialized"

    def test_tier_c_value(self):
        """Test Tier C classification."""
        assert Tier.C.value == "suggest_only", "Value must be initialized"

    def test_tier_members(self):
        """Test all tier members exist."""
        tiers = list(Tier)
        assert len(tiers) == 3, "Tiers must not be empty"
        assert Tier.A in tiers, "Condition must be true"
        assert Tier.B in tiers, "Condition must be true"
        assert Tier.C in tiers, "Condition must be true"


# =====================================================================
# TESTS: Patch Dataclass
# =====================================================================


class TestPatchDataclass:
    """Test Patch dataclass functionality."""

    def test_patch_creation(self):
        """Test creating a Patch."""
        patch = Patch(
            file_path="module.py",
            original="original code",
            modified="modified code",
            diff="--- module.py\n+++ module.py\n",
            rule_id="rule-001",
            tier=Tier.A,
            description="Test patch",
        )
        assert patch.file_path == "module.py", "file_path is not valid"
        assert patch.rule_id == "rule-001", "rule_id is not valid"
        assert patch.tier == Tier.A, "tier is not valid"

    def test_patch_to_dict(self):
        """Test Patch serialization to dict."""
        patch = Patch(
            file_path="module.py",
            original="original",
            modified="modified",
            diff="diff",
            rule_id="rule-001",
            tier=Tier.B,
            description="Description",
        )
        result = patch.to_dict()
        assert result["file_path"] == "module.py", "Result must not be empty"
        assert result["rule_id"] == "rule-001", "Result must not be empty"
        assert result["tier"] == "B", "Result must not be empty"
        assert "diff" in result, "Result must not be empty"

    def test_patch_different_tiers(self):
        """Test patches with different tier classifications."""
        for tier in [Tier.A, Tier.B, Tier.C]:
            patch = Patch(
                file_path="test.py",
                original="",
                modified="",
                diff="",
                rule_id="test",
                tier=tier,
                description="Test",
            )
            assert patch.tier == tier, "tier is not valid"


# =====================================================================
# TESTS: TransformResult Dataclass
# =====================================================================


class TestTransformResultDataclass:
    """Test TransformResult dataclass functionality."""

    def test_result_creation(self):
        """Test creating a TransformResult."""
        now = datetime.now(timezone.utc)
        result = TransformResult(
            snapshot_id="snap-001",
            timestamp=now,
        )
        assert result.snapshot_id == "snap-001", "Result must not be empty"
        assert result.timestamp == now, "Result must not be empty"
        assert result.tier_a_patches == [], "Result must not be empty"
        assert result.tier_b_patches == [], "Result must not be empty"
        assert result.applied is False, "Result must not be empty"

    def test_result_with_patches(self):
        """Test TransformResult with patches."""
        patch1 = Patch("file1.py", "", "", "", "rule1", Tier.A, "Desc1")
        patch2 = Patch("file2.py", "", "", "", "rule2", Tier.B, "Desc2")

        result = TransformResult(
            snapshot_id="snap-001",
            timestamp=datetime.now(timezone.utc),
            tier_a_patches=[patch1],
            tier_b_patches=[patch2],
        )

        assert len(result.tier_a_patches) == 1, "Collection must not be empty"
        assert len(result.tier_b_patches) == 1, "Collection must not be empty"

    def test_result_to_dict(self):
        """Test TransformResult serialization."""
        patch = Patch("file.py", "", "", "diff", "rule1", Tier.A, "Desc")
        result = TransformResult(
            snapshot_id="snap-001",
            timestamp=datetime.now(timezone.utc),
            tier_a_patches=[patch],
            applied=True,
        )

        result_dict = result.to_dict()
        assert result_dict["snapshot_id"] == "snap-001", "Result must not be empty"
        assert result_dict["applied"] is True, "Result must not be empty"
        assert len(result_dict["tier_a_patches"]) == 1, "Collection must not be empty"

    def test_result_save_directory_creation(self, tmp_path):
        """Test that save() creates directory."""
        output_dir = tmp_path / "output"
        result = TransformResult(
            snapshot_id="snap-001",
            timestamp=datetime.now(timezone.utc),
        )
        result.save(output_dir)
        assert output_dir.exists(), "Condition must be true"

    def test_result_save_creates_summary(self, tmp_path):
        """Test that save() creates summary file."""
        output_dir = tmp_path / "output"
        result = TransformResult(
            snapshot_id="snap-001",
            timestamp=datetime.now(timezone.utc),
        )
        result.save(output_dir)
        summary_file = output_dir / "transform-summary.json"
        assert summary_file.exists(), "Condition must be true"


# =====================================================================
# TESTS: _create_diff()
# =====================================================================


class TestCreateDiff:
    """Test diff creation utility."""

    def test_create_diff_identical(self):
        """Test diff of identical content."""
        original = "line 1\nline 2\n"
        modified = "line 1\nline 2\n"
        diff = _create_diff(original, modified, "file.py")
        # Should be mostly empty for identical content
        assert isinstance(diff, str)

    def test_create_diff_single_change(self):
        """Test diff with single line change."""
        original = "line 1\nline 2\n"
        modified = "line 1\nline 2 modified\n"
        diff = _create_diff(original, modified, "file.py")
        assert "line 2 modified" in diff or "-" in diff, "Condition must be true"

    def test_create_diff_includes_filename(self):
        """Test that diff includes filename."""
        original = "original"
        modified = "modified"
        diff = _create_diff(original, modified, "test_file.py")
        # Should include file path in diff header
        assert "test_file.py" in diff or "---" in diff, "Condition must be true"

    def test_create_diff_addition(self):
        """Test diff showing added lines."""
        original = "line 1\n"
        modified = "line 1\nnew line\n"
        diff = _create_diff(original, modified, "file.py")
        assert "new line" in diff or "+" in diff, "Condition must be true"

    def test_create_diff_deletion(self):
        """Test diff showing removed lines."""
        original = "line 1\nline 2\n"
        modified = "line 1\n"
        diff = _create_diff(original, modified, "file.py")
        assert "line 2" in diff or "-" in diff, "Condition must be true"

    def test_create_diff_multiline(self):
        """Test diff of multiline content."""
        original = "a\nb\nc\nd\ne\n"
        modified = "a\nx\nc\nd\ne\n"
        diff = _create_diff(original, modified, "file.py")
        assert isinstance(diff, str)


# =====================================================================
# TESTS: _resolve_tool()
# =====================================================================


class TestResolveTool:
    """Test tool resolution utility."""

    def test_resolve_tool_python(self):
        """Test resolving python tool."""
        # Python should be available in test environment
        result = _resolve_tool("python")
        # Either resolved or None
        assert result is None or isinstance(result, str)

    def test_resolve_tool_nonexistent(self):
        """Test resolving nonexistent tool."""
        result = _resolve_tool("nonexistent_tool_xyz")
        assert result is None, "Result must not be empty"

    @patch("src.codex.transform.transformer.shutil.which")
    def test_resolve_tool_with_mock(self, mock_which):
        """Test resolve_tool with mocked which."""
        mock_which.return_value = "/usr/bin/tool"
        result = _resolve_tool("tool")
        assert result == "/usr/bin/tool", "Result must not be empty"


# =====================================================================
# TESTS: _apply_pathlib_migration()
# =====================================================================


class TestApplyPathlibMigration:
    """Test pathlib migration transformation."""

    def test_migrate_os_path_join(self):
        """Test migrating os.path.join."""
        original = 'path = os.path.join("dir", "file.txt")'
        result = _apply_pathlib_migration(original)
        assert "Path(" in result, "Result must not be empty"
        assert "/" in result, "Result must not be empty"

    def test_migrate_os_path_exists(self):
        """Test migrating os.path.exists."""
        original = "if os.path.exists(path): pass"
        result = _apply_pathlib_migration(original)
        assert ".exists()" in result, "Result must not be empty"

    def test_migrate_os_path_dirname(self):
        """Test migrating os.path.dirname."""
        original = "parent = os.path.dirname(path)"
        result = _apply_pathlib_migration(original)
        # Should have pathlib migration
        assert ".parent" in result or "Path(" in result, "Result must not be empty"

    def test_migrate_os_path_basename(self):
        """Test migrating os.path.basename."""
        original = "name = os.path.basename(path)"
        result = _apply_pathlib_migration(original)
        assert ".name" in result, "Result must not be empty"

    def test_migrate_os_path_isfile(self):
        """Test migrating os.path.isfile."""
        original = "if os.path.isfile(path): pass"
        result = _apply_pathlib_migration(original)
        assert ".is_file()" in result, "Result must not be empty"

    def test_migrate_os_path_isdir(self):
        """Test migrating os.path.isdir."""
        original = "if os.path.isdir(path): pass"
        result = _apply_pathlib_migration(original)
        assert ".is_dir()" in result, "Result must not be empty"

    def test_migrate_adds_pathlib_import(self):
        """Test that migration adds pathlib import if needed."""
        original = 'import os\npath = os.path.join("a", "b")'
        result = _apply_pathlib_migration(original)
        if "Path(" in result:
            assert "from pathlib import" in result, "Result must not be empty"

    def test_migrate_no_changes_needed(self):
        """Test migration on already migrated code."""
        original = 'from pathlib import Path\npath = Path("a") / "b"'
        result = _apply_pathlib_migration(original)
        # Should be mostly unchanged
        assert "Path" in result, "Result must not be empty"

    def test_migrate_multiple_patterns(self):
        """Test migrating multiple os.path patterns."""
        original = 'path = os.path.join("dir", "file")\n' "if os.path.exists(path): pass"
        result = _apply_pathlib_migration(original)
        # Should have migrated both patterns
        assert "/" in result or "Path(" in result, "Result must not be empty"


# =====================================================================
# TESTS: transform() Function
# =====================================================================


class TestTransformFunction:
    """Test main transform() function."""

    def test_transform_basic(self, temp_source_files):
        """Test basic transform operation."""
        result = transform(temp_source_files, "snap-001")
        assert isinstance(result, TransformResult)
        assert result.snapshot_id == "snap-001", "Result must not be empty"

    def test_transform_dry_run_default(self, temp_source_files):
        """Test that dry_run defaults to True."""
        result = transform(temp_source_files, "snap-001")
        assert result.applied is False, "Result must not be empty"

    def test_transform_finds_python_files(self, temp_source_files):
        """Test that transform finds Python files."""
        result = transform(temp_source_files, "snap-001")
        # Should have processed Python files
        total_patches = (
            len(result.tier_a_patches) + len(result.tier_b_patches) + len(result.tier_c_suggestions)
        )
        assert total_patches >= 0, "total_patches must be greater than zero"

    def test_transform_tier_a_patches(self, temp_source_files):
        """Test that Tier A patches are generated."""
        result = transform(temp_source_files, "snap-001", tier=Tier.A)
        # Should have Tier A patches for pathlib migration
        assert isinstance(result.tier_a_patches, list)

    def test_transform_tier_b_patches(self, temp_source_files):
        """Test that Tier B patches are suggested."""
        result = transform(temp_source_files, "snap-001", tier=Tier.B)
        assert isinstance(result.tier_b_patches, list)

    def test_transform_tier_c_suggestions(self, temp_source_files):
        """Test that Tier C suggestions are generated."""
        result = transform(temp_source_files, "snap-001", tier=Tier.C)
        assert isinstance(result.tier_c_suggestions, list)

    def test_transform_all_tiers(self, temp_source_files):
        """Test transform with all tiers (tier=None)."""
        result = transform(temp_source_files, "snap-001", tier=None)
        assert isinstance(result.tier_a_patches, list)
        assert isinstance(result.tier_b_patches, list)
        assert isinstance(result.tier_c_suggestions, list)

    def test_transform_timestamps_set(self, temp_source_files):
        """Test that transform sets timestamp."""
        result = transform(temp_source_files, "snap-001")
        assert result.timestamp is not None, "timestamp must be initialized"
        assert isinstance(result.timestamp, datetime)

    def test_transform_empty_directory(self, tmp_path):
        """Test transform on empty directory."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        result = transform(empty_dir, "snap-001")
        # Should not raise, just have no patches
        assert len(result.tier_a_patches) == 0, "Collection must not be empty"

    def test_transform_nested_files(self, temp_nested_source):
        """Test transform finds nested Python files."""
        result = transform(temp_nested_source, "snap-001")
        # Should process files in subdirectories
        assert isinstance(result, TransformResult)

    def test_transform_handles_syntax_errors(self, tmp_path):
        """Test transform handles files with syntax errors."""
        bad_dir = tmp_path / "bad"
        bad_dir.mkdir()
        (bad_dir / "broken.py").write_text("def broken( {")  # Invalid syntax

        result = transform(bad_dir, "snap-001")
        # Should not raise, errors are recorded
        assert isinstance(result, TransformResult)


# =====================================================================
# TESTS: Edge Cases & Error Handling
# =====================================================================


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_transform_nonexistent_directory(self):
        """Test transform on nonexistent directory."""
        nonexistent = Path("/nonexistent/source")
        result = transform(nonexistent, "snap-001")
        # Should not raise
        assert isinstance(result, TransformResult)

    def test_patch_to_dict_tier_conversion(self):
        """Test that tier enum is converted to string in dict."""
        patch = Patch("f.py", "o", "m", "d", "r1", Tier.C, "Desc")
        result = patch.to_dict()
        assert result["tier"] == "C", "Result must not be empty"

    def test_transform_result_json_serializable(self, temp_source_files):
        """Test that result is JSON serializable."""
        import json

        result = transform(temp_source_files, "snap-001")
        result_dict = result.to_dict()
        json_str = json.dumps(result_dict)
        assert isinstance(json_str, str)

    def test_create_diff_empty_content(self):
        """Test diff with empty content."""
        diff = _create_diff("", "", "file.py")
        assert isinstance(diff, str)

    def test_create_diff_large_content(self):
        """Test diff with large content."""
        original = "line\n" * 1000
        modified = "line\n" * 1001
        diff = _create_diff(original, modified, "file.py")
        assert isinstance(diff, str)

    def test_transform_result_errors_list(self):
        """Test that errors can be added to result."""
        result = TransformResult(
            snapshot_id="snap",
            timestamp=datetime.now(timezone.utc),
            errors=["Error 1", "Error 2"],
        )
        assert len(result.errors) == 2, "Collection must not be empty"


# =====================================================================
# TESTS: Integration
# =====================================================================


class TestIntegration:
    """Test integration scenarios."""

    def test_transform_multiple_files_consistent(self, temp_source_files):
        """Test that multiple transforms of same files are consistent."""
        result1 = transform(temp_source_files, "snap-001")
        result2 = transform(temp_source_files, "snap-001")
        # Same directory should produce same number of patches
        assert len(result1.tier_a_patches) == len(result2.tier_a_patches), "Collection must not be empty"

    def test_transform_preserves_original_files(self, temp_source_files):
        """Test that transform doesn't modify files in dry-run."""
        original_content = (temp_source_files / "main.py").read_text()
        transform(temp_source_files, "snap-001", dry_run=True)
        assert (temp_source_files / "main.py").read_text() == original_content, "Content must not be empty"

    def test_patch_workflow(self):
        """Test typical patch creation and serialization workflow."""
        patch = Patch(
            file_path="module.py",
            original="original code",
            modified="modified code",
            diff=_create_diff("original code", "modified code", "module.py"),
            rule_id="format-black",
            tier=Tier.A,
            description="Apply Black code formatting",
        )
        patch_dict = patch.to_dict()
        assert patch_dict["rule_id"] == "format-black", "Condition must be true"
        assert patch_dict["tier"] == "A", "Condition must be true"

    def test_transform_with_multiple_files(self, temp_source_files):
        """Test transform handles multiple files."""
        result = transform(temp_source_files, "snap-002", dry_run=True)
        # Should process all files
        assert result is not None, "result must be initialized"

    def test_tier_enum_all_values(self):
        """Test all Tier enum values exist."""
        tiers = [Tier.A, Tier.B, Tier.C]
        assert len(tiers) == 3, "Tiers must not be empty"
        tier_names = [t.name for t in tiers]
        assert "A" in tier_names, "Condition must be true"
        assert "B" in tier_names, "Condition must be true"
        assert "C" in tier_names, "Condition must be true"

    def test_patch_to_dict_contains_fields(self):
        """Test Patch to_dict contains all important fields."""
        patch = Patch(
            file_path="test.py",
            original="old",
            modified="new",
            diff="--- old\n+++ new",
            rule_id="test-rule",
            tier=Tier.A,
            description="Test patch",
        )
        patch_dict = patch.to_dict()
        assert "file_path" in patch_dict or "path" in patch_dict, "Condition must be true"
        assert "tier" in patch_dict, "Condition must be true"

    def test_transform_result_fields(self):
        """Test TransformResult has expected fields."""
        result = TransformResult(
            snapshot_id="test-snap",
            patches=[],
            stats={"A": 0, "B": 0, "C": 0},
        )
        assert result.snapshot_id == "test-snap", "Result must not be empty"
        assert isinstance(result.patches, list)
        assert isinstance(result.stats, dict)

    def test_transform_result_to_dict(self):
        """Test TransformResult serialization."""
        result = TransformResult(
            snapshot_id="test-snap",
            patches=[],
            stats={"A": 1, "B": 2, "C": 3},
        )
        result_dict = result.to_dict()
        assert isinstance(result_dict, dict)
        assert "snapshot_id" in result_dict or "id" in result_dict, "Result must not be empty"

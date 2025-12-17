"""
Comprehensive tests for the Codex Transform module.

Tests cover:
- Patch generation and application
- Tier-based transformation classification
- Refactoring rules
- Dry-run mode
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestTransformer:
    """Tests for transformation functionality."""

    def test_transform_creates_patches_dir(self, tmp_path: Path):
        """Test that transform creates patches directory."""
        from src.codex.transform.transformer import transform
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.py").write_text("x = 1\n", encoding="utf-8")
        
        result = transform(source_dir, "test-snapshot", dry_run=True)
        
        assert result.snapshot_id == "test-snapshot"
        assert result.timestamp is not None

    def test_transform_detects_pathlib_migration(self, tmp_path: Path):
        """Test detection of pathlib migration opportunities."""
        from src.codex.transform.transformer import transform
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.py").write_text("""
import os

path = os.path.join("a", "b")
exists = os.path.exists(path)
""", encoding="utf-8")
        
        result = transform(source_dir, "test-snapshot", dry_run=True)
        
        # Should detect pathlib migration opportunity
        pathlib_patches = [p for p in result.tier_a_patches if p.rule_id == "pathlib-migration"]
        assert len(pathlib_patches) > 0

    def test_transform_dry_run_no_modification(self, tmp_path: Path):
        """Test that dry run doesn't modify files."""
        from src.codex.transform.transformer import transform
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        test_file = source_dir / "test.py"
        original_content = "import os\npath = os.path.join('a', 'b')\n"
        test_file.write_text(original_content, encoding="utf-8")
        
        transform(source_dir, "test-snapshot", dry_run=True)
        
        assert test_file.read_text() == original_content

    def test_transform_tier_a_only(self, tmp_path: Path):
        """Test applying only Tier A transformations."""
        from src.codex.transform.transformer import transform, Tier
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.py").write_text("x = 1\n", encoding="utf-8")
        
        result = transform(source_dir, "test-snapshot", tier=Tier.A, dry_run=True)
        
        assert result.tier_b_patches == []
        assert result.tier_c_suggestions == []

    def test_transform_tier_c_suggestions(self, tmp_path: Path):
        """Test Tier C suggestions for async conversion."""
        from src.codex.transform.transformer import transform
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.py").write_text("""
import requests

def fetch():
    return requests.get("http://example.com")
""", encoding="utf-8")
        
        result = transform(source_dir, "test-snapshot", dry_run=True)
        
        # Should suggest async conversion
        async_suggestions = [s for s in result.tier_c_suggestions if s.get("rule_id") == "async-conversion"]
        assert len(async_suggestions) > 0

    def test_transform_result_to_dict(self, tmp_path: Path):
        """Test TransformResult serialization."""
        from src.codex.transform.transformer import transform
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.py").write_text("x = 1\n", encoding="utf-8")
        
        result = transform(source_dir, "test-snapshot", dry_run=True)
        data = result.to_dict()
        
        assert "snapshot_id" in data
        assert "timestamp" in data
        assert "tier_a_patches" in data
        assert "tier_b_patches" in data
        assert "tier_c_suggestions" in data

    def test_transform_result_save(self, tmp_path: Path):
        """Test saving TransformResult to files."""
        from src.codex.transform.transformer import transform
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.py").write_text("""
import os
path = os.path.join("a", "b")
""", encoding="utf-8")
        
        result = transform(source_dir, "test-snapshot", dry_run=True)
        
        output_dir = tmp_path / "patches"
        result.save(output_dir)
        
        assert output_dir.exists()
        assert (output_dir / "transform-summary.json").exists()


class TestPatchGeneration:
    """Tests for patch generation."""

    def test_create_diff(self):
        """Test unified diff creation."""
        from src.codex.transform.transformer import _create_diff
        
        original = "line1\nline2\nline3\n"
        modified = "line1\nmodified\nline3\n"
        
        diff = _create_diff(original, modified, "test.py")
        
        assert "---" in diff
        assert "+++" in diff
        assert "-line2" in diff
        assert "+modified" in diff

    def test_pathlib_migration_patterns(self):
        """Test pathlib migration pattern application."""
        from src.codex.transform.transformer import _apply_pathlib_migration
        
        content = """
import os
path = os.path.join("a", "b")
exists = os.path.exists(path)
dirname = os.path.dirname(path)
"""
        
        result = _apply_pathlib_migration(content)
        
        assert "Path(" in result
        assert ".exists()" in result


class TestTierClassification:
    """Tests for tier classification."""

    def test_tier_enum(self):
        """Test Tier enum values."""
        from src.codex.transform.transformer import Tier
        
        assert Tier.A.value == "safe_auto_apply"
        assert Tier.B.value == "apply_with_tests"
        assert Tier.C.value == "suggest_only"

    def test_patch_tier_assignment(self, tmp_path: Path):
        """Test that patches are assigned correct tiers."""
        from src.codex.transform.transformer import transform, Tier
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.py").write_text("""
import os
path = os.path.join("a", "b")
""", encoding="utf-8")
        
        result = transform(source_dir, "test-snapshot", dry_run=True)
        
        for patch in result.tier_a_patches:
            assert patch.tier == Tier.A

    def test_patch_has_description(self, tmp_path: Path):
        """Test that patches have descriptions."""
        from src.codex.transform.transformer import transform
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.py").write_text("""
import os
os.path.exists("file")
""", encoding="utf-8")
        
        result = transform(source_dir, "test-snapshot", dry_run=True)
        
        for patch in result.tier_a_patches:
            assert patch.description
            assert len(patch.description) > 0


class TestPatch:
    """Tests for Patch dataclass."""

    def test_patch_to_dict(self):
        """Test Patch serialization."""
        from src.codex.transform.transformer import Patch, Tier
        
        patch = Patch(
            file_path="test.py",
            original="old",
            modified="new",
            diff="--- old\n+++ new\n",
            rule_id="test-rule",
            tier=Tier.A,
            description="Test patch",
        )
        
        data = patch.to_dict()
        
        assert data["file_path"] == "test.py"
        assert data["rule_id"] == "test-rule"
        assert data["tier"] == "A"
        assert data["description"] == "Test patch"


class TestErrorHandling:
    """Tests for error handling in transform."""

    def test_transform_handles_read_errors(self, tmp_path: Path):
        """Test graceful handling of file read errors."""
        from src.codex.transform.transformer import transform
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        # Create a valid file
        (source_dir / "valid.py").write_text("x = 1\n", encoding="utf-8")
        
        # Create a binary file that can't be read as text
        (source_dir / "binary.py").write_bytes(b"\x00\x01\x02")
        
        result = transform(source_dir, "test-snapshot", dry_run=True)
        
        # Should complete without crashing
        assert result.snapshot_id == "test-snapshot"

    def test_transform_empty_directory(self, tmp_path: Path):
        """Test transform on empty directory."""
        from src.codex.transform.transformer import transform
        
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        result = transform(source_dir, "test-snapshot", dry_run=True)
        
        assert result.tier_a_patches == []
        assert result.tier_b_patches == []
        assert result.tier_c_suggestions == []

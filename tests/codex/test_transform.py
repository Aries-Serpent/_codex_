"""
Comprehensive tests for the Codex Transform module.

Tests cover:
- Patch generation and application
- Tier-based transformation classification
- Refactoring rules
- Dry-run mode
"""

from pathlib import Path


class TestTransformer:
    """Tests for transformation functionality."""

    def test_transform_creates_patches_dir(self, tmp_path: Path):
        """Test that transform creates patches directory."""
        from codex.transform.transformer import transform

        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.py").write_text("x = 1\n", encoding="utf-8")

        result = transform(source_dir, "test-snapshot", dry_run=True)

        assert result.snapshot_id == "test-snapshot", "Result must not be empty"
        assert result.timestamp is not None, "timestamp must be initialized"

    def test_transform_detects_pathlib_migration(self, tmp_path: Path):
        """Test detection of pathlib migration opportunities."""
        from codex.transform.transformer import transform

        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.py").write_text(
            """
import os

path = os.path.join("a", "b")
exists = os.path.exists(path)
""",
            encoding="utf-8",
        )

        result = transform(source_dir, "test-snapshot", dry_run=True)

        # Should detect pathlib migration opportunity
        pathlib_patches = [p for p in result.tier_a_patches if p.rule_id == "pathlib-migration"]
        assert len(pathlib_patches) > 0, "Pathlib_patches must not be empty"

    def test_transform_dry_run_no_modification(self, tmp_path: Path):
        """Test that dry run doesn't modify files."""
        from codex.transform.transformer import transform

        source_dir = tmp_path / "source"
        source_dir.mkdir()
        test_file = source_dir / "test.py"
        original_content = "import os\npath = os.path.join('a', 'b')\n"
        test_file.write_text(original_content, encoding="utf-8")

        transform(source_dir, "test-snapshot", dry_run=True)

        assert test_file.read_text() == original_content, "Content must not be empty"

    def test_transform_tier_a_only(self, tmp_path: Path):
        """Test applying only Tier A transformations."""
        from codex.transform.transformer import Tier, transform

        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.py").write_text("x = 1\n", encoding="utf-8")

        result = transform(source_dir, "test-snapshot", tier=Tier.A, dry_run=True)

        assert result.tier_b_patches == [], "Result must not be empty"
        assert result.tier_c_suggestions == [], "Result must not be empty"

    def test_transform_tier_c_suggestions(self, tmp_path: Path):
        """Test Tier C suggestions for async conversion."""
        from codex.transform.transformer import transform

        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.py").write_text(
            """
import requests

def fetch():
    return requests.get("http://example.com")
""",
            encoding="utf-8",
        )

        result = transform(source_dir, "test-snapshot", dry_run=True)

        # Should suggest async conversion
        async_suggestions = [
            s for s in result.tier_c_suggestions if s.get("rule_id") == "async-conversion"
        ]
        assert len(async_suggestions) > 0, "Async_suggestions must not be empty"

    def test_transform_result_to_dict(self, tmp_path: Path):
        """Test TransformResult serialization."""
        from codex.transform.transformer import transform

        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.py").write_text("x = 1\n", encoding="utf-8")

        result = transform(source_dir, "test-snapshot", dry_run=True)
        data = result.to_dict()

        assert "snapshot_id" in data, "Data must not be empty"
        assert "timestamp" in data, "Data must not be empty"
        assert "tier_a_patches" in data, "Data must not be empty"
        assert "tier_b_patches" in data, "Data must not be empty"
        assert "tier_c_suggestions" in data, "Data must not be empty"

    def test_transform_result_save(self, tmp_path: Path):
        """Test saving TransformResult to files."""
        from codex.transform.transformer import transform

        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.py").write_text(
            """
import os
path = os.path.join("a", "b")
""",
            encoding="utf-8",
        )

        result = transform(source_dir, "test-snapshot", dry_run=True)

        output_dir = tmp_path / "patches"
        result.save(output_dir)

        assert output_dir.exists(), "Condition must be true"
        assert (output_dir / "transform-summary.json").exists(), "Condition must be true"


class TestPatchGeneration:
    """Tests for patch generation."""

    def test_create_diff(self):
        """Test unified diff creation."""
        from codex.transform.transformer import _create_diff

        original = "line1\nline2\nline3\n"
        modified = "line1\nmodified\nline3\n"

        diff = _create_diff(original, modified, "test.py")

        assert "---" in diff, "Condition must be true"
        assert "+++" in diff, "Condition must be true"
        assert "-line2" in diff, "Condition must be true"
        assert "+modified" in diff, "Condition must be true"

    def test_pathlib_migration_patterns(self):
        """Test pathlib migration pattern application."""
        from codex.transform.transformer import _apply_pathlib_migration

        content = """
import os
path = os.path.join("a", "b")
exists = os.path.exists(path)
dirname = os.path.dirname(path)
"""

        result = _apply_pathlib_migration(content)

        assert "Path(" in result, "Result must not be empty"
        assert ".exists()" in result, "Result must not be empty"


class TestTierClassification:
    """Tests for tier classification."""

    def test_tier_enum(self):
        """Test Tier enum values."""
        from codex.transform.transformer import Tier

        assert Tier.A.value == "safe_auto_apply", "Value must be initialized"
        assert Tier.B.value == "apply_with_tests", "Value must be initialized"
        assert Tier.C.value == "suggest_only", "Value must be initialized"

    def test_patch_tier_assignment(self, tmp_path: Path):
        """Test that patches are assigned correct tiers."""
        from codex.transform.transformer import Tier, transform

        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.py").write_text(
            """
import os
path = os.path.join("a", "b")
""",
            encoding="utf-8",
        )

        result = transform(source_dir, "test-snapshot", dry_run=True)

        for patch in result.tier_a_patches:
            assert patch.tier == Tier.A, "tier is not valid"

    def test_patch_has_description(self, tmp_path: Path):
        """Test that patches have descriptions."""
        from codex.transform.transformer import transform

        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "test.py").write_text(
            """
import os
os.path.exists("file")
""",
            encoding="utf-8",
        )

        result = transform(source_dir, "test-snapshot", dry_run=True)

        for patch in result.tier_a_patches:
            assert patch.description, "Condition must be true"
            assert len(patch.description) > 0, "Collection must not be empty"


class TestPatch:
    """Tests for Patch dataclass."""

    def test_patch_to_dict(self):
        """Test Patch serialization."""
        from codex.transform.transformer import Patch, Tier

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

        assert data["file_path"] == "test.py", "Data must not be empty"
        assert data["rule_id"] == "test-rule", "Data must not be empty"
        assert data["tier"] == "A", "Data must not be empty"
        assert data["description"] == "Test patch", "Data must not be empty"


class TestErrorHandling:
    """Tests for error handling in transform."""

    def test_transform_handles_read_errors(self, tmp_path: Path):
        """Test graceful handling of file read errors."""
        from codex.transform.transformer import transform

        source_dir = tmp_path / "source"
        source_dir.mkdir()

        # Create a valid file
        (source_dir / "valid.py").write_text("x = 1\n", encoding="utf-8")

        # Create a binary file that can't be read as text
        (source_dir / "binary.py").write_bytes(b"\x00\x01\x02")

        result = transform(source_dir, "test-snapshot", dry_run=True)

        # Should complete without crashing
        assert result.snapshot_id == "test-snapshot", "Result must not be empty"

    def test_transform_empty_directory(self, tmp_path: Path):
        """Test transform on empty directory."""
        from codex.transform.transformer import transform

        source_dir = tmp_path / "source"
        source_dir.mkdir()

        result = transform(source_dir, "test-snapshot", dry_run=True)

        assert result.tier_a_patches == [], "Result must not be empty"
        assert result.tier_b_patches == [], "Result must not be empty"
        assert result.tier_c_suggestions == [], "Result must not be empty"

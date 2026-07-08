"""Gap-fill tests for skills.loader module."""

import tempfile
from pathlib import Path

import pytest

from codex.skills.loader import SkillDocLoader, _split_frontmatter


class TestSplitFrontmatter:
    """Tests for _split_frontmatter() function."""

    def test_valid_frontmatter_and_body(self):
        """Should extract YAML frontmatter and body correctly."""
        content = """---
name: test_skill
description: A test skill
---
# Body content
This is the body."""

        frontmatter, body = _split_frontmatter(content)

        assert frontmatter["name"] == "test_skill", "Condition must be true"
        assert frontmatter["description"] == "A test skill", "Condition must be true"
        assert "Body content" in body, "Content must not be empty"

    def test_no_frontmatter(self):
        """Should return empty dict and original content when no frontmatter."""
        content = "Just body content\nNo frontmatter here"

        frontmatter, body = _split_frontmatter(content)

        assert frontmatter == {}, "frontmatter is not valid"
        assert body == content, "Content must not be empty"

    def test_empty_frontmatter(self):
        """Should handle empty frontmatter gracefully."""
        content = """---
---
Body content"""

        frontmatter, body = _split_frontmatter(content)

        assert frontmatter == {}, "frontmatter is not valid"
        assert "Body content" in body, "Content must not be empty"

    def test_invalid_yaml_frontmatter(self):
        """Should handle invalid YAML gracefully."""
        content = """---
invalid: yaml: content:
---
Body content"""

        frontmatter, body = _split_frontmatter(content)

        # Should return empty dict on parse error
        assert frontmatter == {}, "frontmatter is not valid"
        assert "Body content" in body, "Content must not be empty"

    def test_frontmatter_not_dict(self):
        """Should handle frontmatter that's not a mapping."""
        content = """---
- item1
- item2
---
Body content"""

        frontmatter, body = _split_frontmatter(content)

        # Should return empty dict when not a mapping
        assert frontmatter == {}, "frontmatter is not valid"

    def test_complex_yaml_frontmatter(self):
        """Should handle complex YAML structures."""
        content = """---
name: skill
tags:
  - tag1
  - tag2
config:
  timeout: 100
---
Body"""

        frontmatter, body = _split_frontmatter(content)

        assert frontmatter["name"] == "skill", "Condition must be true"
        assert "tag1" in frontmatter["tags"], "Condition must be true"
        assert frontmatter["config"]["timeout"] == 100, "Condition must be true"


class TestSkillDocLoader:
    """Tests for SkillDocLoader class."""

    def test_load_manifest_from_file(self):
        """Should load manifest from markdown file with frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "test_skill.md"
            md_file.write_text("""---
name: test_skill
title: Test Skill
description: A test skill for validation
capabilities:
  - skill.test
enforcement_tier: ADVISORY
---
# Test Skill

This is a test skill.""")

            loader = SkillDocLoader()
            manifest = loader.load_manifest(md_file)

            assert manifest.name == "test_skill", "name is not valid"
            assert manifest.description == "A test skill for validation", "description is not valid"
            assert "skill.test" in manifest.capability_tags, "Condition must be true"
            assert manifest.enforcement_tier == "ADVISORY", "enforcement_tier is not valid"
            assert manifest.doc_path == str(md_file), "doc_path is not valid"

    def test_load_manifest_with_title_fallback(self):
        """Should use title as fallback when name is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "skill.md"
            md_file.write_text("""---
title: My Title
---
Content""")

            loader = SkillDocLoader()
            manifest = loader.load_manifest(md_file)

            assert manifest.name == "My Title", "name is not valid"

    def test_load_manifest_with_filename_fallback(self):
        """Should use filename as fallback when name/title missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "default_name.md"
            md_file.write_text("""---
description: A skill
---
Content""")

            loader = SkillDocLoader()
            manifest = loader.load_manifest(md_file)

            assert manifest.name == "default_name", "name is not valid"

    def test_load_manifest_with_metadata(self):
        """Should preserve custom metadata fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "skill.md"
            md_file.write_text("""---
name: skill
custom_field: custom_value
another_field: 123
---
Content""")

            loader = SkillDocLoader()
            manifest = loader.load_manifest(md_file)

            assert manifest.metadata["custom_field"] == "custom_value", "Data must not be empty"
            assert manifest.metadata["another_field"] == 123, "Data must not be empty"

    def test_load_manifest_with_budget_and_timeout(self):
        """Should load budget_tokens and timeout_ms."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "skill.md"
            md_file.write_text("""---
name: skill
budget_tokens: 5000
timeout_ms: 10000
---
Content""")

            loader = SkillDocLoader()
            manifest = loader.load_manifest(md_file)

            assert manifest.budget_tokens == 5000, "budget_tokens is not valid"
            assert manifest.timeout_ms == 10000, "timeout_ms is not valid"

    def test_load_manifest_nonexistent_file(self):
        """Should raise FileNotFoundError for nonexistent file."""
        loader = SkillDocLoader()

        with pytest.raises(FileNotFoundError):
            loader.load_manifest("/nonexistent/path/skill.md")

    def test_load_many_manifests(self):
        """Should load multiple manifests from multiple files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create multiple skill files
            for i in range(3):
                md_file = tmpdir_path / f"skill{i}.md"
                md_file.write_text(f"""---
name: skill_{i}
description: Skill {i}
---
Content {i}""")

            loader = SkillDocLoader()
            paths = [tmpdir_path / f"skill{i}.md" for i in range(3)]
            manifests = loader.load_many(paths)

            assert len(manifests) == 3, "Manifests must not be empty"
            assert manifests[0].name == "skill_0", "name is not valid"
            assert manifests[1].name == "skill_1", "name is not valid"
            assert manifests[2].name == "skill_2", "name is not valid"

    def test_load_many_with_missing_file(self):
        """Should skip missing files and continue loading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create one valid file
            md_file = tmpdir_path / "skill.md"
            md_file.write_text("""---
name: skill
---
Content""")

            loader = SkillDocLoader()
            paths = [
                md_file,
                tmpdir_path / "nonexistent.md",  # This file doesn't exist
            ]
            manifests = loader.load_many(paths)

            # Should still load the valid file
            assert len(manifests) == 1, "Manifests must not be empty"
            assert manifests[0].name == "skill", "name is not valid"

    def test_load_many_with_invalid_yaml(self):
        """Should load files with invalid YAML with defaults."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create valid file
            valid_file = tmpdir_path / "valid.md"
            valid_file.write_text("""---
name: valid_skill
---
Content""")

            # Create invalid file
            invalid_file = tmpdir_path / "invalid.md"
            invalid_file.write_text("""---
invalid: yaml: content:
---
Content""")

            loader = SkillDocLoader()
            paths = [valid_file, invalid_file]
            manifests = loader.load_many(paths)

            # Both files should be loaded (invalid one gets defaults from filename)
            assert len(manifests) == 2, "Manifests must not be empty"
            assert manifests[0].name == "valid_skill", "name is not valid"
            # Invalid file gets name from filename (stem)
            assert "invalid" in manifests[1].name.lower(), "Condition must be true"

    def test_load_manifest_with_integration_points(self):
        """Should load integration_points from manifest."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            md_file = tmpdir_path / "skill.md"
            md_file.write_text("""---
name: skill
integration_points:
  - point1
  - point2
---
Content""")

            loader = SkillDocLoader()
            manifest = loader.load_manifest(md_file)

            assert len(manifest.integration_points) == 2, "Collection must not be empty"
            assert "point1" in manifest.integration_points, "Condition must be true"

    def test_load_manifest_capability_tags_variants(self):
        """Should support both 'capabilities' and 'capability_tags' keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Test with 'capabilities' key
            md_file1 = tmpdir_path / "skill1.md"
            md_file1.write_text("""---
name: skill1
capabilities:
  - tag1
---
Content""")

            # Test with 'capability_tags' key
            md_file2 = tmpdir_path / "skill2.md"
            md_file2.write_text("""---
name: skill2
capability_tags:
  - tag2
---
Content""")

            loader = SkillDocLoader()
            m1 = loader.load_manifest(md_file1)
            m2 = loader.load_manifest(md_file2)

            assert "tag1" in m1.capability_tags, "Condition must be true"
            assert "tag2" in m2.capability_tags, "Condition must be true"

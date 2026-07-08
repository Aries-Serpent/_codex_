"""Gap-fill tests for skills.doc_loader module."""

import tempfile
from pathlib import Path

from codex.skills.doc_loader import (
    _extract_frontmatter,
    _frontmatter_to_manifest,
    _repo_root,
    load_agent_docs_as_skills,
)


class TestRepoRoot:
    """Tests for _repo_root() function."""

    def test_repo_root_returns_path(self):
        """_repo_root should return a Path object."""
        root = _repo_root()
        assert isinstance(root, Path)
        assert root.exists(), "Condition must be true"

    def test_repo_root_contains_pyproject(self):
        """_repo_root should return directory containing pyproject.toml."""
        root = _repo_root()
        # Should contain pyproject.toml
        assert (root / "pyproject.toml").exists(), "Condition must be true"


class TestExtractFrontmatter:
    """Tests for _extract_frontmatter() function."""

    def test_extract_valid_frontmatter(self):
        """Should extract valid YAML frontmatter."""
        content = """---
name: Test Agent
description: A test agent
capabilities:
  - test
---
# Body"""

        result = _extract_frontmatter(content)

        assert result["name"] == "Test Agent", "Result must not be empty"
        assert result["description"] == "A test agent", "Result must not be empty"
        assert "test" in result["capabilities"], "Result must not be empty"

    def test_no_frontmatter(self):
        """Should return empty dict when no frontmatter."""
        content = "# Just body\nNo frontmatter"

        result = _extract_frontmatter(content)

        assert result == {}, "Result must not be empty"

    def test_invalid_yaml(self):
        """Should return empty dict on invalid YAML."""
        content = """---
invalid: yaml: content:
---
Body"""

        result = _extract_frontmatter(content)

        assert result == {}, "Result must not be empty"

    def test_empty_frontmatter(self):
        """Should handle empty frontmatter gracefully."""
        content = """---
---
Body"""

        result = _extract_frontmatter(content)

        # Empty YAML returns None, which becomes {}
        assert result == {}, "Result must not be empty"

    def test_complex_frontmatter(self):
        """Should handle complex YAML structures."""
        content = """---
name: Skill
tags:
  - tag1
  - tag2
config:
  timeout: 100
  budget: 5000
---
Body"""

        result = _extract_frontmatter(content)

        assert result["name"] == "Skill", "Result must not be empty"
        assert len(result["tags"]) == 2, "Collection must not be empty"
        assert result["config"]["timeout"] == 100, "Result must not be empty"


class TestFrontmatterToManifest:
    """Tests for _frontmatter_to_manifest() function."""

    def test_basic_frontmatter_conversion(self):
        """Should convert basic frontmatter to manifest."""
        fm = {
            "name": "Test Skill",
            "description": "A test skill",
            "capabilities": ["test.skill"],
        }

        manifest = _frontmatter_to_manifest(fm, doc_path=".github/agents/test.md", text="# Test")

        assert manifest is not None, "manifest must be initialized"
        assert manifest.name == "Test Skill", "name is not valid"
        assert manifest.description == "A test skill", "description is not valid"
        assert "test.skill" in manifest.capability_tags, "Condition must be true"

    def test_name_from_file_stem(self):
        """Should derive name from file stem if not provided."""
        fm = {"description": "A skill"}

        manifest = _frontmatter_to_manifest(
            fm, doc_path=".github/agents/my-skill.md", text="# Skill"
        )

        assert manifest is not None, "manifest must be initialized"
        assert manifest.name == "My Skill", "name is not valid"

    def test_capability_tags_variants(self):
        """Should support multiple capability tag keys."""
        # Test with capability_tags
        fm1 = {"capability_tags": ["tag1", "tag2"]}
        m1 = _frontmatter_to_manifest(fm1, doc_path=".github/agents/s1.md", text="# S1")
        assert "tag1" in m1.capability_tags, "Condition must be true"

        # Test with capabilities
        fm2 = {"capabilities": ["tag3"]}
        m2 = _frontmatter_to_manifest(fm2, doc_path=".github/agents/s2.md", text="# S2")
        assert "tag3" in m2.capability_tags, "Condition must be true"

        # Test with capability (singular)
        fm3 = {"capability": "tag4,tag5"}
        m3 = _frontmatter_to_manifest(fm3, doc_path=".github/agents/s3.md", text="# S3")
        assert "tag4" in m3.capability_tags, "Condition must be true"
        assert "tag5" in m3.capability_tags, "Condition must be true"

    def test_skill_id_generation(self):
        """Should generate skill_id from doc_path if not provided."""
        fm = {}

        manifest = _frontmatter_to_manifest(
            fm, doc_path=".github/agents/my-test-skill.md", text="# Skill"
        )

        assert manifest is not None, "manifest must be initialized"
        assert manifest.id == "agent.my_test_skill", "id is not valid"

    def test_custom_skill_id(self):
        """Should use provided skill_id."""
        fm = {"id": "custom.id"}

        manifest = _frontmatter_to_manifest(fm, doc_path=".github/agents/skill.md", text="# Skill")

        assert manifest is not None, "manifest must be initialized"
        assert manifest.id == "custom.id", "id is not valid"

    def test_version_default(self):
        """Should default to version 1.0.0."""
        fm = {}

        manifest = _frontmatter_to_manifest(fm, doc_path=".github/agents/skill.md", text="# Skill")

        assert manifest is not None, "manifest must be initialized"
        assert manifest.version == "1.0.0", "version is not valid"

    def test_custom_version(self):
        """Should use provided version."""
        fm = {"version": "2.5.0"}

        manifest = _frontmatter_to_manifest(fm, doc_path=".github/agents/skill.md", text="# Skill")

        assert manifest is not None, "manifest must be initialized"
        assert manifest.version == "2.5.0", "version is not valid"

    def test_risk_tier_inference_d_capable(self):
        """Should infer high risk for D_CAPABLE autonomy model."""
        fm = {"autonomy_model": "D_CAPABLE"}

        manifest = _frontmatter_to_manifest(fm, doc_path=".github/agents/skill.md", text="# Skill")

        assert manifest is not None, "manifest must be initialized"
        assert manifest.policy.risk_tier == "high", "risk_tier is not valid"

    def test_risk_tier_inference_grounded(self):
        """Should infer high risk for GROUNDED enforcement."""
        fm = {"enforcement_tier": "GROUNDED"}

        manifest = _frontmatter_to_manifest(fm, doc_path=".github/agents/skill.md", text="# Skill")

        assert manifest is not None, "manifest must be initialized"
        assert manifest.policy.risk_tier == "high", "risk_tier is not valid"

    def test_risk_tier_inference_partial(self):
        """Should infer medium risk for PARTIAL enforcement."""
        fm = {"enforcement_tier": "PARTIAL"}

        manifest = _frontmatter_to_manifest(fm, doc_path=".github/agents/skill.md", text="# Skill")

        assert manifest is not None, "manifest must be initialized"
        assert manifest.policy.risk_tier == "medium", "risk_tier is not valid"

    def test_entrypoint_from_integration_points(self):
        """Should derive entrypoint from integration_points."""
        fm = {"integration_points": ["scripts/my_skill.py"]}

        manifest = _frontmatter_to_manifest(fm, doc_path=".github/agents/skill.md", text="# Skill")

        assert manifest is not None, "manifest must be initialized"
        assert "scripts.my_skill:run" in manifest.entrypoint, "Condition must be true"

    def test_doc_hash_generation(self):
        """Should generate doc hash from text content."""
        text = "# Test Skill\n\nThis is test content."
        fm = {}

        manifest = _frontmatter_to_manifest(fm, doc_path=".github/agents/skill.md", text=text)

        assert manifest is not None, "manifest must be initialized"
        assert manifest.doc.hash is not None, "hash must be initialized"
        assert len(manifest.doc.hash) == 16, "Collection must not be empty"


class TestLoadAgentDocsAsSkills:
    """Tests for load_agent_docs_as_skills() function."""

    def test_load_from_valid_directory(self):
        """Should load skills from valid agent docs directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            agents_dir = tmpdir_path / ".github" / "agents"
            agents_dir.mkdir(parents=True)

            # Create test agent doc
            agent_file = agents_dir / "test_agent.md"
            agent_file.write_text("""---
name: Test Agent
description: A test agent
capabilities:
  - test.skill
---
# Test Agent

This is a test agent.""")

            skills = load_agent_docs_as_skills(agents_root=agents_dir)

            assert len(skills) > 0, "Skills must not be empty"
            assert skills[0].manifest.name == "Test Agent", "name is not valid"
            assert "test.skill" in skills[0].manifest.capability_tags, "Condition must be true"

    def test_load_multiple_agent_docs(self):
        """Should load multiple agent doc files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            agents_dir = tmpdir_path / ".github" / "agents"
            agents_dir.mkdir(parents=True)

            # Create multiple agent docs
            for i in range(3):
                agent_file = agents_dir / f"agent_{i}.md"
                agent_file.write_text(f"""---
name: Agent {i}
capabilities:
  - skill.{i}
---
Content {i}""")

            skills = load_agent_docs_as_skills(agents_root=agents_dir)

            assert len(skills) == 3, "Skills must not be empty"

    def test_nonexistent_directory(self):
        """Should return empty list for nonexistent directory."""
        skills = load_agent_docs_as_skills(agents_root=Path("/nonexistent/path"))

        assert skills == [], "skills is not valid"

    def test_skip_invalid_markdown(self):
        """Should skip markdown files without valid frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            agents_dir = tmpdir_path / ".github" / "agents"
            agents_dir.mkdir(parents=True)

            # Create valid agent doc
            valid_file = agents_dir / "valid.md"
            valid_file.write_text("""---
name: Valid Agent
---
Content""")

            # Create invalid agent doc
            invalid_file = agents_dir / "invalid.md"
            invalid_file.write_text("# No frontmatter\nJust content")

            skills = load_agent_docs_as_skills(agents_root=agents_dir)

            # Should only load the valid one
            assert len(skills) == 1, "Skills must not be empty"

    def test_registered_skill_has_source_path(self):
        """Should include source_path in RegisteredSkill."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            agents_dir = tmpdir_path / ".github" / "agents"
            agents_dir.mkdir(parents=True)

            agent_file = agents_dir / "test.md"
            agent_file.write_text("""---
name: Test
---
Content""")

            skills = load_agent_docs_as_skills(agents_root=agents_dir)

            assert len(skills) > 0, "Skills must not be empty"
            assert skills[0].source_path == str(agent_file), "source_path is not valid"

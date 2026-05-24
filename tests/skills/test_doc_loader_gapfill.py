"""Gap-fill tests for skills.doc_loader module."""

import tempfile
from pathlib import Path

import pytest

from codex.skills.doc_loader import (
    _extract_frontmatter,
    _frontmatter_to_manifest,
    load_agent_docs_as_skills,
    _repo_root,
)


class TestRepoRoot:
    """Tests for _repo_root() function."""

    def test_repo_root_returns_path(self):
        """_repo_root should return a Path object."""
        root = _repo_root()
        assert isinstance(root, Path)
        assert root.exists()

    def test_repo_root_contains_pyproject(self):
        """_repo_root should return directory containing pyproject.toml."""
        root = _repo_root()
        # Should contain pyproject.toml
        assert (root / "pyproject.toml").exists()


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
        
        assert result["name"] == "Test Agent"
        assert result["description"] == "A test agent"
        assert "test" in result["capabilities"]

    def test_no_frontmatter(self):
        """Should return empty dict when no frontmatter."""
        content = "# Just body\nNo frontmatter"
        
        result = _extract_frontmatter(content)
        
        assert result == {}

    def test_invalid_yaml(self):
        """Should return empty dict on invalid YAML."""
        content = """---
invalid: yaml: content:
---
Body"""
        
        result = _extract_frontmatter(content)
        
        assert result == {}

    def test_empty_frontmatter(self):
        """Should handle empty frontmatter gracefully."""
        content = """---
---
Body"""
        
        result = _extract_frontmatter(content)
        
        # Empty YAML returns None, which becomes {}
        assert result == {}

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
        
        assert result["name"] == "Skill"
        assert len(result["tags"]) == 2
        assert result["config"]["timeout"] == 100


class TestFrontmatterToManifest:
    """Tests for _frontmatter_to_manifest() function."""

    def test_basic_frontmatter_conversion(self):
        """Should convert basic frontmatter to manifest."""
        fm = {
            "name": "Test Skill",
            "description": "A test skill",
            "capabilities": ["test.skill"],
        }
        
        manifest = _frontmatter_to_manifest(
            fm,
            doc_path=".github/agents/test.md",
            text="# Test"
        )
        
        assert manifest is not None
        assert manifest.name == "Test Skill"
        assert manifest.description == "A test skill"
        assert "test.skill" in manifest.capability_tags

    def test_name_from_file_stem(self):
        """Should derive name from file stem if not provided."""
        fm = {"description": "A skill"}
        
        manifest = _frontmatter_to_manifest(
            fm,
            doc_path=".github/agents/my-skill.md",
            text="# Skill"
        )
        
        assert manifest is not None
        assert manifest.name == "My Skill"

    def test_capability_tags_variants(self):
        """Should support multiple capability tag keys."""
        # Test with capability_tags
        fm1 = {"capability_tags": ["tag1", "tag2"]}
        m1 = _frontmatter_to_manifest(
            fm1,
            doc_path=".github/agents/s1.md",
            text="# S1"
        )
        assert "tag1" in m1.capability_tags
        
        # Test with capabilities
        fm2 = {"capabilities": ["tag3"]}
        m2 = _frontmatter_to_manifest(
            fm2,
            doc_path=".github/agents/s2.md",
            text="# S2"
        )
        assert "tag3" in m2.capability_tags
        
        # Test with capability (singular)
        fm3 = {"capability": "tag4,tag5"}
        m3 = _frontmatter_to_manifest(
            fm3,
            doc_path=".github/agents/s3.md",
            text="# S3"
        )
        assert "tag4" in m3.capability_tags
        assert "tag5" in m3.capability_tags

    def test_skill_id_generation(self):
        """Should generate skill_id from doc_path if not provided."""
        fm = {}
        
        manifest = _frontmatter_to_manifest(
            fm,
            doc_path=".github/agents/my-test-skill.md",
            text="# Skill"
        )
        
        assert manifest is not None
        assert manifest.id == "agent.my_test_skill"

    def test_custom_skill_id(self):
        """Should use provided skill_id."""
        fm = {"id": "custom.id"}
        
        manifest = _frontmatter_to_manifest(
            fm,
            doc_path=".github/agents/skill.md",
            text="# Skill"
        )
        
        assert manifest is not None
        assert manifest.id == "custom.id"

    def test_version_default(self):
        """Should default to version 1.0.0."""
        fm = {}
        
        manifest = _frontmatter_to_manifest(
            fm,
            doc_path=".github/agents/skill.md",
            text="# Skill"
        )
        
        assert manifest is not None
        assert manifest.version == "1.0.0"

    def test_custom_version(self):
        """Should use provided version."""
        fm = {"version": "2.5.0"}
        
        manifest = _frontmatter_to_manifest(
            fm,
            doc_path=".github/agents/skill.md",
            text="# Skill"
        )
        
        assert manifest is not None
        assert manifest.version == "2.5.0"

    def test_risk_tier_inference_d_capable(self):
        """Should infer high risk for D_CAPABLE autonomy model."""
        fm = {"autonomy_model": "D_CAPABLE"}
        
        manifest = _frontmatter_to_manifest(
            fm,
            doc_path=".github/agents/skill.md",
            text="# Skill"
        )
        
        assert manifest is not None
        assert manifest.policy.risk_tier == "high"

    def test_risk_tier_inference_grounded(self):
        """Should infer high risk for GROUNDED enforcement."""
        fm = {"enforcement_tier": "GROUNDED"}
        
        manifest = _frontmatter_to_manifest(
            fm,
            doc_path=".github/agents/skill.md",
            text="# Skill"
        )
        
        assert manifest is not None
        assert manifest.policy.risk_tier == "high"

    def test_risk_tier_inference_partial(self):
        """Should infer medium risk for PARTIAL enforcement."""
        fm = {"enforcement_tier": "PARTIAL"}
        
        manifest = _frontmatter_to_manifest(
            fm,
            doc_path=".github/agents/skill.md",
            text="# Skill"
        )
        
        assert manifest is not None
        assert manifest.policy.risk_tier == "medium"

    def test_entrypoint_from_integration_points(self):
        """Should derive entrypoint from integration_points."""
        fm = {
            "integration_points": ["scripts/my_skill.py"]
        }
        
        manifest = _frontmatter_to_manifest(
            fm,
            doc_path=".github/agents/skill.md",
            text="# Skill"
        )
        
        assert manifest is not None
        assert "scripts.my_skill:run" in manifest.entrypoint

    def test_doc_hash_generation(self):
        """Should generate doc hash from text content."""
        text = "# Test Skill\n\nThis is test content."
        fm = {}
        
        manifest = _frontmatter_to_manifest(
            fm,
            doc_path=".github/agents/skill.md",
            text=text
        )
        
        assert manifest is not None
        assert manifest.doc.hash is not None
        assert len(manifest.doc.hash) == 16


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
            
            assert len(skills) > 0
            assert skills[0].manifest.name == "Test Agent"
            assert "test.skill" in skills[0].manifest.capability_tags

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
            
            assert len(skills) == 3

    def test_nonexistent_directory(self):
        """Should return empty list for nonexistent directory."""
        skills = load_agent_docs_as_skills(agents_root=Path("/nonexistent/path"))
        
        assert skills == []

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
            assert len(skills) == 1

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
            
            assert len(skills) > 0
            assert skills[0].source_path == str(agent_file)

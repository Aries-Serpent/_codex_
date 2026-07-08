"""Tests for the Cognitive Brain SkillRegistry."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from codex.skills.models import BudgetConfig, PolicyConfig, SkillManifest
from codex.skills.registry import SkillRegistry, get_registry, reset_registry


@pytest.fixture(autouse=True)
def fresh_registry():
    """Reset the default registry singleton between tests."""
    reset_registry()
    yield
    reset_registry()


@pytest.fixture
def simple_manifest():
    return SkillManifest(
        id="test.skill.one",
        version="1.0.0",
        name="Test Skill One",
        description="A test skill.",
        capability_tags=["test", "unit"],
        entrypoint="codex.skills.stubs:test_skill_one",
    )


@pytest.fixture
def another_manifest():
    return SkillManifest(
        id="test.skill.two",
        version="2.0.0",
        name="Test Skill Two",
        description="Another test skill.",
        capability_tags=["test", "integration"],
        entrypoint="codex.skills.stubs:test_skill_two",
        policy=PolicyConfig(
            risk_tier="medium",
            budgets=BudgetConfig(calls=10, tokens=5_000, wallclock_ms=30_000),
        ),
    )


class TestSkillRegistryRegister:
    def test_register_returns_registered_skill(self, simple_manifest):
        reg = SkillRegistry()
        skill = reg.register(simple_manifest)
        assert skill.skill_id == "test.skill.one", "skill_id is not valid"
        assert skill.version == "1.0.0", "version is not valid"

    def test_register_idempotent_same_version(self, simple_manifest):
        reg = SkillRegistry()
        s1 = reg.register(simple_manifest)
        s2 = reg.register(simple_manifest)
        assert s1 is s2, "s1 is not valid"
        assert len(reg) == 1, "Reg must not be empty"

    def test_register_two_versions(self, simple_manifest):
        reg = SkillRegistry()
        reg.register(simple_manifest)
        v2 = simple_manifest.model_copy(update={"version": "2.0.0"})
        reg.register(v2)
        assert len(reg) == 1, "Reg must not be empty"
        assert reg.resolve("test.skill.one").version == "2.0.0", "version is not valid"

    def test_register_records_source_path(self, simple_manifest):
        reg = SkillRegistry()
        skill = reg.register(simple_manifest, source_path=os.path.join(tempfile.gettempdir(), "test/manifest.yaml"))
        assert skill.source_path == os.path.join(tempfile.gettempdir(), "test/manifest.yaml"), "source_path is not valid"


class TestSkillRegistryResolve:
    def test_resolve_latest(self, simple_manifest):
        reg = SkillRegistry()
        reg.register(simple_manifest)
        skill = reg.resolve("test.skill.one")
        assert skill is not None, "skill must be initialized"
        assert skill.skill_id == "test.skill.one", "skill_id is not valid"

    def test_resolve_by_version(self, simple_manifest):
        reg = SkillRegistry()
        reg.register(simple_manifest)
        skill = reg.resolve("test.skill.one", version="1.0.0")
        assert skill is not None, "skill must be initialized"

    def test_resolve_missing_returns_none(self):
        reg = SkillRegistry()
        assert reg.resolve("does.not.exist") is None, "Condition must be true"

    def test_resolve_wrong_version_returns_none(self, simple_manifest):
        reg = SkillRegistry()
        reg.register(simple_manifest)
        assert reg.resolve("test.skill.one", version="99.0.0") is None


class TestSkillRegistryList:
    def test_list_all(self, simple_manifest, another_manifest):
        reg = SkillRegistry()
        reg.register(simple_manifest)
        reg.register(another_manifest)
        skills = reg.list()
        assert len(skills) == 2, "Skills must not be empty"

    def test_list_filter_by_capability_tag(self, simple_manifest, another_manifest):
        reg = SkillRegistry()
        reg.register(simple_manifest)
        reg.register(another_manifest)
        skills = reg.list(capability_tag="integration")
        assert len(skills) == 1, "Skills must not be empty"
        assert skills[0].skill_id == "test.skill.two", "skill_id is not valid"

    def test_list_filter_by_risk_tier(self, simple_manifest, another_manifest):
        reg = SkillRegistry()
        reg.register(simple_manifest)
        reg.register(another_manifest)
        skills = reg.list(risk_tier="medium")
        assert len(skills) == 1, "Skills must not be empty"
        assert skills[0].skill_id == "test.skill.two", "skill_id is not valid"

    def test_list_empty_registry(self):
        reg = SkillRegistry()
        assert reg.list() == [], "Condition must be true"


class TestSkillRegistryDiscover:
    def test_discover_finds_manifest_yaml(self, simple_manifest):
        import yaml

        with tempfile.TemporaryDirectory() as tmpdir:
            skill_dir = Path(tmpdir) / "my_skill"
            skill_dir.mkdir()
            manifest_file = skill_dir / "manifest.yaml"
            manifest_file.write_text(yaml.safe_dump(simple_manifest.model_dump()), encoding="utf-8")
            reg = SkillRegistry()
            count = reg.discover(Path(tmpdir))
            assert count == 1, "Count must be greater than zero"
            assert reg.resolve("test.skill.one") is not None, "Value must be initialized"

    def test_discover_skips_invalid_manifest(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bad = Path(tmpdir) / "bad" / "manifest.yaml"
            bad.parent.mkdir()
            bad.write_text("not: valid: yaml: :\n  - bad", encoding="utf-8")
            reg = SkillRegistry()
            count = reg.discover(Path(tmpdir))
            assert count == 0, "Count must be greater than zero"

    def test_discover_uses_default_skills_root(self):
        """Discovery on the real skills package should find built-in skills."""
        reg = SkillRegistry()
        count = reg.discover()
        assert count >= 3, "count must be positive"


class TestBudgetTracking:
    def test_consume_budget(self, simple_manifest):
        reg = SkillRegistry()
        reg.register(simple_manifest)
        reg.consume_budget("test.skill.one", calls=5, tokens=1_000, wallclock_ms=2_000)
        skill = reg.resolve("test.skill.one")
        assert skill.budget_used["calls"] == 5, "Condition must be true"

    def test_reset_budget(self, simple_manifest):
        reg = SkillRegistry()
        reg.register(simple_manifest)
        reg.consume_budget("test.skill.one", calls=5)
        reg.reset_budget("test.skill.one")
        skill = reg.resolve("test.skill.one")
        assert skill.budget_used["calls"] == 0, "Condition must be true"


class TestGetRegistry:
    def test_get_registry_singleton(self):
        r1 = get_registry()
        r2 = get_registry()
        assert r1 is r2, "r1 is not valid"

    def test_reset_registry_creates_fresh(self):
        r1 = get_registry()
        reset_registry()
        r2 = get_registry()
        assert r1 is not r2, "r1 is not valid"

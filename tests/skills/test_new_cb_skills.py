"""Tests for pda.loop.logger and ci.monitor.proactive skills.

Verifies:
  - Both skills are discoverable via SkillRegistry
  - Both have valid manifests (id, entrypoint, pda_loop field)
  - pda.loop.logger all six actions work correctly
  - ci.monitor.proactive returns error on missing credentials (not an import error)
  - PDALoopConfig model field is present on SkillManifest
"""

from __future__ import annotations

import pytest

from codex.skills.ci_monitor_proactive.handler import run as monitor_run
from codex.skills.models import PDALoopConfig, SkillManifest
from codex.skills.pda_loop_logger.handler import run as pda_run
from codex.skills.registry import get_registry, reset_registry

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def fresh_registry():
    reset_registry()
    reg = get_registry()
    reg.discover()
    yield reg
    reset_registry()


# ---------------------------------------------------------------------------
# Registry discovery
# ---------------------------------------------------------------------------


class TestSkillRegistryDiscovery:
    def test_pda_loop_logger_registered(self, fresh_registry):
        skill = fresh_registry.resolve("pda.loop.logger")
        assert skill is not None, "skill must be initialized"
        assert skill.skill_id == "pda.loop.logger", "skill_id is not valid"

    def test_ci_monitor_proactive_registered(self, fresh_registry):
        skill = fresh_registry.resolve("ci.monitor.proactive")
        assert skill is not None, "skill must be initialized"
        assert skill.skill_id == "ci.monitor.proactive", "skill_id is not valid"

    def test_pda_loop_logger_has_cognitive_brain_tag(self, fresh_registry):
        skill = fresh_registry.resolve("pda.loop.logger")
        assert "cognitive-brain" in skill.manifest.capability_tags, "Condition must be true"

    def test_ci_monitor_proactive_has_cognitive_brain_tag(self, fresh_registry):
        skill = fresh_registry.resolve("ci.monitor.proactive")
        assert "cognitive-brain" in skill.manifest.capability_tags, "Condition must be true"

    def test_pda_loop_logger_has_pda_loop_config(self, fresh_registry):
        skill = fresh_registry.resolve("pda.loop.logger")
        assert skill.manifest.pda_loop is not None, "pda_loop must be initialized"
        assert isinstance(skill.manifest.pda_loop, PDALoopConfig)
        assert skill.manifest.pda_loop.enabled is True, "enabled is not valid"

    def test_ci_monitor_proactive_has_pda_loop_config(self, fresh_registry):
        skill = fresh_registry.resolve("ci.monitor.proactive")
        assert skill.manifest.pda_loop is not None, "pda_loop must be initialized"
        assert skill.manifest.pda_loop.enabled is True, "enabled is not valid"

    def test_total_cognitive_brain_skills(self, fresh_registry):
        cb_skills = fresh_registry.list(capability_tag="cognitive-brain")
        assert len(cb_skills) >= 7, f"Expected ≥7 CB skills, got {len(cb_skills)}"

    def test_total_pda_loop_skills(self, fresh_registry):
        all_skills = fresh_registry.list()
        pda_skills = [s for s in all_skills if s.manifest.pda_loop is not None]
        assert len(pda_skills) >= 3, f"Expected ≥3 PDA-loop skills, got {len(pda_skills)}"


# ---------------------------------------------------------------------------
# PDALoopConfig model
# ---------------------------------------------------------------------------


class TestPDALoopConfig:
    def test_pda_loop_config_field_on_manifest(self):
        assert "pda_loop" in SkillManifest.model_fields, "Condition must be true"

    def test_pda_loop_config_defaults(self):
        cfg = PDALoopConfig()
        assert cfg.enabled is True, "enabled is not valid"
        assert cfg.aftermath_store == ".codex/aftermath/pda_iterations.jsonl", "aftermath_store is not valid"

    def test_manifest_without_pda_loop_is_valid(self):
        m = SkillManifest(id="test.skill", name="Test", entrypoint="os:getcwd")
        assert m.pda_loop is None, "pda_loop is not valid"

    def test_manifest_with_pda_loop_parsed(self):
        import yaml

        raw = """
id: test.pda.skill
name: Test PDA Skill
entrypoint: os:getcwd
pda_loop:
  enabled: true
  plan: "plan step"
  do: "do step"
  assess: "assess step"
"""
        data = yaml.safe_load(raw)
        m = SkillManifest.model_validate(data)
        assert m.pda_loop is not None, "pda_loop must be initialized"
        assert m.pda_loop.plan == "plan step", "plan is not valid"
        assert m.pda_loop.do == "do step", "do is not valid"


# ---------------------------------------------------------------------------
# pda.loop.logger handler
# ---------------------------------------------------------------------------


class TestPDALoopLoggerHandler:
    def test_missing_action_returns_error(self):
        result = pda_run({})
        assert result["status"] == "error", "Result must not be empty"
        assert "action" in result["message"], "Result must not be empty"

    def test_unknown_action_returns_error(self):
        result = pda_run({"action": "nonexistent"})
        assert result["status"] == "error", "Result must not be empty"

    def test_summarize_empty_returns_ok(self):
        result = pda_run({"action": "summarize", "limit": 5})
        assert result["status"] == "ok", "Result must not be empty"
        assert "entries" in result, "Result must not be empty"
        assert isinstance(result["entries"], list)

    def test_query_returns_ok(self):
        result = pda_run({"action": "query", "limit": 1})
        assert result["status"] == "ok", "Result must not be empty"
        assert "entries" in result, "Result must not be empty"

    def test_log_failure_missing_fields(self):
        result = pda_run({"action": "log_failure"})
        assert result["status"] == "error", "Result must not be empty"
        assert "Missing fields" in result["message"], "Result must not be empty"

    def test_log_failure_writes_entry(self):
        result = pda_run(
            {
                "action": "log_failure",
                "session": "S293-pytest",
                "pattern_id": "RP-PYTEST-SKILL-TEST",
                "error_text": "unit test error",
            }
        )
        assert result["status"] == "ok", "Result must not be empty"
        assert result["entry"]["pattern_id"] == "RP-PYTEST-SKILL-TEST", "Result must not be empty"
        assert result["entry"]["type"] == "failure", "Result must not be empty"

    def test_log_fix_missing_fields(self):
        result = pda_run({"action": "log_fix"})
        assert result["status"] == "error", "Result must not be empty"

    def test_log_fix_writes_entry(self):
        result = pda_run(
            {
                "action": "log_fix",
                "session": "S293-pytest",
                "pattern_id": "RP-PYTEST-SKILL-TEST",
                "fix_applied": "pytest fix",
                "verification_passed": True,
            }
        )
        assert result["status"] == "ok", "Result must not be empty"
        assert result["entry"]["verification_passed"] is True, "Result must not be empty"

    def test_log_session_writes_entry(self):
        result = pda_run(
            {
                "action": "log_session",
                "session": "S293-pytest",
                "summary": "all tests passed",
                "commit": "abc1234",
            }
        )
        assert result["status"] == "ok", "Result must not be empty"
        assert result["entry"]["type"] == "session", "Result must not be empty"

    def test_query_with_pattern_filter(self):
        # First write a known entry
        pda_run(
            {
                "action": "log_failure",
                "session": "S293-pytest",
                "pattern_id": "RP-QUERY-FILTER-TEST",
            }
        )
        result = pda_run({"action": "query", "pattern_id": "RP-QUERY-FILTER-TEST"})
        assert result["status"] == "ok", "Result must not be empty"
        assert all(e["pattern_id"] == "RP-QUERY-FILTER-TEST" for e in result["entries"]), "Result must not be empty"

    def test_summarize_after_fix_shows_success_rate(self):
        pid = "RP-SUCCESS-RATE-TEST"
        pda_run({"action": "log_failure", "session": "S293", "pattern_id": pid})
        pda_run(
            {"action": "log_fix", "session": "S293", "pattern_id": pid, "verification_passed": True}
        )
        result = pda_run({"action": "summarize", "pattern_id": pid})
        assert result["status"] == "ok", "Result must not be empty"
        matching = [e for e in result["entries"] if e["pattern_id"] == pid]
        if matching:
            assert matching[0]["success_rate"] > 0, "Value must be greater than zero"


# ---------------------------------------------------------------------------
# ci.monitor.proactive handler
# ---------------------------------------------------------------------------


class TestCIMonitorProactiveHandler:
    def test_missing_repo_returns_error(self):
        result = monitor_run({"token": "fake-token"})
        assert result["status"] == "error", "Result must not be empty"
        assert "repo" in result["message"], "Result must not be empty"

    def test_missing_token_returns_error(self):
        result = monitor_run({"repo": "owner/repo"})
        assert result["status"] == "error", "Result must not be empty"
        assert "token" in result["message"], "Result must not be empty"

    def test_invalid_token_dry_run_returns_structured_error(self):
        # With an invalid token + dry_run=True, the monitor may fail at the
        # GitHub API call, but it should return a dict (not raise).
        result = monitor_run(
            {
                "repo": "Aries-Serpent/_codex_",
                "token": "invalid-token-for-test",
                "dry_run": True,
                "max_age_h": 1,
                "target_pr": 0,
            }
        )
        # Must always return a dict with "status"
        assert isinstance(result, dict)
        assert "status" in result, "Result must not be empty"

    def test_entrypoint_is_callable(self, fresh_registry):
        import importlib

        skill = fresh_registry.resolve("ci.monitor.proactive")
        mod_path, func_name = skill.manifest.entrypoint.rsplit(":", 1)
        mod = importlib.import_module(mod_path)
        fn = getattr(mod, func_name)
        assert callable(fn), "Condition must be true"

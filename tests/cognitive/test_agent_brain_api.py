"""Tests for AgentBrainAPI and CognitiveBrain (agent_brain_api.py).

Covers:
* AgentSessionContext dataclass + serialisation
* CompletionReport dataclass
* AgentBrainAPI: get_session_context, report_completion,
  get_continuation_prompt, get_agent_capabilities, survey_unfinished
* AGENT_CAPABILITIES map: all 12 areas covered, all agent IDs valid
* CognitiveBrain singleton: for_agent, session, next, advance,
  help, discover, health, capabilities property
* brain module-level singleton importable from codex.cognitive
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from codex.cognitive.agent_brain_api import (
    AGENT_CAPABILITIES,
    AgentBrainAPI,
    AgentSessionContext,
    CognitiveBrain,
    CompletionReport,
)
from codex.cognitive.planset_orchestrator import PlansetOrchestrator
from codex.cognitive.quantum_planset_engine import ImprovementArea, QuantumPlansetEngine

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_api(tmp_path: Path, agent_id: str = "copilot-coding-agent") -> AgentBrainAPI:
    """Build an AgentBrainAPI with an in-memory planset dir."""
    d = tmp_path / "plans"
    d.mkdir(exist_ok=True)
    (d / "CODEQL_ALERT_RESOLUTION_PLANSET.md").write_text(
        "# CodeQL\n**Status:** 🚧 Active\n", encoding="utf-8"
    )
    (d / "PLANSET_PHASE_23_COVERAGE_30.md").write_text(
        "# Coverage\n**Status**: 🔄 READY\n", encoding="utf-8"
    )
    (d / "WORKFLOW_HEALTH_AUTOMATION_PLANSET.md").write_text(
        "# WF\n**Status:** Ready\n", encoding="utf-8"
    )
    return AgentBrainAPI(
        agent_id=agent_id,
        planset_dir=d,
        state_path=tmp_path / "state.json",
        brain_data_dir=tmp_path / "brain",
    )


def _make_brain(tmp_path: Path) -> CognitiveBrain:
    d = tmp_path / "plans"
    d.mkdir(exist_ok=True)
    (d / "CODEQL_ALERT_RESOLUTION_PLANSET.md").write_text(
        "# CodeQL\n**Status:** 🚧 Active\n", encoding="utf-8"
    )
    (d / "ML_PATTERN_FEEDING_PLANSET.md").write_text(
        "# ML\n**Status:** Ready to Implement\n", encoding="utf-8"
    )
    return CognitiveBrain(
        planset_dir=d,
        state_path=tmp_path / "state.json",
        brain_data_dir=tmp_path / "brain",
    )


# ---------------------------------------------------------------------------
# AgentSessionContext
# ---------------------------------------------------------------------------


class TestAgentSessionContext:
    def test_to_dict_contains_all_keys(self):
        ctx = AgentSessionContext(
            session_id="s1",
            agent_id="copilot-coding-agent",
            next_actions=[],
            continuation_from="fresh",
            active_patterns=[],
            capabilities=["CI_SELF_HEALING"],
            continuation_prompt="@copilot go",
        )
        d = ctx.to_dict()
        assert "session_id" in d, "Condition must be true"
        assert "next_actions" in d, "Condition must be true"
        assert "continuation_prompt" in d, "Condition must be true"

    def test_to_json_valid(self):
        ctx = AgentSessionContext(
            session_id="s2",
            agent_id="a",
            next_actions=[],
            continuation_from="",
            active_patterns=[],
            capabilities=[],
            continuation_prompt="x",
        )
        data = json.loads(ctx.to_json())
        assert data["agent_id"] == "a", "Data must not be empty"


# ---------------------------------------------------------------------------
# CompletionReport
# ---------------------------------------------------------------------------


class TestCompletionReport:
    def test_to_dict(self):
        r = CompletionReport(
            agent_id="codeql-alert-resolution-agent",
            area="SECURITY_REMEDIATION",
            step_id="SEC-01",
            outcome="success",
            notes="107 alerts",
            artifacts=["alerts.json"],
        )
        d = r.to_dict()
        assert d["step_id"] == "SEC-01", "Condition must be true"
        assert d["outcome"] == "success", "Condition must be true"
        assert d["artifacts"] == ["alerts.json"], "Condition must be true"


# ---------------------------------------------------------------------------
# AgentBrainAPI
# ---------------------------------------------------------------------------


class TestAgentBrainAPI:
    def test_get_session_context_returns_context(self, tmp_path: Path):
        api = _make_api(tmp_path)
        ctx = api.get_session_context()
        assert isinstance(ctx, AgentSessionContext)
        assert ctx.agent_id == "copilot-coding-agent", "agent_id is not valid"

    def test_session_context_has_next_actions(self, tmp_path: Path):
        api = _make_api(tmp_path)
        ctx = api.get_session_context()
        assert len(ctx.next_actions) > 0, "Collection must not be empty"

    def test_session_context_continuation_prompt_contains_copilot(self, tmp_path: Path):
        api = _make_api(tmp_path)
        ctx = api.get_session_context()
        assert "@copilot" in ctx.continuation_prompt, "Condition must be true"

    def test_session_context_respects_max_actions(self, tmp_path: Path):
        api = _make_api(tmp_path)
        ctx = api.get_session_context(max_actions=2)
        assert len(ctx.next_actions) <= 2, "Collection must not be empty"

    def test_capabilities_filtered_for_scoped_agent(self, tmp_path: Path):
        api = _make_api(tmp_path, agent_id="codeql-alert-resolution-agent")
        ctx = api.get_session_context()
        # All returned actions should be from SECURITY_REMEDIATION
        areas = {p.area for p in ctx.next_actions}
        assert areas <= {"SECURITY_REMEDIATION"}, "areas is not valid"

    def test_report_completion_returns_report(self, tmp_path: Path):
        api = _make_api(tmp_path)
        report = api.report_completion(
            area=ImprovementArea.SECURITY_REMEDIATION,
            step_id="SEC-01",
            outcome="success",
            notes="done",
        )
        assert isinstance(report, CompletionReport)
        assert report.step_id == "SEC-01", "step_id is not valid"
        assert report.outcome == "success", "outcome is not valid"

    def test_report_completion_advances_orchestrator(self, tmp_path: Path):
        api = _make_api(tmp_path)
        api.report_completion(ImprovementArea.SECURITY_REMEDIATION, "SEC-01")
        completed = api._orch._state.completed_steps.get("SECURITY_REMEDIATION", [])
        assert "SEC-01" in completed, "Condition must be true"

    def test_get_continuation_prompt_is_string(self, tmp_path: Path):
        api = _make_api(tmp_path)
        p = api.get_continuation_prompt()
        assert isinstance(p, str)
        assert "@copilot" in p, "Condition must be true"

    def test_get_agent_capabilities_returns_list(self, tmp_path: Path):
        api = _make_api(tmp_path)
        caps = api.get_agent_capabilities()
        assert isinstance(caps, list)
        assert all(isinstance(c, ImprovementArea) for c in caps)

    def test_survey_unfinished_returns_markdown(self, tmp_path: Path):
        api = _make_api(tmp_path)
        s = api.survey_unfinished()
        assert isinstance(s, str)

    def test_session_context_with_context_signals(self, tmp_path: Path):
        api = _make_api(tmp_path)
        ctx = api.get_session_context(session_context={"open_alerts": 120, "coverage_pct": 40})
        assert ctx is not None, "ctx must be initialized"

    def test_active_patterns_is_list(self, tmp_path: Path):
        api = _make_api(tmp_path)
        ctx = api.get_session_context()
        assert isinstance(ctx.active_patterns, list)

    def test_continuation_from_shows_fresh_state(self, tmp_path: Path):
        api = _make_api(tmp_path)
        ctx = api.get_session_context()
        assert "fresh" in ctx.continuation_from.lower(), "Condition must be true"

    def test_continuation_from_shows_completed_steps(self, tmp_path: Path):
        api = _make_api(tmp_path)
        api.report_completion(ImprovementArea.SECURITY_REMEDIATION, "SEC-01")
        ctx = api.get_session_context()
        assert "SEC-01" in ctx.continuation_from, "Condition must be true"


# ---------------------------------------------------------------------------
# AGENT_CAPABILITIES map
# ---------------------------------------------------------------------------


class TestAgentCapabilitiesMap:
    def test_all_areas_covered(self):
        mapped = set()
        for caps in AGENT_CAPABILITIES.values():
            mapped.update(caps)
        unmapped = set(ImprovementArea) - mapped
        assert not unmapped, f"Areas without agent: {unmapped}"

    def test_all_values_are_improvement_areas(self):
        for agent, caps in AGENT_CAPABILITIES.items():
            for c in caps:
                assert isinstance(c, ImprovementArea), f"{agent} has invalid capability {c}"

    def test_copilot_coding_agent_has_all_areas(self):
        caps = AGENT_CAPABILITIES["copilot-coding-agent"]
        assert set(caps) == set(ImprovementArea), "Condition must be true"

    def test_codeql_agent_covers_security(self):
        assert (ImprovementArea.SECURITY_REMEDIATION, "Condition must be true"
            in AGENT_CAPABILITIES["codeql-alert-resolution-agent"]
        )

    def test_qi_agent_covers_qi_testing(self):
        assert ImprovementArea.QI_TESTING in AGENT_CAPABILITIES["quantum-compliance-tuning-agent"]


# ---------------------------------------------------------------------------
# CognitiveBrain singleton
# ---------------------------------------------------------------------------


class TestCognitiveBrain:
    def test_for_agent_returns_api(self, tmp_path: Path):
        cb = _make_brain(tmp_path)
        api = cb.for_agent("codeql-alert-resolution-agent")
        assert isinstance(api, AgentBrainAPI)

    def test_for_agent_cached(self, tmp_path: Path):
        cb = _make_brain(tmp_path)
        a1 = cb.for_agent("copilot-coding-agent")
        a2 = cb.for_agent("copilot-coding-agent")
        assert a1 is a2, "a1 is not valid"

    def test_session_returns_context(self, tmp_path: Path):
        cb = _make_brain(tmp_path)
        ctx = cb.session("copilot-coding-agent")
        assert isinstance(ctx, AgentSessionContext)

    def test_next_returns_promptset_or_none(self, tmp_path: Path):
        cb = _make_brain(tmp_path)
        result = cb.next()
        # Either a PromptSet or None (all done)
        from codex.cognitive.planset_orchestrator import PromptSet

        assert result is None or isinstance(result, PromptSet)

    def test_advance_returns_report(self, tmp_path: Path):
        cb = _make_brain(tmp_path)
        report = cb.advance("SECURITY_REMEDIATION", "SEC-01", outcome="success")
        assert isinstance(report, CompletionReport)
        assert report.step_id == "SEC-01", "step_id is not valid"

    def test_advance_accepts_improvement_area_enum(self, tmp_path: Path):
        cb = _make_brain(tmp_path)
        report = cb.advance(ImprovementArea.CI_SELF_HEALING, "CI-01")
        assert report.area == "CI_SELF_HEALING", "area is not valid"

    def test_help_returns_string(self, tmp_path: Path):
        cb = _make_brain(tmp_path)
        h = cb.help()
        assert isinstance(h, str)
        assert "brain.session" in h, "Condition must be true"
        assert "brain.next" in h, "Condition must be true"
        assert "brain.advance" in h, "Condition must be true"
        assert "CODEBASE AGENCY POLICY" in h, "Condition must be true"

    def test_help_lists_all_areas(self, tmp_path: Path):
        cb = _make_brain(tmp_path)
        h = cb.help()
        for area in ImprovementArea:
            assert area.value in h, "Value must be initialized"

    def test_discover_returns_dict(self, tmp_path: Path):
        cb = _make_brain(tmp_path)
        d = cb.discover()
        assert isinstance(d, dict)
        assert "improvement_areas" in d, "Condition must be true"
        assert "agent_routing" in d, "Condition must be true"
        assert "engine_equation" in d, "Condition must be true"
        assert "modules" in d, "Condition must be true"
        assert "quickstart" in d, "Condition must be true"

    def test_discover_all_12_areas(self, tmp_path: Path):
        cb = _make_brain(tmp_path)
        d = cb.discover()
        assert set(d["improvement_areas"]) == {a.value for a in ImprovementArea}, "Value must be initialized"

    def test_discover_is_json_serialisable(self, tmp_path: Path):
        cb = _make_brain(tmp_path)
        d = cb.discover()
        serialised = json.dumps(d)
        assert len(serialised) > 100, "Serialised must not be empty"

    def test_health_returns_dict(self, tmp_path: Path):
        cb = _make_brain(tmp_path)
        h = cb.health()
        assert "status" in h, "Condition must be true"
        assert "engine_ok" in h, "Condition must be true"
        assert "unfinished_plansets" in h, "Condition must be true"
        assert "issues" in h, "Condition must be true"

    def test_health_engine_ok(self, tmp_path: Path):
        cb = _make_brain(tmp_path)
        h = cb.health()
        assert h["engine_ok"] is True, "Condition must be true"

    def test_health_status_healthy(self, tmp_path: Path):
        cb = _make_brain(tmp_path)
        h = cb.health()
        assert h["status"] == "healthy", "Condition must be true"

    def test_health_degraded_missing_planset_dir(self, tmp_path: Path):
        cb = CognitiveBrain(
            planset_dir=tmp_path / "nonexistent",
            state_path=tmp_path / "s.json",
        )
        h = cb.health()
        assert h["status"] == "degraded", "Condition must be true"
        assert len(h["issues"]) > 0, "Collection must not be empty"

    def test_capabilities_property_returns_dict(self, tmp_path: Path):
        cb = _make_brain(tmp_path)
        caps = cb.capabilities
        assert isinstance(caps, dict)
        assert "copilot-coding-agent" in caps, "Condition must be true"

    def test_engine_attribute_is_engine(self, tmp_path: Path):
        cb = _make_brain(tmp_path)
        assert isinstance(cb.engine, QuantumPlansetEngine)

    def test_orchestrator_attribute_is_orchestrator(self, tmp_path: Path):
        cb = _make_brain(tmp_path)
        assert isinstance(cb.orchestrator, PlansetOrchestrator)


# ---------------------------------------------------------------------------
# Module-level brain singleton
# ---------------------------------------------------------------------------


class TestBrainSingleton:
    def test_brain_importable(self):
        from codex.cognitive import brain

        assert isinstance(brain, CognitiveBrain)

    def test_brain_has_help(self):
        from codex.cognitive import brain

        assert callable(brain.help, "Condition must be true"
        ), "Condition must be true"

    def test_brain_has_discover(self):
        from codex.cognitive import brain

        d = brain.discover()
        assert "improvement_areas" in d, "Condition must be true"

    def test_brain_has_health(self):
        from codex.cognitive import brain

        h = brain.health()
        assert "status" in h, "Condition must be true"

    def test_brain_for_agent_works(self):
        from codex.cognitive import brain

        api = brain.for_agent("copilot-coding-agent")
        assert isinstance(api, AgentBrainAPI)

    def test_all_exports_importable(self):
        from codex.cognitive import (
            CognitiveBrain,
            brain,
        )

        assert brain is not None, "brain must be initialized"
        assert issubclass(CognitiveBrain, object)

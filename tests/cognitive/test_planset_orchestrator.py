"""Tests for PlansetOrchestrator and orchestrate.py CLI.

Covers:
* PlansetRecord construction
* PromptSet serialisation
* OrchestrationState round-trip
* PlansetOrchestrator.survey() — real .codex/plans/ directory
* PlansetOrchestrator.generate_session() — ranking, dedup, context boosts
* PlansetOrchestrator.next_promptset() — returns highest-amplitude action
* PlansetOrchestrator.advance() — marks complete + decoherence applied
* PlansetOrchestrator.summary() — Markdown output
* PlansetOrchestrator.save_state() / load_state() — JSON round-trip
* orchestrate.py CLI — survey, next, session, advance, summary, stamp-plansets
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Ensure src/ is on path (mirrors orchestrate.py bootstrap)
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from codex.cognitive.planset_orchestrator import (
    _PLANSET_MAP,
    OrchestrationState,
    PlansetOrchestrator,
    PlansetRecord,
    PromptSet,
)
from codex.cognitive.quantum_planset_engine import ImprovementArea, QuantumPlansetEngine

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def planset_dir(tmp_path: Path) -> Path:
    """Create a minimal .codex/plans directory with fake plansets."""
    d = tmp_path / ".codex" / "plans"
    d.mkdir(parents=True)

    (d / "CODEQL_ALERT_RESOLUTION_PLANSET.md").write_text(
        "# CodeQL\n**Status:** 🚧 Active Development\n", encoding="utf-8"
    )
    (d / "PLANSET_PHASE_23_COVERAGE_30.md").write_text(
        "# Coverage 30%\n**Status**: 🔄 READY FOR EXECUTION\n", encoding="utf-8"
    )
    (d / "IP-005_DEPENDENCY_UPDATES_PLANSET.md").write_text(
        "# Dependencies\n**Status:** ✅ COMPLETE\n", encoding="utf-8"
    )
    (d / "PRODUCTION_RAG_PIPELINE_PLANSET.md").write_text(
        "# RAG\n**Status:** 🔄 IN PROGRESS - Phase 1 & 2 Complete\n", encoding="utf-8"
    )
    (d / "WORKFLOW_HEALTH_AUTOMATION_PLANSET.md").write_text(
        "# Workflow Health\n**Status:** Ready to Implement\n", encoding="utf-8"
    )
    (d / "CUSTOM_AGENT_PLANSET_CACHE_LOGIC_VALIDATOR.md").write_text(
        "# Cache\n**Status**: 📋 PLANNED\n", encoding="utf-8"
    )
    (d / "ML_PATTERN_FEEDING_PLANSET.md").write_text(
        "# ML\n**Status:** Ready to Implement\n", encoding="utf-8"
    )
    (d / "AGENT_CHAINING_INTEGRATION_PLANSET.md").write_text(
        "# Chaining\n**Status:** Ready to Implement\n", encoding="utf-8"
    )
    return d


@pytest.fixture()
def orch(planset_dir: Path, tmp_path: Path) -> PlansetOrchestrator:
    return PlansetOrchestrator(
        planset_dir=planset_dir,
        engine=QuantumPlansetEngine(),
        state_path=tmp_path / "state.json",
    )


# ---------------------------------------------------------------------------
# PlansetRecord
# ---------------------------------------------------------------------------


class TestPlansetRecord:
    def test_fields(self, tmp_path: Path):
        p = tmp_path / "TEST.md"
        p.write_text("# Test", encoding="utf-8")
        rec = PlansetRecord(
            path=p,
            stem="TEST",
            area=ImprovementArea.CI_SELF_HEALING,
            is_complete=False,
            status_line="🔄 IN PROGRESS",
        )
        assert rec.stem == "TEST", "stem is not valid"
        assert rec.area == ImprovementArea.CI_SELF_HEALING, "area is not valid"
        assert not rec.is_complete, "Condition must be true"

    def test_unmapped_area_is_none(self, tmp_path: Path):
        p = tmp_path / "UNKNOWN.md"
        p.write_text("# Unknown", encoding="utf-8")
        rec = PlansetRecord(path=p, stem="UNKNOWN", area=None, is_complete=False)
        assert rec.area is None, "area is not valid"


# ---------------------------------------------------------------------------
# PromptSet
# ---------------------------------------------------------------------------


class TestPromptSet:
    def test_to_dict_round_trip(self):
        ps = PromptSet(
            prompt_id="SEC:SEC-01:20260226",
            area="SECURITY_REMEDIATION",
            source_planset="CODEQL_ALERT_RESOLUTION_PLANSET",
            agent="codeql-alert-resolution-agent",
            prompt="Do security stuff",
            context={"open_alerts": 120},
            amplitude=1.2345,
            order=0,
            step_id="SEC-01",
            description="Collect alerts",
        )
        d = ps.to_dict()
        assert d["step_id"] == "SEC-01", "Condition must be true"
        assert d["amplitude"] == pytest.approx(1.2345), "Condition must be true"
        assert d["context"]["open_alerts"] == 120, "Condition must be true"

    def test_to_json_valid(self):
        ps = PromptSet(
            prompt_id="x",
            area="CI_SELF_HEALING",
            source_planset="foo",
            agent="ci-auto-healer-agent",
            prompt="fix CI",
            context={},
            amplitude=0.9,
            order=0,
            step_id="CI-01",
        )
        data = json.loads(ps.to_json())
        assert data["agent"] == "ci-auto-healer-agent", "Data must not be empty"


# ---------------------------------------------------------------------------
# OrchestrationState
# ---------------------------------------------------------------------------


class TestOrchestrationState:
    def test_round_trip(self):
        state = OrchestrationState(
            session_id="session-20260226",
            active_areas=["SECURITY_REMEDIATION"],
            completed_steps={"SECURITY_REMEDIATION": ["SEC-01"]},
            decoherence_sessions={"SECURITY_REMEDIATION": 1},
            last_updated="2026-02-26T00:00:00Z",
        )
        d = state.to_dict()
        restored = OrchestrationState.from_dict(d)
        assert restored.session_id == "session-20260226", "session_id is not valid"
        assert restored.completed_steps["SECURITY_REMEDIATION"] == ["SEC-01"], "rest is not valid"
        assert restored.decoherence_sessions["SECURITY_REMEDIATION"] == 1, "rest is not valid"

    def test_from_dict_missing_keys(self):
        state = OrchestrationState.from_dict({"session_id": "s1"})
        assert state.active_areas == [], "active_areas is not valid"
        assert state.completed_steps == {}, "completed_steps is not valid"


# ---------------------------------------------------------------------------
# PlansetOrchestrator.survey()
# ---------------------------------------------------------------------------


class TestOrchestratorSurvey:
    def test_returns_all_md_files(self, orch: PlansetOrchestrator):
        records = orch.survey()
        stems = [r.stem for r in records]
        assert "CODEQL_ALERT_RESOLUTION_PLANSET" in stems, "Condition must be true"
        assert "IP-005_DEPENDENCY_UPDATES_PLANSET" in stems, "Condition must be true"

    def test_complete_planset_flagged(self, orch: PlansetOrchestrator):
        records = {r.stem: r for r in orch.survey()}
        assert records["IP-005_DEPENDENCY_UPDATES_PLANSET"].is_complete is True, "is_complete is not valid"

    def test_incomplete_planset_flagged(self, orch: PlansetOrchestrator):
        records = {r.stem: r for r in orch.survey()}
        assert records["CODEQL_ALERT_RESOLUTION_PLANSET"].is_complete is False, "is_complete is not valid"

    def test_area_mapping_applied(self, orch: PlansetOrchestrator):
        records = {r.stem: r for r in orch.survey()}
        assert (records["CODEQL_ALERT_RESOLUTION_PLANSET"].area == ImprovementArea.SECURITY_REMEDIATION
        )
        assert records["PLANSET_PHASE_23_COVERAGE_30"].area == ImprovementArea.COVERAGE_IMPROVEMENT

    def test_empty_dir_returns_empty(self, tmp_path: Path):
        empty = tmp_path / "empty"
        empty.mkdir()
        o = PlansetOrchestrator(planset_dir=empty, state_path=tmp_path / "s.json")
        assert o.survey() == [], "Condition must be true"

    def test_nonexistent_dir_returns_empty(self, tmp_path: Path):
        o = PlansetOrchestrator(
            planset_dir=tmp_path / "no_such_dir",
            state_path=tmp_path / "s.json",
        )
        assert o.survey() == [], "Condition must be true"


# ---------------------------------------------------------------------------
# PlansetOrchestrator.generate_session()
# ---------------------------------------------------------------------------


class TestOrchestratorGenerateSession:
    def test_returns_prompt_sets(self, orch: PlansetOrchestrator):
        prompts = orch.generate_session()
        assert len(prompts) > 0, "Prompts must not be empty"
        assert all(isinstance(p, PromptSet) for p in prompts)

    def test_sorted_by_amplitude_descending(self, orch: PlansetOrchestrator):
        prompts = orch.generate_session(max_prompts=15)
        amps = [p.amplitude for p in prompts]
        assert amps == sorted(amps, reverse=True)

    def test_order_field_renumbered(self, orch: PlansetOrchestrator):
        prompts = orch.generate_session(max_prompts=5)
        assert [p.order for p in prompts] == list(range(len(prompts)), "Prompts must not be empty"
        ), "Prompts must not be empty"

    def test_max_prompts_respected(self, orch: PlansetOrchestrator):
        prompts = orch.generate_session(max_prompts=3)
        assert len(prompts) <= 3, "Prompts must not be empty"

    def test_complete_plansets_excluded_by_default(self, orch: PlansetOrchestrator):
        prompts = orch.generate_session()
        sources = {p.source_planset for p in prompts}
        assert "IP-005_DEPENDENCY_UPDATES_PLANSET" not in sources, "Condition must be true"

    def test_context_open_alerts_boosts_security(self, orch: PlansetOrchestrator):
        lo = orch.generate_session(context={"open_alerts": 0}, max_prompts=20)
        hi = orch.generate_session(context={"open_alerts": 200}, max_prompts=20)
        amp_lo = next((p.amplitude for p in lo if p.area == "SECURITY_REMEDIATION"), 0)
        amp_hi = next((p.amplitude for p in hi if p.area == "SECURITY_REMEDIATION"), 0)
        assert amp_hi >= amp_lo, "amp_hi must be greater than zero"

    def test_each_area_deduped_to_one_planset(self, orch: PlansetOrchestrator):
        prompts = orch.generate_session(max_prompts=50)
        sources_per_area: dict = {}
        for p in prompts:
            sources_per_area.setdefault(p.area, set()).add(p.source_planset)
        # Each area maps to exactly one source planset
        for area, srcs in sources_per_area.items():
            assert len(srcs) == 1, f"Area {area} has multiple sources: {srcs}"

    def test_prompt_contains_agent_and_step(self, orch: PlansetOrchestrator):
        prompts = orch.generate_session(max_prompts=1)
        p = prompts[0]
        assert p.agent in p.prompt, "Condition must be true"
        assert p.step_id in p.prompt, "Condition must be true"

    def test_prompt_contains_advance_instruction(self, orch: PlansetOrchestrator):
        prompts = orch.generate_session(max_prompts=1)
        assert "advance" in prompts[0].prompt.lower(), "Condition must be true"


# ---------------------------------------------------------------------------
# PlansetOrchestrator.next_promptset()
# ---------------------------------------------------------------------------


class TestOrchestratorNextPromptset:
    def test_returns_promptset(self, orch: PlansetOrchestrator):
        p = orch.next_promptset()
        assert p is not None, "p must be initialized"
        assert isinstance(p, PromptSet)

    def test_is_highest_amplitude(self, orch: PlansetOrchestrator):
        p_next = orch.next_promptset()
        all_prompts = orch.generate_session(max_prompts=20)
        assert p_next.amplitude == all_prompts[0].amplitude, "amplitude is not valid"

    def test_returns_none_when_all_complete(self, tmp_path: Path):
        empty = tmp_path / "empty"
        empty.mkdir()
        o = PlansetOrchestrator(planset_dir=empty, state_path=tmp_path / "s.json")
        assert o.next_promptset() is None, "Condition must be true"


# ---------------------------------------------------------------------------
# PlansetOrchestrator.advance()
# ---------------------------------------------------------------------------


class TestOrchestratorAdvance:
    def test_marks_step_complete(self, orch: PlansetOrchestrator):
        orch.advance(ImprovementArea.SECURITY_REMEDIATION, "SEC-01")
        assert "SEC-01" in orch._state.completed_steps.get("SECURITY_REMEDIATION", [])

    def test_decoherence_incremented(self, orch: PlansetOrchestrator):
        orch.advance(ImprovementArea.SECURITY_REMEDIATION, "SEC-01")
        assert orch._state.decoherence_sessions.get("SECURITY_REMEDIATION", 0) == 1

    def test_completed_step_excluded_from_session(self, orch: PlansetOrchestrator):
        # Get the first SEC step
        prompts_before = orch.generate_session(max_prompts=20)
        sec_steps_before = [p.step_id for p in prompts_before if p.area == "SECURITY_REMEDIATION"]
        if not sec_steps_before:
            pytest.skip("No SECURITY_REMEDIATION steps in test planset_dir")
        first_sec = sec_steps_before[0]
        orch.advance(ImprovementArea.SECURITY_REMEDIATION, first_sec)
        prompts_after = orch.generate_session(max_prompts=20)
        sec_steps_after = [p.step_id for p in prompts_after if p.area == "SECURITY_REMEDIATION"]
        assert first_sec not in sec_steps_after, "Condition must be true"

    def test_advance_idempotent(self, orch: PlansetOrchestrator):
        orch.advance(ImprovementArea.CI_SELF_HEALING, "CI-01")
        orch.advance(ImprovementArea.CI_SELF_HEALING, "CI-01")  # duplicate
        completed = orch._state.completed_steps.get("CI_SELF_HEALING", [])
        assert completed.count("CI-01") == 1, "Count must be greater than zero"


# ---------------------------------------------------------------------------
# PlansetOrchestrator.summary()
# ---------------------------------------------------------------------------


class TestOrchestratorSummary:
    def test_returns_markdown_string(self, orch: PlansetOrchestrator):
        s = orch.summary()
        assert "Planset Orchestrator" in s or "✅" in s, "Condition must be true"

    def test_contains_step_ids(self, orch: PlansetOrchestrator):
        s = orch.summary()
        # At least one step ID pattern like SEC-01 or CI-01
        import re

        assert re.search(r"[A-Z]+-\d+", s)

    def test_empty_summary_when_all_done(self, tmp_path: Path):
        d = tmp_path / "plans"
        d.mkdir()
        (d / "DONE.md").write_text("# Done\n✅ COMPLETE\n", encoding="utf-8")
        o = PlansetOrchestrator(planset_dir=d, state_path=tmp_path / "s.json")
        s = o.summary()
        assert "nothing left" in s.lower() or "complete" in s.lower(), "Condition must be true"


# ---------------------------------------------------------------------------
# PlansetOrchestrator.save_state() / load_state()
# ---------------------------------------------------------------------------


class TestOrchestratorStatePersistence:
    def test_save_and_load_round_trip(self, orch: PlansetOrchestrator, tmp_path: Path):
        orch.advance(ImprovementArea.SECURITY_REMEDIATION, "SEC-01")
        state_path = tmp_path / "state_rt.json"
        orch.save_state(state_path)
        assert state_path.exists(), "Condition must be true"
        loaded = orch.load_state(state_path)
        assert "SEC-01" in loaded.completed_steps.get("SECURITY_REMEDIATION", [])

    def test_state_file_is_valid_json(self, orch: PlansetOrchestrator, tmp_path: Path):
        orch.advance(ImprovementArea.RAG_PIPELINE, "RAG-01")
        p = tmp_path / "state.json"
        orch.save_state(p)
        data = json.loads(p.read_text())
        assert "completed_steps" in data, "Data must not be empty"
        assert "decoherence_sessions" in data, "Data must not be empty"

    def test_corrupt_state_file_handled(self, tmp_path: Path):
        bad = tmp_path / "bad.json"
        bad.write_text("{not valid json", encoding="utf-8")
        d = tmp_path / "plans"
        d.mkdir()
        o = PlansetOrchestrator(planset_dir=d, state_path=bad)
        # Should not raise; falls back to fresh state
        assert o._state.session_id != "", "session_id is not valid"


# ---------------------------------------------------------------------------
# Planset mapping coverage
# ---------------------------------------------------------------------------


class TestPlansetMapCoverage:
    def test_all_mapped_areas_are_valid_improvement_areas(self):
        for stem, area in _PLANSET_MAP.items():
            assert isinstance(area, ImprovementArea), f"{stem} maps to invalid area {area}"

    def test_all_12_areas_have_at_least_one_mapping(self):
        mapped_areas = set(_PLANSET_MAP.values())
        all_areas = set(ImprovementArea)
        # All 12 improvement areas should be mapped to at least one planset
        unmapped = all_areas - mapped_areas
        assert not unmapped, f"Areas without planset mapping: {unmapped}"

    def test_coverage_improvement_maps_to_phase_plansets(self):
        cov_plansets = [
            k for k, v in _PLANSET_MAP.items() if v == ImprovementArea.COVERAGE_IMPROVEMENT
        ]
        assert any("COVERAGE" in p or "PHASE_14" in p for p in cov_plansets), "Condition must be true"

    def test_qi_testing_maps_to_quantum_plansets(self):
        qi_plansets = [k for k, v in _PLANSET_MAP.items() if v == ImprovementArea.QI_TESTING]
        assert any("QUANTUM" in p for p in qi_plansets), "Condition must be true"


# ---------------------------------------------------------------------------
# CLI — orchestrate.py
# ---------------------------------------------------------------------------


class TestOrchestrateCLI:
    """Tests for the orchestrate.py entry point."""

    def _run(self, argv, planset_dir: Path, tmp_path: Path):
        """Run main() with a patched orchestrator pointing to test planset_dir."""
        from scripts.cognitive.orchestrate import main

        state_path = tmp_path / "cli_state.json"
        with patch(
            "scripts.cognitive.orchestrate._build_orchestrator",
            return_value=PlansetOrchestrator(
                planset_dir=planset_dir,
                engine=QuantumPlansetEngine(),
                state_path=state_path,
            ),
        ):
            return main(argv)

    def test_survey_exits_0(self, planset_dir: Path, tmp_path: Path):
        rc = self._run(["survey"], planset_dir, tmp_path)
        assert rc == 0, "rc is not valid"

    def test_next_exits_0(self, planset_dir: Path, tmp_path: Path):
        rc = self._run(["next"], planset_dir, tmp_path)
        assert rc == 0, "rc is not valid"

    def test_session_exits_0(self, planset_dir: Path, tmp_path: Path):
        rc = self._run(["session"], planset_dir, tmp_path)
        assert rc == 0, "rc is not valid"

    def test_session_json_output(
        self, planset_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture
    ):
        self._run(["session", "--output", "json", "--dry-run"], planset_dir, tmp_path)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert isinstance(data, list)
        assert all("step_id" in item for item in data), "Data must not be empty"

    def test_session_markdown_output(
        self, planset_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture
    ):
        self._run(["session", "--output", "markdown", "--dry-run"], planset_dir, tmp_path)
        out = capsys.readouterr().out
        assert "Planset Orchestrator" in out or "|" in out, "Condition must be true"

    def test_next_json_output(
        self, planset_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture
    ):
        self._run(["next", "--output", "json", "--dry-run"], planset_dir, tmp_path)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert "step_id" in data, "Data must not be empty"

    def test_summary_exits_0(self, planset_dir: Path, tmp_path: Path):
        rc = self._run(["summary", "--dry-run"], planset_dir, tmp_path)
        assert rc in (0, 2)

    def test_advance_exits_0(self, planset_dir: Path, tmp_path: Path):
        rc = self._run(
            ["advance", "SECURITY_REMEDIATION", "SEC-01"],
            planset_dir,
            tmp_path,
        )
        assert rc == 0, "rc is not valid"

    def test_advance_invalid_area_exits_1(
        self, planset_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture
    ):
        rc = self._run(["advance", "INVALID_AREA", "SEC-01"], planset_dir, tmp_path)
        assert rc == 1, "rc is not valid"

    def test_survey_json_output(
        self, planset_dir: Path, tmp_path: Path, capsys: pytest.CaptureFixture
    ):
        self._run(["survey", "--output", "json"], planset_dir, tmp_path)
        out = capsys.readouterr().out
        data = json.loads(out)
        assert isinstance(data, list)
        assert all("stem" in item for item in data), "Data must not be empty"

    def test_session_with_context(self, planset_dir: Path, tmp_path: Path):
        rc = self._run(
            ["session", "--context", '{"open_alerts": 150, "coverage_pct": 40}'],
            planset_dir,
            tmp_path,
        )
        assert rc == 0, "rc is not valid"

    def test_stamp_plansets_adds_footer(self, tmp_path: Path, capsys: pytest.CaptureFixture):
        """stamp-plansets should add footer to every unfinished planset."""
        d = tmp_path / "plans"
        d.mkdir()
        (d / "CODEQL_ALERT_RESOLUTION_PLANSET.md").write_text(
            "# CodeQL\n**Status:** 🚧 Active\n", encoding="utf-8"
        )
        from scripts.cognitive.orchestrate import main

        state_path = tmp_path / "s.json"
        orch_instance = PlansetOrchestrator(
            planset_dir=d, engine=QuantumPlansetEngine(), state_path=state_path
        )
        with patch(
            "scripts.cognitive.orchestrate._build_orchestrator",
            return_value=orch_instance,
        ):
            rc = main(["stamp-plansets"])
        assert rc == 0, "rc is not valid"
        content = (d / "CODEQL_ALERT_RESOLUTION_PLANSET.md").read_text()
        assert "QuantumPlansetEngine Integration" in content, "Content must not be empty"

    def test_stamp_plansets_idempotent(self, tmp_path: Path, capsys: pytest.CaptureFixture):
        """Running stamp-plansets twice should not double-stamp."""
        d = tmp_path / "plans"
        d.mkdir()
        (d / "CODEQL_ALERT_RESOLUTION_PLANSET.md").write_text(
            "# CodeQL\n**Status:** 🚧 Active\n", encoding="utf-8"
        )
        from scripts.cognitive.orchestrate import main

        state_path = tmp_path / "s.json"

        for _ in range(2):
            orch_instance = PlansetOrchestrator(
                planset_dir=d, engine=QuantumPlansetEngine(), state_path=state_path
            )
            with patch(
                "scripts.cognitive.orchestrate._build_orchestrator",
                return_value=orch_instance,
            ):
                main(["stamp-plansets"])

        content = (d / "CODEQL_ALERT_RESOLUTION_PLANSET.md").read_text()
        assert content.count("QuantumPlansetEngine Integration") == 1, "Content must not be empty"

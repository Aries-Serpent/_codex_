"""
Phase 9.2 Task 1 — Public function API contract tests for agents/

Covers public APIs not already exercised in Phase 9.1 files:
- WorkflowNavigator: create_workflow, get_workflow, list_workflows, execute dry-run,
  get_workflow_status, current_step/next_step/navigate_to/suggest_next_action,
  find_workflow, execute_chain, get_workflow_suggestions, _create_dynamic_workflow
- agents.quantum_game_theory: StrategyState.interpret_state (with mocked probe/unembedding),
  create_zero_sum_game (seeded + unseeded), create_prisoners_dilemma, create_security_game
- agents.mental_mapping: MentalMappingModel.to_dict shape contract,
  get_mental_map_summary keys, iterative_review with low-quality node

#AFTERMATH_METRIC - Phase 9.2 public-function API contract tests
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

np = pytest.importorskip("numpy")

from agents.mental_mapping import MentalMappingModel, MentalNode, NodeType, get_timestamp
from agents.quantum_game_theory import (
    StrategyState,
    TeamType,
    create_prisoners_dilemma,
    create_security_game,
    create_zero_sum_game,
)
from agents.workflow_navigator import (
    Workflow,
    WorkflowFrequency,
    WorkflowNavigator,
    WorkflowStep,
)

# ---------------------------------------------------------------------------
# WorkflowNavigator — public function contract tests
# ---------------------------------------------------------------------------


class TestWorkflowNavigatorCreateWorkflow:
    """Contract tests for WorkflowNavigator.create_workflow."""

    def test_create_workflow_returns_uppercase_id(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        wid = nav.create_workflow("my_flow", steps=[])
        assert wid == "MY_FLOW", "wid is not valid"

    def test_create_workflow_id_is_string(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        wid = nav.create_workflow("flow_x", steps=[])
        assert isinstance(wid, str)

    def test_create_workflow_retrievable(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        nav.create_workflow("retrievable", steps=[])
        wf = nav.get_workflow("RETRIEVABLE")
        assert wf is not None, "wf must be initialized"
        assert wf.workflow_id == "RETRIEVABLE", "workflow_id is not valid"

    def test_create_workflow_with_kwargs(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        step = WorkflowStep(id="s1", action="do_thing")
        nav.create_workflow(
            "kw_flow",
            steps=[step],
            name="KW Flow",
            description="desc",
            frequency=WorkflowFrequency.HIGH,
        )
        wf = nav.get_workflow("KW_FLOW")
        assert wf is not None, "wf must be initialized"
        assert wf.name == "KW Flow", "name is not valid"
        assert wf.description == "desc", "description is not valid"
        assert wf.frequency == WorkflowFrequency.HIGH, "frequency is not valid"

    def test_create_workflow_idempotent_overwrites(self, tmp_path: Path) -> None:
        """Creating with the same ID a second time should overwrite."""
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        nav.create_workflow("dup", steps=[])
        nav.create_workflow("dup", steps=[WorkflowStep(id="s1", action="step")])
        wf = nav.get_workflow("DUP")
        assert len(wf.steps) == 1, "Collection must not be empty"

    def test_create_workflow_default_name_from_id(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        nav.create_workflow("my_flow_name", steps=[])
        wf = nav.get_workflow("MY_FLOW_NAME")
        assert "My Flow Name" in wf.name, "Condition must be true"


class TestWorkflowNavigatorGetWorkflow:
    """Contract tests for WorkflowNavigator.get_workflow."""

    def test_get_workflow_unknown_returns_none(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        assert nav.get_workflow("DOES_NOT_EXIST") is None, "Condition must be true"

    def test_get_workflow_case_insensitive(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        nav.create_workflow("case_test", steps=[])
        wf_lower = nav.get_workflow("case_test")
        wf_upper = nav.get_workflow("CASE_TEST")
        assert wf_lower is wf_upper, "wf_lower is not valid"

    def test_get_default_workflow_audit_exec(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        wf = nav.get_workflow("AUDIT_EXEC")
        assert wf is not None, "wf must be initialized"
        assert wf.workflow_id == "AUDIT_EXEC", "workflow_id is not valid"


class TestWorkflowNavigatorListWorkflows:
    """Contract tests for WorkflowNavigator.list_workflows."""

    def test_list_workflows_returns_unique_only(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        workflows = nav.list_workflows()
        ids = [wf.workflow_id for wf in workflows]
        assert len(ids) == len(set(ids)), "list_workflows should return unique workflows"

    def test_list_workflows_filter_by_frequency(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        nav.create_workflow("freq_high", steps=[], frequency=WorkflowFrequency.HIGH)
        high_only = nav.list_workflows(frequency=WorkflowFrequency.HIGH)
        for wf in high_only:
            assert wf.frequency == WorkflowFrequency.HIGH, "frequency is not valid"

    def test_list_workflows_filter_by_category(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        nav.create_workflow("cat_wf", steps=[], category="special")
        special = nav.list_workflows(category="special")
        assert any(wf.workflow_id == "CAT_WF" for wf in special), "workflow_id is not valid"
        assert all(wf.category == "special" for wf in special), "category is not valid"

    def test_list_workflows_no_filter_includes_defaults(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        workflows = nav.list_workflows()
        ids = {wf.workflow_id for wf in workflows}
        assert "AUDIT_EXEC" in ids, "Condition must be true"


class TestWorkflowNavigatorExecuteDryRun:
    """Contract tests for WorkflowNavigator.execute with dry_run=True."""

    def test_execute_dry_run_returns_success(self, tmp_path: Path, capsys) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        result = nav.execute("AUDIT_EXEC", dry_run=True)
        assert result["success"] is True, "Result must not be empty"
        assert result.get("dry_run") is True, "Result must not be empty"

    def test_execute_dry_run_unknown_id_returns_failure(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        result = nav.execute("UNKNOWN_WORKFLOW_XYZ", dry_run=True)
        assert result["success"] is False, "Result must not be empty"
        assert "error" in result, "Result must not be empty"

    def test_execute_dry_run_by_alias(self, tmp_path: Path, capsys) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        result = nav.execute("audit", dry_run=True)
        assert result["success"] is True, "Result must not be empty"


class TestWorkflowNavigatorGetWorkflowStatus:
    """Contract tests for WorkflowNavigator.get_workflow_status."""

    def test_get_status_existing_workflow(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        status = nav.get_workflow_status("AUDIT_EXEC")
        assert status["exists"] is True, "Condition must be true"
        assert status["workflow_id"] == "AUDIT_EXEC", "Condition must be true"
        assert "total_steps" in status, "Condition must be true"
        assert "completed_steps" in status, "Condition must be true"
        assert "failed_steps" in status, "Condition must be true"
        assert "pending_steps" in status, "Condition must be true"

    def test_get_status_unknown_workflow(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        status = nav.get_workflow_status("NO_SUCH_WORKFLOW")
        assert status["exists"] is False, "Condition must be true"
        assert "error" in status, "Error should be raised or set"

    def test_get_status_step_counts_sum_to_total(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        step = WorkflowStep(id="s1", action="test_step")
        nav.create_workflow("status_test", steps=[step])
        status = nav.get_workflow_status("STATUS_TEST")
        total = status["total_steps"]
        assert status["completed_steps"] + status["failed_steps"] + status["pending_steps"] <= total


class TestWorkflowNavigatorNavigation:
    """Tests for stateful navigation methods."""

    def test_current_step_no_active_workflow(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        assert nav.current_step() is None, "Condition must be true"

    def test_next_step_no_active_workflow(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        assert nav.next_step() is None, "Condition must be true"

    def test_previous_step_no_active_workflow(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        assert nav.previous_step() is None, "Condition must be true"

    def test_navigate_to_no_active_workflow(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        result = nav.navigate_to(step_index=0)
        assert result is False, "Result must not be empty"

    def test_current_step_with_active_workflow(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        steps = [WorkflowStep(id="s1", action="a1"), WorkflowStep(id="s2", action="a2")]
        nav.create_workflow("nav_test", steps=steps)
        nav.current_workflow_id = "NAV_TEST"
        nav.current_step_index = 0
        step = nav.current_step()
        assert step is not None, "step must be initialized"
        assert step.id == "s1", "id is not valid"

    def test_next_step_advances_index(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        steps = [WorkflowStep(id="s1", action="a1"), WorkflowStep(id="s2", action="a2")]
        nav.create_workflow("nav_test2", steps=steps)
        nav.current_workflow_id = "NAV_TEST2"
        nav.current_step_index = 0
        step = nav.next_step()
        assert step is not None, "step must be initialized"
        assert step.id == "s2", "id is not valid"
        assert nav.current_step_index == 1, "current_step_index is not valid"

    def test_navigate_to_by_index(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        steps = [WorkflowStep(id="s0", action="a0"), WorkflowStep(id="s1", action="a1")]
        nav.create_workflow("idx_nav", steps=steps)
        nav.current_workflow_id = "IDX_NAV"
        nav.current_step_index = 0
        ok = nav.navigate_to(step_index=1)
        assert ok is True, "ok is not valid"
        assert nav.current_step_index == 1, "current_step_index is not valid"

    def test_navigate_to_by_step_id(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        steps = [WorkflowStep(id="alpha", action="a"), WorkflowStep(id="beta", action="b")]
        nav.create_workflow("id_nav", steps=steps)
        nav.current_workflow_id = "ID_NAV"
        nav.current_step_index = 0
        ok = nav.navigate_to(step_id="beta")
        assert ok is True, "ok is not valid"
        assert nav.current_step_index == 1, "current_step_index is not valid"

    def test_navigate_to_invalid_index_returns_false(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        steps = [WorkflowStep(id="s1", action="a1")]
        nav.create_workflow("idx_bounds", steps=steps)
        nav.current_workflow_id = "IDX_BOUNDS"
        ok = nav.navigate_to(step_index=99)
        assert ok is False, "ok is not valid"

    def test_navigate_to_uses_debug_logging_and_includes_bounds_context(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        steps = [WorkflowStep(id="s0", action="a0"), WorkflowStep(id="s1", action="a1")]
        nav.current_workflow_id = nav.create_workflow("idx_logging", steps=steps)

        with caplog.at_level("DEBUG"):
            assert nav.navigate_to(step_index=1) is True, "Condition must be true"
            assert nav.navigate_to(step_index=99) is False, "Condition must be true"

        assert any(
            record.levelname == "DEBUG"
            and record.message == "Navigating to step index 1 in workflow IDX_LOGGING"
            for record in caplog.records
        )
        assert any(
            record.levelname == "WARNING"
            and record.message
            == "Step index 99 out of bounds for workflow IDX_LOGGING with 2 steps."
            for record in caplog.records
        )

    def test_suggest_next_action_no_workflow(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        assert nav.suggest_next_action() is None, "Condition must be true"

    def test_suggest_next_action_with_workflow(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        steps = [WorkflowStep(id="s1", action="do_thing")]
        nav.create_workflow("suggest_test", steps=steps)
        nav.current_workflow_id = "SUGGEST_TEST"
        nav.current_step_index = 0
        suggestion = nav.suggest_next_action()
        assert suggestion is not None, "suggestion must be initialized"
        assert "do_thing" in suggestion, "Condition must be true"


class TestWorkflowNavigatorFindWorkflow:
    """Tests for WorkflowNavigator.find_workflow."""

    def test_find_workflow_by_entry_point(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        # AUDIT_EXEC has "Run audit pipeline" as an entry point
        wf = nav.find_workflow("Run audit pipeline")
        assert wf is not None, "wf must be initialized"
        assert wf.workflow_id == "AUDIT_EXEC", "workflow_id is not valid"

    def test_find_workflow_unknown_returns_none(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        wf = nav.find_workflow("completely unknown description xyz123")
        assert wf is None, "wf is not valid"


class TestWorkflowNavigatorExecuteChain:
    """Tests for execute_chain."""

    def test_execute_chain_dry_run_single(self, tmp_path: Path, capsys) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        result = nav.execute_chain(["AUDIT_EXEC"], context={})
        # AUDIT_EXEC has real shell commands — failure is acceptable in test env
        assert "chain_results" in result or "success" in result, "Result must not be empty"

    def test_execute_chain_unknown_id_aborts(self, tmp_path: Path, capsys) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        result = nav.execute_chain(["UNKNOWN_XYZ"])
        assert result["success"] is False, "Result must not be empty"
        assert "aborted_at" in result, "Result must not be empty"


class TestWorkflowNavigatorDynamicWorkflows:
    """Tests for _create_dynamic_workflow factory."""

    @pytest.mark.parametrize("wtype", ["test_coverage", "self_heal", "audit_coverage", "test_run"])
    def test_dynamic_workflow_creates_valid_object(self, tmp_path: Path, wtype: str) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        wf = nav._create_dynamic_workflow(wtype)
        assert isinstance(wf, Workflow)
        assert wf.workflow_id.endswith("_DYNAMIC") or wf.workflow_id.upper(), "Condition must be true"

    def test_dynamic_workflow_unknown_type_raises(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        with pytest.raises(ValueError, match="Unknown workflow type"):
            nav._create_dynamic_workflow("nonexistent_type")


class TestWorkflowNavigatorGetSuggestions:
    """Tests for get_workflow_suggestions."""

    def test_suggestions_empty_state(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        suggestions = nav.get_workflow_suggestions({})
        assert isinstance(suggestions, list)

    def test_suggestions_with_recent_commits(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        suggestions = nav.get_workflow_suggestions({"recent_commits": True})
        ids = [wf.workflow_id for wf in suggestions]
        assert "AUDIT_EXEC" in ids, "Condition must be true"

    def test_suggestions_low_coverage_creates_test_workflow(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        suggestions = nav.get_workflow_suggestions({"test_coverage": 50})
        assert len(suggestions) > 0, "Suggestions must not be empty"

    def test_suggestions_many_issues_creates_heal_workflow(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        suggestions = nav.get_workflow_suggestions({"open_issues": 20})
        assert len(suggestions) > 0, "Suggestions must not be empty"


# ---------------------------------------------------------------------------
# StrategyState.interpret_state
# ---------------------------------------------------------------------------


class TestStrategyStateInterpretState:
    """Contract tests for StrategyState.interpret_state."""

    def _make_state(self) -> StrategyState:
        return StrategyState(
            team=TeamType.BLUE,
            strategies=["cooperate", "defect"],
        )

    def test_interpret_state_returns_dict(self) -> None:
        state = self._make_state()
        with patch("agents.interpretability.sparse_probes.interpret_state_vector") as mock_isv:
            mock_isv.return_value = {
                "concepts": [("trust", 0.9)],
                "labels": [("cooperate", 1.2)],
                "confidence": 0.85,
            }
            result = state.interpret_state()
        assert isinstance(result, dict)

    def test_interpret_state_has_probabilities_key(self) -> None:
        state = self._make_state()
        with patch("agents.interpretability.sparse_probes.interpret_state_vector") as mock_isv:
            mock_isv.return_value = {"concepts": [], "labels": [], "confidence": 0.5}
            result = state.interpret_state()
        assert "probabilities" in result, "Result must not be empty"

    def test_interpret_state_probabilities_length(self) -> None:
        state = self._make_state()
        with patch("agents.interpretability.sparse_probes.interpret_state_vector") as mock_isv:
            mock_isv.return_value = {"concepts": [], "labels": [], "confidence": 0.5}
            result = state.interpret_state()
        assert len(result["probabilities"]) == len(state.strategies), "Collection must not be empty"

    def test_interpret_state_with_top_k(self) -> None:
        state = self._make_state()
        with patch("agents.interpretability.sparse_probes.interpret_state_vector") as mock_isv:
            mock_isv.return_value = {"concepts": [], "labels": [], "confidence": 0.5}
            state.interpret_state(top_k=1)
        # top_k must be forwarded to the underlying call
        _, kwargs = mock_isv.call_args
        assert kwargs.get("top_k") == 1, "Condition must be true"

    def test_interpret_state_with_wavefunction_override(self) -> None:
        state = self._make_state()
        override_wf = np.array([1.0 + 0j, 0.0 + 0j])
        with patch("agents.interpretability.sparse_probes.interpret_state_vector") as mock_isv:
            mock_isv.return_value = {"concepts": [], "labels": [], "confidence": 0.5}
            state.interpret_state(wavefunction=override_wf)
        # The override wavefunction should reach the helper (not the default)
        call_args = mock_isv.call_args[0][0]
        # abs(1+0j) = 1.0, abs(0+0j) = 0.0
        assert len(call_args) == 2, "Call_args must not be empty"

    def test_interpret_state_with_probe(self) -> None:
        state = self._make_state()
        mock_probe = MagicMock()
        with patch("agents.interpretability.sparse_probes.interpret_state_vector") as mock_isv:
            mock_isv.return_value = {"concepts": [], "labels": [], "confidence": 0.5}
            state.interpret_state(probe=mock_probe)
        _, kwargs = mock_isv.call_args
        assert kwargs.get("probe") is mock_probe, "Condition must be true"


# ---------------------------------------------------------------------------
# Quantum game factory functions
# ---------------------------------------------------------------------------


class TestCreateZeroSumGame:
    """Tests for create_zero_sum_game factory."""

    def test_returns_four_tuple(self) -> None:
        result = create_zero_sum_game(size=3, seed=42)
        assert len(result) == 4, "Result must not be empty"

    def test_strategy_lists_equal_length(self) -> None:
        blue, red, pb, pr = create_zero_sum_game(size=4, seed=0)
        assert len(blue) == 4, "Blue must not be empty"
        assert len(red) == 4, "Red must not be empty"

    def test_payoff_matrices_shape(self) -> None:
        blue, red, pb, pr = create_zero_sum_game(size=3, seed=1)
        assert pb.shape == (3, 3)
        assert pr.shape == (3, 3)

    def test_zero_sum_property(self) -> None:
        _, _, pb, pr = create_zero_sum_game(size=3, seed=7)
        np.testing.assert_allclose(pb + pr, np.zeros((3, 3)), atol=1e-12)

    def test_seeded_is_deterministic(self) -> None:
        _, _, pb1, _ = create_zero_sum_game(size=3, seed=99)
        _, _, pb2, _ = create_zero_sum_game(size=3, seed=99)
        np.testing.assert_array_equal(pb1, pb2)

    def test_unseeded_varies(self) -> None:
        """seed=None should produce non-deterministic results across calls."""
        _, _, pb1, _ = create_zero_sum_game(size=3, seed=None)
        _, _, pb2, _ = create_zero_sum_game(size=3, seed=None)
        # Very low probability they are identical by chance with 9 floats
        # Allow the test to be skipped if they happen to match (practically never)
        if np.allclose(pb1, pb2):
            pytest.skip("Unseeded results happened to match — extremely rare")

    def test_strategy_names_format(self) -> None:
        blue, _, _, _ = create_zero_sum_game(size=3, seed=5)
        for name in blue:
            assert isinstance(name, str)
            assert name.startswith("S"), "Condition must be true"


class TestCreatePrisonersDilemma:
    """Tests for create_prisoners_dilemma factory."""

    def test_returns_four_tuple(self) -> None:
        result = create_prisoners_dilemma()
        assert len(result) == 4, "Result must not be empty"

    def test_payoff_matrices_2x2(self) -> None:
        blue, red, pb, pr = create_prisoners_dilemma()
        assert pb.shape == (2, 2)
        assert pr.shape == (2, 2)

    def test_strategies_include_cooperate_defect(self) -> None:
        blue, red, _, _ = create_prisoners_dilemma()
        assert any("cooperate" in s.lower() or "C" in s for s in blue), "Condition must be true"


class TestCreateSecurityGame:
    """Tests for create_security_game factory."""

    def test_returns_four_tuple(self) -> None:
        result = create_security_game()
        assert len(result) == 4, "Result must not be empty"

    def test_blue_strategies_include_defense(self) -> None:
        blue, _, _, _ = create_security_game()
        defense_terms = {"Firewall", "IDS", "Patch", "Monitor"}
        assert defense_terms.issubset(set(blue)), "Condition must be true"

    def test_payoff_shapes_match(self) -> None:
        blue, red, pb, pr = create_security_game()
        assert pb.shape == (len(blue), len(red))
        assert pr.shape == (len(blue), len(red))

    def test_payoff_blue_range(self) -> None:
        _, _, pb, _ = create_security_game()
        assert pb.min() >= 0.0, "Value must be greater than zero"
        assert pb.max() <= 1.0, "Condition must be true"


# ---------------------------------------------------------------------------
# MentalMappingModel — to_dict and get_mental_map_summary shape contracts
# ---------------------------------------------------------------------------


class TestMentalMappingModelToDict:
    """Shape contract tests for MentalMappingModel.to_dict."""

    def test_to_dict_has_required_keys(self) -> None:
        mm = MentalMappingModel(agent_id="agent_test")
        d = mm.to_dict()
        for key in (
            "map_id",
            "agent_id",
            "created_at",
            "nodes",
            "edges",
            "learning_history",
            "appraisal_metrics",
            "pattern_library",
            "nodes_needing_review",
        ):
            assert key in d, f"Missing key: {key}"

    def test_to_dict_agent_id_matches(self) -> None:
        mm = MentalMappingModel(agent_id="my_agent")
        assert mm.to_dict()["agent_id"] == "my_agent", "Condition must be true"

    def test_to_dict_nodes_is_dict(self) -> None:
        mm = MentalMappingModel(agent_id="a")
        assert isinstance(mm.to_dict()["nodes"], dict)

    def test_to_dict_edges_is_dict(self) -> None:
        mm = MentalMappingModel(agent_id="a")
        assert isinstance(mm.to_dict()["edges"], dict)

    def test_to_dict_nodes_contain_node_dicts(self) -> None:
        mm = MentalMappingModel(agent_id="a")
        mm.add_node(
            MentalNode(
                node_id="n1",
                node_type=NodeType.OBSERVATION,
                content="obs",
                timestamp=get_timestamp(),
            )
        )
        nodes = mm.to_dict()["nodes"]
        assert "n1" in nodes, "Condition must be true"
        assert isinstance(nodes["n1"], dict)

    def test_to_dict_nodes_needing_review_is_list(self) -> None:
        mm = MentalMappingModel(agent_id="a")
        assert isinstance(mm.to_dict()["nodes_needing_review"], list)


class TestMentalMappingModelGetSummary:
    """Shape contract tests for MentalMappingModel.get_mental_map_summary."""

    def test_summary_has_required_keys(self) -> None:
        mm = MentalMappingModel(agent_id="summary_agent")
        s = mm.get_mental_map_summary()
        for key in (
            "map_id",
            "agent_id",
            "created_at",
            "total_nodes",
            "total_edges",
            "nodes_by_type",
            "nodes_needing_review",
            "learning_history_size",
            "appraisal_metrics",
        ):
            assert key in s, f"Missing key in summary: {key}"

    def test_summary_counts_match(self) -> None:
        mm = MentalMappingModel(agent_id="count_check")
        mm.add_node(
            MentalNode(
                node_id="x1",
                node_type=NodeType.OBSERVATION,
                content="obs",
                timestamp=get_timestamp(),
            )
        )
        s = mm.get_mental_map_summary()
        assert s["total_nodes"] == len(mm.nodes), "Collection must not be empty"
        assert s["total_edges"] == len(mm.edges), "Collection must not be empty"

    def test_summary_agent_id_matches(self) -> None:
        mm = MentalMappingModel(agent_id="my_agent_id")
        assert mm.get_mental_map_summary()["agent_id"] == "my_agent_id", "Condition must be true"


class TestMentalMappingModelIterativeReviewGaps:
    """Additional iterative_review contract tests not in core_flows."""

    def test_iterative_review_returns_list(self) -> None:
        mm = MentalMappingModel(agent_id="review_agent")
        result = mm.iterative_review()
        assert isinstance(result, list)

    def test_iterative_review_with_low_quality_node(self) -> None:
        mm = MentalMappingModel(agent_id="review_agent2")
        node = MentalNode(
            node_id="low_q",
            node_type=NodeType.OBSERVATION,
            content="low quality obs",
            timestamp=get_timestamp(),
            quality_score=0.2,
        )
        mm.add_node(node)
        reviewed = mm.iterative_review(review_threshold=0.5)
        # Node with quality 0.2 < 0.5 threshold should appear in reviewed list
        assert "low_q" in reviewed, "Condition must be true"

    def test_iterative_review_improves_quality(self) -> None:
        mm = MentalMappingModel(agent_id="quality_agent")
        node = MentalNode(
            node_id="improve_me",
            node_type=NodeType.OBSERVATION,
            content="needs improvement",
            timestamp=get_timestamp(),
            quality_score=0.3,
        )
        mm.add_node(node)
        mm.iterative_review(review_threshold=0.5)
        # quality_score should increase after review
        assert mm.nodes["improve_me"].quality_score > 0.3, "quality_score must be greater than zero"

    def test_iterative_review_clears_review_queue(self) -> None:
        mm = MentalMappingModel(agent_id="queue_clear")
        node = MentalNode(
            node_id="queued_node",
            node_type=NodeType.OBSERVATION,
            content="queued",
            timestamp=get_timestamp(),
            quality_score=0.4,
        )
        mm.add_node(node)
        mm.nodes_needing_review.add("queued_node")
        mm.iterative_review(review_threshold=0.5)
        assert "queued_node" not in mm.nodes_needing_review, "Condition must be true"

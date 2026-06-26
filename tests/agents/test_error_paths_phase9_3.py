"""
Phase 9.3 — Error Path Coverage: agents/ modules

Covers exception-handling and error-recovery code paths that were not yet
reached by Phase 9.1 / 9.2 happy-path tests:

  - WorkflowStep.execute: failed command, optional-command pass-through,
    exception in execute block
  - WorkflowNavigator.create_workflow_template: unknown workflow type
  - QuantumInspiredGameEngine.__init__: TypeError when numpy absent
  - BlueRedTeamSimulator methods: TypeError when numpy absent
  - MentalMap.add_edge: TypeError for non-string IDs, ValueError for
    nodes that don't exist
  - SQLiteMemoryStore.__init__: ValueError for disallowed path
  - EnergyLandscape.minimize_free_energy: ValueError when states empty
  - SwarmIntelligence.run_optimization: ValueError when no function given
  - PathQuantumSuperposition.measure_optimal_path: ValueError when empty
  - AgentImportError, AgentConfigError, AgentValidationError,
    AgentExecutionError, EntanglementError, GaugeError hierarchy
  - SimpleMemoryAdapter: store / retrieve / delete / clear / get_history

#AFTERMATH_METRIC - Phase 9.3 error-path coverage tests
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agents.exceptions import (
    AgentConfigError,
    AgentError,
    AgentExecutionError,
    AgentImportError,
    AgentValidationError,
    EntanglementError,
    GaugeError,
)
from agents.mental_mapping import MentalMap, NodeType
from agents.workflow_navigator import (
    StepStatus,
    WorkflowNavigator,
    WorkflowStep,
)

# ---------------------------------------------------------------------------
# WorkflowStep.execute — error paths
# ---------------------------------------------------------------------------


class TestWorkflowStepExecuteErrors:
    """Error paths in WorkflowStep.execute."""

    def test_execute_command_failure_non_optional_returns_failure(self, tmp_path: Path) -> None:
        """A failing command on a non-optional step returns success=False."""
        step = WorkflowStep(id="fail_step", action="fail", command="false")
        result = step.execute({"working_dir": str(tmp_path)})
        assert result["success"] is False, "Result must not be empty"
        assert step.status == StepStatus.FAILED, "status is not valid"

    def test_execute_command_failure_optional_returns_success(self, tmp_path: Path) -> None:
        """A failing command on an *optional* step still returns success=True."""
        step = WorkflowStep(id="opt_step", action="opt", command="false", optional=True)
        result = step.execute({"working_dir": str(tmp_path)})
        assert result["success"] is True, "Result must not be empty"
        assert step.status == StepStatus.COMPLETED, "status is not valid"

    def test_execute_command_success_returns_stdout(self, tmp_path: Path) -> None:
        """A successful command returns success=True and captures stdout."""
        step = WorkflowStep(id="ok_step", action="echo", command="echo hello")
        result = step.execute({"working_dir": str(tmp_path)})
        assert result["success"] is True, "Result must not be empty"
        assert "hello" in result.get("stdout", "")
        assert step.status == StepStatus.COMPLETED, "status is not valid"

    def test_execute_exception_sets_failed_status(self) -> None:
        """An unexpected exception in execute returns success=False and FAILED status."""
        step = WorkflowStep(id="exc_step", action="boom", command="nonexistentcmd__xyz")
        # On systems without the command this raises FileNotFoundError inside subprocess,
        # which is caught by the broad except clause.
        result = step.execute({})
        assert result["success"] is False, "Result must not be empty"
        assert step.status == StepStatus.FAILED, "status is not valid"
        assert "error" in result, "Result must not be empty"

    def test_execute_uses_branch_returns_success(self) -> None:
        """A step with 'uses' (no command) returns success=True."""
        step = WorkflowStep(id="uses_step", action="use", uses="some.module")
        result = step.execute({})
        assert result["success"] is True, "Result must not be empty"
        assert step.status == StepStatus.COMPLETED, "status is not valid"
        assert "Would execute: some.module" in result.get("message", "")

    def test_execute_no_action_returns_skipped(self) -> None:
        """A step with no command and no uses is SKIPPED."""
        step = WorkflowStep(id="noop_step", action="noop")
        result = step.execute({})
        assert result["success"] is True, "Result must not be empty"
        assert step.status == StepStatus.SKIPPED, "status is not valid"
        assert "No action defined" in result.get("message", "")


# ---------------------------------------------------------------------------
# WorkflowNavigator._create_dynamic_workflow — unknown type raises ValueError
# ---------------------------------------------------------------------------


class TestWorkflowNavigatorTemplateErrors:
    """Error paths in WorkflowNavigator._create_dynamic_workflow."""

    def test_unknown_workflow_type_raises_value_error(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        with pytest.raises(ValueError, match="Unknown workflow type"):
            nav._create_dynamic_workflow("nonexistent_type_xyz")

    def test_known_workflow_types_do_not_raise(self, tmp_path: Path) -> None:
        nav = WorkflowNavigator(workspace_dir=tmp_path)
        for wf_type in ("test_coverage", "self_heal", "audit_coverage", "test_run"):
            wf = nav._create_dynamic_workflow(wf_type)
            assert wf is not None, "wf must be initialized"


# ---------------------------------------------------------------------------
# MentalMap.add_edge — TypeError and ValueError error paths
# ---------------------------------------------------------------------------


class TestMentalMapAddEdgeErrors:
    """Error paths in MentalMap.add_edge."""

    def _make_map_with_nodes(self) -> MentalMap:
        m = MentalMap()
        node_a = m.create_node(NodeType.CONCEPT, content="Node A")
        node_b = m.create_node(NodeType.CONCEPT, content="Node B")
        # Store the IDs so tests can reference them
        m._test_id_a = node_a.node_id
        m._test_id_b = node_b.node_id
        return m

    def test_non_string_source_id_raises_type_error(self) -> None:
        m = self._make_map_with_nodes()
        with pytest.raises(TypeError, match="source_id and target_id must be strings"):
            m.connect_nodes(123, m._test_id_b)  # type: ignore[arg-type]

    def test_non_string_target_id_raises_type_error(self) -> None:
        m = self._make_map_with_nodes()
        with pytest.raises(TypeError, match="source_id and target_id must be strings"):
            m.connect_nodes(m._test_id_a, 456)  # type: ignore[arg-type]

    def test_both_non_string_raises_type_error(self) -> None:
        m = self._make_map_with_nodes()
        with pytest.raises(TypeError, match="source_id and target_id must be strings"):
            m.connect_nodes(1, 2)  # type: ignore[arg-type]

    def test_missing_source_node_raises_value_error(self) -> None:
        m = self._make_map_with_nodes()
        with pytest.raises(ValueError, match="Both nodes must exist in the map"):
            m.connect_nodes("nonexistent", m._test_id_b)

    def test_missing_target_node_raises_value_error(self) -> None:
        m = self._make_map_with_nodes()
        with pytest.raises(ValueError, match="Both nodes must exist in the map"):
            m.connect_nodes(m._test_id_a, "nonexistent")

    def test_both_nodes_missing_raises_value_error(self) -> None:
        m = self._make_map_with_nodes()
        with pytest.raises(ValueError, match="Both nodes must exist in the map"):
            m.connect_nodes("x", "y")

    def test_valid_edge_succeeds(self) -> None:
        m = self._make_map_with_nodes()
        edge = m.connect_nodes(m._test_id_a, m._test_id_b)
        assert edge is not None, "edge must be initialized"


# ---------------------------------------------------------------------------
# AgentMemory — disallowed path raises ValueError
# ---------------------------------------------------------------------------


class TestAgentMemoryErrors:
    """Error paths in AgentMemory.__init__."""

    def test_disallowed_path_raises_value_error(self) -> None:
        from agents.agent_memory import AgentMemory

        # /etc is outside home, cwd, and /tmp — should always be disallowed
        with pytest.raises(ValueError, match="outside allowed directories"):
            AgentMemory(db_path=Path("/etc/codex_test_db.sqlite"))

    def test_allowed_path_tmp_succeeds(self, tmp_path: Path) -> None:
        from agents.agent_memory import AgentMemory

        db_path = tmp_path / "test_memory.db"
        store = AgentMemory(db_path=db_path)
        assert store is not None, "store must be initialized"


# ---------------------------------------------------------------------------
# EnergyLandscape.minimize_free_energy — ValueError when no states
# ---------------------------------------------------------------------------


class TestEnergyLandscapeErrors:
    """Error paths in EnergyLandscape."""

    def test_minimize_free_energy_empty_raises(self) -> None:
        from agents.physics_orchestrator import EnergyLandscape

        landscape = EnergyLandscape(temperature=1.0)
        with pytest.raises(ValueError, match="No states in landscape"):
            landscape.minimize_free_energy()

    def test_select_state_empty_returns_none(self) -> None:
        from agents.physics_orchestrator import EnergyLandscape

        landscape = EnergyLandscape(temperature=1.0)
        result = landscape.select_state()
        assert result is None, "Result must not be empty"


# ---------------------------------------------------------------------------
# SwarmIntelligence.run_optimization — ValueError when no function
# ---------------------------------------------------------------------------


class TestSwarmIntelligenceErrors:
    """Error paths in SwarmIntelligence.run_optimization."""

    def test_run_optimization_no_function_raises(self) -> None:
        from agents.physics_orchestrator import SwarmIntelligence

        swarm = SwarmIntelligence(dimensions=2, num_particles=3)
        with pytest.raises(ValueError, match="Either fitness_function or objective_function"):
            swarm.run_optimization()

    def test_run_optimization_with_objective_function_succeeds(self) -> None:
        from agents.physics_orchestrator import SwarmIntelligence

        swarm = SwarmIntelligence(dimensions=2, num_particles=3)
        result = swarm.run_optimization(
            objective_function=lambda pos: -sum(x**2 for x in pos),
            bounds=[(-1.0, 1.0), (-1.0, 1.0)],
            max_iterations=2,
        )
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# SuperpositionExplorer.measure_optimal_path — ValueError when empty
# ---------------------------------------------------------------------------


class TestSuperpositionExplorerErrors:
    """Error paths in SuperpositionExplorer."""

    def test_measure_optimal_path_empty_raises(self) -> None:
        from agents.physics_orchestrator import SuperpositionExplorer

        explorer = SuperpositionExplorer()
        with pytest.raises(ValueError, match="No paths in superposition"):
            explorer.measure_optimal_path()


# ---------------------------------------------------------------------------
# QuantumInspiredGameEngine — TypeError when numpy absent
# ---------------------------------------------------------------------------


class TestQuantumInspiredGameEngineErrors:
    """Error paths in QuantumInspiredGameEngine when numpy is unavailable."""

    def test_init_without_numpy_raises_type_error(self) -> None:
        import agents.quantum_game_theory as qgt_module

        original = qgt_module.NUMPY_AVAILABLE
        try:
            qgt_module.NUMPY_AVAILABLE = False
            with pytest.raises(TypeError, match="QuantumInspiredGameEngine requires numpy"):
                qgt_module.QuantumInspiredGameEngine(blue_strategies=["a"], red_strategies=["b"])
        finally:
            qgt_module.NUMPY_AVAILABLE = original


# ---------------------------------------------------------------------------
# BlueRedTeamSimulator — TypeError when numpy absent
# ---------------------------------------------------------------------------


class TestBlueRedTeamSimulatorErrors:
    """Error paths in BlueRedTeamSimulator when numpy is unavailable."""

    def test_evaluate_hypothesis_without_numpy_raises(self) -> None:
        import agents.quantum_game_theory as qgt_module

        original = qgt_module.NUMPY_AVAILABLE
        try:
            qgt_module.NUMPY_AVAILABLE = True
            sim = qgt_module.BlueRedTeamSimulator(
                blue_strategies=["a"],
                red_strategies=["b"],
            )
            qgt_module.NUMPY_AVAILABLE = False
            with pytest.raises(TypeError, match="requires numpy for hypothesis evaluation"):
                sim.evaluate_hypothesis("test hypothesis")
        finally:
            qgt_module.NUMPY_AVAILABLE = original

    def test_compare_strategies_without_numpy_raises(self) -> None:
        import agents.quantum_game_theory as qgt_module

        original = qgt_module.NUMPY_AVAILABLE
        try:
            qgt_module.NUMPY_AVAILABLE = True
            sim = qgt_module.BlueRedTeamSimulator(
                blue_strategies=["a"],
                red_strategies=["b"],
            )
            qgt_module.NUMPY_AVAILABLE = False
            with pytest.raises(TypeError, match="requires numpy for strategy comparison"):
                sim.compare_strategies(blue_options=[], red_options=[])
        finally:
            qgt_module.NUMPY_AVAILABLE = original

    def test_run_simulation_without_numpy_raises(self) -> None:
        import agents.quantum_game_theory as qgt_module

        original = qgt_module.NUMPY_AVAILABLE
        try:
            qgt_module.NUMPY_AVAILABLE = True
            sim = qgt_module.BlueRedTeamSimulator(
                blue_strategies=["a"],
                red_strategies=["b"],
            )
            qgt_module.NUMPY_AVAILABLE = False
            with pytest.raises(TypeError, match="requires numpy for simulation"):
                sim.run_simulation()
        finally:
            qgt_module.NUMPY_AVAILABLE = original


# ---------------------------------------------------------------------------
# AgentImportError and exception hierarchy
# ---------------------------------------------------------------------------


class TestAgentExceptionHierarchy:
    """Validate custom exception constructors and hierarchy."""

    def test_agent_import_error_message_without_extra(self) -> None:
        err = AgentImportError("numpy")
        assert "numpy" in str(err), "Condition must be true"
        assert "pip install numpy" in str(err), "Condition must be true"
        assert isinstance(err, AgentError)
        assert isinstance(err, ImportError)

    def test_agent_import_error_message_with_extra(self) -> None:
        err = AgentImportError("torch", extra="ml")
        assert "torch" in str(err), "Condition must be true"
        assert "codex-ml[ml]" in str(err), "Condition must be true"

    def test_agent_import_error_with_package_name(self) -> None:
        err = AgentImportError("sklearn", package_name="scikit-learn")
        assert "sklearn" in str(err), "Condition must be true"
        assert "scikit-learn" in str(err), "Condition must be true"

    def test_agent_config_error_is_value_error(self) -> None:
        err = AgentConfigError("bad config")
        assert isinstance(err, ValueError)
        assert isinstance(err, AgentError)
        assert "bad config" in str(err), "Condition must be true"

    def test_agent_validation_error_is_value_error(self) -> None:
        err = AgentValidationError("invariant violated")
        assert isinstance(err, ValueError)
        assert isinstance(err, AgentError)

    def test_agent_execution_error_is_runtime_error(self) -> None:
        err = AgentExecutionError("execution failed")
        assert isinstance(err, RuntimeError)
        assert isinstance(err, AgentError)

    def test_entanglement_error_hierarchy(self) -> None:
        err = EntanglementError("entanglement failure")
        assert isinstance(err, AgentError)
        assert "entanglement failure" in str(err), "Condition must be true"

    def test_gauge_error_hierarchy(self) -> None:
        err = GaugeError("gauge symmetry broken")
        assert isinstance(err, AgentError)
        assert "gauge symmetry broken" in str(err), "Condition must be true"

    def test_raise_and_catch_agent_import_error_as_agent_error(self) -> None:
        with pytest.raises(AgentError):
            raise AgentImportError("scipy")

    def test_raise_and_catch_agent_import_error_as_import_error(self) -> None:
        with pytest.raises(ImportError):
            raise AgentImportError("scipy")


# ---------------------------------------------------------------------------
# SimpleMemoryAdapter → SimpleDictMemory — store / retrieve / delete / clear / get_history
# ---------------------------------------------------------------------------


class TestSimpleMemoryAdapterOperations:
    """Covers SimpleDictMemory store / retrieve / delete / clear / get_history."""

    def _make_adapter(self):
        from agents.cognitive_adapter import SimpleDictMemory

        return SimpleDictMemory()

    def test_store_and_retrieve(self) -> None:
        adapter = self._make_adapter()
        ok = adapter.store("key1", "value1")
        assert ok is True, "ok is not valid"
        assert adapter.retrieve("key1") == "value1", "Value must be initialized"

    def test_retrieve_missing_key_returns_none(self) -> None:
        adapter = self._make_adapter()
        assert adapter.retrieve("no_such_key") is None, "Condition must be true"

    def test_delete_existing_key(self) -> None:
        adapter = self._make_adapter()
        adapter.store("k", "v")
        ok = adapter.delete("k")
        assert ok is True, "ok is not valid"
        assert adapter.retrieve("k") is None, "Condition must be true"

    def test_delete_non_existing_key_returns_true(self) -> None:
        adapter = self._make_adapter()
        result = adapter.delete("ghost_key")
        assert result is True, "Result must not be empty"

    def test_clear_removes_all_entries(self) -> None:
        adapter = self._make_adapter()
        adapter.store("a", 1)
        adapter.store("b", 2)
        ok = adapter.clear()
        assert ok is True, "ok is not valid"
        assert adapter.retrieve("a") is None, "Condition must be true"
        assert adapter.retrieve("b") is None, "Condition must be true"

    def test_get_history_returns_most_recent_first(self) -> None:
        adapter = self._make_adapter()
        adapter.store("seq", "v1")
        adapter.store("seq", "v2")
        history = adapter.get_history("seq")
        assert len(history) >= 2, "History must not be empty"
        # Most recent is first
        _, val = history[0]
        assert val == "v2", "val is not valid"

    def test_get_history_missing_key_returns_empty(self) -> None:
        adapter = self._make_adapter()
        assert adapter.get_history("nope") == [], "Condition must be true"

    def test_search_by_metadata(self) -> None:
        adapter = self._make_adapter()
        adapter.store("x", 42, metadata={"tag": "important"})
        adapter.store("y", 99, metadata={"tag": "other"})
        results = adapter.search({"tag": "important"})
        assert len(results) >= 1, "Results must not be empty"
        keys = [k for k, _ in results]
        assert "x" in keys, "Condition must be true"

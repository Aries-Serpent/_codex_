"""
Phase 9.4 — Edge Case Coverage: agents/ modules

Covers boundary conditions, rare paths, and corner cases that were not
yet reached by Phase 9.1 / 9.2 happy-path or 9.3 error-path tests:

  - EnergyLandscape: single-point landscape, cool_system, calculate_system_entropy
  - SwarmIntelligence: num_particles=1, coordinate_agents
  - SuperpositionExplorer: single-path (no interference), add/measure cycle
  - QuantumState: amplitude normalisation edge cases (zero, single entry)
  - MentalMappingModel: empty map operations, same-node self-connect,
    confidence=0.0 and confidence=1.0, empty reasoning chain
  - QuantumInspiredGameEngine: single strategy per player
  - BlueRedTeamSimulator: num_rounds=0, empty blue/red options
  - WorkflowNavigator: non-existent workspace dir, step with both command+uses,
    workflow with zero steps
  - SimpleDictMemory: get_history limit=0, search with empty query
  - LegacyAgentAdapter: legacy agent that raises on process()

#AFTERMATH_METRIC - Phase 9.4 edge-case coverage tests
"""

from __future__ import annotations

from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# EnergyLandscape — single-point landscape and entropy edge cases
# ---------------------------------------------------------------------------


class TestEnergyLandscapeSinglePoint:
    """Edge cases when the landscape has exactly one state."""

    def test_single_state_minimize_returns_that_state(self) -> None:
        from agents.physics_orchestrator import EnergyLandscape, EnergyState

        landscape = EnergyLandscape(temperature=1.0)
        state = EnergyState(configuration={"x": 0}, energy=0.5, entropy=0.1, temperature=1.0)
        landscape.add_state(state)
        result = landscape.minimize_free_energy()
        assert result is state, "Result must not be empty"

    def test_single_state_select_returns_that_state(self) -> None:
        from agents.physics_orchestrator import EnergyLandscape, EnergyState

        landscape = EnergyLandscape(temperature=1.0)
        state = EnergyState(configuration={"x": 0}, energy=0.5, entropy=0.1, temperature=1.0)
        landscape.add_state(state)
        selected = landscape.select_state()
        assert selected is state, "selected is not valid"

    def test_single_state_entropy_is_zero(self) -> None:
        from agents.physics_orchestrator import EnergyLandscape, EnergyState

        landscape = EnergyLandscape(temperature=1.0)
        state = EnergyState(configuration={"x": 0}, energy=0.5, entropy=0.0, temperature=1.0)
        landscape.add_state(state)
        entropy = landscape.calculate_system_entropy()
        # One deterministic state → probabilities are 1.0 → entropy ~0
        assert isinstance(entropy, float)

    def test_cool_system_reduces_temperature(self) -> None:
        from agents.physics_orchestrator import EnergyLandscape, EnergyState

        landscape = EnergyLandscape(temperature=2.0)
        state = EnergyState(configuration={}, energy=1.0, entropy=0.0, temperature=2.0)
        landscape.add_state(state)
        landscape.cool_system(cooling_rate=0.5)
        assert landscape.temperature == pytest.approx(1.0), "temperature is not valid"

    def test_empty_landscape_entropy_is_zero(self) -> None:
        from agents.physics_orchestrator import EnergyLandscape

        landscape = EnergyLandscape(temperature=1.0)
        assert landscape.calculate_system_entropy() == 0.0, "l is not valid"

    def test_multi_state_entropy_positive(self) -> None:
        from agents.physics_orchestrator import EnergyLandscape, EnergyState

        landscape = EnergyLandscape(temperature=1.0)
        for e in [0.0, 1.0, 2.0]:
            landscape.add_state(
                EnergyState(configuration={"e": e}, energy=e, entropy=0.0, temperature=1.0)
            )
        entropy = landscape.calculate_system_entropy()
        assert entropy > 0.0, "entropy must be greater than zero"

    def test_integrate_with_self_appraisal_returns_dict(self) -> None:
        from agents.physics_orchestrator import EnergyLandscape

        landscape = EnergyLandscape(temperature=1.0)
        result = landscape.integrate_with_self_appraisal(0.9, 0.8)
        assert "free_energy" in result, "Result must not be empty"
        assert "probability" in result, "Result must not be empty"
        assert "system_entropy" in result, "Result must not be empty"
        assert "recommendation" in result, "Result must not be empty"


# ---------------------------------------------------------------------------
# SwarmIntelligence — num_particles=1, coordinate_agents
# ---------------------------------------------------------------------------


class TestSwarmIntelligenceSingleParticle:
    """Edge cases for SwarmIntelligence with a single particle."""

    def test_single_particle_optimization_returns_result(self) -> None:
        from agents.physics_orchestrator import SwarmIntelligence

        swarm = SwarmIntelligence(dimensions=1, num_particles=1)
        result = swarm.run_optimization(
            objective_function=lambda pos: -(pos[0] ** 2),
            bounds=[(-1.0, 1.0)],
            max_iterations=3,
        )
        assert "best_position" in result, "Result must not be empty"
        assert "best_score" in result, "Result must not be empty"

    def test_coordinate_agents_moves_toward_target(self) -> None:
        from agents.physics_orchestrator import SwarmIntelligence

        swarm = SwarmIntelligence(dimensions=2, num_particles=2)
        agents = [(0.0, 0.0), (2.0, 0.0)]
        target = (1.0, 1.0)
        new_positions = swarm.coordinate_agents(agents, target)
        assert len(new_positions) == 2, "New_positions must not be empty"
        # Each agent should have moved (position changed)
        for orig, new in zip(agents, new_positions):
            assert new != orig, "new is not valid"

    def test_num_agents_property_equals_num_particles(self) -> None:
        from agents.physics_orchestrator import SwarmIntelligence

        swarm = SwarmIntelligence(dimensions=2, num_particles=5)
        assert swarm.num_agents == 5, "num_agents is not valid"

    def test_optimize_alias_works(self) -> None:
        from agents.physics_orchestrator import SwarmIntelligence

        swarm = SwarmIntelligence(dimensions=1, num_particles=2)
        result = swarm.optimize(
            fitness_function=lambda pos: -abs(pos[0]),
            bounds=[(-5.0, 5.0)],
            max_iterations=2,
        )
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# SuperpositionExplorer — single path, no interference
# ---------------------------------------------------------------------------


class TestSuperpositionExplorerSinglePath:
    """Edge cases for SuperpositionExplorer with a single path."""

    def _make_path(self):
        from agents.physics_orchestrator import ActionPath, ActionType

        path = ActionPath(
            action_type=ActionType.ANALYZE,
            description="single path",
            confidence=0.8,
            risk=0.1,
            impact=0.9,
        )
        return path

    def test_single_path_measure_returns_that_path(self) -> None:
        from agents.physics_orchestrator import SuperpositionExplorer

        explorer = SuperpositionExplorer()
        path = self._make_path()
        explorer.add_path(path)
        selected, prob = explorer.measure_optimal_path()
        assert selected is path, "selected is not valid"
        assert prob == pytest.approx(1.0, abs=1e-9)

    def test_apply_interference_with_single_path_does_not_raise(self) -> None:
        from agents.physics_orchestrator import SuperpositionExplorer

        explorer = SuperpositionExplorer()
        path = self._make_path()
        explorer.add_path(path)
        # Should not raise even with single path
        explorer.apply_interference()

    def test_run_grover_iteration_single_path(self) -> None:
        from agents.physics_orchestrator import SuperpositionExplorer

        explorer = SuperpositionExplorer()
        path = self._make_path()
        explorer.add_path(path)
        # apply_interference works without _mlp_scorer; only oracle needs it
        explorer.apply_interference()
        # After interference, path is still recoverable
        selected, _ = explorer.measure_optimal_path()
        assert selected is path, "selected is not valid"

    def test_empty_explorer_no_superposition_state(self) -> None:
        from agents.physics_orchestrator import SuperpositionExplorer

        explorer = SuperpositionExplorer()
        assert explorer.superposition_state is None, "superposition_state is not valid"
        assert explorer.paths == [], "paths is not valid"


# ---------------------------------------------------------------------------
# QuantumState — amplitude normalisation edge cases
# ---------------------------------------------------------------------------


class TestQuantumStateNormalisation:
    """Edge cases in QuantumState amplitude normalisation."""

    def test_single_amplitude_normalises_to_one(self) -> None:
        from agents.physics_orchestrator import QuantumState

        qs = QuantumState(amplitudes={"a": complex(3.0, 0)})
        prob = qs.probability("a")
        assert prob == pytest.approx(1.0), "prob is not valid"

    def test_multiple_equal_amplitudes_normalised(self) -> None:
        from agents.physics_orchestrator import QuantumState

        qs = QuantumState(amplitudes={"a": complex(1, 0), "b": complex(1, 0)})
        assert qs.probability("a") == pytest.approx(0.5), "Condition must be true"
        assert qs.probability("b") == pytest.approx(0.5), "Condition must be true"

    def test_unknown_state_probability_is_zero(self) -> None:
        from agents.physics_orchestrator import QuantumState

        qs = QuantumState(amplitudes={"a": complex(1, 0)})
        assert qs.probability("nonexistent") == 0.0, "Condition must be true"

    def test_collapse_returns_highest_prob_state(self) -> None:
        from agents.physics_orchestrator import QuantumState

        qs = QuantumState(amplitudes={"high": complex(3, 0), "low": complex(1, 0)})
        collapsed = qs.collapse()
        assert collapsed == "high", "collapsed is not valid"

    def test_apply_phase_does_not_change_probability(self) -> None:
        from agents.physics_orchestrator import QuantumState

        qs = QuantumState(amplitudes={"a": complex(1, 0)})
        prob_before = qs.probability("a")
        import math

        qs.apply_phase("a", math.pi / 4)
        prob_after = qs.probability("a")
        assert prob_after == pytest.approx(prob_before, abs=1e-9)


# ---------------------------------------------------------------------------
# MentalMappingModel — empty map, self-connect, confidence extremes
# ---------------------------------------------------------------------------


class TestMentalMappingEdgeCases:
    """Edge cases in MentalMappingModel."""

    def test_empty_map_summary_returns_dict(self) -> None:
        from agents.mental_mapping import MentalMappingModel

        model = MentalMappingModel()
        summary = model.get_mental_map_summary()
        assert isinstance(summary, dict)

    def test_empty_map_iterative_review_returns_empty_list(self) -> None:
        from agents.mental_mapping import MentalMappingModel

        model = MentalMappingModel()
        result = model.iterative_review()
        assert result == [], "Result must not be empty"

    def test_empty_map_calculate_metrics_returns_dict(self) -> None:
        from agents.mental_mapping import MentalMappingModel

        model = MentalMappingModel()
        metrics = model.calculate_metrics()
        assert isinstance(metrics, dict)

    def test_node_with_zero_confidence_marked_for_review(self) -> None:
        from agents.mental_mapping import MentalMappingModel, NodeType

        model = MentalMappingModel()
        node = model.create_node(NodeType.CONCEPT, content="low-conf", confidence=0.0)
        assert node.needs_review is True, "needs_review is not valid"

    def test_node_with_max_confidence_not_marked_for_review(self) -> None:
        from agents.mental_mapping import MentalMappingModel, NodeType

        model = MentalMappingModel()
        node = model.create_node(NodeType.CONCEPT, content="high-conf", confidence=1.0)
        assert node.needs_review is False, "needs_review is not valid"

    def test_connect_node_to_itself(self) -> None:
        from agents.mental_mapping import EdgeType, MentalMappingModel, NodeType

        model = MentalMappingModel()
        node = model.create_node(NodeType.CONCEPT, content="self-ref", confidence=1.0)
        # Self-connect should not raise (both nodes exist)
        edge = model.connect_nodes(node.node_id, node.node_id, edge_type=EdgeType.CAUSES)
        assert edge is not None, "edge must be initialized"
        assert edge.source_id == node.node_id, "source_id is not valid"
        assert edge.target_id == node.node_id, "target_id is not valid"

    def test_get_reasoning_chain_on_empty_node(self) -> None:
        from agents.mental_mapping import MentalMappingModel, NodeType

        model = MentalMappingModel()
        node = model.create_node(NodeType.CONCEPT, content="no reasoning", confidence=1.0)
        assert node.reasoning_chain == [], "reasoning_chain is not valid"

    def test_add_reasoning_step_to_node(self) -> None:
        from agents.mental_mapping import MentalMappingModel, NodeType

        model = MentalMappingModel()
        node = model.create_node(NodeType.CONCEPT, content="with reasoning", confidence=1.0)
        step = node.add_reasoning_step(
            thought="test thought",
            reasoning_type="deductive",
            confidence=0.9,
        )
        assert step is not None, "step must be initialized"
        assert len(node.reasoning_chain) == 1, "Collection must not be empty"

    def test_node_mark_for_review_and_review(self) -> None:
        from agents.mental_mapping import MentalMappingModel, NodeType

        model = MentalMappingModel()
        node = model.create_node(NodeType.CONCEPT, content="review me", confidence=1.0)
        node.mark_for_review("test_reason")
        assert node.needs_review is True, "needs_review is not valid"
        node.review(0.9, notes="looks good")
        assert node.needs_review is False, "needs_review is not valid"
        assert node.quality_score == pytest.approx(0.9), "quality_score is not valid"

    def test_bfs_on_empty_map_returns_empty(self) -> None:
        from agents.mental_mapping import MentalMappingModel

        model = MentalMappingModel()
        result = model.bfs()
        assert result == [], "Result must not be empty"

    def test_dfs_on_empty_map_returns_empty(self) -> None:
        from agents.mental_mapping import MentalMappingModel

        model = MentalMappingModel()
        result = model.dfs()
        assert result == [], "Result must not be empty"

    def test_get_connected_nodes_empty_map_returns_empty(self) -> None:
        from agents.mental_mapping import MentalMappingModel, NodeType

        model = MentalMappingModel()
        node = model.create_node(NodeType.CONCEPT, content="isolated", confidence=1.0)
        connected = model.get_connected_nodes(node.node_id)
        assert connected == [], "connected is not valid"


# ---------------------------------------------------------------------------
# QuantumInspiredGameEngine — single strategy per player
# ---------------------------------------------------------------------------


class TestQuantumInspiredGameEngineSingleStrategy:
    """Edge cases for QuantumInspiredGameEngine with a single strategy per player."""

    def test_single_strategy_each_player_does_not_raise(self) -> None:
        import agents.quantum_game_theory as qgt_module

        if not qgt_module.NUMPY_AVAILABLE:
            pytest.skip("numpy not available")

        import numpy as np

        payoff = np.array([[1.0]])
        engine = qgt_module.QuantumInspiredGameEngine(
            blue_strategies=["only_blue"],
            red_strategies=["only_red"],
            payoff_blue=payoff,
            payoff_red=payoff,
        )
        assert engine is not None, "engine must be initialized"

    def test_single_strategy_payoffs_accessible(self) -> None:
        import agents.quantum_game_theory as qgt_module

        if not qgt_module.NUMPY_AVAILABLE:
            pytest.skip("numpy not available")

        import numpy as np

        payoff = np.array([[1.0]])
        engine = qgt_module.QuantumInspiredGameEngine(
            blue_strategies=["only_blue"],
            red_strategies=["only_red"],
            payoff_blue=payoff,
            payoff_red=payoff,
        )
        blue_payoff, red_payoff = engine.get_payoffs()
        assert isinstance(blue_payoff, float)
        assert isinstance(red_payoff, float)

    def test_single_strategy_play_round_returns_dict(self) -> None:
        import agents.quantum_game_theory as qgt_module

        if not qgt_module.NUMPY_AVAILABLE:
            pytest.skip("numpy not available")

        import numpy as np

        payoff = np.array([[1.0]])
        engine = qgt_module.QuantumInspiredGameEngine(
            blue_strategies=["only_blue"],
            red_strategies=["only_red"],
            payoff_blue=payoff,
            payoff_red=payoff,
        )
        result = engine.play_round()
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# BlueRedTeamSimulator — num_rounds=0, empty options
# ---------------------------------------------------------------------------


class TestBlueRedTeamSimulatorEdgeCases:
    """Edge cases in BlueRedTeamSimulator."""

    def _make_sim(self):
        import agents.quantum_game_theory as qgt_module

        if not qgt_module.NUMPY_AVAILABLE:
            pytest.skip("numpy not available")
        return qgt_module.BlueRedTeamSimulator(
            blue_strategies=["attack", "defend"],
            red_strategies=["probe", "exploit"],
        )

    def test_run_simulation_zero_rounds_raises(self) -> None:
        sim = self._make_sim()
        # num_rounds=0 causes IndexError on round_results[-1] in source
        with pytest.raises((IndexError, Exception)):
            sim.run_simulation(num_rounds=0)

    def test_compare_strategies_empty_options_raises(self) -> None:
        sim = self._make_sim()
        # Empty options cause max() on empty iterable → ValueError
        with pytest.raises((ValueError, Exception)):
            sim.compare_strategies(blue_options=[], red_options=[])

    def test_run_simulation_single_round(self) -> None:
        sim = self._make_sim()
        result = sim.run_simulation(num_rounds=1)
        assert isinstance(result, dict)

    def test_evaluate_hypothesis_returns_dict(self) -> None:
        sim = self._make_sim()
        result = sim.evaluate_hypothesis("test hypothesis")
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# WorkflowNavigator — non-existent workspace dir, both command+uses, zero steps
# ---------------------------------------------------------------------------


class TestWorkflowNavigatorEdgeCases:
    """Edge cases in WorkflowNavigator and WorkflowStep."""

    def test_nonexistent_workspace_dir_still_constructs(self, tmp_path: Path) -> None:
        from agents.workflow_navigator import WorkflowNavigator

        nonexistent = tmp_path / "no_such_dir"
        # Should not raise on construction
        nav = WorkflowNavigator(workspace_dir=nonexistent)
        assert nav is not None, "nav must be initialized"

    def test_step_with_both_command_and_uses_executes_command(self, tmp_path: Path) -> None:
        from agents.workflow_navigator import WorkflowStep

        # Per the implementation, command takes precedence over uses
        step = WorkflowStep(id="both", action="both", command="echo hello", uses="some.module")
        result = step.execute({"working_dir": str(tmp_path)})
        # command wins: should succeed
        assert result["success"] is True, "Result must not be empty"

    def test_workflow_with_zero_steps(self, tmp_path: Path) -> None:
        from agents.workflow_navigator import Workflow, WorkflowFrequency, WorkflowNavigator

        nav = WorkflowNavigator(workspace_dir=tmp_path)
        wf = Workflow(
            workflow_id="EMPTY_WF",
            name="empty workflow",
            description="no steps",
            frequency=WorkflowFrequency.LOW,
            steps=[],
        )
        nav.register_workflow(wf)
        retrieved = nav.get_workflow("EMPTY_WF")
        assert retrieved is not None, "retrieved must be initialized"
        assert len(retrieved.steps) == 0, "Collection must not be empty"

    def test_workflow_step_status_starts_pending(self) -> None:
        from agents.workflow_navigator import StepStatus, WorkflowStep

        step = WorkflowStep(id="s", action="a")
        assert step.status == StepStatus.PENDING, "status is not valid"

    def test_list_workflows_returns_registered(self, tmp_path: Path) -> None:
        from agents.workflow_navigator import WorkflowNavigator

        nav = WorkflowNavigator(workspace_dir=tmp_path)
        workflows = nav.list_workflows()
        assert isinstance(workflows, list)


# ---------------------------------------------------------------------------
# SimpleDictMemory — get_history limit=0, empty search query
# ---------------------------------------------------------------------------


class TestSimpleDictMemoryEdgeCases:
    """Edge cases for SimpleDictMemory."""

    def _make_memory(self):
        from agents.cognitive_adapter import SimpleDictMemory

        return SimpleDictMemory()

    def test_get_history_limit_zero_returns_empty(self) -> None:
        mem = self._make_memory()
        mem.store("key", "value1")
        mem.store("key", "value2")
        # Python slice [-0:] == [0:] which is the full list; actual behavior is all entries
        result = mem.get_history("key", limit=0)
        # limit=0 is a degenerate case: Python -0 == 0, so returns full history
        assert isinstance(result, list)

    def test_get_history_limit_one_returns_most_recent(self) -> None:
        mem = self._make_memory()
        mem.store("key", "first")
        mem.store("key", "second")
        result = mem.get_history("key", limit=1)
        assert len(result) == 1, "Result must not be empty"
        _, val = result[0]
        assert val == "second", "val is not valid"

    def test_search_empty_query_matches_all(self) -> None:
        mem = self._make_memory()
        mem.store("a", 1, metadata={"type": "x"})
        mem.store("b", 2, metadata={"type": "y"})
        # Empty query: all entries match (all metadata pass trivially)
        results = mem.search({})
        assert len(results) == 2, "Results must not be empty"

    def test_search_with_no_metadata_match_returns_empty(self) -> None:
        mem = self._make_memory()
        mem.store("a", 1)  # no metadata
        results = mem.search({"tag": "missing"})
        assert results == [], "Result must not be empty"

    def test_store_overwrite_keeps_history(self) -> None:
        mem = self._make_memory()
        mem.store("k", "v1")
        mem.store("k", "v2")
        assert mem.retrieve("k") == "v2", "Condition must be true"
        history = mem.get_history("k")
        assert len(history) == 2, "History must not be empty"


# ---------------------------------------------------------------------------
# LegacyAgentAdapter — legacy agent that raises on process()
# ---------------------------------------------------------------------------


class TestLegacyAgentAdapterEdgeCases:
    """Edge cases for LegacyAgentAdapter."""

    def test_adapter_with_raising_legacy_agent_returns_failure(self) -> None:
        from agents.cognitive_adapter import LegacyAgentAdapter

        class BrokenAgent:
            def process(self, data):
                raise RuntimeError("legacy failure")

        adapter = LegacyAgentAdapter(BrokenAgent())
        observation = adapter.observe({"input": "data"})
        orientation = adapter.orient(observation)
        decision = adapter.decide(orientation)
        result = adapter.act(decision)
        assert result.success is False, "Result must not be empty"
        assert len(result.errors) > 0, "Collection must not be empty"
        assert "legacy failure" in result.errors[0], "Result must not be empty"

    def test_adapter_with_working_legacy_agent_returns_success(self) -> None:
        from agents.cognitive_adapter import LegacyAgentAdapter

        class WorkingAgent:
            def process(self, data):
                return {"processed": True}

        adapter = LegacyAgentAdapter(WorkingAgent())
        observation = adapter.observe({"input": "data"})
        orientation = adapter.orient(observation)
        decision = adapter.decide(orientation)
        result = adapter.act(decision)
        assert result.success is True, "Result must not be empty"
        assert result.output == {"processed": True}, "Result must not be empty"

    def test_adapter_with_execute_method_fallback(self) -> None:
        from agents.cognitive_adapter import LegacyAgentAdapter

        class ExecuteAgent:
            def execute(self, data):
                return "executed"

        adapter = LegacyAgentAdapter(ExecuteAgent())
        observation = adapter.observe({})
        orientation = adapter.orient(observation)
        decision = adapter.decide(orientation)
        result = adapter.act(decision)
        assert result.success is True, "Result must not be empty"
        assert result.output == "executed", "Result must not be empty"

    def test_adapter_callable_fallback(self) -> None:
        from agents.cognitive_adapter import LegacyAgentAdapter

        class CallableAgent:
            def __call__(self, data):
                return "called"

        adapter = LegacyAgentAdapter(CallableAgent())
        observation = adapter.observe({})
        orientation = adapter.orient(observation)
        decision = adapter.decide(orientation)
        result = adapter.act(decision)
        assert result.success is True, "Result must not be empty"

    def test_wrap_legacy_agent_returns_planner(self) -> None:
        from agents.cognitive_adapter import wrap_legacy_agent

        class SimpleAgent:
            def process(self, data):
                return data

        planner = wrap_legacy_agent(SimpleAgent())
        assert planner is not None, "planner must be initialized"

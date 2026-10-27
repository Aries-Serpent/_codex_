"""Regression contracts for the bounded agent typing lane."""

from __future__ import annotations

import builtins
import importlib.util
import json
import math
import sys
from pathlib import Path

import httpx
import numpy as np
import pytest

from agents import developer_orchestrator, physics_integration
from agents.advanced_physics_calculators import (
    AdvancedPhysicsOrchestrator,
    EMFieldRouter,
    FluidChannel,
    FluidFlowScheduler,
    RelativityScheduler,
)
from agents.developer_orchestrator import CodeComponent, PhysicsGuidedDeveloperOrchestrator
from agents.mlp_scoring import MLPScorer
from agents.msp_client import MSPClient
from agents.physics_orchestrator import PathIntegralCalculator
from agents.quantum_game_theory import (
    QuantumGameState,
    QuantumInspiredGameEngine,
    StrategyState,
    TeamType,
)


@pytest.mark.parametrize("explicit_id", [False, True])
def test_fluid_registration_uses_channel_identity(explicit_id: bool) -> None:
    scheduler = FluidFlowScheduler(num_channels=0)
    channel = FluidChannel(channel_id="actual", capacity=10.0)
    if explicit_id:
        scheduler.add_channel("compatibility-alias", channel)
    else:
        scheduler.add_channel(channel)
    assert scheduler.channels == {"actual": channel}
    assert scheduler.inject_flow("actual", 2.0)
    assert channel.current_flow == 2.0


def test_fluid_registration_rejects_id_without_channel() -> None:
    scheduler = FluidFlowScheduler(num_channels=0)
    with pytest.raises(TypeError, match="FluidChannel"):
        scheduler.add_channel("missing")
    assert scheduler.channels == {}


def test_em_field_alias_and_partial_state_guard() -> None:
    router = EMFieldRouter(grid_resolution=8, grid_size=5)
    assert router.grid_resolution == router.grid_size == 5
    potential, field = router.get_field_at_position(np.array([0.5, 0.5]))
    assert potential == 0.0
    np.testing.assert_array_equal(field, [0.0, 0.0])

    router.add_charge(np.array([0.5, 0.5]), 2.0)
    potential, field = router.get_field_at_position(np.array([0.5, 0.5]))
    assert potential > 0
    assert field.shape == (2,)
    assert router.prioritize_regions(num_regions=1)

    # Partial state may occur when an external caller resets a calculated field.
    router.electric_field = None
    potential, field = router.get_field_at_position(np.array([0.5, 0.5]))
    assert potential == 0.0
    np.testing.assert_array_equal(field, [0.0, 0.0])
    assert router.prioritize_regions() == []


@pytest.mark.parametrize("explicit_velocity", [False, True])
def test_relativity_velocity_defaults_preserve_explicit_input(explicit_velocity: bool) -> None:
    scheduler = RelativityScheduler()
    position = np.array([1.0, 2.0])
    velocity = np.array([0.25, 0.5]) if explicit_velocity else None
    scheduler.add_agent("worker", position, velocity, clock_offset=3.0)
    agent = scheduler.agents["worker"]
    assert agent["position"] is position
    assert agent["clock_offset"] == 3.0
    if explicit_velocity:
        assert agent["velocity"] is velocity
    else:
        np.testing.assert_array_equal(agent["velocity"], [0.0, 0.0])


def test_advanced_analysis_keeps_each_paradigm_output() -> None:
    orchestrator = AdvancedPhysicsOrchestrator()
    result = orchestrator.full_analysis(
        {
            "exploration": True,
            "param_ranges": [(0.0, 1.0)],
            "structure": {"main": {"helper": {}}},
            "workflow": True,
            "hotspots": [([0.5, 0.5], 1.0)],
            "signals": [{"position": (2, 2), "amplitude": 0.1}],
            "agents": [{"agent_id": "worker", "position": np.array([0.0, 0.0])}],
        }
    )
    assert set(result["paradigms"]) == {
        "chaos",
        "fractal",
        "fluid",
        "em_field",
        "wave",
        "relativity",
    }
    assert result["paradigms"]["chaos"]["test_cases_generated"] == 10
    assert result["paradigms"]["wave"]["propagation_steps"] == 50
    assert result["paradigms"]["relativity"]["agents_synchronized"] == 1
    assert orchestrator.orchestration_log[-1] is result


@pytest.mark.parametrize("use_numpy", [False, True])
def test_mlp_weight_representations_and_feature_dimensions(use_numpy: bool) -> None:
    scorer = MLPScorer(input_dim=3, hidden_dim=2, use_numpy=use_numpy)
    assert isinstance(scorer.W1, np.ndarray if use_numpy else list)
    features = [0.2, 0.4, 0.0]
    weights = np.asarray(scorer.W1)
    hidden = np.maximum(0.0, weights @ features + scorer.b1)
    expected = float((np.asarray(scorer.W2) @ hidden + scorer.b2)[0])
    assert scorer.score([0.2, 0.4]) == pytest.approx(expected)
    assert scorer.score([0.2, 0.4, 0.0, 99.0]) == pytest.approx(expected)
    assert all(math.isfinite(score) for score in scorer.batch_score([[], features]))


@pytest.mark.parametrize("component_id", ["function-id", ""])
def test_development_workflow_reuses_component_api(
    monkeypatch: pytest.MonkeyPatch, component_id: str
) -> None:
    monkeypatch.setattr(developer_orchestrator, "ADVANCED_PHYSICS", False)
    monkeypatch.setattr(developer_orchestrator, "log_message", lambda *args: None)
    orchestrator = PhysicsGuidedDeveloperOrchestrator()
    component = CodeComponent(
        name="calculate",
        component_type="function",
        description="Return a calculated value.",
        component_id=component_id,
    )
    orchestrator.components = [component]
    result = orchestrator.execute_workflow(["IMPLEMENTATION", "TESTING"])
    assert result["steps_failed"] == []
    assert result["steps_completed"] == ["IMPLEMENTATION", "TESTING"]
    assert result["success"] is True
    assert component.implementation_status == "complete"
    assert result["outputs"]["implementation"] == {
        "components_generated": 1,
        "total_lines": component.code.count("\n"),
    }
    assert result["outputs"]["testing"] == {"components_validated": 1, "all_valid": True}


def test_requirement_and_validation_results_keep_mutable_collections(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(developer_orchestrator, "ADVANCED_PHYSICS", False)
    monkeypatch.setattr(developer_orchestrator, "log_message", lambda *args: None)
    orchestrator = PhysicsGuidedDeveloperOrchestrator()
    analysis = orchestrator.analyze_user_requirements({"app_name": "example"})
    assert analysis["missing_variables"]
    assert 0.0 < analysis["completeness"] < 1.0
    assert all(item["name"] in analysis["suggestions"] for item in analysis["missing_variables"])
    validation = orchestrator.validate_code("def broken(:\n\t# TODO\n", "broken")
    assert validation["valid"] is False
    assert validation["errors"][0].startswith("Syntax error")
    assert len(validation["warnings"]) == 2


def test_workflow_continues_after_unknown_step(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(developer_orchestrator, "ADVANCED_PHYSICS", False)
    monkeypatch.setattr(developer_orchestrator, "log_message", lambda *args: None)
    result = PhysicsGuidedDeveloperOrchestrator().execute_workflow(["unknown", "TESTING"])
    assert result["steps_failed"] == ["Unknown step: unknown"]
    assert result["steps_completed"] == ["TESTING"]
    assert result["success"] is False


def test_tenant_patch_preserves_heterogeneous_values_and_false() -> None:
    requests: list[httpx.Request] = []

    def respond(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"updated": True})

    with MSPClient(api_key=None) as client:
        client.client.close()
        client.client = httpx.Client(
            base_url=client.base_url, transport=httpx.MockTransport(respond)
        )
        assert client.update_tenant(
            "tenant-1",
            name="renamed",
            quota={"requests": 0},
            policies=[],
            metadata={"tier": "trial"},
            active=False,
        ) == {"updated": True}
        client.update_tenant("tenant-1")
    assert requests[0].url.path == "/admin/tenants/tenant-1"
    assert json.loads(requests[0].content) == {
        "name": "renamed",
        "quota": {"requests": 0},
        "policies": [],
        "metadata": {"tier": "trial"},
        "active": False,
    }
    assert json.loads(requests[1].content) == {}


def test_path_action_default_and_custom_lagrangians() -> None:
    calculator = PathIntegralCalculator(hbar=2.0)
    path = [{"kinetic": 4.0, "potential": 1.0}, {"kinetic": 2.0}]
    assert calculator.calculate_action(path) == 2.5
    assert calculator.calculate_action([]) == 0.0
    assert calculator.calculate_action(path, lambda state: state["kinetic"] * 2.0) == 6.0


def test_quantum_product_density_and_zero_norm_contracts() -> None:
    blue = StrategyState(TeamType.BLUE, ["a", "b"])
    red = StrategyState(TeamType.RED, ["c", "d"])
    state = QuantumGameState(blue, red)
    assert state.joint_wavefunction is not None
    assert np.linalg.norm(state.joint_wavefunction) == pytest.approx(1.0)
    assert np.trace(state.to_density_matrix()) == pytest.approx(1.0)
    product = state.break_entanglement()
    np.testing.assert_allclose(product.joint_wavefunction, state.joint_wavefunction)
    zero = QuantumGameState(blue, red, joint_wavefunction=np.zeros(4, dtype=complex))
    np.testing.assert_array_equal(zero.joint_wavefunction, np.zeros(4))
    raw = QuantumGameState(np.array([1.0, 0.0]), np.array([0.0, 1.0]))
    np.testing.assert_allclose(raw.joint_wavefunction, [0.0, 1.0, 0.0, 0.0])


@pytest.mark.parametrize("operation", ["normalize", "to_density_matrix"])
def test_quantum_cleared_joint_state_is_explicit_error(operation: str) -> None:
    state = QuantumGameState(
        StrategyState(TeamType.BLUE, ["a"]), StrategyState(TeamType.RED, ["b"])
    )
    state.joint_wavefunction = None
    with pytest.raises(ValueError, match="joint wavefunction"):
        getattr(state, operation)()


def test_quantum_missing_team_amplitudes_are_guarded() -> None:
    blue = StrategyState(TeamType.BLUE, ["a"])
    red = StrategyState(TeamType.RED, ["b"])
    state = QuantumGameState(blue, red)
    blue.wavefunction = None
    with pytest.raises(ValueError, match="team wavefunctions"):
        QuantumGameState(blue, red)
    with pytest.raises(ValueError, match="team wavefunctions"):
        state.break_entanglement()


def test_quantum_engine_preserves_payoff_and_checks_missing_state() -> None:
    engine = QuantumInspiredGameEngine(
        ["a", "b"], ["c", "d"], np.full((2, 2), 3.0), np.full((2, 2), -3.0), entanglement=0.3
    )
    assert engine.expected_payoff(TeamType.BLUE) == pytest.approx(3.0)
    assert engine.expected_payoff(TeamType.RED) == pytest.approx(-3.0)
    engine.game_state.joint_wavefunction = None
    with pytest.raises(ValueError, match="joint wavefunction"):
        engine.expected_payoff(TeamType.BLUE)
    engine.blue_state.wavefunction = None
    with pytest.raises(ValueError, match="team wavefunctions"):
        engine._apply_entanglement(0.5)


def test_hybrid_without_optional_engines_preserves_empty_outputs(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(physics_integration, "ADVANCED_PHYSICS_AVAILABLE", False)
    monkeypatch.setattr(physics_integration, "PHYSICS_ORCHESTRATOR_AVAILABLE", False)
    monkeypatch.setattr(physics_integration, "log_message", lambda *args: None)
    orchestrator = physics_integration.HybridPhysicsOrchestrator()
    result = orchestrator.orchestrate_with_all_paradigms({})
    assert result["paradigms_used"] == []
    assert result["classical_physics"] is None
    assert result["advanced_physics"] is None
    assert isinstance(result["recommendations"], list)
    assert orchestrator.decision_history[-1] is result


@pytest.mark.parametrize(
    "name",
    [
        "advanced_physics_calculators",
        "quantum_game_theory",
        "mlp_scoring",
        "developer_orchestrator",
    ],
)
def test_optional_numpy_import_remains_supported(
    monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    real_import = builtins.__import__

    def without_numpy(module: str, *args, **kwargs):
        if module == "numpy" or module.startswith("numpy."):
            raise ImportError("NumPy deliberately unavailable in contract test")
        return real_import(module, *args, **kwargs)

    path = Path(developer_orchestrator.__file__).with_name(f"{name}.py")
    module_name = f"_round3_no_numpy_{name}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, module_name, module)
    monkeypatch.setattr(builtins, "__import__", without_numpy)
    spec.loader.exec_module(module)
    assert module.NUMPY_AVAILABLE is False
    if name == "mlp_scoring":
        assert math.isfinite(module.MLPScorer(2).score([0.5, 0.25]))
    elif name == "advanced_physics_calculators":
        scheduler = module.FluidFlowScheduler(num_channels=0)
        channel = module.FluidChannel(channel_id="offline", capacity=5.0)
        scheduler.add_channel(channel)
        assert scheduler.inject_flow("offline", 1.0)
        np_fallback = module.np
        assert list(np_fallback.array([1.0, 2.0]) * 2.0) == [2.0, 4.0]
    elif name == "quantum_game_theory":
        state = module.StrategyState("blue", ["a", "b"])
        state.normalize_wavefunction()
        assert sum(state.get_measurement_probabilities()) == pytest.approx(1.0)
    else:
        assert module.np.array([1.0, 2.0]) == [1.0, 2.0]

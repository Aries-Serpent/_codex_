"""Unit tests for agents/quantum_game_theory.py (Phase 9.1 coverage push).

Targets previously uncovered code paths:
- ``PayoffOperator`` (shape, to_hamiltonian, as_diagonal_operator,
  expected_value, ``players`` alias).
- ``QuantumGameState.get_reduced_density_matrix`` (Blue + Red),
  ``break_entanglement``, ``calculate_correlation``,
  ``violates_bell_inequality`` (both branches).
- ``ClassicalGameEngine.best_response_red``, ``calculate``,
  ``compute_nash_equilibrium``.
- ``QuantumInspiredGameEngine.payoff_variance`` /
  ``risk_adjusted_utility`` / ``gradient_payoff_wrt_theta`` /
  ``quantum_policy_gradient_step`` / ``apply_decoherence``,
  ``play_round`` with noise, ``num_players`` shorthand.
- ``BlueRedTeamSimulator`` quantum-branch ``evaluate_hypothesis``,
  ``compare_strategies``, ``run_simulation`` (both modes).
- Scenario factories: prisoner's dilemma, zero-sum, security.
"""

from __future__ import annotations

import numpy as np
import pytest

from agents.quantum_game_theory import (
    BlueRedTeamSimulator,
    ClassicalGameEngine,
    PayoffOperator,
    QuantumGameState,
    QuantumInspiredGameEngine,
    StrategyState,
    TeamType,
    create_prisoners_dilemma,
    create_security_game,
    create_zero_sum_game,
)


# ---------------------------------------------------------------------------
# PayoffOperator
# ---------------------------------------------------------------------------
def test_payoff_operator_shape_and_alias():
    matrix = np.array([[1.0, 0.0], [0.0, 2.0]])
    # Pass a non-TeamType team value so __post_init__ swaps in the players list
    op = PayoffOperator(matrix, team="custom", players=["a", "b"])
    assert op.shape == (2, 2)
    np.testing.assert_array_equal(op.matrix, matrix)
    assert op.team == ["a", "b"]


def test_payoff_operator_to_hamiltonian_and_diag_and_expected_value():
    matrix = np.array([[1.0, 0.0], [0.0, 2.0]])
    op = PayoffOperator(matrix, TeamType.BLUE)
    np.testing.assert_array_equal(op.to_hamiltonian(), -matrix)

    diag = op.as_diagonal_operator()
    assert diag.shape == (4, 4)
    np.testing.assert_array_equal(np.diag(diag), [1.0, 0.0, 0.0, 2.0])

    # |ψ⟩ = uniform 4-vector → ⟨ψ|diag|ψ⟩ = (1+2)/4 = 0.75
    psi = np.ones(4, dtype=complex) / 2
    assert op.expected_value(psi) == pytest.approx(0.75), "Value must be initialized"


# ---------------------------------------------------------------------------
# QuantumGameState reduced density, break entanglement, Bell inequality
# ---------------------------------------------------------------------------
def _basic_game_state(entanglement: float = 0.0) -> QuantumGameState:
    blue = StrategyState(TeamType.BLUE, ["b0", "b1"])
    red = StrategyState(TeamType.RED, ["r0", "r1"])
    return QuantumGameState(blue_state=blue, red_state=red, entanglement_strength=entanglement)


def test_reduced_density_matrix_blue_and_red():
    qs = _basic_game_state()
    rho_blue = qs.get_reduced_density_matrix(TeamType.BLUE)
    rho_red = qs.get_reduced_density_matrix(TeamType.RED)
    assert rho_blue.shape == (2, 2)
    assert rho_red.shape == (2, 2)
    # Product state → trace = 1 for both
    assert np.trace(rho_blue).real == pytest.approx(1.0, abs=1e-6)
    assert np.trace(rho_red).real == pytest.approx(1.0, abs=1e-6)


def test_break_entanglement_returns_product_state():
    qs = _basic_game_state()
    qs.apply_entangling_gate(strength=0.6)
    assert qs.entangled is True, "entangled is not valid"
    product = qs.break_entanglement()
    assert product.entanglement_strength == 0.0, "entanglement_strength is not valid"
    assert product.entangled is False, "entangled is not valid"
    # Norm preserved
    norm = np.vdot(product.joint_wavefunction, product.joint_wavefunction).real
    assert norm == pytest.approx(1.0, abs=1e-6)


def test_calculate_correlation_and_bell_inequality_zero_entanglement():
    qs = _basic_game_state()
    # No entanglement → correlation = 0, Bell not violated
    assert qs.calculate_correlation() == 0.0, "Condition must be true"
    assert qs.violates_bell_inequality() is False, "Condition must be true"


def test_calculate_correlation_with_entanglement():
    qs = _basic_game_state()
    qs.apply_entangling_gate(strength=1.0)
    val = qs.calculate_correlation()
    # Should be a finite scalar within the clipping bounds
    assert -2.828 <= val <= 2.828, "828 is not valid"


# ---------------------------------------------------------------------------
# ClassicalGameEngine extras
# ---------------------------------------------------------------------------
def _classical_engine() -> ClassicalGameEngine:
    blue = ["b0", "b1"]
    red = ["r0", "r1"]
    payoff_blue = np.array([[2.0, 0.0], [3.0, 1.0]])
    payoff_red = np.array([[2.0, 3.0], [0.0, 1.0]])
    return ClassicalGameEngine(blue, red, payoff_blue, payoff_red)


def test_classical_best_response_red():
    eng = _classical_engine()
    idx = eng.best_response_red()
    assert idx in (0, 1)


def test_classical_calculate_alias_runs():
    eng = _classical_engine()
    result = eng.calculate()
    assert "pi_blue" in result and "pi_red" in result, "Result must not be empty"
    assert "iterations" in result, "Result must not be empty"


def test_classical_compute_nash_equilibrium_runs():
    eng = _classical_engine()
    result = eng.compute_nash_equilibrium()
    assert "payoff_blue" in result, "Result must not be empty"
    assert "history" in result, "Result must not be empty"


# ---------------------------------------------------------------------------
# QuantumInspiredGameEngine: variance / risk / gradient / decoherence
# ---------------------------------------------------------------------------
def _quantum_engine(entanglement: float = 0.0) -> QuantumInspiredGameEngine:
    blue = ["b0", "b1"]
    red = ["r0", "r1"]
    payoff_blue = np.array([[2.0, 0.0], [3.0, 1.0]])
    payoff_red = np.array([[2.0, 3.0], [0.0, 1.0]])
    return QuantumInspiredGameEngine(blue, red, payoff_blue, payoff_red, entanglement=entanglement)


def test_quantum_engine_num_players_shorthand():
    qe = QuantumInspiredGameEngine(num_players=3)
    assert qe.blue_state.num_strategies == 3, "num_strategies is not valid"
    assert qe.red_state.num_strategies == 3, "num_strategies is not valid"


def test_quantum_engine_entangled_init_path():
    qe = _quantum_engine(entanglement=0.5)
    assert qe.game_state.entanglement_strength == pytest.approx(0.5), "entanglement_strength is not valid"


def test_payoff_variance_and_risk_adjusted():
    qe = _quantum_engine()
    var_blue = qe.payoff_variance(TeamType.BLUE)
    var_red = qe.payoff_variance(TeamType.RED)
    assert var_blue >= 0, "var_blue must be greater than zero"
    assert var_red >= 0, "var_red must be greater than zero"

    util_blue = qe.risk_adjusted_utility(TeamType.BLUE, risk_aversion=0.5)
    util_red = qe.risk_adjusted_utility(TeamType.RED, risk_aversion=0.5)
    assert np.isfinite(util_blue), "Condition must be true"
    assert np.isfinite(util_red), "Condition must be true"


def test_gradient_payoff_wrt_theta_and_policy_step():
    qe = _quantum_engine()
    g_blue = qe.gradient_payoff_wrt_theta(TeamType.BLUE, theta_current=0.1)
    g_red = qe.gradient_payoff_wrt_theta(TeamType.RED, theta_current=0.1)
    assert np.isfinite(g_blue), "Condition must be true"
    assert np.isfinite(g_red), "Condition must be true"

    new_blue, new_red = qe.quantum_policy_gradient_step(
        learning_rate=0.05, theta_blue=0.2, theta_red=0.2
    )
    assert np.isfinite(new_blue), "Condition must be true"
    assert np.isfinite(new_red), "Condition must be true"


def test_apply_decoherence_full_gamma_collapses_state():
    qe = _quantum_engine()
    qe.apply_decoherence(gamma=1.0)
    # Wavefunction should still be normalized
    norm = np.vdot(qe.game_state.joint_wavefunction, qe.game_state.joint_wavefunction).real
    assert norm == pytest.approx(1.0, abs=1e-6)


def test_play_round_with_noise():
    qe = _quantum_engine()
    out = qe.play_round(theta_blue=0.1, theta_red=0.05, apply_noise=True, decoherence_gamma=0.3)
    assert "blue_payoff" in out and "red_payoff" in out, "Condition must be true"
    assert np.isfinite(out["blue_payoff"]), "Condition must be true"
    assert np.isfinite(out["red_payoff"]), "Condition must be true"


# ---------------------------------------------------------------------------
# BlueRedTeamSimulator (quantum branch) + classical
# ---------------------------------------------------------------------------
def test_simulator_quantum_evaluate_hypothesis_and_history():
    blue, red, payoff_blue, payoff_red = create_prisoners_dilemma()
    sim = BlueRedTeamSimulator(
        blue_strategies=blue,
        red_strategies=red,
        payoff_blue=payoff_blue,
        payoff_red=payoff_red,
        mode="quantum",
        entanglement=0.0,
        noise_level=0.2,  # exercises decoherence branch
        risk_aversion=0.3,
    )
    result = sim.evaluate_hypothesis(
        "test hypothesis",
        blue_strategy_weights=np.array([1.0, 1.0]),
        red_strategy_weights=np.array([1.0, 1.0]),
    )
    assert result["mode"] == "quantum", "Result must not be empty"
    assert "blue_payoff_variance" in result, "Result must not be empty"
    assert "red_risk_adjusted_utility" in result, "Result must not be empty"
    assert "measurement_probabilities" in result, "Result must not be empty"
    assert sim.history[-1] is result, "Result must not be empty"


def test_simulator_classical_evaluate_hypothesis():
    blue, red, payoff_blue, payoff_red = create_prisoners_dilemma()
    sim = BlueRedTeamSimulator(
        blue_strategies=blue,
        red_strategies=red,
        payoff_blue=payoff_blue,
        payoff_red=payoff_red,
        mode="classical",
    )
    result = sim.evaluate_hypothesis("classical")
    assert result["mode"] == "classical", "Result must not be empty"
    assert "gibbs_distribution" in result, "Result must not be empty"
    assert "converged" in result, "Result must not be empty"


def test_simulator_compare_strategies_quantum():
    blue, red, payoff_blue, payoff_red = create_prisoners_dilemma()
    sim = BlueRedTeamSimulator(
        blue_strategies=blue,
        red_strategies=red,
        payoff_blue=payoff_blue,
        payoff_red=payoff_red,
        mode="quantum",
    )
    options = [np.array([1.0, 1.0]), np.array([2.0, 1.0])]
    result = sim.compare_strategies(blue_options=options, red_options=options)
    assert result["total_configurations"] == 4, "Result must not be empty"
    assert "best_for_blue" in result, "Result must not be empty"
    assert "best_for_red" in result, "Result must not be empty"


def test_simulator_compare_strategies_classical():
    blue, red, payoff_blue, payoff_red = create_prisoners_dilemma()
    sim = BlueRedTeamSimulator(
        blue_strategies=blue,
        red_strategies=red,
        payoff_blue=payoff_blue,
        payoff_red=payoff_red,
        mode="classical",
    )
    options = [np.array([1.0, 1.0]), np.array([1.0, 2.0])]
    result = sim.compare_strategies(blue_options=options, red_options=options)
    assert result["total_configurations"] == 4, "Result must not be empty"


def test_simulator_run_simulation_quantum_and_classical():
    blue, red, payoff_blue, payoff_red = create_prisoners_dilemma()

    sim_q = BlueRedTeamSimulator(
        blue_strategies=blue,
        red_strategies=red,
        payoff_blue=payoff_blue,
        payoff_red=payoff_red,
        mode="quantum",
        noise_level=0.1,
    )
    out_q = sim_q.run_simulation(num_rounds=3, learning_rate=0.05)
    assert out_q["num_rounds"] == 3, "Condition must be true"
    assert len(out_q["rounds"]) == 3, "Collection must not be empty"
    assert "final_blue_payoff" in out_q, "Condition must be true"

    sim_c = BlueRedTeamSimulator(
        blue_strategies=blue,
        red_strategies=red,
        payoff_blue=payoff_blue,
        payoff_red=payoff_red,
        mode="classical",
    )
    out_c = sim_c.run_simulation(num_rounds=4, learning_rate=0.05)
    assert out_c["num_rounds"] == 4, "Condition must be true"
    assert len(out_c["rounds"]) == 4, "Collection must not be empty"


# ---------------------------------------------------------------------------
# Scenario factory functions
# ---------------------------------------------------------------------------
def test_create_prisoners_dilemma_shape():
    blue, red, p_blue, p_red = create_prisoners_dilemma()
    assert blue == ["Cooperate", "Defect"]
    assert red == ["Cooperate", "Defect"]
    assert p_blue.shape == (2, 2)
    assert p_red.shape == (2, 2)


def test_create_zero_sum_game_is_zero_sum():
    blue, red, p_blue, p_red = create_zero_sum_game(size=3, seed=42)
    assert len(blue) == 3 and len(red) == 3, "Blue must not be empty"
    np.testing.assert_allclose(p_blue + p_red, 0.0)


def test_create_security_game_shape():
    blue, red, p_blue, p_red = create_security_game()
    assert len(blue) == 4, "Blue must not be empty"
    assert len(red) == 4, "Red must not be empty"
    assert p_blue.shape == (4, 4)
    assert p_red.shape == (4, 4)
    # payoff_red = 1 - payoff_blue
    np.testing.assert_allclose(p_blue + p_red, 1.0)

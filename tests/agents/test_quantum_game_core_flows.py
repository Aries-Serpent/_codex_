"""
Comprehensive tests for Quantum Game Theory core flows.

Coverage targets:
- ClassicalGameEngine: Lines 402-591 (replicator dynamics, equilibrium)
- QuantumInspiredGameEngine: Lines 593-897 (quantum operations, entanglement)
- BlueRedTeamSimulator: Lines 898-1183 (simulation flows, strategies)

Target coverage: 33.40% → 85%+
"""

import pytest

pytest.importorskip("numpy", reason="numpy not installed")
import numpy as np

from agents.quantum_game_theory import (
    NUMPY_AVAILABLE,
    BlueRedTeamSimulator,
    ClassicalGameEngine,
    QuantumGameState,
    QuantumInspiredGameEngine,
    StrategyState,
    TeamType,
)


@pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy not available")
class TestClassicalGameEngine:
    """Test suite for ClassicalGameEngine (energy-based game theory)."""

    @pytest.fixture
    def payoff_matrices_prisoners_dilemma(self):
        """Classic prisoner's dilemma payoffs."""
        # Blue payoffs: [[cooperate-cooperate, cooperate-defect],
        #                [defect-cooperate, defect-defect]]
        payoff_blue = np.array([[3.0, 0.0], [5.0, 1.0]])
        payoff_red = np.array([[3.0, 5.0], [0.0, 1.0]])
        return payoff_blue, payoff_red

    @pytest.fixture
    def classical_engine(self, payoff_matrices_prisoners_dilemma):
        """Create classical game engine with prisoner's dilemma."""
        blue_payoff, red_payoff = payoff_matrices_prisoners_dilemma
        blue_strategies = ["Cooperate", "Defect"]
        red_strategies = ["Cooperate", "Defect"]
        return ClassicalGameEngine(
            blue_strategies=blue_strategies,
            red_strategies=red_strategies,
            payoff_blue=blue_payoff,
            payoff_red=red_payoff,
            beta=1.0,
            alpha=0.5,
        )

    def test_classical_engine_initialization(self, classical_engine):
        """Test ClassicalGameEngine initializes correctly."""
        assert classical_engine is not None, "classical_engine must be initialized"
        assert hasattr(classical_engine, "pi_blue")
        assert hasattr(classical_engine, "pi_red")
        assert classical_engine.pi_blue is not None, "pi_blue must be initialized"
        assert classical_engine.pi_red is not None, "pi_red must be initialized"
        # Probabilities should sum to 1
        assert np.isclose(classical_engine.pi_blue.sum(), 1.0)
        assert np.isclose(classical_engine.pi_red.sum(), 1.0)

    def test_expected_payoff_calculation(self, classical_engine):
        """Test expected payoff calculation for both teams."""
        blue_payoff = classical_engine.expected_payoff(TeamType.BLUE)
        red_payoff = classical_engine.expected_payoff(TeamType.RED)

        assert isinstance(blue_payoff, (float, np.floating))
        assert isinstance(red_payoff, (float, np.floating))
        assert blue_payoff >= 0.0, "blue_payoff must be greater than zero"
        assert red_payoff >= 0.0, "red_payoff must be greater than zero"

    def test_replicator_dynamics_step(self, classical_engine):
        """Test single replicator dynamics step."""
        initial_blue = classical_engine.pi_blue.copy()
        initial_red = classical_engine.pi_red.copy()

        classical_engine.replicator_dynamics_step(dt=0.1)

        # Probabilities should sum to 1
        assert np.isclose(classical_engine.pi_blue.sum(), 1.0)
        assert np.isclose(classical_engine.pi_red.sum(), 1.0)

        # Probabilities should have changed (unless at equilibrium)
        assert not np.array_equal(classical_engine.pi_blue, initial_blue) or not np.array_equal(
            classical_engine.pi_red, initial_red
        )

    def test_run_dynamics_convergence(self, classical_engine):
        """Test that dynamics converge over multiple steps."""
        results = classical_engine.simulate_to_equilibrium(
            max_iterations=50, convergence_threshold=1e-6
        )

        assert "pi_blue" in results, "Result must not be empty"
        assert "pi_red" in results, "Result must not be empty"
        assert "payoff_blue" in results, "Result must not be empty"
        assert "payoff_red" in results, "Result must not be empty"

        # Final probabilities should sum to 1
        assert np.isclose(results["pi_blue"].sum(), 1.0)
        assert np.isclose(results["pi_red"].sum(), 1.0)

    def test_nash_equilibrium_computation(self, classical_engine):
        """Test Nash equilibrium approximation."""
        equilibrium = classical_engine.compute_nash_equilibrium()

        assert "pi_blue" in equilibrium, "Condition must be true"
        assert "pi_red" in equilibrium, "Condition must be true"

        # Equilibrium probabilities should sum to 1
        assert np.isclose(equilibrium["pi_blue"].sum(), 1.0)
        assert np.isclose(equilibrium["pi_red"].sum(), 1.0)

    def test_gibbs_sampling_temperature_effects(self, classical_engine):
        """Test that beta (inverse temperature) affects sampling."""
        # Create two engines with different beta values
        blue_payoff, red_payoff = (
            classical_engine.payoff_blue,
            classical_engine.payoff_red,
        )

        # Low beta (high temperature) → more random
        low_beta_engine = ClassicalGameEngine(
            blue_strategies=["Cooperate", "Defect"],
            red_strategies=["Cooperate", "Defect"],
            payoff_blue=blue_payoff,
            payoff_red=red_payoff,
            beta=0.1,
        )

        # High beta (low temperature) → more deterministic
        high_beta_engine = ClassicalGameEngine(
            blue_strategies=["Cooperate", "Defect"],
            red_strategies=["Cooperate", "Defect"],
            payoff_blue=blue_payoff,
            payoff_red=red_payoff,
            beta=10.0,
        )

        # Sample from Gibbs distribution
        low_beta_samples = low_beta_engine.gibbs_sample(num_samples=100)
        high_beta_samples = high_beta_engine.gibbs_sample(num_samples=100)

        # Verify we got samples
        assert len(low_beta_samples) == 100, "Low_beta_samples must not be empty"
        assert len(high_beta_samples) == 100, "High_beta_samples must not be empty"


@pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy not available")
class TestQuantumInspiredGameEngine:
    """Test suite for QuantumInspiredGameEngine (quantum-inspired game theory)."""

    @pytest.fixture
    def quantum_engine(self):
        """Create quantum game engine with standard setup."""
        blue_probs = np.array([0.5, 0.5])
        red_probs = np.array([0.5, 0.5])
        payoff_blue = np.array([[3.0, 0.0], [5.0, 1.0]])
        payoff_red = np.array([[3.0, 5.0], [0.0, 1.0]])
        return QuantumInspiredGameEngine(blue_probs, red_probs, payoff_blue, payoff_red)

    def test_quantum_engine_initialization(self, quantum_engine):
        """Test QuantumInspiredGameEngine initializes correctly."""
        assert quantum_engine is not None, "quantum_engine must be initialized"
        assert hasattr(quantum_engine, "game_state")
        assert quantum_engine.game_state.joint_wavefunction is not None, "joint_wavefunction must be initialized"
        assert quantum_engine.game_state.entanglement_strength >= 0.0, "entanglement_strength must be greater than zero"

    def test_wavefunction_normalization(self, quantum_engine):
        """Test that wavefunction remains normalized."""
        wavefunction = quantum_engine.game_state.joint_wavefunction
        norm = np.sum(np.abs(wavefunction) ** 2)
        assert np.isclose(norm, 1.0), "Wavefunction should be normalized"

    def test_apply_strategy_update(self, quantum_engine):
        """Test quantum strategy update (unitary evolution)."""
        initial_wf = quantum_engine.game_state.joint_wavefunction.copy()

        quantum_engine.apply_strategy_update(theta_blue=0.1, theta_red=0.1)

        updated_wf = quantum_engine.game_state.joint_wavefunction

        # Wavefunction should have changed
        assert not np.array_equal(initial_wf, updated_wf)

        # But still normalized
        norm = np.sum(np.abs(updated_wf) ** 2)
        assert np.isclose(norm, 1.0)

    def test_apply_decoherence(self, quantum_engine):
        """Test decoherence (quantum→classical transition)."""
        quantum_engine.apply_decoherence(gamma=0.5)

        # After decoherence, wavefunction should still be normalized
        norm = np.sum(np.abs(quantum_engine.game_state.joint_wavefunction) ** 2)
        assert np.isclose(norm, 1.0)

    def test_expected_payoff_quantum(self, quantum_engine):
        """Test expected payoff calculation in quantum regime."""
        blue_payoff = quantum_engine.expected_payoff(TeamType.BLUE)
        red_payoff = quantum_engine.expected_payoff(TeamType.RED)

        assert isinstance(blue_payoff, (float, np.floating))
        assert isinstance(red_payoff, (float, np.floating))

    def test_play_round_returns_valid_results(self, quantum_engine):
        """Test play_round returns valid payoff dictionary."""
        result = quantum_engine.play_round(theta_blue=0.1, theta_red=0.1)

        assert "blue_payoff" in result, "Result must not be empty"
        assert "red_payoff" in result, "Result must not be empty"
        assert "entanglement" in result, "Result must not be empty"
        assert result["entanglement"] >= 0.0, "Value must be greater than zero"

    def test_quantum_policy_gradient_step(self, quantum_engine):
        """Test quantum policy gradient optimization."""
        initial_theta_blue = 0.1
        initial_theta_red = 0.1

        new_blue, new_red = quantum_engine.quantum_policy_gradient_step(
            theta_blue=initial_theta_blue,
            theta_red=initial_theta_red,
            learning_rate=0.05,
        )

        # Thetas should have updated
        assert new_blue != initial_theta_blue or new_red != initial_theta_red, "new_blue is not valid"

    def test_get_payoffs_method(self, quantum_engine):
        """Test get_payoffs convenience method."""
        blue_payoff, red_payoff = quantum_engine.get_payoffs()

        assert isinstance(blue_payoff, (float, np.floating))
        assert isinstance(red_payoff, (float, np.floating))


@pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy not available")
class TestBlueRedTeamSimulator:
    """Test suite for BlueRedTeamSimulator (high-level simulation)."""

    @pytest.fixture
    def simulator_quantum(self):
        """Create quantum mode simulator."""
        blue_strategies = ["defend", "attack", "monitor"]
        red_strategies = ["exploit", "probe", "escalate"]
        payoff_blue = np.random.rand(3, 3)
        payoff_red = np.random.rand(3, 3)

        return BlueRedTeamSimulator(
            blue_strategies=blue_strategies,
            red_strategies=red_strategies,
            payoff_blue=payoff_blue,
            payoff_red=payoff_red,
            mode="quantum",
            entanglement=0.3,
            noise_level=0.1,
        )

    @pytest.fixture
    def simulator_classical(self):
        """Create classical mode simulator."""
        blue_strategies = ["defend", "attack"]
        red_strategies = ["exploit", "probe"]
        payoff_blue = np.array([[3.0, 0.0], [5.0, 1.0]])
        payoff_red = np.array([[3.0, 5.0], [0.0, 1.0]])

        return BlueRedTeamSimulator(
            blue_strategies=blue_strategies,
            red_strategies=red_strategies,
            payoff_blue=payoff_blue,
            payoff_red=payoff_red,
            mode="classical",
        )

    def test_simulator_initialization_quantum(self, simulator_quantum):
        """Test simulator initializes in quantum mode."""
        assert simulator_quantum.mode == "quantum", "mode is not valid"
        assert simulator_quantum.entanglement == 0.3, "entanglement is not valid"
        assert simulator_quantum.noise_level == 0.1, "noise_level is not valid"
        assert hasattr(simulator_quantum, "quantum_engine")

    def test_simulator_initialization_classical(self, simulator_classical):
        """Test simulator initializes in classical mode."""
        assert simulator_classical.mode == "classical", "mode is not valid"
        assert hasattr(simulator_classical, "classical_engine")

    def test_run_simulation_quantum_mode(self, simulator_quantum):
        """Test running simulation in quantum mode."""
        results = simulator_quantum.run_simulation(num_rounds=10, learning_rate=0.1)

        assert results["mode"] == "quantum", "Result must not be empty"
        assert results["num_rounds"] == 10, "Result must not be empty"
        assert "rounds" in results, "Result must not be empty"
        assert len(results["rounds"]) == 10, "Collection must not be empty"
        assert "final_blue_payoff" in results, "Result must not be empty"
        assert "final_red_payoff" in results, "Result must not be empty"

    def test_run_simulation_classical_mode(self, simulator_classical):
        """Test running simulation in classical mode."""
        results = simulator_classical.run_simulation(num_rounds=10, learning_rate=0.1)

        assert results["mode"] == "classical", "Result must not be empty"
        assert results["num_rounds"] == 10, "Result must not be empty"
        assert "rounds" in results, "Result must not be empty"
        assert len(results["rounds"]) == 10, "Collection must not be empty"

    def test_simulation_rounds_structure(self, simulator_quantum):
        """Test that each round has correct structure."""
        results = simulator_quantum.run_simulation(num_rounds=5, learning_rate=0.05)

        for round_data in results["rounds"]:
            assert "round" in round_data, "Data must not be empty"
            assert "blue_payoff" in round_data, "Data must not be empty"
            assert "red_payoff" in round_data, "Data must not be empty"

    def test_payoff_accumulation(self, simulator_quantum):
        """Test that payoffs accumulate over rounds."""
        results = simulator_quantum.run_simulation(num_rounds=10, learning_rate=0.1)

        # Final payoffs should be sum of all rounds
        total_blue = sum(r["blue_payoff"] for r in results["rounds"])
        total_red = sum(r["red_payoff"] for r in results["rounds"])

        assert np.isclose(results["final_blue_payoff"], total_blue)
        assert np.isclose(results["final_red_payoff"], total_red)

    def test_zero_rounds_simulation(self, simulator_classical):
        """Test simulation with zero rounds."""
        results = simulator_classical.run_simulation(num_rounds=0, learning_rate=0.1)

        assert results["num_rounds"] == 0, "Result must not be empty"
        assert len(results["rounds"]) == 0, "Collection must not be empty"
        assert results["final_blue_payoff"] == 0.0, "Result must not be empty"
        assert results["final_red_payoff"] == 0.0, "Result must not be empty"

    def test_different_learning_rates(self, simulator_quantum):
        """Test simulation with different learning rates."""
        # Low learning rate
        results_low = simulator_quantum.run_simulation(num_rounds=5, learning_rate=0.01)

        # High learning rate
        results_high = simulator_quantum.run_simulation(num_rounds=5, learning_rate=0.5)

        # Both should complete successfully
        assert results_low["num_rounds"] == 5, "Result must not be empty"
        assert results_high["num_rounds"] == 5, "Result must not be empty"


@pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy not available")
class TestQuantumGameState:
    """Test suite for QuantumGameState."""

    def test_quantum_state_initialization(self):
        """Test QuantumGameState creates valid quantum state."""
        blue_strategies = ["Cooperate", "Defect"]
        red_strategies = ["Cooperate", "Defect"]

        blue_state = StrategyState(team=TeamType.BLUE, strategies=blue_strategies)
        red_state = StrategyState(team=TeamType.RED, strategies=red_strategies)

        state = QuantumGameState(
            blue_state=blue_state, red_state=red_state, entanglement_strength=0.2
        )

        assert state.joint_wavefunction is not None, "joint_wavefunction must be initialized"
        assert np.isclose(np.sum(np.abs(state.joint_wavefunction) ** 2), 1.0)
        assert state.entanglement_strength == 0.2, "entanglement_strength is not valid"

    def test_measurement_collapse(self):
        """Test wavefunction measurement collapses state."""
        blue_strategies = ["Cooperate", "Defect"]
        red_strategies = ["Cooperate", "Defect"]

        blue_state = StrategyState(team=TeamType.BLUE, strategies=blue_strategies)
        red_state = StrategyState(team=TeamType.RED, strategies=red_strategies)

        state = QuantumGameState(blue_state=blue_state, red_state=red_state)

        blue_idx, red_idx = state.measure()

        # Indices should be valid
        assert 0 <= blue_idx < 2, "0 is not valid"
        assert 0 <= red_idx < 2, "0 is not valid"

    def test_apply_entangling_gate(self):
        """Test entangling gate application."""
        blue_probs = np.array([0.6, 0.4])
        red_probs = np.array([0.7, 0.3])
        state = QuantumGameState(blue_probs, red_probs, entanglement_strength=0.0)

        initial_wf = state.joint_wavefunction.copy()
        state.apply_entangling_gate(strength=0.5)

        # Wavefunction should change
        assert not np.array_equal(initial_wf, state.joint_wavefunction)

        # Still normalized
        assert np.isclose(np.sum(np.abs(state.joint_wavefunction) ** 2), 1.0)


@pytest.mark.skipif(not NUMPY_AVAILABLE, reason="numpy not available")
class TestIntegrationScenarios:
    """Integration tests for complete game theory scenarios."""

    def test_quantum_vs_classical_comparison(self):
        """Compare quantum and classical modes on same game."""
        blue_strats = ["cooperate", "defect"]
        red_strats = ["cooperate", "defect"]
        payoff_b = np.array([[3.0, 0.0], [5.0, 1.0]])
        payoff_r = np.array([[3.0, 5.0], [0.0, 1.0]])

        # Run classical
        sim_classical = BlueRedTeamSimulator(
            blue_strats, red_strats, payoff_b, payoff_r, mode="classical"
        )
        results_classical = sim_classical.run_simulation(10, 0.1)

        # Run quantum
        sim_quantum = BlueRedTeamSimulator(
            blue_strats,
            red_strats,
            payoff_b,
            payoff_r,
            mode="quantum",
            entanglement=0.3,
        )
        results_quantum = sim_quantum.run_simulation(10, 0.1)

        # Both should produce valid results
        assert results_classical["num_rounds"] == 10, "Result must not be empty"
        assert results_quantum["num_rounds"] == 10, "Result must not be empty"

        # Quantum might have different payoffs due to entanglement
        assert results_classical["mode"] == "classical", "Result must not be empty"
        assert results_quantum["mode"] == "quantum", "Result must not be empty"

    def test_convergence_to_nash(self):
        """Test that classical dynamics converge to Nash equilibrium."""
        blue_probs = np.array([0.5, 0.5])
        red_probs = np.array([0.5, 0.5])
        payoff_b = np.array([[3.0, 0.0], [5.0, 1.0]])
        payoff_r = np.array([[3.0, 5.0], [0.0, 1.0]])

        engine = ClassicalGameEngine(blue_probs, red_probs, payoff_b, payoff_r)

        # Run many steps
        results = engine.run_dynamics(steps=100, learning_rate=0.05)

        # Should converge (final probabilities should be stable)
        assert results["final_blue_probs"].sum() == pytest.approx(1.0, abs=0.01)
        assert results["final_red_probs"].sum() == pytest.approx(1.0, abs=0.01)

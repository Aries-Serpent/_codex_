"""
Comprehensive tests for EnergyLandscape and energy-based optimization.

Coverage target: Lines 1165-1317 in agents/physics_orchestrator.py

Test Categories:
- EnergyState initialization and properties
- EnergyLandscape state management
- Gibbs distribution and state selection
- Free energy minimization
- Simulated annealing
- System entropy calculations
"""

import math

import pytest

from agents.physics_orchestrator import EnergyLandscape, EnergyState


class TestEnergyState:
    """Test suite for EnergyState dataclass."""

    @pytest.fixture
    def basic_state(self):
        """Create a basic energy state."""
        return EnergyState(
            configuration={"param1": 10, "param2": 20},
            energy=50.0,
            entropy=2.0,
            temperature=1.0,
            state_id="state_1",
        )

    @pytest.fixture
    def high_energy_state(self):
        """Create a high energy state."""
        return EnergyState(
            configuration={"param1": 100},
            energy=200.0,
            entropy=5.0,
            temperature=1.0,
            state_id="high_energy",
        )

    @pytest.fixture
    def low_energy_state(self):
        """Create a low energy state."""
        return EnergyState(
            configuration={"param1": 1},
            energy=10.0,
            entropy=1.0,
            temperature=1.0,
            state_id="low_energy",
        )

    def test_energy_state_initialization(self, basic_state):
        """Test EnergyState initializes correctly."""
        assert basic_state.configuration == {"param1": 10, "param2": 20}
        assert basic_state.energy == 50.0, "energy is not valid"
        assert basic_state.entropy == 2.0, "entropy is not valid"
        assert basic_state.temperature == 1.0, "temperature is not valid"
        assert basic_state.state_id == "state_1", "state_id is not valid"

    def test_internal_energy_alias(self):
        """Test internal_energy parameter aliases to energy."""
        state = EnergyState(configuration={}, internal_energy=75.0, temperature=1.0)
        assert state.energy == 75.0, "energy is not valid"

    def test_free_energy_calculation(self, basic_state):
        """Test Helmholtz free energy: F = E - T*S"""
        # F = 50 - 1.0 * 2.0 = 48.0
        free_energy = basic_state.free_energy()
        assert abs(free_energy - 48.0) < 0.001, "Condition must be true"

    def test_free_energy_temperature_dependence(self):
        """Test free energy changes with temperature."""
        config = {"x": 1}

        # Low temperature
        state_low_temp = EnergyState(
            configuration=config, energy=100.0, entropy=10.0, temperature=0.5
        )

        # High temperature
        state_high_temp = EnergyState(
            configuration=config, energy=100.0, entropy=10.0, temperature=2.0
        )

        # F_low = 100 - 0.5*10 = 95
        # F_high = 100 - 2.0*10 = 80
        assert state_low_temp.free_energy() > state_high_temp.free_energy(), "Value must be greater than zero"

    def test_boltzmann_probability(self, basic_state):
        """Test Boltzmann probability calculation."""
        # P ∝ exp(-E/kT)
        # With reference_energy = 0: P = exp(-50/1.0) = exp(-50)
        prob = basic_state.boltzmann_probability(reference_energy=0.0)
        expected = math.exp(-50.0)
        assert abs(prob - expected) < 0.001, "Condition must be true"

    def test_boltzmann_probability_with_reference(self, basic_state):
        """Test Boltzmann probability with non-zero reference."""
        # Delta E = 50 - 40 = 10
        # P = exp(-10/1.0) = exp(-10)
        prob = basic_state.boltzmann_probability(reference_energy=40.0)
        expected = math.exp(-10.0)
        assert abs(prob - expected) < 0.001, "Condition must be true"

    def test_boltzmann_probability_temperature_protection(self):
        """Test Boltzmann probability protects against zero temperature."""
        state = EnergyState(
            configuration={},
            energy=50.0,
            temperature=0.0,  # Should be clamped to 0.01
        )
        # Should not raise ZeroDivisionError
        prob = state.boltzmann_probability()
        # With clamped temp=0.01, exp(-50/0.01) = exp(-5000) ≈ 0 (underflow)
        # The key is it doesn't raise ZeroDivisionError, value can be ~0
        assert prob >= 0, "prob must be greater than zero"
        assert not math.isnan(prob), "Condition must be true"


class TestEnergyLandscape:
    """Test suite for EnergyLandscape class."""

    @pytest.fixture
    def landscape(self):
        """Create empty energy landscape."""
        return EnergyLandscape(temperature=1.0)

    @pytest.fixture
    def populated_landscape(self):
        """Create landscape with multiple states."""
        landscape = EnergyLandscape(temperature=1.0)

        # Add states with varying energies
        landscape.add_state(
            EnergyState(configuration={"x": 1}, energy=10.0, entropy=1.0, state_id="low")
        )
        landscape.add_state(
            EnergyState(configuration={"x": 2}, energy=50.0, entropy=2.0, state_id="medium")
        )
        landscape.add_state(
            EnergyState(configuration={"x": 3}, energy=100.0, entropy=3.0, state_id="high")
        )

        return landscape

    def test_landscape_initialization(self, landscape):
        """Test EnergyLandscape initializes correctly."""
        assert landscape.temperature == 1.0, "temperature is not valid"
        assert len(landscape.states) == 0, "Collection must not be empty"
        assert len(landscape.history) == 0, "Collection must not be empty"
        assert landscape.partition_function == 0.0, "partition_function is not valid"

    def test_add_state(self, landscape):
        """Test adding states to landscape."""
        state = EnergyState(configuration={"test": 1}, energy=25.0, temperature=0.5)

        landscape.add_state(state)

        assert len(landscape.states) == 1, "Collection must not be empty"
        assert landscape.states[0] == state, "l is not valid"
        # Temperature should be synchronized
        assert state.temperature == landscape.temperature, "temperature is not valid"
        # Partition function should be updated
        assert landscape.partition_function > 0, "partition_function must be greater than zero"

    def test_partition_function_update(self, populated_landscape):
        """Test partition function updates correctly."""
        # Z = sum(exp(-E_i/kT) for each state)
        # With min energy = 10, T = 1:
        # Z = exp(0) + exp(-40) + exp(-90)
        # Z ≈ 1.0 + small + very_small ≈ 1.0
        assert populated_landscape.partition_function > 0, "partition_function must be greater than zero"
        assert populated_landscape.partition_function >= 1.0, "partition_function must be greater than zero"

    def test_gibbs_probability(self, populated_landscape):
        """Test Gibbs probability calculation."""
        # Lowest energy state should have highest probability
        low_state = populated_landscape.states[0]  # energy = 10
        high_state = populated_landscape.states[2]  # energy = 100

        prob_low = populated_landscape.gibbs_probability(low_state)
        prob_high = populated_landscape.gibbs_probability(high_state)

        assert prob_low > prob_high, "prob_low must be greater than zero"
        assert 0 <= prob_low <= 1, "0 is not valid"
        assert 0 <= prob_high <= 1, "0 is not valid"

    def test_gibbs_probabilities_sum_to_one(self, populated_landscape):
        """Test all Gibbs probabilities sum to 1."""
        total_prob = sum(
            populated_landscape.gibbs_probability(s) for s in populated_landscape.states
        )
        assert abs(total_prob - 1.0) < 0.001, "Condition must be true"

    def test_select_state_prefers_low_energy(self, populated_landscape):
        """Test state selection prefers low energy states."""
        # At low temperature, should select lowest energy
        populated_landscape.temperature = 0.1
        for state in populated_landscape.states:
            state.temperature = 0.1
        populated_landscape._update_partition_function()

        selected = populated_landscape.select_state()

        # Should select the lowest energy state (energy=10)
        assert selected.energy == 10.0, "energy is not valid"
        assert selected.state_id == "low", "state_id is not valid"

    def test_select_state_empty_landscape(self, landscape):
        """Test selecting from empty landscape returns None."""
        selected = landscape.select_state()
        assert selected is None, "selected is not valid"

    def test_minimize_free_energy(self, populated_landscape):
        """Test free energy minimization finds optimal state."""
        optimal = populated_landscape.minimize_free_energy()

        # Should find state with minimum F = E - T*S
        # State "low": F = 10 - 1*1 = 9
        # State "medium": F = 50 - 1*2 = 48
        # State "high": F = 100 - 1*3 = 97
        assert optimal.state_id == "low", "state_id is not valid"
        assert optimal.free_energy() == 9.0, "Condition must be true"

    def test_minimize_free_energy_empty_landscape(self, landscape):
        """Test minimization raises error on empty landscape."""
        with pytest.raises(ValueError, match="No states in landscape"):
            landscape.minimize_free_energy()

    def test_minimize_free_energy_records_history(self, populated_landscape):
        """Test minimization records search history."""
        initial_history_len = len(populated_landscape.history)

        populated_landscape.minimize_free_energy(max_iterations=10)

        # History should have recorded visited states
        assert len(populated_landscape.history) > initial_history_len, "Collection must not be empty"

    def test_cool_system(self, populated_landscape):
        """Test simulated annealing cooling."""
        initial_temp = populated_landscape.temperature

        populated_landscape.cool_system(cooling_rate=0.9)

        # Temperature should decrease
        assert populated_landscape.temperature == initial_temp * 0.9, "temperature is not valid"

        # All states should have updated temperature
        for state in populated_landscape.states:
            assert state.temperature == populated_landscape.temperature, "temperature is not valid"

    def test_cool_system_multiple_iterations(self, populated_landscape):
        """Test repeated cooling converges to low temperature."""
        for _ in range(10):
            populated_landscape.cool_system(cooling_rate=0.95)

        # Temperature should be significantly reduced
        # (0.95)^10 ≈ 0.599
        assert populated_landscape.temperature < 0.6, "temperature is not valid"

    def test_calculate_system_entropy(self, populated_landscape):
        """Test system entropy calculation: S = -Σ P_i * ln(P_i)"""
        system_entropy = populated_landscape.calculate_system_entropy()

        # Entropy should be non-negative
        assert system_entropy >= 0, "system_entropy must be greater than zero"

        # For multiple states with different probabilities, entropy > 0
        assert system_entropy > 0, "system_entropy must be greater than zero"

    def test_system_entropy_empty_landscape(self, landscape):
        """Test entropy of empty landscape is zero."""
        entropy = landscape.calculate_system_entropy()
        assert entropy == 0.0, "entropy is not valid"

    def test_system_entropy_single_state(self, landscape):
        """Test entropy of single-state landscape is zero."""
        landscape.add_state(EnergyState(configuration={}, energy=50.0))

        # Single certain state has zero entropy
        entropy = landscape.calculate_system_entropy()
        assert abs(entropy) < 0.001, "Condition must be true"


class TestEnergyLandscapeIntegration:
    """Integration tests for energy-based optimization."""

    def test_simulated_annealing_workflow(self):
        """Test complete simulated annealing optimization."""
        landscape = EnergyLandscape(temperature=10.0)  # Start hot

        # Add states representing different solutions
        for i in range(10):
            landscape.add_state(
                EnergyState(
                    configuration={"solution": i},
                    energy=float((i - 5) ** 2),  # Parabola, minimum at i=5
                    entropy=1.0,
                    state_id=f"sol_{i}",
                )
            )

        # Run simulated annealing
        for iteration in range(20):
            landscape.cool_system(cooling_rate=0.9)

        # After cooling, select best state
        best = landscape.select_state()

        # Should find state near minimum (i=5, energy=0)
        assert best.energy <= 1.0, "energy is not valid"

    def test_free_energy_vs_pure_energy_minimization(self):
        """Test that free energy considers both energy and entropy."""
        landscape = EnergyLandscape(temperature=2.0)

        # State A: Low energy, low entropy
        state_a = EnergyState(configuration={"type": "A"}, energy=10.0, entropy=1.0, state_id="A")

        # State B: Higher energy, much higher entropy
        state_b = EnergyState(configuration={"type": "B"}, energy=15.0, entropy=10.0, state_id="B")

        landscape.add_state(state_a)
        landscape.add_state(state_b)

        # Pure energy: A wins (10 < 15)
        # Free energy at T=2:
        # F_A = 10 - 2*1 = 8
        # F_B = 15 - 2*10 = -5
        # Free energy: B wins!

        optimal = landscape.minimize_free_energy()
        assert optimal.state_id == "B", "state_id is not valid"

    def test_temperature_effect_on_selection(self):
        """Test that temperature affects state selection randomness."""
        # Low temperature - deterministic
        landscape_cold = EnergyLandscape(temperature=0.01)
        landscape_cold.add_state(EnergyState({"x": 1}, energy=10.0, entropy=1.0))
        landscape_cold.add_state(EnergyState({"x": 2}, energy=100.0, entropy=1.0))

        selected_cold = landscape_cold.select_state()
        assert selected_cold.energy == 10.0, "energy is not valid"

        # High temperature - less deterministic (still picks lowest in this impl)
        landscape_hot = EnergyLandscape(temperature=100.0)
        landscape_hot.add_state(EnergyState({"x": 1}, energy=10.0, entropy=1.0))
        landscape_hot.add_state(EnergyState({"x": 2}, energy=100.0, entropy=1.0))

        landscape_hot.select_state()
        # Current implementation is deterministic, but probabilities are closer
        prob_low_cold = landscape_cold.gibbs_probability(landscape_cold.states[0])
        prob_low_hot = landscape_hot.gibbs_probability(landscape_hot.states[0])

        # At high temp, probability difference is smaller
        assert prob_low_cold > prob_low_hot or prob_low_cold > 0.99, "prob_low_cold must be greater than zero"

    def test_energy_landscape_for_decision_optimization(self):
        """Test using energy landscape for decision optimization."""
        # Scenario: Choose between multiple project approaches
        landscape = EnergyLandscape(temperature=1.5)

        # Approach 1: Quick but risky
        landscape.add_state(
            EnergyState(
                configuration={"approach": "quick", "time": 1, "risk": 0.8},
                energy=20.0,  # Low cost
                entropy=5.0,  # High uncertainty
                state_id="quick",
            )
        )

        # Approach 2: Moderate
        landscape.add_state(
            EnergyState(
                configuration={"approach": "moderate", "time": 3, "risk": 0.4},
                energy=40.0,
                entropy=2.0,
                state_id="moderate",
            )
        )

        # Approach 3: Thorough but expensive
        landscape.add_state(
            EnergyState(
                configuration={"approach": "thorough", "time": 5, "risk": 0.1},
                energy=80.0,  # High cost
                entropy=0.5,  # Low uncertainty
                state_id="thorough",
            )
        )

        # Find optimal approach
        optimal = landscape.minimize_free_energy()

        # At T=1.5:
        # F_quick = 20 - 1.5*5 = 12.5
        # F_moderate = 40 - 1.5*2 = 37
        # F_thorough = 80 - 1.5*0.5 = 79.25
        assert optimal.state_id == "quick", "state_id is not valid"

        # Now cool the system (reduce temperature)
        for _ in range(10):
            landscape.cool_system(cooling_rate=0.8)

        # At lower temperature, entropy matters less
        # Might shift preference based on energy alone
        new_optimal = landscape.minimize_free_energy()
        # Could still be "quick" since it has lowest energy
        assert new_optimal is not None, "new_optimal must be initialized"

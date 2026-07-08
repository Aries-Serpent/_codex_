"""
Unit tests for Advanced Physics Calculators.

Tests all emerging physics paradigms:
1. Chaos Theory
2. Fractal Geometry
3. Fluid Dynamics
4. Electromagnetic Fields
5. Wave Propagation
6. Relativistic Effects
"""

import pytest

# Skip entire module if numpy is not available (optional dependency)
np = pytest.importorskip("numpy", reason="numpy required for advanced physics calculations")

from agents.advanced_physics_calculators import (
    AdvancedPhysicsOrchestrator,
    ChaoticAttractor,
    ChaoticNeuralNetwork,
    EMFieldRouter,
    FluidChannel,
    FluidFlowScheduler,
    FractalAnalyzer,
    RelativityScheduler,
    WavePropagator,
)

# =============================================================================
# CHAOS THEORY TESTS
# =============================================================================


class TestChaoticAttractor:
    """Test chaotic attractor implementations."""

    def test_logistic_map_iteration(self):
        """Test logistic map produces values in [0,1]."""
        attractor = ChaoticAttractor(attractor_type="logistic")

        for _ in range(100):
            state = attractor.iterate(1)
            assert 0.0 <= state[0] <= 1.0, "Logistic map should stay in [0,1]"

    def test_logistic_map_chaos(self):
        """Test logistic map exhibits chaos for r=3.9."""
        attractor = ChaoticAttractor(attractor_type="logistic", parameters={"r": 3.9})

        # Iterate and collect states
        states = []
        for _ in range(1000):
            state = attractor.iterate(1)
            states.append(state[0])

        # Chaos: no fixed point, should have high variance
        variance = np.var(states[100:])  # Skip transient
        assert variance > 0.01, "Chaotic system should have high variance"

    def test_lyapunov_exponent_positive(self):
        """Test Lyapunov exponent is positive for chaotic regime."""
        attractor = ChaoticAttractor(attractor_type="logistic", parameters={"r": 3.9})

        lyapunov = attractor.lyapunov_exponent(iterations=500)

        # For r=3.9, Lyapunov exponent should be positive (chaotic)
        assert lyapunov > 0, "Lyapunov exponent should be positive for chaos"


class TestChaoticNeuralNetwork:
    """Test chaotic neural network functionality."""

    def test_network_initialization(self):
        """Test network initializes correctly."""
        cnn = ChaoticNeuralNetwork(num_neurons=10)

        assert len(cnn.neurons) == 10, "Collection must not be empty"
        assert cnn.coupling_strength == 0.1, "coupling_strength is not valid"

    def test_parameter_generation(self):
        """Test chaotic test parameter generation."""
        cnn = ChaoticNeuralNetwork(num_neurons=3)

        param_ranges = [(0.0, 10.0), (0.0, 1.0), (-5.0, 5.0)]
        test_cases = cnn.generate_test_parameters(param_ranges, num_tests=50)

        assert len(test_cases) == 50, "Test_cases must not be empty"

        # Check parameters are within ranges
        for params in test_cases:
            assert len(params) == 3, "Params must not be empty"
            assert 0.0 <= params[0] <= 10.0, "0 is not valid"
            assert 0.0 <= params[1] <= 1.0, "0 is not valid"
            assert -5.0 <= params[2] <= 5.0, "0 is not valid"

    def test_parameter_generation_zero_tests(self):
        """Test generating zero test cases returns empty list."""
        cnn = ChaoticNeuralNetwork(num_neurons=3)

        param_ranges = [(0.0, 10.0)]
        test_cases = cnn.generate_test_parameters(param_ranges, num_tests=0)

        assert len(test_cases) == 0, "Test_cases must not be empty"
        assert isinstance(test_cases, list)


# =============================================================================
# FRACTAL GEOMETRY TESTS
# =============================================================================


class TestFractalAnalyzer:
    """Test fractal analysis functionality."""

    def test_box_counting_dimension_line(self):
        """Test box counting for a line (dimension ≈ 1)."""
        analyzer = FractalAnalyzer()

        # Create a line
        points = np.array([[i / 100, i / 100] for i in range(100)])

        dimension = analyzer.box_counting_dimension(points)

        # Line should have dimension close to 1 (allowing wider range for discrete sampling)
        assert 0.6 <= dimension <= 1.4, f"Line dimension should be ~1, got {dimension}"

    def test_code_tree_analysis(self):
        """Test code tree fractal analysis."""
        analyzer = FractalAnalyzer()

        # Create a simple tree structure
        tree = {
            "module": {
                "class1": {"method1": {}, "method2": {}},
                "class2": {"method3": {}, "method4": {}},
            }
        }

        analysis = analyzer.analyze_code_tree(tree)

        assert "depth" in analysis, "Condition must be true"
        assert "nodes" in analysis, "Condition must be true"
        assert "fractal_dimension" in analysis, "Condition must be true"
        assert analysis["nodes"] > 1, "Value must be greater than zero"


# =============================================================================
# FLUID DYNAMICS TESTS
# =============================================================================


class TestFluidChannel:
    """Test fluid channel physics."""

    def test_reynolds_number_laminar(self):
        """Test Reynolds number calculation for laminar flow."""
        channel = FluidChannel(
            channel_id="test", current_flow=10.0, viscosity=0.5, width=1.0, height=1.0
        )

        re = channel.reynolds_number()

        # Low flow / high viscosity = low Re (laminar)
        assert re < 2300, "Should be laminar flow"
        assert not channel.is_turbulent(), "Condition must be true"

    def test_reynolds_number_turbulent(self):
        """Test Reynolds number calculation for turbulent flow."""
        channel = FluidChannel(
            channel_id="test",
            current_flow=100000.0,  # Very high flow
            viscosity=0.001,  # Very low viscosity
            width=1.0,
            height=1.0,
        )

        re = channel.reynolds_number()

        # High flow / low viscosity = high Re (turbulent)
        assert re > 2300, "Should be turbulent flow"
        assert channel.is_turbulent(), "Condition must be true"

    def test_flow_regime(self):
        """Test flow regime determination."""
        channel = FluidChannel(channel_id="test", width=2.0, height=1.0)

        # Test laminar
        regime = channel.flow_regime(velocity=0.1, viscosity=1.0)
        assert regime == "laminar", "regime is not valid"

        # Test turbulent
        regime = channel.flow_regime(velocity=100.0, viscosity=0.0001)
        assert regime == "turbulent", "regime is not valid"


class TestFluidFlowScheduler:
    """Test fluid flow scheduler."""

    def test_scheduler_initialization(self):
        """Test scheduler initializes with channels."""
        scheduler = FluidFlowScheduler(num_channels=5)

        assert len(scheduler.channels) == 5, "Collection must not be empty"
        assert all(isinstance(ch, FluidChannel) for ch in scheduler.channels.values())

    def test_flow_injection(self):
        """Test flow injection into channels."""
        scheduler = FluidFlowScheduler(num_channels=3)

        channel_id = list(scheduler.channels.keys())[0]

        success = scheduler.inject_flow(channel_id, 50.0)

        assert success, "Should successfully inject flow"
        assert scheduler.channels[channel_id].current_flow == 50.0, "current_flow is not valid"

    def test_flow_injection_nonexistent_channel(self):
        """Test flow injection into non-existent channel."""
        scheduler = FluidFlowScheduler(num_channels=3)

        success = scheduler.inject_flow("nonexistent_channel", 50.0)

        assert not success, "Should fail for non-existent channel"

    def test_flow_injection_exceeds_capacity(self):
        """Test flow injection that exceeds capacity."""
        scheduler = FluidFlowScheduler(num_channels=1)

        channel_id = list(scheduler.channels.keys())[0]
        scheduler.channels[channel_id].capacity = 100.0

        # Fill to near capacity
        success1 = scheduler.inject_flow(channel_id, 90.0)
        assert success1, "success1 is not valid"

        # Try to exceed capacity
        success2 = scheduler.inject_flow(channel_id, 20.0)
        assert not success2, "Should not exceed capacity"


# =============================================================================
# ELECTROMAGNETIC FIELD TESTS
# =============================================================================


class TestEMFieldRouter:
    """Test electromagnetic field router."""

    def test_field_initialization(self):
        """Test EM field router initializes."""
        router = EMFieldRouter(grid_resolution=10)

        assert router.grid_resolution == 10, "grid_resolution is not valid"
        assert len(router.charges) == 0, "Collection must not be empty"

    def test_charge_addition(self):
        """Test adding charges updates field."""
        router = EMFieldRouter(grid_resolution=10)

        router.add_charge(np.array([0.5, 0.5]), charge=1.0)

        assert len(router.charges) == 1, "Collection must not be empty"
        assert router.potential_field is not None, "potential_field must be initialized"


# =============================================================================
# WAVE PROPAGATION TESTS
# =============================================================================


class TestWavePropagator:
    """Test wave propagation system."""

    def test_wave_initialization(self):
        """Test wave propagator initializes."""
        wave = WavePropagator(grid_size=30)

        assert wave.grid_size == 30, "grid_size is not valid"
        assert wave.field.shape == (30, 30)

    def test_source_addition(self):
        """Test adding wave sources."""
        wave = WavePropagator(grid_size=30)

        wave.add_source(position=(15, 15), amplitude=1.0, frequency=1.0)

        assert len(wave.sources) == 1, "Collection must not be empty"


# =============================================================================
# RELATIVISTIC EFFECTS TESTS
# =============================================================================


class TestRelativityScheduler:
    """Test relativistic scheduler."""

    def test_scheduler_initialization(self):
        """Test scheduler initializes."""
        scheduler = RelativityScheduler(speed_of_light=100.0)

        assert scheduler.c == 100.0, "c is not valid"
        assert len(scheduler.agents) == 0, "Collection must not be empty"

    def test_agent_addition(self):
        """Test adding agents."""
        scheduler = RelativityScheduler()

        scheduler.add_agent(
            agent_id="agent1",
            position=np.array([0.0, 0.0]),
            velocity=np.array([10.0, 0.0]),
        )

        assert "agent1" in scheduler.agents, "Condition must be true"
        assert scheduler.agents["agent1"]["clock_offset"] == 0.0, "Condition must be true"

    def test_lorentz_factor(self):
        """Test Lorentz factor calculation."""
        scheduler = RelativityScheduler(speed_of_light=100.0)

        # Low velocity: γ ≈ 1
        gamma_low = scheduler.lorentz_factor(np.array([10.0, 0.0]))
        assert 1.0 <= gamma_low <= 1.1, "Low velocity should give γ ≈ 1"

        # High velocity: γ > 1
        gamma_high = scheduler.lorentz_factor(np.array([90.0, 0.0]))
        assert gamma_high > 2.0, "High velocity should give γ >> 1"


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestAdvancedPhysicsOrchestrator:
    """Test unified orchestrator."""

    def test_orchestrator_initialization(self):
        """Test orchestrator initializes all components."""
        orchestrator = AdvancedPhysicsOrchestrator()

        assert orchestrator.chaos is not None, "chaos must be initialized"
        assert orchestrator.fractal is not None, "fractal must be initialized"
        assert orchestrator.fluid is not None, "fluid must be initialized"
        assert orchestrator.em_field is not None, "em_field must be initialized"
        assert orchestrator.wave is not None, "wave must be initialized"
        assert orchestrator.relativity is not None, "relativity must be initialized"

    def test_status_reporting(self):
        """Test status reporting."""
        orchestrator = AdvancedPhysicsOrchestrator()

        status = orchestrator.get_status()

        assert status["chaos"] == "active", "Condition must be true"
        assert status["fractal"] == "active", "Condition must be true"
        assert status["fluid"] == "active", "Condition must be true"
        assert status["em_field"] == "active", "Condition must be true"
        assert status["wave"] == "active", "Condition must be true"
        assert status["relativity"] == "active", "Condition must be true"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

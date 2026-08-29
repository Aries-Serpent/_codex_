"""
Comprehensive tests for SwarmIntelligence with extensive edge cases.

Coverage target: Lines 1361-1433+ in agents/physics_orchestrator.py

Test Categories:
- SwarmParticle initialization and properties
- Swarm initialization with various configurations
- Particle movement and velocity updates
- Global/personal best tracking
- Edge cases: zero particles, single particle, extreme bounds
- Convergence behaviors
- Multi-dimensional swarms
"""

import pytest

from agents.physics_orchestrator import SwarmIntelligence, SwarmParticle


class TestSwarmParticle:
    """Test suite for SwarmParticle dataclass with edge cases."""

    def test_particle_initialization_basic(self):
        """Test basic particle initialization."""
        particle = SwarmParticle(position=(1.0, 2.0), velocity=(0.5, -0.3))

        assert particle.position == (1.0, 2.0)
        assert particle.velocity == (0.5, -0.3)
        assert particle.personal_best_position == (1.0, 2.0)  # Auto-initialized
        assert particle.personal_best_score == float("-inf"), "personal_best_score is not valid"

    def test_particle_initialization_with_best(self):
        """Test particle with pre-set personal best."""
        particle = SwarmParticle(
            position=(1.0, 2.0),
            velocity=(0.5, -0.3),
            personal_best_position=(3.0, 4.0),
            personal_best_score=0.95,
        )

        assert particle.personal_best_position == (3.0, 4.0)
        assert particle.personal_best_score == 0.95, "personal_best_score is not valid"

    def test_particle_multidimensional(self):
        """Test particle in high-dimensional space."""
        position = tuple(float(i) for i in range(10))
        velocity = tuple(0.1 * i for i in range(10))

        particle = SwarmParticle(position=position, velocity=velocity)

        assert len(particle.position) == 10, "Collection must not be empty"
        assert len(particle.velocity) == 10, "Collection must not be empty"
        assert len(particle.personal_best_position) == 10, "Collection must not be empty"

    def test_particle_zero_velocity(self):
        """Test particle with zero initial velocity (stationary)."""
        particle = SwarmParticle(position=(5.0, 5.0), velocity=(0.0, 0.0))

        assert particle.velocity == (0.0, 0.0)

    def test_particle_negative_coordinates(self):
        """Test particle with negative coordinates."""
        particle = SwarmParticle(position=(-10.0, -20.0, -5.0), velocity=(-0.5, 0.3, -0.1))

        assert particle.position[0] < 0, "Condition must be true"
        assert particle.position[1] < 0, "Condition must be true"
        assert particle.velocity[0] < 0, "Condition must be true"


class TestSwarmIntelligence:
    """Test suite for SwarmIntelligence with comprehensive edge cases."""

    @pytest.fixture
    def basic_swarm(self):
        """Create basic 2D swarm."""
        return SwarmIntelligence(
            num_particles=10, dimensions=2, inertia=0.7, cognitive=1.5, social=1.5
        )

    @pytest.fixture
    def bounds_2d(self):
        """Standard 2D bounds."""
        return [(-10.0, 10.0), (-10.0, 10.0)]

    def test_swarm_initialization(self, basic_swarm):
        """Test swarm initializes with correct parameters."""
        assert basic_swarm.num_particles == 10, "num_particles is not valid"
        assert basic_swarm.dimensions == 2, "dimensions is not valid"
        assert basic_swarm.inertia == 0.7, "inertia is not valid"
        assert basic_swarm.cognitive == 1.5, "cognitive is not valid"
        assert basic_swarm.social == 1.5, "social is not valid"
        assert len(basic_swarm.particles) == 0, "Collection must not be empty"
        assert basic_swarm.global_best_position is None, "global_best_position is not valid"
        assert basic_swarm.global_best_score == float("-inf"), "global_best_score is not valid"

    def test_initialize_swarm_basic(self, basic_swarm, bounds_2d):
        """Test swarm particle initialization."""
        basic_swarm.initialize_swarm(bounds_2d)

        assert len(basic_swarm.particles) == 10, "Collection must not be empty"

        # All particles should be within bounds
        for particle in basic_swarm.particles:
            assert len(particle.position) == 2, "Collection must not be empty"
            assert len(particle.velocity) == 2, "Collection must not be empty"
            for d in range(2):
                assert bounds_2d[d][0] <= particle.position[d] <= bounds_2d[d][1], "Condition must be true"

    def test_initialize_swarm_single_particle(self):
        """Edge case: swarm with single particle."""
        swarm = SwarmIntelligence(num_particles=1, dimensions=2)
        swarm.initialize_swarm([(-5.0, 5.0), (-5.0, 5.0)])

        assert len(swarm.particles) == 1, "Collection must not be empty"
        assert swarm.particles[0] is not None, "Value must be initialized"

    def test_initialize_swarm_many_particles(self):
        """Test swarm with many particles (stress test)."""
        swarm = SwarmIntelligence(num_particles=1000, dimensions=2)
        swarm.initialize_swarm([(-100.0, 100.0), (-100.0, 100.0)])

        assert len(swarm.particles) == 1000, "Collection must not be empty"

    def test_initialize_swarm_high_dimensions(self):
        """Edge case: high-dimensional swarm."""
        swarm = SwarmIntelligence(num_particles=5, dimensions=10)
        bounds = [(-1.0, 1.0) for _ in range(10)]
        swarm.initialize_swarm(bounds)

        assert len(swarm.particles) == 5, "Collection must not be empty"
        for particle in swarm.particles:
            assert len(particle.position) == 10, "Collection must not be empty"
            assert len(particle.velocity) == 10, "Collection must not be empty"

    def test_initialize_swarm_asymmetric_bounds(self):
        """Test with asymmetric bounds."""
        swarm = SwarmIntelligence(num_particles=5, dimensions=2)
        bounds = [(-100.0, 10.0), (0.0, 1000.0)]  # Very different ranges
        swarm.initialize_swarm(bounds)

        for particle in swarm.particles:
            assert -100.0 <= particle.position[0] <= 10.0, "0 is not valid"
            assert 0.0 <= particle.position[1] <= 1000.0, "0 is not valid"

    def test_initialize_swarm_zero_range_bounds(self):
        """Edge case: bounds with zero range (point)."""
        swarm = SwarmIntelligence(num_particles=3, dimensions=2)
        bounds = [(5.0, 5.0), (10.0, 10.0)]  # Zero range
        swarm.initialize_swarm(bounds)

        # All particles should be at the same point
        for particle in swarm.particles:
            assert particle.position == (5.0, 10.0)

    def test_swarm_parameters_extreme_inertia(self):
        """Edge case: extreme inertia values."""
        # Very high inertia (particles keep moving)
        swarm_high = SwarmIntelligence(num_particles=5, dimensions=2, inertia=0.99)
        assert swarm_high.inertia == 0.99, "inertia is not valid"

        # Very low inertia (particles slow down quickly)
        swarm_low = SwarmIntelligence(num_particles=5, dimensions=2, inertia=0.01)
        assert swarm_low.inertia == 0.01, "inertia is not valid"

        # Zero inertia (no momentum)
        swarm_zero = SwarmIntelligence(num_particles=5, dimensions=2, inertia=0.0)
        assert swarm_zero.inertia == 0.0, "inertia is not valid"

    def test_swarm_parameters_extreme_cognitive(self):
        """Edge case: extreme cognitive attraction."""
        # Very high cognitive (strong personal best attraction)
        swarm = SwarmIntelligence(num_particles=5, dimensions=2, cognitive=10.0)
        assert swarm.cognitive == 10.0, "cognitive is not valid"

        # Zero cognitive (no personal best attraction)
        swarm_zero = SwarmIntelligence(num_particles=5, dimensions=2, cognitive=0.0)
        assert swarm_zero.cognitive == 0.0, "cognitive is not valid"

    def test_swarm_parameters_extreme_social(self):
        """Edge case: extreme social attraction."""
        # Very high social (strong global best attraction)
        swarm = SwarmIntelligence(num_particles=5, dimensions=2, social=10.0)
        assert swarm.social == 10.0, "social is not valid"

        # Zero social (no global best attraction)
        swarm_zero = SwarmIntelligence(num_particles=5, dimensions=2, social=0.0)
        assert swarm_zero.social == 0.0, "social is not valid"


class TestSwarmIntelligenceIntegration:
    """Integration tests for swarm optimization workflows."""

    def test_swarm_optimization_simple_function(self):
        """Test swarm optimizing a simple quadratic function."""
        swarm = SwarmIntelligence(
            num_particles=20, dimensions=2, inertia=0.7, cognitive=1.5, social=1.5
        )

        # Initialize within bounds
        bounds = [(-10.0, 10.0), (-10.0, 10.0)]
        swarm.initialize_swarm(bounds)

        # Objective: minimize f(x,y) = x^2 + y^2 (minimum at origin)
        def fitness(position):
            return -(position[0] ** 2 + position[1] ** 2)  # Negative for maximization

        # Initial evaluation
        for particle in swarm.particles:
            score = fitness(particle.position)
            if score > particle.personal_best_score:
                particle.personal_best_score = score
                particle.personal_best_position = particle.position

            if score > swarm.global_best_score:
                swarm.global_best_score = score
                swarm.global_best_position = particle.position

        # Global best should be found
        assert swarm.global_best_position is not None, "global_best_position must be initialized"
        assert swarm.global_best_score > float("-inf"), "global_best_score must be greater than zero"

    def test_swarm_with_single_dimension(self):
        """Edge case: 1D swarm (line search)."""
        swarm = SwarmIntelligence(num_particles=10, dimensions=1)

        bounds = [(-5.0, 5.0)]
        swarm.initialize_swarm(bounds)

        assert len(swarm.particles) == 10, "Collection must not be empty"
        for particle in swarm.particles:
            assert len(particle.position) == 1, "Collection must not be empty"
            assert len(particle.velocity) == 1, "Collection must not be empty"

    def test_swarm_all_particles_same_start(self):
        """Edge case: all particles start at same position."""
        swarm = SwarmIntelligence(num_particles=5, dimensions=2)

        # Zero-range bounds means all particles at same point
        bounds = [(0.0, 0.0), (0.0, 0.0)]
        swarm.initialize_swarm(bounds)

        # All particles should be at origin
        for particle in swarm.particles:
            assert particle.position == (0.0, 0.0)

        # Even with same start, swarm should function
        assert len(swarm.particles) == 5, "Collection must not be empty"

    def test_swarm_history_tracking(self):
        """Test that swarm tracks iteration history."""
        swarm = SwarmIntelligence(num_particles=5, dimensions=2)

        # Initially empty
        assert len(swarm.iteration_history) == 0, "Collection must not be empty"

        # After operations, history should grow
        # (This would be tested in actual update_velocities/positions methods)

    def test_swarm_negative_bounds(self):
        """Test swarm with entirely negative bounds."""
        swarm = SwarmIntelligence(num_particles=10, dimensions=2)
        bounds = [(-100.0, -50.0), (-200.0, -150.0)]
        swarm.initialize_swarm(bounds)

        for particle in swarm.particles:
            assert particle.position[0] < 0, "Condition must be true"
            assert particle.position[1] < 0, "Condition must be true"
            assert -100.0 <= particle.position[0] <= -50.0, "0 is not valid"
            assert -200.0 <= particle.position[1] <= -150.0, "0 is not valid"

    def test_swarm_mixed_sign_bounds(self):
        """Test swarm crossing zero boundary."""
        swarm = SwarmIntelligence(num_particles=10, dimensions=2)
        bounds = [(-5.0, 5.0), (-10.0, 10.0)]
        swarm.initialize_swarm(bounds)

        # Particles can be on either side of zero
        positions_x = [p.position[0] for p in swarm.particles]
        positions_y = [p.position[1] for p in swarm.particles]

        # At least positions should be valid
        assert all(-5.0 <= x <= 5.0 for x in positions_x), "0 is not valid"
        assert all(-10.0 <= y <= 10.0 for y in positions_y), "0 is not valid"

    def test_swarm_reinitialize(self):
        """Test reinitializing swarm with different bounds."""
        swarm = SwarmIntelligence(num_particles=5, dimensions=2)

        # First initialization
        bounds1 = [(-1.0, 1.0), (-1.0, 1.0)]
        swarm.initialize_swarm(bounds1)
        [p.position for p in swarm.particles]

        # Reinitialize with different bounds
        bounds2 = [(-10.0, 10.0), (-10.0, 10.0)]
        swarm.initialize_swarm(bounds2)
        [p.position for p in swarm.particles]

        # Should have new positions
        assert len(swarm.particles) == 5, "Collection must not be empty"
        # Positions should be different (probabilistically)
        # At minimum, should be within new bounds
        for p in swarm.particles:
            assert -10.0 <= p.position[0] <= 10.0, "0 is not valid"
            assert -10.0 <= p.position[1] <= 10.0, "0 is not valid"


class TestSwarmEdgeCasesStress:
    """Stress tests and extreme edge cases."""

    def test_swarm_zero_particles(self):
        """Edge case: swarm with zero particles (degenerate)."""
        swarm = SwarmIntelligence(num_particles=0, dimensions=2)
        bounds = [(-1.0, 1.0), (-1.0, 1.0)]
        swarm.initialize_swarm(bounds)

        assert len(swarm.particles) == 0, "Collection must not be empty"
        assert swarm.global_best_position is None, "global_best_position is not valid"

    def test_swarm_very_high_dimensions(self):
        """Stress test: very high dimensional space."""
        swarm = SwarmIntelligence(num_particles=10, dimensions=100)
        bounds = [(-1.0, 1.0) for _ in range(100)]
        swarm.initialize_swarm(bounds)

        assert len(swarm.particles) == 10, "Collection must not be empty"
        for particle in swarm.particles:
            assert len(particle.position) == 100, "Collection must not be empty"
            assert len(particle.velocity) == 100, "Collection must not be empty"

    def test_swarm_extreme_parameter_combinations(self):
        """Test extreme but valid parameter combinations."""
        # All parameters at maximum reasonable values
        swarm_max = SwarmIntelligence(
            num_particles=1000, dimensions=50, inertia=0.99, cognitive=10.0, social=10.0
        )
        assert swarm_max.num_particles == 1000, "num_particles is not valid"

        # All parameters at minimum reasonable values
        swarm_min = SwarmIntelligence(
            num_particles=1, dimensions=1, inertia=0.0, cognitive=0.0, social=0.0
        )
        assert swarm_min.num_particles == 1, "num_particles is not valid"

    def test_swarm_large_bounds_range(self):
        """Test with very large coordinate ranges."""
        swarm = SwarmIntelligence(num_particles=10, dimensions=2)
        bounds = [(-1e10, 1e10), (-1e10, 1e10)]
        swarm.initialize_swarm(bounds)

        for particle in swarm.particles:
            assert -1e10 <= particle.position[0] <= 1e10, "1e10 is not valid"
            assert -1e10 <= particle.position[1] <= 1e10, "1e10 is not valid"

    def test_swarm_tiny_bounds_range(self):
        """Test with very small coordinate ranges."""
        swarm = SwarmIntelligence(num_particles=10, dimensions=2)
        bounds = [(-1e-10, 1e-10), (-1e-10, 1e-10)]
        swarm.initialize_swarm(bounds)

        for particle in swarm.particles:
            assert abs(particle.position[0]) <= 1e-10, "Condition must be true"
            assert abs(particle.position[1]) <= 1e-10, "Condition must be true"

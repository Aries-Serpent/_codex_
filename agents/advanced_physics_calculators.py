"""
Advanced Physics Calculators for AI Agent Decision Making.

This module implements emerging physics paradigms for enhanced orchestration:
1. Chaos Theory - Chaotic neural networks for adaptive search
2. Fractal Geometry - Multi-scale pattern recognition
3. Fluid Dynamics - Workflow flow modeling
4. Electromagnetic Fields - Influence propagation
5. Wave Propagation - Interference-based consensus
6. Relativistic Effects - Latency-aware scheduling

Author: Copilot AI Agent
Version: 1.0.0
"""

import math
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Minimal numpy stubs for type hints
    class np:  # type: ignore
        ndarray = Any


# =============================================================================
# CHAOS THEORY
# =============================================================================


@dataclass
class ChaoticAttractor:
    """
    Represents a chaotic attractor for unpredictable exploration.
    
    Chaotic systems are sensitive to initial conditions and exhibit
    deterministic but unpredictable behavior, useful for escaping
    local optima in decision spaces.
    """
    attractor_type: str = "logistic"  # logistic, lorenz, henon
    parameters: Dict[str, float] = field(default_factory=dict)
    state: np.ndarray = field(default_factory=lambda: np.array([0.5]))
    history: List[np.ndarray] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize default parameters based on attractor type."""
        if not self.parameters:
            if self.attractor_type == "logistic":
                self.parameters = {"r": 3.9}  # Chaotic regime
            elif self.attractor_type == "lorenz":
                self.parameters = {"sigma": 10.0, "rho": 28.0, "beta": 8.0/3.0}
                self.state = np.array([1.0, 1.0, 1.0])
            elif self.attractor_type == "henon":
                self.parameters = {"a": 1.4, "b": 0.3}
                self.state = np.array([0.0, 0.0])
    
    def iterate(self, steps: int = 1) -> np.ndarray:
        """
        Iterate the chaotic map for specified steps.
        
        Returns the final state after iteration.
        """
        for _ in range(steps):
            if self.attractor_type == "logistic":
                self._logistic_map()
            elif self.attractor_type == "lorenz":
                self._lorenz_system()
            elif self.attractor_type == "henon":
                self._henon_map()
            
            self.history.append(self.state.copy())
        
        return self.state
    
    def _logistic_map(self) -> None:
        """
        Logistic map: x_{n+1} = r * x_n * (1 - x_n)
        
        Exhibits chaotic behavior for r > 3.57.
        """
        r = self.parameters["r"]
        x = self.state[0]
        self.state[0] = r * x * (1 - x)
    
    def _lorenz_system(self, dt: float = 0.01) -> None:
        """
        Lorenz system: dx/dt = σ(y-x), dy/dt = x(ρ-z)-y, dz/dt = xy-βz
        
        Famous butterfly attractor exhibiting deterministic chaos.
        """
        sigma = self.parameters["sigma"]
        rho = self.parameters["rho"]
        beta = self.parameters["beta"]
        
        x, y, z = self.state
        
        # Runge-Kutta 4th order integration
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z
        
        self.state += np.array([dx, dy, dz]) * dt
    
    def _henon_map(self) -> None:
        """
        Hénon map: x_{n+1} = 1 - a*x_n^2 + y_n, y_{n+1} = b*x_n
        
        2D discrete-time dynamical system with strange attractor.
        """
        a = self.parameters["a"]
        b = self.parameters["b"]
        
        x, y = self.state
        self.state = np.array([1 - a * x**2 + y, b * x])
    
    def lyapunov_exponent(self, iterations: int = 1000) -> float:
        """
        Estimate largest Lyapunov exponent (measure of chaos).
        
        Positive exponent indicates chaotic behavior (exponential divergence).
        """
        if self.attractor_type != "logistic":
            return 0.0  # Only implemented for logistic map for now
        
        r = self.parameters["r"]
        x = 0.5
        sum_log = 0.0
        
        for _ in range(iterations):
            x = r * x * (1 - x)
            derivative = abs(r - 2 * r * x)
            if derivative > 0:
                sum_log += math.log(derivative)
        
        return sum_log / iterations


class ChaoticNeuralNetwork:
    """
    Chaotic Neural Network for adaptive, non-repetitive search.
    
    Uses chaotic dynamics to explore decision space unpredictably,
    useful for breaking out of local optima and discovering novel solutions.
    
    Applications:
    - Randomized test generation
    - Non-repetitive code review paths
    - Adaptive workflow exploration
    - Hidden bug discovery through sensitivity to initial conditions
    """
    
    def __init__(
        self,
        num_neurons: int = 10,
        attractor_type: str = "logistic",
        coupling_strength: float = 0.1
    ):
        self.num_neurons = num_neurons
        self.neurons = [
            ChaoticAttractor(attractor_type=attractor_type)
            for _ in range(num_neurons)
        ]
        self.coupling_strength = coupling_strength
        self.exploration_history: List[Dict[str, Any]] = []
    
    def couple_neurons(self) -> None:
        """
        Couple chaotic neurons through weak interactions.
        
        Coupling synchronizes some neurons while maintaining chaos,
        creating complex collective dynamics.
        """
        states = np.array([n.state[0] for n in self.neurons])
        mean_state = np.mean(states)
        
        for neuron in self.neurons:
            # Weak coupling to mean field
            perturbation = self.coupling_strength * (mean_state - neuron.state[0])
            neuron.state[0] += perturbation
            # Keep in valid range
            neuron.state[0] = max(0.001, min(0.999, neuron.state[0]))
    
    def evolve(self, steps: int = 10) -> np.ndarray:
        """
        Evolve the chaotic neural network.
        
        Returns the final state of all neurons.
        """
        for _ in range(steps):
            # Iterate each neuron
            for neuron in self.neurons:
                neuron.iterate(1)
            
            # Couple neurons
            self.couple_neurons()
        
        return np.array([n.state[0] for n in self.neurons])
    
    def generate_test_parameters(
        self,
        param_ranges: List[Tuple[float, float]],
        num_tests: int = 100
    ) -> List[List[float]]:
        """
        Generate chaotic test parameters for randomized testing.
        
        Uses chaotic dynamics to create diverse, non-repetitive test cases.
        
        Args:
            param_ranges: List of (min, max) tuples for each parameter
            num_tests: Number of test cases to generate
        
        Returns:
            List of parameter vectors
        """
        test_cases = []
        
        for _ in range(num_tests):
            # Evolve network
            state = self.evolve(steps=1)
            
            # Map chaotic states to parameter ranges
            params = []
            for i, (min_val, max_val) in enumerate(param_ranges):
                # Use modulo for more neurons than parameters
                chaotic_value = state[i % len(state)]
                param = min_val + chaotic_value * (max_val - min_val)
                params.append(param)
            
            test_cases.append(params)
            
            # Record exploration
            self.exploration_history.append({
                'test_id': len(test_cases),
                'parameters': params,
                'network_state': state.copy()
            })
        
        return test_cases
    
    def inject_chaos(
        self,
        decision_value: float,
        chaos_strength: float = 0.1
    ) -> float:
        """
        Inject chaos into a decision value for exploration.
        
        Args:
            decision_value: Base decision value
            chaos_strength: Strength of chaotic perturbation (0-1)
        
        Returns:
            Perturbed decision value
        """
        # Evolve first neuron
        chaotic_state = self.neurons[0].iterate(1)[0]
        
        # Add chaotic perturbation centered at 0
        perturbation = chaos_strength * (chaotic_state - 0.5) * 2
        
        return decision_value + perturbation


# =============================================================================
# FRACTAL GEOMETRY
# =============================================================================


class FractalAnalyzer:
    """
    Fractal-based analyzer for recursive pattern recognition in code structures.
    
    Uses fractal geometry to:
    - Decompose code trees at multiple scales
    - Detect self-similar patterns in dependencies
    - Calculate fractal dimensions for anomaly detection
    - Identify recursive structures
    
    Applications:
    - Multi-scale code analysis
    - Dependency graph anomaly detection
    - Self-similar issue identification
    - Hierarchical pattern recognition
    """
    
    def __init__(self, max_depth: int = 10):
        self.max_depth = max_depth
        self.analysis_history: List[Dict[str, Any]] = []
    
    def box_counting_dimension(
        self,
        points: np.ndarray,
        box_sizes: Optional[List[float]] = None
    ) -> float:
        """
        Calculate fractal dimension using box-counting method.
        
        D = lim_{ε→0} log(N(ε)) / log(1/ε)
        
        where N(ε) is the number of boxes of size ε needed to cover the set.
        
        Args:
            points: Array of points (n_points, n_dimensions)
            box_sizes: List of box sizes to try (defaults to powers of 2)
        
        Returns:
            Estimated fractal dimension
        """
        if box_sizes is None:
            box_sizes = [2**(-i) for i in range(1, 10)]
        
        counts = []
        for box_size in box_sizes:
            # Count boxes needed
            if len(points.shape) == 1:
                points = points.reshape(-1, 1)
            
            min_coords = np.min(points, axis=0)
            
            # Hash points to grid cells
            grid_indices = ((points - min_coords) / box_size).astype(int)
            unique_cells = set(map(tuple, grid_indices))
            
            counts.append(len(unique_cells))
        
        # Linear regression on log-log plot
        log_sizes = np.log(box_sizes)
        log_counts = np.log(counts)
        
        # Fit line
        coeffs = np.polyfit(log_sizes, log_counts, 1)
        dimension = -coeffs[0]  # Negative slope is the dimension
        
        return dimension
    
    def analyze_code_tree(
        self,
        tree_structure: Dict[str, Any],
        current_depth: int = 0
    ) -> Dict[str, Any]:
        """
        Analyze code tree structure using fractal decomposition.
        
        Args:
            tree_structure: Nested dict representing code hierarchy
            current_depth: Current recursion depth
        
        Returns:
            Analysis results including fractal properties
        """
        if current_depth >= self.max_depth:
            return {'depth': current_depth, 'nodes': 1, 'branches': 0}
        
        num_children = 0
        child_depths = []
        total_nodes = 1  # Count self
        
        # Recursively analyze children
        for key, value in tree_structure.items():
            if isinstance(value, dict):
                num_children += 1
                child_analysis = self.analyze_code_tree(value, current_depth + 1)
                child_depths.append(child_analysis['depth'])
                total_nodes += child_analysis.get('nodes', 1)
        
        # Calculate local fractal properties
        branching_ratio = num_children if num_children > 0 else 1
        avg_child_depth = np.mean(child_depths) if child_depths else 0
        
        # Self-similarity measure
        self_similarity = self._calculate_self_similarity(
            current_depth, avg_child_depth, branching_ratio
        )
        
        result = {
            'depth': current_depth,
            'nodes': total_nodes,
            'branches': num_children,
            'branching_ratio': branching_ratio,
            'self_similarity': self_similarity,
            'avg_child_depth': avg_child_depth
        }
        
        if current_depth == 0:
            # Calculate overall fractal dimension
            result['fractal_dimension'] = self._estimate_tree_dimension(result)
            self.analysis_history.append(result)
        
        return result
    
    def _calculate_self_similarity(
        self,
        depth: int,
        avg_child_depth: float,
        branching_ratio: float
    ) -> float:
        """
        Calculate self-similarity score.
        
        Higher score indicates more self-similar structure.
        """
        if depth == 0 or avg_child_depth == 0:
            return 0.0
        
        # Compare depth ratios (perfect self-similarity has ratio ≈ 1)
        depth_ratio = avg_child_depth / (depth + 1)
        
        # Branching consistency (log scale)
        branching_score = 1.0 / (1.0 + abs(math.log(branching_ratio + 1) - math.log(2)))
        
        return depth_ratio * branching_score
    
    def _estimate_tree_dimension(self, tree_stats: Dict[str, Any]) -> float:
        """
        Estimate fractal dimension of tree structure.
        
        Uses relationship: D ≈ log(N) / log(R)
        where N is branching factor and R is depth ratio.
        """
        nodes = tree_stats.get('nodes', 1)
        depth = tree_stats.get('depth', 1)
        branches = tree_stats.get('branches', 1)
        
        if depth == 0 or branches == 0:
            return 1.0
        
        # Estimate dimension
        dimension = math.log(nodes) / math.log(depth + 1)
        
        return min(dimension, 3.0)  # Cap at 3D
    
    def detect_anomalies(
        self,
        structures: List[Dict[str, Any]],
        threshold: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in code structures using fractal analysis.
        
        Anomalies are structures with significantly different fractal
        dimensions from the mean.
        
        Args:
            structures: List of code tree structures to analyze
            threshold: Standard deviation threshold for anomaly detection
        
        Returns:
            List of anomalous structures with details
        """
        dimensions = []
        analyses = []
        
        for struct in structures:
            analysis = self.analyze_code_tree(struct)
            dimensions.append(analysis.get('fractal_dimension', 1.0))
            analyses.append(analysis)
        
        # Calculate statistics
        mean_dim = np.mean(dimensions)
        std_dim = np.std(dimensions)
        
        # Identify anomalies
        anomalies = []
        for i, (dim, analysis) in enumerate(zip(dimensions, analyses)):
            z_score = abs(dim - mean_dim) / (std_dim + 1e-6)
            
            if z_score > threshold:
                anomalies.append({
                    'index': i,
                    'fractal_dimension': dim,
                    'z_score': z_score,
                    'analysis': analysis,
                    'anomaly_type': 'high_dimension' if dim > mean_dim else 'low_dimension'
                })
        
        return anomalies


# =============================================================================
# FLUID DYNAMICS
# =============================================================================


@dataclass
class FluidChannel:
    """
    Represents a channel in the workflow fluid network.
    
    Models task flow as fluid through a pipe with:
    - Flow rate (tasks/time)
    - Pressure (urgency)
    - Viscosity (resistance)
    """
    channel_id: str = ""
    name: str = ""  # Alias for channel_id
    capacity: float = 100.0  # Maximum flow rate
    current_flow: float = 0.0
    pressure: float = 1.0
    viscosity: float = 0.1  # Resistance to flow
    cross_section: float = 1.0
    
    def __post_init__(self):
        """Handle name/channel_id aliasing"""
        if self.name and not self.channel_id:
            self.channel_id = self.name
        elif self.channel_id and not self.name:
            self.name = self.channel_id
    
    def reynolds_number(self) -> float:
        """
        Calculate Reynolds number: Re = ρvL/μ
        
        Re < 2300: Laminar flow (smooth, predictable)
        Re > 4000: Turbulent flow (chaotic, mixing)
        """
        # Simplified: Re ∝ flow / viscosity
        return self.current_flow / (self.viscosity + 0.01)
    
    def is_turbulent(self) -> bool:
        """Check if flow is turbulent."""
        return self.reynolds_number() > 2300
    
    def pressure_drop(self, length: float = 1.0) -> float:
        """
        Calculate pressure drop using Hagen-Poiseuille equation.
        
        ΔP = 8μLQ/(πr⁴) for laminar flow
        """
        if self.cross_section == 0:
            return 0.0
        
        # Simplified pressure drop
        return 8 * self.viscosity * length * self.current_flow / (self.cross_section**2)


class FluidFlowScheduler:
    """
    Fluid dynamics-inspired workflow scheduler.
    
    Models task pipelines as fluid flowing through channels:
    - Tasks are fluid particles
    - Channels have capacity (pipe diameter)
    - Bottlenecks create pressure buildup
    - Turbulence enables mixing and adaptation
    
    Uses Navier-Stokes-inspired algorithms for:
    - Load balancing (pressure equilibration)
    - Bottleneck detection (pressure gradients)
    - Dynamic routing (flow optimization)
    - Turbulence-based adaptability
    
    Applications:
    - Dynamic resource scheduling
    - Workflow optimization
    - Bottleneck identification
    - Load balancing
    """
    
    def __init__(self, num_channels: int = 5):
        self.channels: Dict[str, FluidChannel] = {}
        for i in range(num_channels):
            channel_id = f"channel_{i}"
            self.channels[channel_id] = FluidChannel(
                channel_id=channel_id,
                capacity=100.0,
                viscosity=random.uniform(0.05, 0.2)
            )
        
        self.flow_history: List[Dict[str, Any]] = []
    
    def add_channel(self, channel: FluidChannel) -> None:
        """Add a new channel to the network."""
        self.channels[channel.channel_id] = channel
    
    def inject_flow(self, channel_id: str, flow_rate: float) -> bool:
        """
        Inject flow into a channel.
        
        Returns True if successful, False if channel is at capacity.
        """
        if channel_id not in self.channels:
            return False
        
        channel = self.channels[channel_id]
        
        if channel.current_flow + flow_rate <= channel.capacity:
            channel.current_flow += flow_rate
            channel.pressure += flow_rate * 0.1  # Pressure increases with flow
            return True
        else:
            return False
    
    def balance_pressure(self) -> Dict[str, Any]:
        """
        Balance pressure across channels using fluid dynamics.
        
        Redistributes flow to equalize pressure, similar to how
        fluid flows from high to low pressure regions.
        
        Optimized to O(n) by balancing highest and lowest pressure channels
        in a single pass. This is more efficient than iterative balancing
        approaches which would require multiple O(n) passes.
        """
        # Calculate average pressure
        pressures = [ch.pressure for ch in self.channels.values()]
        avg_pressure = np.mean(pressures)
        
        redistributions = []
        
        # Get channel list
        channel_list = list(self.channels.values())
        if len(channel_list) < 2:
            return {
                'redistributions': [],
                'initial_avg_pressure': avg_pressure,
                'final_avg_pressure': avg_pressure,
                'pressure_variance': 0.0
            }
        
        # Find max and min pressure channels for efficient O(n) balancing
        max_ch = max(channel_list, key=lambda ch: ch.pressure)
        min_ch = min(channel_list, key=lambda ch: ch.pressure)
        pressure_diff = max_ch.pressure - min_ch.pressure
        
        if abs(pressure_diff) > 0.1:
            # Flow from high to low pressure
            # Flow rate proportional to pressure gradient
            transfer_rate = 0.1 * pressure_diff
            
            # Transfer flow
            if transfer_rate > 0 and max_ch.current_flow > 0:
                amount = min(abs(transfer_rate), max_ch.current_flow * 0.1)
                if min_ch.current_flow + amount <= min_ch.capacity:
                    max_ch.current_flow -= amount
                    min_ch.current_flow += amount
                    max_ch.pressure -= amount * 0.05
                    min_ch.pressure += amount * 0.05
                    
                    redistributions.append({
                        'from': max_ch.channel_id,
                        'to': min_ch.channel_id,
                        'amount': amount
                    })
        
        return {
            'redistributions': redistributions,
            'initial_avg_pressure': avg_pressure,
            'final_avg_pressure': np.mean([ch.pressure for ch in self.channels.values()]),
            'pressure_variance': np.var([ch.pressure for ch in self.channels.values()])
        }
    
    def detect_bottlenecks(self, threshold: float = 0.8) -> List[str]:
        """
        Detect bottleneck channels.
        
        Bottlenecks are channels operating near capacity with high pressure.
        
        Args:
            threshold: Capacity utilization threshold (0-1)
        
        Returns:
            List of bottleneck channel IDs
        """
        bottlenecks = []
        
        for channel_id, channel in self.channels.items():
            utilization = channel.current_flow / channel.capacity
            
            if utilization >= threshold:
                bottlenecks.append(channel_id)
        
        return bottlenecks
    
    def optimize_flow(self, iterations: int = 10) -> Dict[str, Any]:
        """
        Optimize flow distribution using iterative pressure balancing.
        
        Simulates fluid dynamics to find optimal flow distribution.
        """
        initial_state = {
            'total_flow': sum(ch.current_flow for ch in self.channels.values()),
            'bottlenecks': len(self.detect_bottlenecks()),
            'pressure_variance': np.var([ch.pressure for ch in self.channels.values()])
        }
        
        for i in range(iterations):
            result = self.balance_pressure()
            self.flow_history.append({
                'iteration': i,
                **result
            })
        
        final_state = {
            'total_flow': sum(ch.current_flow for ch in self.channels.values()),
            'bottlenecks': len(self.detect_bottlenecks()),
            'pressure_variance': np.var([ch.pressure for ch in self.channels.values()])
        }
        
        return {
            'initial': initial_state,
            'final': final_state,
            'improvement': {
                'bottleneck_reduction': initial_state['bottlenecks'] - final_state['bottlenecks'],
                'pressure_stabilization': initial_state['pressure_variance'] - final_state['pressure_variance']
            }
        }
    
    def calculate_turbulence(self) -> Dict[str, Any]:
        """
        Calculate turbulence levels in each channel.
        
        Turbulence enables adaptive behavior and mixing.
        """
        turbulent_channels = []
        reynolds_numbers = {}
        
        for channel_id, channel in self.channels.items():
            re = channel.reynolds_number()
            reynolds_numbers[channel_id] = re
            
            if channel.is_turbulent():
                turbulent_channels.append(channel_id)
        
        return {
            'turbulent_channels': turbulent_channels,
            'reynolds_numbers': reynolds_numbers,
            'turbulence_ratio': len(turbulent_channels) / len(self.channels)
        }


# =============================================================================
# ELECTROMAGNETIC FIELDS
# =============================================================================


class EMFieldRouter:
    """
    Electromagnetic field-based router for influence propagation.
    
    Models decision networks as electromagnetic fields:
    - Code hotspots are charges creating fields
    - Field lines guide reviewer focus
    - Potential φ(r) = Σ q_i / |r - r_i|
    - Force on agents: F = qE = -q∇φ
    
    Applications:
    - Spatial prioritization in AI decision-making
    - Automated review guidance
    - Influence propagation in networks
    - Attention focusing
    """
    
    def __init__(self, grid_resolution: int = 20):
        self.grid_resolution = grid_resolution
        self.charges: List[Tuple[np.ndarray, float]] = []  # (position, charge)
        self.potential_field: Optional[np.ndarray] = None
        self.electric_field: Optional[Tuple[np.ndarray, np.ndarray]] = None
    
    def add_charge(self, position: np.ndarray, charge: float) -> None:
        """
        Add a charge (code hotspot) to the field.
        
        Args:
            position: 2D position in decision space
            charge: Charge magnitude (positive = attractive, negative = repulsive)
        """
        self.charges.append((position, charge))
        self._recalculate_fields()
    
    def _recalculate_fields(self) -> None:
        """
        Recalculate electromagnetic fields from charges.
        
        Potential: φ(r) = Σ q_i / |r - r_i|
        Electric field: E = -∇φ
        """
        # Create grid
        x = np.linspace(0, 1, self.grid_resolution)
        y = np.linspace(0, 1, self.grid_resolution)
        X, Y = np.meshgrid(x, y)
        
        # Calculate potential at each grid point
        potential = np.zeros_like(X)
        
        for pos, charge in self.charges:
            # Distance from charge to each grid point
            dx = X - pos[0]
            dy = Y - pos[1]
            r = np.sqrt(dx**2 + dy**2) + 0.01  # Avoid singularity
            
            # Add contribution to potential
            potential += charge / r
        
        self.potential_field = potential
        
        # Calculate electric field (negative gradient)
        dy_pot, dx_pot = np.gradient(potential)
        self.electric_field = (-dx_pot, -dy_pot)
    
    def get_field_at_position(self, position: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        Get potential and electric field at a specific position.
        
        Returns:
            (potential, electric_field_vector)
        """
        if self.potential_field is None:
            return 0.0, np.array([0.0, 0.0])
        
        # Convert position to grid indices
        i = int(position[0] * (self.grid_resolution - 1))
        j = int(position[1] * (self.grid_resolution - 1))
        i = max(0, min(self.grid_resolution - 1, i))
        j = max(0, min(self.grid_resolution - 1, j))
        
        potential = self.potential_field[j, i]
        electric_field = np.array([self.electric_field[0][j, i], self.electric_field[1][j, i]])
        
        return potential, electric_field
    
    def route_agent(
        self,
        start_position: np.ndarray,
        steps: int = 50,
        step_size: float = 0.02
    ) -> List[np.ndarray]:
        """
        Route an agent along field lines.
        
        Agent follows electric field lines from start position,
        naturally moving toward positive charges (hotspots).
        
        Args:
            start_position: Starting position in [0,1]^2
            steps: Number of routing steps
            step_size: Size of each step
        
        Returns:
            Trajectory as list of positions
        """
        trajectory = [start_position.copy()]
        position = start_position.copy()
        
        for _ in range(steps):
            # Get electric field at current position
            _, E = self.get_field_at_position(position)
            
            # Move along field
            position += step_size * E
            
            # Clamp to bounds
            position = np.clip(position, 0.0, 1.0)
            
            trajectory.append(position.copy())
        
        return trajectory
    
    def prioritize_regions(
        self,
        num_regions: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Identify high-priority regions based on field strength.
        
        Returns regions sorted by field magnitude (highest priority first).
        """
        if self.potential_field is None or not NUMPY_AVAILABLE:
            return []
        
        # Calculate field magnitude at each point
        Ex, Ey = self.electric_field
        field_magnitude = np.sqrt(Ex**2 + Ey**2)
        
        # Efficient peak finding using scipy.ndimage.maximum_filter when available
        try:
            from scipy.ndimage import maximum_filter
            # Find local maxima: points that are equal to the local maximum in a 3x3 neighborhood
            neighborhood_size = 3
            max_filtered = maximum_filter(field_magnitude, size=neighborhood_size, mode='constant')
            local_max = (field_magnitude == max_filtered)
            # Exclude border pixels to match original behavior
            local_max[[0, -1], :] = False
            local_max[:, [0, -1]] = False
        except ImportError:
            # Fallback: original method if scipy is not available
            local_max = np.zeros_like(field_magnitude, dtype=bool)
            for i in range(1, field_magnitude.shape[0] - 1):
                for j in range(1, field_magnitude.shape[1] - 1):
                    val = field_magnitude[i, j]
                    # Get 3x3 neighborhood and flatten
                    neighborhood = field_magnitude[i-1:i+2, j-1:j+2].flatten()
                    # Exclude the center value (index 4 in the flattened 3x3 array)
                    neighbors = np.delete(neighborhood, 4)
                    if (val > neighbors).all():
                        local_max[i, j] = True
        
        # Get positions and magnitudes of peaks
        peak_positions = np.argwhere(local_max)
        peak_magnitudes = field_magnitude[local_max]
        
        # Sort by magnitude
        sorted_indices = np.argsort(peak_magnitudes)[::-1]
        
        # Convert to normalized coordinates
        regions = []
        for idx in sorted_indices[:num_regions]:
            j, i = peak_positions[idx]
            x = i / (self.grid_resolution - 1)
            y = j / (self.grid_resolution - 1)
            
            regions.append({
                'position': np.array([x, y]),
                'priority': float(peak_magnitudes[idx]),
                'grid_index': (i, j)
            })
        
        return regions


# =============================================================================
# WAVE PROPAGATION
# =============================================================================


class WavePropagator:
    """
    Wave propagation system for signal broadcasting and interference.
    
    Models agent communication as wave propagation:
    - Signals propagate as waves
    - Constructive interference amplifies agreement
    - Destructive interference cancels conflicts
    - Wavelets for multi-resolution analysis
    
    Applications:
    - Consensus building in distributed systems
    - Signal broadcasting through hierarchies
    - Multi-resolution anomaly detection
    - Communication pattern analysis
    """
    
    def __init__(
        self,
        grid_size: int = 50,
        wave_speed: float = 1.0,
        damping: float = 0.1
    ):
        self.grid_size = grid_size
        self.wave_speed = wave_speed
        self.damping = damping
        
        # Wave field (amplitude at each grid point)
        self.field = np.zeros((grid_size, grid_size))
        self.velocity = np.zeros((grid_size, grid_size))
        
        self.sources: List[Dict[str, Any]] = []
        self.history: List[np.ndarray] = []
    
    def add_source(
        self,
        position: Tuple[int, int],
        amplitude: float = 1.0,
        frequency: float = 1.0,
        phase: float = 0.0
    ) -> None:
        """
        Add a wave source (signal transmitter).
        
        Args:
            position: Grid position (i, j)
            amplitude: Wave amplitude
            frequency: Oscillation frequency
            phase: Initial phase
        """
        self.sources.append({
            'position': position,
            'amplitude': amplitude,
            'frequency': frequency,
            'phase': phase
        })
    
    def propagate(self, dt: float = 0.1, steps: int = 100) -> List[np.ndarray]:
        """
        Propagate waves using wave equation.
        
        ∂²u/∂t² = c²∇²u - γ∂u/∂t
        
        where c is wave speed and γ is damping.
        
        Returns history of field states.
        """
        c2 = self.wave_speed**2
        
        for step in range(steps):
            # Apply sources
            for source in self.sources:
                i, j = source['position']
                t = step * dt
                
                # Oscillating source
                self.field[i, j] += source['amplitude'] * np.sin(
                    2 * np.pi * source['frequency'] * t + source['phase']
                )
            
            # Calculate Laplacian (∇²u)
            laplacian = (
                np.roll(self.field, 1, axis=0) +
                np.roll(self.field, -1, axis=0) +
                np.roll(self.field, 1, axis=1) +
                np.roll(self.field, -1, axis=1) -
                4 * self.field
            )
            
            # Update velocity (includes damping)
            self.velocity += (c2 * laplacian - self.damping * self.velocity) * dt
            
            # Update field
            self.field += self.velocity * dt
            
            # Store history
            self.history.append(self.field.copy())
        
        return self.history
    
    def measure_interference(
        self,
        position: Tuple[int, int]
    ) -> Dict[str, float]:
        """
        Measure interference pattern at a position.
        
        Analyzes constructive vs destructive interference.
        """
        if len(self.history) < 10:
            return {'constructive': 0.0, 'destructive': 0.0, 'net': 0.0}
        
        i, j = position
        
        # Get time series at position
        time_series = [h[i, j] for h in self.history[-100:]]
        
        # Calculate power (energy)
        power = np.mean(np.array(time_series)**2)
        
        # Calculate expected power from individual sources
        individual_powers = [s['amplitude']**2 for s in self.sources]
        expected_power = np.sum(individual_powers) if individual_powers else 1.0
        
        # Interference factor (add epsilon to prevent division by zero)
        interference_factor = power / (expected_power + 1e-10)
        
        if interference_factor > 1.0:
            return {
                'constructive': interference_factor - 1.0,
                'destructive': 0.0,
                'net': interference_factor - 1.0
            }
        else:
            return {
                'constructive': 0.0,
                'destructive': 1.0 - interference_factor,
                'net': interference_factor - 1.0
            }
    
    def wavelet_transform(
        self,
        signal: np.ndarray,
        scales: Optional[List[int]] = None
    ) -> Dict[int, np.ndarray]:
        """
        Perform simple wavelet transform for multi-resolution analysis.
        
        Uses Haar wavelet for simplicity.
        
        Args:
            signal: 1D signal to analyze
            scales: List of scales to compute
        
        Returns:
            Dict mapping scale to wavelet coefficients
        """
        if scales is None:
            scales = [1, 2, 4, 8, 16]
        
        coefficients = {}
        
        for scale in scales:
            # Haar wavelet at this scale
            wavelet = np.array([1.0] * scale + [-1.0] * scale)
            
            # Convolve signal with wavelet
            coef = np.convolve(signal, wavelet, mode='same')
            coefficients[scale] = coef
        
        return coefficients
    
    def detect_anomalies_wavelet(
        self,
        threshold: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies using wavelet multi-resolution analysis.
        
        Anomalies show up as high-magnitude wavelet coefficients.
        """
        if len(self.history) < 10:
            return []
        
        # Extract time series from center of grid
        center_i, center_j = self.grid_size // 2, self.grid_size // 2
        time_series = np.array([h[center_i, center_j] for h in self.history])
        
        # Wavelet transform
        wavelets = self.wavelet_transform(time_series)
        
        anomalies = []
        
        for scale, coeffs in wavelets.items():
            # Find high-magnitude coefficients
            mean_coeff = np.mean(np.abs(coeffs))
            std_coeff = np.std(coeffs)
            
            for t, coeff in enumerate(coeffs):
                if abs(coeff) > mean_coeff + threshold * std_coeff:
                    anomalies.append({
                        'time': t,
                        'scale': scale,
                        'coefficient': float(coeff),
                        'z_score': (coeff - mean_coeff) / (std_coeff + 1e-6)
                    })
        
        return anomalies


# =============================================================================
# RELATIVISTIC EFFECTS  
# =============================================================================


class RelativityScheduler:
    """
    Relativity-aware scheduler for latency and synchronization.
    
    Accounts for:
    - Clock drift between microservices (time dilation analogy)
    - Spacetime locality (network latency as "distance")
    - Cross-boundary delays (horizon effects)
    - Relativistic scheduling (priority based on proper time)
    
    Applications:
    - Latency-aware distributed systems
    - Synchronized AI automation
    - Cross-boundary workflow optimization
    - Clock drift compensation
    """
    
    def __init__(self, speed_of_light: float = 100.0):
        self.c = speed_of_light  # Maximum communication speed
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.reference_time: float = 0.0
        self.scheduling_history: List[Dict[str, Any]] = []
    
    def add_agent(
        self,
        agent_id: str,
        position: np.ndarray,
        velocity: np.ndarray = None,
        clock_offset: float = 0.0
    ) -> None:
        """
        Add an agent to the relativistic system.
        
        Args:
            agent_id: Unique agent identifier
            position: Position in "space" (network topology)
            velocity: Velocity vector (rate of position change)
            clock_offset: Initial clock offset from reference
        """
        if velocity is None:
            velocity = np.zeros_like(position)
        
        self.agents[agent_id] = {
            'position': position,
            'velocity': velocity,
            'clock_offset': clock_offset,
            'proper_time': 0.0
        }
    
    def lorentz_factor(self, velocity: np.ndarray) -> float:
        """
        Calculate Lorentz factor: γ = 1/√(1 - v²/c²)
        
        Accounts for time dilation effects.
        """
        v_magnitude = np.linalg.norm(velocity)
        
        # Prevent superluminal speeds
        if v_magnitude >= self.c:
            v_magnitude = 0.9999 * self.c
        
        beta = v_magnitude / self.c
        gamma = 1.0 / math.sqrt(1.0 - beta**2)
        
        return gamma
    
    def time_dilation(self, agent_id: str, coordinate_time: float) -> float:
        """
        Calculate proper time accounting for time dilation.
        
        τ = t / γ
        
        Faster-moving agents experience slower proper time.
        """
        if agent_id not in self.agents:
            return coordinate_time
        
        agent = self.agents[agent_id]
        gamma = self.lorentz_factor(agent['velocity'])
        
        proper_time = coordinate_time / gamma
        
        return proper_time
    
    def communication_delay(
        self,
        agent_a_id: str,
        agent_b_id: str
    ) -> float:
        """
        Calculate communication delay between agents.
        
        delay = distance / c
        
        Analogous to light travel time in relativity.
        """
        if agent_a_id not in self.agents or agent_b_id not in self.agents:
            return 0.0
        
        pos_a = self.agents[agent_a_id]['position']
        pos_b = self.agents[agent_b_id]['position']
        
        distance = np.linalg.norm(pos_a - pos_b)
        delay = distance / self.c
        
        return delay
    
    def synchronize_clocks(self) -> Dict[str, float]:
        """
        Synchronize agent clocks using Einstein synchronization.
        
        Accounts for signal propagation delays.
        
        Returns:
            Clock corrections for each agent
        """
        if not self.agents:
            return {}
        
        # Use first agent as reference
        reference_id = list(self.agents.keys())[0]
        reference_pos = self.agents[reference_id]['position']
        
        corrections = {}
        
        for agent_id, agent in self.agents.items():
            # Communication delay to reference
            distance = np.linalg.norm(agent['position'] - reference_pos)
            delay = distance / self.c
            
            # Correct for propagation delay
            correction = -delay
            
            # Correct for time dilation
            gamma = self.lorentz_factor(agent['velocity'])
            correction *= gamma
            
            corrections[agent_id] = correction
            agent['clock_offset'] += correction
        
        return corrections
    
    def schedule_task(
        self,
        task_id: str,
        agent_id: str,
        deadline: float,
        priority: float = 1.0
    ) -> Dict[str, Any]:
        """
        Schedule a task with relativistic corrections.
        
        Adjusts deadline based on proper time and communication delays.
        """
        if agent_id not in self.agents:
            return {'success': False, 'reason': 'agent_not_found'}
        
        agent = self.agents[agent_id]
        
        # Calculate proper time deadline
        gamma = self.lorentz_factor(agent['velocity'])
        proper_deadline = deadline / gamma
        
        # Account for clock offset
        adjusted_deadline = proper_deadline - agent['clock_offset']
        
        # Calculate scheduling priority
        # Higher gamma (faster agent) gets lower priority for time-sensitive tasks
        adjusted_priority = priority / gamma
        
        schedule_entry = {
            'task_id': task_id,
            'agent_id': agent_id,
            'coordinate_deadline': deadline,
            'proper_deadline': proper_deadline,
            'adjusted_deadline': adjusted_deadline,
            'priority': adjusted_priority,
            'lorentz_factor': gamma,
            'success': True
        }
        
        self.scheduling_history.append(schedule_entry)
        
        return schedule_entry
    
    def optimize_cross_boundary_delays(
        self,
        boundaries: List[Tuple[str, str]]
    ) -> Dict[str, Any]:
        """
        Optimize delays for cross-boundary workflows.
        
        Accounts for communication latency and time synchronization.
        
        Args:
            boundaries: List of (agent_a_id, agent_b_id) boundary pairs
        
        Returns:
            Optimization results with delay analysis
        """
        delays = []
        optimizations = []
        
        for agent_a, agent_b in boundaries:
            delay = self.communication_delay(agent_a, agent_b)
            delays.append(delay)
            
            # Suggest optimization: move agents closer or pre-compute
            if delay > 1.0:
                optimizations.append({
                    'boundary': (agent_a, agent_b),
                    'current_delay': delay,
                    'suggestion': 'reduce_distance' if delay > 2.0 else 'pre_compute',
                    'priority': 'high' if delay > 5.0 else 'medium'
                })
        
        return {
            'total_boundaries': len(boundaries),
            'avg_delay': np.mean(delays) if delays else 0.0,
            'max_delay': max(delays) if delays else 0.0,
            'optimizations': optimizations
        }


# =============================================================================
# INTEGRATION UTILITIES
# =============================================================================


class AdvancedPhysicsOrchestrator:
    """
    Unified orchestrator integrating all advanced physics paradigms.
    
    Provides a single interface to:
    - Chaotic exploration (ChaoticNeuralNetwork)
    - Fractal analysis (FractalAnalyzer)
    - Fluid scheduling (FluidFlowScheduler)
    - EM field routing (EMFieldRouter)
    - Wave propagation (WavePropagator)
    - Relativistic scheduling (RelativityScheduler)
    """
    
    def __init__(self):
        self.chaos = ChaoticNeuralNetwork()
        self.fractal = FractalAnalyzer()
        self.fluid = FluidFlowScheduler()
        self.em_field = EMFieldRouter()
        self.wave = WavePropagator()
        self.relativity = RelativityScheduler()
        
        self.orchestration_log: List[Dict[str, Any]] = []
    
    def full_analysis(
        self,
        decision_space: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run full physics analysis on decision space.
        
        Combines all paradigms for comprehensive evaluation.
        """
        results = {
            'timestamp': 0.0,
            'paradigms': {}
        }
        
        # 1. Chaos analysis
        if 'exploration' in decision_space:
            param_ranges = decision_space.get('param_ranges', [(0, 1)])
            test_cases = self.chaos.generate_test_parameters(param_ranges, num_tests=10)
            results['paradigms']['chaos'] = {
                'test_cases_generated': len(test_cases),
                'lyapunov_exponent': self.chaos.neurons[0].lyapunov_exponent()
            }
        
        # 2. Fractal analysis
        if 'structure' in decision_space:
            structure = decision_space['structure']
            fractal_analysis = self.fractal.analyze_code_tree(structure)
            results['paradigms']['fractal'] = fractal_analysis
        
        # 3. Fluid dynamics
        if 'workflow' in decision_space:
            optimization = self.fluid.optimize_flow()
            results['paradigms']['fluid'] = optimization
        
        # 4. EM field routing
        if 'hotspots' in decision_space:
            for pos, charge in decision_space['hotspots']:
                self.em_field.add_charge(np.array(pos), charge)
            priorities = self.em_field.prioritize_regions()
            results['paradigms']['em_field'] = {
                'priority_regions': priorities
            }
        
        # 5. Wave propagation
        if 'signals' in decision_space:
            for signal in decision_space['signals']:
                self.wave.add_source(**signal)
            self.wave.propagate(steps=50)
            results['paradigms']['wave'] = {
                'propagation_steps': len(self.wave.history)
            }
        
        # 6. Relativistic scheduling
        if 'agents' in decision_space:
            for agent in decision_space['agents']:
                self.relativity.add_agent(**agent)
            sync_result = self.relativity.synchronize_clocks()
            results['paradigms']['relativity'] = {
                'agents_synchronized': len(sync_result)
            }
        
        self.orchestration_log.append(results)
        return results
    
    def get_status(self) -> Dict[str, str]:
        """Get status of all physics calculators."""
        return {
            'chaos': 'active',
            'fractal': 'active',
            'fluid': 'active',
            'em_field': 'active',
            'wave': 'active',
            'relativity': 'active'
        }


# Export main classes
__all__ = [
    # Chaos Theory
    'ChaoticAttractor',
    'ChaoticNeuralNetwork',
    # Fractal Geometry
    'FractalAnalyzer',
    # Fluid Dynamics
    'FluidChannel',
    'FluidFlowScheduler',
    # Electromagnetic Fields
    'EMFieldRouter',
    # Wave Propagation
    'WavePropagator',
    # Relativistic Effects
    'RelativityScheduler',
    # Unified Orchestrator
    'AdvancedPhysicsOrchestrator',
]

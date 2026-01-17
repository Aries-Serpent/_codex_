"""
Quantum-Inspired Game Theory for AI Agent Decision Making

This module implements a physics-inspired game theory framework combining:
1. Classical energy-based game logic (statistical physics approach)
2. Quantum-inspired extension (wavefunctions, operators, superposition, entanglement)

The framework models Blue Team (defense) vs Red Team (attack) scenarios using
Hilbert space representations and quantum operators for deterministic hypothesis
evaluation with probabilistic outcomes.

Core Concepts:
- Strategy spaces mapped to Hilbert spaces
- Payoffs represented as Hermitian operators
- Mixed strategies as wavefunctions
- Quantum unitaries for strategy updates
- Decoherence for modeling noise/uncertainty

References:
- Quantum game theory: Eisert, Wilkens, Lewenstein (1999)
- Energy-based game theory: Statistical mechanics approach to Nash equilibria
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Union

# Initialize logger before use in exception handlers
logger = logging.getLogger(__name__)

# Optional numpy import with graceful fallback
try:
    import numpy as np

    NUMPY_AVAILABLE = True
except ImportError as e:
    logger.debug(f"ImportError: {e}")
    logger.warning(f"ImportError: {e}", exc_info=True)
    # Provide minimal numpy-like interface for type hints
    NUMPY_AVAILABLE = False

    class _NumpyStub:
        """Minimal numpy stub for when numpy is not available."""

        ndarray = list  # Type hint fallback

        @staticmethod
        def ones(n, dtype=None):
            """Stub for np.ones"""
            raise ImportError(
                "numpy is required for quantum game theory. Install with: pip install numpy"
            )

        @staticmethod
        def sqrt(x):
            """Stub for np.sqrt"""
            raise ImportError(
                "numpy is required for quantum game theory. Install with: pip install numpy"
            )

        @staticmethod
        def zeros(shape, dtype=None):
            """Stub for np.zeros"""
            raise ImportError(
                "numpy is required for quantum game theory. Install with: pip install numpy"
            )

        @staticmethod
        def exp(x):
            """Stub for np.exp"""
            raise ImportError(
                "numpy is required for quantum game theory. Install with: pip install numpy"
            )

        @staticmethod
        def dot(a, b):
            """Stub for np.dot"""
            raise ImportError(
                "numpy is required for quantum game theory. Install with: pip install numpy"
            )

        @staticmethod
        def conj(x):
            """Stub for np.conj"""
            raise ImportError(
                "numpy is required for quantum game theory. Install with: pip install numpy"
            )

        @staticmethod
        def real(x):
            """Stub for np.real"""
            raise ImportError(
                "numpy is required for quantum game theory. Install with: pip install numpy"
            )

    np = _NumpyStub()

logger = logging.getLogger(__name__)

__all__ = [
    "TeamType",
    "StrategyState",
    "PayoffOperator",
    "QuantumGameState",
    "ClassicalGameEngine",
    "QuantumInspiredGameEngine",
    "BlueRedTeamSimulator",
    "NUMPY_AVAILABLE",
]


class TeamType(Enum):
    """Team identifiers for game theory scenarios"""

    BLUE = "blue"  # Defense team
    RED = "red"  # Attack team
    NEUTRAL = "neutral"


@dataclass
class StrategyState:
    """Represents a strategy configuration for a team.

    Attributes:
        team: Team identifier (string or TeamType)
        strategies: list of strategy names or np.array of probabilities
        probabilities: Classical probability distribution (optional)
        wavefunction: Quantum amplitude vector (optional)
    """

    team: Union[TeamType, str]
    strategies: Union[list[str], Any]  # Can be list of names or np.array
    probabilities: Optional[Any] = None  # np.ndarray when numpy available
    wavefunction: Optional[Any] = None  # np.ndarray when numpy available

    def __post_init__(self):
        # Handle string team names
        if isinstance(self.team, str):
            # Keep as string for flexibility, but could convert to TeamType
            pass

        # Handle strategies as np.array (probability distribution)
        if NUMPY_AVAILABLE and hasattr(self.strategies, "shape"):
            # strategies is actually a probability/amplitude array
            if self.probabilities is None:
                self.probabilities = self.strategies
            if self.wavefunction is None:
                self.wavefunction = self.strategies
            # Generate strategy names if needed
            if isinstance(self.strategies, np.ndarray):
                n = len(self.strategies)
                self.strategies = [f"strategy_{i}" for i in range(n)]

        if not NUMPY_AVAILABLE:
            # Lightweight fallback without numpy
            if isinstance(self.strategies, list):
                n = len(self.strategies)
                if self.probabilities is None:
                    self.probabilities = [1.0 / n] * n
                if self.wavefunction is None:
                    self.wavefunction = [1.0 / math.sqrt(n)] * n
            return

        n = len(self.strategies)
        if self.probabilities is None:
            # Uniform classical distribution
            self.probabilities = np.ones(n) / n
        if self.wavefunction is None:
            # Uniform superposition (equal amplitudes)
            self.wavefunction = np.ones(n, dtype=complex) / np.sqrt(n)

    @property
    def num_strategies(self) -> int:
        return len(self.strategies)

    def normalize_wavefunction(self) -> None:
        """Ensure wavefunction is normalized"""
        if not NUMPY_AVAILABLE:
            # Simple normalization for list-based fallback
            norm = math.sqrt(sum(abs(x) ** 2 for x in self.wavefunction))
            if norm > 1e-10:
                self.wavefunction = [x / norm for x in self.wavefunction]
            return

        norm = np.sqrt(np.vdot(self.wavefunction, self.wavefunction).real)
        if norm > 1e-10:
            self.wavefunction = self.wavefunction / norm

    def get_measurement_probabilities(self) -> Any:
        """Get probabilities from wavefunction (Born rule)"""
        if not NUMPY_AVAILABLE:
            return [abs(x) ** 2 for x in self.wavefunction]
        return np.abs(self.wavefunction) ** 2

    def collapse_to_strategy_index(self, rng: Optional[Any] = None) -> int:
        """Measure the wavefunction, returning a strategy index.

        Args:
            rng: Random number generator for reproducibility (numpy.random.Generator if available)

        Returns:
            Index of the selected strategy (use strategies[index] for name)
        """
        if not NUMPY_AVAILABLE:
            import random

            probs = self.get_measurement_probabilities()
            return random.choices(range(len(probs)), weights=probs)[0]

        if rng is None:
            rng = np.random.default_rng()
        probs = self.get_measurement_probabilities()
        return rng.choice(len(probs), p=probs)

    def collapse_to_strategy(self, rng: Optional[np.random.Generator] = None) -> str:
        """Measure the wavefunction, returning the strategy name.

        Args:
            rng: Random number generator for reproducibility

        Returns:
            Name of the selected strategy
        """
        idx = self.collapse_to_strategy_index(rng)
        return self.strategies[idx]

    def interpret_state(
        self,
        *,
        wavefunction: Optional[Any] = None,
        probabilities: Optional[Any] = None,
        probe: Optional[Any] = None,
        unembedding: Optional[Any] = None,
        top_k: int = 3,
    ) -> dict[str, Any]:
        """Interpret the current strategy state into concepts and labels.

        Args:
            wavefunction: Optional wavefunction override (uses self.wavefunction if None)
            probabilities: Optional probabilities override (uses self.probabilities if None)
            probe: Optional SparseLinearProbe for concept extraction
            unembedding: Optional UnembeddingHead for label projection
            top_k: Number of top concepts/labels to return

        Returns:
            Dictionary with:
                - concepts: List of (concept_name, score) tuples
                - labels: List of (label_name, logit) tuples
                - confidence: Overall confidence score
                - probabilities: Measurement probabilities
        """
        from agents.interpretability.sparse_probes import interpret_state_vector

        # Use provided or default wavefunction/probabilities
        wf = wavefunction if wavefunction is not None else self.wavefunction
        # Note: probabilities parameter kept for future use but not currently utilized
        # in the interpretation logic

        # Convert wavefunction to real vector for interpretation
        if not NUMPY_AVAILABLE:
            # Pure Python fallback
            state_vector = [abs(x) for x in wf]
        else:
            # Numpy path: use amplitudes (magnitudes)
            state_vector = np.abs(wf)

        # Interpret the state vector
        result = interpret_state_vector(
            state_vector,
            probe=probe,
            unembedding=unembedding,
            top_k=top_k,
        )

        # Add probability distribution
        if not NUMPY_AVAILABLE:
            result["probabilities"] = [abs(x) ** 2 for x in wf]
        else:
            result["probabilities"] = (np.abs(wf) ** 2).tolist()

        return result


@dataclass
class PayoffOperator:
    """Hermitian operator representing payoffs in quantum game theory.

    In quantum game theory, payoffs are represented as Hermitian operators
    whose expectation values give expected utilities.

    Attributes:
        payoff_matrix: Classical payoff matrix P[i,j]
        team: Team this operator belongs to (or players list)
    """

    payoff_matrix: np.ndarray
    team: Union[TeamType, list[str]] = TeamType.BLUE
    players: list[str] = field(default_factory=list)  # Alias for team

    def __post_init__(self):
        """Handle backwards compatibility"""
        # If players list provided, convert to team
        if self.players and not isinstance(self.team, TeamType):
            self.team = self.players  # Store players list

    @property
    def matrix(self) -> np.ndarray:
        """Alias for payoff_matrix"""
        return self.payoff_matrix

    @property
    def shape(self) -> tuple[int, int]:
        return self.payoff_matrix.shape

    def to_hamiltonian(self) -> np.ndarray:
        """Convert payoff to Hamiltonian (H = -P for minimization)"""
        return -self.payoff_matrix

    def as_diagonal_operator(self) -> np.ndarray:
        """Create diagonal operator in joint strategy basis.

        For joint state |i,j⟩, the operator is diagonal with entries P[i,j].
        """
        diag_entries = self.payoff_matrix.flatten()
        return np.diag(diag_entries)

    def expected_value(self, joint_wavefunction: np.ndarray) -> float:
        """Calculate expected payoff: ⟨ψ|Û|ψ⟩"""
        op = self.as_diagonal_operator()
        return np.vdot(joint_wavefunction, op @ joint_wavefunction).real


@dataclass
class QuantumGameState:
    """Complete quantum state of a two-team game.

    The joint state lives in H_A ⊗ H_B where:
    - H_A = C^m (Blue team Hilbert space)
    - H_B = C^n (Red team Hilbert space)

    Attributes:
        blue_state: Blue team strategy state
        red_state: Red team strategy state
        joint_wavefunction: Entangled/product state in H_A ⊗ H_B
        entanglement_strength: Degree of correlation (0=product, 1=maximally entangled)
    """

    blue_state: StrategyState
    red_state: StrategyState
    joint_wavefunction: Optional[np.ndarray] = None
    entanglement_strength: float = 0.0

    def __post_init__(self):
        if self.joint_wavefunction is None:
            # Initialize as product state
            self.joint_wavefunction = np.outer(
                self.blue_state.wavefunction, self.red_state.wavefunction
            ).flatten()

        self.normalize()

    @property
    def dimension(self) -> int:
        """Total Hilbert space dimension m × n"""
        return self.blue_state.num_strategies * self.red_state.num_strategies

    def normalize(self) -> None:
        """Normalize joint wavefunction"""
        norm = np.sqrt(np.vdot(self.joint_wavefunction, self.joint_wavefunction).real)
        if norm > 1e-10:
            self.joint_wavefunction = self.joint_wavefunction / norm

    def to_density_matrix(self) -> np.ndarray:
        """Convert pure state to density matrix: ρ = |ψ⟩⟨ψ|"""
        psi = self.joint_wavefunction
        return np.outer(psi, np.conj(psi))

    def get_reduced_density_matrix(self, team: TeamType) -> np.ndarray:
        """Partial trace to get reduced density matrix for one team"""
        m = self.blue_state.num_strategies
        n = self.red_state.num_strategies
        rho = self.to_density_matrix().reshape(m, n, m, n)

        if team == TeamType.BLUE:
            # Trace over Red (indices 1 and 3)
            return np.trace(rho, axis1=1, axis2=3)
        else:
            # Trace over Blue (indices 0 and 2)
            return np.trace(rho, axis1=0, axis2=2)

    def measure(self, rng: Optional[np.random.Generator] = None) -> tuple[int, int]:
        """Measure joint state, returning (blue_strategy_idx, red_strategy_idx)"""
        if rng is None:
            rng = np.random.default_rng()

        probs = np.abs(self.joint_wavefunction) ** 2
        num_red = self.red_state.num_strategies

        flat_idx = rng.choice(len(probs), p=probs)
        i = flat_idx // num_red
        j = flat_idx % num_red
        return i, j

    @property
    def entangled(self) -> bool:
        """Check if state is entangled (non-zero entanglement strength)"""
        return self.entanglement_strength > 0.0

    def break_entanglement(self) -> "QuantumGameState":
        """Break entanglement and return product state.

        Returns:
            New QuantumGameState with entanglement_strength=0 and product state
        """
        # Create new product state from current team states
        product_wavefunction = np.outer(
            self.blue_state.wavefunction, self.red_state.wavefunction
        ).flatten()

        return QuantumGameState(
            blue_state=self.blue_state,
            red_state=self.red_state,
            joint_wavefunction=product_wavefunction,
            entanglement_strength=0.0,
        )

    def calculate_correlation(self) -> float:
        """Calculate quantum correlation measure (CHSH-style).

        Computes correlation between blue and red measurements using:
        E(a,b) = Tr(ρ * σ_a ⊗ σ_b)

        Returns:
            Correlation value in range [-1, 1] for product states,
            can exceed classical bounds for entangled states
        """
        # Get reduced density matrices
        rho_blue = self.get_reduced_density_matrix(TeamType.BLUE)
        rho_red = self.get_reduced_density_matrix(TeamType.RED)

        # Calculate correlation using entanglement strength
        # For product state: correlation = 0
        # For maximally entangled: correlation approaches theoretical bound

        # Simple proxy: use entanglement strength weighted by state overlap
        if self.entanglement_strength == 0.0:
            return 0.0

        # Calculate overlap of reduced states with maximally mixed
        m = self.blue_state.num_strategies
        n = self.red_state.num_strategies

        # Purity measures: Tr(ρ²)
        purity_blue = np.trace(rho_blue @ rho_blue).real
        purity_red = np.trace(rho_red @ rho_red).real

        # Correlation scales with entanglement and anti-correlates with purity
        # (mixed states have less correlation)
        correlation = self.entanglement_strength * (2 - purity_blue - purity_red)

        # Clip to reasonable bounds (classical: [-1,1], quantum: up to 2√2 for CHSH)
        return np.clip(correlation, -2.828, 2.828)

    def violates_bell_inequality(self) -> bool:
        """Check if state violates Bell/CHSH inequality.

        Classical bound: |E| ≤ 2
        Quantum (Tsirelson) bound: |E| ≤ 2√2 ≈ 2.828

        Returns:
            True if correlation exceeds classical bound (suggests quantum entanglement)
        """
        correlation = abs(self.calculate_correlation())
        CLASSICAL_BOUND = 2.0
        return correlation > CLASSICAL_BOUND


class ClassicalGameEngine:
    """Classical energy-based game theory engine.

    Maps game theory to statistical physics:
    - Payoffs → Hamiltonian (H = -P)
    - Strategies → Microstates
    - Mixed strategies → Gibbs distribution
    - Nash equilibrium → Thermal equilibrium

    Uses:
    - Gibbs sampling for equilibrium computation
    - Replicator dynamics for strategy evolution
    - Simulated annealing for optimization
    """

    def __init__(
        self,
        blue_strategies: list[str],
        red_strategies: list[str],
        payoff_blue: np.ndarray,
        payoff_red: np.ndarray,
        beta: float = 1.0,
        alpha: float = 0.5,
    ):
        """Initialize classical game engine.

        Args:
            blue_strategies: list of Blue team strategy names
            red_strategies: list of Red team strategy names
            payoff_blue: Payoff matrix P_A[i,j] for Blue
            payoff_red: Payoff matrix P_B[i,j] for Red
            beta: Inverse temperature (higher = more deterministic)
            alpha: Team weight for combined Hamiltonian (0=Red, 1=Blue)
        """
        self.blue_strategies = blue_strategies
        self.red_strategies = red_strategies
        self.payoff_blue = payoff_blue
        self.payoff_red = payoff_red
        self.beta = beta
        self.alpha = alpha

        # Energy landscapes
        self.H_blue = -payoff_blue  # Hamiltonian
        self.H_red = -payoff_red
        self.H_combined = alpha * self.H_blue + (1 - alpha) * self.H_red

        # Initialize mixed strategies uniformly
        self.pi_blue = np.ones(len(blue_strategies)) / len(blue_strategies)
        self.pi_red = np.ones(len(red_strategies)) / len(red_strategies)

    def gibbs_distribution(self) -> np.ndarray:
        """Compute Gibbs distribution over joint strategies.

        p(i,j) ∝ exp(-β H(i,j))

        Returns:
            Joint probability distribution P[i,j]
        """
        exp_energies = np.exp(-self.beta * self.H_combined)
        Z = np.sum(exp_energies)  # Partition function
        return exp_energies / Z

    def expected_payoff(self, team: TeamType) -> float:
        """Compute expected payoff for a team under current mixed strategies."""
        if team == TeamType.BLUE:
            return np.einsum("i,ij,j->", self.pi_blue, self.payoff_blue, self.pi_red)
        else:
            return np.einsum("i,ij,j->", self.pi_blue, self.payoff_red, self.pi_red)

    def best_response_blue(self) -> int:
        """Compute Blue's best response to Red's current strategy"""
        expected_payoffs = self.payoff_blue @ self.pi_red
        return int(np.argmax(expected_payoffs))

    def best_response_red(self) -> int:
        """Compute Red's best response to Blue's current strategy"""
        expected_payoffs = self.pi_blue @ self.payoff_red
        return int(np.argmax(expected_payoffs))

    def replicator_dynamics_step(self, dt: float = 0.1) -> None:
        """Perform one step of replicator dynamics.

        Updates mixed strategies according to:
        π̇_A(i) = π_A(i) [U_A(i, π_B) - Ū_A(π_A, π_B)]
        """
        # Blue team update
        U_blue = self.payoff_blue @ self.pi_red  # Payoffs for each pure strategy
        U_bar_blue = self.pi_blue @ U_blue  # Average payoff
        delta_blue = self.pi_blue * (U_blue - U_bar_blue)
        self.pi_blue = self.pi_blue + dt * delta_blue
        self.pi_blue = np.maximum(self.pi_blue, 1e-10)
        self.pi_blue = self.pi_blue / np.sum(self.pi_blue)

        # Red team update
        U_red = self.pi_blue @ self.payoff_red  # Payoffs for each pure strategy
        U_bar_red = U_red @ self.pi_red  # Average payoff
        delta_red = self.pi_red * (U_red - U_bar_red)
        self.pi_red = self.pi_red + dt * delta_red
        self.pi_red = np.maximum(self.pi_red, 1e-10)
        self.pi_red = self.pi_red / np.sum(self.pi_red)

    def simulate_to_equilibrium(
        self, max_iterations: int = 1000, convergence_threshold: float = 1e-6
    ) -> dict[str, Any]:
        """Run replicator dynamics until convergence.

        Returns:
            Dictionary with equilibrium strategies and metrics
        """
        history = []

        for iteration in range(max_iterations):
            pi_blue_old = self.pi_blue.copy()
            pi_red_old = self.pi_red.copy()

            self.replicator_dynamics_step()

            # Check convergence
            delta_blue = np.max(np.abs(self.pi_blue - pi_blue_old))
            delta_red = np.max(np.abs(self.pi_red - pi_red_old))

            history.append(
                {
                    "iteration": iteration,
                    "delta_blue": delta_blue,
                    "delta_red": delta_red,
                    "payoff_blue": self.expected_payoff(TeamType.BLUE),
                    "payoff_red": self.expected_payoff(TeamType.RED),
                }
            )

            if delta_blue < convergence_threshold and delta_red < convergence_threshold:
                logger.info(f"Converged after {iteration + 1} iterations")
                break

        return {
            "pi_blue": self.pi_blue.copy(),
            "pi_red": self.pi_red.copy(),
            "payoff_blue": self.expected_payoff(TeamType.BLUE),
            "payoff_red": self.expected_payoff(TeamType.RED),
            "iterations": len(history),
            "converged": len(history) < max_iterations,
            "history": history,
        }

    def gibbs_sample(
        self, num_samples: int = 1000, rng: Optional[np.random.Generator] = None
    ) -> list[tuple[int, int]]:
        """Sample joint strategies from Gibbs distribution."""
        if rng is None:
            rng = np.random.default_rng()

        p_joint = self.gibbs_distribution()
        flat_probs = p_joint.flatten()

        num_red = len(self.red_strategies)

        samples = []
        for _ in range(num_samples):
            flat_idx = rng.choice(len(flat_probs), p=flat_probs)
            i = flat_idx // num_red
            j = flat_idx % num_red
            samples.append((i, j))

        return samples

    def compute_nash_equilibrium(self) -> dict[str, Any]:
        """
        Compute Nash equilibrium using replicator dynamics.

        This method finds a Nash equilibrium by iterating the game dynamics
        until convergence. The equilibrium is a stable state where neither
        player can improve their payoff by unilaterally changing strategy.

        Returns:
            Dictionary with equilibrium strategies and metrics
        """
        return self.simulate_to_equilibrium()

    def calculate(self) -> dict[str, Any]:
        """
        Calculate equilibrium (alias for compute_nash_equilibrium).

        Returns:
            Dictionary with equilibrium strategies and metrics
        """
        return self.compute_nash_equilibrium()


class QuantumInspiredGameEngine:
    """Quantum-inspired game theory engine.

    Extends classical game theory with:
    - Wavefunctions as strategy representations
    - Unitary operators as strategy updates
    - Entanglement for correlated strategies
    - Decoherence for noise modeling

    Key differences from classical:
    - Strategies can be in superposition
    - Teams can be entangled (correlated beyond classical)
    - Interference effects can amplify/suppress strategies
    """

    def __init__(
        self,
        blue_strategies: list[str],
        red_strategies: list[str],
        payoff_blue: np.ndarray,
        payoff_red: np.ndarray,
        entanglement: float = 0.0,
    ):
        """Initialize quantum game engine.

        Args:
            blue_strategies: list of Blue team strategy names
            red_strategies: list of Red team strategy names
            payoff_blue: Payoff matrix P_A[i,j] for Blue
            payoff_red: Payoff matrix P_B[i,j] for Red
            entanglement: Initial entanglement strength (0-1)
        """
        self.blue_strategies = blue_strategies
        self.red_strategies = red_strategies

        # Create strategy states
        self.blue_state = StrategyState(TeamType.BLUE, blue_strategies)
        self.red_state = StrategyState(TeamType.RED, red_strategies)

        # Create payoff operators
        self.U_blue = PayoffOperator(payoff_blue, TeamType.BLUE)
        self.U_red = PayoffOperator(payoff_red, TeamType.RED)

        # Create quantum game state
        self.game_state = QuantumGameState(
            self.blue_state, self.red_state, entanglement_strength=entanglement
        )

        # Initialize with optional entanglement
        if entanglement > 0:
            self._apply_entanglement(entanglement)

    def _apply_entanglement(self, strength: float) -> None:
        """Apply entangling operation to create correlated strategies.

        Uses a simple parameterized entangling gate:
        J(γ) = exp(iγ (|00⟩⟨00| - |11⟩⟨11|))

        For simplicity, we interpolate between product and maximally entangled.
        """
        m = self.blue_state.num_strategies
        n = self.red_state.num_strategies

        # Product state
        psi_product = np.outer(self.blue_state.wavefunction, self.red_state.wavefunction).flatten()

        # Simple entangled state (Bell-like for min dimensions)
        min_dim = min(m, n)
        psi_entangled = np.zeros(m * n, dtype=complex)
        for k in range(min_dim):
            idx = k * n + k
            if idx < m * n:
                psi_entangled[idx] = 1.0 / np.sqrt(min_dim)

        # Interpolate
        self.game_state.joint_wavefunction = (1 - strength) * psi_product + strength * psi_entangled
        self.game_state.normalize()
        self.game_state.entanglement_strength = strength

    def create_rotation_unitary(
        self, theta: float, phi: float = 0.0, dimension: int = 2
    ) -> np.ndarray:
        """Create a parameterized unitary for strategy updates.

        For dimension=2, this is:
        U(θ, φ) = [[cos(θ/2), -e^{iφ} sin(θ/2)],
                    [e^{-iφ} sin(θ/2), cos(θ/2)]]

        For higher dimensions, extends to block-diagonal rotations.
        """
        if dimension == 2:
            c = math.cos(theta / 2)
            s = math.sin(theta / 2)
            exp_phi = np.exp(1j * phi)
            return np.array([[c, -exp_phi * s], [np.conj(exp_phi) * s, c]], dtype=complex)
        else:
            # Block-diagonal extension
            U = np.eye(dimension, dtype=complex)
            for k in range(0, dimension - 1, 2):
                c = math.cos(theta / 2)
                s = math.sin(theta / 2)
                U[k, k] = c
                U[k, k + 1] = -s
                U[k + 1, k] = s
                U[k + 1, k + 1] = c
            return U

    def apply_strategy_update(
        self, theta_blue: float, theta_red: float, phi_blue: float = 0.0, phi_red: float = 0.0
    ) -> None:
        """Apply unitary strategy updates to both teams.

        |ψ_new⟩ = (U_A ⊗ U_B) |ψ_old⟩
        """
        m = self.blue_state.num_strategies
        n = self.red_state.num_strategies

        U_blue = self.create_rotation_unitary(theta_blue, phi_blue, m)
        U_red = self.create_rotation_unitary(theta_red, phi_red, n)

        # Kronecker product
        U_joint = np.kron(U_blue, U_red)

        # Apply to state
        self.game_state.joint_wavefunction = U_joint @ self.game_state.joint_wavefunction
        self.game_state.normalize()

    def expected_payoff(self, team: TeamType) -> float:
        """Calculate expected payoff for a team: ⟨ψ|Û|ψ⟩"""
        if team == TeamType.BLUE:
            return self.U_blue.expected_value(self.game_state.joint_wavefunction)
        else:
            return self.U_red.expected_value(self.game_state.joint_wavefunction)

    def payoff_variance(self, team: TeamType) -> float:
        """Calculate variance of payoff: ⟨ψ|Û²|ψ⟩ - ⟨ψ|Û|ψ⟩²

        Useful for risk-sensitive decision making.
        """
        psi = self.game_state.joint_wavefunction

        if team == TeamType.BLUE:
            U_op = self.U_blue.as_diagonal_operator()
        else:
            U_op = self.U_red.as_diagonal_operator()

        E_U = np.vdot(psi, U_op @ psi).real
        E_U2 = np.vdot(psi, U_op @ U_op @ psi).real

        return E_U2 - E_U**2

    def risk_adjusted_utility(self, team: TeamType, risk_aversion: float = 0.5) -> float:
        """Calculate risk-adjusted utility.

        J = E[U] - λ Var(U)

        Args:
            team: Team to calculate for
            risk_aversion: λ parameter (0 = risk-neutral, higher = risk-averse)
        """
        mean = self.expected_payoff(team)
        variance = self.payoff_variance(team)
        return mean - risk_aversion * variance

    def apply_decoherence(self, gamma: float) -> None:
        """Apply dephasing decoherence to model noise/imperfect coordination.

        Reduces off-diagonal elements of density matrix by factor (1-γ).
        γ = 0: No decoherence (pure quantum)
        γ = 1: Full decoherence (classical mixed state)
        """
        rho = self.game_state.to_density_matrix()

        # Dephasing: reduce off-diagonal elements
        dim = len(rho)
        for i in range(dim):
            for j in range(dim):
                if i != j:
                    rho[i, j] *= 1 - gamma

        # Extract dominant eigenvector as new pure state approximation
        eigenvalues, eigenvectors = np.linalg.eigh(rho)
        dominant_idx = np.argmax(eigenvalues)
        self.game_state.joint_wavefunction = eigenvectors[:, dominant_idx]
        self.game_state.normalize()

    def gradient_payoff_wrt_theta(
        self, team: TeamType, theta_current: float, epsilon: float = 0.01
    ) -> float:
        """Estimate gradient of expected payoff w.r.t. rotation angle.

        Uses parameter-shift rule (quantum gradient estimation).
        """
        # Save current state
        psi_backup = self.game_state.joint_wavefunction.copy()

        # Forward evaluation
        if team == TeamType.BLUE:
            self.apply_strategy_update(theta_current + epsilon, 0.0)
        else:
            self.apply_strategy_update(0.0, theta_current + epsilon)
        payoff_plus = self.expected_payoff(team)

        # Restore and backward evaluation
        self.game_state.joint_wavefunction = psi_backup.copy()
        if team == TeamType.BLUE:
            self.apply_strategy_update(theta_current - epsilon, 0.0)
        else:
            self.apply_strategy_update(0.0, theta_current - epsilon)
        payoff_minus = self.expected_payoff(team)

        # Restore original state
        self.game_state.joint_wavefunction = psi_backup

        return (payoff_plus - payoff_minus) / (2 * epsilon)

    def quantum_policy_gradient_step(
        self, learning_rate: float = 0.1, theta_blue: float = 0.0, theta_red: float = 0.0
    ) -> tuple[float, float]:
        """Perform one step of quantum policy gradient for both teams.

        Returns updated (theta_blue, theta_red).
        """
        grad_blue = self.gradient_payoff_wrt_theta(TeamType.BLUE, theta_blue)
        grad_red = self.gradient_payoff_wrt_theta(TeamType.RED, theta_red)

        theta_blue_new = theta_blue + learning_rate * grad_blue
        theta_red_new = theta_red + learning_rate * grad_red

        return theta_blue_new, theta_red_new

    def play_round(
        self,
        theta_blue: float = 0.1,
        theta_red: float = 0.1,
        apply_noise: bool = False,
        decoherence_gamma: float = 0.0,
    ) -> dict[str, float]:
        """Play a single round of the quantum game.

        Args:
            theta_blue: Blue team's strategy rotation angle
            theta_red: Red team's strategy rotation angle
            apply_noise: Whether to apply decoherence (noise)
            decoherence_gamma: Strength of decoherence (0-1)

        Returns:
            Dictionary with payoffs for both teams
        """
        # Apply strategy updates
        self.apply_strategy_update(theta_blue, theta_red)

        # Optionally apply noise
        if apply_noise and decoherence_gamma > 0:
            self.apply_decoherence(decoherence_gamma)

        # Calculate payoffs
        blue_payoff = self.expected_payoff(TeamType.BLUE)
        red_payoff = self.expected_payoff(TeamType.RED)

        return {
            "blue_payoff": blue_payoff,
            "red_payoff": red_payoff,
            "entanglement": self.game_state.entanglement_strength,
            "interpretability": self.interpret_states(),
        }

    def get_payoffs(self) -> tuple[float, float]:
        """Get current expected payoffs for both teams.

        Returns:
            tuple of (blue_payoff, red_payoff)
        """
        blue_payoff = self.expected_payoff(TeamType.BLUE)
        red_payoff = self.expected_payoff(TeamType.RED)
        return (blue_payoff, red_payoff)

    def interpret_states(
        self,
        *,
        probe: Optional[Any] = None,
        unembedding: Optional[Any] = None,
        top_k: int = 3,
    ) -> dict[str, Any]:
        """Return interpretability artifacts for both teams.

        Args:
            probe: Optional SparseLinearProbe for concept extraction
            unembedding: Optional UnembeddingHead for label projection
            top_k: Number of top concepts/labels to return

        Returns:
            Dictionary with:
                - blue: Interpretation of blue team state
                - red: Interpretation of red team state
        """
        blue_interp = self.blue_state.interpret_state(
            probe=probe,
            unembedding=unembedding,
            top_k=top_k,
        )

        red_interp = self.red_state.interpret_state(
            probe=probe,
            unembedding=unembedding,
            top_k=top_k,
        )

        return {
            "blue": blue_interp,
            "red": red_interp,
        }


class BlueRedTeamSimulator:
    """High-level simulator for Blue Team vs Red Team scenarios.

    Combines classical and quantum-inspired game theory for:
    - Defense (Blue) vs Attack (Red) strategy optimization
    - Correlated strategies via entanglement
    - Risk-sensitive decision making
    - Noise modeling via decoherence
    """

    def __init__(
        self,
        blue_strategies: list[str],
        red_strategies: list[str],
        payoff_blue: np.ndarray,
        payoff_red: np.ndarray,
        mode: str = "quantum",
        entanglement: float = 0.0,
        noise_level: float = 0.0,
        risk_aversion: float = 0.5,
    ):
        """Initialize simulator.

        Args:
            blue_strategies: Defense strategy names
            red_strategies: Attack strategy names
            payoff_blue: Blue team payoff matrix
            payoff_red: Red team payoff matrix
            mode: "classical" or "quantum"
            entanglement: Entanglement strength for quantum mode
            noise_level: Decoherence level for modeling uncertainty
            risk_aversion: Risk aversion parameter for decision making
        """
        self.mode = mode
        self.noise_level = noise_level
        self.risk_aversion = risk_aversion

        self.classical_engine = ClassicalGameEngine(
            blue_strategies, red_strategies, payoff_blue, payoff_red
        )

        self.quantum_engine = QuantumInspiredGameEngine(
            blue_strategies, red_strategies, payoff_blue, payoff_red, entanglement=entanglement
        )

        self.history: list[dict[str, Any]] = []

    def evaluate_hypothesis(
        self,
        hypothesis: str,
        blue_strategy_weights: Optional[np.ndarray] = None,
        red_strategy_weights: Optional[np.ndarray] = None,
    ) -> dict[str, Any]:
        """Evaluate a hypothesis about optimal strategies.

        Uses physics-inspired calculations to assess:
        - Expected payoffs for both teams
        - Risk (variance) of outcomes
        - Equilibrium stability

        Args:
            hypothesis: Description of the hypothesis
            blue_strategy_weights: Optional prior weights for Blue strategies
            red_strategy_weights: Optional prior weights for Red strategies

        Returns:
            Evaluation results with metrics and recommendations
        """
        results = {
            "hypothesis": hypothesis,
            "mode": self.mode,
            "timestamp": None,  # Can be set by caller
        }

        # Initialize strategy weights if provided
        if blue_strategy_weights is not None:
            self.classical_engine.pi_blue = blue_strategy_weights / np.sum(blue_strategy_weights)
            self.quantum_engine.blue_state.wavefunction = np.sqrt(
                blue_strategy_weights / np.sum(blue_strategy_weights)
            )
            self.quantum_engine.blue_state.normalize_wavefunction()

        if red_strategy_weights is not None:
            self.classical_engine.pi_red = red_strategy_weights / np.sum(red_strategy_weights)
            self.quantum_engine.red_state.wavefunction = np.sqrt(
                red_strategy_weights / np.sum(red_strategy_weights)
            )
            self.quantum_engine.red_state.normalize_wavefunction()

        if self.mode == "classical":
            # Classical analysis
            equilibrium = self.classical_engine.simulate_to_equilibrium()

            results.update(
                {
                    "blue_expected_payoff": equilibrium["payoff_blue"],
                    "red_expected_payoff": equilibrium["payoff_red"],
                    "blue_equilibrium_strategy": equilibrium["pi_blue"].tolist(),
                    "red_equilibrium_strategy": equilibrium["pi_red"].tolist(),
                    "converged": equilibrium["converged"],
                    "iterations": equilibrium["iterations"],
                    "gibbs_distribution": self.classical_engine.gibbs_distribution().tolist(),
                }
            )
        else:
            # Quantum analysis
            # Apply noise if specified
            if self.noise_level > 0:
                self.quantum_engine.apply_decoherence(self.noise_level)

            blue_payoff = self.quantum_engine.expected_payoff(TeamType.BLUE)
            red_payoff = self.quantum_engine.expected_payoff(TeamType.RED)

            blue_variance = self.quantum_engine.payoff_variance(TeamType.BLUE)
            red_variance = self.quantum_engine.payoff_variance(TeamType.RED)

            blue_risk_adj = self.quantum_engine.risk_adjusted_utility(
                TeamType.BLUE, self.risk_aversion
            )
            red_risk_adj = self.quantum_engine.risk_adjusted_utility(
                TeamType.RED, self.risk_aversion
            )

            results.update(
                {
                    "blue_expected_payoff": blue_payoff,
                    "red_expected_payoff": red_payoff,
                    "blue_payoff_variance": blue_variance,
                    "red_payoff_variance": red_variance,
                    "blue_risk_adjusted_utility": blue_risk_adj,
                    "red_risk_adjusted_utility": red_risk_adj,
                    "entanglement_strength": self.quantum_engine.game_state.entanglement_strength,
                    "measurement_probabilities": np.abs(
                        self.quantum_engine.game_state.joint_wavefunction
                    ).tolist(),
                }
            )

        self.history.append(results)
        return results

    def compare_strategies(
        self,
        blue_options: list[np.ndarray],
        red_options: list[np.ndarray],
    ) -> dict[str, Any]:
        """Compare multiple strategy configurations.

        Useful for hypothesis testing across different configurations.
        """
        comparisons = []

        for i, blue_weights in enumerate(blue_options):
            for j, red_weights in enumerate(red_options):
                result = self.evaluate_hypothesis(
                    f"Blue config {i} vs Red config {j}",
                    blue_strategy_weights=blue_weights,
                    red_strategy_weights=red_weights,
                )
                result["blue_config_idx"] = i
                result["red_config_idx"] = j
                comparisons.append(result)

        # Find optimal configurations
        if self.mode == "quantum":
            best_for_blue = max(comparisons, key=lambda x: x["blue_risk_adjusted_utility"])
            best_for_red = max(comparisons, key=lambda x: x["red_risk_adjusted_utility"])
        else:
            best_for_blue = max(comparisons, key=lambda x: x["blue_expected_payoff"])
            best_for_red = max(comparisons, key=lambda x: x["red_expected_payoff"])

        return {
            "comparisons": comparisons,
            "best_for_blue": best_for_blue,
            "best_for_red": best_for_red,
            "total_configurations": len(comparisons),
        }

    def run_simulation(
        self,
        num_rounds: int = 10,
        learning_rate: float = 0.1,
    ) -> dict[str, Any]:
        """Run multi-round simulation with learning.

        Both teams update their strategies based on outcomes.
        """
        round_results = []
        theta_blue, theta_red = 0.0, 0.0

        for round_num in range(num_rounds):
            if self.mode == "quantum":
                # Quantum policy gradient updates
                theta_blue, theta_red = self.quantum_engine.quantum_policy_gradient_step(
                    learning_rate, theta_blue, theta_red
                )
                self.quantum_engine.apply_strategy_update(theta_blue, theta_red)

                if self.noise_level > 0:
                    self.quantum_engine.apply_decoherence(self.noise_level)

                result = {
                    "round": round_num,
                    "theta_blue": theta_blue,
                    "theta_red": theta_red,
                    "blue_payoff": self.quantum_engine.expected_payoff(TeamType.BLUE),
                    "red_payoff": self.quantum_engine.expected_payoff(TeamType.RED),
                }
            else:
                # Classical replicator dynamics
                self.classical_engine.replicator_dynamics_step(dt=learning_rate)

                result = {
                    "round": round_num,
                    "pi_blue": self.classical_engine.pi_blue.copy().tolist(),
                    "pi_red": self.classical_engine.pi_red.copy().tolist(),
                    "blue_payoff": self.classical_engine.expected_payoff(TeamType.BLUE),
                    "red_payoff": self.classical_engine.expected_payoff(TeamType.RED),
                }

            round_results.append(result)

        return {
            "mode": self.mode,
            "num_rounds": num_rounds,
            "learning_rate": learning_rate,
            "rounds": round_results,
            "final_blue_payoff": round_results[-1]["blue_payoff"],
            "final_red_payoff": round_results[-1]["red_payoff"],
        }


# Utility functions for creating common game scenarios


def create_prisoners_dilemma() -> tuple[list[str], list[str], np.ndarray, np.ndarray]:
    """Create Prisoner's Dilemma payoff matrices."""
    strategies = ["Cooperate", "Defect"]
    # (row, col) = (Blue, Red)
    # Payoffs: (T > R > P > S), T=3, R=2, P=1, S=0
    payoff_blue = np.array(
        [
            [2, 0],  # Blue Cooperate: (C,C)=2, (C,D)=0
            [3, 1],  # Blue Defect: (D,C)=3, (D,D)=1
        ]
    )
    payoff_red = np.array(
        [
            [2, 3],  # Red vs Blue Cooperate: (C,C)=2, (C,D)=3
            [0, 1],  # Red vs Blue Defect: (D,C)=0, (D,D)=1
        ]
    )
    return strategies, strategies, payoff_blue, payoff_red


def create_zero_sum_game(
    size: int = 3, seed: Optional[int] = None
) -> tuple[list[str], list[str], np.ndarray, np.ndarray]:
    """Create a random zero-sum game.

    Args:
        size: Number of strategies per team
        seed: Random seed for reproducibility. If None, uses system entropy
              for the random generator which varies between runs.

    Returns:
        tuple of (blue_strategies, red_strategies, payoff_blue, payoff_red)
    """
    rng = np.random.default_rng(seed)
    strategies = [f"S{i}" for i in range(size)]
    payoff_blue = rng.standard_normal((size, size))
    payoff_red = -payoff_blue  # Zero-sum
    return strategies, strategies, payoff_blue, payoff_red


def create_security_game() -> tuple[list[str], list[str], np.ndarray, np.ndarray]:
    """Create a cybersecurity-inspired game.

    Blue (Defense): Firewall, IDS, Patch, Monitor
    Red (Attack): Exploit, DDoS, Phishing, Insider
    """
    blue_strategies = ["Firewall", "IDS", "Patch", "Monitor"]
    red_strategies = ["Exploit", "DDoS", "Phishing", "Insider"]

    # Payoffs reflect effectiveness of defense against each attack
    payoff_blue = np.array(
        [
            [0.8, 0.6, 0.3, 0.2],  # Firewall effectiveness
            [0.7, 0.5, 0.6, 0.4],  # IDS effectiveness
            [0.9, 0.3, 0.4, 0.5],  # Patching effectiveness
            [0.5, 0.4, 0.7, 0.8],  # Monitoring effectiveness
        ]
    )

    payoff_red = 1.0 - payoff_blue  # Adversarial (almost zero-sum)

    return blue_strategies, red_strategies, payoff_blue, payoff_red

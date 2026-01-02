"""
Entanglement Manager for Quantum-Inspired Agent Coordination.

Implements Bell-state-inspired correlation tracking for multi-agent systems,
enabling synchronized decision-making and reduced redundancy.

Physics Inspiration:
- Bell State: |Ψ⟩ = (|00⟩ + |11⟩)/√2 (maximally entangled)
- Measurement Correlation: P(both_agree) > P(independent)
- State Collapse Synchronization

Rayleigh Metrics:
- NA (Numerical Aperture): 1.0 → 2.0 (two-agent coordination)
- Correlation Accuracy: Target > 0.90
- State Sync Latency: < 10ms
"""

import time
import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional
from collections import Counter
import math

from cognitive_brain.quantum.config import QuantumConfig
from cognitive_brain.quantum.coherence_monitor import CoherenceMonitor
from cognitive_brain.quantum.base import QuantumFeature


@dataclass
class EntangledPair:
    """
    Represents an entangled pair of agents.
    
    Attributes:
        pair_id: Unique identifier for the entangled pair
        agent1_id: First agent identifier
        agent2_id: Second agent identifier
        correlation_strength: Target correlation coefficient (0-1)
        observed_states: History of (agent1_state, agent2_state) observations
        created_at: Timestamp when pair was created
        last_measurement: Timestamp of last correlation measurement
    """
    pair_id: str
    agent1_id: str
    agent2_id: str
    correlation_strength: float
    observed_states: List[Tuple[Any, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_measurement: Optional[float] = None


@dataclass
class CorrelationMeasurement:
    """
    Correlation measurement result for an entangled pair.
    
    Attributes:
        pair_id: Entangled pair identifier
        correlation: Pearson correlation coefficient (-1 to 1)
        mutual_information: Mutual information in bits
        sample_size: Number of observations used
        timestamp: Measurement timestamp
    """
    pair_id: str
    correlation: float
    mutual_information: float
    sample_size: int
    timestamp: float = field(default_factory=time.time)


class EntanglementManager:
    """
    Manages quantum-inspired entanglement between agent pairs.
    
    Enables correlated state evolution and synchronized decision-making,
    reducing redundancy and improving cross-agent consistency.
    
    Bell State Representation:
    - |00⟩: Both agents in state 0 (e.g., both approve)
    - |11⟩: Both agents in state 1 (e.g., both reject)
    - |Ψ⟩ = (|00⟩ + |11⟩)/√2: Maximally entangled
    
    Example:
        >>> config = QuantumConfig.from_env()
        >>> monitor = CoherenceMonitor(config, repository)
        >>> manager = EntanglementManager(config, monitor)
        >>> pair_id = manager.create_entanglement("compliance", "security")
        >>> manager.update_correlation(pair_id, "approve", "approve")
        >>> correlation = manager.measure_correlation(pair_id)
    """
    
    def __init__(self, config: QuantumConfig, monitor: CoherenceMonitor):
        """
        Initialize Entanglement Manager.
        
        Args:
            config: Quantum configuration with feature flags
            monitor: Coherence monitor for tracking correlation quality
        """
        self.config = config
        self.monitor = monitor
        self.entangled_pairs: Dict[str, EntangledPair] = {}
        self.correlation_history: List[CorrelationMeasurement] = []
    
    def create_entanglement(
        self, 
        agent1_id: str, 
        agent2_id: str,
        correlation_strength: float = 1.0
    ) -> str:
        """
        Create entangled pair between two agents.
        
        Args:
            agent1_id: First agent identifier
            agent2_id: Second agent identifier
            correlation_strength: Target correlation (0-1), default 1.0
        
        Returns:
            Pair ID for future reference
        
        Raises:
            ValueError: If correlation_strength not in [0, 1]
        
        Example:
            >>> pair_id = manager.create_entanglement("agent1", "agent2", 0.9)
        """
        if not 0 <= correlation_strength <= 1:
            raise ValueError(f"correlation_strength must be in [0, 1], got {correlation_strength}")
        
        # Generate deterministic pair ID
        pair_key = f"{agent1_id}:{agent2_id}"
        pair_id = hashlib.sha256(pair_key.encode()).hexdigest()[:16]
        
        # Check for existing entanglement
        if pair_id in self.entangled_pairs:
            return pair_id
        
        # Create new entangled pair
        pair = EntangledPair(
            pair_id=pair_id,
            agent1_id=agent1_id,
            agent2_id=agent2_id,
            correlation_strength=correlation_strength
        )
        
        self.entangled_pairs[pair_id] = pair
        
        # Record creation event
        if self.config.is_enabled(QuantumFeature.ENTANGLEMENT.value):
            self.monitor.record_metric(
                feature='entanglement',
                metric_name='pair_created',
                metric_value=correlation_strength,
                metadata={'agent1': agent1_id, 'agent2': agent2_id}
            )
        
        return pair_id
    
    def measure_correlation(self, pair_id: str) -> float:
        """
        Measure Pearson correlation between entangled agents.
        
        Computes correlation coefficient from observed state history.
        
        Args:
            pair_id: Entangled pair identifier
        
        Returns:
            Pearson correlation coefficient (-1 to 1):
            - 1.0 = perfect positive correlation
            - 0.0 = no correlation
            - -1.0 = perfect negative correlation
        
        Raises:
            KeyError: If pair_id not found
            ValueError: If insufficient observations (< 2)
        
        Example:
            >>> correlation = manager.measure_correlation(pair_id)
            >>> print(f"Correlation: {correlation:.3f}")
        """
        if pair_id not in self.entangled_pairs:
            raise KeyError(f"Entangled pair {pair_id} not found")
        
        pair = self.entangled_pairs[pair_id]
        
        if len(pair.observed_states) < 2:
            raise ValueError(f"Insufficient observations for correlation (need >= 2, have {len(pair.observed_states)})")
        
        # Convert states to numeric for correlation
        states1, states2 = zip(*pair.observed_states)
        numeric1 = self._states_to_numeric(states1)
        numeric2 = self._states_to_numeric(states2)
        
        # Compute Pearson correlation
        correlation = self._pearson_correlation(numeric1, numeric2)
        
        # Record measurement
        pair.last_measurement = time.time()
        
        if self.config.is_enabled(QuantumFeature.ENTANGLEMENT.value):
            self.monitor.record_metric(
                feature='entanglement',
                metric_name='correlation',
                metric_value=correlation,
                metadata={'pair_id': pair_id, 'sample_size': len(pair.observed_states)}
            )
        
        return correlation
    
    def collapse_entangled_state(
        self, 
        pair_id: str,
        agent1_measurement: Any
    ) -> Any:
        """
        Collapse entangled state based on agent1 measurement.
        
        When agent1 makes a decision, agent2 state collapses to a correlated
        state based on the target correlation strength. Uses historical
        patterns to suggest agent2 state.
        
        Args:
            pair_id: Entangled pair identifier
            agent1_measurement: Agent1's measured state
        
        Returns:
            Suggested state for agent2 (correlated with agent1)
        
        Raises:
            KeyError: If pair_id not found
        
        Example:
            >>> agent2_state = manager.collapse_entangled_state(pair_id, "approve")
            >>> # agent2_state is likely "approve" if correlation is high
        """
        if pair_id not in self.entangled_pairs:
            raise KeyError(f"Entangled pair {pair_id} not found")
        
        pair = self.entangled_pairs[pair_id]
        
        # If no history, return same state (perfect correlation guess)
        if not pair.observed_states:
            return agent1_measurement
        
        # Find most common agent2 state when agent1 had this state
        matching_agent2_states = [
            state2 for state1, state2 in pair.observed_states
            if state1 == agent1_measurement
        ]
        
        if not matching_agent2_states:
            # No matching history, return same state
            return agent1_measurement
        
        # Return most frequent correlated state
        state_counts = Counter(matching_agent2_states)
        suggested_state = state_counts.most_common(1)[0][0]
        
        # Record collapse event
        if self.config.is_enabled(QuantumFeature.ENTANGLEMENT.value):
            self.monitor.record_metric(
                feature='entanglement',
                metric_name='state_collapse',
                metric_value=pair.correlation_strength,
                metadata={
                    'pair_id': pair_id,
                    'agent1_state': str(agent1_measurement),
                    'agent2_state': str(suggested_state)
                }
            )
        
        return suggested_state
    
    def get_entanglement_strength(self, pair_id: str) -> float:
        """
        Get current entanglement strength for a pair.
        
        Returns the target correlation strength, not measured correlation.
        Use measure_correlation() for actual observed correlation.
        
        Args:
            pair_id: Entangled pair identifier
        
        Returns:
            Correlation strength (0-1)
        
        Raises:
            KeyError: If pair_id not found
        """
        if pair_id not in self.entangled_pairs:
            raise KeyError(f"Entangled pair {pair_id} not found")
        
        return self.entangled_pairs[pair_id].correlation_strength
    
    def update_correlation(
        self,
        pair_id: str,
        agent1_state: Any,
        agent2_state: Any
    ) -> None:
        """
        Update correlation tracking with new observations.
        
        Records a new (agent1_state, agent2_state) observation to improve
        correlation measurement accuracy over time.
        
        Args:
            pair_id: Entangled pair identifier
            agent1_state: Agent1's observed state
            agent2_state: Agent2's observed state
        
        Raises:
            KeyError: If pair_id not found
        
        Example:
            >>> manager.update_correlation(pair_id, "approve", "approve")
            >>> manager.update_correlation(pair_id, "reject", "reject")
        """
        if pair_id not in self.entangled_pairs:
            raise KeyError(f"Entangled pair {pair_id} not found")
        
        pair = self.entangled_pairs[pair_id]
        pair.observed_states.append((agent1_state, agent2_state))
        
        # Record update
        if self.config.is_enabled(QuantumFeature.ENTANGLEMENT.value):
            self.monitor.record_metric(
                feature='entanglement',
                metric_name='observation_added',
                metric_value=1.0,
                metadata={
                    'pair_id': pair_id,
                    'total_observations': len(pair.observed_states)
                }
            )
    
    def break_entanglement(self, pair_id: str) -> None:
        """
        Break entanglement between agent pair.
        
        Removes the entangled pair and clears observation history.
        
        Args:
            pair_id: Entangled pair identifier
        
        Raises:
            KeyError: If pair_id not found
        """
        if pair_id not in self.entangled_pairs:
            raise KeyError(f"Entangled pair {pair_id} not found")
        
        del self.entangled_pairs[pair_id]
        
        if self.config.is_enabled(QuantumFeature.ENTANGLEMENT.value):
            self.monitor.record_metric(
                feature='entanglement',
                metric_name='pair_broken',
                metric_value=1.0,
                metadata={'pair_id': pair_id}
            )
    
    def compute_bell_state_fidelity(self, pair_id: str) -> float:
        """
        Compute fidelity to ideal Bell state.
        
        Ideal Bell state: P(00) = P(11) = 0.5, P(01) = P(10) = 0
        Fidelity = 1.0 for perfect Bell state matching
        
        Args:
            pair_id: Entangled pair identifier
        
        Returns:
            Fidelity score (0-1), 1.0 = perfect Bell state
        
        Raises:
            KeyError: If pair_id not found
            ValueError: If insufficient observations
        """
        if pair_id not in self.entangled_pairs:
            raise KeyError(f"Entangled pair {pair_id} not found")
        
        pair = self.entangled_pairs[pair_id]
        
        if len(pair.observed_states) < 2:
            raise ValueError(f"Insufficient observations for fidelity (need >= 2)")
        
        # Convert to binary states
        states = []
        for s1, s2 in pair.observed_states:
            # Map to 0 or 1
            b1 = 1 if self._state_to_binary(s1) else 0
            b2 = 1 if self._state_to_binary(s2) else 0
            states.append((b1, b2))
        
        # Count state occurrences
        state_counts = Counter(states)
        total = len(states)
        
        p00 = state_counts[(0, 0)] / total
        p01 = state_counts[(0, 1)] / total
        p10 = state_counts[(1, 0)] / total
        p11 = state_counts[(1, 1)] / total
        
        # Ideal Bell state: P(00) = P(11) = 0.5, P(01) = P(10) = 0
        # Fidelity = 1 - average deviation from ideal
        deviation = (
            abs(p00 - 0.5) + 
            abs(p11 - 0.5) + 
            abs(p01 - 0.0) + 
            abs(p10 - 0.0)
        ) / 2  # Normalize to [0, 1]
        
        fidelity = 1.0 - deviation
        
        return fidelity
    
    def compute_mutual_information(self, pair_id: str) -> float:
        """
        Compute mutual information between agent states (bits).
        
        Measures how much information agent1 state provides about agent2 state.
        
        Args:
            pair_id: Entangled pair identifier
        
        Returns:
            Mutual information in bits (>= 0)
        
        Raises:
            KeyError: If pair_id not found
            ValueError: If insufficient observations
        """
        if pair_id not in self.entangled_pairs:
            raise KeyError(f"Entangled pair {pair_id} not found")
        
        pair = self.entangled_pairs[pair_id]
        
        if len(pair.observed_states) < 2:
            raise ValueError(f"Insufficient observations for mutual information")
        
        states1, states2 = zip(*pair.observed_states)
        
        return self._mutual_information(states1, states2)
    
    # Private helper methods
    
    def _states_to_numeric(self, states: Tuple[Any, ...]) -> List[float]:
        """Convert states to numeric values for correlation calculation."""
        # Create mapping from unique states to integers
        unique_states = sorted(set(states), key=str)
        state_to_int = {state: i for i, state in enumerate(unique_states)}
        
        return [float(state_to_int[state]) for state in states]
    
    def _pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """Compute Pearson correlation coefficient."""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        n = len(x)
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        
        # Compute covariance and standard deviations
        covariance = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n)) / n
        std_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x) / n)
        std_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y) / n)
        
        # Handle zero variance
        if std_x == 0 or std_y == 0:
            return 1.0 if std_x == std_y else 0.0
        
        correlation = covariance / (std_x * std_y)
        
        # Clamp to [-1, 1] due to floating point errors
        return max(-1.0, min(1.0, correlation))
    
    def _state_to_binary(self, state: Any) -> bool:
        """Convert state to binary (True/False)."""
        if isinstance(state, bool):
            return state
        if isinstance(state, (int, float)):
            return state > 0
        if isinstance(state, str):
            return state.lower() in ('approve', 'accept', 'pass', 'true', '1', 'yes')
        return bool(state)
    
    def _mutual_information(self, states_a: Tuple[Any, ...], states_b: Tuple[Any, ...]) -> float:
        """Compute mutual information in bits."""
        if len(states_a) != len(states_b) or len(states_a) < 2:
            return 0.0
        
        n = len(states_a)
        
        # Compute joint and marginal probabilities
        joint_counts = Counter(zip(states_a, states_b))
        counts_a = Counter(states_a)
        counts_b = Counter(states_b)
        
        mi = 0.0
        for (a, b), joint_count in joint_counts.items():
            p_joint = joint_count / n
            p_a = counts_a[a] / n
            p_b = counts_b[b] / n
            
            if p_joint > 0 and p_a > 0 and p_b > 0:
                mi += p_joint * math.log2(p_joint / (p_a * p_b))
        
        return max(0.0, mi)  # Ensure non-negative

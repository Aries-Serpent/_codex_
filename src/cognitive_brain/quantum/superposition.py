"""
Superposition Engine - Parallel Decision Path Exploration

Implements quantum-inspired superposition for evaluating multiple decision
paths in parallel, then collapsing to the optimal choice based on weighted
probabilities.
"""

import math
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import List, Dict, Any, Callable, Optional
from functools import wraps

from cognitive_brain.quantum.config import QuantumConfig
from cognitive_brain.quantum.base import QuantumFeature, QuantumState
from cognitive_brain.quantum.coherence_monitor import CoherenceMonitor


@dataclass
class Decision:
    """
    Represents a decision option in the superposition.
    
    Attributes:
        id: Unique identifier
        name: Human-readable name
        evaluation_fn: Function to evaluate this decision's quality
        metadata: Additional decision metadata
    """
    
    id: str
    name: str
    evaluation_fn: Callable[[], float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def evaluate(self) -> float:
        """
        Evaluate this decision's quality score.
        
        Returns:
            Quality score (higher is better)
        """
        return self.evaluation_fn()


@dataclass
class SuperpositionState:
    """
    Quantum superposition state: |Ψ⟩ = Σᵢ αᵢ|decision_i⟩
    
    Represents multiple decision paths existing simultaneously until
    wave function collapse selects the optimal path.
    
    Attributes:
        decisions: List of decision options
        amplitudes: Probability amplitudes for each decision
        probabilities: Squared amplitudes (|αᵢ|²)
        coherence: Measure of superposition quality
        evaluated: Whether parallel evaluation has been performed
    """
    
    decisions: List[Decision]
    amplitudes: List[float] = field(default_factory=list)
    probabilities: List[float] = field(default_factory=list)
    coherence: float = 1.0
    evaluated: bool = False
    
    def __post_init__(self):
        """Initialize amplitudes with equal weights."""
        if not self.amplitudes:
            n = len(self.decisions)
            if n == 0:
                raise ValueError("Cannot create superposition with zero decisions")
            
            # Equal superposition: αᵢ = 1/√n
            amplitude = 1.0 / math.sqrt(n)
            self.amplitudes = [amplitude] * n
    
    def get_decision_by_id(self, decision_id: str) -> Optional[Decision]:
        """Get decision by ID."""
        for decision in self.decisions:
            if decision.id == decision_id:
                return decision
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'num_decisions': len(self.decisions),
            'amplitudes': self.amplitudes,
            'probabilities': self.probabilities,
            'coherence': self.coherence,
            'evaluated': self.evaluated,
            'decision_ids': [d.id for d in self.decisions],
        }


class SuperpositionEngine:
    """
    Quantum-inspired parallel decision evaluation engine.
    
    Evaluates multiple decision paths simultaneously using thread-based
    parallelism, then collapses the superposition to select the optimal
    decision based on weighted probabilities.
    
    Example:
        >>> engine = SuperpositionEngine(config)
        >>> 
        >>> # Define decision options
        >>> decisions = [
        ...     Decision('D1', 'Approve', lambda: 0.9),
        ...     Decision('D2', 'Reject', lambda: 0.3),
        ...     Decision('D3', 'Review', lambda: 0.7)
        ... ]
        >>> 
        >>> # Create superposition and evaluate
        >>> state = engine.create_superposition(decisions)
        >>> probs = engine.evaluate_parallel(state)
        >>> best = engine.collapse(state)
        >>> print(f"Best decision: {best.name}")
    """
    
    def __init__(
        self,
        config: QuantumConfig,
        monitor: Optional[CoherenceMonitor] = None,
        max_workers: Optional[int] = None
    ):
        """
        Initialize superposition engine.
        
        Args:
            config: Quantum configuration
            monitor: Optional coherence monitor
            max_workers: Maximum parallel workers (default: # of decisions)
        """
        self.config = config
        self.monitor = monitor
        self.max_workers = max_workers
        
        self._evaluation_times: List[float] = []
    
    def create_superposition(self, decisions: List[Decision]) -> SuperpositionState:
        """
        Create quantum superposition of decision paths.
        
        Args:
            decisions: List of decision options
            
        Returns:
            SuperpositionState with equal amplitude weights
            
        Raises:
            ValueError: If decisions list is empty
        """
        if not decisions:
            raise ValueError("Cannot create superposition with empty decisions list")
        
        state = SuperpositionState(decisions=decisions)
        
        # Record coherence if monitor available
        if self.monitor:
            self.monitor.record_metric(
                feature='superposition',
                metric_name='coherence',
                metric_value=state.coherence,
                metadata={
                    'num_decisions': len(decisions),
                    'operation': 'create'
                }
            )
        
        return state
    
    def evaluate_parallel(self, state: SuperpositionState) -> List[float]:
        """
        Evaluate all decision paths in parallel.
        
        Uses ThreadPoolExecutor to execute evaluation functions simultaneously,
        then normalizes scores to probability distribution.
        
        Args:
            state: SuperpositionState to evaluate
            
        Returns:
            List of probabilities (normalized scores)
        """
        start_time = time.time()
        
        # Determine number of workers
        num_workers = self.max_workers or len(state.decisions)
        num_workers = min(num_workers, len(state.decisions))
        
        # Parallel evaluation
        scores = []
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            # Submit all evaluation tasks
            future_to_idx = {
                executor.submit(decision.evaluate): idx
                for idx, decision in enumerate(state.decisions)
            }
            
            # Collect results in order
            results = [None] * len(state.decisions)
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    score = future.result()
                    results[idx] = max(score, 0.0)  # Ensure non-negative
                except Exception as e:
                    # Fallback to zero score on error
                    results[idx] = 0.0
            
            scores = results
        
        # Normalize to probability distribution: P_i = score_i / Σ scores
        total = sum(scores)
        if total == 0:
            # Equal probabilities if all scores are zero
            probabilities = [1.0 / len(scores)] * len(scores)
        else:
            probabilities = [s / total for s in scores]
        
        # Update state
        state.probabilities = probabilities
        state.evaluated = True
        
        # Calculate coherence based on entropy
        state.coherence = self._calculate_coherence(probabilities)
        
        # Record metrics
        elapsed = time.time() - start_time
        self._evaluation_times.append(elapsed)
        
        if self.monitor:
            self.monitor.record_metric(
                feature='superposition',
                metric_name='evaluation_time',
                metric_value=elapsed,
                metadata={
                    'num_decisions': len(state.decisions),
                    'num_workers': num_workers
                }
            )
            
            self.monitor.record_metric(
                feature='superposition',
                metric_name='coherence',
                metric_value=state.coherence,
                metadata={'operation': 'evaluate'}
            )
        
        return probabilities
    
    def collapse(self, state: SuperpositionState) -> Decision:
        """
        Collapse superposition to single optimal decision.
        
        Wave function collapse: select decision with highest probability |αᵢ|².
        
        Args:
            state: SuperpositionState to collapse
            
        Returns:
            Decision with highest probability
            
        Raises:
            ValueError: If state not yet evaluated
        """
        if not state.evaluated:
            # Auto-evaluate if needed
            self.evaluate_parallel(state)
        
        # Check coherence threshold
        if state.coherence < 0.3:
            # Coherence too low - fallback might be needed
            if self.monitor:
                self.monitor.record_metric(
                    feature='superposition',
                    metric_name='low_coherence_collapse',
                    metric_value=state.coherence,
                    metadata={'threshold': 0.3}
                )
        
        # Collapse to highest probability
        best_idx = state.probabilities.index(max(state.probabilities))
        best_decision = state.decisions[best_idx]
        
        # Record collapse
        if self.monitor:
            self.monitor.record_metric(
                feature='superposition',
                metric_name='collapse',
                metric_value=state.probabilities[best_idx],
                metadata={
                    'decision_id': best_decision.id,
                    'decision_name': best_decision.name,
                    'coherence': state.coherence
                }
            )
        
        return best_decision
    
    def get_coherence(self, state: SuperpositionState) -> float:
        """
        Get coherence of superposition state.
        
        Args:
            state: SuperpositionState to check
            
        Returns:
            Coherence value (0.0 to 1.0)
        """
        if not state.evaluated:
            # Calculate based on amplitudes
            return self._calculate_coherence([a ** 2 for a in state.amplitudes])
        
        return state.coherence
    
    def _calculate_coherence(self, probabilities: List[float]) -> float:
        """
        Calculate coherence from probability distribution.
        
        Uses normalized Shannon entropy as coherence measure:
        - High entropy (uniform distribution) = low coherence
        - Low entropy (peaked distribution) = high coherence
        
        Args:
            probabilities: Probability distribution
            
        Returns:
            Coherence value (0.0 to 1.0)
        """
        if not probabilities or sum(probabilities) == 0:
            return 0.0
        
        # Shannon entropy: H = -Σ P_i log(P_i)
        entropy = 0.0
        for p in probabilities:
            if p > 0:
                entropy -= p * math.log(p)
        
        # Maximum entropy for uniform distribution
        max_entropy = math.log(len(probabilities)) if len(probabilities) > 1 else 1.0
        
        # Normalized entropy: 0 (peaked) to 1 (uniform)
        if max_entropy > 0:
            normalized_entropy = entropy / max_entropy
        else:
            normalized_entropy = 0.0
        
        # Coherence is inverse of entropy
        coherence = 1.0 - normalized_entropy
        
        return max(0.0, min(1.0, coherence))
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Get engine performance metrics.
        
        Returns:
            Dictionary with timing statistics
        """
        if not self._evaluation_times:
            return {
                'avg_time': 0.0,
                'min_time': 0.0,
                'max_time': 0.0,
                'total_evaluations': 0
            }
        
        return {
            'avg_time': sum(self._evaluation_times) / len(self._evaluation_times),
            'min_time': min(self._evaluation_times),
            'max_time': max(self._evaluation_times),
            'total_evaluations': len(self._evaluation_times)
        }


def quantum_superposition(
    enabled_config_attr: str = 'superposition',
    fallback_on_low_coherence: bool = True,
    coherence_threshold: float = 0.3
):
    """
    Decorator for quantum superposition decision-making.
    
    Wraps a function to use superposition engine if feature is enabled,
    otherwise falls back to classical execution.
    
    Args:
        enabled_config_attr: Config attribute to check (default: 'superposition')
        fallback_on_low_coherence: Whether to fallback if coherence < threshold
        coherence_threshold: Minimum coherence for quantum execution
    
    Example:
        >>> @quantum_superposition()
        ... def make_decision(self, options):
        ...     # Classical implementation
        ...     return max(options, key=lambda o: o.score)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if quantum feature is enabled
            # This is a placeholder - real implementation would check config
            # from context or instance
            
            # For now, just execute the original function
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator

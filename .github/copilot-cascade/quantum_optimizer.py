"""
Quantum-Inspired Optimization for Cascade Delegation.

Leverages _codex_ quantum physics patterns from agents/advanced_physics_calculators.py
for optimizing task scheduling, detecting entanglement, and quantum tunneling.
"""

import logging
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add agents to path for imports
agents_path = Path(__file__).resolve().parents[2] / "agents"
if str(agents_path) not in sys.path:
    sys.path.insert(0, str(agents_path))

# Import from _codex_ physics calculators
try:
    from advanced_physics_calculators import NUMPY_AVAILABLE, ChaoticAttractor

    PHYSICS_AVAILABLE = True
except ImportError:
    PHYSICS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Physics calculators not available, using fallback implementations")

# Import numpy if available
if PHYSICS_AVAILABLE and NUMPY_AVAILABLE:
    import numpy as np
else:
    # Fallback implementations
    import random as _random

    class np:  # type: ignore
        @staticmethod
        def array(x):
            return x

        @staticmethod
        def exp(x):
            if isinstance(x, (list, tuple)):
                return [math.exp(i) for i in x]
            return math.exp(x)

        class random:
            @staticmethod
            def random():
                return _random.random()


logger = logging.getLogger(__name__)


@dataclass
class QuantumState:
    """Represents a quantum state for task optimization."""

    amplitude: complex
    phase: float
    entangled_tasks: List[str]
    probability: float = 0.0

    def __post_init__(self):
        """Calculate probability from amplitude."""
        self.probability = abs(self.amplitude) ** 2


class QuantumOptimizer:
    """
    Uses quantum principles for cascade optimization.

    Integrates with _codex_ physics patterns for:
    - Superposition: Parallel task exploration
    - Entanglement: Dependency detection
    - Tunneling: Bypass barriers
    - Chaos: Escape local optima
    """

    def __init__(self, superposition_threshold: float = 0.7):
        """
        Initialize quantum optimizer.

        Args:
            superposition_threshold: Minimum probability for superposition states
        """
        self.superposition_threshold = superposition_threshold
        self.entanglement_map: Dict[str, List[str]] = {}
        self.chaos_attractor: Optional[Any] = None

        # Initialize chaos attractor if physics available
        if PHYSICS_AVAILABLE:
            try:
                self.chaos_attractor = ChaoticAttractor(
                    attractor_type="lorenz", initial_state=(1.0, 1.0, 1.0)
                )
                logger.info("Quantum optimizer initialized with Lorenz attractor")
            except Exception as e:
                logger.warning(f"Failed to initialize chaos attractor: {e}")

    def create_superposition(self, tasks: List[Any]) -> List[Tuple[Any, float]]:
        """
        Create superposition of tasks for parallel execution.

        Uses quantum probability amplitudes to determine optimal task scheduling.

        Args:
            tasks: List of DelegationTask objects

        Returns:
            List of (task, probability) tuples sorted by execution priority
        """
        if not tasks:
            return []

        task_states = []

        for task in tasks:
            # Calculate quantum complexity
            complexity = self._calculate_quantum_complexity(task)

            # Create quantum amplitude with phase
            # Lower complexity = higher amplitude = higher priority
            amplitude = complex(
                math.cos(complexity * math.pi / 4), math.sin(complexity * math.pi / 4)
            )

            # Calculate probability from amplitude
            probability = abs(amplitude) ** 2

            task_states.append((task, probability))

        # Normalize probabilities
        total_prob = sum(p for _, p in task_states)
        if total_prob > 0:
            normalized = [(t, p / total_prob) for t, p in task_states]
        else:
            # Fallback to uniform distribution
            uniform_prob = 1.0 / len(tasks)
            normalized = [(t, uniform_prob) for t, _ in task_states]

        # Sort by probability (highest first)
        sorted_states = sorted(normalized, key=lambda x: x[1], reverse=True)

        logger.debug(f"Created superposition of {len(tasks)} tasks")
        return sorted_states

    def detect_entanglement(self, task1: Any, task2: Any) -> float:
        """
        Detect quantum entanglement between tasks.

        Entangled tasks share context and should be executed with correlation.

        Args:
            task1: First task
            task2: Second task

        Returns:
            Entanglement strength (0.0 to 1.0)
        """
        # Extract contexts
        ctx1 = getattr(task1, "context", {})
        ctx2 = getattr(task2, "context", {})

        if not ctx1 or not ctx2:
            return 0.0

        # Find shared keys
        shared_keys = set(ctx1.keys()) & set(ctx2.keys())

        if not shared_keys:
            return 0.0

        # Calculate entanglement based on shared information
        entanglement = 0.0

        for key in shared_keys:
            val1 = ctx1[key]
            val2 = ctx2[key]

            # String similarity
            if isinstance(val1, str) and isinstance(val2, str):
                similarity = self._string_similarity(val1, val2)
                entanglement += similarity

            # Exact match for other types
            elif val1 == val2:
                entanglement += 1.0

        # Normalize by number of shared keys
        entanglement_strength = min(entanglement / len(shared_keys), 1.0)

        # Record entanglement in map
        task1_id = getattr(task1, "task_id", str(id(task1)))
        task2_id = getattr(task2, "task_id", str(id(task2)))

        if entanglement_strength > 0.5:  # Strong entanglement threshold
            if task1_id not in self.entanglement_map:
                self.entanglement_map[task1_id] = []
            self.entanglement_map[task1_id].append(task2_id)

        return entanglement_strength

    def quantum_tunnel(self, blocked_task: Any) -> Optional[Any]:
        """
        Use quantum tunneling to bypass blocked tasks.

        Creates alternative task configuration with reduced requirements.

        Args:
            blocked_task: Task that is blocked or failing

        Returns:
            Tunneled task variant, or None if tunneling fails
        """
        # Assess barrier height
        barrier_height = self._assess_barrier(blocked_task)

        # Calculate tunneling probability using quantum mechanics
        # P = exp(-2 * barrier_height)
        tunnel_prob = math.exp(-2 * barrier_height)

        logger.debug(f"Tunneling probability: {tunnel_prob:.3f} (barrier: {barrier_height:.3f})")

        # Attempt tunneling
        if np.random.random() < tunnel_prob:
            # Create tunneled version
            try:
                # Reduce context complexity
                reduced_context = self._reduce_context(getattr(blocked_task, "context", {}))

                # Create new task with reduced requirements
                task_type = getattr(blocked_task, "task_type", "generic")
                task_id = getattr(blocked_task, "task_id", "unknown")

                # Build tunneled task (simplified representation)
                tunneled = type(
                    "TunneledTask",
                    (),
                    {
                        "task_id": f"{task_id}_tunneled",
                        "task_type": task_type,
                        "context": reduced_context,
                        "priority": getattr(blocked_task, "priority", 1) + 1,
                        "tunneled": True,
                    },
                )()

                logger.info(f"Quantum tunneling successful for {task_id}")
                return tunneled

            except Exception as e:
                logger.error(f"Tunneling failed: {e}")
                return None

        return None

    def apply_chaos_exploration(self, current_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply chaotic dynamics for exploration.

        Uses Lorenz attractor from _codex_ physics calculators to escape local optima.

        Args:
            current_state: Current optimization state

        Returns:
            Perturbed state for exploration
        """
        if not PHYSICS_AVAILABLE or self.chaos_attractor is None:
            # Fallback: simple random perturbation
            return {**current_state, "exploration_factor": 0.1}

        try:
            # Evolve chaos attractor
            dt = 0.01
            for _ in range(10):  # 10 steps of evolution
                self.chaos_attractor.evolve(dt)

            # Extract current chaotic state
            state_vector = self.chaos_attractor.state

            # Use chaotic values to perturb optimization
            chaos_factor = abs(float(state_vector[0])) / 20.0  # Normalize Lorenz x-coordinate

            perturbed_state = {
                **current_state,
                "exploration_factor": min(chaos_factor, 0.5),
                "chaos_x": float(state_vector[0]),
                "chaos_y": float(state_vector[1]),
                "chaos_z": float(state_vector[2]),
            }

            logger.debug(f"Applied chaos exploration: factor={chaos_factor:.3f}")
            return perturbed_state

        except Exception as e:
            logger.error(f"Chaos exploration failed: {e}")
            return current_state

    def _calculate_quantum_complexity(self, task: Any) -> float:
        """
        Calculate quantum complexity metric for task.

        Lower complexity = higher priority for execution.
        """
        # Base complexity from context size
        context = getattr(task, "context", {})
        base_complexity = len(str(context)) / 1000.0

        # Task type weights
        task_type = str(getattr(task, "task_type", "generic")).lower()

        type_weights = {
            "security_scan": 2.0,
            "refactor": 1.5,
            "review": 1.0,
            "code_review": 1.0,
            "documentation": 0.5,
            "test": 0.7,
            "test_generation": 0.7,
        }

        weight = type_weights.get(task_type, 1.0)

        return base_complexity * weight

    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity using Jaccard index."""
        if not s1 or not s2:
            return 0.0

        # Tokenize
        set1 = set(s1.lower().split())
        set2 = set(s2.lower().split())

        if not set1 or not set2:
            return 0.0

        # Jaccard similarity
        intersection = set1 & set2
        union = set1 | set2

        return len(intersection) / len(union) if union else 0.0

    def _assess_barrier(self, task: Any) -> float:
        """Assess difficulty barrier for task (0.0 to 5.0)."""
        context = getattr(task, "context", {})
        barriers = 0.0

        # Check for various blocking factors
        if context.get("requires_auth"):
            barriers += 2.0

        if context.get("large_codebase"):
            barriers += 1.5

        if context.get("complex_dependencies"):
            barriers += 1.0

        timeout = getattr(task, "timeout_seconds", 300)
        if timeout < 60:
            barriers += 1.0

        # High priority tasks have lower barriers
        priority = getattr(task, "priority", 2)
        if priority == 1:  # High priority
            barriers *= 0.7

        return min(barriers, 5.0)

    def _reduce_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Reduce context complexity for tunneled task."""
        reduced = {}

        # Keep only essential keys
        essential_keys = [
            "code",
            "error",
            "prompt",
            "language",
            "file_path",
            "description",
            "requirements",
        ]

        for key in essential_keys:
            if key in context:
                value = context[key]

                # Truncate strings
                if isinstance(value, str) and len(value) > 500:
                    reduced[key] = value[:500] + "... [truncated]"
                else:
                    reduced[key] = value

        return reduced

    def get_statistics(self) -> Dict[str, Any]:
        """Get quantum optimizer statistics."""
        return {
            "superposition_threshold": self.superposition_threshold,
            "entangled_pairs": len(self.entanglement_map),
            "chaos_attractor_available": self.chaos_attractor is not None,
            "physics_integration": PHYSICS_AVAILABLE,
            "entanglement_map_size": sum(len(v) for v in self.entanglement_map.values()),
        }


# Singleton instance
_quantum_optimizer_instance: Optional[QuantumOptimizer] = None


def get_quantum_optimizer() -> QuantumOptimizer:
    """Get or create quantum optimizer singleton."""
    global _quantum_optimizer_instance
    if _quantum_optimizer_instance is None:
        _quantum_optimizer_instance = QuantumOptimizer()
    return _quantum_optimizer_instance

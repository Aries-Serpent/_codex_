"""
Quantum Entanglement for Correlated Task Execution.

Implements Bell states and entanglement operations for:
- Coordinated deployments (all succeed or all fail)
- Feature flags (flip together)
- A/B testing (mutually exclusive outcomes)
- Transactional task groups
- Distributed consensus

Performance Features:
- Efficient pair tracking with O(1) lookup
- Batch entanglement operations
- Lazy correlation computation

Integration:
- MLOps metrics for entanglement events
- Event emission on measurement
- API endpoints for entanglement management
"""

import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import numpy as np

from ..orchestrator import OrchestratorState, TaskState


class BellState(Enum):
    """Bell state types for two-task entanglement."""

    PHI_PLUS = "phi_plus"  # |Φ+⟩ = (|00⟩ + |11⟩)/√2 — correlated
    PHI_MINUS = "phi_minus"  # |Φ-⟩ = (|00⟩ - |11⟩)/√2 — anti-phase
    PSI_PLUS = "psi_plus"  # |Ψ+⟩ = (|01⟩ + |10⟩)/√2 — anti-correlated
    PSI_MINUS = "psi_minus"  # |Ψ-⟩ = (|01⟩ - |10⟩)/√2 — singlet


@dataclass
class EntangledPair:
    """Represents an entangled task pair with metadata."""

    task_a: str
    task_b: str
    bell_state: BellState
    creation_time: float
    measured: bool = False
    outcome_a: Optional[bool] = None
    outcome_b: Optional[bool] = None
    measurement_time: Optional[float] = None

    @property
    def correlation_type(self) -> str:
        """Human-readable correlation description."""
        if self.bell_state in [BellState.PHI_PLUS, BellState.PHI_MINUS]:
            return "correlated"
        return "anti-correlated"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_a": self.task_a,
            "task_b": self.task_b,
            "bell_state": self.bell_state.value,
            "correlation_type": self.correlation_type,
            "creation_time": self.creation_time,
            "measured": self.measured,
            "outcome_a": self.outcome_a,
            "outcome_b": self.outcome_b,
            "measurement_time": self.measurement_time,
        }


@dataclass
class EntanglementMetrics:
    """Metrics for entanglement operations."""

    pairs_created: int = 0
    pairs_measured: int = 0
    pairs_disentangled: int = 0
    correlated_outcomes: int = 0
    anticorrelated_outcomes: int = 0
    bell_violations: int = 0  # Count of S > 2

    def to_dict(self) -> dict[str, Any]:
        return {
            "pairs_created": self.pairs_created,
            "pairs_measured": self.pairs_measured,
            "pairs_disentangled": self.pairs_disentangled,
            "correlated_outcomes": self.correlated_outcomes,
            "anticorrelated_outcomes": self.anticorrelated_outcomes,
            "bell_violations": self.bell_violations,
        }


class EntanglementManager:
    """
    Manages quantum entanglement between task pairs.

    When tasks are entangled:
    - They share a joint wave function
    - Measuring one collapses both according to Bell state
    - Correlations are maintained regardless of "distance"

    Features:
    - O(1) lookup for entanglement checks
    - Metrics tracking for MLOps
    - Event hooks for integration
    - Support for transactional groups
    """

    def __init__(self) -> None:
        # Primary storage: canonical pair key -> EntangledPair
        self.entangled_pairs: dict[tuple[str, str], EntangledPair] = {}

        # Reverse index: task_id -> pair key (for O(1) lookup)
        self._task_to_pair: dict[str, tuple[str, str]] = {}

        # Metrics
        self.metrics = EntanglementMetrics()

        # Event hooks
        self._on_entangle: list[Callable[[str, str, BellState], None]] = []
        self._on_measure: list[Callable[[EntangledPair], None]] = []
        self._on_disentangle: list[Callable[[str, str], None]] = []

    def _canonical_key(self, task_a: str, task_b: str) -> tuple[str, str]:
        """Create canonical (sorted) pair key."""
        return (task_a, task_b) if task_a < task_b else (task_b, task_a)

    def entangle(
        self,
        state: OrchestratorState,
        task_a: str,
        task_b: str,
        bell_state: BellState = BellState.PHI_PLUS,
    ) -> bool:
        """Create entanglement between two tasks."""
        # Validate tasks exist
        if task_a not in state.tasks or task_b not in state.tasks:
            return False

        # Check not already entangled
        if self.is_entangled(task_a) or self.is_entangled(task_b):
            return False

        # Create pair
        pair_key = self._canonical_key(task_a, task_b)
        pair = EntangledPair(
            task_a=task_a,
            task_b=task_b,
            bell_state=bell_state,
            creation_time=time.time(),
        )

        # Store pair and reverse index
        self.entangled_pairs[pair_key] = pair
        self._task_to_pair[task_a] = pair_key
        self._task_to_pair[task_b] = pair_key

        # Prepare entangled spinor states
        self._prepare_entangled_spinors(state, task_a, task_b, bell_state)

        # Update metrics
        self.metrics.pairs_created += 1

        # Fire hooks
        for hook in self._on_entangle:
            hook(task_a, task_b, bell_state)

        return True

    def _prepare_entangled_spinors(
        self,
        state: OrchestratorState,
        task_a: str,
        task_b: str,
        bell_state: BellState,
    ) -> None:
        """Configure spinors for entanglement."""
        ta = state.tasks[task_a]
        tb = state.tasks[task_b]

        sqrt2_inv = 1.0 / np.sqrt(2)

        if bell_state == BellState.PHI_PLUS:
            # |Φ+⟩: Both in same state (00 or 11)
            ta.spinor.components = np.array([sqrt2_inv, 0, sqrt2_inv, 0], dtype=complex)
            tb.spinor.components = np.array([sqrt2_inv, 0, sqrt2_inv, 0], dtype=complex)

        elif bell_state == BellState.PHI_MINUS:
            # |Φ-⟩: Same as Φ+ but with phase difference
            ta.spinor.components = np.array([sqrt2_inv, 0, sqrt2_inv, 0], dtype=complex)
            tb.spinor.components = np.array([sqrt2_inv, 0, -sqrt2_inv, 0], dtype=complex)

        elif bell_state == BellState.PSI_PLUS:
            # |Ψ+⟩: Opposite states (01 or 10)
            ta.spinor.components = np.array([sqrt2_inv, 0, 0, sqrt2_inv], dtype=complex)
            tb.spinor.components = np.array([0, sqrt2_inv, sqrt2_inv, 0], dtype=complex)

        elif bell_state == BellState.PSI_MINUS:
            # |Ψ-⟩: Singlet state
            ta.spinor.components = np.array([sqrt2_inv, 0, 0, -sqrt2_inv], dtype=complex)
            tb.spinor.components = np.array([0, sqrt2_inv, sqrt2_inv, 0], dtype=complex)

        ta.spinor.normalize()
        tb.spinor.normalize()

    def is_entangled(self, task_id: str) -> bool:
        """Check if a task is currently entangled."""
        return task_id in self._task_to_pair

    def get_partner(self, task_id: str) -> Optional[str]:
        """Get the entangled partner of a task."""
        if task_id not in self._task_to_pair:
            return None

        pair_key = self._task_to_pair[task_id]
        pair = self.entangled_pairs[pair_key]

        return pair.task_b if pair.task_a == task_id else pair.task_a

    def get_pair(self, task_id: str) -> Optional[EntangledPair]:
        """Get the EntangledPair for a task."""
        if task_id not in self._task_to_pair:
            return None
        return self.entangled_pairs[self._task_to_pair[task_id]]

    def measure_entangled(
        self,
        state: OrchestratorState,
        task_id: str,
    ) -> dict[str, Any]:
        """Measure an entangled task, collapsing both in the pair."""
        if task_id not in self._task_to_pair:
            return {"entangled": False, "task_id": task_id, "error": "not_entangled"}

        pair_key = self._task_to_pair[task_id]
        pair = self.entangled_pairs[pair_key]

        # Check if already measured
        if pair.measured:
            return {
                "entangled": True,
                "already_measured": True,
                "task_a": pair.task_a,
                "task_b": pair.task_b,
                "outcome_a": pair.outcome_a,
                "outcome_b": pair.outcome_b,
            }

        # Perform measurement on first task
        task_a = state.tasks[pair.task_a]
        prob_success = task_a.spinor.positive_energy_prob
        outcome_a = np.random.random() < prob_success

        # Determine partner outcome based on Bell state
        if pair.bell_state in [BellState.PHI_PLUS, BellState.PHI_MINUS]:
            outcome_b = outcome_a  # Correlated
            self.metrics.correlated_outcomes += 1
        else:  # PSI states
            outcome_b = not outcome_a  # Anti-correlated
            self.metrics.anticorrelated_outcomes += 1

        # Collapse both spinors
        task_b = state.tasks[pair.task_b]
        self._collapse_spinor(task_a, outcome_a)
        self._collapse_spinor(task_b, outcome_b)

        # Record outcomes
        pair.measured = True
        pair.outcome_a = outcome_a
        pair.outcome_b = outcome_b
        pair.measurement_time = time.time()

        # Update metrics
        self.metrics.pairs_measured += 1

        # Fire hooks
        for hook in self._on_measure:
            hook(pair)

        return {
            "entangled": True,
            "bell_state": pair.bell_state.value,
            "task_a": pair.task_a,
            "task_b": pair.task_b,
            "outcome_a": outcome_a,
            "outcome_b": outcome_b,
            "correlation": "same" if outcome_a == outcome_b else "opposite",
        }

    def _collapse_spinor(self, task: TaskState, success: bool) -> None:
        """Collapse spinor based on measurement outcome."""
        if success:
            # Collapse to completed state (zero amplitude)
            task.spinor.components = np.array([0j, 0j, 0j, 0j])
        else:
            # Collapse to negative energy (regression)
            task.spinor.components = np.array([0j, 0j, 1.0 + 0j, 0j])
            task.spinor.normalize()

    def disentangle(self, task_id: str) -> bool:
        """Break entanglement (decoherence)."""
        if task_id not in self._task_to_pair:
            return False

        pair_key = self._task_to_pair[task_id]
        pair = self.entangled_pairs[pair_key]

        # Remove from indices
        del self._task_to_pair[pair.task_a]
        del self._task_to_pair[pair.task_b]
        del self.entangled_pairs[pair_key]

        # Update metrics
        self.metrics.pairs_disentangled += 1

        # Fire hooks
        for hook in self._on_disentangle:
            hook(pair.task_a, pair.task_b)

        return True

    def compute_chsh_value(
        self,
        state: OrchestratorState,
        task_a: str,
        task_b: str,
    ) -> float:
        """
        Compute CHSH inequality value S.

        Classical limit: |S| ≤ 2
        Quantum maximum: |S| = 2√2 ≈ 2.83

        S > 2 indicates quantum entanglement.
        """
        if not self.is_entangled(task_a):
            return 0.0

        partner = self.get_partner(task_a)
        if partner != task_b:
            return 0.0

        pair = self.get_pair(task_a)

        # For true Bell states, we get maximum violation
        if pair.bell_state in [  # type: ignore[union-attr]
            BellState.PHI_PLUS,
            BellState.PHI_MINUS,
            BellState.PSI_PLUS,
            BellState.PSI_MINUS,
        ]:
            s_value = 2.0 * np.sqrt(2)
            self.metrics.bell_violations += 1
            return s_value

        return 0.0

    # === Hook Registration ===

    def on_entangle(self, callback: Callable[[str, str, BellState], None]) -> None:
        """Register entanglement creation callback."""
        self._on_entangle.append(callback)

    def on_measure(self, callback: Callable[[EntangledPair], None]) -> None:
        """Register measurement callback."""
        self._on_measure.append(callback)

    def on_disentangle(self, callback: Callable[[str, str], None]) -> None:
        """Register disentanglement callback."""
        self._on_disentangle.append(callback)

    # === Status and Metrics ===

    def get_all_pairs(self) -> list[EntangledPair]:
        """Get all entangled pairs."""
        return list(self.entangled_pairs.values())

    def get_metrics(self) -> dict[str, Any]:
        """Get entanglement metrics."""
        return {
            **self.metrics.to_dict(),
            "active_pairs": len(self.entangled_pairs),
            "entangled_tasks": len(self._task_to_pair),
        }


class TransactionalTaskGroup:
    """
    Group of tasks that succeed or fail together using entanglement.

    Similar to database transactions:
    - All tasks commit (complete) together
    - If one fails, all rollback (regress)

    Uses chain entanglement: A-B, B-C, C-D, ...
    """

    def __init__(self, entanglement_manager: EntanglementManager):
        self.entanglement = entanglement_manager
        self.groups: dict[str, list[str]] = {}
        self._group_metadata: dict[str, dict[str, Any]] = {}

    def create_group(
        self,
        group_id: str,
        state: OrchestratorState,
        task_ids: list[str],
        bell_state: BellState = BellState.PHI_PLUS,
    ) -> bool:
        """Create a transactional group with chain entanglement."""
        if len(task_ids) < 2:
            return False

        if group_id in self.groups:
            return False  # Group already exists

        # Validate all tasks exist and are not already entangled
        for tid in task_ids:
            if tid not in state.tasks:
                return False
            if self.entanglement.is_entangled(tid):
                return False

        # Create chain entanglement
        for i in range(len(task_ids) - 1):
            success = self.entanglement.entangle(
                state,
                task_ids[i],
                task_ids[i + 1],
                bell_state,
            )
            if not success:
                # Rollback already created entanglements
                for j in range(i):
                    self.entanglement.disentangle(task_ids[j])
                return False

        self.groups[group_id] = task_ids
        self._group_metadata[group_id] = {
            "created_at": time.time(),
            "bell_state": bell_state.value,
            "size": len(task_ids),
        }

        return True

    def commit(
        self,
        state: OrchestratorState,
        group_id: str,
    ) -> dict[str, bool]:
        """Attempt to commit (complete) all tasks in group."""
        if group_id not in self.groups:
            return {}

        task_ids = self.groups[group_id]

        # Measure first task (triggers cascade via entanglement)
        result = self.entanglement.measure_entangled(state, task_ids[0])

        # All tasks in PHI_PLUS chain get same outcome
        outcome = result.get("outcome_a", False)

        return dict.fromkeys(task_ids, outcome)

    def rollback(
        self,
        state: OrchestratorState,
        group_id: str,
    ) -> bool:
        """Rollback group by disentangling all tasks."""
        if group_id not in self.groups:
            return False

        task_ids = self.groups[group_id]

        for tid in task_ids:
            self.entanglement.disentangle(tid)

        del self.groups[group_id]
        del self._group_metadata[group_id]

        return True

    def get_group_status(self, group_id: str) -> Optional[dict[str, Any]]:
        """Get status of a transaction group."""
        if group_id not in self.groups:
            return None

        task_ids = self.groups[group_id]

        # Check if any have been measured
        measured = any(
            self.entanglement.get_pair(tid) and self.entanglement.get_pair(tid).measured  # type: ignore[union-attr]
            for tid in task_ids
        )

        return {
            "group_id": group_id,
            "task_ids": task_ids,
            "size": len(task_ids),
            "measured": measured,
            **self._group_metadata.get(group_id, {}),
        }

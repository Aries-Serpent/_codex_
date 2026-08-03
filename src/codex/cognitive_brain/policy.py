"""Physics-Inspired Deterministic Reasoning Policy.

Scores candidate action plans along five conceptual dimensions borrowed from
physics and information theory:

    Path 🛤️   — execution-trajectory efficiency (shortest-plan cost)
    Fields 🔄 — contextual force / constraint weighting
    Patterns 👁️ — known error / behaviour motif recognition
    Redundancy 🔀 — resilience through alternate branches
    Balance ⚖️  — tradeoff equilibrium (speed vs certainty vs risk)

All scoring is fully deterministic under a fixed seed, enabling reproducible
CI validation and A/B comparisons.

Usage::

    policy = DeterministicPolicy(seed=42)
    best = policy.select(candidates, context)
"""

from __future__ import annotations

import hashlib
import logging
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class PolicyContext:
    """Runtime context fed into the scoring model."""

    task_type: str  # e.g. "repo_introspection", "ui_interaction", "web_validation"
    confidence: float  # 0.0 – 1.0 confidence in task intent
    risk_level: float  # 0.0 (safe) – 1.0 (high risk)
    dependency_count: int  # number of upstream dependencies
    time_budget_ms: float  # allowed wall-clock budget in milliseconds
    known_patterns: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CandidatePlan:
    """A candidate action plan to be scored by the policy."""

    plan_id: str
    description: str
    estimated_steps: int
    estimated_latency_ms: float
    fallback_branches: int  # number of fallback options available
    certainty: float  # 0.0 – 1.0
    risk: float  # 0.0 – 1.0
    matched_patterns: List[str] = field(default_factory=list)
    constraints_satisfied: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ScoredPlan:
    """A :class:`CandidatePlan` annotated with its per-dimension scores."""

    plan: CandidatePlan
    path_score: float = 0.0
    fields_score: float = 0.0
    patterns_score: float = 0.0
    redundancy_score: float = 0.0
    balance_score: float = 0.0
    total_score: float = 0.0
    rank: int = 0

    def score_breakdown(self) -> Dict[str, float]:
        """Return a dict of dimension → score for telemetry/logging."""
        return {
            "path": round(self.path_score, 4),
            "fields": round(self.fields_score, 4),
            "patterns": round(self.patterns_score, 4),
            "redundancy": round(self.redundancy_score, 4),
            "balance": round(self.balance_score, 4),
            "total": round(self.total_score, 4),
        }


# ---------------------------------------------------------------------------
# Policy implementation
# ---------------------------------------------------------------------------


class DeterministicPolicy:
    """Score and rank candidate plans using physics-inspired dimensions.

    All floating-point arithmetic uses only pure-Python ``math`` functions so
    results are portable and reproducible across Python versions.

    Parameters
    ----------
    seed:
        Integer seed used when deterministic tie-breaking is needed.  Two
        calls with the same *seed*, *candidates*, and *context* will always
        return the same winner.
    weights:
        Per-dimension weight overrides.  Missing dimensions fall back to the
        built-in defaults.
    """

    _DEFAULT_WEIGHTS: Dict[str, float] = {
        "path": 0.25,
        "fields": 0.20,
        "patterns": 0.20,
        "redundancy": 0.15,
        "balance": 0.20,
    }

    def __init__(
        self,
        seed: int = 42,
        weights: Optional[Dict[str, float]] = None,
    ) -> None:
        self._seed = seed
        self._weights = dict(self._DEFAULT_WEIGHTS)
        if weights:
            self._weights.update(weights)
        self._normalise_weights()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def score(
        self, plan: CandidatePlan, context: PolicyContext
    ) -> ScoredPlan:
        """Compute the five-dimension score for a single *plan* / *context* pair."""
        path = self._score_path(plan, context)
        fields = self._score_fields(plan, context)
        patterns = self._score_patterns(plan, context)
        redundancy = self._score_redundancy(plan, context)
        balance = self._score_balance(plan, context)

        total = (
            path * self._weights["path"]
            + fields * self._weights["fields"]
            + patterns * self._weights["patterns"]
            + redundancy * self._weights["redundancy"]
            + balance * self._weights["balance"]
        )

        return ScoredPlan(
            plan=plan,
            path_score=path,
            fields_score=fields,
            patterns_score=patterns,
            redundancy_score=redundancy,
            balance_score=balance,
            total_score=total,
        )

    def rank(
        self, candidates: Sequence[CandidatePlan], context: PolicyContext
    ) -> List[ScoredPlan]:
        """Score and rank *candidates*, returning highest score first.

        Tie-breaking is deterministic: plans with equal total scores are
        ordered by a hash of (seed, plan_id).
        """
        scored = [self.score(p, context) for p in candidates]
        scored.sort(
            key=lambda s: (
                -round(s.total_score, 6),
                self._tiebreak_key(s.plan.plan_id),
            )
        )
        for i, s in enumerate(scored):
            s.rank = i + 1
        logger.debug(
            "Policy ranking: %s plans, winner=%s score=%.4f",
            len(scored),
            scored[0].plan.plan_id if scored else "—",
            scored[0].total_score if scored else 0.0,
        )
        return scored

    def select(
        self, candidates: Sequence[CandidatePlan], context: PolicyContext
    ) -> Optional[ScoredPlan]:
        """Return the top-ranked plan, or None if *candidates* is empty."""
        ranked = self.rank(candidates, context)
        return ranked[0] if ranked else None

    # ------------------------------------------------------------------
    # Dimension scorers
    # ------------------------------------------------------------------

    def _score_path(self, plan: CandidatePlan, context: PolicyContext) -> float:
        """Path 🛤️ — efficiency of the execution trajectory.

        Shorter plans with lower latency score higher.  Both step-count and
        latency are normalised to [0, 1] using a soft exponential decay so
        that very short plans approach 1.0 and very long plans approach 0.0.
        """
        step_score = math.exp(-0.1 * max(plan.estimated_steps, 1))
        # Normalise latency against the context budget.
        budget = max(context.time_budget_ms, 1.0)
        latency_ratio = min(plan.estimated_latency_ms / budget, 2.0)
        latency_score = math.exp(-latency_ratio)
        return 0.5 * step_score + 0.5 * latency_score

    def _score_fields(self, plan: CandidatePlan, context: PolicyContext) -> float:
        """Fields 🔄 — degree to which contextual constraints are satisfied.

        Each satisfied constraint contributes equally.  If no constraints are
        declared the field score is 0.8 (neutral-positive default).
        """
        if not context.constraints:
            return 0.8
        satisfied = len(
            [c for c in context.constraints if c in plan.constraints_satisfied]
        )
        return satisfied / len(context.constraints)

    def _score_patterns(self, plan: CandidatePlan, context: PolicyContext) -> float:
        """Patterns 👁️ — alignment with known behavioural motifs.

        Plans that match contextually recognised patterns score higher.  The
        score is the Jaccard similarity between the plan's matched patterns and
        the context's known patterns.
        """
        known = set(context.known_patterns)
        matched = set(plan.matched_patterns)
        if not known and not matched:
            return 0.5  # no information → neutral
        if not known:
            return 0.3  # plan has patterns but context has none — slight penalty
        intersection = known & matched
        union = known | matched
        return len(intersection) / len(union)

    def _score_redundancy(self, plan: CandidatePlan, context: PolicyContext) -> float:
        """Redundancy 🔀 — resilience through alternate branches.

        More fallback branches → more resilient → higher score, bounded by a
        logarithmic curve so we don't over-reward trivial branching.
        """
        branches = max(plan.fallback_branches, 0)
        # log2(branches + 1) ∈ [0, ∞); divide by log2(9) ≈ 3.17 so that
        # 8 branches → 1.0 and 0 branches → 0.0.
        return min(math.log2(branches + 1) / math.log2(9), 1.0)

    def _score_balance(self, plan: CandidatePlan, context: PolicyContext) -> float:
        """Balance ⚖️ — equilibrium between speed, certainty, and risk.

        Utility = certainty - risk.  Adjusted by context confidence so that
        high-confidence contexts reward certainty more.
        """
        utility = plan.certainty - plan.risk
        # Map utility (-1..1) to score (0..1).
        raw = (utility + 1.0) / 2.0
        # Blend with context confidence as a weight.
        blended = raw * context.confidence + 0.5 * (1.0 - context.confidence)
        return max(0.0, min(blended, 1.0))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _normalise_weights(self) -> None:
        total = sum(self._weights.values())
        if total <= 0:
            raise ValueError("Policy weights must sum to a positive value")
        for k in self._weights:
            self._weights[k] /= total

    def _tiebreak_key(self, plan_id: str) -> int:
        """Return a deterministic integer for tie-breaking."""
        digest = hashlib.sha256(f"{self._seed}:{plan_id}".encode()).hexdigest()
        return int(digest[:8], 16)

    @property
    def weights(self) -> Dict[str, float]:
        """Read-only view of the active per-dimension weights."""
        return dict(self._weights)

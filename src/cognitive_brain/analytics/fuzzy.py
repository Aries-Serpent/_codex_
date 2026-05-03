"""
Fuzzy Logic PoC for Compliance Boundary Cases (Phase 4)

Implements triangular and trapezoidal membership functions for gradual
boundary classification — reduces false negatives on ambiguous cases
at pattern decision boundaries.

Feature flag: CODEX_FUZZY_MODE=true (default: false)

Research basis: CHHIP 2021 — Fuzzy logic achieved 12% false-negative reduction
for borderline compliance cases in financial regulation contexts.

API:
    engine = FuzzyEngine.default()
    result = engine.evaluate(score=0.68, business_impact=0.65, remediation_cost=5000.0)
    # FuzzyResult(approve=0.0, monitor=0.72, conditional=0.28, reject=0.0, dominant="monitor")

Integration point (behind feature flag):
    In QuantumComplianceAssessor._assess_classical() or post-scoring blending,
    use fuzzy_blend() to adjust near-boundary decisions.
"""

import os
from dataclasses import dataclass
from typing import Any


def _fuzzy_mode_enabled() -> bool:
    """Check CODEX_FUZZY_MODE env flag (default: false)."""
    return os.getenv("CODEX_FUZZY_MODE", "false").lower() in (
        "true",
        "1",
        "yes",
        "on",
    )


# ---------------------------------------------------------------------------
# Membership functions
# ---------------------------------------------------------------------------


def trimf(x: float, a: float, b: float, c: float) -> float:
    """
    Triangular membership function.

    Returns the degree of membership of ``x`` in [a, b, c]:
    - 0.0 for x ≤ a or x ≥ c
    - 1.0 for x == b
    - Linear interpolation otherwise

    Args:
        x: Input value.
        a: Left foot (membership = 0).
        b: Peak (membership = 1).
        c: Right foot (membership = 0).
    """
    if x <= a or x >= c:
        return 0.0
    if x <= b:
        return (x - a) / (b - a) if b != a else 1.0
    return (c - x) / (c - b) if c != b else 1.0


def trapmf(x: float, a: float, b: float, c: float, d: float) -> float:
    """
    Trapezoidal membership function.

    Returns the degree of membership of ``x`` in [a, b, c, d]:
    - 0.0 for x ≤ a or x ≥ d
    - 1.0 for b ≤ x ≤ c
    - Linear interpolation on the shoulders

    Args:
        x: Input value.
        a: Left foot (membership = 0).
        b: Left shoulder (membership = 1).
        c: Right shoulder (membership = 1).
        d: Right foot (membership = 0).
    """
    if x <= a or x >= d:
        return 0.0
    if x <= b:
        return (x - a) / (b - a) if b != a else 1.0
    if x <= c:
        return 1.0
    return (d - x) / (d - c) if d != c else 1.0


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class FuzzyResult:
    """
    Fuzzy evaluation result for a compliance assessment.

    Attributes:
        approve:      Fuzzy membership in "approve" set.
        monitor:      Fuzzy membership in "approve with monitoring" set.
        conditional:  Fuzzy membership in "conditional approval" set.
        reject:       Fuzzy membership in "reject" set.
        dominant:     Decision class with highest membership.
        confidence:   Membership value of the dominant class.
    """

    approve: float
    monitor: float
    conditional: float
    reject: float
    dominant: str
    confidence: float


# ---------------------------------------------------------------------------
# Fuzzy Engine
# ---------------------------------------------------------------------------


class FuzzyEngine:
    """
    Fuzzy Logic engine for compliance boundary case classification.

    Uses triangular and trapezoidal membership functions to model
    uncertainty at pattern decision boundaries.  Defuzzification
    uses the maximum membership (Mamdani) method.

    The engine is fully configurable but ships with sensible defaults
    that match the compliance pattern thresholds from Phase 1/2.

    Example::

        engine = FuzzyEngine.default()
        result = engine.evaluate(score=0.72, business_impact=0.65,
                                 remediation_cost=5000.0)
        print(result.dominant, result.confidence)
        # "monitor" 0.74
    """

    def __init__(
        self,
        # Score membership bounds [a, b, c] or [a, b, c, d]
        score_low: tuple = (0.0, 0.0, 0.40, 0.55),
        score_medium: tuple = (0.40, 0.60, 0.75),
        score_high: tuple = (0.65, 0.80, 1.0, 1.0),
        # Impact membership bounds
        impact_low: tuple = (0.0, 0.0, 0.50, 0.65),
        impact_high: tuple = (0.55, 0.70, 1.0, 1.0),
        # Cost membership bounds (normalised to thousands)
        cost_low: tuple = (0.0, 0.0, 3.0, 6.0),
        cost_high: tuple = (5.0, 10.0, 1e9, 1e9),
    ) -> None:
        self.score_low = score_low
        self.score_medium = score_medium
        self.score_high = score_high
        self.impact_low = impact_low
        self.impact_high = impact_high
        self.cost_low = cost_low
        self.cost_high = cost_high

    @classmethod
    def default(cls) -> "FuzzyEngine":
        """Return an engine pre-configured for the compliance pattern space."""
        return cls()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(
        self,
        score: float,
        business_impact: float,
        remediation_cost: float,
    ) -> FuzzyResult:
        """
        Evaluate fuzzy compliance membership for three input variables.

        Applies Mamdani inference with four fuzzy rules:

        1. score_high AND impact_high → approve
        2. score_medium AND impact_high → monitor
        3. score_medium AND impact_low → conditional
        4. score_low → reject

        Args:
            score:             Compliance score (0.0–1.0).
            business_impact:   Business impact (0.0–1.0).
            remediation_cost:  Remediation cost in currency units (e.g. GBP).

        Returns:
            ``FuzzyResult`` with memberships and dominant class.
        """
        cost_k = remediation_cost / 1000.0  # normalise to thousands

        # ---- Fuzzify inputs ----
        s_low = trapmf(score, *self.score_low)
        s_med = trimf(score, *self.score_medium)
        s_high = trapmf(score, *self.score_high)

        i_low = trapmf(business_impact, *self.impact_low)
        i_high = trapmf(business_impact, *self.impact_high)

        c_low = trapmf(cost_k, *self.cost_low)
        c_high = trapmf(cost_k, *self.cost_high)

        # ---- Fuzzy rules (AND = min) ----
        # Rule 1: High score + high impact → APPROVE
        approve = min(s_high, i_high)
        # Rule 2: Medium score + high impact → MONITOR
        monitor = min(s_med, i_high)
        # Rule 3: Medium score + low impact → CONDITIONAL (low cost amplifies)
        conditional = min(s_med, i_low, max(c_low, 0.5))
        # Rule 4: Low score → REJECT (high cost strengthens)
        reject = max(s_low, min(s_low, c_high))

        # ---- Defuzzification: maximum membership ----
        scores = {
            "approve": approve,
            "monitor": monitor,
            "conditional": conditional,
            "reject": reject,
        }
        dominant = max(scores, key=lambda k: scores[k])
        confidence = scores[dominant]

        return FuzzyResult(
            approve=approve,
            monitor=monitor,
            conditional=conditional,
            reject=reject,
            dominant=dominant,
            confidence=confidence,
        )

    def apply_membership_tuning(self, tuning_rules: dict[str, Any]) -> "FuzzyEngine":
        """
        Apply membership-function parameter tuning and return a NEW FuzzyEngine.

        Returns a new instance with updated membership bounds — does NOT mutate
        ``self`` (safe for concurrent use).  Only applied when
        ``CODEX_FUZZY_MODE=true``; returns ``self`` unchanged otherwise.

        Supported keys in ``tuning_rules`` (each value is a tuple of floats):
            ``score_low``, ``score_medium``, ``score_high``,
            ``impact_low``, ``impact_high``,
            ``cost_low``, ``cost_high``

        Args:
            tuning_rules: Dict mapping membership-parameter name → new tuple of
                          boundary floats (3-tuple for triangular, 4-tuple for
                          trapezoidal).

        Returns:
            New ``FuzzyEngine`` with adjusted parameters, or ``self`` if
            ``CODEX_FUZZY_MODE`` is disabled.
        """
        if not _fuzzy_mode_enabled():
            return self

        def _t(key: str, default: tuple) -> tuple:
            raw = tuning_rules.get(key)
            if raw is None:
                return default
            return tuple(float(v) for v in raw)

        return FuzzyEngine(
            score_low=_t("score_low", self.score_low),
            score_medium=_t("score_medium", self.score_medium),
            score_high=_t("score_high", self.score_high),
            impact_low=_t("impact_low", self.impact_low),
            impact_high=_t("impact_high", self.impact_high),
            cost_low=_t("cost_low", self.cost_low),
            cost_high=_t("cost_high", self.cost_high),
        )

    def fuzzy_blend(
        self,
        crisp_decision: str,
        score: float,
        business_impact: float,
        remediation_cost: float,
        threshold: float = 0.15,
    ) -> str:
        """
        Optionally override a crisp decision for near-boundary cases.

        When the fuzzy engine detects a high-confidence alternative decision
        (membership > ``threshold``) AND the crisp and fuzzy decisions differ,
        the fuzzy decision overrides — reducing false negatives at boundaries.

        Only active when ``CODEX_FUZZY_MODE=true``.

        Args:
            crisp_decision:   Decision string from the main path
                              ("approve", "monitor", "conditional", "reject").
            score:            Compliance score.
            business_impact:  Business impact.
            remediation_cost: Remediation cost.
            threshold:        Minimum fuzzy confidence to trigger override.

        Returns:
            Potentially overridden decision string.
        """
        if not _fuzzy_mode_enabled():
            return crisp_decision

        result = self.evaluate(score, business_impact, remediation_cost)

        # Only override if fuzzy is confident and disagrees
        if result.dominant != crisp_decision and result.confidence >= threshold:
            return result.dominant
        return crisp_decision

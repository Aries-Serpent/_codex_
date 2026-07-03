"""Stratified Routing for Cognitive Brain Skills.

The router scores each registered skill against a query objective and selects
the highest-scoring candidate.  If no executable skill is available or policy
blocks execution, a doc-skill fallback is used.

Scoring formula::

    score = (
        w_match    * match_score        # capability tag overlap
      + w_fresh    * freshness_score    # inverse budget exhaustion
      + w_aais     * aais_score         # doc quality
      - w_cost     * cost_penalty       # budget consumed fraction
      - w_risk     * risk_penalty       # risk tier penalty
    )

Default weights: match=0.40, fresh=0.15, aais=0.25, cost=0.10, risk=0.10.

Usage::

    from codex.skills.routing import StratifiedRouter
    from codex.skills.registry import get_registry

    router = StratifiedRouter(get_registry())
    decision = router.route(
        objective="retrieve relevant docs",
        tags=["docs", "retrieval"],
        constraints={"risk_tier_max": "medium"},
    )
    logger.info(decision.selected_skill_id)
"""

from __future__ import annotations

from typing import Any

from codex.logging.structured_logger import logger

from .models import RegisteredSkill, RoutingDecision, RoutingScore
from .registry import SkillRegistry

# Default scoring weights (must sum to 1.0)
_W_MATCH = 0.40
_W_FRESH = 0.15
_W_AAIS = 0.25
_W_COST = 0.10
_W_RISK = 0.10

_RISK_TIER_RANK: dict[str, int] = {"low": 0, "medium": 1, "high": 2}
_RISK_PENALTY_MAP: dict[str, float] = {"low": 0.0, "medium": 0.2, "high": 0.6}


class StratifiedRouter:
    """Score and select skills using the AAIS-weighted stratified routing formula.

    Parameters
    ----------
    registry:
        The :class:`~codex.skills.registry.SkillRegistry` to query.
    weights:
        Optional override for the scoring weights.
        Keys: ``match``, ``fresh``, ``aais``, ``cost``, ``risk``.
    """

    def __init__(
        self,
        registry: SkillRegistry,
        *,
        weights: dict[str, float] | None = None,
    ) -> None:
        self._registry = registry
        w = weights or {}
        self._w_match = w.get("match", _W_MATCH)
        self._w_fresh = w.get("fresh", _W_FRESH)
        self._w_aais = w.get("aais", _W_AAIS)
        self._w_cost = w.get("cost", _W_COST)
        self._w_risk = w.get("risk", _W_RISK)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def route(
        self,
        objective: str,
        tags: list[str] | None = None,
        *,
        caller_id: str = "*",
        constraints: dict[str, Any] | None = None,
    ) -> RoutingDecision:
        """Select the best skill for *objective*.

        Parameters
        ----------
        objective:
            Natural-language description of the task to route.
        tags:
            Preferred capability tags to match against.
        caller_id:
            Identity of the requesting agent (for allowlist checks).
        constraints:
            Optional routing constraints:
            - ``risk_tier_max``: ``"low" | "medium" | "high"`` (default ``"high"``)
            - ``budget_calls_min``: minimum remaining call budget required.

        Returns
        -------
        RoutingDecision
        """
        tags = tags or []
        constraints = constraints or {}
        risk_tier_max = constraints.get("risk_tier_max", "high")
        budget_calls_min: int = constraints.get("budget_calls_min", 1)

        candidates = self._registry.list()

        # Filter by risk tier ceiling
        max_rank = _RISK_TIER_RANK.get(risk_tier_max, 2)
        candidates = [
            s for s in candidates if _RISK_TIER_RANK.get(s.manifest.policy.risk_tier, 0) <= max_rank
        ]

        # Filter by caller allowlist
        candidates = [s for s in candidates if s.caller_allowed(caller_id)]

        # Filter by minimum budget headroom
        candidates = [s for s in candidates if s.has_budget_headroom(calls=budget_calls_min)]

        if not candidates:
            return RoutingDecision(
                reason="No eligible skills found after filtering",
                fallback_used=False,
            )

        # Score all candidates
        scores = [self._score(skill, objective, tags) for skill in candidates]
        scores.sort(key=lambda s: s.total_score, reverse=True)

        best = scores[0]
        logger.info(
            "Router: selected '%s@%s' (score=%.3f)",
            best.skill_id,
            best.version,
            best.total_score,
        )

        return RoutingDecision(
            selected_skill_id=best.skill_id,
            selected_version=best.version,
            scores=scores,
            fallback_used=False,
            reason=f"Top score {best.total_score:.3f}",
        )

    def score_skill(
        self,
        skill_id: str,
        objective: str,
        tags: list[str] | None = None,
        version: str | None = None,
    ) -> RoutingScore | None:
        """Return the routing score for a specific skill.

        Returns None if the skill is not registered.
        """
        skill = self._registry.resolve(skill_id, version)
        if skill is None:
            return None
        return self._score(skill, objective, tags or [])

    # ------------------------------------------------------------------
    # Internal scoring
    # ------------------------------------------------------------------

    def _score(
        self,
        skill: RegisteredSkill,
        objective: str,
        tags: list[str],
    ) -> RoutingScore:
        """Compute the composite routing score for one skill."""
        manifest = skill.manifest

        match_score = self._capability_match(manifest.capability_tags, tags, objective)
        freshness_score = self._freshness(skill)
        aais_score = manifest.doc.aais_score if manifest.doc else 0.5
        cost_penalty = self._cost_penalty(skill)
        risk_penalty = _RISK_PENALTY_MAP.get(manifest.policy.risk_tier, 0.0)

        total = (
            self._w_match * match_score
            + self._w_fresh * freshness_score
            + self._w_aais * aais_score
            - self._w_cost * cost_penalty
            - self._w_risk * risk_penalty
        )
        total = max(0.0, min(1.0, total))

        return RoutingScore(
            skill_id=manifest.id,
            version=manifest.version,
            total_score=round(total, 4),
            match_score=round(match_score, 4),
            freshness_score=round(freshness_score, 4),
            aais_score=round(aais_score, 4),
            cost_penalty=round(cost_penalty, 4),
            risk_penalty=round(risk_penalty, 4),
        )

    @staticmethod
    def _capability_match(
        skill_tags: list[str],
        query_tags: list[str],
        objective: str,
    ) -> float:
        """Jaccard-like match between skill tags and query tags + objective keywords."""
        if not skill_tags:
            return 0.0

        query_terms = set(query_tags) | {w.lower() for w in objective.split() if len(w) > 3}
        skill_set = {t.lower() for t in skill_tags}

        intersection = skill_set & query_terms
        union = skill_set | query_terms

        if not union:
            return 0.0

        # Jaccard similarity
        jaccard = len(intersection) / len(union)
        # Bonus if all query tags are covered
        coverage_bonus = (
            0.2 if query_tags and all(t.lower() in skill_set for t in query_tags) else 0.0
        )

        return min(1.0, jaccard + coverage_bonus)

    @staticmethod
    def _freshness(skill: RegisteredSkill) -> float:
        """Score 1.0 when budget is untouched; decays as usage grows."""
        budget_cfg = skill.manifest.policy.budgets
        calls_used = skill.budget_used.get("calls", 0)
        if budget_cfg.calls <= 0:
            return 1.0
        exhaustion = calls_used / budget_cfg.calls
        return max(0.0, 1.0 - exhaustion)

    @staticmethod
    def _cost_penalty(skill: RegisteredSkill) -> float:
        """Fraction of token budget already consumed (0 = fresh, 1 = exhausted)."""
        budget_cfg = skill.manifest.policy.budgets
        tokens_used = skill.budget_used.get("tokens", 0)
        if budget_cfg.tokens <= 0:
            return 0.0
        return min(1.0, tokens_used / budget_cfg.tokens)


__all__ = ["StratifiedRouter"]

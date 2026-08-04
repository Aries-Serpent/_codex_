"""Tests for DeterministicPolicy (physics-inspired plan scoring).

Covers:
- Unit: per-dimension scorers
- Unit: ranking stability / determinism
- Unit: tie-breaking consistency
- Unit: weight normalisation
- Unit: empty candidates
"""

from __future__ import annotations

import pytest

from src.codex.cognitive_brain.policy import (
    CandidatePlan,
    DeterministicPolicy,
    PolicyContext,
    ScoredPlan,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def policy() -> DeterministicPolicy:
    return DeterministicPolicy(seed=42)


@pytest.fixture()
def context() -> PolicyContext:
    return PolicyContext(
        task_type="repo_introspection",
        confidence=0.8,
        risk_level=0.1,
        dependency_count=1,
        time_budget_ms=5000,
        known_patterns=["repo_introspection", "code_search"],
        constraints=["read_only"],
    )


def _make_plan(
    plan_id: str = "test_plan",
    steps: int = 3,
    latency: float = 800.0,
    branches: int = 2,
    certainty: float = 0.9,
    risk: float = 0.05,
    matched_patterns: list[str] | None = None,
    constraints_satisfied: list[str] | None = None,
) -> CandidatePlan:
    return CandidatePlan(
        plan_id=plan_id,
        description="test",
        estimated_steps=steps,
        estimated_latency_ms=latency,
        fallback_branches=branches,
        certainty=certainty,
        risk=risk,
        matched_patterns=matched_patterns or [],
        constraints_satisfied=constraints_satisfied or [],
    )


# ---------------------------------------------------------------------------
# DeterministicPolicy unit tests
# ---------------------------------------------------------------------------


class TestDeterministicPolicy:
    def test_score_returns_scored_plan(self, policy: DeterministicPolicy, context: PolicyContext) -> None:
        plan = _make_plan()
        scored = policy.score(plan, context)
        assert isinstance(scored, ScoredPlan)
        assert 0.0 <= scored.total_score <= 1.0

    def test_all_dimension_scores_in_range(
        self, policy: DeterministicPolicy, context: PolicyContext
    ) -> None:
        plan = _make_plan(matched_patterns=["repo_introspection"], constraints_satisfied=["read_only"])
        scored = policy.score(plan, context)
        for name, val in scored.score_breakdown().items():
            assert 0.0 <= val <= 1.0, f"Dimension '{name}' out of range: {val}"

    def test_deterministic_same_inputs(
        self, context: PolicyContext
    ) -> None:
        """Same seed + same inputs must produce identical scores."""
        p1 = DeterministicPolicy(seed=42)
        p2 = DeterministicPolicy(seed=42)
        plan = _make_plan(matched_patterns=["repo_introspection"], constraints_satisfied=["read_only"])
        s1 = p1.score(plan, context)
        s2 = p2.score(plan, context)
        assert s1.total_score == s2.total_score

    def test_different_seed_may_differ_in_tiebreak(self) -> None:
        """Different seeds should produce different tiebreak orderings for equal scores."""
        p1 = DeterministicPolicy(seed=1)
        p2 = DeterministicPolicy(seed=99)
        key1 = p1._tiebreak_key("plan_x")
        key2 = p2._tiebreak_key("plan_x")
        assert key1 != key2

    def test_rank_returns_all_candidates(
        self, policy: DeterministicPolicy, context: PolicyContext
    ) -> None:
        plans = [_make_plan(plan_id=f"p{i}") for i in range(5)]
        ranked = policy.rank(plans, context)
        assert len(ranked) == 5

    def test_rank_is_sorted_descending(
        self, policy: DeterministicPolicy, context: PolicyContext
    ) -> None:
        plans = [
            _make_plan("fast", steps=1, latency=100, certainty=0.99, risk=0.01),
            _make_plan("slow", steps=20, latency=9000, certainty=0.3, risk=0.9),
        ]
        ranked = policy.rank(plans, context)
        assert ranked[0].total_score >= ranked[1].total_score

    def test_rank_assigns_sequential_ranks(
        self, policy: DeterministicPolicy, context: PolicyContext
    ) -> None:
        plans = [_make_plan(plan_id=f"p{i}") for i in range(4)]
        ranked = policy.rank(plans, context)
        assert [r.rank for r in ranked] == [1, 2, 3, 4]

    def test_select_returns_top_plan(
        self, policy: DeterministicPolicy, context: PolicyContext
    ) -> None:
        plans = [
            _make_plan("best", certainty=0.99, risk=0.01, branches=5),
            _make_plan("worst", certainty=0.1, risk=0.9, branches=0),
        ]
        winner = policy.select(plans, context)
        assert winner is not None
        assert winner.plan.plan_id == "best"

    def test_select_empty_candidates_returns_none(
        self, policy: DeterministicPolicy, context: PolicyContext
    ) -> None:
        assert policy.select([], context) is None

    def test_path_score_shorter_plan_wins(
        self, policy: DeterministicPolicy, context: PolicyContext
    ) -> None:
        short = _make_plan("short", steps=1, latency=100)
        long_ = _make_plan("long", steps=50, latency=9000)
        s_short = policy.score(short, context)
        s_long = policy.score(long_, context)
        assert s_short.path_score > s_long.path_score

    def test_fields_score_all_constraints_satisfied(
        self, policy: DeterministicPolicy, context: PolicyContext
    ) -> None:
        plan = _make_plan(constraints_satisfied=["read_only"])
        scored = policy.score(plan, context)
        assert scored.fields_score == 1.0

    def test_fields_score_no_constraints_neutral(
        self, policy: DeterministicPolicy
    ) -> None:
        ctx = PolicyContext(
            task_type="x", confidence=0.5, risk_level=0.2,
            dependency_count=1, time_budget_ms=5000,
            constraints=[],
        )
        plan = _make_plan()
        scored = policy.score(plan, ctx)
        assert scored.fields_score == 0.8  # neutral default

    def test_patterns_score_full_overlap(
        self, policy: DeterministicPolicy, context: PolicyContext
    ) -> None:
        plan = _make_plan(matched_patterns=["repo_introspection", "code_search"])
        scored = policy.score(plan, context)
        assert scored.patterns_score == 1.0  # perfect Jaccard overlap

    def test_patterns_score_no_overlap(
        self, policy: DeterministicPolicy, context: PolicyContext
    ) -> None:
        plan = _make_plan(matched_patterns=["ui_interaction"])
        scored = policy.score(plan, context)
        assert scored.patterns_score < 0.5

    def test_redundancy_score_more_branches_higher(
        self, policy: DeterministicPolicy, context: PolicyContext
    ) -> None:
        low = _make_plan("low", branches=0)
        high = _make_plan("high", branches=8)
        s_low = policy.score(low, context)
        s_high = policy.score(high, context)
        assert s_high.redundancy_score > s_low.redundancy_score

    def test_redundancy_score_zero_branches(
        self, policy: DeterministicPolicy, context: PolicyContext
    ) -> None:
        plan = _make_plan(branches=0)
        scored = policy.score(plan, context)
        assert scored.redundancy_score == 0.0

    def test_balance_score_low_risk_high_certainty(
        self, policy: DeterministicPolicy, context: PolicyContext
    ) -> None:
        plan = _make_plan(certainty=0.99, risk=0.01)
        scored = policy.score(plan, context)
        assert scored.balance_score > 0.7

    def test_balance_score_high_risk_low_certainty(
        self, policy: DeterministicPolicy, context: PolicyContext
    ) -> None:
        plan = _make_plan(certainty=0.1, risk=0.95)
        scored = policy.score(plan, context)
        assert scored.balance_score < 0.4

    def test_weights_sum_to_one(self, policy: DeterministicPolicy) -> None:
        total = sum(policy.weights.values())
        assert abs(total - 1.0) < 1e-9, f"Weights must sum to 1.0, got {total}"

    def test_custom_weights_applied(self, context: PolicyContext) -> None:
        # Give 100% weight to path; everything else → 0.
        p = DeterministicPolicy(seed=42, weights={"path": 1.0, "fields": 0, "patterns": 0, "redundancy": 0, "balance": 0})
        plan = _make_plan(steps=1, latency=50)
        scored = p.score(plan, context)
        # total_score ≈ path_score (other terms are 0)
        assert abs(scored.total_score - scored.path_score) < 1e-9

    def test_invalid_zero_weights_raises(self) -> None:
        with pytest.raises(ValueError):
            DeterministicPolicy(weights={"path": 0, "fields": 0, "patterns": 0, "redundancy": 0, "balance": 0})

    def test_score_breakdown_keys(
        self, policy: DeterministicPolicy, context: PolicyContext
    ) -> None:
        plan = _make_plan()
        scored = policy.score(plan, context)
        keys = set(scored.score_breakdown())
        assert keys == {"path", "fields", "patterns", "redundancy", "balance", "total"}

    def test_tiebreak_is_consistent(self, policy: DeterministicPolicy) -> None:
        k1 = policy._tiebreak_key("same_id")
        k2 = policy._tiebreak_key("same_id")
        assert k1 == k2

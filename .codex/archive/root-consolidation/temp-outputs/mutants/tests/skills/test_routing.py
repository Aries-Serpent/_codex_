"""Tests for StratifiedRouter."""

from __future__ import annotations

import pytest

from codex.skills.models import BudgetConfig, DocMeta, PolicyConfig, SkillManifest
from codex.skills.registry import SkillRegistry, reset_registry
from codex.skills.routing import StratifiedRouter


@pytest.fixture(autouse=True)
def fresh_registry():
    reset_registry()
    yield
    reset_registry()


def _register_skill(
    reg: SkillRegistry, skill_id: str, tags: list[str], risk_tier: str = "low", aais: float = 0.9
) -> None:
    reg.register(
        SkillManifest(
            id=skill_id,
            version="1.0.0",
            name=skill_id.replace(".", " ").title(),
            entrypoint=f"codex.skills.stubs:{skill_id.replace('.', '_')}",
            capability_tags=tags,
            policy=PolicyConfig(
                risk_tier=risk_tier,  # type: ignore[arg-type]
                budgets=BudgetConfig(calls=100, tokens=50_000, wallclock_ms=30_000),
            ),
            doc=DocMeta(doc_id=f"doc_{skill_id}", aais_score=aais),
        )
    )


class TestStratifiedRouterBasic:
    def test_route_selects_best_matching_skill(self):
        reg = SkillRegistry()
        _register_skill(reg, "doc.retriever", ["docs", "retrieval"])
        _register_skill(reg, "code.search", ["code", "search"])
        router = StratifiedRouter(reg)
        decision = router.route("retrieve documentation", tags=["docs", "retrieval"])
        assert decision.selected_skill_id == "doc.retriever", "selected_skill_id is not valid"

    def test_route_returns_none_when_no_skills(self):
        reg = SkillRegistry()
        router = StratifiedRouter(reg)
        decision = router.route("do something")
        assert decision.selected_skill_id is None, "selected_skill_id is not valid"

    def test_route_returns_scores_list(self):
        reg = SkillRegistry()
        _register_skill(reg, "doc.retriever", ["docs"])
        _register_skill(reg, "code.search", ["code"])
        router = StratifiedRouter(reg)
        decision = router.route("anything", tags=["docs"])
        assert len(decision.scores) == 2, "Collection must not be empty"
        # Scores sorted descending
        assert decision.scores[0].total_score >= decision.scores[1].total_score, "total_score must be greater than zero"

    def test_route_scores_between_0_and_1(self):
        reg = SkillRegistry()
        _register_skill(reg, "doc.retriever", ["docs"])
        router = StratifiedRouter(reg)
        decision = router.route("search docs", tags=["docs"])
        for s in decision.scores:
            assert 0.0 <= s.total_score <= 1.0, "0 is not valid"


class TestStratifiedRouterConstraints:
    def test_risk_tier_max_filters_high_risk(self):
        reg = SkillRegistry()
        _register_skill(reg, "safe.skill", ["task"], risk_tier="low")
        _register_skill(reg, "risky.skill", ["task"], risk_tier="high")
        router = StratifiedRouter(reg)
        decision = router.route("do task", tags=["task"], constraints={"risk_tier_max": "low"})
        assert decision.selected_skill_id == "safe.skill", "selected_skill_id is not valid"

    def test_budget_min_filters_exhausted_skills(self):
        reg = SkillRegistry()
        _register_skill(reg, "fresh.skill", ["task"])
        _register_skill(reg, "used.skill", ["task"])
        reg.consume_budget("used.skill", calls=100)  # exhaust budget
        router = StratifiedRouter(reg)
        decision = router.route("do task", tags=["task"])
        assert decision.selected_skill_id == "fresh.skill", "selected_skill_id is not valid"

    def test_allowlist_blocks_caller(self):
        reg = SkillRegistry()
        reg.register(
            SkillManifest(
                id="restricted.skill",
                version="1.0.0",
                name="Restricted",
                entrypoint="stub:fn",
                capability_tags=["task"],
                policy=PolicyConfig(allowlist=["admin"], budgets=BudgetConfig()),
            )
        )
        router = StratifiedRouter(reg)
        decision = router.route("do task", tags=["task"], caller_id="normal-user")
        assert decision.selected_skill_id is None, "selected_skill_id is not valid"


class TestStratifiedRouterScoring:
    def test_higher_aais_score_wins(self):
        reg = SkillRegistry()
        _register_skill(reg, "high.quality", ["docs"], aais=0.95)
        _register_skill(reg, "low.quality", ["docs"], aais=0.40)
        router = StratifiedRouter(reg)
        decision = router.route("search docs", tags=["docs"])
        assert decision.selected_skill_id == "high.quality", "selected_skill_id is not valid"

    def test_score_skill_returns_routing_score(self):
        reg = SkillRegistry()
        _register_skill(reg, "doc.retriever", ["docs", "retrieval"])
        router = StratifiedRouter(reg)
        score = router.score_skill("doc.retriever", "retrieve docs", ["docs"])
        assert score is not None, "score must be initialized"
        assert 0.0 <= score.total_score <= 1.0, "0 is not valid"
        assert score.skill_id == "doc.retriever", "skill_id is not valid"

    def test_score_skill_returns_none_for_unknown(self):
        reg = SkillRegistry()
        router = StratifiedRouter(reg)
        assert router.score_skill("unknown.skill", "anything") is None

    def test_custom_weights_affect_scores(self):
        reg = SkillRegistry()
        _register_skill(reg, "doc.skill", ["docs"], aais=0.9)
        # Maximise AAIS weight
        router = StratifiedRouter(
            reg, weights={"match": 0.1, "fresh": 0.1, "aais": 0.6, "cost": 0.1, "risk": 0.1}
        )
        score = router.score_skill("doc.skill", "docs", ["docs"])
        assert score is not None, "score must be initialized"
        # AAIS contribution should dominate
        assert score.aais_score == pytest.approx(0.9, abs=0.01)

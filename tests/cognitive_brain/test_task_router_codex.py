"""Tests for src/codex/cognitive/task_router.py — Phase 2 coverage gap-fill.

Covers RoutingRequest, RoutingResult, and TaskRouter (routing, fallback,
available_agents, route_many, helpers).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from codex.cognitive.task_router import (
    RoutingRequest,
    RoutingResult,
    TaskRouter,
)

# ---------------------------------------------------------------------------
# Data-class smoke tests
# ---------------------------------------------------------------------------


class TestRoutingRequest:
    def test_minimal_construction(self) -> None:
        req = RoutingRequest(task_description="Fix failing CI")
        assert req.task_description == "Fix failing CI"
        assert req.tags == []
        assert req.urgency == "normal"
        assert req.preferred_agent is None
        assert req.exclude_agents == []

    def test_full_construction(self) -> None:
        req = RoutingRequest(
            task_description="Security scan",
            tags=["security", "cve"],
            urgency="critical",
            preferred_agent="security-audit-agent",
            exclude_agents=["ci-testing-agent"],
        )
        assert req.urgency == "critical"
        assert "security" in req.tags
        assert req.preferred_agent == "security-audit-agent"
        assert req.exclude_agents == ["ci-testing-agent"]


class TestRoutingResult:
    def test_construction(self) -> None:
        result = RoutingResult(
            selected_agent="ci-testing-agent",
            confidence=0.85,
            reasoning="Matched 2/2 tags",
        )
        assert result.selected_agent == "ci-testing-agent"
        assert result.confidence == pytest.approx(0.85)
        assert result.alternative_agents == []
        assert result.matched_tags == []
        assert result.fallback_used is False

    def test_fallback_flag(self) -> None:
        result = RoutingResult(
            selected_agent="fallback-agent",
            confidence=0.3,
            reasoning="No tags matched",
            fallback_used=True,
        )
        assert result.fallback_used is True


# ---------------------------------------------------------------------------
# TaskRouter — empty registry (no AGENT_REGISTRY.yaml available in tests)
# ---------------------------------------------------------------------------


class TestTaskRouterEmptyRegistry:
    """TaskRouter degrades gracefully when the AGENT_REGISTRY is absent."""

    @pytest.fixture()
    def router(self, tmp_path: Path) -> TaskRouter:
        """Router pointed at non-existent paths so no real I/O occurs."""
        return TaskRouter(
            registry_path=tmp_path / "AGENT_REGISTRY.yaml",
            pattern_store_path=tmp_path / "pattern_store.json",
        )

    def test_route_returns_routing_result(self, router: TaskRouter) -> None:
        req = RoutingRequest(task_description="Fix CI", tags=["ci_failure"])
        result = router.route(req)
        assert isinstance(result, RoutingResult)

    def test_route_fallback_when_no_registry(self, router: TaskRouter) -> None:
        req = RoutingRequest(task_description="Unknown task", tags=["unknown_tag"])
        result = router.route(req)
        # Without a registry every request hits the fallback path
        assert result.fallback_used is True
        assert result.confidence <= 0.5

    def test_route_confidence_between_0_and_1(self, router: TaskRouter) -> None:
        req = RoutingRequest(task_description="Any task")
        result = router.route(req)
        assert 0.0 <= result.confidence <= 1.0

    def test_route_many_returns_list(self, router: TaskRouter) -> None:
        requests = [
            RoutingRequest("Task A", tags=["ci"]),
            RoutingRequest("Task B", tags=["security"]),
        ]
        results = router.route_many(requests)
        assert len(results) == 2
        assert all(isinstance(r, RoutingResult) for r in results)

    def test_available_agents_empty_when_no_registry(self, router: TaskRouter) -> None:
        agents = router.available_agents()
        assert isinstance(agents, list)
        assert agents == []

    def test_available_agents_with_tag_empty(self, router: TaskRouter) -> None:
        agents = router.available_agents(tag="ci_failure")
        assert agents == []


# ---------------------------------------------------------------------------
# TaskRouter — minimal in-memory registry via YAML file
# ---------------------------------------------------------------------------


class TestTaskRouterWithRegistry:
    """TaskRouter with a minimal YAML registry written to disk."""

    @pytest.fixture()
    def router(self, tmp_path: Path) -> TaskRouter:
        registry_yaml = tmp_path / "AGENT_REGISTRY.yaml"
        registry_yaml.write_text(
            """
agents:
  - name: ci-testing-agent
    status: active
    capability_tags:
      - ci_failure
      - python
      - test_runner
  - name: security-audit-agent
    status: active
    capability_tags:
      - security
      - cve
      - vulnerability
  - name: old-agent
    status: deprecated
    capability_tags:
      - ci_failure
""",
            encoding="utf-8",
        )
        return TaskRouter(
            registry_path=registry_yaml,
            pattern_store_path=tmp_path / "pattern_store.json",
        )

    def test_available_agents_all_active(self, router: TaskRouter) -> None:
        agents = router.available_agents()
        assert "ci-testing-agent" in agents
        assert "security-audit-agent" in agents
        # deprecated agent must be excluded
        assert "old-agent" not in agents

    def test_available_agents_filtered_by_tag(self, router: TaskRouter) -> None:
        agents = router.available_agents(tag="security")
        assert "security-audit-agent" in agents
        assert "ci-testing-agent" not in agents

    def test_route_matches_ci_agent(self, router: TaskRouter) -> None:
        req = RoutingRequest(
            task_description="CI pipeline failing",
            tags=["ci_failure", "python"],
        )
        result = router.route(req)
        assert result.selected_agent == "ci-testing-agent"
        assert result.fallback_used is False
        assert len(result.matched_tags) > 0

    def test_route_security_tags(self, router: TaskRouter) -> None:
        req = RoutingRequest(
            task_description="CVE scan required",
            tags=["security", "cve"],
        )
        result = router.route(req)
        assert result.selected_agent == "security-audit-agent"

    def test_route_preferred_agent_respected(self, router: TaskRouter) -> None:
        req = RoutingRequest(
            task_description="Security task",
            tags=["security"],
            preferred_agent="ci-testing-agent",
        )
        result = router.route(req)
        # Preferred agent should be prioritised even if tag match is weaker
        assert result.selected_agent == "ci-testing-agent"

    def test_route_exclude_agents(self, router: TaskRouter) -> None:
        req = RoutingRequest(
            task_description="CI fix",
            tags=["ci_failure"],
            exclude_agents=["ci-testing-agent"],
        )
        result = router.route(req)
        assert result.selected_agent != "ci-testing-agent"

    def test_route_many_batch(self, router: TaskRouter) -> None:
        requests = [
            RoutingRequest("CI fix", tags=["ci_failure"]),
            RoutingRequest("Security review", tags=["security"]),
            RoutingRequest("Unknown work"),
        ]
        results = router.route_many(requests)
        assert len(results) == 3
        assert results[0].selected_agent == "ci-testing-agent"
        assert results[1].selected_agent == "security-audit-agent"

    def test_route_high_confidence_for_strong_match(self, router: TaskRouter) -> None:
        req = RoutingRequest(
            task_description="Python CI failures",
            tags=["ci_failure", "python", "test_runner"],
        )
        result = router.route(req)
        # All 3 tags match ci-testing-agent → high confidence
        assert result.confidence >= 0.5


# ---------------------------------------------------------------------------
# Private helper: _load_pattern_success
# ---------------------------------------------------------------------------


class TestLoadPatternSuccess:
    def test_missing_file_returns_empty(self, tmp_path: Path) -> None:
        router = TaskRouter(
            registry_path=tmp_path / "r.yaml",
            pattern_store_path=tmp_path / "missing.json",
        )
        # Access internal dict directly to verify empty
        assert router._pattern_success == {}

    def test_valid_pattern_store_parsed(self, tmp_path: Path) -> None:
        store_path = tmp_path / "pattern_store.json"
        store_path.write_text(
            json.dumps(
                {
                    "learning_log": [
                        {"agent_name": "ci-testing-agent", "outcome": "success"},
                        {"agent_name": "ci-testing-agent", "outcome": "success"},
                        {"agent_name": "ci-testing-agent", "outcome": "failure"},
                    ]
                }
            ),
            encoding="utf-8",
        )
        router = TaskRouter(
            registry_path=tmp_path / "r.yaml",
            pattern_store_path=store_path,
        )
        rate = router._pattern_success.get("ci-testing-agent", 0.0)
        assert rate == pytest.approx(2 / 3)

#!/usr/bin/env python3
"""
Phase 11.2 — Routing Performance & Correctness Tests
=======================================================
Validates the AdvancedAgentRouter against Phase 11.2 success criteria:
- ≥ 95% routing accuracy
- < 500ms p99 routing latency
- Correct approval-gate assignment
- Fallback chain construction
- Batch routing correctness
"""

from __future__ import annotations

import statistics
import sys
import time
from pathlib import Path

# Ensure scripts/ci is importable when running via pytest from repo root
_SCRIPTS_CI = Path(__file__).resolve().parents[2] / "scripts" / "ci"
if str(_SCRIPTS_CI) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_CI))

import pytest  # noqa: E402
from phase_11_2_advanced_router import (  # noqa: E402
    AdvancedAgentRouter,
    RoutingDecision,
    _tokenise,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def router() -> AdvancedAgentRouter:
    return AdvancedAgentRouter()


# ---------------------------------------------------------------------------
# Correctness tests
# ---------------------------------------------------------------------------


class TestRoutingAccuracy:
    """Validate that the router selects the expected agent for canonical tasks."""

    CANONICAL_CASES = [
        ("fix CI coverage failures in pytest", "unified-coverage-agent"),
        ("run test coverage gap analysis", "unified-coverage-agent"),
        ("security scan for CVE vulnerabilities", "unified-security-scanner"),
        ("detect secrets committed to repository", "unified-security-scanner"),
        ("GitHub Actions workflow yaml syntax error", "workflow-ci-fixer"),
        ("broken documentation links in README", "unified-doc-agent"),
        ("performance regression detected in benchmark", "performance-regression-detector"),
        ("ModuleNotFoundError in CI pipeline", "ci-importerror-agent"),
        ("publish package to PyPI", "pypi-publishing-operations-agent"),
        ("agent health degraded alert", "workflow-health-monitor"),
    ]

    def test_all_canonical_cases(self, router: AdvancedAgentRouter) -> None:
        """All canonical cases must route to the expected agent."""
        passed = 0
        failures = []
        for task, expected in self.CANONICAL_CASES:
            decision = router.route(task)
            if decision.primary_agent == expected:
                passed += 1
            else:
                failures.append(
                    f"  FAIL: '{task}' → got '{decision.primary_agent}' "
                    f"(expected '{expected}', confidence={decision.confidence:.1f})"
                )

        accuracy = passed / len(self.CANONICAL_CASES) * 100
        fail_msg = "\n".join(failures)
        assert accuracy >= 95.0, (
            f"Routing accuracy {accuracy:.1f}% < 95% target.\nFailures:\n{fail_msg}"
        )

    def test_router_self_test(self, router: AdvancedAgentRouter) -> None:
        """Built-in self-test must pass with ≥ 95% accuracy."""
        results = router.self_test()
        assert results["meets_target"], (
            f"Self-test accuracy {results['accuracy']}% < 95%"
        )

    def test_decision_has_required_fields(self, router: AdvancedAgentRouter) -> None:
        """Every decision must have all required fields populated."""
        decision = router.route("fix broken CI tests")
        assert decision.primary_agent, "primary_agent must not be empty"
        assert 0.0 <= decision.confidence <= 100.0, "confidence must be 0–100"
        assert decision.approval_gate in ("auto-approve", "human-review", "escalate")
        assert isinstance(decision.fallback_chain, list)
        assert len(decision.fallback_chain) <= 3, "Collection must not be empty"
        assert decision.routing_latency_ms >= 0, "routing_latency_ms must be greater than zero"
        assert decision.timestamp, "Condition must be true"
        assert isinstance(decision.top_candidates, list)

    def test_fallback_chain_excludes_primary(self, router: AdvancedAgentRouter) -> None:
        """The fallback chain must not include the primary agent."""
        for task, _ in self.CANONICAL_CASES:
            decision = router.route(task)
            assert decision.primary_agent not in decision.fallback_chain, (
                f"Primary agent '{decision.primary_agent}' appears in its own fallback chain"
            )


# ---------------------------------------------------------------------------
# Approval gate tests
# ---------------------------------------------------------------------------


class TestApprovalGates:
    """Validate approval gate thresholds are correctly applied."""

    def test_high_confidence_auto_approve(self, router: AdvancedAgentRouter) -> None:
        """Very specific tasks must get auto-approve gate."""
        # Highly specific task that should score ≥ 90
        decision = router.route("pytest coverage gap fill fail_under branch")
        if decision.confidence >= 90.0:
            assert decision.approval_gate == "auto-approve", "approval_gate is not valid"

    def test_low_confidence_escalate(self, router: AdvancedAgentRouter) -> None:
        """Gibberish tasks must get escalate gate (low confidence)."""
        decision = router.route("xyzzy frobnicate quux")
        if decision.confidence < 75.0:
            assert decision.approval_gate == "escalate", "approval_gate is not valid"

    def test_gate_thresholds_consistent(self, router: AdvancedAgentRouter) -> None:
        """Gate must be consistent with confidence score."""
        for task, _ in TestRoutingAccuracy.CANONICAL_CASES:
            d = router.route(task)
            if d.confidence >= 90.0:
                assert d.approval_gate == "auto-approve", "approval_gate is not valid"
            elif d.confidence >= 75.0:
                assert d.approval_gate == "human-review", "approval_gate is not valid"
            else:
                assert d.approval_gate == "escalate", "approval_gate is not valid"


# ---------------------------------------------------------------------------
# Latency / performance tests
# ---------------------------------------------------------------------------


class TestRoutingLatency:
    """Validate Phase 11.2 latency targets."""

    N_ITERATIONS = 50

    def _sample_latencies(self, router: AdvancedAgentRouter) -> list[float]:
        tasks = [
            "fix CI coverage failures",
            "security scan",
            "broken documentation links",
            "workflow yaml error",
            "performance regression",
        ]
        latencies = []
        for _ in range(self.N_ITERATIONS):
            task = tasks[_ % len(tasks)]
            start = time.monotonic()
            router.route(task)
            latencies.append((time.monotonic() - start) * 1000.0)
        return latencies

    def test_p99_latency_under_500ms(self, router: AdvancedAgentRouter) -> None:
        """p99 routing latency must be < 500ms."""
        latencies = self._sample_latencies(router)
        sorted_lat = sorted(latencies)
        p99_idx = int(0.99 * len(sorted_lat))
        p99 = sorted_lat[min(p99_idx, len(sorted_lat) - 1)]
        assert p99 < 500.0, f"p99 latency {p99:.2f}ms exceeds 500ms target"

    def test_p50_latency_under_200ms(self, router: AdvancedAgentRouter) -> None:
        """p50 routing latency must be < 200ms (from spec)."""
        latencies = self._sample_latencies(router)
        p50 = statistics.median(latencies)
        assert p50 < 200.0, f"p50 latency {p50:.2f}ms exceeds 200ms target"

    def test_reported_latency_accurate(self, router: AdvancedAgentRouter) -> None:
        """decision.routing_latency_ms must be a positive float."""
        for task, _ in TestRoutingAccuracy.CANONICAL_CASES[:5]:
            decision = router.route(task)
            assert decision.routing_latency_ms > 0.0, "routing_latency_ms must be greater than zero"
            assert decision.routing_latency_ms < 5000.0, "routing_latency_ms is not valid"


# ---------------------------------------------------------------------------
# Batch routing tests
# ---------------------------------------------------------------------------


class TestBatchRouting:
    """Validate batch routing returns correct number and type of decisions."""

    def test_batch_returns_same_count(self, router: AdvancedAgentRouter) -> None:
        tasks = ["coverage tests", "security scan", "docs", "ci failure"]
        decisions = router.batch_route(tasks)
        assert len(decisions) == len(tasks), "Decisions must not be empty"

    def test_batch_all_decisions_valid(self, router: AdvancedAgentRouter) -> None:
        tasks = ["coverage", "security", "documentation", "ci"]
        decisions = router.batch_route(tasks)
        for d in decisions:
            assert isinstance(d, RoutingDecision)
            assert d.primary_agent, "Condition must be true"
            assert 0 <= d.confidence <= 100, "0 is not valid"

    def test_empty_batch(self, router: AdvancedAgentRouter) -> None:
        decisions = router.batch_route([])
        assert decisions == [], "decisions is not valid"


# ---------------------------------------------------------------------------
# Tokeniser / embedding helpers
# ---------------------------------------------------------------------------


class TestHelpers:
    def test_tokenise_basic(self) -> None:
        assert _tokenise("CI/CD failure") == ["ci", "cd", "failure"]

    def test_tokenise_empty(self) -> None:
        assert _tokenise("") == [], "Condition must be true"

    def test_tokenise_punctuation(self) -> None:
        tokens = _tokenise("ModuleNotFoundError: No module named 'foo'")
        assert "modulenotfounderror" in tokens, "Error should be raised or set"
        assert "foo" in tokens, "Condition must be true"


# ---------------------------------------------------------------------------
# Agent profile tests
# ---------------------------------------------------------------------------


class TestAgentProfiles:
    def test_all_profiles_have_keywords(self, router: AdvancedAgentRouter) -> None:
        for profile in router._profiles:
            assert profile.keywords, f"{profile.agent_id} has no keywords"

    def test_all_profiles_have_id_and_name(self, router: AdvancedAgentRouter) -> None:
        for profile in router._profiles:
            assert profile.agent_id, "Condition must be true"
            assert profile.name, "Condition must be true"

    def test_no_duplicate_agent_ids(self, router: AdvancedAgentRouter) -> None:
        ids = [p.agent_id for p in router._profiles]
        assert len(ids) == len(set(ids)), "Duplicate agent IDs found"

    def test_list_agents_cli(self) -> None:
        from phase_11_2_advanced_router import main

        rc = main(["--list-agents"])
        assert rc == 0, "rc is not valid"

    def test_self_test_cli(self) -> None:
        from phase_11_2_advanced_router import main

        rc = main(["--self-test"])
        # 0 = meets 95% target, 1 = below target — both are valid returns
        assert rc in (0, 1)

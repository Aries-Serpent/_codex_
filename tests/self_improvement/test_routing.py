"""Tests for the Cognitive Brain middleware route planner."""

from codex.cognitive_brain.routing import RouteDecision, RouteRequest, RouteState, plan_route


def test_plan_uses_first_available_native_route() -> None:
    plan = plan_route(
        RouteRequest("github.read", "get_repository", "Aries-Serpent/_codex_"),
        {
            "github_mcp": RouteState.UNAVAILABLE,
            "vscode_github": RouteState.EXPOSED,
            "gh": RouteState.VERIFIED,
            "rest_graphql": RouteState.VERIFIED,
        },
    )

    assert plan.decision is RouteDecision.ALLOW
    assert plan.preferred_adapter == "gh"
    assert [candidate.adapter for candidate in plan.candidates] == [
        "github_mcp",
        "vscode_github",
        "gh",
        "rest_graphql",
        "playwright",
    ]


def test_documented_route_is_not_executable() -> None:
    plan = plan_route(
        RouteRequest("github.read", "get_repository", "Aries-Serpent/_codex_"),
        {"github_mcp": RouteState.DOCUMENTED, "rest_graphql": RouteState.VERIFIED},
    )

    assert plan.preferred_adapter == "rest_graphql"


def test_unknown_capability_is_denied() -> None:
    plan = plan_route(RouteRequest("unknown", "read", "target"), {})

    assert plan.decision is RouteDecision.DENY
    assert plan.preferred_adapter is None
    assert "unknown capability" in plan.reasons[0]


def test_write_route_is_dry_run_only_even_when_mutating_is_omitted() -> None:
    plan = plan_route(
        RouteRequest("github.write", "create_pull_request", "Aries-Serpent/_codex_"),
        {"gh": RouteState.VERIFIED},
    )

    assert plan.decision is RouteDecision.DRY_RUN_ONLY
    assert plan.preferred_adapter == "gh"
    assert not plan.execution_enabled


def test_destructive_action_on_read_capability_is_denied() -> None:
    plan = plan_route(
        RouteRequest("github.read", "delete_repository", "Aries-Serpent/_codex_"),
        {"github_mcp": RouteState.VERIFIED},
        allow_writes=True,
    )

    assert plan.decision is RouteDecision.DENY
    assert plan.preferred_adapter is None
    assert "unsupported action" in plan.reasons[0]


def test_denied_plan_has_no_preferred_adapter() -> None:
    plan = plan_route(
        RouteRequest("github.read", "get_repository", "Aries-Serpent/_codex_"),
        {"rest_graphql": RouteState.VERIFIED},
        allow_writes=False,
    )
    unavailable_plan = plan_route(
        RouteRequest("github.read", "unknown_action", "Aries-Serpent/_codex_"),
        {"rest_graphql": RouteState.VERIFIED},
    )

    assert plan.decision is RouteDecision.ALLOW
    assert unavailable_plan.decision is RouteDecision.DENY
    assert unavailable_plan.preferred_adapter is None


def test_agent_task_routes_are_registered_and_writes_remain_dry_run() -> None:
    from codex.cognitive_brain.routing import RouteRequest, plan_route

    read_plan = plan_route(
        RouteRequest("github.agent_tasks.read", "list_agent_tasks", "Aries-Serpent/_codex_"),
        {"github_mcp": RouteState.VERIFIED},
    )
    write_plan = plan_route(
        RouteRequest("github.write", "create_agent_task", "Aries-Serpent/_codex_"),
        {"github_mcp": RouteState.VERIFIED},
    )

    assert read_plan.decision is RouteDecision.ALLOW
    assert write_plan.decision is RouteDecision.DRY_RUN_ONLY


def test_custom_agent_resolver_maps_known_and_rejects_unknown_agents() -> None:
    from codex.cognitive_brain.routing import (
        resolve_custom_agent,
        resolve_custom_agent_route,
    )

    assert resolve_custom_agent("CI Failure Diagnostician") == "ci-failure-diagnostician"
    assert resolve_custom_agent_route("session-wrapup-autofix-agent") == (
        "github.write",
        "continue_agent_task",
    )
    assert resolve_custom_agent("unknown-agent") is None
    assert resolve_custom_agent_route("unknown-agent") is None

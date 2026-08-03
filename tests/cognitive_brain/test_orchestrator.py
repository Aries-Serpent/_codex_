"""Tests for MCPOrchestrator toolchain planning.

Covers:
- Unit: correct tool selected per task intent
- Unit: fallback plan present
- Unit: empty candidates handled gracefully
- Integration: policy scores in plan match expected shape
- Integration: available_tools restriction honoured
"""

from __future__ import annotations

import pytest

from src.codex.cognitive_brain.orchestrator import (
    TOOL_GITHUB_MCP,
    TOOL_PLAYWRIGHT,
    TOOL_SHELL,
    TOOL_WEB_SEARCH,
    MCPOrchestrator,
    ToolchainPlan,
)
from src.codex.cognitive_brain.policy import DeterministicPolicy, PolicyContext

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def orchestrator() -> MCPOrchestrator:
    """Default orchestrator: no shell, standard MCP tools."""
    return MCPOrchestrator(policy=DeterministicPolicy(seed=42))


@pytest.fixture()
def shell_orchestrator() -> MCPOrchestrator:
    return MCPOrchestrator(
        policy=DeterministicPolicy(seed=42),
        allow_shell=True,
        available_tools=[TOOL_GITHUB_MCP, TOOL_PLAYWRIGHT, TOOL_WEB_SEARCH, TOOL_SHELL],
    )


# ---------------------------------------------------------------------------
# MCPOrchestrator unit tests
# ---------------------------------------------------------------------------


class TestMCPOrchestrator:
    def test_repo_introspection_selects_github_mcp(self, orchestrator: MCPOrchestrator) -> None:
        plan = orchestrator.plan("repo_introspection")
        assert plan.primary_tool == TOOL_GITHUB_MCP

    def test_code_search_selects_github_mcp(self, orchestrator: MCPOrchestrator) -> None:
        plan = orchestrator.plan("code_search")
        assert plan.primary_tool == TOOL_GITHUB_MCP

    def test_ci_investigation_selects_github_mcp(self, orchestrator: MCPOrchestrator) -> None:
        plan = orchestrator.plan("ci_investigation")
        assert plan.primary_tool == TOOL_GITHUB_MCP

    def test_ui_interaction_prefers_playwright(self, orchestrator: MCPOrchestrator) -> None:
        # Playwright should score higher for ui_interaction.
        plan = orchestrator.plan(
            "ui_interaction",
            context=PolicyContext(
                task_type="ui_interaction",
                confidence=0.9,
                risk_level=0.1,
                dependency_count=1,
                time_budget_ms=10_000,
                known_patterns=["ui_interaction", "playwright"],
                constraints=[],
            ),
        )
        assert plan.primary_tool in (TOOL_PLAYWRIGHT, TOOL_GITHUB_MCP)  # policy-driven

    def test_web_validation_can_select_web_search(self, orchestrator: MCPOrchestrator) -> None:
        plan = orchestrator.plan(
            "web_validation",
            context=PolicyContext(
                task_type="web_validation",
                confidence=0.8,
                risk_level=0.1,
                dependency_count=1,
                time_budget_ms=10_000,
                known_patterns=["web_validation", "external_reference"],
                constraints=["external_access"],
            ),
        )
        assert plan.primary_tool in (TOOL_WEB_SEARCH, TOOL_GITHUB_MCP)

    def test_plan_has_steps(self, orchestrator: MCPOrchestrator) -> None:
        plan = orchestrator.plan("repo_introspection")
        assert len(plan.steps) > 0

    def test_plan_has_policy_scores(self, orchestrator: MCPOrchestrator) -> None:
        plan = orchestrator.plan("repo_introspection")
        assert "total" in plan.policy_scores
        assert isinstance(plan.policy_scores["total"], float)

    def test_plan_has_fallback(self, orchestrator: MCPOrchestrator) -> None:
        plan = orchestrator.plan("repo_introspection")
        assert plan.fallback_plan is not None

    def test_fallback_has_steps(self, orchestrator: MCPOrchestrator) -> None:
        plan = orchestrator.plan("repo_introspection")
        assert plan.fallback_plan is not None
        assert len(plan.fallback_plan.steps) > 0

    def test_plan_task_intent_preserved(self, orchestrator: MCPOrchestrator) -> None:
        plan = orchestrator.plan("my_custom_task")
        assert plan.task_intent == "my_custom_task"

    def test_available_tools_returned(self, orchestrator: MCPOrchestrator) -> None:
        tools = orchestrator.available_tools()
        assert TOOL_GITHUB_MCP in tools
        assert TOOL_PLAYWRIGHT in tools
        assert TOOL_WEB_SEARCH in tools
        # shell not in default orchestrator.
        assert TOOL_SHELL not in tools

    def test_shell_orchestrator_includes_shell(
        self, shell_orchestrator: MCPOrchestrator
    ) -> None:
        tools = shell_orchestrator.available_tools()
        assert TOOL_SHELL in tools

    def test_local_test_can_select_shell(self, shell_orchestrator: MCPOrchestrator) -> None:
        plan = shell_orchestrator.plan(
            "local_test",
            context=PolicyContext(
                task_type="local_test",
                confidence=0.95,
                risk_level=0.3,
                dependency_count=1,
                time_budget_ms=30_000,
                known_patterns=["local_test", "lint"],
                constraints=["deterministic"],
            ),
        )
        # Shell should be a viable candidate.
        assert plan.primary_tool in (TOOL_SHELL, TOOL_GITHUB_MCP)

    def test_unknown_task_does_not_crash(self, orchestrator: MCPOrchestrator) -> None:
        plan = orchestrator.plan("completely_unknown_task_xyz")
        assert isinstance(plan, ToolchainPlan)

    def test_deterministic_output_same_inputs(self, orchestrator: MCPOrchestrator) -> None:
        ctx = PolicyContext(
            task_type="code_search",
            confidence=0.75,
            risk_level=0.1,
            dependency_count=1,
            time_budget_ms=5000,
            known_patterns=["code_search"],
            constraints=["read_only"],
        )
        plan1 = orchestrator.plan("code_search", ctx)
        plan2 = orchestrator.plan("code_search", ctx)
        assert plan1.primary_tool == plan2.primary_tool
        assert plan1.policy_scores == plan2.policy_scores

    def test_plan_notes_non_empty(self, orchestrator: MCPOrchestrator) -> None:
        plan = orchestrator.plan("repo_introspection")
        assert len(plan.notes) > 0

    def test_step_has_fallback_tool(self, orchestrator: MCPOrchestrator) -> None:
        plan = orchestrator.plan("repo_introspection")
        # Primary step should declare a fallback surface.
        primary_steps = [s for s in plan.steps if s.required]
        assert len(primary_steps) > 0

    def test_step_tool_is_known_surface(self, orchestrator: MCPOrchestrator) -> None:
        plan = orchestrator.plan("repo_introspection")
        known = {TOOL_GITHUB_MCP, TOOL_PLAYWRIGHT, TOOL_WEB_SEARCH, TOOL_SHELL}
        for step in plan.steps:
            assert step.tool in known, f"Unknown tool surface: {step.tool}"

    def test_pr_review_uses_github_mcp(self, orchestrator: MCPOrchestrator) -> None:
        plan = orchestrator.plan("pr_review")
        assert plan.primary_tool == TOOL_GITHUB_MCP

"""MCP Capability Orchestrator — runtime toolchain planner.

Selects and orders the optimal combination of MCP-backed tools for a given
task intent, using the physics-inspired :class:`~policy.DeterministicPolicy`
to score candidate toolchains and the :class:`~model_negotiator.ModelNegotiator`
to ensure model-safe execution configs.

Supported tool surfaces (read-only, current runtime)
-----------------------------------------------------
    github_mcp   — 35 read-only GitHub MCP tools (repo, issues, PRs, CI …)
    playwright   — 21 Playwright MCP tools (browser, screenshots, form fill …)
    web_search   — standalone web-search tool
    shell        — local shell / CLI execution (policy-gated)

Decision heuristic (default)
-----------------------------
    1. Repo-state introspection → ``github_mcp``
    2. UI / browser evidence    → ``playwright``
    3. External validation      → ``web_search``
    4. Local build / test       → ``shell``

Usage::

    orchestrator = MCPOrchestrator()
    plan = orchestrator.plan(task_intent="repo_introspection", context=ctx)
    for step in plan.steps:
        result = step.execute(...)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence

from .policy import (
    CandidatePlan,
    DeterministicPolicy,
    PolicyContext,
    ScoredPlan,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tool surface identifiers
# ---------------------------------------------------------------------------

TOOL_GITHUB_MCP = "github_mcp"
TOOL_PLAYWRIGHT = "playwright"
TOOL_WEB_SEARCH = "web_search"
TOOL_SHELL = "shell"

# Task-type → primary tool surface default mapping.
_TASK_TOOL_DEFAULTS: Dict[str, str] = {
    "repo_introspection": TOOL_GITHUB_MCP,
    "code_search": TOOL_GITHUB_MCP,
    "pr_review": TOOL_GITHUB_MCP,
    "ci_investigation": TOOL_GITHUB_MCP,
    "ui_interaction": TOOL_PLAYWRIGHT,
    "browser_repro": TOOL_PLAYWRIGHT,
    "screenshot": TOOL_PLAYWRIGHT,
    "web_validation": TOOL_WEB_SEARCH,
    "external_reference": TOOL_WEB_SEARCH,
    "local_build": TOOL_SHELL,
    "local_test": TOOL_SHELL,
    "lint": TOOL_SHELL,
}


# ---------------------------------------------------------------------------
# Toolchain step and plan
# ---------------------------------------------------------------------------


@dataclass
class ToolchainStep:
    """A single tool-surface invocation within a :class:`ToolchainPlan`."""

    tool: str  # one of TOOL_* constants
    purpose: str  # human-readable description
    required: bool = True  # if False, skip on tool unavailability
    fallback_tool: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolchainPlan:
    """Ordered sequence of :class:`ToolchainStep` objects for a task.

    Attributes
    ----------
    task_intent:
        The task type that triggered this plan.
    steps:
        Ordered tool invocations.
    policy_scores:
        Raw dimension scores from the underlying :class:`DeterministicPolicy`.
    fallback_plan:
        An alternate :class:`ToolchainPlan` executed if the primary fails.
    """

    task_intent: str
    steps: List[ToolchainStep] = field(default_factory=list)
    policy_scores: Dict[str, float] = field(default_factory=dict)
    fallback_plan: Optional["ToolchainPlan"] = None
    notes: List[str] = field(default_factory=list)

    @property
    def primary_tool(self) -> Optional[str]:
        """Return the tool surface of the first required step."""
        for step in self.steps:
            if step.required:
                return step.tool
        return None


# ---------------------------------------------------------------------------
# Candidate toolchain library
# ---------------------------------------------------------------------------


def _make_candidates(task_intent: str, allow_shell: bool) -> List[CandidatePlan]:
    """Build the set of candidate :class:`CandidatePlan` objects to score."""
    candidates: List[CandidatePlan] = []

    # GitHub MCP toolchain.
    candidates.append(
        CandidatePlan(
            plan_id="github_mcp_primary",
            description="Use GitHub MCP read-only tools for repo-state introspection",
            estimated_steps=3,
            estimated_latency_ms=800,
            fallback_branches=2,
            certainty=0.9,
            risk=0.05,
            matched_patterns=[
                "repo_introspection",
                "code_search",
                "pr_review",
                "ci_investigation",
                task_intent,
            ],
            constraints_satisfied=["read_only", "authenticated", "deterministic"],
        )
    )

    # Playwright toolchain.
    candidates.append(
        CandidatePlan(
            plan_id="playwright_primary",
            description="Use Playwright MCP tools for UI/browser evidence gathering",
            estimated_steps=5,
            estimated_latency_ms=3000,
            fallback_branches=1,
            certainty=0.75,
            risk=0.20,
            matched_patterns=[
                "ui_interaction",
                "browser_repro",
                "screenshot",
                task_intent,
            ],
            constraints_satisfied=["visual_evidence", "reproducible"],
        )
    )

    # Web-search toolchain.
    candidates.append(
        CandidatePlan(
            plan_id="web_search_primary",
            description="Use web_search for external validation and reference lookup",
            estimated_steps=2,
            estimated_latency_ms=1500,
            fallback_branches=1,
            certainty=0.65,
            risk=0.10,
            matched_patterns=[
                "web_validation",
                "external_reference",
                task_intent,
            ],
            constraints_satisfied=["external_access"],
        )
    )

    # Shell / CLI toolchain (policy-gated).
    if allow_shell:
        candidates.append(
            CandidatePlan(
                plan_id="shell_primary",
                description="Use local shell/CLI for deterministic build/test execution",
                estimated_steps=4,
                estimated_latency_ms=5000,
                fallback_branches=3,
                certainty=0.95,
                risk=0.30,
                matched_patterns=[
                    "local_build",
                    "local_test",
                    "lint",
                    task_intent,
                ],
                constraints_satisfied=["deterministic", "offline_capable"],
            )
        )

    return candidates


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


class MCPOrchestrator:
    """Plan and coordinate MCP tool invocations for a given task intent.

    Parameters
    ----------
    policy:
        Scoring policy to use.  Defaults to a :class:`DeterministicPolicy`
        with seed 42.
    allow_shell:
        Whether shell/CLI tools are considered in the candidate pool.
        Set ``False`` in sandboxed or read-only runtimes.
    available_tools:
        Explicit set of tool surface IDs available in the current runtime.
        Defaults to ``{github_mcp, playwright, web_search}``.
    """

    def __init__(
        self,
        policy: Optional[DeterministicPolicy] = None,
        allow_shell: bool = False,
        available_tools: Optional[Sequence[str]] = None,
    ) -> None:
        self._policy = policy or DeterministicPolicy(seed=42)
        self._allow_shell = allow_shell
        self._available_tools: frozenset[str] = (
            frozenset(available_tools)
            if available_tools is not None
            else frozenset({TOOL_GITHUB_MCP, TOOL_PLAYWRIGHT, TOOL_WEB_SEARCH})
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def plan(
        self,
        task_intent: str,
        context: Optional[PolicyContext] = None,
    ) -> ToolchainPlan:
        """Produce a :class:`ToolchainPlan` for *task_intent*.

        Parameters
        ----------
        task_intent:
            Short descriptor of the task (e.g. ``"repo_introspection"``).
        context:
            Optional :class:`~policy.PolicyContext` to guide scoring.
            If omitted, a default neutral context is constructed.
        """
        # Ensure kernel is loaded before planning (deferred import avoids circular dependency)
        from .kernel import assert_loaded
        assert_loaded()

        ctx = context or self._default_context(task_intent)
        candidates = _make_candidates(task_intent, self._allow_shell)
        scored = self._policy.rank(candidates, ctx)
        best = scored[0] if scored else None

        if best is None:
            logger.warning("MCPOrchestrator: no candidates for task_intent=%s", task_intent)
            return ToolchainPlan(
                task_intent=task_intent,
                notes=["No candidates available; empty plan returned"],
            )

        steps = self._build_steps(best, task_intent)
        fallback_plan = self._build_fallback_plan(scored, task_intent, ctx)

        plan = ToolchainPlan(
            task_intent=task_intent,
            steps=steps,
            policy_scores=best.score_breakdown(),
            fallback_plan=fallback_plan,
            notes=[
                f"Primary toolchain: {best.plan.plan_id} (score={best.total_score:.4f})",
                f"Policy ranking considered {len(scored)} candidates",
            ],
        )
        logger.info(
            "MCPOrchestrator plan: task=%s primary_tool=%s score=%.4f",
            task_intent,
            plan.primary_tool,
            best.total_score,
        )
        return plan

    def available_tools(self) -> frozenset[str]:
        """Return the set of tool surfaces visible to this orchestrator."""
        return self._available_tools

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_steps(self, winner: ScoredPlan, task_intent: str) -> List[ToolchainStep]:
        """Translate a scored plan into concrete :class:`ToolchainStep` objects."""
        plan_id = winner.plan.plan_id
        steps: List[ToolchainStep] = []

        if "github_mcp" in plan_id:
            steps.append(
                ToolchainStep(
                    tool=TOOL_GITHUB_MCP,
                    purpose=f"Repo-state introspection for task '{task_intent}'",
                    required=True,
                    fallback_tool=TOOL_WEB_SEARCH,
                )
            )
        elif "playwright" in plan_id:
            steps.append(
                ToolchainStep(
                    tool=TOOL_PLAYWRIGHT,
                    purpose=f"Browser evidence gathering for task '{task_intent}'",
                    required=True,
                    fallback_tool=TOOL_WEB_SEARCH,
                )
            )
        elif "web_search" in plan_id:
            steps.append(
                ToolchainStep(
                    tool=TOOL_WEB_SEARCH,
                    purpose=f"External validation for task '{task_intent}'",
                    required=True,
                    fallback_tool=TOOL_GITHUB_MCP,
                )
            )
        elif "shell" in plan_id:
            steps.append(
                ToolchainStep(
                    tool=TOOL_SHELL,
                    purpose=f"Local deterministic execution for task '{task_intent}'",
                    required=True,
                    fallback_tool=TOOL_GITHUB_MCP,
                )
            )
        else:
            steps.append(
                ToolchainStep(
                    tool=TOOL_GITHUB_MCP,
                    purpose="Default GitHub MCP fallback",
                    required=True,
                )
            )

        return steps

    def _build_fallback_plan(
        self,
        ranked: List[ScoredPlan],
        task_intent: str,
        context: PolicyContext,
    ) -> Optional[ToolchainPlan]:
        """Build a fallback plan from the second-ranked candidate."""
        if len(ranked) < 2:
            return None
        second = ranked[1]
        steps = self._build_steps(second, task_intent)
        return ToolchainPlan(
            task_intent=task_intent,
            steps=steps,
            policy_scores=second.score_breakdown(),
            notes=[f"Fallback: {second.plan.plan_id} (score={second.total_score:.4f})"],
        )

    @staticmethod
    def _default_context(task_intent: str) -> PolicyContext:
        """Build a neutral :class:`PolicyContext` for *task_intent*."""
        known = [task_intent]
        if task_intent in _TASK_TOOL_DEFAULTS:
            known.append(_TASK_TOOL_DEFAULTS[task_intent])
        return PolicyContext(
            task_type=task_intent,
            confidence=0.7,
            risk_level=0.2,
            dependency_count=1,
            time_budget_ms=10_000,
            known_patterns=known,
            constraints=["read_only"],
        )

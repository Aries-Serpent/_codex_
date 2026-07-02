"""Shared helpers for the personalized Copilot campaign CLI surfaces."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class TaskRoutingDecision:
    """Decision describing whether a workflow should use bash or the task agent."""

    command: str
    category: str
    recommended_runner: str
    recommended_agent: str
    rationale: str
    prompt_template: str

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-serializable representation."""
        return asdict(self)


@dataclass(frozen=True)
class AgentChainStep:
    """Single step in a specialized agent chain."""

    order: int
    agent: str
    purpose: str
    prompt_template: str


@dataclass(frozen=True)
class AgentChainPlan:
    """Ordered plan for chaining specialized agents."""

    focus: str
    summary: str
    steps: list[AgentChainStep] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return {
            "focus": self.focus,
            "summary": self.summary,
            "steps": [asdict(step) for step in self.steps],
        }


_TASK_KEYWORDS = (
    "pytest",
    "nox",
    "ruff",
    "mypy",
    "pre-commit",
    "pip install",
    "npm install",
    "go test",
    "cargo test",
    "python -m pytest",
    "python scripts/ci/auto_fix_common_issues.py",
)

_BASH_KEYWORDS = ("rg ", "grep ", "find ", "cat ", "sed ", "awk ")

_CHAIN_LIBRARY: dict[str, AgentChainPlan] = {
    "codeql": AgentChainPlan(
        focus="codeql",
        summary="Resolve security findings with the dedicated CodeQL-first chain.",
        steps=[
            AgentChainStep(
                order=1,
                agent="codeql-alert-resolution-agent",
                purpose="Fix open CodeQL findings with targeted code changes.",
                prompt_template=(
                    "Fix all open CodeQL alerts for this branch and summarize each " "remediation."
                ),
            ),
            AgentChainStep(
                order=2,
                agent="code-scanning-remediation-agent",
                purpose="Sweep remaining code scanning findings and normalize fixes.",
                prompt_template=(
                    "Review remaining code scanning findings after CodeQL "
                    "remediation and close any valid gaps."
                ),
            ),
        ],
    ),
    "security": AgentChainPlan(
        focus="security",
        summary="Use the security scanner + remediation chain for dependency and GHAS issues.",
        steps=[
            AgentChainStep(
                order=1,
                agent="unified-security-scanner",
                purpose="Collect dependency, secrets, and SAST findings in one pass.",
                prompt_template=(
                    "Run a unified security scan and summarize the actionable " "findings only."
                ),
            ),
            AgentChainStep(
                order=2,
                agent="code-scanning-remediation-agent",
                purpose="Apply code-level remediation to valid findings.",
                prompt_template=(
                    "Remediate the actionable findings from the unified "
                    "security scan and explain what changed."
                ),
            ),
        ],
    ),
    "ci": AgentChainPlan(
        focus="ci",
        summary="Use the CI healing chain before manual debugging loops.",
        steps=[
            AgentChainStep(
                order=1,
                agent="ci-auto-healer-agent",
                purpose="Apply recurring CI fix patterns and produce diagnostics.",
                prompt_template=(
                    "Diagnose the failing CI jobs and auto-apply all safe fix " "patterns."
                ),
            ),
            AgentChainStep(
                order=2,
                agent="autonomous-test-healer-agent",
                purpose="Repair remaining failing tests after CI stabilization.",
                prompt_template=(
                    "Fix the remaining failing tests after the CI auto-healer "
                    "pass and report the root causes."
                ),
            ),
        ],
    ),
    "coverage": AgentChainPlan(
        focus="coverage",
        summary="Use the unified coverage specialist instead of ad-hoc coverage work.",
        steps=[
            AgentChainStep(
                order=1,
                agent="unified-coverage-agent",
                purpose="Prioritize the highest-impact coverage gaps and propose safe tests.",
                prompt_template=(
                    "Increase coverage in the touched modules without changing "
                    "production behavior."
                ),
            ),
        ],
    ),
    "docs": AgentChainPlan(
        focus="docs",
        summary="Use the unified documentation chain for multi-file documentation upkeep.",
        steps=[
            AgentChainStep(
                order=1,
                agent="unified-doc-agent",
                purpose="Coordinate doc freshness, consolidation, and link cleanup.",
                prompt_template=(
                    "Update the relevant documentation to match the "
                    "implementation and fix broken references."
                ),
            ),
        ],
    ),
    "orchestration": AgentChainPlan(
        focus="orchestration",
        summary="Use the cognitive/orchestrator chain for multi-step repository work.",
        steps=[
            AgentChainStep(
                order=1,
                agent="cognitive-brain-cli-agent",
                purpose="Translate the high-level goal into CLI-driven execution steps.",
                prompt_template=(
                    "Plan and execute this workflow through the Codex CLI and "
                    "report the checkpoints."
                ),
            ),
            AgentChainStep(
                order=2,
                agent="agent-orchestrator",
                purpose="Coordinate any required follow-on specialist agents.",
                prompt_template=(
                    "Orchestrate the remaining specialized agents needed to "
                    "complete the workflow safely."
                ),
            ),
        ],
    ),
}


def recommend_task_route(command: str, category: str | None = None) -> TaskRoutingDecision:
    """Recommend whether a user should use bash or the task agent."""

    normalized = command.strip().lower()
    resolved_category = (category or "").strip().lower()

    if resolved_category in {"deterministic", "ci", "validation", "install"} or any(
        keyword in normalized for keyword in _TASK_KEYWORDS
    ):
        return TaskRoutingDecision(
            command=command,
            category=resolved_category or "deterministic",
            recommended_runner="task",
            recommended_agent="task",
            rationale=(
                "This command is deterministic and high-volume, so the task agent can "
                "compress success output while preserving failures."
            ),
            prompt_template=(
                f"Run this deterministically and summarize success/failure: " f'"{command}"'
            ),
        )

    if resolved_category in {"exploration", "research"} or any(
        keyword in normalized for keyword in _BASH_KEYWORDS
    ):
        return TaskRoutingDecision(
            command=command,
            category=resolved_category or "exploration",
            recommended_runner="bash",
            recommended_agent="direct-cli",
            rationale=(
                "This command is exploratory or inspection-heavy, so direct bash output "
                "is easier to iterate on than a compressed task-agent response."
            ),
            prompt_template=f'Run directly in bash while investigating: "{command}"',
        )

    return TaskRoutingDecision(
        command=command,
        category=resolved_category or "general",
        recommended_runner="general-purpose",
        recommended_agent="general-purpose",
        rationale=(
            "This looks multi-step or ambiguous, so a general-purpose agent gives better "
            "reasoning and state management than raw bash."
        ),
        prompt_template=f'Handle this end-to-end with explicit reasoning: "{command}"',
    )


def build_agent_chain(focus: str) -> AgentChainPlan:
    """Return the recommended specialized-agent chain for a workflow focus."""

    normalized = focus.strip().lower()
    if normalized not in _CHAIN_LIBRARY:
        available = ", ".join(sorted(_CHAIN_LIBRARY))
        raise ValueError(f"Unknown focus '{focus}'. Available focuses: {available}")
    return _CHAIN_LIBRARY[normalized]

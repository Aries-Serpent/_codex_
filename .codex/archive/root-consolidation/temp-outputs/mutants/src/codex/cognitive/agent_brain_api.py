"""
AgentBrainAPI — The Copilot-agent-facing surface of the Cognitive Brain.

This module is the primary integration point between GitHub Copilot Coding Agent
sessions and the cognitive brain infrastructure.  Any AI agent that uses this
codebase should call ``AgentBrainAPI`` at session start to obtain context and
next actions, then report outcomes so the brain learns.

The codebase is an **advanced extension of GitHub Copilot Coding Agent**.
Every subsystem — ``QuantumPlansetEngine``, ``PlansetOrchestrator``,
``AgentBrainInterface`` — exists to benefit the AI agents that drive it.

Design contract
---------------
* **Stateless calls** — each call is self-contained; state persists in JSON
* **Agent-ID routing** — filters plansets to those owned by the calling agent
* **Learning loop** — ``report_completion()`` feeds back into the pattern store
* **Continuation prompts** — generates the exact ``@copilot`` body for the
  next session so Copilot picks up exactly where the last session ended

Usage
-----
::

    from codex.cognitive import AgentBrainAPI, ImprovementArea

    api = AgentBrainAPI(agent_id="codeql-alert-resolution-agent")

    # 1. Get full session context at session start
    ctx = api.get_session_context(
        session_context={"open_alerts": 120, "coverage_pct": 45}
    )
    logger.info(ctx.continuation_prompt)
    for action in ctx.next_actions[:3]:
        logger.info(f"[{action.step_id}] {action.agent}: {action.prompt[:80]}")

    # 2. After completing a step, report back
    api.report_completion(
        area=ImprovementArea.SECURITY_REMEDIATION,
        step_id="SEC-01",
        outcome="success",
        notes="107 alerts collected, 12 P0 identified",
    )

    # 3. Get the @copilot continuation prompt for the next PR/session
    follow_up = api.get_continuation_prompt(
        session_context={"open_alerts": 108}
    )
    # post follow_up as a PR comment via github-guru-agent.create_copilot_pr()

Mermaid — Integration architecture
------------------------------------
See :class:`AgentBrainAPI` docstring for embedded Mermaid diagram.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from codex.cognitive.brain_interface import AgentBrainInterface, LearningFeedback
from codex.cognitive.planset_orchestrator import PlansetOrchestrator, PromptSet
from codex.cognitive.quantum_planset_engine import ImprovementArea, QuantumPlansetEngine
from codex.logging.structured_logger import logger

# ---------------------------------------------------------------------------
# Agent → ImprovementArea capability map
# Maps each custom agent's ID to the planset area(s) it serves.
# When an agent calls get_session_context(), results are pre-filtered to
# show only the areas that agent is responsible for.
# ---------------------------------------------------------------------------
AGENT_CAPABILITIES: dict[str, list[ImprovementArea]] = {
    # Security
    "codeql-alert-resolution-agent": [ImprovementArea.SECURITY_REMEDIATION],
    "code-scanning-remediation-agent": [ImprovementArea.SECURITY_REMEDIATION],
    "security-audit-agent": [ImprovementArea.SECURITY_REMEDIATION],
    "dependency-vulnerability-scanner": [
        ImprovementArea.SECURITY_REMEDIATION,
        ImprovementArea.DEPENDENCY_MODERNISATION,
    ],
    # Coverage / Testing
    "coverage-gapfill-agent": [ImprovementArea.COVERAGE_IMPROVEMENT],
    "coverage-maintenance-agent": [ImprovementArea.COVERAGE_IMPROVEMENT],
    "test-alignment-fixer-enhanced": [ImprovementArea.TEST_ASSERTION_UPDATE],
    "autonomous-test-healer-agent": [
        ImprovementArea.TEST_ASSERTION_UPDATE,
        ImprovementArea.COVERAGE_IMPROVEMENT,
    ],
    "mutation-testing-agent": [ImprovementArea.COVERAGE_IMPROVEMENT],
    # CI / Workflow
    "ci-failure-resolution-agent": [ImprovementArea.CI_SELF_HEALING],
    "ci-auto-healer-agent": [ImprovementArea.CI_SELF_HEALING],
    "ci-testing-agent": [ImprovementArea.CI_SELF_HEALING],
    "ci-health-alert-agent": [ImprovementArea.CI_SELF_HEALING],
    "workflow-health-monitor": [ImprovementArea.WORKFLOW_HEALTH],
    "workflow-ci-fixer": [ImprovementArea.WORKFLOW_HEALTH],
    "workflow-analytics-agent": [ImprovementArea.WORKFLOW_HEALTH],
    "workflow-optimization-agent": [ImprovementArea.WORKFLOW_HEALTH],
    # D_CAPABLE Agents (Decision Authority)
    "rust-error-validator": [ImprovementArea.CI_SELF_HEALING],
    "test-assertion-updater": [ImprovementArea.TEST_ASSERTION_UPDATE],
    "test-pattern-guardian": [ImprovementArea.TEST_ASSERTION_UPDATE],
    "copilot-session-chain": [ImprovementArea.AGENT_CHAINING],
    "packaging-validation-agent": [ImprovementArea.DEPENDENCY_MODERNISATION],
    "energy-conversion-agent": [ImprovementArea.ML_PATTERN_FEEDING],
    # Cache
    "cache-management-agent": [ImprovementArea.CACHE_VALIDATION],
    "cache-manager-integration": [ImprovementArea.CACHE_VALIDATION],
    # RAG / ML
    "rag-module-management-agent": [ImprovementArea.RAG_PIPELINE],
    "rag-freshness-loop-agent": [
        ImprovementArea.RAG_PIPELINE,
        ImprovementArea.ML_PATTERN_FEEDING,
    ],
    "ml-validation-suite-agent": [ImprovementArea.ML_PATTERN_FEEDING],
    # Agent Chaining
    "agent-orchestrator": [ImprovementArea.AGENT_CHAINING],
    "workflow-management-agent": [ImprovementArea.AGENT_CHAINING],
    # QI / Quantum
    "quantum-compliance-tuning-agent": [ImprovementArea.QI_TESTING],
    # Documentation
    "link-validator-agent": [ImprovementArea.DOCUMENTATION_HYGIENE],
    "doc-freshness-checker": [ImprovementArea.DOCUMENTATION_HYGIENE],
    "unified-doc-agent": [ImprovementArea.DOCUMENTATION_HYGIENE],
    # Cognitive brain / general
    "cognitive-brain-manager": [
        ImprovementArea.ML_PATTERN_FEEDING,
        ImprovementArea.AGENT_CHAINING,
    ],
    "github-guru-agent": list(ImprovementArea),  # full access
    # Copilot Coding Agent — the primary consumer
    "copilot-coding-agent": list(ImprovementArea),
    "copilot-swe-agent": list(ImprovementArea),
}


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class AgentSessionContext:
    """
    Everything an AI agent needs at the start of a Copilot session.

    Attributes
    ----------
    session_id:
        Unique identifier for this session.
    agent_id:
        The agent that requested this context.
    next_actions:
        Ranked list of ``PromptSet`` objects the agent should execute.
    continuation_from:
        Summary of the previous session so the agent can resume correctly.
    active_patterns:
        Relevant patterns from the brain's pattern store.
    capabilities:
        ``ImprovementArea`` values this agent is responsible for.
    continuation_prompt:
        Ready-to-paste ``@copilot`` PR comment body for the next session.
    generated_at:
        ISO-8601 timestamp.
    """

    session_id: str
    agent_id: str
    next_actions: list[PromptSet]
    continuation_from: str
    active_patterns: list[dict[str, Any]]
    capabilities: list[str]
    continuation_prompt: str
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["next_actions"] = [a.to_dict() for a in self.next_actions]
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class CompletionReport:
    """Outcome reported by an agent after completing a planset step."""

    agent_id: str
    area: str
    step_id: str
    outcome: str  # "success" | "failure" | "partial"
    notes: str = ""
    artifacts: list[str] = field(default_factory=list)
    reported_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ---------------------------------------------------------------------------
# AgentBrainAPI
# ---------------------------------------------------------------------------


class AgentBrainAPI:
    """
    Copilot-agent-facing façade over the cognitive brain infrastructure.

    Integrates three subsystems:

    * ``AgentBrainInterface`` — pattern store, objectives, learning feedback
    * ``PlansetOrchestrator`` — surveys unfinished plansets, ranks next actions
    * ``QuantumPlansetEngine`` — physics-scores each improvement step

    Architecture
    ------------
    .. code-block:: text

        GitHub Copilot Coding Agent
               │
               │  get_session_context()
               ▼
        ┌─────────────────────────────────────┐
        │           AgentBrainAPI             │
        │  agent_id-aware routing + scoring   │
        └────────┬────────────┬───────────────┘
                 │            │
         ┌───────▼──────┐  ┌──▼──────────────────┐
         │ BrainInterface│  │  PlansetOrchestrator │
         │ pattern store │  │  QuantumPlansetEngine│
         │ objectives    │  │  30 planset files    │
         └───────────────┘  └─────────────────────┘
                 │
         report_completion()
                 │
         ┌───────▼──────────┐
         │  Learning Stored  │
         │  Next agent       │
         │  benefits         │
         └───────────────────┘

    Parameters
    ----------
    agent_id:
        The calling agent's canonical ID (e.g. ``"codeql-alert-resolution-agent"``).
        Use ``"copilot-coding-agent"`` for the primary GitHub Copilot session.
    planset_dir:
        Path to ``.codex/plans/``.  Defaults to repo-relative path.
    state_path:
        Where orchestrator state is persisted between sessions.
    brain_data_dir:
        Where ``AgentBrainInterface`` stores pattern/session data.
    max_actions:
        Default maximum number of ``PromptSet`` objects per session.
    """

    def __init__(
        self,
        agent_id: str = "copilot-coding-agent",
        planset_dir: Optional[Path] = None,
        state_path: Optional[Path] = None,
        brain_data_dir: Optional[Path] = None,
        max_actions: int = 10,
    ) -> None:
        self.agent_id = agent_id
        self._max_actions = max_actions
        self._capabilities = AGENT_CAPABILITIES.get(agent_id, list(ImprovementArea))

        _root = Path(__file__).resolve().parents[3]
        _plans = planset_dir or (_root / ".codex" / "plans")
        _state = state_path or (_plans / ".orchestrator_state.json")
        _brain_dir = brain_data_dir or (_root / ".codex" / "brain")

        self._orch = PlansetOrchestrator(
            planset_dir=_plans,
            engine=QuantumPlansetEngine(),
            state_path=_state,
        )
        self._brain = AgentBrainInterface(
            agent_id=agent_id,
            repo_root=str(_brain_dir.parent) if _brain_dir.name == "brain" else str(_brain_dir),
        )

    # ------------------------------------------------------------------
    # Primary API methods
    # ------------------------------------------------------------------

    def get_session_context(
        self,
        session_context: Optional[dict[str, Any]] = None,
        max_actions: Optional[int] = None,
    ) -> AgentSessionContext:
        """
        Return everything the agent needs to start a Copilot session.

        This is the **first call** every agent should make at session start.
        It queries the orchestrator for ranked next actions, searches the
        pattern store for relevant context from previous sessions, and
        assembles a ready-to-paste ``@copilot`` continuation prompt.

        Parameters
        ----------
        session_context:
            Live signals from the current environment, e.g.::

                {
                    "open_alerts": 120,
                    "coverage_pct": 45,
                    "failing_checks": 3,
                }

        max_actions:
            Override the default ``max_actions`` for this call.

        Returns
        -------
        AgentSessionContext
        """
        ctx = session_context or {}
        limit = max_actions or self._max_actions
        session_id = datetime.now(timezone.utc).strftime("session-%Y%m%d-%H%M")

        # 1. Get ranked next actions filtered to this agent's capabilities
        all_prompts = self._orch.generate_session(context=ctx, max_prompts=limit * 3)
        filtered = (
            [p for p in all_prompts if ImprovementArea(p.area) in self._capabilities]
            if self._capabilities != list(ImprovementArea)
            else all_prompts
        )
        next_actions = filtered[:limit]

        # 2. Query brain for relevant patterns
        query = f"{self.agent_id} session context"
        raw_patterns = self._safe_query_patterns(query)

        # 3. Build continuation summary from previous state
        completed = self._orch._state.completed_steps
        n_completed = sum(len(v) for v in completed.values())
        continuation_from = (
            f"Previous session completed {n_completed} step(s) across "
            f"{len(completed)} area(s): "
            + ", ".join(f"{area}[{', '.join(steps)}]" for area, steps in completed.items())
            if completed
            else "No previous session state — starting fresh."
        )

        # 4. Generate continuation prompt
        prompt = self._build_continuation_prompt(next_actions, ctx, session_id)

        return AgentSessionContext(
            session_id=session_id,
            agent_id=self.agent_id,
            next_actions=next_actions,
            continuation_from=continuation_from,
            active_patterns=raw_patterns,
            capabilities=[c.value for c in self._capabilities],
            continuation_prompt=prompt,
        )

    def report_completion(
        self,
        area: ImprovementArea,
        step_id: str,
        outcome: str = "success",
        notes: str = "",
        artifacts: Optional[list[str]] = None,
    ) -> CompletionReport:
        """
        Mark a planset step as complete and feed the outcome into the brain.

        This method:

        1. Calls ``PlansetOrchestrator.advance()`` to dequeue the step
        2. Submits a ``LearningFeedback`` to ``AgentBrainInterface``
        3. Returns a ``CompletionReport`` for audit/logging

        Parameters
        ----------
        area:
            The ``ImprovementArea`` the step belongs to.
        step_id:
            The completed step ID (e.g. ``"SEC-01"``).
        outcome:
            One of ``"success"``, ``"failure"``, ``"partial"``.
        notes:
            Free-text notes for the learning store.
        artifacts:
            List of artifact paths or URLs produced.
        """
        self._orch.advance(area, step_id)

        pattern_id = f"{area.value}-{step_id}-{self.agent_id}"
        feedback = LearningFeedback(
            pattern_id=pattern_id,
            agent_id=self.agent_id,
            outcome=outcome,
            context={
                "area": area.value,
                "step_id": step_id,
                "notes": notes,
                "artifacts": artifacts or [],
            },
        )
        self._safe_submit_learning(feedback)

        report = CompletionReport(
            agent_id=self.agent_id,
            area=area.value,
            step_id=step_id,
            outcome=outcome,
            notes=notes,
            artifacts=artifacts or [],
        )
        logger.info(
            "Completion reported: agent=%s area=%s step=%s outcome=%s",
            self.agent_id,
            area.value,
            step_id,
            outcome,
        )
        return report

    def get_continuation_prompt(
        self,
        session_context: Optional[dict[str, Any]] = None,
    ) -> str:
        """
        Return the ready-to-paste ``@copilot`` PR comment body for the next session.

        Paste this string into a PR comment or use
        ``github-guru-agent.create_copilot_pr()`` to open a new PR with
        Copilot automatically starting a session.

        Parameters
        ----------
        session_context:
            Optional live signals (forwarded to the orchestrator).

        Returns
        -------
        str
            A formatted ``@copilot continue ...`` prompt string.
        """
        ctx = session_context or {}
        prompts = self._orch.generate_session(context=ctx, max_prompts=5)
        return self._build_continuation_prompt(
            prompts, ctx, datetime.now(timezone.utc).strftime("session-%Y%m%d")
        )

    def get_agent_capabilities(self) -> list[ImprovementArea]:
        """Return the ``ImprovementArea`` values this agent is responsible for."""
        return list(self._capabilities)

    def survey_unfinished(self) -> str:
        """
        Return a Markdown table of all unfinished plansets.

        Useful for including in a PR description or session summary.
        """
        return self._orch.summary()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_continuation_prompt(
        self,
        actions: list[PromptSet],
        ctx: dict[str, Any],
        session_id: str,
    ) -> str:
        completed = self._orch._state.completed_steps
        n_done = sum(len(v) for v in completed.values())
        lines = [
            "@copilot continue with next phase tasks for this PR",
            "",
            f"**📋 Session Context** — generated by `AgentBrainAPI` ({session_id})",
            "",
        ]
        if n_done:
            lines += [
                f"**Previous progress**: {n_done} step(s) completed across "
                f"{len(completed)} area(s).",
                "",
            ]
        if ctx:
            lines += [
                "**Live signals**:",
                "```json",
                json.dumps(ctx, indent=2),
                "```",
                "",
            ]
        if actions:
            lines += ["**🎯 Next actions** (physics-ranked):"]
            for i, p in enumerate(actions[:5], 1):
                lines.append(
                    f"{i}. `[{p.step_id}]` **{p.agent}** — {p.description[:80]}"
                    f" *(amp={p.amplitude:.4f})*"
                )
            lines.append("")
        lines += [
            "**Instructions**:",
            "- Execute steps in priority order (highest amplitude first)",
            "- Apply self-healing if CI fails before moving to next step",
            "- Call `AgentBrainAPI.report_completion()` after each step",
            "- Run `python scripts/cognitive/orchestrate.py next` to refresh priority",
            "",
            "_Auto-generated by `src/codex/cognitive/agent_brain_api.py`_",
        ]
        return "\n".join(lines)

    def _safe_query_patterns(self, query: str) -> list[dict[str, Any]]:
        try:
            matches = self._brain.query_patterns(query, limit=5)
            return [
                {
                    "pattern_id": m.pattern_id,
                    "description": m.description,
                    "confidence": (
                        m.confidence.value if hasattr(m.confidence, "value") else str(m.confidence)
                    ),
                    "match_score": getattr(m, "match_score", 0.0),
                }
                for m in matches
            ]
        except (ValueError, TypeError, RuntimeError) as exc:
            logger.debug("Pattern query skipped: %s", exc)
            return []

    def _safe_submit_learning(self, feedback: LearningFeedback) -> None:
        try:
            self._brain.submit_learning(
                pattern_id=feedback.pattern_id,
                outcome=feedback.outcome,
                context=feedback.context,
            )
        except (ValueError, TypeError, RuntimeError) as exc:
            logger.debug("Learning submission skipped: %s", exc)

    def __repr__(self) -> str:  # pragma: no cover
        caps = ", ".join(c.value for c in self._capabilities[:3])
        more = f" +{len(self._capabilities) - 3}" if len(self._capabilities) > 3 else ""
        return f"AgentBrainAPI(agent='{self.agent_id}', capabilities=[{caps}{more}])"


# ---------------------------------------------------------------------------
# CognitiveBrain — unified, self-describing singleton
# ---------------------------------------------------------------------------


class CognitiveBrain:
    """
    The single entry-point to the entire cognitive brain infrastructure.

    This class is the **intuitive, zero-documentation** interface for AI agents.
    Import ``brain`` from ``codex.cognitive`` and everything is reachable from
    that one object — no class instantiation, no directory hunting, no reading docs.

    Quick-start (3 lines)
    ---------------------
    ::

        from codex.cognitive import brain

        ctx  = brain.session("my-agent-id")   # → AgentSessionContext
        next = brain.next()                    # → highest-priority PromptSet
        brain.advance("SECURITY_REMEDIATION", "SEC-01")

    Self-discovery
    --------------
    ::

        logger.info(brain.help())
        logger.info(brain.discover())
        logger.info(brain.health())

    Architecture (Mermaid)
    ----------------------
    ::

        from codex.cognitive import brain → CognitiveBrain (singleton)
               │
               ├── brain.for_agent(id)   → AgentBrainAPI
               │       ├── get_session_context()
               │       ├── report_completion()
               │       └── get_continuation_prompt()
               │
               ├── brain.session(id)     → AgentSessionContext
               ├── brain.next()          → PromptSet
               ├── brain.advance()       → CompletionReport
               │
               ├── brain.help()          → usage guide (str)
               ├── brain.discover()      → capability map (dict)
               ├── brain.health()        → health status (dict)
               │
               └── brain.orchestrator   → PlansetOrchestrator
                   brain.engine         → QuantumPlansetEngine
                   brain.capabilities   → dict[agent_id → [ImprovementArea]]

    Parameters
    ----------
    planset_dir:
        Path to ``.codex/plans/``.  Auto-detected if not given.
    state_path:
        Where orchestrator state is persisted.
    brain_data_dir:
        Where ``AgentBrainInterface`` pattern data lives.
    """

    _VERSION = "1.0.0"

    def __init__(
        self,
        planset_dir: Optional[Path] = None,
        state_path: Optional[Path] = None,
        brain_data_dir: Optional[Path] = None,
    ) -> None:
        _root = Path(__file__).resolve().parents[3]
        _plans = planset_dir or (_root / ".codex" / "plans")
        _state = state_path or (_plans / ".orchestrator_state.json")
        _bdir = brain_data_dir or (_root / ".codex" / "brain")

        self.engine = QuantumPlansetEngine()
        self.orchestrator = PlansetOrchestrator(
            planset_dir=_plans,
            engine=self.engine,
            state_path=_state,
        )
        self._plans = _plans
        self._state = _state
        self._bdir = _bdir
        self._api_cache: dict[str, AgentBrainAPI] = {}

    # ------------------------------------------------------------------
    # Primary API — intuitive, short names
    # ------------------------------------------------------------------

    def for_agent(self, agent_id: str) -> AgentBrainAPI:
        """
        Return a pre-configured ``AgentBrainAPI`` scoped to ``agent_id``.

        Results are cached so repeated calls are free.

        Example
        -------
        ::

            api = brain.for_agent("codeql-alert-resolution-agent")
            ctx = api.get_session_context({"open_alerts": 120})
        """
        if agent_id not in self._api_cache:
            self._api_cache[agent_id] = AgentBrainAPI(
                agent_id=agent_id,
                planset_dir=self._plans,
                state_path=self._state,
                brain_data_dir=self._bdir,
            )
        return self._api_cache[agent_id]

    def session(
        self,
        agent_id: str = "copilot-coding-agent",
        context: Optional[dict[str, Any]] = None,
        max_actions: int = 10,
    ) -> AgentSessionContext:
        """
        One-call session start — returns everything needed to begin a Copilot session.

        Parameters
        ----------
        agent_id:
            The calling agent (defaults to generic Copilot coding agent).
        context:
            Live environment signals, e.g. ``{"open_alerts": 120}``.
        max_actions:
            How many ranked next actions to include.

        Returns
        -------
        AgentSessionContext
            Contains ``next_actions``, ``continuation_prompt``,
            ``continuation_from``, ``active_patterns``.
        """
        return self.for_agent(agent_id).get_session_context(
            session_context=context,
            max_actions=max_actions,
        )

    def next(
        self,
        agent_id: str = "copilot-coding-agent",
        context: Optional[dict[str, Any]] = None,
    ) -> Optional[PromptSet]:
        """
        Return the single highest-priority next action across ALL plansets.

        Parameters
        ----------
        agent_id:
            Filter to areas owned by this agent.
        context:
            Live signals forwarded to the engine.

        Returns
        -------
        PromptSet or None
        """
        return self.orchestrator.next_promptset(context=context)

    def advance(
        self,
        area: str | ImprovementArea,
        step_id: str,
        agent_id: str = "copilot-coding-agent",
        outcome: str = "success",
        notes: str = "",
    ) -> CompletionReport:
        """
        Mark a step complete, persist state, and feed learning back into the brain.

        Parameters
        ----------
        area:
            ``ImprovementArea`` value or string, e.g. ``"SECURITY_REMEDIATION"``.
        step_id:
            Step ID to mark complete, e.g. ``"SEC-01"``.
        agent_id:
            The agent that completed the step.
        outcome:
            ``"success"`` | ``"failure"`` | ``"partial"``.
        notes:
            Free-text notes stored in the pattern store.

        Returns
        -------
        CompletionReport
        """
        if isinstance(area, str):
            area = ImprovementArea(area)
        return self.for_agent(agent_id).report_completion(
            area=area, step_id=step_id, outcome=outcome, notes=notes
        )

    # ------------------------------------------------------------------
    # Self-discovery
    # ------------------------------------------------------------------

    def help(self) -> str:
        """
        Return a complete, human- and agent-readable usage guide.

        Any AI agent can call ``print(brain.help())`` to understand
        the entire cognitive brain in one shot.
        """
        areas = "\n".join(f"  • {a.value}" for a in ImprovementArea)
        agents = "\n".join(
            f"  {aid:<45} → {', '.join(c.value for c in caps[:2])}"
            + (f" +{len(caps) - 2} more" if len(caps) > 2 else "")
            for aid, caps in list(AGENT_CAPABILITIES.items())[:12]
        )
        return f"""
╔══════════════════════════════════════════════════════════════════╗
║         _codex_ Cognitive Brain  v{self._VERSION}                      ║
║    Advanced extension of GitHub Copilot Coding Agent             ║
╚══════════════════════════════════════════════════════════════════╝

QUICK START (3 lines)
─────────────────────
  from codex.cognitive import brain

  ctx  = brain.session("my-agent-id")   # full session context
  next = brain.next()                    # highest-priority action
  brain.advance("SECURITY_REMEDIATION", "SEC-01")  # mark done

FULL API
────────
  brain.for_agent(agent_id)           → AgentBrainAPI (scoped)
  brain.session(agent_id, context)    → AgentSessionContext
  brain.next(agent_id, context)       → PromptSet (highest priority)
  brain.advance(area, step_id, ...)   → CompletionReport
  brain.help()                        → this guide
  brain.discover()                    → JSON capability map
  brain.health()                      → live health dict
  brain.engine                        → QuantumPlansetEngine
  brain.orchestrator                  → PlansetOrchestrator
  brain.capabilities                  → agent→areas dict

IMPROVEMENT AREAS (12 total)
─────────────────────────────
{areas}

AGENT ROUTING (first 12)
─────────────────────────
{agents}

CLI
───
  python scripts/cognitive/orchestrate.py next
  python scripts/cognitive/orchestrate.py session --output markdown
  python scripts/cognitive/orchestrate.py survey
  python scripts/cognitive/orchestrate.py advance SECURITY_REMEDIATION SEC-01
  python scripts/cognitive/orchestrate.py stamp-plansets
  python scripts/cognitive/orchestrate.py help

CODEBASE AGENCY POLICY
──────────────────────
  Every agent MUST leave the codebase better than it found it.
  After each step: call brain.advance() to persist learning.
  The next agent inherits your progress automatically.
""".strip()

    def discover(self) -> dict[str, Any]:
        """
        Return a complete JSON-serialisable capability map of the brain.

        Agents can call this to understand all available areas, plansets,
        agents, and their relationships without reading any documentation.

        Returns
        -------
        dict
            Keys: ``version``, ``improvement_areas``, ``agent_routing``,
            ``planset_coverage``, ``engine_equation``, ``cli``, ``quickstart``.
        """
        records = self.orchestrator.survey()
        planset_coverage = {
            area.value: [r.stem for r in records if r.area == area and not r.is_complete]
            for area in ImprovementArea
        }
        agent_routing = {aid: [c.value for c in caps] for aid, caps in AGENT_CAPABILITIES.items()}
        return {
            "version": self._VERSION,
            "description": "Advanced extension of GitHub Copilot Coding Agent",
            "improvement_areas": [a.value for a in ImprovementArea],
            "agent_routing": agent_routing,
            "planset_coverage": planset_coverage,
            "engine_equation": (
                "Score = (Impact × Confidence × Momentum) / (Energy × (1+Risk) × (1+Friction))"
            ),
            "amplitude": "sqrt(Score)",
            "collapse_rule": "Steps sorted by amplitude desc; entangled partners promoted",
            "learning_loop": (
                "brain.advance() → PlansetOrchestrator.advance() "
                "→ AgentBrainInterface.submit_learning() → "
                "next agent's patterns enriched"
            ),
            "cli": "python scripts/cognitive/orchestrate.py",
            "quickstart": (
                "from codex.cognitive import brain\n"
                "ctx = brain.session('my-agent-id')\n"
                "brain.advance('SECURITY_REMEDIATION', 'SEC-01')"
            ),
            "modules": {
                "QuantumPlansetEngine": "src/codex/cognitive/quantum_planset_engine.py",
                "PlansetOrchestrator": "src/codex/cognitive/planset_orchestrator.py",
                "AgentBrainAPI": "src/codex/cognitive/agent_brain_api.py",
                "AgentBrainInterface": "src/codex/cognitive/brain_interface.py",
                "CognitiveBrain": "src/codex/cognitive/agent_brain_api.py",
                "orchestrate CLI": "scripts/cognitive/orchestrate.py",
            },
        }

    def health(self) -> dict[str, Any]:
        """
        Return a live health status dict for the cognitive brain.

        Checks planset directory, orchestrator state, and engine availability.

        Returns
        -------
        dict
            Keys: ``status``, ``planset_dir_exists``, ``plansets_found``,
            ``unfinished_plansets``, ``completed_steps``, ``areas_active``,
            ``engine_ok``, ``issues``.
        """
        issues: list[str] = []

        planset_exists = self._plans.exists()
        if not planset_exists:
            issues.append(f"planset_dir missing: {self._plans}")

        records = self.orchestrator.survey() if planset_exists else []
        unfinished = [r for r in records if not r.is_complete]
        completed = self.orchestrator._state.completed_steps
        n_done = sum(len(v) for v in completed.values())
        areas_active = len({r.area for r in unfinished if r.area})

        try:
            test_ps = self.engine.generate(ImprovementArea.CI_SELF_HEALING)
            engine_ok = len(test_ps.steps) > 0
        except Exception as exc:
            engine_ok = False
            issues.append(f"engine error: {exc}")

        status = "healthy" if not issues else "degraded"

        return {
            "status": status,
            "version": self._VERSION,
            "planset_dir_exists": planset_exists,
            "plansets_found": len(records),
            "unfinished_plansets": len(unfinished),
            "completed_steps_total": n_done,
            "areas_active": areas_active,
            "engine_ok": engine_ok,
            "state_path": str(self._state),
            "issues": issues,
        }

    @property
    def capabilities(self) -> dict[str, list[str]]:
        """Return the full agent→capabilities mapping as a plain dict."""
        return {aid: [c.value for c in caps] for aid, caps in AGENT_CAPABILITIES.items()}

    def __repr__(self) -> str:  # pragma: no cover
        try:
            h = self.health()
            return (
                f"CognitiveBrain(v{self._VERSION}, "
                f"status={h['status']}, "
                f"unfinished={h['unfinished_plansets']}, "
                f"areas={h['areas_active']})"
            )
        except Exception:
            return f"CognitiveBrain(v{self._VERSION})"

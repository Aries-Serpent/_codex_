"""
Planset Orchestrator — Autonomous Next-Action Engine.

Surveys all unfinished plansets in ``.codex/plans/``, maps them to
``ImprovementArea`` values, scores them via ``QuantumPlansetEngine``,
and generates ranked ``PromptSet`` objects that tell agents exactly what
to do next and in what order.

Architecture
------------
::

    PlansetOrchestrator
        │
        ├── survey()           → list[PlansetRecord]
        │       reads .codex/plans/ → maps filenames to ImprovementArea
        │
        ├── generate_session() → list[PromptSet]
        │       runs engine.generate() + engine.collapse() per area
        │       returns ranked prompts ordered by amplitude
        │
        ├── next_promptset()   → PromptSet
        │       single highest-priority action for the current session
        │
        └── advance(area, step_id)
                marks step complete → apply decoherence to remaining steps

Mermaid
-------
See ``.codex/plans/QUANTUM_PLANSETS_CODEBASE_IMPROVEMENT.md`` for full diagram.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from codex.cognitive.quantum_planset_engine import (
    ImprovementArea,
    PlanStep,
    QuantumPlansetEngine,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Planset-filename → ImprovementArea mapping
# Covers every unfinished planset found in the .codex/plans/ audit.
# ---------------------------------------------------------------------------
_PLANSET_MAP: dict[str, ImprovementArea] = {
    # CI / Self-Healing
    "CI_FINAL_RESOLUTION_PR3339_MERGE_PLANSET": ImprovementArea.CI_SELF_HEALING,
    "CUSTOM_AGENT_PLANSET_CI_FAILURE_DIAGNOSTICIAN": ImprovementArea.CI_SELF_HEALING,
    "BATCH_TRIAGE_COGNITIVE_BRAIN_INTEGRATION_PLANSET": ImprovementArea.CI_SELF_HEALING,
    "WORKFLOW_HEALTH_AUTOMATION_PLANSET": ImprovementArea.WORKFLOW_HEALTH,
    # Security
    "CODEQL_ALERT_RESOLUTION_PLANSET": ImprovementArea.SECURITY_REMEDIATION,
    "CUSTOM_AGENT_PLANSET_SECURITY_ADVISORY_RESOLVER": ImprovementArea.SECURITY_REMEDIATION,
    # Coverage / Testing
    "PHASE_14_TEST_COVERAGE_IMPROVEMENT_PLANSET": ImprovementArea.COVERAGE_IMPROVEMENT,
    "PLANSET_PHASE_23_COVERAGE_30": ImprovementArea.COVERAGE_IMPROVEMENT,
    "PLANSET_PHASE_24_COVERAGE_50": ImprovementArea.COVERAGE_IMPROVEMENT,
    "PLANSET_PHASE_25_COVERAGE_70": ImprovementArea.COVERAGE_IMPROVEMENT,
    "PLANSET_TEST_SIGNATURE_VALIDATION_PRODUCTION": ImprovementArea.COVERAGE_IMPROVEMENT,
    "CUSTOM_AGENT_PLANSET_TEST_ASSERTION_UPDATER": ImprovementArea.TEST_ASSERTION_UPDATE,
    # Documentation
    "PHASE_12_DOCUMENTATION_QUALITY_PLANSET": ImprovementArea.DOCUMENTATION_HYGIENE,
    # Dependencies
    "IP-005_DEPENDENCY_UPDATES_PLANSET": ImprovementArea.DEPENDENCY_MODERNISATION,
    # Cache
    "CUSTOM_AGENT_PLANSET_CACHE_LOGIC_VALIDATOR": ImprovementArea.CACHE_VALIDATION,
    # RAG
    "PRODUCTION_RAG_PIPELINE_PLANSET": ImprovementArea.RAG_PIPELINE,
    "AI_AGENT_RAG_EXECUTION_PLANSET": ImprovementArea.RAG_PIPELINE,
    # ML
    "ML_PATTERN_FEEDING_PLANSET": ImprovementArea.ML_PATTERN_FEEDING,
    # Agent Chaining / Ecosystem
    "AGENT_CHAINING_INTEGRATION_PLANSET": ImprovementArea.AGENT_CHAINING,
    "AGENT_ECOSYSTEM_COGNITIVE_BRAIN_INTEGRATION_PLANSET": ImprovementArea.AGENT_CHAINING,
    # QI / Quantum
    "PHASE_3_4_QUANTUM_AUTONOMOUS_PLANSETS": ImprovementArea.QI_TESTING,
    # Multi-phase master plansets (map to highest-impact area)
    "NEXT_ITERATION_PLANSET_2026_02_04": ImprovementArea.CI_SELF_HEALING,
    "NEXT_PHASE_PLANSETS": ImprovementArea.COVERAGE_IMPROVEMENT,
    "PHASE6_CONTINUATION_PLANSET": ImprovementArea.CI_SELF_HEALING,
    "PHASE_15_MASTER_PLANSET": ImprovementArea.COVERAGE_IMPROVEMENT,
    "PHASE_16_MASTER_PLANSET": ImprovementArea.COVERAGE_IMPROVEMENT,
    "PHASE_17_MASTER_PLANSET": ImprovementArea.CI_SELF_HEALING,
    "PHASE_18_MASTER_PLANSET": ImprovementArea.COVERAGE_IMPROVEMENT,
    "PHASE_20_MASTER_PLANSET": ImprovementArea.SECURITY_REMEDIATION,
    "PHASE_21_MASTER_PLANSET": ImprovementArea.CI_SELF_HEALING,
    "PHASE_67_EXECUTION_PLANSET": ImprovementArea.AGENT_CHAINING,
    "MASTER_PLANSET_PRODUCTION_READINESS": ImprovementArea.CI_SELF_HEALING,
    "TOP3_AGENT_ENHANCEMENT_PLANSETS": ImprovementArea.AGENT_CHAINING,
    "PR3248_CODE_QUALITY_RESOLUTION_PLANSET": ImprovementArea.TEST_ASSERTION_UPDATE,
    "PR3248_REMAINING_ITEMS_SOLUTION_PLANSET": ImprovementArea.TEST_ASSERTION_UPDATE,
    "DYNAMICS_365_ENHANCEMENT_PLANSET": ImprovementArea.ML_PATTERN_FEEDING,
    "ENHANCEMENT_RESEARCH_PLANSETS": ImprovementArea.ML_PATTERN_FEEDING,
}

# Status markers that indicate a planset is unfinished
_INCOMPLETE_MARKERS: re.Pattern = re.compile(
    r"IN PROGRESS|PENDING|PLANNED|READY FOR EXECUTION|🔄|🚧|📋|🟡",
    re.IGNORECASE,
)
_COMPLETE_MARKERS: re.Pattern = re.compile(
    r"✅\s*(COMPLETE|VERIFIED|DONE)",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclass
class PlansetRecord:
    """Metadata about a discovered planset file."""

    path: Path
    stem: str
    area: Optional[ImprovementArea]
    is_complete: bool
    status_line: str = ""


@dataclass
class PromptSet:
    """
    A concrete, agent-ready prompt derived from a collapsed planset step.

    Attributes
    ----------
    prompt_id:
        Unique identifier ``<area>:<step_id>:<session>``.
    area:
        The ``ImprovementArea`` this prompt belongs to.
    source_planset:
        Filename of the originating ``.codex/plans/`` document.
    agent:
        The custom agent that should execute this prompt.
    prompt:
        The ready-to-send natural-language instruction.
    context:
        Session context forwarded from the orchestrator.
    amplitude:
        Physics-scored priority (higher = execute sooner).
    order:
        Sequence index within this session's ranked list.
    step_id:
        The originating ``PlanStep.step_id``.
    description:
        Full description from the engine template.
    """

    prompt_id: str
    area: str
    source_planset: str
    agent: str
    prompt: str
    context: dict[str, Any]
    amplitude: float
    order: int
    step_id: str
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class OrchestrationState:
    """Persisted state between orchestrator sessions."""

    session_id: str
    active_areas: list[str] = field(default_factory=list)
    completed_steps: dict[str, list[str]] = field(default_factory=dict)
    deferred_areas: list[str] = field(default_factory=list)
    decoherence_sessions: dict[str, int] = field(default_factory=dict)
    last_updated: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> OrchestrationState:
        return cls(
            session_id=data.get("session_id", ""),
            active_areas=data.get("active_areas", []),
            completed_steps=data.get("completed_steps", {}),
            deferred_areas=data.get("deferred_areas", []),
            decoherence_sessions=data.get("decoherence_sessions", {}),
            last_updated=data.get("last_updated", ""),
        )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


class PlansetOrchestrator:
    """
    Surveys all unfinished plansets, maps them to ``ImprovementArea`` values,
    scores them via ``QuantumPlansetEngine``, and emits ranked ``PromptSet``
    objects so agents know exactly what to do next and in what order.

    Parameters
    ----------
    planset_dir:
        Path to the directory containing ``.codex/plans/`` markdown files.
        Defaults to ``.codex/plans/`` relative to the current working directory.
    engine:
        ``QuantumPlansetEngine`` instance to reuse.  A new instance is
        created if not provided.
    state_path:
        Where to persist ``OrchestrationState`` between sessions.
    """

    def __init__(
        self,
        planset_dir: Optional[Path] = None,
        engine: Optional[QuantumPlansetEngine] = None,
        state_path: Optional[Path] = None,
    ) -> None:
        self._dir = planset_dir or Path(".codex/plans")
        self._engine = engine or QuantumPlansetEngine()
        self._state_path = state_path or (self._dir / ".orchestrator_state.json")
        self._state: OrchestrationState = self._load_state()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def survey(self) -> list[PlansetRecord]:
        """
        Scan ``planset_dir`` for markdown files, detect completion status,
        and map each to an ``ImprovementArea``.

        Returns
        -------
        list[PlansetRecord]
            One record per ``.md`` file found, sorted by area then filename.
        """
        records: list[PlansetRecord] = []
        if not self._dir.exists():
            return records

        for p in sorted(self._dir.glob("*.md")):
            stem = p.stem
            area = _PLANSET_MAP.get(stem)
            status_line = ""
            is_complete = False

            try:
                text = p.read_text(encoding="utf-8", errors="replace")
                # Check first 3000 chars for status signals
                head = text[:3000]
                if _COMPLETE_MARKERS.search(head):
                    is_complete = True
                elif not _INCOMPLETE_MARKERS.search(head):
                    # No markers: default assume unfinished
                    is_complete = False
                # Grab first status line
                for line in head.splitlines():
                    if re.search(r"status", line, re.IGNORECASE):
                        status_line = line.strip()[:80]
                        break
            except OSError:
                logger.debug("Suppressed exception in handler", exc_info=True)
            records.append(
                PlansetRecord(
                    path=p,
                    stem=stem,
                    area=area,
                    is_complete=is_complete,
                    status_line=status_line,
                )
            )

        return sorted(records, key=lambda r: (str(r.area or ""), r.stem))

    def generate_session(
        self,
        context: Optional[dict[str, Any]] = None,
        max_prompts: int = 10,
        include_complete: bool = False,
    ) -> list[PromptSet]:
        """
        Generate a ranked list of ``PromptSet`` objects for the current session.

        For each unfinished planset area, collapses the planset and converts
        each executable step into a ``PromptSet``.  Results are sorted by
        amplitude descending so agents always execute highest-value work first.

        Parameters
        ----------
        context:
            Session-level signals (e.g. ``{"open_alerts": 120, "coverage_pct": 45}``).
        max_prompts:
            Maximum number of prompts to return.
        include_complete:
            If ``True``, includes prompts from fully-complete plansets too.

        Returns
        -------
        list[PromptSet]
            Ranked prompts, highest amplitude first.
        """
        ctx = context or {}
        records = self.survey()
        seen_areas: set[Any] = set()
        all_prompts: list[PromptSet] = []

        for rec in records:
            if rec.area is None:
                continue
            if not include_complete and rec.is_complete:
                continue
            if rec.area in seen_areas:
                continue
            seen_areas.add(rec.area)

            area_ctx = self._build_area_context(rec.area, ctx)
            ps = self._engine.generate(rec.area, context=area_ctx)

            # Skip steps already completed this session
            completed = self._state.completed_steps.get(rec.area.value, [])
            dec_sessions = self._state.decoherence_sessions.get(rec.area.value, 0)
            if dec_sessions > 0:
                self._engine.apply_decoherence(ps, sessions=dec_sessions)

            path = self._engine.collapse(ps)
            for step in path:
                if step.step_id in completed:
                    continue
                prompt_set = self._step_to_promptset(
                    step=step,
                    area=rec.area,
                    source_planset=rec.stem,
                    context=area_ctx,
                    order=len(all_prompts),
                )
                all_prompts.append(prompt_set)

        # Sort globally by amplitude descending
        all_prompts.sort(key=lambda p: p.amplitude, reverse=True)

        # Re-number after sort
        for i, p in enumerate(all_prompts):
            p.order = i

        return all_prompts[:max_prompts]

    def next_promptset(
        self,
        context: Optional[dict[str, Any]] = None,
    ) -> Optional[PromptSet]:
        """
        Return the single highest-priority ``PromptSet`` for the current session.

        Parameters
        ----------
        context:
            Session-level signals passed to the engine.

        Returns
        -------
        PromptSet or None
            The highest-amplitude next action, or ``None`` if all work is done.
        """
        prompts = self.generate_session(context=context, max_prompts=1)
        return prompts[0] if prompts else None

    def advance(self, area: ImprovementArea, step_id: str) -> None:
        """
        Mark a step as complete and apply decoherence to remaining steps in that area.

        Parameters
        ----------
        area:
            The ``ImprovementArea`` the step belongs to.
        step_id:
            The ``PlanStep.step_id`` that was completed (e.g. ``"SEC-01"``).
        """
        key = area.value
        if key not in self._state.completed_steps:
            self._state.completed_steps[key] = []
        if step_id not in self._state.completed_steps[key]:
            self._state.completed_steps[key].append(step_id)

        # Each completed step ages the remaining ones by 1 session
        self._state.decoherence_sessions[key] = self._state.decoherence_sessions.get(key, 0) + 1
        self._state.last_updated = datetime.now(timezone.utc).isoformat()
        self._save_state()

    def summary(self, context: Optional[dict[str, Any]] = None) -> str:
        """
        Return a Markdown summary table of the next session's ranked prompts.

        Parameters
        ----------
        context:
            Optional session signals.

        Returns
        -------
        str
            Markdown table string.
        """
        prompts = self.generate_session(context=context, max_prompts=15)
        if not prompts:
            return "✅ All plansets complete — nothing left to orchestrate.\n"

        lines = [
            "## 🧭 Planset Orchestrator — Next Session",
            "",
            "| # | Step | Agent | Source Planset | Amplitude |",
            "|---|------|-------|----------------|-----------|",
        ]
        for p in prompts:
            lines.append(
                f"| {p.order + 1} | `{p.step_id}` | {p.agent} | "
                f"`{p.source_planset}` | `{p.amplitude:.4f}` |"
            )
        lines.extend(["", f"*Generated: {datetime.now(timezone.utc).isoformat()}*", ""])
        return "\n".join(lines)

    def save_state(self, path: Optional[Path] = None) -> Path:
        """Persist orchestration state to JSON."""
        out = path or self._state_path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(self._state.to_dict(), indent=2),
            encoding="utf-8",
        )
        return out

    def load_state(self, path: Optional[Path] = None) -> OrchestrationState:
        """Load orchestration state from JSON."""
        src = path or self._state_path
        if src.exists():
            data = json.loads(src.read_text(encoding="utf-8"))
            self._state = OrchestrationState.from_dict(data)
        return self._state

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_area_context(
        self, area: ImprovementArea, global_ctx: dict[str, Any]
    ) -> dict[str, Any]:
        """Merge global session context with area-specific defaults."""
        ctx = dict(global_ctx)
        # Propagate common signals to per-area keys the engine understands
        mapping = {
            ImprovementArea.COVERAGE_IMPROVEMENT: {"coverage_pct": ctx.get("coverage_pct", 0)},
            ImprovementArea.SECURITY_REMEDIATION: {"open_alerts": ctx.get("open_alerts", 0)},
            ImprovementArea.CI_SELF_HEALING: {"failing_checks": ctx.get("failing_checks", 0)},
            ImprovementArea.DEPENDENCY_MODERNISATION: {"stale_deps": ctx.get("stale_deps", 0)},
            ImprovementArea.QI_TESTING: {
                "failing_patterns": ctx.get("failing_patterns", 0),
                "k1": ctx.get("k1", 0.0),
            },
            ImprovementArea.CACHE_VALIDATION: {"cache_failures": ctx.get("cache_failures", 0)},
            ImprovementArea.TEST_ASSERTION_UPDATE: {
                "stale_assertions": ctx.get("stale_assertions", 0),
            },
            ImprovementArea.RAG_PIPELINE: {"phase3_pending": ctx.get("phase3_pending", False)},
            ImprovementArea.ML_PATTERN_FEEDING: {
                "pattern_lag_sessions": ctx.get("pattern_lag_sessions", 0),
            },
            ImprovementArea.WORKFLOW_HEALTH: {
                "stuck_workflows": ctx.get("stuck_workflows", 0),
            },
            ImprovementArea.AGENT_CHAINING: {
                "chain_depth_needed": ctx.get("chain_depth_needed", 0),
            },
        }
        ctx.update(mapping.get(area, {}))
        return ctx

    def _step_to_promptset(
        self,
        step: PlanStep,
        area: ImprovementArea,
        source_planset: str,
        context: dict[str, Any],
        order: int,
    ) -> PromptSet:
        """Convert a ``PlanStep`` into a concrete ``PromptSet``."""
        session = datetime.now(timezone.utc).strftime("%Y%m%d")
        prompt_id = f"{area.value}:{step.step_id}:{session}"
        prompt = (
            f"You are the `{step.agent}` agent.\n\n"
            f"**Task [{step.step_id}]**: {step.action}\n\n"
            f"**Details**: {step.description}\n\n"
            f"**Source planset**: `{source_planset}`\n"
            f"**Amplitude**: `{step.effective_amplitude():.4f}` "
            f"(physics-scored priority)\n\n"
            f"Execute this task now. Apply self-healing if CI fails. "
            f"Call `advance(ImprovementArea.{area.value}, '{step.step_id}')` "
            f"on the orchestrator when complete."
        )
        return PromptSet(
            prompt_id=prompt_id,
            area=area.value,
            source_planset=source_planset,
            agent=step.agent,
            prompt=prompt,
            context=context,
            amplitude=step.effective_amplitude(),
            order=order,
            step_id=step.step_id,
            description=step.description,
        )

    def _load_state(self) -> OrchestrationState:
        if self._state_path.exists():
            try:
                data = json.loads(self._state_path.read_text(encoding="utf-8"))
                return OrchestrationState.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                logger.debug("Suppressed exception in handler", exc_info=True)
        return OrchestrationState(
            session_id=datetime.now(timezone.utc).strftime("session-%Y%m%d"),
        )

    def _save_state(self) -> None:
        self.save_state()

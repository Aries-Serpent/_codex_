"""Track-C workflow orchestration for capability planning and execution.

This module provides a phased workflow system for managing capability
implementations, rollbacks, and error handling across six standard phases:
Preparation, Search & Mapping, Best-Effort Construction, Controlled Pruning,
Error Capture, and Finalization.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable, Mapping, MutableMapping, Sequence
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime

logger = logging.getLogger(__name__)

PhaseAction = Callable[["WorkflowContext", "CapabilityPlan"], None]
RollbackAction = Callable[["WorkflowContext"], None]

SIX_PHASES: Sequence[str] = (
    "Preparation",
    "Search & Mapping",
    "Best-Effort Construction",
    "Controlled Pruning",
    "Error Capture",
    "Finalization",
)


@dataclass
class ErrorRecord:
    timestamp: datetime
    phase: str
    capability: str
    step: str
    message: str
    exception_type: str
    context: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "timestamp": self.timestamp.isoformat(timespec="seconds"),
            "phase": self.phase,
            "capability": self.capability,
            "step": self.step,
            "message": self.message,
            "exception_type": self.exception_type,
            "context": self.context,
        }


@dataclass
class WorkflowContext:
    capability: str
    offline_mode: bool = True
    phase_history: list[str] = field(default_factory=list)
    routes: MutableMapping[str, list[str]] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    pruned: list[str] = field(default_factory=list)
    errors: list[ErrorRecord] = field(default_factory=list)
    rollbacks: list[tuple[str, RollbackAction]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    failed_phases: list[str] = field(default_factory=list)
    summary: dict[str, object] = field(default_factory=dict)

    def register_rollback(self, label: str, rollback: RollbackAction) -> None:
        self.rollbacks.append((label, rollback))

    def apply_rollbacks(self) -> None:
        while self.rollbacks:
            label, rollback = self.rollbacks.pop()
            try:
                rollback(self)
            except (ValueError, TypeError, RuntimeError):
                logger.warning("Exception occurred", exc_info=True)
                # Rollbacks should not interrupt remaining cleanup.
                self.failed_phases.append(f"rollback:{label}")


@dataclass
class CapabilityPlan:
    name: str
    aliases: Sequence[str] = field(default_factory=tuple)
    search_targets: Sequence[str] = field(default_factory=tuple)
    construction_steps: Sequence[str] = field(default_factory=tuple)
    pruning_rules: Sequence[str] = field(default_factory=tuple)
    phase_overrides: Mapping[str, PhaseAction] | None = None

    def get_action(self, phase_name: str) -> PhaseAction | None:
        if self.phase_overrides and phase_name in self.phase_overrides:
            return self.phase_overrides[phase_name]
        return None


class CapabilityRouter:
    def __init__(self, plans: Iterable[CapabilityPlan] | None = None) -> None:
        self._plans: dict[str, CapabilityPlan] = {}
        if plans:
            for plan in plans:
                self.register(plan)

    def register(self, plan: CapabilityPlan) -> None:
        self._plans[plan.name.lower()] = plan
        for alias in plan.aliases:
            self._plans[alias.lower()] = plan

    def resolve(self, capability: str) -> CapabilityPlan:
        key = capability.lower()
        if key not in self._plans:
            raise KeyError(f"Unknown capability: {capability}")
        return self._plans[key]


def record_error(
    ctx: WorkflowContext,
    phase: str,
    step: str,
    exc: Exception,
    *,
    extra_context: Mapping[str, object] | None = None,
) -> ErrorRecord:
    record = ErrorRecord(
        timestamp=datetime.now(UTC),
        phase=phase,
        capability=ctx.capability,
        step=step,
        message=str(exc),
        exception_type=exc.__class__.__name__,
        context=dict(extra_context or {}),
    )
    ctx.errors.append(record)
    ctx.failed_phases.append(phase)
    return record


@contextmanager
def step_context(
    ctx: WorkflowContext,
    phase: str,
    step: str,
    *,
    rollback: RollbackAction | None = None,
    extra_context: Mapping[str, object] | None = None,
):
    try:
        yield
    except Exception as exc:
        record_error(ctx, phase, step, exc, extra_context=extra_context)
        if rollback:
            rollback(ctx)


def _preparation_phase(ctx: WorkflowContext, plan: CapabilityPlan) -> None:
    ctx.notes.append(f"prepared:{plan.name}")
    ctx.summary["offline"] = ctx.offline_mode
    prepared_flag = f"prepared:{plan.name}"

    def rollback(context: WorkflowContext) -> None:
        if prepared_flag in context.notes:
            context.notes.remove(prepared_flag)

    ctx.register_rollback("preparation", rollback)


def _search_and_mapping_phase(ctx: WorkflowContext, plan: CapabilityPlan) -> None:
    targets = list(plan.search_targets) or ["baseline-scan"]
    ctx.routes[plan.name] = targets

    def rollback(context: WorkflowContext) -> None:
        context.routes.pop(plan.name, None)

    ctx.register_rollback("search_and_mapping", rollback)


def _best_effort_construction_phase(ctx: WorkflowContext, plan: CapabilityPlan) -> None:
    constructed = [f"{plan.name}:{step}" for step in (plan.construction_steps or ("prototype",))]
    ctx.artifacts.extend(constructed)

    def rollback(context: WorkflowContext) -> None:
        for _ in constructed:
            if context.artifacts:
                context.artifacts.pop()

    ctx.register_rollback("best_effort_construction", rollback)


def _controlled_pruning_phase(ctx: WorkflowContext, plan: CapabilityPlan) -> None:
    pruned_local: list[str] = []
    if ctx.artifacts:
        for artifact in list(ctx.artifacts):
            rule_match = any(rule in artifact for rule in plan.pruning_rules)
            duplicate = ctx.artifacts.count(artifact) > 1
            if rule_match or duplicate:
                ctx.artifacts.remove(artifact)
                ctx.pruned.append(artifact)
                pruned_local.append(artifact)

    def rollback(context: WorkflowContext) -> None:
        while pruned_local:
            item = pruned_local.pop()
            context.artifacts.append(item)
            if item in context.pruned:
                context.pruned.remove(item)

    ctx.register_rollback("controlled_pruning", rollback)


def _error_capture_phase(ctx: WorkflowContext, plan: CapabilityPlan) -> None:
    if ctx.errors:
        ctx.apply_rollbacks()
    ctx.notes.append("errors-reviewed")
    ctx.register_rollback(
        "error_capture",
        lambda context: context.notes.pop() if context.notes else None,  # type: ignore[arg-type]
    )


def _finalization_phase(ctx: WorkflowContext, plan: CapabilityPlan) -> None:
    ctx.summary.update(
        {
            "capability": plan.name,
            "phases": list(ctx.phase_history),
            "errors": [err.to_dict() for err in ctx.errors],
            "artifacts": list(ctx.artifacts),
            "pruned": list(ctx.pruned),
            "routes": {plan.name: ctx.routes.get(plan.name, [])},
        }
    )
    ctx.register_rollback("finalization", lambda context: context.summary.clear())


PHASE_IMPLEMENTATIONS: Mapping[str, PhaseAction] = {
    "Preparation": _preparation_phase,
    "Search & Mapping": _search_and_mapping_phase,
    "Best-Effort Construction": _best_effort_construction_phase,
    "Controlled Pruning": _controlled_pruning_phase,
    "Error Capture": _error_capture_phase,
    "Finalization": _finalization_phase,
}


CAPABILITY_ROUTING: dict[str, CapabilityPlan] = {
    "tokenization": CapabilityPlan(
        name="tokenization",
        aliases=("token", "bpe"),
        search_targets=("datasets", "normalizers", "decoders"),
        construction_steps=("build-vocab", "package-tokenizer"),
        pruning_rules=("duplicate", "scratch"),
    ),
    "training": CapabilityPlan(
        name="training",
        aliases=("train",),
        search_targets=("configs", "checkpoints", "optimizers"),
        construction_steps=("compile", "optimizer-step"),
        pruning_rules=("stale",),
    ),
    "evaluation": CapabilityPlan(
        name="evaluation",
        aliases=("eval",),
        search_targets=("metrics", "datasets", "reports"),
        construction_steps=("score", "summarize"),
        pruning_rules=("redundant",),
    ),
}

DEFAULT_ROUTER = CapabilityRouter(CAPABILITY_ROUTING.values())


class WorkflowOrchestrator:
    def __init__(
        self, router: CapabilityRouter | None = None, *, offline_mode: bool = True
    ) -> None:
        self.router = router or DEFAULT_ROUTER
        self.offline_mode = offline_mode

    def run(self, capability: str) -> WorkflowContext:
        plan = self.router.resolve(capability)
        ctx = WorkflowContext(capability=plan.name, offline_mode=self.offline_mode)

        for phase_name in SIX_PHASES:
            action = plan.get_action(phase_name) or PHASE_IMPLEMENTATIONS[phase_name]
            with step_context(
                ctx,
                phase_name,
                action.__name__,
                extra_context={
                    "capability": plan.name,
                    "phase": phase_name,
                    "offline": ctx.offline_mode,
                },
            ):
                action(ctx, plan)
            ctx.phase_history.append(phase_name)

        return ctx


def run_capability(
    capability: str,
    *,
    offline_mode: bool = True,
    router: CapabilityRouter | None = None,
) -> WorkflowContext:
    orchestrator = WorkflowOrchestrator(router=router, offline_mode=offline_mode)
    return orchestrator.run(capability)

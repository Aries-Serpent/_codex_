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
    """Captured workflow failure with its phase, step, and capability identity.

    Args:
        timestamp: Capture time, normally an aware UTC datetime.
        phase: Phase label recorded in failed_phases.
        capability: Canonical capability name.
        step: Name of the failing action.
        message: Exception text.
        exception_type: Exception class name.
        context: Additional metadata, defaulting to a new empty dictionary.
    """

    timestamp: datetime
    phase: str
    capability: str
    step: str
    message: str
    exception_type: str
    context: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        """Return error fields with timestamp formatted to second precision.

        The context dictionary is shared, not copied, and its values are not
        made JSON-safe. An aware UTC timestamp keeps its +00:00 offset.
        """
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
    """Mutable per-run state shared by phase actions and rollback callbacks.

    Args:
        capability: Canonical capability name used by error records.
        offline_mode: Informational flag; it does not enforce network isolation.
        phase_history: Completed phase-attempt labels in execution order.
        routes: Capability-to-search-target mapping.
        artifacts: Constructed artifact labels, not filesystem handles.
        pruned: Labels removed by pruning.
        errors: Captured ErrorRecord instances.
        rollbacks: Stack of labeled cleanup callbacks.
        notes: Free-form phase annotations.
        failed_phases: Failure labels, including caught rollback failures.
        summary: Finalization output; later phases need not refresh it.

    Collection fields default to independent empty containers per instance.
    """

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
        """Push a labeled cleanup action onto this run's rollback stack.

        Args:
            label: Diagnostic identifier used if cleanup fails.
            rollback: Callable receiving this context when apply_rollbacks runs.

        Returns:
            None. Registration alone does not execute the callback.
        """
        self.rollbacks.append((label, rollback))

    def apply_rollbacks(self) -> None:
        """Pop and execute registered callbacks in last-in, first-out order.

        Returns:
            None. ValueError, TypeError, and RuntimeError from a callback are
            logged and recorded as rollback:<label>; remaining cleanup continues.

        Other exceptions propagate, leaving still-unpopped callbacks registered.
        """
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
    """Declarative inputs and optional phase actions for one capability.

    Args:
        name: Canonical route name.
        aliases: Additional case-insensitive route keys.
        search_targets: Labels recorded during search, or baseline-scan if empty.
        construction_steps: Artifact suffixes, or prototype if empty.
        pruning_rules: Substrings whose matching artifacts are pruned.
        phase_overrides: Exact SIX_PHASES labels mapped to replacement
            callables accepting WorkflowContext and this plan.
    """

    name: str
    aliases: Sequence[str] = field(default_factory=tuple)
    search_targets: Sequence[str] = field(default_factory=tuple)
    construction_steps: Sequence[str] = field(default_factory=tuple)
    pruning_rules: Sequence[str] = field(default_factory=tuple)
    phase_overrides: Mapping[str, PhaseAction] | None = None

    def get_action(self, phase_name: str) -> PhaseAction | None:
        """Return the override for an exact phase_name, or None if absent.

        No default implementation is resolved here; the orchestrator supplies it.
        """
        if self.phase_overrides and phase_name in self.phase_overrides:
            return self.phase_overrides[phase_name]
        return None


class CapabilityRouter:
    """Resolve case-insensitive capability names and aliases to shared plans.

    Args:
        plans: Optional iterable registered in order. Later registrations
            overwrite colliding keys; names are lowercased, not stripped.
    """

    def __init__(self, plans: Iterable[CapabilityPlan] | None = None) -> None:
        self._plans: dict[str, CapabilityPlan] = {}
        if plans:
            for plan in plans:
                self.register(plan)

    def register(self, plan: CapabilityPlan) -> None:
        """Map plan.name and each alias to plan, overwriting colliding keys.

        Args:
            plan: CapabilityPlan retained by reference, not copied.

        Returns:
            None. Re-registering does not remove aliases from an earlier plan.
        """
        self._plans[plan.name.lower()] = plan
        for alias in plan.aliases:
            self._plans[alias.lower()] = plan

    def resolve(self, capability: str) -> CapabilityPlan:
        """Return the shared plan registered for capability, ignoring case.

        Args:
            capability: Canonical name or alias; whitespace remains significant.

        Raises:
            KeyError: If no matching route has been registered.
        """
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
    """Append a UTC-stamped error record and mark the phase as failed.

    Args:
        ctx: Run context to mutate.
        phase: Failed phase label, appended even if already recorded.
        step: Failing operation's diagnostic name.
        exc: Exception whose text and class name are captured, not re-raised.
        extra_context: Optional metadata shallow-copied into the record.

    Returns:
        The same ErrorRecord instance appended to ctx.errors.
    """
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
    """Capture and suppress an Exception raised inside one workflow step.

    Args:
        ctx: Context receiving error and failed-phase records.
        phase: Phase label for captured errors.
        step: Diagnostic action label.
        rollback: Optional immediate cleanup callable receiving ctx on failure;
            it is not registered on the rollback stack.
        extra_context: Metadata passed to record_error on failure.

    Yields:
        None, allowing the caller's action to execute.

    Exceptions from rollback propagate; BaseException subclasses from the
    body are not intercepted. Successful steps do not invoke rollback.
    """
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
    """Run six ordered phase actions against a newly allocated context.

    Args:
        router: Capability lookup table; None uses DEFAULT_ROUTER.
        offline_mode: Metadata passed into contexts, not a network restriction.

    Built-in actions manipulate in-memory labels rather than building models
    or writing artifacts. Overrides may perform their own side effects.
    """

    def __init__(
        self, router: CapabilityRouter | None = None, *, offline_mode: bool = True
    ) -> None:
        self.router = router or DEFAULT_ROUTER
        self.offline_mode = offline_mode

    def run(self, capability: str) -> WorkflowContext:
        """Resolve capability and attempt every phase in SIX_PHASES order.

        Args:
            capability: Name or alias recognized by this orchestrator's router.

        Returns:
            New WorkflowContext containing attempted phase history and captured
            errors. Action Exceptions are suppressed by step_context so later
            phases run. The default Error Capture phase applies pending rollbacks.
            Finalization's summary is built before its own history entry is added.

        Raises:
            KeyError: If capability cannot be resolved.
            AttributeError: If a phase callable has no __name__ attribute.
        """
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
    """Execute a capability with a fresh WorkflowOrchestrator.

    Args:
        capability: Canonical route name or case-insensitive alias.
        offline_mode: Informational context flag, default True.
        router: Optional custom CapabilityRouter; None selects DEFAULT_ROUTER.

    Returns:
        WorkflowContext with phase history, summary, and captured errors.

    Raises:
        KeyError: If the chosen router does not recognize capability.

    Example:
        >>> context = run_capability("token")
        >>> context.capability
        'tokenization'
        >>> context.phase_history == list(SIX_PHASES)
        True
    """
    orchestrator = WorkflowOrchestrator(router=router, offline_mode=offline_mode)
    return orchestrator.run(capability)

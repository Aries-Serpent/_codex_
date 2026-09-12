"""Observe–Orient–Decide–Act contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Mapping, Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class Observation:
    """Structured input captured by the observe stage."""

    source: str
    data: Mapping[str, object]
    observed_at: datetime
    metadata: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Orientation:
    """Context and analysis derived from an observation."""

    context: Mapping[str, object]
    analysis: str
    confidence: float


@dataclass(frozen=True, slots=True)
class Decision:
    """Action selected by the decide stage."""

    action: str
    parameters: Mapping[str, object] = field(default_factory=dict)
    reason: str = ""
    confidence: float = 0.0


@dataclass(frozen=True, slots=True)
class ActionResult:
    """Outcome reported by the act stage."""

    success: bool
    output: object = None
    errors: tuple[str, ...] = ()
    metrics: Mapping[str, float] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class OODACycle:
    """Portable record joining the four stage contracts."""

    observation: Observation
    orientation: Orientation
    decision: Decision
    result: ActionResult


@runtime_checkable
class OODAProtocol(Protocol):
    """Structural boundary for a consumer-owned OODA planner."""

    def observe(self, input_data: Mapping[str, object]) -> Observation:
        """Gather and structure raw input."""

        ...

    def orient(self, observation: Observation) -> Orientation:
        """Analyze an observation in context."""

        ...

    def decide(self, orientation: Orientation) -> Decision:
        """Select an action from an orientation."""

        ...

    def act(self, decision: Decision) -> ActionResult:
        """Execute a decision."""

        ...


__all__ = [
    "ActionResult",
    "Decision",
    "Observation",
    "OODACycle",
    "OODAProtocol",
    "Orientation",
]

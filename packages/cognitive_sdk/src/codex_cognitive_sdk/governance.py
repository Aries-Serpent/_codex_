"""Governance request, decision, and policy contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class GovernanceRequest:
    """An authorization request presented to a governance boundary."""

    actor: str
    action: str
    resource: str
    context: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GovernanceDecision:
    """The portable result of evaluating a governance request."""

    allowed: bool
    reason: str = ""
    obligations: tuple[str, ...] = ()


@runtime_checkable
class GovernanceProtocol(Protocol):
    """Structural boundary implemented by consumer-owned policy engines."""

    def evaluate(self, request: GovernanceRequest) -> GovernanceDecision:
        """Evaluate an authorization request without performing the action."""

        ...


__all__ = ["GovernanceDecision", "GovernanceProtocol", "GovernanceRequest"]

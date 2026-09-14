"""Governance request, decision, and policy contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Mapping, Protocol, runtime_checkable


def _freeze_mapping(value: Mapping[str, object] | None) -> Mapping[str, object]:
    """Return an immutable mapping snapshot for a frozen dataclass field."""

    if value is None:
        return MappingProxyType({})
    if isinstance(value, MappingProxyType):
        return value
    return MappingProxyType(dict(value))


@dataclass(frozen=True, slots=True)
class GovernanceRequest:
    """An authorization request presented to a governance boundary."""

    actor: str
    action: str
    resource: str
    context: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "context", _freeze_mapping(self.context))


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

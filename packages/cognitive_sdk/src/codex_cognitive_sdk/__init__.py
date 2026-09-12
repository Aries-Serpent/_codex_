"""Public API for the standalone Codex cognitive contract boundary."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

from .__about__ import __version__

if TYPE_CHECKING:
    from .governance import (  # noqa: F401
        GovernanceDecision,
        GovernanceProtocol,
        GovernanceRequest,
    )
    from .memory import MemoryProtocol, MemoryQuery, MemoryRecord  # noqa: F401
    from .ooda import (  # noqa: F401
        ActionResult,
        Decision,
        Observation,
        OODACycle,
        OODAProtocol,
        Orientation,
    )

_EXPORTS = {
    "ActionResult": ".ooda",
    "Decision": ".ooda",
    "GovernanceDecision": ".governance",
    "GovernanceProtocol": ".governance",
    "GovernanceRequest": ".governance",
    "MemoryProtocol": ".memory",
    "MemoryQuery": ".memory",
    "MemoryRecord": ".memory",
    "Observation": ".ooda",
    "OODACycle": ".ooda",
    "OODAProtocol": ".ooda",
    "Orientation": ".ooda",
}

__all__ = [*_EXPORTS, "__version__"]


def __getattr__(name: str) -> object:
    """Resolve public contracts without eagerly importing domain modules."""

    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    value = getattr(import_module(module_name, __name__), name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    """Return the deliberate package-root API."""

    return sorted(set(globals()) | set(__all__))

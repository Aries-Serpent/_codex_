from __future__ import annotations

import importlib
import sys
from datetime import datetime, timezone


def test_package_root_is_lazy_and_exports_contracts() -> None:
    for name in tuple(sys.modules):
        if name == "codex_cognitive_sdk" or name.startswith("codex_cognitive_sdk."):
            sys.modules.pop(name)

    package = importlib.import_module("codex_cognitive_sdk")

    assert package.__version__ == "0.1.0a1"
    assert "codex_cognitive_sdk.governance" not in sys.modules
    assert package.GovernanceRequest.__name__ == "GovernanceRequest"
    assert "codex_cognitive_sdk.governance" in sys.modules


def test_package_root_api_is_explicit() -> None:
    import codex_cognitive_sdk

    assert set(codex_cognitive_sdk.__all__) == {
        "ActionResult",
        "Decision",
        "GovernanceDecision",
        "GovernanceProtocol",
        "GovernanceRequest",
        "MemoryProtocol",
        "MemoryQuery",
        "MemoryRecord",
        "Observation",
        "OODACycle",
        "OODAProtocol",
        "Orientation",
        "__version__",
    }


def test_contracts_are_constructible_from_package_root() -> None:
    from codex_cognitive_sdk import (
        ActionResult,
        Decision,
        GovernanceDecision,
        GovernanceRequest,
        MemoryQuery,
        MemoryRecord,
        Observation,
        OODACycle,
        Orientation,
    )

    now = datetime.now(timezone.utc)
    observation = Observation(source="test", data={"signal": True}, observed_at=now)
    orientation = Orientation(context={}, analysis="safe", confidence=1.0)
    decision = Decision(action="continue", confidence=1.0)
    result = ActionResult(success=True)

    assert GovernanceRequest("agent", "read", "memory").action == "read"
    assert GovernanceDecision(allowed=True).allowed
    assert MemoryRecord("memory-1", "value", now).content == "value"
    assert MemoryQuery(limit=5).limit == 5
    assert OODACycle(observation, orientation, decision, result).result.success

"""Codex-provided stub for Hydra's ``hydra.extra`` setuptools plugin.

The real plugin ships with some Hydra distributions, but offline or minimal
installations used in CI often omit it which breaks implicit imports triggered
by Hydra's auto-discovery.  This stub keeps the import resolvable while clearly
signalling that the implementation is a lightweight placeholder.
"""

from __future__ import annotations

import sys
import types
from dataclasses import dataclass
from typing import Optional

__all__ = ["HydraExtraStatus", "ensure", "ensure_registered", "status", "__version__"]

__version__ = "0.1.0.dev0"


@dataclass(frozen=True)
class HydraExtraStatus:
    """Expose the state of the shim so callers can introspect behaviour."""

    available: bool
    reason: Optional[str] = None


def _build_stub_module() -> types.ModuleType:
    module = types.ModuleType("hydra.extra")
    module.__doc__ = (
        "Codex stub for the hydra.extra plugin. The full plugin is unavailable, "
        "so the shim exports minimal markers only."
    )
    module.AVAILABLE = False  # type: ignore[attr-defined]
    module.STUB = True  # type: ignore[attr-defined]
    return module


def ensure_registered() -> types.ModuleType:
    """Guarantee that ``hydra.extra`` can be imported."""

    existing = sys.modules.get("hydra.extra")
    if isinstance(existing, types.ModuleType):
        return existing
    module = _build_stub_module()
    sys.modules["hydra.extra"] = module
    return module


def ensure() -> types.ModuleType:
    """Alias for :func:`ensure_registered` to mirror the real plugin."""

    return ensure_registered()


def status() -> HydraExtraStatus:
    module = sys.modules.get("hydra.extra")
    if isinstance(module, types.ModuleType) and getattr(module, "STUB", False):
        return HydraExtraStatus(available=False, reason="codex-stub")
    return HydraExtraStatus(available=True)


ensure_registered()

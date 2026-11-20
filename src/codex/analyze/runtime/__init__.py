"""Compatibility package for the runtime analysis API.

The canonical implementation lives in ``aries_serpent_core.analyze.runtime``.
The aliases share module state, including monkeypatches, with that package.
"""

from __future__ import annotations

import sys

from aries_serpent_core.analyze.runtime import (
    ExecutionResult,
    RuntimeReport,
    RuntimeTracer,
    SandboxConfig,
    SandboxManager,
    sandbox,
    tracer,
)

sys.modules.setdefault(f"{__name__}.sandbox", sandbox)
sys.modules.setdefault(f"{__name__}.tracer", tracer)

__all__ = [
    "ExecutionResult",
    "RuntimeReport",
    "RuntimeTracer",
    "SandboxConfig",
    "SandboxManager",
    "sandbox",
    "tracer",
]

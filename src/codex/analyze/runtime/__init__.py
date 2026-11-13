"""Compatibility package for the runtime analysis API.

The canonical implementation lives in ``aries_serpent_core.analyze.runtime``.
This package keeps the documented ``codex.analyze.runtime`` import path (see
``src/aries_serpent_core/README.md``) working, including the ``.sandbox`` and
``.tracer`` submodules. The submodules are aliased (not re-executed) so module
state and monkeypatching are shared with the canonical implementation.
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

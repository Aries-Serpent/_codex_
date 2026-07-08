"""Lightweight seed-state registry.

This module owns the global RNG-state snapshot variables and the
``register_seed_snapshot`` function.  It is intentionally import-light so that
both ``seeding.py`` and ``checkpointing.py`` can import from here without
creating a circular-import cycle (DR-001).

Design constraint: **no imports from other codex_ml.utils sub-modules**.
"""

from __future__ import annotations

from typing import Any, Optional

# ---------------------------------------------------------------------------
# Module-level RNG state cache (last seeded snapshot)
# ---------------------------------------------------------------------------

_LAST_SEEDED_PYTHON_STATE: Optional[tuple[Any, ...]] = None
_LAST_SEEDED_NUMPY_STATE: Optional[Any] = None
_LAST_SEEDED_TORCH_STATE: Optional[Any] = None
_LAST_SEEDED_TORCH_CUDA_STATE: Optional[Any] = None


def register_seed_snapshot(
    *,
    python_state: Optional[Any] = None,
    numpy_state: Optional[Any] = None,
    torch_state: Optional[Any] = None,
    torch_cuda_state: Optional[Any] = None,
) -> None:
    """Record RNG states captured immediately after a seeding operation.

    All arguments are keyword-only.  Pass only the states that changed.
    """

    global _LAST_SEEDED_PYTHON_STATE
    global _LAST_SEEDED_NUMPY_STATE
    global _LAST_SEEDED_TORCH_STATE
    global _LAST_SEEDED_TORCH_CUDA_STATE

    if python_state is not None:
        _LAST_SEEDED_PYTHON_STATE = python_state
    if numpy_state is not None:
        _LAST_SEEDED_NUMPY_STATE = numpy_state
    if torch_state is not None:
        _LAST_SEEDED_TORCH_STATE = torch_state
    if torch_cuda_state is not None:
        _LAST_SEEDED_TORCH_CUDA_STATE = torch_cuda_state


def get_last_seed_snapshot() -> dict[str, Any]:
    """Return a copy of the last recorded seed snapshot."""

    return {
        "python": _LAST_SEEDED_PYTHON_STATE,
        "numpy": _LAST_SEEDED_NUMPY_STATE,
        "torch": _LAST_SEEDED_TORCH_STATE,
        "torch_cuda": _LAST_SEEDED_TORCH_CUDA_STATE,
    }


__all__ = [
    "get_last_seed_snapshot",
    "register_seed_snapshot",
]

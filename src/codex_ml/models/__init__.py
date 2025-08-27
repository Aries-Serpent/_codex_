"""Model implementations for Codex ML.

Historically importing :mod:`codex_ml.models` would eagerly import the
``minilm`` model.  That model depends on optional heavy dependencies (for
example :mod:`torch`) which are not available in the execution environment used
for the tests.  The eager import therefore triggered a
``ModuleNotFoundError`` even when only lightweight utilities such as
``codex_ml.models.activations`` were required.

To make the package robust we attempt to import ``minilm`` lazily and fall back
to ``None`` when those dependencies are missing.  This keeps the public API
intact while allowing the rest of the package to be imported without the full
ML stack.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

try:  # pragma: no cover - optional dependency
    from .minilm import MiniLM, MiniLMConfig
except Exception:  # pragma: no cover - dependency not installed
    MiniLM = None  # type: ignore[assignment]
    MiniLMConfig = None  # type: ignore[assignment]

if TYPE_CHECKING:  # retain type information for type checkers
    from .minilm import MiniLM, MiniLMConfig

__all__ = ["MiniLM", "MiniLMConfig"]

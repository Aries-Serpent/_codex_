"""Compatibility wrapper for the legacy ``codex.rag`` namespace.

The canonical RAG implementation lives under ``src/aries_serpent_core/rag`` and
``src/rag``. The branch's generated tests import ``codex.rag.*`` directly, so
we expose that namespace without changing the real implementations.
"""

from __future__ import annotations

from pathlib import Path

_src_root = Path(__file__).resolve().parents[2]
_legacy_rag = _src_root / "aries_serpent_core" / "rag"
_root_rag = _src_root / "rag"

# Allow Python to resolve ``codex.rag.<module>`` to the real RAG package.
__path__ = [str(Path(__file__).resolve().parent), str(_legacy_rag), str(_root_rag)]

try:
    from aries_serpent_core.rag import *  # noqa: F401,F403
except Exception:
    try:
        from rag import *  # noqa: F401,F403
    except Exception:  # pragma: no cover - compatibility fallback
        pass

__all__ = []

"""Proxy package that loads repository-local ``codex_utils`` implementation."""

from __future__ import annotations

import importlib.util
import pathlib
import sys

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
_IMPL_PATH = _REPO_ROOT / "codex_utils" / "__init__.py"

if not _IMPL_PATH.exists():  # pragma: no cover - repository layout unexpected
    raise ImportError("codex_utils package implementation not found in repository root")

_spec = importlib.util.spec_from_file_location("codex_utils._repo_impl", _IMPL_PATH)
if _spec is None or _spec.loader is None:  # pragma: no cover - defensive
    raise ImportError(f"Unable to load codex_utils implementation from {_IMPL_PATH}")
_module = importlib.util.module_from_spec(_spec)
sys.modules.setdefault(_spec.name, _module)
_spec.loader.exec_module(_module)

# Replace current module entry with the implementation module so that
# submodule imports (e.g. ``codex_utils.repro``) resolve correctly.
sys.modules[__name__] = _module

__all__ = getattr(_module, "__all__", [])
globals().update({k: getattr(_module, k) for k in __all__})

for key, value in _module.__dict__.items():
    if key.startswith("_") or key in globals():
        continue
    globals()[key] = value

"""
Legacy compatibility shim for engine_hf_trainer module.

DEPRECATED: Use ``src.training.engine_hf_trainer`` directly.
This file is a thin re-export shim maintained for backward compatibility with
scripts that import ``from training.engine_hf_trainer import ...``.

Migration guide:
  Replace ``from training.engine_hf_trainer import X``
  with    ``from src.training.engine_hf_trainer import X``
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "Importing from 'training.engine_hf_trainer' is deprecated. "
    "Use 'src.training.engine_hf_trainer' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from src.training.engine_hf_trainer import *  # noqa: E402, F401, F403

import src.training.engine_hf_trainer as _src_mod  # noqa: E402

# Re-expose private helpers needed by tests that monkeypatch via
# "training.engine_hf_trainer.<name>".
try:
    _make_accelerator = _src_mod._make_accelerator  # type: ignore[attr-defined]
except AttributeError:  # pragma: no cover
    pass

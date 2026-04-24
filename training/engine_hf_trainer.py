"""
Legacy compatibility shim for engine_hf_trainer module.

DEPRECATED: Use ``src.training.engine_hf_trainer`` directly.
This file is a thin re-export shim maintained for backward compatibility with
scripts that import ``from training.engine_hf_trainer import ...``.

Migration guide:
  Replace ``from training.engine_hf_trainer import X``
  with    ``from src.training.engine_hf_trainer import X``

Implementation note:
  The shim aliases ``sys.modules[__name__]`` to the source module so that all
  symbols (including private helpers and re-imported third-party names like
  ``AutoTokenizer``) are transparently visible, and so that
  ``monkeypatch.setattr("training.engine_hf_trainer.X", ...)`` correctly
  patches the real symbol used by ``run_hf_trainer`` inside
  ``src.training.engine_hf_trainer``.
"""

from __future__ import annotations

import sys as _sys
import warnings as _warnings

_warnings.warn(
    "Importing from 'training.engine_hf_trainer' is deprecated. "
    "Use 'src.training.engine_hf_trainer' instead.",
    DeprecationWarning,
    stacklevel=2,
)

import src.training.engine_hf_trainer as _src_mod  # noqa: E402

# Alias the module in sys.modules so that subsequent imports of
# ``training.engine_hf_trainer`` resolve to the source module and monkeypatches
# applied via the legacy name reach the real symbol namespace.
_sys.modules[__name__] = _src_mod

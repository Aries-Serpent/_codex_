"""
Legacy compatibility shim for functional_training module.

DEPRECATED: Use ``src.training.functional_training`` directly.
This file is a thin re-export shim maintained for backward compatibility with
scripts that import ``from training.functional_training import ...``.

Migration guide:
  Replace ``from training.functional_training import X``
  with    ``from src.training.functional_training import X``

Implementation note:
  The shim aliases ``sys.modules[__name__]`` to the source module so that all
  symbols (including private helpers and bare-module imports like ``torch``)
  are transparently visible and so that monkeypatches applied via the legacy
  name reach the real symbols used by ``_maybe_collect_system_metrics`` etc.
"""

from __future__ import annotations

import sys as _sys
import warnings as _warnings

_warnings.warn(
    "Importing from 'training.functional_training' is deprecated. "
    "Use 'src.training.functional_training' instead.",
    DeprecationWarning,
    stacklevel=2,
)

import src.training.functional_training as _src_mod  # noqa: E402

_sys.modules[__name__] = _src_mod

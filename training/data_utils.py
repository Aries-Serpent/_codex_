"""
Legacy compatibility shim for data_utils module.

DEPRECATED: Use ``src.training.data_utils`` directly.
This file is a thin re-export shim maintained for backward compatibility with
scripts that import ``from training.data_utils import ...``.

Migration guide:
  Replace ``from training.data_utils import X``
  with    ``from src.training.data_utils import X``

Implementation note:
  The shim aliases ``sys.modules[__name__]`` to the source module so that all
  symbols (including private helpers like ``_stable_checksum_of_seq_repr`` and
  ``_require_torch``) are transparently visible and so that monkeypatches
  applied via the legacy name reach the real symbols.
"""

from __future__ import annotations

import sys as _sys
import warnings as _warnings

_warnings.warn(
    "Importing from 'training.data_utils' is deprecated. "
    "Use 'src.training.data_utils' instead.",
    DeprecationWarning,
    stacklevel=2,
)

import src.training.data_utils as _src_mod  # noqa: E402

_sys.modules[__name__] = _src_mod

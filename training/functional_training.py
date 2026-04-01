"""
Legacy compatibility shim for functional_training module.

DEPRECATED: Use ``src.training.functional_training`` directly.
This file is a thin re-export shim maintained for backward compatibility with
scripts that import ``from training.functional_training import ...``.

Migration guide:
  Replace ``from training.functional_training import X``
  with    ``from src.training.functional_training import X``
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "Importing from 'training.functional_training' is deprecated. "
    "Use 'src.training.functional_training' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from src.training.functional_training import *  # noqa: E402, F401, F403

import src.training.functional_training as _src_mod  # noqa: E402

# Re-expose private helpers and module-level names (e.g. ``torch``) that tests
# monkeypatch via "training.functional_training.<name>".  ``import *`` only
# exports public names, so private symbols and bare-module imports from the
# source file must be forwarded explicitly.
# Example: ``monkeypatch.setattr("training.functional_training.torch.optim.AdamW", ...)``
for _name in ("torch", "_codex_logging_bootstrap", "_codex_log_all"):
    _val = getattr(_src_mod, _name, None)
    if _val is not None:
        globals()[_name] = _val
del _name, _val

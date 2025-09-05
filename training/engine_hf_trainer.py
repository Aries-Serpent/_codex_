"""Backward-compatibility wrapper for :mod:`training.engine_hf_trainer`.

This shim re-exports public symbols from ``engine_hf_trainer.py-user-review`` so
that existing imports of ``training.engine_hf_trainer`` continue to work after
the file was renamed for review.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_module_name = "engine_hf_trainer_user_review"
_module_path = Path(__file__).with_name("engine_hf_trainer.py-user-review")
_spec = importlib.util.spec_from_file_location(_module_name, _module_path)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise ImportError(f"Cannot load {_module_name} from {_module_path}")

_engine_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_engine_module)

__all__ = getattr(
    _engine_module,
    "__all__",
    [name for name in dir(_engine_module) if not name.startswith("_")],
)

globals().update({name: getattr(_engine_module, name) for name in __all__})

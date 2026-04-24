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

import src.training.engine_hf_trainer as _src_mod  # noqa: E402
from src.training.engine_hf_trainer import *  # noqa: E402, F401, F403

# Re-expose helpers and re-imported third-party symbols needed by tests that
# monkeypatch via "training.engine_hf_trainer.<name>".  ``import *`` only
# exports names listed in ``__all__`` (and never underscore-prefixed ones), so
# any symbol patched through this shim must be forwarded explicitly.
# Example: ``monkeypatch.setattr("training.engine_hf_trainer.AutoTokenizer", ...)``
_FORWARDED_NAMES = (
    # Private helpers
    "_make_accelerator",
    # Transformers symbols re-imported in src.training.engine_hf_trainer
    "AutoModelForCausalLM",
    "AutoTokenizer",
    "DataCollatorForLanguageModeling",
    "Trainer",
    "TrainingArguments",
    "TrainerCallback",
    "EarlyStoppingCallback",
    # Codex-internal helpers re-imported in src.training.engine_hf_trainer
    "apply_lora",
    "set_reproducible",
    "set_seed",
)
for _name in _FORWARDED_NAMES:
    _val = getattr(_src_mod, _name, None)
    if _val is not None:
        globals()[_name] = _val
del _name, _val

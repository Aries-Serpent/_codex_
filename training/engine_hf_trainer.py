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
from src.training.engine_hf_trainer import (  # noqa: E402, F401
    AsyncLogFile,
    CSVMetricsWriter,
    HFTrainerConfig,
    NDJSONMetricsWriter,
    build_trainer,
    build_training_args,
    get_hf_revision,
    run_hf_trainer,
)

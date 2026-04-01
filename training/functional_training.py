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
from src.training.functional_training import (  # noqa: E402, F401
    TrainCfg,
    evaluate_batches,
    evaluate_dataloader,
    main,
    run_custom_trainer,
)

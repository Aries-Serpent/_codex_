"""
Legacy compatibility shim for data_utils module.

DEPRECATED: Use ``src.training.data_utils`` directly.
This file is a thin re-export shim maintained for backward compatibility with
scripts that import ``from training.data_utils import ...``.

Migration guide:
  Replace ``from training.data_utils import X``
  with    ``from src.training.data_utils import X``
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "Importing from 'training.data_utils' is deprecated. "
    "Use 'src.training.data_utils' instead.",
    DeprecationWarning,
    stacklevel=2,
)

from src.training.data_utils import *  # noqa: E402, F401, F403
from src.training.data_utils import (  # noqa: E402, F401
    TextDataset,
    cache_dataset,
    load_cached,
    split_dataset,
    split_texts,
)

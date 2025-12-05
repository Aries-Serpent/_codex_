"""
Legacy compatibility layer for training module.

DEPRECATED: Use src.training.* instead.
This module provides backward compatibility by re-exporting from canonical src.training.
"""
import warnings as _warnings

_warnings.warn(
    "Importing from 'training' is deprecated. Use 'src.training' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export all public members from canonical src.training modules
from src.training.engine_hf_trainer import *  # noqa: F401, F403
from src.training.functional_training import *  # noqa: F401, F403
from src.training.data_utils import *  # noqa: F401, F403
from src.training.checkpoint_manager import *  # noqa: F401, F403
from src.training.config import *  # noqa: F401, F403
from src.training.trainer import *  # noqa: F401, F403

# Build __all__ from all imported modules
import src.training.engine_hf_trainer as _m1
import src.training.functional_training as _m2
import src.training.data_utils as _m3
import src.training.checkpoint_manager as _m4
import src.training.config as _m5
import src.training.trainer as _m6

__all__ = []
for _mod in [_m1, _m2, _m3, _m4, _m5, _m6]:
    __all__.extend([_name for _name in dir(_mod) if not _name.startswith("_")])

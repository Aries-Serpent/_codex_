"""
Legacy compatibility layer for training module.

DEPRECATED: Use src.training.* instead.
This module provides backward compatibility by re-exporting from canonical src.training.
"""

import warnings as _warnings

_warnings.warn(
    "Importing from 'training' is deprecated. Use 'src.training' instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export all public members from canonical src.training modules
from src.training.checkpoint_manager import CheckpointManager  # noqa: F401
from src.training.config import TrainingConfig  # noqa: F401
from src.training.data_utils import (  # noqa: F401
    TextDataset,
    cache_dataset,
    deterministic_shuffle,
    load_cached,
    split_dataset,
    split_texts,
)
from src.training.engine_hf_trainer import (  # noqa: F401
    CSVMetricsWriter,
    HFTrainerConfig,
    NDJSONMetricsWriter,
    build_parser,
    build_trainer,
    build_training_args,
    load_training_arguments,
    prepare_dataset,
    run_hf_trainer,
)
from src.training.functional_training import (  # noqa: F401
    TrainCfg,
    evaluate_batches,
    evaluate_dataloader,
    main,
    run_custom_trainer,
)
from src.training.trainer import (  # noqa: F401
    CheckpointConfig,
    Trainer,
    TrainerConfig,
)

__all__ = [
    "CheckpointManager",
    "TrainingConfig",
    "TextDataset",
    "cache_dataset",
    "deterministic_shuffle",
    "load_cached",
    "split_dataset",
    "split_texts",
    "CSVMetricsWriter",
    "HFTrainerConfig",
    "NDJSONMetricsWriter",
    "build_parser",
    "build_trainer",
    "build_training_args",
    "load_training_arguments",
    "prepare_dataset",
    "run_hf_trainer",
    "TrainCfg",
    "evaluate_batches",
    "evaluate_dataloader",
    "main",
    "run_custom_trainer",
    "CheckpointConfig",
    "Trainer",
    "TrainerConfig",
]

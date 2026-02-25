"""
CLI Pipeline Module

Pipeline orchestration for CLI commands.
"""

from pathlib import Path
from typing import Any, Dict, Optional


class PipelineValidationError(Exception):
    """Raised when pipeline configuration validation fails."""
    pass


def validate_pipeline_config(config: Dict[str, Any]) -> None:
    """
    Validate pipeline configuration.

    Args:
        config: Pipeline configuration dictionary

    Raises:
        KeyError: If required configuration keys are missing
        ValueError: If configuration values are invalid

    Examples:
        >>> validate_pipeline_config({"data": {}, "model": {}})
        >>> validate_pipeline_config({})  # doctest: +SKIP
        Traceback (most recent call last):
        ...
        KeyError: 'data'
    """
    # Check required keys
    if "data" not in config:
        raise KeyError("data configuration is required")

    # Validate checkpoint if provided
    if "trainer" in config and isinstance(config["trainer"], dict):
        checkpoint = config["trainer"].get("checkpoint")
        if checkpoint is not None:
            # If checkpoint is a string, it should be a valid path
            if isinstance(checkpoint, str):
                ckpt_path = Path(checkpoint)
                if not ckpt_path.exists():
                    raise ValueError(f"checkpoint file not found: {checkpoint}")
            # If checkpoint is not a dict, it's invalid
            elif not isinstance(checkpoint, dict):
                raise ValueError(
                    f"checkpoint must be a dict or path string, got {type(checkpoint).__name__}"
                )


def run_pipeline(
    model: Any,
    tokenizer: Optional[Any],
    train_ds: Optional[Any],
    val_ds: Optional[Any],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Run training pipeline with validation.

    Args:
        model: Model to train
        tokenizer: Optional tokenizer
        train_ds: Training dataset
        val_ds: Optional validation dataset
        config: Pipeline configuration

    Returns:
        Dictionary with training results

    Raises:
        KeyError: If required configuration is missing
        ValueError: If configuration is invalid
    """
    # Validate configuration first
    validate_pipeline_config(config)

    raise NotImplementedError(
        "run_pipeline() is not yet implemented. "
        "Wire to src/codex_ml/training/functional_training.py::run_functional_training "
        "or src/codex/training.py::run_custom_trainer before using in production."
    )

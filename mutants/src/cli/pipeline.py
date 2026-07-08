"""
CLI Pipeline Module

Pipeline orchestration for CLI commands.
"""

from pathlib import Path
from typing import Any, Optional


class PipelineValidationError(Exception):
    """Raised when pipeline configuration validation fails."""


def validate_pipeline_config(config: dict[str, Any]) -> None:
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
    config: dict[str, Any],
) -> dict[str, Any]:
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

    try:
        from codex_ml.training.functional_training import TrainConfig, train

        trainer_cfg = config.get("trainer", {})
        _defaults = TrainConfig()
        train_cfg = TrainConfig(
            epochs=trainer_cfg.get("epochs", _defaults.epochs),
            batch_size=trainer_cfg.get("batch_size", _defaults.batch_size),
            lr=trainer_cfg.get("lr", _defaults.lr),
            seed=trainer_cfg.get("seed", _defaults.seed),
            gradient_accumulation_steps=trainer_cfg.get(
                "gradient_accumulation_steps", _defaults.gradient_accumulation_steps
            ),
            checkpoint_dir=trainer_cfg.get("checkpoint_dir", _defaults.checkpoint_dir),
        )

        # Extract texts from train_ds
        if train_ds is None:
            texts: list[str] = []
        elif isinstance(train_ds, list):
            texts = train_ds
        elif hasattr(train_ds, "texts"):
            texts = list(train_ds.texts)
        else:
            try:
                texts = list(train_ds)
            except TypeError as exc:
                raise ValueError(
                    f"train_ds must be a list, have a .texts attribute, or be iterable; "
                    f"got {type(train_ds).__name__}"
                ) from exc

        # Extract val_texts from val_ds
        val_texts = None
        if val_ds is not None:
            if isinstance(val_ds, list):
                val_texts = val_ds
            elif hasattr(val_ds, "texts"):
                val_texts = list(val_ds.texts)
            else:
                try:
                    val_texts = list(val_ds)
                except TypeError as exc:
                    raise ValueError(
                        f"val_ds must be a list, have a .texts attribute, or be iterable; "
                        f"got {type(val_ds).__name__}"
                    ) from exc

        metrics = train(texts, config=train_cfg, val_texts=val_texts, model=model)
        return {"status": "ok", "metrics": metrics}
    except Exception as e:
        return {"status": "error", "error": str(e)}

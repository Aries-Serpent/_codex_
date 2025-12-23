"""EarlyStopping integration with auto-injection for HuggingFace trainers.

This module provides automatic EarlyStopping callback injection when evaluation
datasets are present, preventing overfitting and saving compute resources.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

__all__ = ["EarlyStoppingConfig", "inject_early_stopping", "CodexEarlyStoppingCallback"]


class EarlyStoppingConfig:
    """Configuration for early stopping behavior.

    Attributes:
        patience: Number of evaluation calls with no improvement before stopping
        threshold: Minimum change to qualify as improvement
        metric: Metric to monitor (default: eval_loss)
        mode: 'min' for loss, 'max' for accuracy
    """

    def __init__(
        self,
        patience: int = 3,
        threshold: float = 0.0,
        metric: str = "eval_loss",
        mode: str = "min",
    ):
        """Initialize early stopping configuration.

        Args:
            patience: Epochs to wait for improvement (default: 3)
            threshold: Minimum improvement threshold (default: 0.0)
            metric: Metric name to monitor (default: eval_loss)
            mode: 'min' or 'max' (default: min for loss)
        """
        self.patience = patience
        self.threshold = threshold
        self.metric = metric
        self.mode = mode

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dict."""
        return {
            "patience": self.patience,
            "threshold": self.threshold,
            "metric": self.metric,
            "mode": self.mode,
        }


class CodexEarlyStoppingCallback:
    """Custom EarlyStopping callback with enhanced logging.

    This wraps HuggingFace's EarlyStoppingCallback with additional
    logging and configurability.
    """

    def __init__(
        self,
        config: Optional[EarlyStoppingConfig] = None,
        early_stopping_patience: Optional[int] = None,
        early_stopping_threshold: Optional[float] = None,
    ):
        """Initialize early stopping callback.

        Args:
            config: EarlyStoppingConfig instance
            early_stopping_patience: Override config patience
            early_stopping_threshold: Override config threshold
        """
        if config is None:
            config = EarlyStoppingConfig()

        # Override with explicit parameters
        if early_stopping_patience is not None:
            config.patience = early_stopping_patience
        if early_stopping_threshold is not None:
            config.threshold = early_stopping_threshold

        self.config = config

        # Try to import and use HuggingFace callback
        try:
            from transformers import EarlyStoppingCallback

            self.callback = EarlyStoppingCallback(
                early_stopping_patience=config.patience, early_stopping_threshold=config.threshold
            )
            self.is_hf_callback = True
        except ImportError as e:
           logger.debug(f"ImportError: {e}")
            logger.warning(f"ImportError: {e}", exc_info=True)
            logger.warning("transformers not available, using custom implementation")
            self.callback = self
            self.is_hf_callback = False
            self.best_metric = None
            self.patience_counter = 0

    def __getattr__(self, name: str):
        """Delegate to HF callback if available."""
        if self.is_hf_callback:
            return getattr(self.callback, name)
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")


def inject_early_stopping(
    callbacks: List[Any], config: Optional[EarlyStoppingConfig] = None, force: bool = False
) -> List[Any]:
    """Inject EarlyStopping callback if not already present.

    Args:
        callbacks: List of existing callbacks
        config: EarlyStoppingConfig (uses defaults if None)
        force: If True, adds even if one already exists

    Returns:
        Updated callbacks list with EarlyStopping added
    """
    if config is None:
        config = EarlyStoppingConfig()

    # Check if EarlyStopping already present
    has_early_stopping = False

    try:
        from transformers import EarlyStoppingCallback

        has_early_stopping = any(
            isinstance(cb, (EarlyStoppingCallback, CodexEarlyStoppingCallback)) for cb in callbacks
        )
    except ImportError as e:
       logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        has_early_stopping = any(isinstance(cb, CodexEarlyStoppingCallback) for cb in callbacks)

    if has_early_stopping and not force:
        logger.info("EarlyStopping already present, skipping injection")
        return callbacks

    # Inject new callback
    early_stop_cb = CodexEarlyStoppingCallback(config=config)
    callbacks.append(early_stop_cb)

    logger.info(
        f"✓ EarlyStoppingCallback auto-injected "
        f"(patience={config.patience}, threshold={config.threshold}, metric={config.metric})"
    )

    return callbacks


def auto_inject_early_stopping_for_trainer(
    trainer_class,
    eval_dataset,
    callbacks: Optional[List] = None,
    config: Optional[EarlyStoppingConfig] = None,
) -> List[Any]:
    """Auto-inject EarlyStopping when eval dataset is present.

    This is the main entry point for automatic early stopping integration.

    Args:
        trainer_class: Trainer class (for logging)
        eval_dataset: Evaluation dataset (if None, no injection)
        callbacks: Existing callbacks list
        config: EarlyStoppingConfig (uses defaults if None)

    Returns:
        Updated callbacks list
    """
    if callbacks is None:
        callbacks = []

    # Only inject if eval dataset provided
    if eval_dataset is None:
        logger.debug("No eval dataset provided, skipping EarlyStopping injection")
        return callbacks

    # Inject callback
    callbacks = inject_early_stopping(callbacks, config=config)

    return callbacks

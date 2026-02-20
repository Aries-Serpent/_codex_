"""EarlyStopping integration with auto-injection for HuggingFace trainers.

This module provides automatic EarlyStopping callback injection when evaluation
datasets are present, preventing overfitting and saving compute resources.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

__all__ = [
    "EarlyStoppingConfig",
    "EarlyStopping",
    "inject_early_stopping",
    "CodexEarlyStoppingCallback",
    "EarlyStoppingCallback",
    "create_early_stopping_from_config",
]


class EarlyStoppingConfig:
    """Configuration for early stopping behavior.

    Attributes:
        patience: Number of evaluation calls with no improvement before stopping
        threshold: Minimum change to qualify as improvement
        metric: Metric to monitor (default: eval_loss)
        mode: 'min' for loss, 'max' for accuracy
        enabled: Whether early stopping is enabled (default: True)
        monitor: Alias for metric parameter (for compatibility)
    """

    def __init__(
        self,
        patience: int = 3,
        threshold: float = 0.0,
        metric: str = "eval_loss",
        mode: str = "min",
        enabled: bool = False,
        monitor: Optional[str] = None,
    ):
        """Initialize early stopping configuration.

        Args:
            patience: Epochs to wait for improvement (default: 3)
            threshold: Minimum improvement threshold (default: 0.0)
            metric: Metric name to monitor (default: eval_loss)
            mode: 'min' or 'max' (default: min for loss)
            enabled: Whether early stopping is enabled (default: False)
            monitor: Alias for metric parameter (default: None)
        """
        self.patience = patience
        self.threshold = threshold
        self.metric = monitor if monitor is not None else metric
        self.monitor = self.metric  # Alias
        self.mode = mode
        self.enabled = enabled

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dict."""
        return {
            "patience": self.patience,
            "threshold": self.threshold,
            "metric": self.metric,
            "mode": self.mode,
            "enabled": self.enabled,
            "monitor": self.monitor,
        }


class EarlyStopping:
    """Standalone EarlyStopping implementation for non-HuggingFace training loops.
    
    Attributes:
        patience: Number of evaluation calls with no improvement before stopping
        monitor: Metric name to monitor
        mode: 'min' for metrics that should decrease, 'max' for metrics that should increase
    """

    def __init__(
        self,
        patience: int = 3,
        monitor: str = "val_loss",
        mode: str = "min",
    ):
        """Initialize early stopping.

        Args:
            patience: Epochs to wait for improvement (default: 3)
            monitor: Metric name to monitor (default: val_loss)
            mode: 'min' or 'max' (default: min for loss)
        """
        self.patience = patience
        self.monitor = monitor
        self.mode = mode
        self.best_metric = None
        self.patience_counter = 0
        self.should_stop = False

    def check_metric(self, metrics: dict[str, float]) -> bool:
        """Check if training should stop based on metric.

        Args:
            metrics: Dictionary of metric values

        Returns:
            True if training should stop, False otherwise
        """
        if self.monitor not in metrics:
            logger.warning(f"Monitored metric '{self.monitor}' not found in metrics")
            return False

        current_metric = metrics[self.monitor]

        # First evaluation
        if self.best_metric is None:
            self.best_metric = current_metric
            return False

        # Check if improved
        improved = False
        if self.mode == "min":
            improved = current_metric < self.best_metric
        else:  # max
            improved = current_metric > self.best_metric

        if improved:
            self.best_metric = current_metric
            self.patience_counter = 0
        else:
            self.patience_counter += 1

        if self.patience_counter >= self.patience:
            self.should_stop = True
            logger.info(
                f"Early stopping triggered: no improvement in {self.monitor} "
                f"for {self.patience} evaluations"
            )
            return True

        return False


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
    callbacks: list[Any], config: Optional[EarlyStoppingConfig] = None, force: bool = False
) -> list[Any]:
    """Inject EarlyStopping callback if not already present.

    Args:
        callbacks: list of existing callbacks
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

        # Check isinstance for real instances, or check type name for mocks
        has_early_stopping = any(
            isinstance(cb, (EarlyStoppingCallback, CodexEarlyStoppingCallback))
            or type(cb).__name__ in ("EarlyStoppingCallback", "CodexEarlyStoppingCallback")
            for cb in callbacks
        )
    except ImportError as e:
        logger.debug(f"ImportError: {e}")
        logger.warning(f"ImportError: {e}", exc_info=True)
        has_early_stopping = any(
            isinstance(cb, CodexEarlyStoppingCallback)
            or type(cb).__name__ == "CodexEarlyStoppingCallback"
            for cb in callbacks
        )

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
    callbacks: Optional[list] = None,
    config: Optional[EarlyStoppingConfig] = None,
) -> list[Any]:
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


def create_early_stopping_from_config(config: EarlyStoppingConfig) -> Optional[EarlyStopping]:
    """Create EarlyStopping instance from configuration.

    Args:
        config: EarlyStoppingConfig instance

    Returns:
        EarlyStopping instance if enabled, None otherwise
    """
    if not getattr(config, 'enabled', True):
        return None

    return EarlyStopping(
        patience=getattr(config, 'patience', 3),
        monitor=getattr(config, 'monitor', getattr(config, 'metric', 'val_loss')),
        mode=getattr(config, 'mode', 'min'),
    )


# Alias for backward compatibility
EarlyStoppingCallback = CodexEarlyStoppingCallback

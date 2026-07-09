"""EarlyStopping integration with auto-injection for HuggingFace trainers.

This module provides automatic EarlyStopping callback injection when evaluation
datasets are present, preventing overfitting and saving compute resources.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

__all__ = [
    "CodexEarlyStoppingCallback",
    "EarlyStopping",
    "EarlyStoppingCallback",
    "EarlyStoppingConfig",
    "create_early_stopping_from_config",
    "inject_early_stopping",
]


class EarlyStoppingConfig:
    """Configuration for early stopping behavior.

    Attributes:
        patience: Number of evaluation calls with no improvement before stopping
        threshold: Minimum change to qualify as improvement (alias for min_delta)
        min_delta: Minimum change to qualify as improvement
        metric: Metric to monitor (default: eval_loss)
        mode: 'min' for loss, 'max' for accuracy
        enabled: Whether early stopping is enabled (default: False)
        monitor: Alias for metric parameter (for compatibility)
        verbose: Whether to log early stopping events (default: True)
    """

    def __init__(
        self,
        patience: int = 3,
        threshold: float = 0.0,
        metric: str = "eval_loss",
        mode: str = "min",
        enabled: bool = False,
        monitor: Optional[str] = None,
        min_delta: Optional[float] = None,
        verbose: bool = True,
    ):
        """Initialize early stopping configuration.

        Args:
            patience: Epochs to wait for improvement (default: 3)
            threshold: Minimum improvement threshold (default: 0.0, alias for min_delta)
            metric: Metric name to monitor (default: eval_loss)
            mode: 'min' or 'max' (default: min for loss)
            enabled: Whether early stopping is enabled (default: False)
            monitor: Alias for metric parameter (default: None)
            min_delta: Minimum change to qualify as improvement (default: 1e-4)
            verbose: Whether to log early stopping events (default: True)
        """
        self.patience = patience
        # min_delta takes precedence, otherwise use threshold, otherwise default
        if min_delta is not None:
            self.min_delta = min_delta
            self.threshold = min_delta
        elif threshold != 0.0:
            self.min_delta = threshold
            self.threshold = threshold
        else:
            self.min_delta = 1e-4
            self.threshold = 0.0  # Respect the explicit threshold=0.0; use min_delta internally
        self.metric = monitor if monitor is not None else metric
        # Default monitor to "val_loss" if metric is still "eval_loss"
        if self.metric == "eval_loss" and monitor is None:
            self.monitor = "val_loss"
        else:
            self.monitor = self.metric  # Alias
        self.mode = mode
        self.enabled = enabled
        self.verbose = verbose

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dict."""
        return {
            "patience": self.patience,
            "threshold": self.threshold,
            "min_delta": self.min_delta,
            "metric": self.metric,
            "mode": self.mode,
            "enabled": self.enabled,
            "monitor": self.monitor,
            "verbose": self.verbose,
        }


class EarlyStopping:
    """Standalone EarlyStopping implementation for non-HuggingFace training loops.

    Attributes:
        patience: Number of evaluation calls with no improvement before stopping
        monitor: Metric name to monitor
        mode: 'min' for metrics that should decrease, 'max' for metrics that should increase
        min_delta: Minimum change to qualify as improvement
        verbose: Whether to log early stopping events
        wait: Current count of evaluations with no improvement
        best_value: Best metric value observed
        best_epoch: Epoch when best value was observed
        stopped_epoch: Epoch when training was stopped (0 if not stopped)
    """

    def __init__(
        self,
        patience: int = 3,
        monitor: str = "val_loss",
        mode: str = "min",
        min_delta: float = 0.0,
        verbose: bool = True,
    ):
        """Initialize early stopping.

        Args:
            patience: Epochs to wait for improvement (default: 3)
            monitor: Metric name to monitor (default: val_loss)
            mode: 'min' or 'max' (default: min for loss)
            min_delta: Minimum change to qualify as improvement (default: 0.0)
            verbose: Whether to log early stopping events (default: True)

        Raises:
            ValueError: If patience <= 0 or mode not in ['min', 'max']
        """
        if patience <= 0:
            raise ValueError(f"patience must be positive, got {patience}")
        if mode not in ["min", "max"]:
            raise ValueError(f"mode must be 'min' or 'max', got '{mode}'")

        self.patience = patience
        self.monitor = monitor
        self.mode = mode
        self.min_delta = min_delta
        self.verbose = verbose

        # Primary state tracking (canonical attributes)
        self.wait = 0
        self.best_value: Optional[float] = None
        self.best_epoch = 0
        self.stopped_epoch = 0
        # Backward-compatible aliases: legacy code using check_metric() read
        # best_metric / patience_counter / _should_stop_flag directly.
        # These mirror wait / best_value / (wait >= patience) respectively.
        self.best_metric: Optional[float] = None  # alias for best_value
        self.patience_counter = 0  # alias for wait
        self._should_stop_flag = False  # set True when stopped

    def _is_improvement(self, value: float) -> bool:
        """Check if a value represents an improvement over the best value.

        Args:
            value: Current metric value

        Returns:
            True if value is an improvement, False otherwise
        """
        if self.best_value is None:
            return True

        if self.mode == "min":
            return value < (self.best_value - self.min_delta)
        # mode == "max"
        return value > (self.best_value + self.min_delta)

    def update(self, value: float, epoch: int = 0) -> bool:
        """Update early stopping state with a new metric value.

        Args:
            value: Current metric value
            epoch: Current epoch number (default: 0)

        Returns:
            True if this is an improvement, False otherwise
        """
        if self._is_improvement(value):
            self.best_value = value
            self.best_epoch = epoch
            self.wait = 0
            if self.verbose:
                logger.info(f"Epoch {epoch}: {self.monitor} improved to {value:.4f}")
            return True
        self.wait += 1
        if self.verbose:
            logger.info(
                f"Epoch {epoch}: {self.monitor} did not improve from {self.best_value:.4f} "
                f"(current: {value:.4f}, wait: {self.wait}/{self.patience})"
            )
        return False

    def should_stop(self, value: float, epoch: int = 0) -> bool:
        """Check if training should stop based on the current metric value.

        This method updates the internal state and returns whether training should stop.

        Args:
            value: Current metric value
            epoch: Current epoch number (default: 0)

        Returns:
            True if training should stop, False otherwise
        """
        self.update(value, epoch)

        if self.wait >= self.patience:
            self.stopped_epoch = epoch
            if self.verbose:
                logger.info(
                    f"Early stopping triggered at epoch {epoch}: "
                    f"no improvement in {self.monitor} for {self.patience} evaluations "
                    f"(best: {self.best_value:.4f} at epoch {self.best_epoch})"
                )
            return True

        return False

    def reset(self) -> None:
        """Reset early stopping state to initial values."""
        self.wait = 0
        self.best_value = None
        self.best_epoch = 0
        self.stopped_epoch = 0
        self.best_metric = None
        self.patience_counter = 0
        self._should_stop_flag = False

    def state_dict(self) -> dict[str, Any]:
        """Return early stopping state as a dictionary for serialization.

        Returns:
            Dictionary containing all state variables
        """
        return {
            "wait": self.wait,
            "best_value": self.best_value,
            "best_epoch": self.best_epoch,
            "stopped_epoch": self.stopped_epoch,
            "patience": self.patience,
            "monitor": self.monitor,
            "mode": self.mode,
            "min_delta": self.min_delta,
            "verbose": self.verbose,
        }

    def load_state_dict(self, state: dict[str, Any]) -> None:
        """Load early stopping state from a dictionary.

        Args:
            state: Dictionary containing state variables
        """
        self.wait = state.get("wait", 0)
        self.best_value = state.get("best_value")
        self.best_epoch = state.get("best_epoch", 0)
        self.stopped_epoch = state.get("stopped_epoch", 0)
        self.patience = state.get("patience", self.patience)
        self.monitor = state.get("monitor", self.monitor)
        self.mode = state.get("mode", self.mode)
        self.min_delta = state.get("min_delta", self.min_delta)
        if "verbose" in state:
            self.verbose = state["verbose"]

    def check_metric(self, metrics: dict[str, float]) -> bool:
        """Check if training should stop based on metric (backward compatibility).

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
            self.best_value = current_metric
            return False

        # Check if improved
        improved = False
        if self.mode == "min":
            improved = current_metric < (self.best_metric - self.min_delta)
        else:  # max
            improved = current_metric > (self.best_metric + self.min_delta)

        if improved:
            self.best_metric = current_metric
            self.best_value = current_metric
            self.patience_counter = 0
            self.wait = 0
        else:
            self.patience_counter += 1
            self.wait += 1

        if self.patience_counter >= self.patience:
            self._should_stop_flag = True
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
                early_stopping_patience=config.patience,
                early_stopping_threshold=config.threshold,
            )
            self.is_hf_callback = True
        except ImportError as e:
            type(e).__name__
            logger.debug("ImportError: <ERROR_TYPE>")
            logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
            logger.warning("transformers not available, using custom implementation")
            self.callback = self  # type: ignore[assignment]
            self.is_hf_callback = False
            self.best_metric = None
            self.patience_counter = 0

    def __getattr__(self, name: str):
        """Delegate to HF callback if available."""
        if self.is_hf_callback:
            return getattr(self.callback, name)
        raise AttributeError(f"'{type(self).__name__}' has no attribute '{name}'")


def inject_early_stopping(
    callbacks: list[Any],
    config: Optional[EarlyStoppingConfig] = None,
    force: bool = False,
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
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
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
    return inject_early_stopping(callbacks, config=config)


def create_early_stopping_from_config(
    config: EarlyStoppingConfig,
) -> Optional[EarlyStopping]:
    """Create EarlyStopping instance from configuration.

    Args:
        config: EarlyStoppingConfig instance

    Returns:
        EarlyStopping instance if enabled, None otherwise
    """
    if not getattr(config, "enabled", True):
        return None

    return EarlyStopping(
        patience=getattr(config, "patience", 3),
        monitor=getattr(config, "monitor", getattr(config, "metric", "val_loss")),
        mode=getattr(config, "mode", "min"),
    )


# Alias for backward compatibility
EarlyStoppingCallback = CodexEarlyStoppingCallback

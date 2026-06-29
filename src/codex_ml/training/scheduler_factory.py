"""Learning rate scheduler factory for flexible scheduler selection.

from __future__ import annotations

This module provides a factory function to create various learning rate
schedulers with configuration support.

Example usage:
    ```python
    from codex_ml.training.scheduler_factory import create_scheduler

    scheduler = create_scheduler(
        optimizer=optimizer,
        scheduler_type='cosine',
        num_training_steps=1000,
        num_warmup_steps=100
    )

    for batch in dataloader:
        loss = train_step(batch)
        optimizer.step()
        scheduler.step()
    ```
"""

import logging

logger = logging.getLogger(__name__)

import math
from typing import Any, Literal

LOGGER = logging.getLogger(__name__)

# Type alias for scheduler types
SchedulerType = Literal[
    "constant",
    "constant_with_warmup",
    "linear",
    "cosine",
    "cosine_with_restarts",
    "polynomial",
    "inverse_sqrt",
]


def create_scheduler(
    optimizer: Any,
    scheduler_type: SchedulerType = "linear",
    num_training_steps: int | None = None,
    num_warmup_steps: int = 0,
    num_cycles: float = 0.5,
    lr_end: float = 0.0,
    power: float = 1.0,
    **kwargs: Any,
) -> Any:
    """Create a learning rate scheduler.

    This function creates various types of learning rate schedulers commonly
    used in deep learning training. It supports PyTorch native schedulers and
    HuggingFace Transformers schedulers.

    Args:
        optimizer: PyTorch optimizer to schedule
        scheduler_type: Type of scheduler to create. Options:
            - 'constant': Constant learning rate (no changes)
            - 'constant_with_warmup': Warmup then constant
            - 'linear': Linear decay with optional warmup
            - 'cosine': Cosine annealing with optional warmup
            - 'cosine_with_restarts': Cosine with restarts
            - 'polynomial': Polynomial decay
            - 'inverse_sqrt': Inverse square root decay
        num_training_steps: Total number of training steps
        num_warmup_steps: Number of warmup steps (default: 0)
        num_cycles: Number of cycles for cosine with restarts (default: 0.5)
        lr_end: Final learning rate for linear/polynomial (default: 0.0)
        power: Power for polynomial decay (default: 1.0)
        **kwargs: Additional arguments passed to scheduler constructor

    Returns:
        Learning rate scheduler instance

    Raises:
        ValueError: If scheduler_type is not recognized
        ImportError: If required library is not available

    Example:
        ```python
        # Linear warmup with cosine decay
        scheduler = create_scheduler(
            optimizer,
            scheduler_type='cosine',
            num_training_steps=10000,
            num_warmup_steps=500
        )

        # Constant learning rate
        scheduler = create_scheduler(
            optimizer,
            scheduler_type='constant'
        )
        ```
    """
    # Try HuggingFace transformers schedulers first (more comprehensive)
    try:
        from transformers import get_scheduler as get_transformers_scheduler

        # Map our scheduler types to transformers names
        scheduler_name_map = {
            "constant": "constant",
            "constant_with_warmup": "constant_with_warmup",
            "linear": "linear",
            "cosine": "cosine",
            "cosine_with_restarts": "cosine_with_restarts",
            "polynomial": "polynomial",
            "inverse_sqrt": "inverse_sqrt",
        }

        if scheduler_type not in scheduler_name_map:
            raise ValueError(
                f"Unknown scheduler type: {scheduler_type}. "
                f"Available types: {list(scheduler_name_map.keys())}"
            )

        transformers_name = scheduler_name_map[scheduler_type]

        # Build scheduler kwargs
        scheduler_kwargs = {
            "num_warmup_steps": num_warmup_steps,
        }

        # Add num_training_steps for schedulers that need it
        if scheduler_type != "constant":
            if num_training_steps is None:
                raise ValueError(
                    f"num_training_steps is required for scheduler type '{scheduler_type}'"
                )
            scheduler_kwargs["num_training_steps"] = num_training_steps

        # Add scheduler-specific arguments
        if scheduler_type == "cosine_with_restarts":
            scheduler_kwargs["num_cycles"] = num_cycles  # type: ignore[assignment]
        elif scheduler_type == "polynomial":
            scheduler_kwargs["lr_end"] = lr_end  # type: ignore[assignment]
            scheduler_kwargs["power"] = power  # type: ignore[assignment]

        # Merge with any additional kwargs
        scheduler_kwargs.update(kwargs)

        LOGGER.info(
            f"Creating transformers scheduler: type={transformers_name}, "
            f"warmup_steps={num_warmup_steps}, "
            f"training_steps={num_training_steps}"
        )

        return get_transformers_scheduler(
            name=transformers_name,
            optimizer=optimizer,
            **scheduler_kwargs,
        )

    except (ImportError, TypeError) as e:
        type(e).__name__
        logger.debug("ImportError or TypeError: <ERROR_TYPE>")
        logger.debug("transformers error: <ERROR_TYPE>")
        LOGGER.warning(
            "transformers not available or TypeError, falling back to PyTorch schedulers"
        )
        # Fall back to PyTorch native schedulers
        return _create_pytorch_scheduler(
            optimizer=optimizer,
            scheduler_type=scheduler_type,
            num_training_steps=num_training_steps,
            num_warmup_steps=num_warmup_steps,
            num_cycles=num_cycles,
            lr_end=lr_end,
            power=power,
            **kwargs,
        )


def _create_pytorch_scheduler(
    optimizer: Any,
    scheduler_type: SchedulerType,
    num_training_steps: int | None,
    num_warmup_steps: int,
    num_cycles: float,
    lr_end: float,
    power: float,
    **kwargs: Any,
) -> Any:
    """Create scheduler using PyTorch native schedulers.

    This is a fallback when transformers is not available.
    """
    try:
        from torch.optim import lr_scheduler
    except ImportError as e:
        type(e).__name__
        logger.debug("ImportError: <ERROR_TYPE>")
        raise ImportError(
            "PyTorch is required for scheduler creation. Install with: pip install torch"
        ) from e

    def _make_lambda_lr(lr_lambda):
        try:
            return lr_scheduler.LambdaLR(optimizer, lr_lambda=lr_lambda)
        except TypeError as exc:
            raise ImportError(
                f"Scheduler creation requires a torch.optim.Optimizer: {exc}"
            ) from exc

    if scheduler_type == "constant":
        # Constant LR (identity scheduler)
        return _make_lambda_lr(lambda step: 1.0)

    if scheduler_type == "constant_with_warmup":

        def lr_lambda(step):
            if step < num_warmup_steps:
                return float(step) / float(max(1, num_warmup_steps))
            return 1.0

        return _make_lambda_lr(lr_lambda)

    if scheduler_type == "linear":
        if num_training_steps is None:
            raise ValueError("num_training_steps required for linear scheduler")

        def lr_lambda(step):
            if step < num_warmup_steps:
                return float(step) / float(max(1, num_warmup_steps))
            return max(
                0.0,
                float(num_training_steps - step)
                / float(max(1, num_training_steps - num_warmup_steps)),
            )

        return _make_lambda_lr(lr_lambda)

    if scheduler_type == "cosine":
        if num_training_steps is None:
            raise ValueError("num_training_steps required for cosine scheduler")

        def lr_lambda(step):
            if step < num_warmup_steps:
                return float(step) / float(max(1, num_warmup_steps))
            progress = float(step - num_warmup_steps) / float(
                max(1, num_training_steps - num_warmup_steps)
            )
            return max(0.0, 0.5 * (1.0 + math.cos(math.pi * progress)))

        return _make_lambda_lr(lr_lambda)

    if scheduler_type == "cosine_with_restarts":
        if num_training_steps is None:
            raise ValueError("num_training_steps required for cosine_with_restarts")

        return lr_scheduler.CosineAnnealingWarmRestarts(
            optimizer,
            T_0=num_training_steps // int(num_cycles),
            T_mult=1,
            **kwargs,
        )

    if scheduler_type == "polynomial":
        if num_training_steps is None:
            raise ValueError("num_training_steps required for polynomial scheduler")

        return lr_scheduler.PolynomialLR(
            optimizer,
            total_iters=num_training_steps,
            power=power,
            **kwargs,
        )

    if scheduler_type == "inverse_sqrt":

        def lr_lambda(step):
            if step < num_warmup_steps:
                return float(step) / float(max(1, num_warmup_steps))
            return math.sqrt(num_warmup_steps / max(step, 1))

        return _make_lambda_lr(lr_lambda)

    raise ValueError(
        f"Unknown scheduler type: {scheduler_type}. "
        f"Available types: constant, constant_with_warmup, linear, "
        f"cosine, cosine_with_restarts, polynomial, inverse_sqrt"
    )


def get_available_schedulers() -> list[str]:
    """Get list of available scheduler types.

    Returns:
        List of scheduler type names
    """
    return [
        "constant",
        "constant_with_warmup",
        "linear",
        "cosine",
        "cosine_with_restarts",
        "polynomial",
        "inverse_sqrt",
    ]


def calculate_num_training_steps(
    num_epochs: int,
    dataset_size: int,
    batch_size: int,
    gradient_accumulation_steps: int = 1,
) -> int:
    """Calculate total number of training steps.

    Args:
        num_epochs: Number of training epochs
        dataset_size: Size of training dataset
        batch_size: Batch size
        gradient_accumulation_steps: Gradient accumulation steps

    Returns:
        Total number of optimization steps

    Example:
        ```python
        steps = calculate_num_training_steps(
            num_epochs=3,
            dataset_size=10000,
            batch_size=32,
            gradient_accumulation_steps=4
        )
        # steps = 3 * (10000 / (32 * 4)) = 234
        ```
    """
    effective_batch_size = batch_size * gradient_accumulation_steps
    steps_per_epoch = math.ceil(dataset_size / effective_batch_size)
    total_steps = num_epochs * steps_per_epoch

    LOGGER.debug(
        f"Calculated training steps: {total_steps} "
        f"(epochs={num_epochs}, dataset={dataset_size}, "
        f"batch={batch_size}, grad_accum={gradient_accumulation_steps})"
    )

    return total_steps

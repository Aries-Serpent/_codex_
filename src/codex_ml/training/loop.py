"""Reference minimal training loop skeleton (CPU-safe, import-safe).

This module provides a lightweight training loop abstraction that avoids
heavy dependencies at import time. The model is expected to implement
a `.step(batch, state)` method that returns metrics.

Example usage::

    from codex_ml.training.loop import train_epoch

    class SimpleModel:
        def step(self, batch, state):
            # Process batch and return metrics
            return {"loss": 0.5, "accuracy": 0.9}

    model = SimpleModel()
    dataloader = [{"input": i} for i in range(10)]

    results = train_epoch(
        model=model,
        dataloader=dataloader,
        callbacks=None,
        state={"epoch": 1},
    )

    print(f"Epoch complete. Metrics: {results}")

The loop does not import torch/transformers at module level to remain
import-safe and usable in minimal environments.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable

from codex_ml.interfaces.contracts import (
    TrainingContractError,
    validate_training_model,
)


def train_epoch(
    model: Any,
    dataloader: Iterable[Any],
    callbacks: list[Callable] | None = None,
    state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Execute one training epoch over the provided dataloader.

    The model must implement a `.step(batch, state)` method that:
    - Accepts a batch from the dataloader and the current state dict
    - Performs forward pass, loss computation, and backward pass internally
    - Returns a dict of metrics for the step

    Args:
        model: Model object with a `.step(batch, state)` method
        dataloader: Iterable yielding batches (dicts, tuples, or tensors)
        callbacks: Optional list of callback functions called after each step.
                   Each callback receives (step_idx, batch, metrics, state).
        state: Optional state dict (e.g., {"epoch": 1, "global_step": 0})
               that is passed to model.step() and updated during training.

    Returns:
        Dictionary with aggregated metrics and final state.

    Example::

        class MyModel:
            def step(self, batch, state):
                # Your training logic here
                loss = compute_loss(batch)
                loss.backward()
                optimizer.step()
                return {"loss": loss.item()}

        results = train_epoch(
            model=MyModel(),
            dataloader=my_dataloader,
            state={"epoch": 1},
        )
    """
    if state is None:
        state = {}

    if callbacks is None:
        callbacks = []

    validate_training_model(model)

    metrics_accumulator: dict[str, list[float]] = {}

    for step_idx, batch in enumerate(dataloader):
        # Call model's step method
        step_metrics = model.step(batch, state)
        if not isinstance(step_metrics, dict):
            raise TrainingContractError("Model.step must return a mapping of metrics")

        # Accumulate metrics
        for key, value in step_metrics.items():
            if not isinstance(key, str):
                raise TrainingContractError("Metric keys must be strings")
            if key not in metrics_accumulator:
                metrics_accumulator[key] = []
            # Handle numeric values
            if isinstance(value, (int, float)):
                metrics_accumulator[key].append(float(value))
            elif hasattr(value, "item"):  # torch tensor-like
                metrics_accumulator[key].append(float(value.item()))
            else:
                raise TrainingContractError("Metric values must be numeric")

        # Update state
        state["step"] = step_idx

        # Call callbacks
        for callback in callbacks:
            callback(step_idx, batch, step_metrics, state)

    # Compute averages
    aggregated = {}
    for key, values in metrics_accumulator.items():
        if values:
            aggregated[f"{key}_mean"] = sum(values) / len(values)
            aggregated[f"{key}_last"] = values[-1]

    aggregated["num_steps"] = len(next(iter(metrics_accumulator.values()), []))
    aggregated["state"] = state

    return aggregated


def save_epoch_checkpoint(
    out_dir: str,
    state: dict[str, Any],
    meta: dict[str, Any],
) -> str:
    """Save a checkpoint after an epoch using the checkpoint_core module.

    This is a thin wrapper around checkpoint_core.save_checkpoint that
    provides a training-focused interface.

    Args:
        out_dir: Directory path to save the checkpoint
        state: State dictionary containing model weights, optimizer state, etc.
        meta: Metadata dictionary with epoch, step, metrics, etc.

    Returns:
        Path to the saved checkpoint directory

    Example::

        save_epoch_checkpoint(
            out_dir="checkpoints/epoch_5",
            state={"model": model.state_dict(), "optimizer": optimizer.state_dict()},
            meta={"epoch": 5, "loss": 0.25, "timestamp": "2025-11-11"},
        )

    Note:
        This function requires PyTorch to be installed. If torch is not
        available, it will raise a RuntimeError from checkpoint_core.
    """
    # Import checkpoint_core here to avoid heavy imports at module level
    from codex_ml.checkpointing.checkpoint_core import save_checkpoint

    return save_checkpoint(
        out_dir=out_dir,
        state=state,
        meta=meta,
        keep_last_k=5,  # Default retention policy
    )


__all__ = ["train_epoch", "save_epoch_checkpoint"]

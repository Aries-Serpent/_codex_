"""Minimal training loop scaffolding for _codex_.

This is intentionally tiny: a placeholder API that can be extended to integrate
with real optimizers, schedulers, and gradient accumulation.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)
from collections.abc import Iterable
from typing import Any

from codex_ml.interfaces.contracts import TrainingContractError
from codex_ml.logging.metrics import MetricLogger


def train_one_step(loss_value: float) -> float:
    """Return a dummy updated loss for smoke tests."""
    return loss_value * 0.9


def train_epoch(
    model: Any, dataloader: Iterable[dict[str, Any]], state: dict[str, Any]
) -> dict[str, float]:
    if not dataloader:
        raise TrainingContractError("Dataloader must not be empty")
    losses = []
    for batch in dataloader:
        if "input_ids" not in batch:
            raise TrainingContractError("input_ids missing from batch")
        try:
            result = model.step(batch, state)
        except Exception as exc:  # pragma: no cover - surfaced in tests
            raise TrainingContractError(f"Model.step failed to process batch: {exc}") from exc
        if "loss" not in result:
            raise TrainingContractError("Model step did not return loss")
        losses.append(float(result["loss"]))
    return {
        "loss_mean": sum(losses) / len(losses),
        "loss_last": losses[-1],
        "num_batches": len(losses),
    }


def run_minimal_training(config: dict[str, Any], max_steps: int, run_dir: str) -> dict[str, float]:
    """
    Very small training routine used by the minimal CLI.

    The function decays a scalar loss and logs it to metrics.ndjson for
    downstream indexing. It intentionally avoids heavyweight dependencies.

    Parameters
    ----------
    config : dict[str, Any]
        Configuration dictionary. Expected keys:
        - 'training.base_loss' (float, optional): Initial loss value (default: 10.0)
        - 'training.decay' (float, optional): Loss decay factor per step (default: 0.9)
    max_steps : int
        Number of training steps to run (minimum 1).
    run_dir : str
        Directory path where metrics.ndjson will be written.

    Returns
    -------
    dict[str, float]
        Dictionary containing:
        - 'loss_final': The final loss value after training.
    """

    run_path = Path(run_dir)
    run_path.mkdir(parents=True, exist_ok=True)
    loss = float(config.get("training", {}).get("base_loss", 10.0))
    decay = float(config.get("training", {}).get("decay", 0.9))
    max_steps = max(1, int(max_steps))
    metrics_path = run_path / "metrics.ndjson"
    with MetricLogger(metrics_path) as logger:
        for step in range(max_steps):
            logger.log(step=step, loss=loss)
            loss = train_one_step(loss) * decay
    return {"loss_final": loss}


def run_minimal_evaluation(
    config: dict[str, Any], checkpoint: str, run_dir: str
) -> dict[str, float]:
    """Tiny evaluation stub that logs a deterministic score."""

    run_path = Path(run_dir)
    run_path.mkdir(parents=True, exist_ok=True)
    base_score = float(config.get("eval", {}).get("base_score", 0.5))
    checkpoint_hint = 0.1 if checkpoint else 0.0
    score = min(1.0, base_score + checkpoint_hint)
    metrics_path = run_path / "metrics.ndjson"
    with MetricLogger(metrics_path) as logger:
        logger.log(step=0, score=score)
    return {"score": score}

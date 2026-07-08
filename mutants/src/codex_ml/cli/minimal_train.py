"""Minimal training + evaluation CLI for _codex_ scaffolding.

This module ties together:
- config loading
- tokenization
- simple dataset
- training loop
- evaluator
- tracking stub

The goal is to provide a small, end-to-end path that can be invoked from
tests or from the examples directory without external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from codex.logging.structured_logger import logger
from codex_ml.config import load as cfg_load
from codex_ml.data.simple_dataset import Sample, SimpleDataset
from codex_ml.eval import evaluator
from codex_ml.modeling import model_factory
from codex_ml.tracking import mlflow_wrapper
from codex_ml.training import loop as training_loop


@dataclass
class MinimalRunResult:
    loss_before: float
    loss_after: float
    score: float


def _build_dummy_samples() -> list[Sample]:
    return [
        Sample(text="hello codex", label=1),
        Sample(text="goodbye codex", label=0),
        Sample(text="codex ml", label=1),
    ]


def run_minimal(experiment_name: Optional[str] = None) -> MinimalRunResult:
    """Run a minimal training+evaluation loop using in-repo scaffolding only."""
    config = cfg_load.load_config(experiment_name=experiment_name)

    training_cfg = config.get("training", {})
    epochs = int(training_cfg.get("epochs", 1))
    base_loss = float(training_cfg.get("base_loss", 10.0))

    samples = _build_dummy_samples()
    ds = SimpleDataset(samples, seed=int(training_cfg.get("seed", 0)))
    encoded = ds.encoded()

    model = model_factory.build_model(config.get("model", {}))

    loss = base_loss
    for _ in range(max(epochs, 1)):
        loss = training_loop.train_one_step(loss)

    predictions = [1 if sum(s.tokens) % 2 == 0 else 0 for s in encoded]
    targets = [s.label for s in encoded]
    score = evaluator.evaluate_constant(predictions, targets)

    mlflow_wrapper.log_metric("minimal_loss_before", base_loss)
    mlflow_wrapper.log_metric("minimal_loss_after", loss)
    mlflow_wrapper.log_metric("minimal_score", float(score))

    _ = model
    return MinimalRunResult(loss_before=base_loss, loss_after=loss, score=score)


def main() -> None:
    result = run_minimal(experiment_name=None)
    logger.info("loss_before:", result.loss_before)
    logger.info("loss_after:", result.loss_after)
    logger.info("score:", result.score)


if __name__ == "__main__":  # pragma: no cover
    main()

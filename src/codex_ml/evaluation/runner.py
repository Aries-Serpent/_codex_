"""
Unified Evaluation Runner (WP-C: Evaluation Standardization)

This module provides a standardized evaluation interface with pluggable metric adapters.
Integrates with the tracking system (MLflow/NDJSON) for centralized result logging.

Key Features:
- Unified EvaluationRunner interface
- Pluggable metric adapters (accuracy, BLEU, ROUGE, perplexity, latency)
- Automatic tracking writer integration
- Offline-first with JSON artifact generation
- Supports custom metrics via callable interface

Usage:
    from codex_ml.evaluation.runner import EvaluationRunner
    from codex_ml.evaluation.metrics import AccuracyMetric, RougeMetric

    runner = EvaluationRunner(
        model=model,
        dataset=validation_dataset,
        metrics=[AccuracyMetric(), RougeMetric(['rouge1', 'rougeL'])],
        tracking_writer=tracking_writer,  # Optional
        output_dir="artifacts/evaluation"
    )

    results = runner.run()
    # Results: {'accuracy': 0.85, 'rouge1': 0.72, 'rougeL': 0.68, ...}
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import json  # noqa: E402
import time  # noqa: E402
from abc import ABC  # noqa: E402
from collections.abc import Callable  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any, Optional  # noqa: E402

from codex.logging.structured_logger import logger

try:
    import torch

    DataLoader = torch.utils.data.DataLoader
except ImportError as e:
    error_type = type(e).__name__
    logger.debug("ImportError: <ERROR_TYPE>")
    logger.warning("ImportError: <ERROR_TYPE>", exc_info=True)
    torch = None  # type: ignore[assignment]
    DataLoader = None


@dataclass
class EvaluationConfig:
    """Configuration for evaluation runs."""

    batch_size: int = 32
    max_samples: Optional[int] = None
    device: str = "cpu"
    num_workers: int = 0
    output_dir: str = "artifacts/evaluation"
    save_predictions: bool = False
    log_interval: int = 10
    # Additional fields expected by tests
    max_batches: Optional[int] = None
    seed: Optional[int] = None
    metrics: Optional[Any] = None
    system_metrics: bool = False


class MetricAdapter(ABC):
    """
    Base class for metric adapters.

    Subclasses should implement:
    - compute(predictions, references) -> dict[str, float]
    """

    def __init__(self, name: str):
        self.name = name
        self._predictions: list[Any] = []
        self._references: list[Any] = []

    def add_batch(self, predictions: Any, references: Any) -> None:
        """Accumulate batch results."""
        self._predictions.extend(predictions if isinstance(predictions, list) else [predictions])
        self._references.extend(references if isinstance(references, list) else [references])

    def compute(self) -> dict[str, float]:
        """Compute final metrics from accumulated results."""
        raise NotImplementedError("Subclasses must implement compute()")

    def reset(self) -> None:
        """Reset accumulated results."""
        self._predictions.clear()
        self._references.clear()


class EvaluationRunner:
    """
    Unified evaluation runner with metric adapters and tracking integration.

    This runner provides:
    - Standardized evaluation loop
    - Metric adapter interface
    - Tracking writer integration (MLflow/NDJSON)
    - Artifact generation (summary JSON, predictions)
    - Latency/throughput measurement

    Args:
        model: Model to evaluate (should have forward() or predict() method)
        dataset: Evaluation dataset or DataLoader
        metrics: list of MetricAdapter instances or callables
        config: EvaluationConfig instance
        tracking_writer: Optional tracking writer (MLflowWriter/NdjsonWriter)
        output_dir: Directory for artifacts (default: artifacts/evaluation)
    """

    def __init__(
        self,
        model: Any,
        dataset: Any | DataLoader,  # type: ignore[valid-type]
        metrics: list[MetricAdapter | Callable],
        config: Optional[EvaluationConfig] = None,
        tracking_writer: Optional[Any] = None,
        output_dir: Optional[str] = None,
    ):
        self.model = model
        self.dataset = dataset
        self.metrics = [self._wrap_metric(m) for m in metrics]
        self.config = config or EvaluationConfig()
        self.tracking_writer = tracking_writer

        # Override output_dir if provided
        if output_dir:
            self.config.output_dir = output_dir

        self.output_path = Path(self.config.output_dir)
        self.output_path.mkdir(parents=True, exist_ok=True)

        # Results storage
        self.results: dict[str, Any] = {}
        self.predictions: list[Any] = []

    def _wrap_metric(self, metric: MetricAdapter | Callable) -> MetricAdapter:
        """Wrap callable metrics in MetricAdapter interface."""
        if isinstance(metric, MetricAdapter):
            return metric

        # Wrap callable in adapter
        class CallableMetricAdapter(MetricAdapter):
            def __init__(self, fn: Callable, name: str):
                super().__init__(name)
                self.fn = fn

            def compute(self) -> dict[str, float]:
                try:
                    result = self.fn(self._predictions, self._references)
                    if isinstance(result, dict):
                        return result
                    return {self.name: float(result)}
                except (ValueError, TypeError, RuntimeError) as e:
                    type(e).__name__
                    logger.debug("Exception: <ERROR_TYPE>")
                    logger.debug("Exception caught, returning", exc_info=True)
                    return {f"{self.name}_error": str(e)}  # type: ignore[dict-item]

        name = getattr(metric, "__name__", "custom_metric")
        return CallableMetricAdapter(metric, name)

    def run(self) -> dict[str, Any]:
        """
        Execute evaluation run.

        Returns:
            Dictionary with evaluation results:
            {
                'metrics': {'accuracy': 0.85, 'rouge1': 0.72, ...},
                'latency_ms': 150.5,
                'throughput_samples_per_sec': 45.2,
                'num_samples': 1000,
                'timestamp': '2025-12-07T22:30:00Z'
            }
        """
        logger.info(f"Starting evaluation run with {len(self.metrics)} metrics...")

        # Setup
        if torch and hasattr(self.model, "eval"):
            self.model.eval()

        dataloader = self._get_dataloader()
        start_time = time.time()
        total_samples = 0

        # Reset metrics
        for metric in self.metrics:
            metric.reset()

        # Evaluation loop
        grad_context = (
            torch.no_grad() if torch is not None and hasattr(torch, "no_grad") else _nullcontext()
        )
        with grad_context:
            for batch_idx, batch in enumerate(dataloader):
                if self.config.max_samples and total_samples >= self.config.max_samples:
                    break

                # Extract inputs and targets
                if isinstance(batch, (tuple, list)):
                    inputs, targets = batch[0], batch[1]
                elif isinstance(batch, dict):
                    inputs = batch.get("input_ids", batch.get("inputs"))
                    targets = batch.get("labels", batch.get("targets"))
                else:
                    inputs, targets = batch, None

                # Move to device
                if torch and self.config.device != "cpu":
                    if hasattr(inputs, "to"):
                        inputs = inputs.to(self.config.device)
                    if targets and hasattr(targets, "to"):
                        targets = targets.to(self.config.device)

                # Forward pass
                if hasattr(self.model, "predict"):
                    predictions = self.model.predict(inputs)
                elif hasattr(self.model, "forward"):
                    predictions = self.model.forward(inputs)
                else:
                    call_fn = getattr(self.model, "__call__", None)
                    if not callable(call_fn):
                        raise ValueError(
                            f"Model {type(self.model)} has no predict/forward method and is not callable"  # noqa: E501
                        )
                    try:
                        predictions = call_fn(inputs)
                    except TypeError as e:
                        raise ValueError(
                            f"Model {type(self.model)}.__call__(inputs) raised TypeError: {e}"
                        ) from e

                # Accumulate for metrics
                batch_size = len(inputs) if hasattr(inputs, "__len__") else 1
                total_samples += batch_size

                for metric in self.metrics:
                    metric.add_batch(predictions, targets)

                # Optionally save predictions
                if self.config.save_predictions:
                    self.predictions.append(
                        {
                            "batch_idx": batch_idx,
                            "predictions": self._detach(predictions),
                            "targets": self._detach(targets),
                        }
                    )

                # Log progress
                if (batch_idx + 1) % self.config.log_interval == 0:
                    logger.info(f"  Processed {total_samples} samples...")

        elapsed_time = time.time() - start_time

        # Compute metrics
        metric_results = {}
        for metric in self.metrics:
            try:
                computed = metric.compute()
                metric_results.update(computed)
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.info(f"Warning: Metric {metric.name} failed: <ERROR_TYPE>")
                metric_results[f"{metric.name}_error"] = str(e)  # type: ignore[assignment]

        # Build results
        self.results = {
            "metrics": metric_results,
            "latency_ms": elapsed_time * 1000,
            "throughput_samples_per_sec": total_samples / elapsed_time if elapsed_time > 0 else 0,
            "num_samples": total_samples,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "config": {
                "batch_size": self.config.batch_size,
                "device": self.config.device,
                "max_samples": self.config.max_samples,
            },
        }

        # Save artifacts
        self._save_summary()
        if self.config.save_predictions:
            self._save_predictions()

        # Log to tracking writer
        if self.tracking_writer:
            self._log_to_tracking()

        logger.info(f"Evaluation complete: {total_samples} samples in {elapsed_time:.2f}s")
        logger.info(f"Results: {metric_results}")

        return self.results

    def _get_dataloader(self) -> Any:
        """Get or create DataLoader from dataset."""
        if DataLoader is not None and isinstance(self.dataset, DataLoader):
            return self.dataset

        # If torch available, create DataLoader
        if torch is not None and DataLoader is not None:
            return DataLoader(
                self.dataset,
                batch_size=self.config.batch_size,
                shuffle=False,
                num_workers=self.config.num_workers,
            )

        # Fallback: assume dataset is iterable
        return self.dataset

    def _detach(self, tensor: Any) -> Any:
        """Detach tensor from computation graph and move to CPU."""
        if torch and isinstance(tensor, torch.Tensor):
            return tensor.detach().cpu().tolist()
        return tensor

    def _save_summary(self) -> None:
        """Save evaluation summary to JSON."""
        summary_path = self.output_path / "evaluation_summary.json"
        with open(summary_path, "w") as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Saved summary to {summary_path}")

    def _save_predictions(self) -> None:
        """Save predictions to JSON."""
        if not self.predictions:
            return

        predictions_path = self.output_path / "predictions.json"
        with open(predictions_path, "w") as f:
            json.dump(self.predictions, f, indent=2)
        logger.info(f"Saved predictions to {predictions_path}")

    def _log_to_tracking(self) -> None:
        """Log results to tracking writer (MLflow/NDJSON)."""
        try:
            # Log metrics
            for name, value in self.results["metrics"].items():
                if isinstance(value, (int, float)):
                    self.tracking_writer.log_metric(name, value)  # type: ignore[union-attr]

            # Log performance metrics
            self.tracking_writer.log_metric("latency_ms", self.results["latency_ms"])  # type: ignore[union-attr]
            self.tracking_writer.log_metric(  # type: ignore[union-attr]
                "throughput", self.results["throughput_samples_per_sec"]
            )

            # Log artifact
            summary_path = str(self.output_path / "evaluation_summary.json")
            if hasattr(self.tracking_writer, "log_artifact"):
                self.tracking_writer.log_artifact(summary_path)  # type: ignore[union-attr]

            logger.info("Logged results to tracking writer")
        except (IOError, OSError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.info("Warning: Failed to log to tracking writer: <ERROR_TYPE>")


class _nullcontext:
    """Fallback context manager when torch.no_grad() not available."""

    def __enter__(self) -> "_nullcontext":
        return self

    def __exit__(self, *args) -> None:
        pass

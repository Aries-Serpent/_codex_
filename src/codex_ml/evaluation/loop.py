"""
CPU-safe evaluation loop with pluggable metrics and logging.

Follows the specification from reports/specs/_codex__EvalLoop_and_CLI_Spec.md
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Optional, Protocol

__all__ = ["Criterion", "Logger", "EvaluationConfig", "EvaluationResult", "evaluate_epoch", "run_evaluation"]

LOGGER = logging.getLogger(__name__)


class Criterion(Protocol):
    """Protocol for loss computation."""
    
    def __call__(self, outputs, targets) -> "torch.Tensor":
        """Compute loss given outputs and targets."""
        ...


class Logger(Protocol):
    """Protocol for metrics logging."""
    
    def log(self, record: Dict[str, Any]) -> None:
        """Log a metrics record."""
        ...
    
    def close(self) -> None:
        """Close logger and flush buffers."""
        ...


@dataclass
class EvaluationConfig:
    """Configuration for evaluation run."""
    
    device: str = "cpu"
    max_batches: Optional[int] = None
    seed: Optional[int] = None
    metrics: Optional[Dict[str, Any]] = None
    system_metrics: bool = False


@dataclass
class EvaluationResult:
    """Result of evaluation run."""
    
    loss: float
    count: int
    metrics: Dict[str, float] = field(default_factory=dict)
    batches_processed: int = 0


def evaluate_epoch(
    model,
    dataloader: Iterable,
    criterion: Criterion,
    device: str = "cpu",
    metrics: Optional[Dict[str, Any]] = None,
    logger: Optional[Iterable[Logger]] = None,
    max_batches: Optional[int] = None,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Run evaluation over dataloader with torch.no_grad, model.eval().
    
    Args:
        model: PyTorch model to evaluate
        dataloader: Iterable of (inputs, targets) batches
        criterion: Loss function following Criterion protocol
        device: Device string (default "cpu")
        metrics: Optional dict mapping metric name -> callable(preds, targets) -> float
        logger: Optional iterable of Logger protocol objects
        max_batches: Optional limit on number of batches to process
        seed: Optional seed for dataloader generator (determinism)
    
    Returns:
        Summary dict with keys: "loss", "count", "metrics"
    
    Notes:
        - Sets model.eval() and wraps in torch.no_grad()
        - Lazy imports torch to avoid heavy dependency at module load
        - CPU-safe by default; no CUDA assumptions
        - Deterministic when seed is provided
    """
    # Lazy import torch (heavy dependency)
    try:
        import torch
    except ImportError as e:
        raise ImportError(
            "PyTorch is required for evaluation. "
            "Install with: pip install torch"
        ) from e
    
    # Set up determinism if seed provided
    if seed is not None:
        torch.manual_seed(seed)
        if hasattr(dataloader, "generator"):
            dataloader.generator = torch.Generator().manual_seed(seed)
    
    # Initialize loggers list
    loggers = list(logger) if logger else []
    
    # Set model to eval mode
    model.eval()
    model = model.to(device)
    
    # Initialize accumulators
    running_loss = 0.0
    total_count = 0
    batches_processed = 0
    
    # Metric accumulators
    metric_accumulators: Dict[str, list] = {}
    if metrics:
        for metric_name in metrics.keys():
            metric_accumulators[metric_name] = []
    
    try:
        with torch.no_grad():
            for batch_idx, batch in enumerate(dataloader):
                # Check max_batches limit
                if max_batches is not None and batch_idx >= max_batches:
                    LOGGER.info(f"Reached max_batches limit: {max_batches}")
                    break
                
                # Unpack batch
                if isinstance(batch, (tuple, list)) and len(batch) >= 2:
                    inputs, targets = batch[0], batch[1]
                else:
                    raise ValueError(f"Expected batch to be (inputs, targets), got {type(batch)}")
                
                # Move to device
                inputs = inputs.to(device)
                targets = targets.to(device)
                
                # Forward pass
                outputs = model(inputs)
                
                # Compute loss
                loss = criterion(outputs, targets)
                
                # Update accumulators
                batch_size = inputs.size(0)
                running_loss += loss.item() * batch_size
                total_count += batch_size
                batches_processed += 1
                
                # Compute batch metrics
                batch_metrics = {}
                if metrics:
                    # Get predictions (argmax for classification, direct for regression)
                    if outputs.dim() > 1 and outputs.size(-1) > 1:
                        _, predicted = outputs.max(-1)
                    else:
                        predicted = outputs
                    
                    for metric_name, metric_fn in metrics.items():
                        try:
                            metric_value = metric_fn(predicted, targets)
                            if isinstance(metric_value, torch.Tensor):
                                metric_value = metric_value.item()
                            batch_metrics[metric_name] = metric_value
                            metric_accumulators[metric_name].append(metric_value)
                        except Exception as e:
                            LOGGER.warning(f"Metric {metric_name} failed: {e}")
                
                # Log batch-level metrics (optional)
                if loggers:
                    batch_record = {
                        "batch": batch_idx,
                        "loss": loss.item(),
                        "batch_size": batch_size,
                        **batch_metrics,
                    }
                    for log in loggers:
                        try:
                            log.log(batch_record)
                        except Exception as e:
                            LOGGER.warning(f"Logger failed: {e}")
        
        # Compute epoch-level aggregates
        avg_loss = running_loss / total_count if total_count > 0 else 0.0
        
        aggregated_metrics = {}
        for metric_name, values in metric_accumulators.items():
            if values:
                aggregated_metrics[metric_name] = sum(values) / len(values)
        
        # Epoch summary
        summary = {
            "loss": avg_loss,
            "count": total_count,
            "metrics": aggregated_metrics,
            "batches_processed": batches_processed,
        }
        
        # Log epoch summary
        if loggers:
            epoch_record = {
                "epoch_summary": True,
                **summary,
            }
            for log in loggers:
                try:
                    log.log(epoch_record)
                except Exception as e:
                    LOGGER.warning(f"Logger failed on epoch summary: {e}")
        
        return summary
        
    finally:
        # Close all loggers
        for log in loggers:
            try:
                log.close()
            except Exception as e:
                LOGGER.warning(f"Logger close failed: {e}")


def run_evaluation(
    model,
    dataloader: Iterable,
    criterion: Criterion,
    config: Optional[EvaluationConfig] = None,
    logger: Optional[Iterable[Logger]] = None,
) -> EvaluationResult:
    """
    High-level evaluation runner with config object.
    
    Args:
        model: PyTorch model to evaluate
        dataloader: Iterable of (inputs, targets) batches
        criterion: Loss function
        config: Optional EvaluationConfig (uses defaults if None)
        logger: Optional iterable of Logger objects
    
    Returns:
        EvaluationResult with loss, count, metrics, batches_processed
    """
    if config is None:
        config = EvaluationConfig()
    
    summary = evaluate_epoch(
        model=model,
        dataloader=dataloader,
        criterion=criterion,
        device=config.device,
        metrics=config.metrics,
        logger=logger,
        max_batches=config.max_batches,
        seed=config.seed,
    )
    
    return EvaluationResult(
        loss=summary["loss"],
        count=summary["count"],
        metrics=summary.get("metrics", {}),
        batches_processed=summary.get("batches_processed", 0),
    )

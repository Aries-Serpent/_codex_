"""Extended trainer with evaluation, gradient accumulation, and checkpointing."""

from __future__ import annotations

import contextlib
import json
import logging
from collections.abc import Callable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:  # pragma: no cover - optional torch guard for import-time failures
    import torch
    from torch import nn
    from torch.cuda.amp import GradScaler, autocast
    from torch.utils.data import DataLoader
except Exception:  # pragma: no cover - propagate a consistent runtime error lazily
    torch = None  # type: ignore[assignment]
    nn = Any  # type: ignore[assignment]
    GradScaler = None  # type: ignore[assignment]
    autocast = None  # type: ignore[assignment]
    DataLoader = Any  # type: ignore[assignment]

if torch is not None:  # pragma: no cover - typing bridge
    TensorType = torch.Tensor
    OptimizerType = torch.optim.Optimizer
    DataLoaderType = DataLoader
else:  # pragma: no cover - fallback types
    TensorType = Any
    OptimizerType = Any
    DataLoaderType = Any

from ..logging_utils import (
    LoggingConfig,
    LoggingSession,
    log_metrics,
    setup_logging,
    shutdown_logging,
)
from .simple_trainer import SimpleTrainer

LOGGER = logging.getLogger(__name__)


MetricFn = Callable[[TensorType, TensorType], float]
LossFn = Callable[[TensorType, TensorType], TensorType]


@dataclass(slots=True, init=False)
class CheckpointConfig:
    directory: str
    best_k: int = 1
    monitor: str = "val_loss"
    mode: str = "min"  # either "min" or "max"
    save_optimizer: bool = True

    def __init__(
        self,
        directory: str,
        best_k: int = 1,
        monitor: str = "val_loss",
        mode: str | None = None,
        save_optimizer: bool = True,
        *,
        keep_best_k: int | None = None,
        maximize_metric: bool | None = None,
    ) -> None:
        effective_best_k = best_k
        if keep_best_k is not None:
            if best_k != 1 and keep_best_k != best_k:
                raise ValueError("Conflicting best_k/keep_best_k values; please specify only one")
            effective_best_k = keep_best_k

        resolved_mode = mode or "min"
        if maximize_metric is not None:
            desired_mode = "max" if maximize_metric else "min"
            if mode is not None and resolved_mode.lower() not in {"min", "max"}:
                raise ValueError("mode must be 'min' or 'max' when used with maximize_metric")
            if mode is not None and resolved_mode.lower() != desired_mode:
                raise ValueError("Conflicting mode/maximize_metric values; please specify only one")
            resolved_mode = desired_mode

        object.__setattr__(self, "directory", directory)
        object.__setattr__(self, "best_k", int(effective_best_k))
        object.__setattr__(self, "monitor", monitor)
        object.__setattr__(self, "mode", resolved_mode)
        object.__setattr__(self, "save_optimizer", bool(save_optimizer))
        self.__post_init__()

    def __post_init__(self) -> None:
        if self.best_k < 1:
            raise ValueError("best_k must be >= 1")
        normalised_mode = self.mode.lower()
        if normalised_mode not in {"min", "max"}:
            raise ValueError("mode must be 'min' or 'max'")
        object.__setattr__(self, "mode", normalised_mode)

    def path_for_epoch(self, epoch: int) -> Path:
        return Path(self.directory) / f"epoch_{epoch}.pt"


@dataclass(slots=True)
class TrainerConfig:
    epochs: int = 1
    gradient_accumulation_steps: int = 1
    mixed_precision: bool = False
    max_grad_norm: float | None = None
    log_every_n_steps: int = 0
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    checkpoint: CheckpointConfig | None = None


@dataclass(slots=True)
class TrainingState:
    epoch: int = 0
    global_step: int = 0
    best_metric: float | None = None


class Trainer:
    """Extended training loop wrapper that builds on :class:`SimpleTrainer`."""

    def __init__(
        self,
        model: nn.Module,
        optimizer: OptimizerType,
        train_loader: DataLoaderType,
        *,
        val_loader: DataLoaderType | None = None,
        loss_fn: LossFn | None = None,
        metric_fn: MetricFn | None = None,
        config: TrainerConfig | Mapping[str, Any] | None = None,
        trainer_config: TrainerConfig | Mapping[str, Any] | None = None,
        checkpoint_config: CheckpointConfig | Mapping[str, Any] | None = None,
        device: str | None = None,
    ) -> None:
        if torch is None or GradScaler is None or autocast is None:
            raise RuntimeError("torch is required for the extended trainer")
        if config is not None and trainer_config is not None:
            raise TypeError("Pass only one of 'config' or 'trainer_config'")

        resolved_config: TrainerConfig | None = None
        selected = trainer_config if trainer_config is not None else config
        if isinstance(selected, TrainerConfig):
            resolved_config = selected
        elif isinstance(selected, Mapping):
            resolved_config = TrainerConfig(**selected)
        elif selected is not None:
            raise TypeError(
                "config/trainer_config must be a TrainerConfig or mapping when provided"
            )

        cfg = resolved_config or TrainerConfig()

        if checkpoint_config is not None:
            if cfg.checkpoint is not None:
                raise TypeError(
                    "Pass checkpoint settings via either config.checkpoint or the"
                    " checkpoint_config argument, not both"
                )
            if isinstance(checkpoint_config, CheckpointConfig):
                cfg.checkpoint = checkpoint_config
            elif isinstance(checkpoint_config, Mapping):
                cfg.checkpoint = CheckpointConfig(**checkpoint_config)
            else:
                raise TypeError(
                    "checkpoint_config must be a CheckpointConfig or mapping when provided"
                )

        if cfg.gradient_accumulation_steps < 1:
            raise ValueError("gradient_accumulation_steps must be >= 1")
        self.simple = SimpleTrainer(model=model, optimizer=optimizer, device=device or "cpu")
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.loss_fn = loss_fn or self._default_loss
        self.metric_fn = metric_fn
        self.config = cfg
        self.scaler = GradScaler(enabled=cfg.mixed_precision)
        self.state = TrainingState()
        self.history: list[Mapping[str, float]] = []
        self._checkpoints: list[tuple[float, Path, Path]] = []
        self._logging_session: LoggingSession = setup_logging(cfg.logging)

        if cfg.checkpoint is not None:
            Path(cfg.checkpoint.directory).mkdir(parents=True, exist_ok=True)

    @property
    def device(self) -> str:
        return self.simple.device

    def _prepare_batch(
        self, batch: Sequence | Mapping[str, torch.Tensor]
    ) -> tuple[Any, torch.Tensor]:
        if isinstance(batch, Mapping):
            mapping = dict(batch)
            if "labels" not in mapping:
                raise ValueError("Batch mapping must include a 'labels' tensor")
            labels = mapping.pop("labels")
            labels = labels.to(self.device)
            inputs: MutableMapping[str, Any] = {}
            for key, value in mapping.items():
                inputs[key] = value.to(self.device) if hasattr(value, "to") else value
            return inputs, labels
        if isinstance(batch, Sequence) and len(batch) == 2:
            inputs, labels = batch
            if isinstance(inputs, Mapping):
                merged = dict(inputs)
                merged["labels"] = labels
                return self._prepare_batch(merged)
            if hasattr(inputs, "to"):
                inputs = inputs.to(self.device)
            if hasattr(labels, "to"):
                labels = labels.to(self.device)
            return inputs, labels
        raise TypeError("Unsupported batch type; expected mapping or (inputs, labels) tuple")

    def _forward(self, inputs: Any) -> torch.Tensor:
        if isinstance(inputs, Mapping):
            return self.simple.model(**inputs)  # type: ignore[arg-type]
        return self.simple.model(inputs)

    def _default_loss(self, outputs: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        logits = getattr(outputs, "logits", outputs)
        return torch.nn.functional.cross_entropy(logits, labels)

    def _compute_metrics(
        self,
        outputs: torch.Tensor,
        labels: torch.Tensor,
        *,
        include_loss: bool = True,
    ) -> MutableMapping[str, float]:
        metrics: MutableMapping[str, float] = {}
        if include_loss:
            loss = self.loss_fn(outputs, labels)
            metrics["val_loss"] = float(loss.detach().cpu().item())
        if self.metric_fn is not None:
            try:
                metrics["val_metric"] = float(self.metric_fn(outputs, labels))
            except Exception as exc:  # pragma: no cover - metric robustness guard
                LOGGER.debug("Metric function failed: %s", exc)
        return metrics

    def _should_replace(self, new_metric: float) -> bool:
        if self.config.checkpoint is None:
            return False
        if self.state.best_metric is None:
            return True
        mode = self.config.checkpoint.mode.lower()
        if mode not in {"min", "max"}:
            raise ValueError("checkpoint.mode must be 'min' or 'max'")
        if mode == "min":
            return new_metric < self.state.best_metric
        return new_metric > self.state.best_metric

    def _monitor_value(self, metrics: Mapping[str, float]) -> float | None:
        monitor_key = (
            self.config.checkpoint.monitor if self.config.checkpoint else None
        ) or "val_loss"
        return metrics.get(monitor_key)

    def _prune_checkpoints(self) -> None:
        cfg = self.config.checkpoint
        if cfg is None:
            return
        reverse = cfg.mode.lower() == "max"
        self._checkpoints.sort(key=lambda item: item[0], reverse=reverse)
        while len(self._checkpoints) > cfg.best_k:
            _, ckpt_path, meta_path = self._checkpoints.pop(-1)
            for path in (ckpt_path, meta_path):
                try:
                    path.unlink(missing_ok=True)
                except Exception as exc:  # pragma: no cover - retention guard
                    LOGGER.debug("Failed to remove checkpoint '%s': %s", path, exc)

    def _save_checkpoint(self, epoch: int, metrics: Mapping[str, float]) -> None:
        cfg = self.config.checkpoint
        if cfg is None:
            return
        monitor_value = self._monitor_value(metrics)
        if monitor_value is None:
            LOGGER.debug("Skipping checkpoint save; monitor '%s' missing", cfg.monitor)
            return

        checkpoint_path = cfg.path_for_epoch(epoch)
        metadata_path = checkpoint_path.with_suffix(".json")
        payload = {
            "epoch": epoch,
            "global_step": self.state.global_step,
            "metrics": dict(metrics),
            "monitor": monitor_value,
        }
        payload["has_optimizer_state"] = cfg.save_optimizer
        checkpoint: dict[str, Any] = {
            "model_state": self.simple.model.state_dict(),
            **payload,
        }
        if cfg.save_optimizer:
            checkpoint["optimizer_state"] = self.simple.optimizer.state_dict()
        try:
            torch.save(checkpoint, checkpoint_path)
            metadata_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            self._checkpoints.append((monitor_value, checkpoint_path, metadata_path))
            self._prune_checkpoints()
            if self._should_replace(monitor_value):
                self.state.best_metric = monitor_value
        except Exception as exc:  # pragma: no cover - persistence guard
            LOGGER.warning("Failed to persist checkpoint '%s': %s", checkpoint_path, exc)

    def evaluate(self) -> Mapping[str, float]:
        if self.val_loader is None:
            raise RuntimeError("Validation loader is not configured")
        self.simple.model.eval()
        losses: list[float] = []
        metrics: list[MutableMapping[str, float]] = []
        with torch.no_grad():
            for batch in self.val_loader:
                inputs, labels = self._prepare_batch(batch)
                outputs = self._forward(inputs)
                batch_metrics = self._compute_metrics(outputs, labels)
                losses.append(batch_metrics.get("val_loss", 0.0))
                metrics.append(batch_metrics)
        self.simple.model.train()
        aggregated: MutableMapping[str, float] = {}
        if losses:
            aggregated["val_loss"] = float(sum(losses) / len(losses))
        keys = {key for metric in metrics for key in metric}
        for key in keys:
            values = [metric[key] for metric in metrics if key in metric]
            if values:
                aggregated[key] = float(sum(values) / len(values))
        return aggregated

    def train(self) -> list[Mapping[str, float]]:
        cfg = self.config
        grad_steps = cfg.gradient_accumulation_steps
        for epoch in range(1, cfg.epochs + 1):
            self.state.epoch = epoch
            running_loss = 0.0
            num_batches = 0
            self.simple.optimizer.zero_grad(set_to_none=True)

            for step, batch in enumerate(self.train_loader, start=1):
                inputs, labels = self._prepare_batch(batch)
                with autocast(enabled=cfg.mixed_precision):
                    outputs = self._forward(inputs)
                    loss = self.loss_fn(outputs, labels)
                loss_value = float(loss.detach().cpu().item())
                running_loss += loss_value
                num_batches += 1
                scaled_loss = loss / grad_steps
                self.scaler.scale(scaled_loss).backward()

                should_step = step % grad_steps == 0 or step == len(self.train_loader)
                if should_step:
                    if cfg.max_grad_norm is not None:
                        self.scaler.unscale_(self.simple.optimizer)
                        torch.nn.utils.clip_grad_norm_(
                            self.simple.model.parameters(), cfg.max_grad_norm
                        )
                    self.scaler.step(self.simple.optimizer)
                    self.scaler.update()
                    self.simple.optimizer.zero_grad(set_to_none=True)
                    self.state.global_step += 1

                if (
                    cfg.log_every_n_steps
                    and should_step
                    and (self.state.global_step % cfg.log_every_n_steps == 0)
                ):
                    log_metrics(
                        self._logging_session,
                        {"train_loss": running_loss / max(1, num_batches)},
                        self.state.global_step,
                    )

            avg_loss = running_loss / max(1, num_batches)
            epoch_metrics: MutableMapping[str, float] = {"train_loss": float(avg_loss)}

            if self.val_loader is not None:
                try:
                    eval_metrics = self.evaluate()
                    epoch_metrics.update(eval_metrics)
                except Exception as exc:  # pragma: no cover - evaluation robustness
                    LOGGER.warning("Validation failed at epoch %s: %s", epoch, exc)

            self.history.append(dict(epoch_metrics))
            log_metrics(self._logging_session, epoch_metrics, epoch)
            self._save_checkpoint(epoch, epoch_metrics)

        return self.history

    def close(self) -> None:
        shutdown_logging(self._logging_session)

    def __del__(self) -> None:  # pragma: no cover - defensive cleanup
        with contextlib.suppress(Exception):
            self.close()


ExtendedTrainer = Trainer

__all__ = [
    "CheckpointConfig",
    "ExtendedTrainer",
    "Trainer",
    "TrainerConfig",
]

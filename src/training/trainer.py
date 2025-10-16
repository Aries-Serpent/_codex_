"""Extended training loop with evaluation, logging, and checkpointing."""

from __future__ import annotations

import json
import math
import pickle
from collections.abc import Callable, Iterable, Mapping, MutableMapping
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
from codex_ml.utils.error_log import log_error
from src.logging_utils import MLflowRunHandle, close_tensorboard, init_mlflow, init_tensorboard

from .simple_trainer import SimpleTrainer

Batch = Any
LossFn = Callable[[Any, Any], Any]
MetricFn = Callable[[Any, Any], float]


@dataclass(slots=True)
class TrainerLoggingConfig:
    """Optional logging integrations controlled via configuration."""

    enable_tensorboard: bool = False
    tensorboard_log_dir: str = "runs/tensorboard"
    enable_mlflow: bool = False
    mlflow_run_name: str = "codex-trainer"
    mlflow_tracking_uri: str | None = None
    mlflow_experiment: str | None = None


@dataclass(slots=True)
class CheckpointRecord:
    """Record describing a saved checkpoint and its metric."""

    epoch: int
    path: Path
    metric: float


class Trainer:
    """Extended trainer built around :class:`SimpleTrainer` for compatibility."""

    def __init__(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        train_loader: Iterable[Batch],
        *,
        val_loader: Iterable[Batch] | None = None,
        device: str = "cpu",
        loss_fn: LossFn | None = None,
        metric_fn: MetricFn | None = None,
        metric_mode: str = "min",
        gradient_accumulation_steps: int = 1,
        mixed_precision: bool = False,
        max_grad_norm: float | None = None,
        checkpoint_dir: str | Path | None = None,
        keep_best_k: int = 3,
        logging_config: TrainerLoggingConfig | Mapping[str, Any] | None = None,
        seed: int | None = None,
    ) -> None:
        if gradient_accumulation_steps < 1:
            raise ValueError("gradient_accumulation_steps must be >= 1")
        if keep_best_k < 1:
            raise ValueError("keep_best_k must be >= 1")
        self.simple = SimpleTrainer(model, optimizer, device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.loss_fn = loss_fn or self._default_loss_fn()
        self.metric_fn = metric_fn
        if metric_mode not in {"min", "max"}:
            raise ValueError("metric_mode must be 'min' or 'max'")
        self.metric_mode = metric_mode
        self.gradient_accumulation_steps = gradient_accumulation_steps
        self.max_grad_norm = max_grad_norm
        self.keep_best_k = keep_best_k
        self.checkpoint_dir = Path(checkpoint_dir) if checkpoint_dir else None
        if self.checkpoint_dir:
            self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self._scaler = self._build_grad_scaler(mixed_precision)
        self._checkpoints: list[CheckpointRecord] = []
        self._global_step = 0
        self._tensorboard = None
        self._mlflow: MLflowRunHandle | None = None
        config = self._coerce_logging_config(logging_config)
        if config.enable_tensorboard:
            self._tensorboard = init_tensorboard(True, config.tensorboard_log_dir)
        if config.enable_mlflow:
            self._mlflow = init_mlflow(
                True,
                config.mlflow_run_name,
                tracking_uri=config.mlflow_tracking_uri,
                experiment=config.mlflow_experiment,
            )
        if seed is not None:
            torch.manual_seed(seed)
            if getattr(torch.cuda, "is_available", lambda: False)():
                torch.cuda.manual_seed_all(seed)

    def _default_loss_fn(self) -> LossFn:
        fn = getattr(torch.nn.functional, "cross_entropy", None)
        if fn is None:
            raise RuntimeError(
                "torch.nn.functional.cross_entropy is required when no custom loss_fn is provided"
            )
        return fn

    def _build_grad_scaler(self, mixed_precision: bool) -> torch.cuda.amp.GradScaler | None:
        if not mixed_precision:
            return None
        cuda = getattr(torch, "cuda", None)
        amp = getattr(cuda, "amp", None)
        if cuda is None or amp is None or not hasattr(amp, "GradScaler"):
            raise RuntimeError(
                "Mixed precision requested but torch.cuda.amp.GradScaler is unavailable"
            )
        return amp.GradScaler()

    def _coerce_logging_config(
        self, config: TrainerLoggingConfig | Mapping[str, Any] | None
    ) -> TrainerLoggingConfig:
        if config is None:
            return TrainerLoggingConfig()
        if isinstance(config, TrainerLoggingConfig):
            return config
        data = dict(config)
        enable_mlflow = data.get("enable_mlflow")
        if enable_mlflow is None:
            enable_mlflow = data.get("mlflow_enable")
        return TrainerLoggingConfig(
            enable_tensorboard=bool(data.get("enable_tensorboard")),
            tensorboard_log_dir=str(data.get("tensorboard_log_dir", "runs/tensorboard")),
            enable_mlflow=bool(enable_mlflow),
            mlflow_run_name=str(data.get("mlflow_run_name", "codex-trainer")),
            mlflow_tracking_uri=data.get("mlflow_tracking_uri"),
            mlflow_experiment=data.get("mlflow_experiment"),
        )

    def step(self, batch: Batch) -> float:
        """Compatibility shim delegating to :class:`SimpleTrainer`."""

        return self.simple.step(batch)

    def _optimizer_step(self) -> None:
        if self._scaler is not None:
            if self.max_grad_norm is not None and hasattr(torch.nn.utils, "clip_grad_norm_"):
                self._scaler.unscale_(self.simple.optimizer)
                torch.nn.utils.clip_grad_norm_(self.simple.model.parameters(), self.max_grad_norm)
            self._scaler.step(self.simple.optimizer)
            self._scaler.update()
        else:
            if self.max_grad_norm is not None and hasattr(torch.nn.utils, "clip_grad_norm_"):
                torch.nn.utils.clip_grad_norm_(self.simple.model.parameters(), self.max_grad_norm)
            self.simple.optimizer.step()
        self.simple.optimizer.zero_grad()

    def _backward(self, loss: Any) -> None:
        if self._scaler is not None:
            scaled = self._scaler.scale(loss)
            scaled.backward()
        else:
            loss.backward()

    def _train_epoch(self, epoch: int) -> float:
        self.simple.model.train()
        total_loss = 0.0
        steps_since_update = 0
        batch_count = 0
        for batch in self.train_loader:
            self._global_step += 1
            inputs, targets = self._move_to_device(batch)
            context = {"epoch": epoch, "global_step": self._global_step}
            try:
                with self._autocast():
                    outputs = self._forward(inputs)
                    loss = self.loss_fn(outputs, targets)
            except Exception as exc:
                log_error("training.forward", str(exc), json.dumps(context))
                raise
            loss_to_backprop = loss
            if self.gradient_accumulation_steps > 1:
                loss_to_backprop = loss / float(self.gradient_accumulation_steps)
            self._backward(loss_to_backprop)
            steps_since_update += 1
            if steps_since_update >= self.gradient_accumulation_steps:
                self._optimizer_step()
                steps_since_update = 0
            total_loss += float(loss.detach().cpu().item())
            batch_count += 1
        if steps_since_update:
            self._optimizer_step()
        return total_loss / max(1, batch_count)

    def _forward(self, inputs: Any) -> Any:
        if isinstance(inputs, Mapping):
            return self.simple.model(**inputs)
        return self.simple.model(inputs)

    @contextmanager
    def _autocast(self):
        if self._scaler is None:
            yield
            return
        cuda = getattr(torch, "cuda", None)
        amp = getattr(cuda, "amp", None)
        autocast = getattr(amp, "autocast", None)
        if autocast is None:
            yield
            return
        with autocast():
            yield

    def _move_to_device(self, batch: Any) -> tuple[Any, Any]:
        if isinstance(batch, Mapping):
            batch_on_device = {
                key: value.to(self.simple.device) if hasattr(value, "to") else value
                for key, value in batch.items()
            }
            labels = batch_on_device.pop("labels", None)
            if labels is None:
                raise ValueError("Batch dictionary must contain a 'labels' entry")
            return batch_on_device, labels
        if isinstance(batch, list | tuple) and len(batch) == 2:
            inputs, targets = batch
            inputs = inputs.to(self.simple.device) if hasattr(inputs, "to") else inputs
            targets = targets.to(self.simple.device) if hasattr(targets, "to") else targets
            return inputs, targets
        raise TypeError(
            "Unsupported batch format; expected tuple or mapping with inputs and labels"
        )

    def evaluate(self) -> float:
        if self.val_loader is None or self.metric_fn is None:
            raise RuntimeError("Validation loader and metric_fn are required for evaluation")
        self.simple.model.eval()
        scores: list[float] = []
        no_grad = getattr(torch, "no_grad", None)
        context = no_grad() if callable(no_grad) else nullcontext()
        with context:
            for batch in self.val_loader:
                inputs, targets = self._move_to_device(batch)
                outputs = self._forward(inputs)
                score = self.metric_fn(outputs, targets)
                scores.append(float(score))
        self.simple.model.train()
        return sum(scores) / max(1, len(scores))

    def _should_replace(self, metric: float, best_metric: float) -> bool:
        if self.metric_mode == "max":
            return metric > best_metric
        return metric < best_metric

    def _save_checkpoint(self, epoch: int, metric: float, train_loss: float) -> None:
        if self.checkpoint_dir is None:
            return
        path = self.checkpoint_dir / f"epoch-{epoch:02d}.pt"
        try:
            state = {
                "epoch": epoch,
                "metric": metric,
                "train_loss": train_loss,
                "model": self.simple.model.state_dict(),
                "optimizer": self.simple.optimizer.state_dict(),
            }
            if hasattr(torch, "save"):
                torch.save(state, path)
            else:
                with path.open("wb") as handle:
                    pickle.dump(state, handle)
        except Exception as exc:  # pragma: no cover - filesystem failures are rare in tests
            log_error("training.checkpoint", str(exc), str(path))
            raise
        self._checkpoints.append(CheckpointRecord(epoch=epoch, path=path, metric=metric))
        self._prune_checkpoints()

    def _prune_checkpoints(self) -> None:
        if len(self._checkpoints) <= self.keep_best_k:
            return
        reverse = self.metric_mode == "max"
        self._checkpoints.sort(key=lambda item: item.metric, reverse=reverse)
        while len(self._checkpoints) > self.keep_best_k:
            worst = self._checkpoints.pop(-1)
            try:
                worst.path.unlink(missing_ok=True)
            except Exception as exc:  # pragma: no cover - filesystem failures are rare
                log_error("training.checkpoint", str(exc), f"remove:{worst.path}")

    def _log_epoch(self, epoch: int, train_loss: float, val_metric: float | None) -> None:
        payload: MutableMapping[str, float] = {"train_loss": train_loss}
        if val_metric is not None:
            payload["val_metric"] = val_metric
        if self._tensorboard is not None:
            for key, value in payload.items():
                self._tensorboard.add_scalar(key, value, epoch)
        if self._mlflow is not None:
            self._mlflow.log_metrics(payload, step=epoch)

    def train(self, epochs: int) -> dict[str, list[float]]:
        history: dict[str, list[float]] = {"train_loss": [], "val_metric": []}
        best_metric = math.inf if self.metric_mode != "max" else -math.inf
        for epoch in range(1, epochs + 1):
            train_loss = self._train_epoch(epoch)
            history["train_loss"].append(train_loss)
            val_metric: float | None = None
            if self.val_loader is not None and self.metric_fn is not None:
                val_metric = self.evaluate()
                history["val_metric"].append(val_metric)
            metric_for_ckpt = val_metric if val_metric is not None else train_loss
            self._log_epoch(epoch, train_loss, val_metric)
            if val_metric is not None:
                baseline_unset = (self.metric_mode != "max" and best_metric is math.inf) or (
                    self.metric_mode == "max" and best_metric is -math.inf
                )
                if baseline_unset or self._should_replace(val_metric, best_metric):
                    best_metric = val_metric
            self._save_checkpoint(epoch, metric_for_ckpt, train_loss)
        if not history["val_metric"]:
            history.pop("val_metric")
        close_tensorboard(self._tensorboard)
        if self._mlflow is not None:
            self._mlflow.end()
        return history


__all__ = ["Trainer", "TrainerLoggingConfig"]

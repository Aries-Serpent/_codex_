"""Extended training utilities with evaluation and checkpoint retention."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import torch
from logging_utils import LoggingConfig, init_mlflow, init_tensorboard

try:
    from torch.utils.data import DataLoader
except Exception:  # pragma: no cover - torch stub fallback
    DataLoader = None  # type: ignore[assignment]
from utils.error_logging import append_error

from .simple_trainer import SimpleTrainer


@dataclass(slots=True)
class CheckpointConfig:
    """Settings controlling checkpoint emission and retention."""

    directory: str | None = None
    keep_best_k: int = 1
    maximize_metric: bool = False


@dataclass(slots=True)
class TrainerConfig:
    """Runtime knobs for ``ExtendedTrainer``."""

    epochs: int = 1
    gradient_accumulation_steps: int = 1
    mixed_precision: bool = False
    seed: int = 42
    loss_fn: Callable[[torch.Tensor, torch.Tensor], torch.Tensor] | None = None


class ExtendedTrainer:
    """Train ``torch.nn.Module`` instances with evaluation + checkpointing."""

    def __init__(
        self,
        model: torch.nn.Module,
        optimizer: torch.optim.Optimizer,
        train_loader: DataLoader,
        *,
        device: str = "cpu",
        val_loader: DataLoader | None = None,
        trainer_config: TrainerConfig | None = None,
        checkpoint_config: CheckpointConfig | None = None,
        logging_config: LoggingConfig | None = None,
        metric_fn: Callable[[torch.Tensor, torch.Tensor], float] | None = None,
    ) -> None:
        if DataLoader is None:
            raise RuntimeError("torch.utils.data is required to use ExtendedTrainer")

        trainer_config = trainer_config or TrainerConfig()
        checkpoint_config = checkpoint_config or CheckpointConfig()
        logging_config = logging_config or LoggingConfig()

        torch.manual_seed(trainer_config.seed)
        if torch.cuda.is_available():  # pragma: no branch - deterministic seeding guard
            torch.cuda.manual_seed_all(trainer_config.seed)
        self.simple_trainer = SimpleTrainer(model, optimizer, device=device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.metric_fn = metric_fn
        self.config = trainer_config
        self.checkpoints = checkpoint_config
        self.logging_config = logging_config
        self.loss_fn = trainer_config.loss_fn or torch.nn.functional.cross_entropy
        self.tensorboard_writer = None
        self._mlflow = None
        self._mlflow_run = None
        self._checkpoint_records: list[tuple[float, Path]] = []
        self._amp_enabled = bool(trainer_config.mixed_precision and torch.cuda.is_available())
        self._prepare_logging()

    # ------------------------------------------------------------------
    # Lifecycle helpers
    def _prepare_logging(self) -> None:
        if self.logging_config.enable_tensorboard:
            self.tensorboard_writer = init_tensorboard(self.logging_config.tensorboard_log_dir)
        if self.logging_config.enable_mlflow:
            mlflow_module, mlflow_run = init_mlflow(
                self.logging_config.mlflow_run_name,
                tracking_uri=self.logging_config.mlflow_tracking_uri,
                tags=self.logging_config.mlflow_tags,
            )
            self._mlflow = mlflow_module
            self._mlflow_run = mlflow_run

    def _close_logging(self) -> None:
        if self.tensorboard_writer is not None:
            try:
                self.tensorboard_writer.flush()
                self.tensorboard_writer.close()
            except Exception as exc:  # pragma: no cover - flush failures are non fatal
                append_error(
                    "3.2", "tensorboard close", str(exc), self.logging_config.tensorboard_log_dir
                )
            finally:
                self.tensorboard_writer = None
        if self._mlflow is not None:
            try:
                if self._mlflow_run is not None:
                    self._mlflow.end_run()
            except Exception as exc:  # pragma: no cover - mlflow teardown guard
                append_error("3.2", "mlflow close", str(exc), self.logging_config.mlflow_run_name)
            finally:
                self._mlflow_run = None

    # ------------------------------------------------------------------
    # Training & evaluation
    def train(self) -> None:
        grad_accum = max(1, int(self.config.gradient_accumulation_steps))
        scaler = torch.cuda.amp.GradScaler(enabled=self._amp_enabled)
        optimizer = self.simple_trainer.optimizer
        device = self.simple_trainer.device

        for epoch in range(1, self.config.epochs + 1):
            epoch_loss = 0.0
            self.simple_trainer.model.train()
            optimizer.zero_grad(set_to_none=True)
            for step, batch in enumerate(self.train_loader, start=1):
                inputs, targets = self._move_to_device(batch, device)
                with torch.cuda.amp.autocast(enabled=self._amp_enabled):
                    outputs = self.simple_trainer.model(inputs)
                    loss = self.loss_fn(outputs, targets)
                loss_value = loss.detach().cpu().item()
                epoch_loss += float(loss_value)
                loss = loss / grad_accum
                scaler.scale(loss).backward()
                if step % grad_accum == 0 or step == len(self.train_loader):
                    scaler.step(optimizer)
                    scaler.update()
                    optimizer.zero_grad(set_to_none=True)
            avg_loss = epoch_loss / max(1, len(self.train_loader))
            val_metric = self.evaluate() if self.val_loader and self.metric_fn else None
            self._log_epoch(epoch, avg_loss, val_metric)
            metric_value = val_metric if val_metric is not None else avg_loss
            self._save_checkpoint(epoch, metric_value, has_metric=val_metric is not None)

        self._close_logging()

    def evaluate(self) -> float:
        if self.val_loader is None or self.metric_fn is None:
            raise RuntimeError("Validation loader and metric_fn must be provided for evaluation")
        self.simple_trainer.model.eval()
        total = 0.0
        count = 0
        device = self.simple_trainer.device
        with torch.no_grad():
            for batch in self.val_loader:
                inputs, targets = self._move_to_device(batch, device)
                outputs = self.simple_trainer.model(inputs)
                score = float(self.metric_fn(outputs, targets))
                total += score
                count += 1
        self.simple_trainer.model.train()
        return total / max(1, count)

    # ------------------------------------------------------------------
    def _move_to_device(
        self, batch: tuple[torch.Tensor, torch.Tensor], device: str
    ) -> tuple[torch.Tensor, torch.Tensor]:
        inputs, targets = batch
        return inputs.to(device), targets.to(device)

    def _log_epoch(self, epoch: int, train_loss: float, val_metric: float | None) -> None:
        payload = {"epoch": epoch, "train_loss": train_loss}
        if val_metric is not None:
            payload["val_metric"] = val_metric
        print(json.dumps(payload))

        if self.tensorboard_writer is not None:
            try:
                self.tensorboard_writer.add_scalar("train/loss", train_loss, epoch)
                if val_metric is not None:
                    self.tensorboard_writer.add_scalar("val/metric", val_metric, epoch)
            except Exception as exc:
                append_error("3.2", "tensorboard log", str(exc), f"epoch={epoch}")
        if self._mlflow is not None and self._mlflow_run is not None:
            try:
                self._mlflow.log_metric("train_loss", train_loss, step=epoch)
                if val_metric is not None:
                    self._mlflow.log_metric("val_metric", val_metric, step=epoch)
            except Exception as exc:
                append_error("3.2", "mlflow log", str(exc), f"epoch={epoch}")

    def _save_checkpoint(self, epoch: int, score: float, *, has_metric: bool) -> None:
        directory = self.checkpoints.directory
        if directory is None:
            return
        target_dir = Path(directory)
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            append_error("3.2", "checkpoint mkdir", str(exc), directory)
            return

        checkpoint_path = target_dir / f"epoch-{epoch}.pt"
        state = {
            "model_state": self.simple_trainer.model.state_dict(),
            "optimizer_state": self.simple_trainer.optimizer.state_dict(),
            "epoch": epoch,
            "score": score,
            "has_metric": has_metric,
        }
        try:
            torch.save(state, checkpoint_path)
        except Exception as exc:
            append_error("3.2", "checkpoint save", str(exc), str(checkpoint_path))
            return

        metric_score = score
        if not has_metric:
            metric_score = float("-inf") if self.checkpoints.maximize_metric else float("inf")
        self._checkpoint_records.append((metric_score, checkpoint_path))
        self._checkpoint_records.sort(
            key=lambda item: item[0], reverse=self.checkpoints.maximize_metric
        )
        while len(self._checkpoint_records) > max(1, self.checkpoints.keep_best_k):
            _, doomed = self._checkpoint_records.pop()
            try:
                doomed.unlink(missing_ok=True)
            except Exception as exc:
                append_error("3.2", "checkpoint cleanup", str(exc), str(doomed))


__all__ = [
    "CheckpointConfig",
    "ExtendedTrainer",
    "TrainerConfig",
]

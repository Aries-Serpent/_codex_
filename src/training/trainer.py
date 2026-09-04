"""Extended trainer with evaluation, gradient accumulation, and checkpointing."""

from __future__ import annotations

import contextlib
import inspect
import json
import logging
import os
import time
import weakref
from collections.abc import Callable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeAlias

logger = logging.getLogger(__name__)


def _shutdown_logging_session(session: LoggingSession | None) -> None:
    """Best-effort shutdown for optional logging resources."""
    if session is None:
        return
    try:
        shutdown_logging(session)
    except Exception:
        logger.debug("Failed to shut down logging session during finalization", exc_info=True)


try:  # pragma: no cover - optional torch guard for import-time failures
    import torch
    from torch import nn

    _HAS_REAL_TORCH = True
    GradScaler = torch.cuda.amp.GradScaler
    autocast = torch.cuda.amp.autocast
    DataLoader = torch.utils.data.DataLoader
except (ImportError, ModuleNotFoundError, ValueError, TypeError, AttributeError):  # pragma: no cover - degrade to a safe torch stub when absent
    _HAS_REAL_TORCH = False

    class _NoOpScaler:
        def __init__(self, *, enabled: bool = False) -> None:
            self.enabled = enabled

        def scale(self, loss: Any) -> Any:
            return loss

        def unscale_(self, _optimizer: Any) -> None:
            return None

        def step(self, optimizer: Any) -> None:
            optimizer.step()

        def update(self) -> None:
            return None

    class _NoOpNoGrad(contextlib.AbstractContextManager[Any]):
        def __exit__(self, exc_type, exc, tb) -> None:
            _ = (exc_type, exc, tb)

    class _TorchStub:
        class nn:
            class utils:
                @staticmethod
                def clip_grad_norm_(_params: Any, _max_norm: float) -> None:
                    return None

        @staticmethod
        def save(payload: Any, path: Path | str) -> None:
            raise RuntimeError(
                "torch.save is unavailable in torch stub mode; "
                "install real torch or disable checkpointing"
            )

        @staticmethod
        def no_grad() -> _NoOpNoGrad:
            return _NoOpNoGrad()

    torch = _TorchStub()  # type: ignore[assignment]
    nn = Any  # type: ignore[assignment]
    GradScaler = _NoOpScaler

    def autocast(*, enabled: bool = False) -> object:
        return contextlib.nullcontext()

    DataLoader = Any

# Define type aliases
if TYPE_CHECKING:  # pragma: no cover - typing bridge
    TensorType: TypeAlias = Any
    OptimizerType: TypeAlias = Any
    DataLoaderType: TypeAlias = Any
else:  # pragma: no cover - runtime fallback
    TensorType: TypeAlias = Any
    OptimizerType: TypeAlias = Any
    DataLoaderType: TypeAlias = Any


# Lazy import to break circular dependency with codex_ml.utils.repro
def _set_seed(seed: int) -> None:
    """Set random seed. Tries codex_ml implementation, falls back to basic torch/numpy."""
    try:
        from codex_ml.utils.repro import set_seed as _codex_set_seed

        _codex_set_seed(seed)
    except (ImportError, AttributeError):
        # Fallback if codex_ml not available
        try:
            import random

            random.seed(seed)
        except Exception:
            pass
        try:
            import numpy as np

            np.random.seed(seed)
        except Exception:
            pass
        try:
            if _HAS_REAL_TORCH:
                torch.manual_seed(seed)
                torch.cuda.manual_seed_all(seed)
        except Exception:
            pass


from ..logging_utils import (  # noqa: E402
    LoggingConfig,
    LoggingSession,
    log_metrics,
    setup_logging,
    shutdown_logging,
)
from ..metrics import append_ndjson  # noqa: E402
from .checkpointing import load_checkpoint  # noqa: E402
from .simple_trainer import SimpleTrainer  # noqa: E402

if hasattr(torch, "load"):
    try:
        _TORCH_SUPPORTS_WEIGHTS_ONLY = "weights_only" in inspect.signature(torch.load).parameters
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        _TORCH_SUPPORTS_WEIGHTS_ONLY = False
    _TORCH_LOAD_FN = getattr(torch, "load", None)
else:
    _TORCH_SUPPORTS_WEIGHTS_ONLY = False
    _TORCH_LOAD_FN = None


def _load_checkpoint_payload(path: Path, *, map_location: Any) -> Mapping[str, Any]:
    if torch is None or _TORCH_LOAD_FN is None:
        raise RuntimeError("torch is required to load checkpoints")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        kwargs["weights_only"] = False
    try:
        result = _TORCH_LOAD_FN(path, **kwargs)
    except TypeError as exc:
        type(exc).__name__
        logger.debug("TypeError: <ERROR_TYPE>")
        raise
    if not isinstance(result, Mapping):
        return {}
    return result


LOGGER = logging.getLogger(__name__)


_CHECKPOINT_POINTER_VERSION = "1.0"


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
    seed: int | None = None
    metrics_ndjson_path: str | None = None


# NOTE: Public compatibility alias expected by trainer API consumers and tests.
TrainerLoggingConfig = LoggingConfig


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
        gradient_accumulation_steps: int | None = None,
        checkpoint_dir: str | Path | None = None,
        keep_best_k: int | None = None,
        logging_config: LoggingConfig | Mapping[str, Any] | None = None,
        metric_mode: str | None = None,
        maximize_metric: bool | None = None,
    ) -> None:
        if not _HAS_REAL_TORCH and os.getenv("CODEX_ALLOW_TORCH_STUB", "0") != "1":
            raise RuntimeError(
                "Trainer requires a real torch installation. "
                "Set CODEX_ALLOW_TORCH_STUB=1 only for explicit stub-mode tests."
            )
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

        if gradient_accumulation_steps is not None:
            cfg.gradient_accumulation_steps = int(gradient_accumulation_steps)

        if logging_config is not None:
            if isinstance(logging_config, LoggingConfig):
                cfg.logging = logging_config
            elif isinstance(logging_config, Mapping):
                cfg.logging = LoggingConfig(**logging_config)
            else:
                raise TypeError("logging_config must be a LoggingConfig or mapping when provided")

        if metric_mode is not None:
            normalized_mode = metric_mode.lower()
            if normalized_mode not in {"min", "max"}:
                raise ValueError("metric_mode must be 'min' or 'max'")
        else:
            normalized_mode = None

        if cfg.seed is not None:
            try:
                resolved_seed = int(cfg.seed)
            except (TypeError, ValueError) as exc:
                type(exc).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                raise ValueError("TrainerConfig.seed must be an int") from exc
            _set_seed(resolved_seed)
            cfg.seed = resolved_seed

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
        elif checkpoint_dir is not None or keep_best_k is not None or normalized_mode is not None:
            if checkpoint_dir is None:
                raise TypeError("checkpoint_dir is required when configuring checkpoint options")
            cfg.checkpoint = CheckpointConfig(
                directory=str(checkpoint_dir),
                keep_best_k=keep_best_k,
                mode=normalized_mode,
                maximize_metric=maximize_metric,
            )

        if not _HAS_REAL_TORCH and cfg.checkpoint is not None:
            raise RuntimeError(
                "Checkpointing requires a real torch installation. "
                "Either install PyTorch or disable checkpoint_dir/checkpoint_config "
                "(checkpoint configuration is incompatible with CODEX_ALLOW_TORCH_STUB=1)."
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
        self._finalizer = weakref.finalize(self, _shutdown_logging_session, self._logging_session)
        metrics_path = cfg.metrics_ndjson_path
        self._metrics_path: Path | None = Path(metrics_path) if metrics_path else None
        self._resume_metadata: Mapping[str, Any] | None = None

        if cfg.checkpoint is not None:
            checkpoint_dir = Path(cfg.checkpoint.directory)
            checkpoint_dir.mkdir(parents=True, exist_ok=True)
            self._hydrate_existing_checkpoints(checkpoint_dir)
            latest = self._find_latest_checkpoint(checkpoint_dir)
            resumed = False
            if latest is not None:
                try:
                    self._load_checkpoint(*latest)
                except (
                    ValueError,
                    TypeError,
                    RuntimeError,
                ) as exc:  # pragma: no cover - resume is best-effort
                    LOGGER.warning("Auto-resume skipped due to error: %s", exc)
                else:
                    resumed = True
            if not resumed:
                self._resume_from_latest_checkpoint(cfg.checkpoint)

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

    def _zero_grad(self) -> None:
        try:
            self.simple.optimizer.zero_grad(set_to_none=True)
        except TypeError:
            self.simple.optimizer.zero_grad()

    def _forward(self, inputs: Any) -> torch.Tensor:
        if isinstance(inputs, Mapping):
            return self.simple.model(**inputs)
        return self.simple.model(inputs)

    def _latest_checkpoint_path(self, directory: str | Path) -> Path | None:
        try:
            candidates = sorted(
                (p for p in Path(directory).glob("epoch*-metric*.pt") if p.is_file()),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )
        except (IOError, OSError, ModuleNotFoundError, ImportError):  # pragma: no cover - directory read failure
            return None
        return candidates[0] if candidates else None

    def _resume_from_latest_checkpoint(self, cfg: CheckpointConfig) -> None:
        latest = self._latest_checkpoint_path(cfg.directory)
        if latest is None:
            return
        try:
            epoch, metric = load_checkpoint(latest, self.simple.model, self.simple.optimizer)
        except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover - robustness guard
            LOGGER.warning("Failed to auto-resume from %s: %s", latest, exc)
            return
        self.state.epoch = int(epoch)
        self.state.best_metric = float(metric)
        LOGGER.info(
            "Auto-resumed training from checkpoint %s (epoch=%s, metric=%s)",
            latest.name,
            epoch,
            metric,
        )

    def _default_loss(self, outputs: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        logits = getattr(outputs, "logits", outputs)
        return torch.nn.functional.cross_entropy(logits, labels)  # type: ignore[attr-defined]

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
            except (
                ValueError,
                TypeError,
                RuntimeError,
            ) as exc:  # pragma: no cover - metric robustness guard
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

    def _hydrate_existing_checkpoints(self, directory: Path) -> None:
        cfg = self.config.checkpoint
        if cfg is None:
            return
        entries: list[tuple[float, Path, Path]] = []
        for meta_path in sorted(directory.glob("epoch_*.json")):
            try:
                data = json.loads(meta_path.read_text(encoding="utf-8"))
            except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:
                type(exc).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                LOGGER.debug("Skipping checkpoint metadata %s: %s", meta_path, exc)
                continue
            monitor_value = data.get("monitor")
            if monitor_value is None:
                continue
            checkpoint_path = meta_path.with_suffix(".pt")
            if not checkpoint_path.exists():
                continue
            try:
                monitor_float = float(monitor_value)
            except (TypeError, ValueError):
                logger.debug("Exception caught, continuing", exc_info=True)
                continue
            entries.append((monitor_float, checkpoint_path, meta_path))
        if not entries:
            return
        self._checkpoints.extend(entries)
        reverse = cfg.mode.lower() == "max"
        self._checkpoints.sort(key=lambda item: item[0], reverse=reverse)
        self.state.best_metric = self._checkpoints[0][0]

    def _find_latest_checkpoint(self, directory: Path) -> tuple[Path, Mapping[str, Any]] | None:
        pointer = directory / "latest.json"
        if pointer.exists():
            try:
                payload = json.loads(pointer.read_text(encoding="utf-8"))
            except (IOError, OSError, ModuleNotFoundError, ImportError):
                logger.warning("Exception occurred", exc_info=True)
                payload = {}
            path_hint = payload.get("path")
            if path_hint:
                candidate = directory / str(path_hint)
                if candidate.exists():
                    return candidate, payload
        latest: tuple[Path, Mapping[str, Any]] | None = None
        for meta_path in sorted(directory.glob("epoch_*.json")):
            try:
                data = json.loads(meta_path.read_text(encoding="utf-8"))
            except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:
                type(exc).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                LOGGER.debug("Skipping checkpoint metadata %s: %s", meta_path, exc)
                continue
            checkpoint_path = meta_path.with_suffix(".pt")
            if not checkpoint_path.exists():
                continue
            epoch = data.get("epoch", 0)
            try:
                epoch_int = int(epoch)
            except (TypeError, ValueError):
                epoch_int = 0
            if latest is None or epoch_int > int(latest[1].get("epoch", 0)):
                enriched = dict(data)
                enriched.setdefault("path", checkpoint_path.name)
                latest = (checkpoint_path, enriched)
        return latest

    def _load_checkpoint(self, checkpoint_path: Path, pointer: Mapping[str, Any]) -> None:
        payload = _load_checkpoint_payload(checkpoint_path, map_location=self.device)
        model_state = payload.get("model_state") or payload.get("model")
        if isinstance(model_state, Mapping):
            self.simple.model.load_state_dict(model_state)
        optimizer_state = payload.get("optimizer_state") or payload.get("optimizer")
        if (
            optimizer_state
            and self.config.checkpoint is not None
            and self.config.checkpoint.save_optimizer
        ):
            with contextlib.suppress(Exception):
                self.simple.optimizer.load_state_dict(optimizer_state)

        epoch = pointer.get("epoch") or payload.get("epoch", 0)
        global_step = pointer.get("global_step") or payload.get("global_step", 0)
        monitor = pointer.get("monitor") or payload.get("monitor")
        try:
            self.state.epoch = int(epoch)
        except (TypeError, ValueError):
            self.state.epoch = 0
        try:
            self.state.global_step = int(global_step)
        except (TypeError, ValueError):
            self.state.global_step = 0
        if monitor is not None:
            with contextlib.suppress(TypeError, ValueError):
                self.state.best_metric = float(monitor)
        self._resume_metadata = pointer
        LOGGER.info(
            "Resumed trainer state from %s (epoch=%s, global_step=%s)",
            checkpoint_path,
            self.state.epoch,
            self.state.global_step,
        )

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
                except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover - retention guard
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
        payload["schema_version"] = _CHECKPOINT_POINTER_VERSION
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
            pointer_payload = {
                "schema_version": _CHECKPOINT_POINTER_VERSION,
                "epoch": epoch,
                "path": checkpoint_path.name,
                "global_step": self.state.global_step,
                "monitor": monitor_value,
                "updated_at": time.time(),
            }
            pointer_path = checkpoint_path.parent / "latest.json"
            pointer_path.write_text(json.dumps(pointer_payload, indent=2), encoding="utf-8")
        except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover - persistence guard
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

    def train(self, *, epochs: int | None = None) -> list[Mapping[str, float]]:
        cfg = self.config
        if epochs is not None:
            cfg.epochs = int(epochs)
        completed_epoch = max(0, self.state.epoch)
        start_epoch = completed_epoch + 1

        if completed_epoch:
            LOGGER.info(
                "Resuming training loop from epoch %s (next epoch=%s, target=%s)",
                completed_epoch,
                start_epoch,
                cfg.epochs,
            )

        if start_epoch > cfg.epochs:
            LOGGER.info(
                "Skipping training loop; start_epoch=%s exceeds configured epochs=%s",
                start_epoch,
                cfg.epochs,
            )
            return self.history[-1] if self.history else {}  # type: ignore[return-value]

        for epoch in range(start_epoch, cfg.epochs + 1):
            self.state.epoch = epoch

            # Train epoch
            epoch_metrics = self._train_epoch()

            # Validate epoch
            if self.val_loader is not None:
                self._validate_epoch(epoch, epoch_metrics)

            # Record history and metrics
            self.history.append(dict(epoch_metrics))
            log_metrics(self._logging_session, epoch_metrics, epoch)

            # Checkpoint epoch
            self._checkpoint_epoch(epoch, epoch_metrics)

        return self.history[-1] if self.history else {}  # type: ignore[return-value]

    def _train_epoch(self) -> MutableMapping[str, float]:
        """Train for one epoch and return metrics."""
        cfg = self.config
        grad_steps = cfg.gradient_accumulation_steps
        running_loss = 0.0
        num_batches = 0
        self._zero_grad()

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
                self._optimizer_step(cfg)
                self.state.global_step += 1

            if cfg.log_every_n_steps and should_step:
                self._log_step_metrics(running_loss, num_batches)

        avg_loss = running_loss / max(1, num_batches)
        return {"train_loss": float(avg_loss)}

    def _optimizer_step(self, cfg: TrainerConfig) -> None:
        """Perform optimizer step with gradient clipping if configured."""
        if cfg.max_grad_norm is not None:
            self.scaler.unscale_(self.simple.optimizer)
            torch.nn.utils.clip_grad_norm_(self.simple.model.parameters(), cfg.max_grad_norm)  # type: ignore[attr-defined]
        self.scaler.step(self.simple.optimizer)
        self.scaler.update()
        self._zero_grad()

    def _log_step_metrics(self, running_loss: float, num_batches: int) -> None:
        """Log metrics for current step."""
        if self.state.global_step % self.config.log_every_n_steps == 0:
            log_metrics(
                self._logging_session,
                {"train_loss": running_loss / max(1, num_batches)},
                self.state.global_step,
            )

    def _validate_epoch(
        self,
        epoch: int,
        epoch_metrics: MutableMapping[str, float],
    ) -> None:
        """Validate for current epoch and update metrics."""
        try:
            eval_metrics = self.evaluate()
            epoch_metrics.update(eval_metrics)
        except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover - evaluation robustness
            LOGGER.warning("Validation failed at epoch %s: %s", epoch, exc)

    def _checkpoint_epoch(
        self,
        epoch: int,
        epoch_metrics: Mapping[str, float],
    ) -> None:
        """Handle checkpoint saving and metrics recording."""
        if self._metrics_path is not None:
            try:
                record = {"epoch": epoch, "global_step": self.state.global_step}
                record.update({k: float(v) for k, v in epoch_metrics.items()})  # type: ignore[misc]
                append_ndjson(record, self._metrics_path)
            except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover - diagnostics only
                LOGGER.debug("Failed to write metrics NDJSON: %s", exc)
        self._save_checkpoint(epoch, epoch_metrics)

    def close(self) -> None:
        finalizer = getattr(self, "_finalizer", None)
        if finalizer is not None and finalizer.alive:
            finalizer.detach()
        session = getattr(self, "_logging_session", None)
        if session is not None:
            shutdown_logging(session)
            self._logging_session = None
            self._finalizer = None


ExtendedTrainer = Trainer

__all__ = [
    "CheckpointConfig",
    "ExtendedTrainer",
    "Trainer",
    "TrainerConfig",
    "TrainerLoggingConfig",
]

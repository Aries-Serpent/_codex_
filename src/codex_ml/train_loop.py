# PATCH: Added CUDNN determinism helper, checkpoint SHA256 hashing, config snapshot,
# retention policy execution, & metadata enhancements.
#
# New params:
#   deterministic_cudnn: bool = False
#   run_config: dict | None  (persisted to config.snapshot.json if provided)
#   retention_policy: dict | None  (e.g. {"keep_last":3, "keep_every":5})
#
# Metadata additions:
#   - latest.json now includes "checkpoint_sha256"
#   - metadata.json includes "checkpoint_sha256"
#   - final result includes "checkpoint_sha256_last"
#
# Behavior:
#   - Config snapshot written once per run (overwrites existing file).
#   - After saving an epoch checkpoint, optional retention pruning executes.

from __future__ import annotations

import hashlib
import json
import logging
import random
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from codex_ml.utils.checkpoint import load_checkpoint, save_checkpoint

logger = logging.getLogger(__name__)

try:
    import torch
    from torch import nn, optim
    from torch.optim.lr_scheduler import StepLR

    _HAS_TORCH = True
except Exception:  # noqa: broad-except
    torch = None  # type: ignore
    nn = None  # type: ignore
    optim = None  # type: ignore
    StepLR = None  # type: ignore
    _HAS_TORCH = False

try:
    from codex_ml.models.registry import get_model as instantiate_model
except Exception:  # noqa: broad-except
    instantiate_model = None  # type: ignore

try:
    from codex_ml.lora import apply_lora
except Exception:  # noqa: broad-except
    apply_lora = None  # type: ignore

try:
    from codex_ml.data import loaders as data_loaders
except Exception:  # noqa: broad-except
    data_loaders = None  # type: ignore

try:
    from codex_ml.callbacks import (
        Callback,
        EvaluationCallback,
        LoggingCallback,
        merge_callback_results,
    )
except Exception:  # noqa: broad-except

    class Callback:  # type: ignore
        def on_train_start(self, state: Dict[str, Any]) -> None: ...

        def on_epoch_start(self, epoch: int, state: Dict[str, Any]) -> None: ...

        def on_epoch_end(
            self,
            epoch: int,
            metrics: Dict[str, Any],
            state: Dict[str, Any],
        ) -> None: ...

        def on_train_end(self, state: Dict[str, Any]) -> None: ...

    def merge_callback_results(
        base: Dict[str, Any], addon: Dict[str, Any] | None
    ) -> Dict[str, Any]:
        if addon:
            base.update(addon)
        return base

    EvaluationCallback = Callback  # type: ignore
    LoggingCallback = Callback  # type: ignore

try:
    from codex_ml.utils.determinism import set_cudnn_deterministic
except Exception:  # noqa: broad-except

    def set_cudnn_deterministic(enable: bool, benchmark: bool = False):  # type: ignore
        return


try:
    from codex_ml.utils.retention import prune_checkpoints
except Exception:  # noqa: broad-except

    def prune_checkpoints(*args, **kwargs):  # type: ignore
        return {"dry_run": True}


_DEFAULT_SEED = 1234


def _set_seed(seed: Optional[int]):
    if seed in (None, 0):
        seed = _DEFAULT_SEED
    random.seed(seed)
    try:
        import numpy as np  # noqa

        np.random.seed(seed)  # type: ignore
    except Exception:  # noqa: broad-except
        pass
    if _HAS_TORCH:
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)


def _now_ts() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _resolve_dtype(dtype: Optional[str]):
    if not _HAS_TORCH or dtype is None:
        return None
    mapping = {
        "fp32": torch.float32,
        "float32": torch.float32,
        "f32": torch.float32,
        "bf16": getattr(torch, "bfloat16", None),
        "bfloat16": getattr(torch, "bfloat16", None),
        "fp16": torch.float16,
        "float16": torch.float16,
        "f16": torch.float16,
    }
    return mapping.get(dtype.lower(), None)


def _attempt_resume(model, optimizer, scheduler, checkpoint_dir: str | Path):
    resume_meta = {}
    if not checkpoint_dir:
        return 1, resume_meta
    ckpt_dir = Path(checkpoint_dir)
    latest_file = ckpt_dir / "latest.json"
    if not latest_file.exists():
        return 1, resume_meta
    try:
        data = json.loads(latest_file.read_text())
        last_epoch = int(data.get("epoch", 0))
        if last_epoch < 1:
            return 1, resume_meta
        ckpt_path = ckpt_dir / data.get("path", "")
        model_file = ckpt_path / "model.pt"
        if model is not None and model_file.exists():
            try:
                load_checkpoint(
                    model=model,
                    optimizer=optimizer,
                    scheduler=scheduler,
                    ckpt_dir=ckpt_path,
                )
                resume_meta["model_state_loaded"] = True
                resume_meta["optimizer_state_loaded"] = optimizer is not None
                resume_meta["scheduler_state_loaded"] = scheduler is not None
                # propagate sha256 if present
                sha = data.get("checkpoint_sha256")
                if sha:
                    resume_meta["previous_checkpoint_sha256"] = sha
            except Exception as e:  # noqa
                resume_meta["model_state_loaded"] = False
                resume_meta["optimizer_state_loaded"] = False
                resume_meta["scheduler_state_loaded"] = False
                resume_meta["model_state_error"] = str(e)
        start_epoch = last_epoch + 1
        resume_meta["resumed_from_epoch"] = last_epoch
        resume_meta["latest_checkpoint_path"] = str(ckpt_path)
        return start_epoch, resume_meta
    except Exception as e:  # noqa: broad-except
        resume_meta["resume_error"] = f"latest.json parse failure: {e}"
        return 1, resume_meta


def _select_parameters_for_optimization(model):
    if model is None:
        return []
    return [p for p in model.parameters() if p.requires_grad]


def _synthetic_step(model):
    if model is None:
        return 0.0
    first_param = None
    for p in model.parameters():
        if p.requires_grad and p.ndim > 0:
            first_param = p
            break
    if first_param is None:
        return 0.0
    loss_tensor = (first_param.float() ** 2).mean()
    loss_tensor.backward()
    return float(loss_tensor.detach().cpu().item())


def _init_scheduler(scheduler_cfg: Optional[dict], optimizer, total_epochs: int):
    if not scheduler_cfg or optimizer is None or not _HAS_TORCH:
        return None
    sched_type = scheduler_cfg.get("type")
    if not sched_type:
        return None
    base_lrs = [g["lr"] for g in optimizer.param_groups]

    if sched_type == "linear":
        final_lr_scale = float(scheduler_cfg.get("final_lr_scale", 0.0))

        class _LinearEpochScheduler:
            def __init__(self, opt, total_epochs, final_scale, base_lrs):
                self.opt = opt
                self.total_epochs = max(total_epochs, 1)
                self.final_scale = final_scale
                self.base_lrs = base_lrs
                self.last_epoch = 0

            def get_lr(self):
                progress = min(self.last_epoch / self.total_epochs, 1.0)
                scale = (1 - progress) + progress * self.final_scale
                return [lr * scale for lr in self.base_lrs]

            def step(self):
                self.last_epoch += 1
                new_lrs = self.get_lr()
                for g, lr in zip(self.opt.param_groups, new_lrs):
                    g["lr"] = lr

            def state_dict(self):
                return {
                    "last_epoch": self.last_epoch,
                    "total_epochs": self.total_epochs,
                    "final_lr_scale": self.final_scale,
                    "base_lrs": self.base_lrs,
                    "type": "linear",
                }

            def load_state_dict(self, state):
                self.last_epoch = state.get("last_epoch", 0)

        return _LinearEpochScheduler(optimizer, total_epochs, final_lr_scale, base_lrs)

    if sched_type == "step":
        if StepLR is None:
            return None
        step_size = int(scheduler_cfg.get("step_size", 1))
        gamma = float(scheduler_cfg.get("gamma", 0.9))
        return StepLR(optimizer, step_size=step_size, gamma=gamma)

    logger.warning("Unknown scheduler type '%s' - ignoring.", sched_type)
    return None


def _scheduler_current_lr(scheduler, optimizer):
    if scheduler is None or optimizer is None:
        return None
    try:
        return [pg["lr"] for pg in optimizer.param_groups]
    except Exception:  # noqa: broad-except
        return None


def _file_sha256(path: Path) -> str | None:
    if not path.exists():
        return None
    h = hashlib.sha256()
    try:
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:  # noqa: broad-except
        return None


@dataclass
class TrainingMetrics:
    epoch: int
    synthetic_loss: float | None = None
    optimizer_steps: int = 0
    total_steps: int = 0

    def to_dict(self):
        return asdict(self)


def run_training(
    epochs: int = 1,
    grad_accum: int = 1,
    seed: int | None = None,
    model: Optional[Any] = None,
    model_name: str | None = None,
    lora: bool = False,
    lora_cfg: dict | None = None,
    device: str | None = None,
    dtype: str | None = None,
    checkpoint_dir: str | None = None,
    resume: bool = False,
    steps_per_epoch: int = 4,
    return_state: bool = False,
    scheduler_cfg: dict | None = None,
    dataset_sources: Optional[List[str]] = None,
    dataset_cache_dir: Optional[str] = None,
    callbacks: Optional[List[Callback]] = None,
    eval_fn: Optional[Callable[[int, Dict[str, Any]], Dict[str, Any]]] = None,
    # NEW:
    deterministic_cudnn: bool = False,
    run_config: Optional[Dict[str, Any]] = None,
    retention_policy: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Training loop (extended):
      - CUDNN determinism (opt-in)
      - checkpoint sha256
      - config snapshot
      - retention policy
    """
    t_start = time.time()
    _set_seed(seed)
    if deterministic_cudnn:
        set_cudnn_deterministic(True, benchmark=False)

    if grad_accum < 1:
        grad_accum = 1
    if steps_per_epoch < 1:
        steps_per_epoch = 1

    default_device = "cuda" if (_HAS_TORCH and torch.cuda.is_available()) else "cpu"
    model_device = device or default_device
    resolved_dtype = _resolve_dtype(dtype)

    # Dataset ingestion (summaries only)
    dataset_files_count = 0
    dataset_total_records = 0
    dataset_checksums: List[str] = []
    if dataset_sources:
        if data_loaders is None:
            logger.warning("Dataset loaders unavailable; skipping dataset ingestion.")
        else:
            cache_dir = Path(dataset_cache_dir or "artifacts/data_cache")
            cache_dir.mkdir(parents=True, exist_ok=True)
            for src in dataset_sources:
                path = Path(src)
                if not path.exists():
                    logger.warning("Dataset source missing: %s", src)
                    continue
                try:
                    if path.suffix.lower() == ".jsonl":
                        _, meta = data_loaders.load_jsonl(path)
                    elif path.suffix.lower() == ".csv":
                        _, meta = data_loaders.load_csv(path)
                    else:
                        logger.warning("Unsupported dataset format: %s", path)
                        continue
                    dataset_files_count += 1
                    dataset_total_records += meta["num_records"]
                    dataset_checksums.append(meta["checksum"])
                except Exception as e:  # noqa: broad-except
                    logger.warning("Failed to load dataset %s: %s", src, e)

    internal_model_created = False
    model_params_count = None
    if model is None and model_name and _HAS_TORCH and instantiate_model is not None:
        try:
            model = instantiate_model(
                name=model_name,
                device=model_device,
                dtype=resolved_dtype,
                local_files_only=True,
            )
            internal_model_created = True
        except Exception as e:  # noqa: broad-except
            logger.warning("Failed to load model '%s': %s", model_name, e)
            model = None

    if model is not None and lora and apply_lora is not None:
        try:
            apply_lora(model, **(lora_cfg or {}))
        except Exception as e:  # noqa: broad-except
            logger.warning("Failed to apply LoRA: %s", e)

    if model is not None and _HAS_TORCH:
        try:
            model_params_count = sum(p.numel() for p in model.parameters())
        except Exception:  # noqa: broad-except
            model_params_count = None

    optimizer = None
    if model is not None and _HAS_TORCH:
        params = _select_parameters_for_optimization(model)
        if params:
            optimizer = optim.Adam(params, lr=1e-3)

    if _HAS_TORCH:
        scheduler = _init_scheduler(scheduler_cfg, optimizer, total_epochs=epochs)
    else:
        scheduler = None

    cb_list: List[Callback] = []
    if callbacks:
        cb_list.extend(callbacks)
    if eval_fn:
        cb_list.append(EvaluationCallback(eval_fn))
    cb_list.append(LoggingCallback())

    state: Dict[str, Any] = {
        "start_time": _now_ts(),
        "model": model,
        "optimizer": optimizer,
        "scheduler": scheduler,
        "dataset_total_records": dataset_total_records,
        "run_config": run_config,
    }

    for cb in cb_list:
        try:
            cb.on_train_start(state)
        except Exception as e:  # noqa: broad-except
            logger.warning("Callback on_train_start error: %s", e)

    # Persist config snapshot (if provided)
    if run_config and checkpoint_dir:
        try:
            ckpt_root = Path(checkpoint_dir)
            ckpt_root.mkdir(parents=True, exist_ok=True)
            (ckpt_root / "config.snapshot.json").write_text(
                json.dumps(run_config, indent=2, sort_keys=True)
            )
        except Exception as e:  # noqa: broad-except
            logger.warning("Failed to write config snapshot: %s", e)

    start_epoch = 1
    resume_meta = {}
    if resume and checkpoint_dir:
        start_epoch, resume_meta = _attempt_resume(
            model,
            optimizer,
            scheduler,
            checkpoint_dir,
        )

    target_epochs = int(epochs)
    if start_epoch > target_epochs:
        result = {
            "resumed": bool(resume_meta),
            "resumed_from_epoch": resume_meta.get("resumed_from_epoch"),
            "final_epoch": start_epoch - 1,
            "start_epoch": start_epoch,
            "message": "No epochs to run; already completed.",
            "optimizer_steps": 0,
            "total_steps": 0,
            "steps_per_epoch": steps_per_epoch,
            "grad_accum": grad_accum,
            "scheduler_type": scheduler_cfg.get("type") if scheduler_cfg else None,
            "dataset_files_count": len(dataset_sources or []),
            "dataset_total_records": dataset_total_records,
            "learning_rate_history": [],
        }
        if resume_meta:
            result["resume_meta"] = resume_meta
        if return_state:
            result["model"] = model
            result["optimizer"] = optimizer
            result["scheduler"] = scheduler
            result["state"] = state
        return result

    total_optimizer_steps = 0
    total_steps = 0
    learning_rate_history: List[List[float]] = []
    last_checkpoint_sha = None

    for epoch in range(start_epoch, target_epochs + 1):
        for cb in cb_list:
            try:
                cb.on_epoch_start(epoch, state)
            except Exception as e:  # noqa: broad-except
                logger.warning("Callback on_epoch_start error: %s", e)

        epoch_loss_accum = 0.0
        synthetic_losses: List[float] = []
        steps_this_epoch = 0
        optimizer_steps_this_epoch = 0

        if model is not None and optimizer is not None and _HAS_TORCH:
            if resolved_dtype is not None:
                try:
                    model.to(dtype=resolved_dtype)
                except Exception:  # noqa: broad-except
                    pass
            model.to(model_device)
            model.train()
            optimizer.zero_grad(set_to_none=True)

            for step in range(steps_per_epoch):
                steps_this_epoch += 1
                total_steps += 1
                loss_val = _synthetic_step(model)
                epoch_loss_accum += loss_val
                synthetic_losses.append(loss_val)
                if (step + 1) % grad_accum == 0:
                    try:
                        optimizer.step()
                        optimizer.zero_grad(set_to_none=True)
                        optimizer_steps_this_epoch += 1
                        total_optimizer_steps += 1
                    except Exception as e:  # noqa: broad-except
                        logger.warning("Optimizer step failed: %s", e)

            if steps_per_epoch % grad_accum != 0:
                try:
                    optimizer.step()
                    optimizer.zero_grad(set_to_none=True)
                    optimizer_steps_this_epoch += 1
                    total_optimizer_steps += 1
                except Exception as e:  # noqa: broad-except
                    logger.warning("Final optimizer step failed: %s", e)
        else:
            steps_this_epoch = steps_per_epoch
            total_steps += steps_per_epoch

        avg_loss = None
        if synthetic_losses:
            avg_loss = epoch_loss_accum / max(len(synthetic_losses), 1)

        if scheduler is not None and optimizer is not None:
            try:
                scheduler.step()
            except Exception as e:  # noqa: broad-except
                logger.warning("Scheduler step failed: %s", e)
            current_lrs = _scheduler_current_lr(scheduler, optimizer)
        else:
            current_lrs = _scheduler_current_lr(None, optimizer)

        learning_rate_history.append(current_lrs or [])

        epoch_metrics = TrainingMetrics(
            epoch=epoch,
            synthetic_loss=avg_loss,
            optimizer_steps=optimizer_steps_this_epoch,
            total_steps=steps_this_epoch,
        ).to_dict()
        epoch_metrics["lr"] = current_lrs

        for cb in cb_list:
            try:
                addon = cb.on_epoch_end(epoch, epoch_metrics, state)
                merge_callback_results(epoch_metrics, addon)
            except Exception as e:  # noqa: broad-except
                logger.warning("Callback on_epoch_end error: %s", e)

        if checkpoint_dir:
            epoch_dir = Path(checkpoint_dir) / f"epoch-{epoch:04d}"
            epoch_dir.mkdir(parents=True, exist_ok=True)
            ckpt_metadata = {
                "epoch": epoch,
                "created_at": _now_ts(),
                "model_params": model_params_count,
                "optimizer_steps_total": total_optimizer_steps,
                "optimizer_steps_epoch": optimizer_steps_this_epoch,
                "steps_per_epoch": steps_per_epoch,
                "grad_accum": grad_accum,
                "avg_loss": avg_loss,
                "scheduler_type": scheduler_cfg.get("type") if scheduler_cfg else None,
                "current_lrs": current_lrs,
                "learning_rate_history_len": len(learning_rate_history),
            }
            checkpoint_file = epoch_dir / "model.pt"
            if model is not None and _HAS_TORCH:
                try:
                    save_checkpoint(
                        model=model,
                        optimizer=optimizer,
                        scheduler=scheduler,
                        out_dir=epoch_dir,
                        metadata=ckpt_metadata,
                    )
                except Exception as e:  # noqa: broad-except
                    msg = "Failed to save checkpoint for epoch %d: %s"
                    logger.warning(msg, epoch, e)
            # Compute sha256
            last_checkpoint_sha = _file_sha256(checkpoint_file)
            # Update metadata.json to include sha (sidecar appended)
            try:
                meta_file = epoch_dir / "metadata.json"
                if meta_file.exists():
                    meta_data = json.loads(meta_file.read_text())
                else:
                    meta_data = {}
                meta_data["checkpoint_sha256"] = last_checkpoint_sha
                meta_file.write_text(json.dumps(meta_data, indent=2))
            except Exception as e:  # noqa: broad-except
                logger.warning("Failed to augment metadata.json: %s", e)

            latest_payload = {
                "epoch": epoch,
                "path": epoch_dir.name,
                "created_at": _now_ts(),
                "model_params": model_params_count,
                "optimizer_steps_total": total_optimizer_steps,
                "scheduler_type": scheduler_cfg.get("type") if scheduler_cfg else None,
                "checkpoint_sha256": last_checkpoint_sha,
            }
            try:
                (Path(checkpoint_dir) / "latest.json").write_text(
                    json.dumps(latest_payload, indent=2)
                )
            except Exception as e:  # noqa: broad-except
                logger.warning("Failed to write latest.json: %s", e)

            # Retention pruning
            if retention_policy:
                try:
                    prune_result = prune_checkpoints(checkpoint_dir, **retention_policy)
                    state["retention_last"] = prune_result
                except Exception as e:  # noqa: broad-except
                    logger.warning("Retention pruning failed: %s", e)

        logger.info(
            "Epoch %d/%d | loss=%s | steps=%d | opt_steps=%d | lr=%s | sha=%s",
            epoch,
            target_epochs,
            f"{avg_loss:.6f}" if avg_loss is not None else "n/a",
            steps_this_epoch,
            optimizer_steps_this_epoch,
            current_lrs,
            last_checkpoint_sha[:12] if last_checkpoint_sha else None,
        )

    for cb in cb_list:
        try:
            cb.on_train_end(state)
        except Exception as e:  # noqa: broad-except
            logger.warning("Callback on_train_end error: %s", e)

    wall = time.time() - t_start
    result = {
        "resumed": bool(resume_meta),
        "resumed_from_epoch": resume_meta.get("resumed_from_epoch"),
        "final_epoch": target_epochs,
        "start_epoch": start_epoch,
        "epochs": target_epochs,
        "optimizer_steps": total_optimizer_steps,
        "total_steps": total_steps,
        "steps_per_epoch": steps_per_epoch,
        "grad_accum": grad_accum,
        "model_params": model_params_count,
        "internal_model_created": internal_model_created,
        "wall_time_sec": wall,
        "scheduler_type": scheduler_cfg.get("type") if scheduler_cfg else None,
        "learning_rate_history": learning_rate_history,
        "dataset_files_count": len(dataset_sources or []),
        "dataset_total_records": dataset_total_records,
        "dataset_checksums": dataset_checksums,
        "checkpoint_sha256_last": last_checkpoint_sha,
        "retention_last": state.get("retention_last"),
    }
    if resume_meta:
        result["resume_meta"] = resume_meta

    if return_state:
        result["model"] = model
        result["optimizer"] = optimizer
        result["scheduler"] = scheduler
        result["state"] = state

    return result


__all__ = ["run_training"]

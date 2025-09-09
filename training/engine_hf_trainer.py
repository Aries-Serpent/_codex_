"""Minimal HuggingFace Trainer wrapper.

This module provides a thin convenience around ``transformers.Trainer``
for causal language modeling. It supports training either a pretrained
``AutoModelForCausalLM`` or a user supplied ``torch.nn.Module`` using a
``DataCollatorForLanguageModeling`` compatible collator.

Multi-GPU setups are enabled automatically when multiple CUDA devices are
available and ``torch.distributed`` is installed. NCCL is required for the
backend when GPUs are used. Set ``distributed=False`` to disable distributed
initialisation.

Features:
- Automatic tokenizer setup with pad token fallback
- LoRA integration via optional peft package
- Multi-GPU distributed training support
- Flexible precision settings (fp16/bf16)
- TensorBoard logging integration
- Checkpoint management with periodic saves
- Comprehensive metrics computation and logging
- YAML-based training configuration
- Deterministic seeding across libraries
"""

from __future__ import annotations

# ruff: noqa: E402


# --- Accelerate compatibility shim (must run before importing transformers.Trainer) ---
def _install_accelerate_compat() -> None:
    """
    Monkey-patch ``accelerate.Accelerator`` to accept both legacy kwargs
    (``dispatch_batches``, ``split_batches``, ``even_batches``, ``logging_dir``)
    and the new API (``dataloader_config``, ``project_dir``). Prints which path
    is chosen for CI visibility.
    """
    try:
        import accelerate  # type: ignore
        from accelerate import Accelerator as _BaseAccelerator  # type: ignore

        # presence of DataLoaderConfiguration indicates new-style API (v0.30+)
        DataLoaderConfiguration = getattr(
            getattr(accelerate, "utils", object()), "DataLoaderConfiguration", None
        )
    except Exception as e:  # pragma: no cover
        print(f"[codex][accelerate] failed to inspect accelerate: {e}")
        return

    class _CompatAccelerator(_BaseAccelerator):  # type: ignore[misc, override]
        def __init__(self, *args, **kwargs):
            # Normalize project_dir
            if "logging_dir" in kwargs and "project_dir" not in kwargs:
                kwargs["project_dir"] = kwargs.pop("logging_dir")
                print("[codex][accelerate] mapped logging_dir -> project_dir")

            if DataLoaderConfiguration is not None:
                # New API path: build dataloader_config from legacy kwargs if present
                dispatch = kwargs.pop("dispatch_batches", None)
                split = kwargs.pop("split_batches", None)
                even = kwargs.pop("even_batches", None)
                dlc = None
                if any(x is not None for x in (dispatch, split, even)):
                    dlc = DataLoaderConfiguration(
                        dispatch_batches=bool(dispatch) if dispatch is not None else False,
                        split_batches=bool(split) if split is not None else False,
                        even_batches=bool(even) if even is not None else False,
                    )
                # Respect explicit dataloader_config if the caller provided one
                if "dataloader_config" not in kwargs and dlc is not None:
                    kwargs["dataloader_config"] = dlc
                    print("[codex][accelerate] v>=0.30: using DataLoaderConfiguration path")
                else:
                    print(
                        "[codex][accelerate] v>=0.30: using provided dataloader_config or defaults"
                    )
            else:
                # Legacy path: translate or drop new-style kwargs
                project_dir = kwargs.pop("project_dir", None)
                if project_dir is not None and "logging_dir" not in kwargs:
                    kwargs["logging_dir"] = project_dir
                    print("[codex][accelerate] mapped project_dir -> logging_dir")

                dlc = kwargs.pop("dataloader_config", None)
                if dlc is not None:
                    if hasattr(dlc, "dispatch_batches"):
                        kwargs.setdefault(
                            "dispatch_batches", bool(getattr(dlc, "dispatch_batches"))
                        )
                    if hasattr(dlc, "split_batches"):
                        kwargs.setdefault("split_batches", bool(getattr(dlc, "split_batches")))
                    if hasattr(dlc, "even_batches"):
                        kwargs.setdefault("even_batches", bool(getattr(dlc, "even_batches")))
                    print(
                        "[codex][accelerate] v<0.30: translated dataloader_config -> legacy kwargs"
                    )

                print("[codex][accelerate] v<0.30: using legacy kwargs path")

            super().__init__(*args, **kwargs)

    # Monkey-patch the module attribute so any downstream `from accelerate import Accelerator`
    # after this point will see the compat subclass.
    setattr(accelerate, "Accelerator", _CompatAccelerator)  # type: ignore[attr-defined]
    print("[codex][accelerate] installed compat Accelerator shim")


# Install the shim BEFORE importing transformers/Trainer
_install_accelerate_compat()

import argparse
import json
import math
import os
import random
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, cast

import numpy as np
import torch
import yaml
from datasets import Dataset
from omegaconf import OmegaConf
from packaging.version import parse as _v
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    EarlyStoppingCallback,
    Trainer,
    TrainerCallback,
    TrainingArguments,
)
from transformers import __version__ as _hf_version
from transformers.optimization import get_scheduler

from codex_ml.data_utils import split_dataset
from codex_ml.monitoring.async_writer import AsyncLogFile
from codex_ml.monitoring.codex_logging import (
    CodexLoggers,
    _codex_log_all,
    _codex_logging_bootstrap,
    _codex_patch_argparse,
    _codex_sample_system,
)
from codex_ml.monitoring.schema import LogRecord
from codex_ml.peft.peft_adapter import apply_lora
from codex_ml.utils.checkpointing import build_payload_bytes, load_payload, set_seed
from codex_ml.utils.error_log import log_error
from codex_ml.utils.provenance import snapshot_hydra_config
from codex_ml.utils.repro import set_reproducible
from codex_utils.repro import log_env_info

# Optional dependencies with graceful fallbacks
try:  # optional checkpoint callback
    from training.checkpoint_manager import CheckpointManager
except Exception as exc:  # pragma: no cover - missing in some envs
    CheckpointManager = None  # type: ignore[assignment]
    log_error("checkpoint_import", str(exc), "training.checkpoint_manager")

try:  # Optional TensorBoard integration
    from tools.monitoring_integrate import SummaryWriter  # type: ignore
except Exception:  # pragma: no cover - optional dep
    SummaryWriter = None


try:  # Optional accelerate integration
    from accelerate import Accelerator as _Accelerator  # type: ignore
except Exception:  # pragma: no cover - optional dep
    _Accelerator = None  # type: ignore[assignment]


def _make_accelerator(**accelerate_kwargs: Any):
    """Construct an Accelerator using the global compatibility shim."""
    if _Accelerator is None:
        return None
    return _Accelerator(**accelerate_kwargs)


def build_trainer(
    model,
    args,
    train_ds,
    eval_ds,
    data_collator,
    tokenizer,
    scheduler_name: str = "linear",
    early_stop_patience: int | None = 3,
    early_stop_threshold: float | None = 0.0,
    **kw,
):
    """Construct a HF Trainer with optional early stopping and named LR scheduler."""
    if early_stop_patience:
        # Early stop needs a coherent best-model metric setup
        setattr(args, "load_best_model_at_end", True)
        if not getattr(args, "metric_for_best_model", None):
            setattr(args, "metric_for_best_model", "eval_loss")
        if getattr(args, "greater_is_better", None) is None:
            # default for loss-like metrics
            setattr(args, "greater_is_better", False)
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=train_ds,
        eval_dataset=eval_ds,
        data_collator=data_collator,
        tokenizer=tokenizer,
        **kw,
    )
    if early_stop_patience:
        trainer.add_callback(
            EarlyStoppingCallback(
                early_stopping_patience=int(early_stop_patience),
                early_stopping_threshold=float(early_stop_threshold or 0.0),
            )
        )
    if hasattr(trainer, "create_scheduler"):
        max_steps = getattr(args, "max_steps", 0)
        batch_size = max(1, getattr(args, "train_batch_size", 8))
        steps_per_epoch = (
            math.ceil(len(train_ds) / batch_size) if hasattr(train_ds, "__len__") else 0
        )
        num_steps = (
            max_steps
            if max_steps > 0
            else int(args.num_train_epochs * steps_per_epoch) if steps_per_epoch else None
        )
        trainer.create_scheduler(num_training_steps=num_steps)
        if scheduler_name:
            training_steps = num_steps
            if training_steps is None and hasattr(train_ds, "__len__"):
                try:
                    training_steps = args.num_train_epochs * (len(train_ds) // batch_size + 1)
                except TypeError:
                    training_steps = num_steps
            if training_steps is not None:
                trainer.lr_scheduler = get_scheduler(
                    name=scheduler_name,
                    optimizer=trainer.optimizer,
                    num_warmup_steps=getattr(args, "warmup_steps", 0),
                    num_training_steps=training_steps,
                )
    return trainer


__all__ = [
    "run_hf_trainer",
    "HFTrainerConfig",
    "build_training_args",
    "build_trainer",
    "load_training_arguments",
    "prepare_dataset",
    "_seed_everything",
    "_worker_init_fn",
    "_compute_metrics",
    "NDJSONMetricsWriter",
    "build_parser",
]


def build_training_args(
    output_dir: str,
    lr: float = 5e-5,
    *,
    gradient_accumulation_steps: int = 1,
    fp16: bool = False,
    bf16: bool = False,
    seed: Optional[int] = 42,
    **kw,
) -> TrainingArguments:
    """Construct ``TrainingArguments`` with common precision flags.

    Parameters
    ----------
    output_dir : str
        Directory for saving model checkpoints and logs
    lr : float, default=5e-5
        Learning rate for optimization
    gradient_accumulation_steps : int, default=1
        Steps to accumulate gradients before update
    fp16 : bool, default=False
        Enable half precision training
    bf16 : bool, default=False
        Enable bfloat16 precision training
    seed : int, optional, default=42
        Random seed for reproducibility
    **kw
        Additional keyword arguments for TrainingArguments

    Returns
    -------
    TrainingArguments
        Configured training arguments object
    """
    return TrainingArguments(
        output_dir=output_dir,
        learning_rate=lr,
        gradient_accumulation_steps=gradient_accumulation_steps,
        fp16=fp16,
        bf16=bf16,
        seed=seed,
        **kw,
    )


def _compute_metrics(eval_pred):
    """Compute token accuracy and perplexity for evaluation.

    Parameters
    ----------
    eval_pred : tuple
        Tuple of (predictions, labels) from evaluation

    Returns
    -------
    dict
        Dictionary containing token_accuracy and perplexity metrics
    """
    preds, labels = eval_pred
    import numpy as np

    mask = labels != -100
    acc = (preds.argmax(-1)[mask] == labels[mask]).mean() if mask.any() else 0.0
    loss = None
    try:
        logits = preds[mask]
        lbl = labels[mask]
        log_probs = logits - logits.max(axis=-1, keepdims=True)
        log_probs = log_probs - np.log(np.exp(log_probs).sum(axis=-1, keepdims=True))
        loss = float(-log_probs[np.arange(logits.shape[0]), lbl].mean())
    except Exception:
        loss = None
    ppl = float("inf") if loss in (None, 0) else math.exp(loss)
    return {"token_accuracy": float(acc), "perplexity": ppl}


def _seed_everything(seed: int = 42):
    """Set deterministic seeds across all libraries.

    Parameters
    ----------
    seed : int, default=42
        Seed value for reproducibility
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True)


def _worker_init_fn(worker_id):
    """Initialize worker with deterministic seed.

    Parameters
    ----------
    worker_id : int
        Worker process identifier
    """
    s = np.random.SeedSequence(42)
    np.random.seed(s.generate_state(1, dtype=np.uint32)[0] + worker_id)


class NDJSONMetricsWriter:
    """Write metrics to newline-delimited JSON format.

    If ``async_write`` is ``True`` an :class:`AsyncLogFile` is used to
    persist records without blocking the caller.
    """

    def __init__(self, path: str = ".codex/metrics.ndjson", async_write: bool = False):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.async_write = async_write
        self._async = AsyncLogFile(str(self.path)) if async_write else None

    def write(self, obj: dict | LogRecord) -> None:
        """Write ``obj`` as a JSON line respecting the strict schema."""

        if isinstance(obj, LogRecord):
            data = obj.redacted().dict()
        else:
            try:
                data = LogRecord(**obj).redacted().dict()  # type: ignore[arg-type]
            except Exception:
                data = obj
        if self._async is not None:
            self._async.write(data)
        else:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=True) + "\n")

    def close(self) -> None:
        if self._async is not None:
            self._async.close()

    def __del__(self) -> None:  # pragma: no cover - best effort
        try:
            self.close()
        except Exception:
            pass


@dataclass
class HFTrainerConfig:
    """Configuration for the HuggingFace Trainer.

    Attributes
    ----------
    model_name : str
        Name or path of the model to use
    tokenizer_name : str, optional
        Name or path of the tokenizer (defaults to model_name)
    config_path : Path, optional
        Path to YAML configuration file
    fp16 : bool
        Enable fp16 precision
    bf16 : bool
        Enable bf16 precision
    lora_r : int, optional
        LoRA rank parameter
    lora_alpha : int, optional
        LoRA alpha parameter
    lora_dropout : float, optional
        LoRA dropout rate
    precision : str, optional
        Precision setting override
    gradient_accumulation_steps : int
        Gradient accumulation steps
    checkpoint_dir : Path, optional
        Directory for checkpoints
    save_steps : int
        Steps between saves
    keep_last : int
        Number of recent checkpoints to retain
    best_metric : str, optional
        Metric name to track best model
    best_mode : str
        Comparison mode for best metric ("min" or "max")
    """

    model_name: str = "sshleifer/tiny-gpt2"
    tokenizer_name: Optional[str] = None
    config_path: Optional[Path] = None
    fp16: bool = False
    bf16: bool = False
    lora_r: Optional[int] = None
    lora_alpha: Optional[int] = None
    lora_dropout: Optional[float] = None
    precision: Optional[str] = None
    gradient_accumulation_steps: int = 1
    checkpoint_dir: Optional[Path] = None
    save_steps: int = 100
    keep_last: int = 3
    best_metric: Optional[str] = None
    best_mode: str = "min"


def load_training_arguments(
    path: Optional[Path],
    output_dir: Path,
    precision: Optional[str],
    *,
    gradient_accumulation_steps: int = 1,
    tensorboard: bool = False,
    has_eval: bool = False,
    hydra_cfg: Optional[dict] = None,
) -> TrainingArguments:
    """Load ``TrainingArguments`` from YAML and apply runtime overrides."""
    cfg: Dict[str, object] = {}
    # Load base config from Hydra when provided
    if hydra_cfg is not None:
        cfg.update(hydra_cfg)
    elif path is not None:
        if path.exists():
            loaded = OmegaConf.to_container(OmegaConf.load(path), resolve=True)
            if isinstance(loaded, dict):
                cfg.update(loaded)
        else:
            print(f"[warning] config {path} missing, using default training args")
    cfg.setdefault("output_dir", str(output_dir))
    cfg["output_dir"] = str(output_dir)

    # Provide sane defaults when config is missing or incomplete
    cfg.setdefault("num_train_epochs", 1)
    cfg.setdefault("learning_rate", 5e-4)
    cfg.setdefault("per_device_train_batch_size", 8)

    if precision:
        p = precision.lower()
        if p == "fp16":
            cfg["fp16"] = True
        elif p == "bf16":
            cfg["bf16"] = True

    if tensorboard:
        cfg.setdefault("report_to", ["tensorboard"])
        cfg.setdefault("logging_dir", str(output_dir / "tensorboard"))

    if has_eval:
        cfg.setdefault("evaluation_strategy", "epoch")
        cfg.setdefault("logging_strategy", "epoch")

    # Handle gradient accumulation steps with both parameter fallback and Hydra integration
    if hydra_cfg and "gradient_accumulation_steps" in hydra_cfg:
        cfg.setdefault(
            "gradient_accumulation_steps",
            int(hydra_cfg["gradient_accumulation_steps"]),
        )
    else:
        cfg.setdefault("gradient_accumulation_steps", int(gradient_accumulation_steps))

    # Remove non-TrainingArguments keys from config
    for extra in (
        "lora_r",
        "lora_alpha",
        "lora_dropout",
        "precision",
        "checkpoint_dir",
        "model_name",
        "tokenizer_name",
        "tokenizer_path",
        "use_fast_tokenizer",
        "epochs",
        "val_split",
        "test_split",
        "logging",
        "checkpoint",
        "training",
        "early_stopping_patience",
        "lora",
    ):
        cfg.pop(extra, None)

    # Drop unsupported label smoothing when transformers is too old
    if "label_smoothing_factor" in cfg and _v(_hf_version) < _v("4.3.0"):
        cfg.pop("label_smoothing_factor")

    return TrainingArguments(**cfg)


def prepare_dataset(texts: Iterable[str], tokenizer) -> Dataset:
    """Tokenize an iterable of texts into a ``Dataset``."""
    ds = Dataset.from_dict({"text": list(texts)})
    ds = ds.map(lambda ex: tokenizer(ex["text"], truncation=True), batched=True)
    return ds


def run_hf_trainer(
    texts: Iterable[str],
    output_dir: Path,
    model: Optional[torch.nn.Module] = None,
    *,
    model_name: str = "sshleifer/tiny-gpt2",
    tokenizer_name: Optional[str] = None,
    tokenizer_path: Optional[str] = None,
    use_fast_tokenizer: bool = True,
    config_path: Optional[Path] = None,
    fp16: bool = False,
    bf16: bool = False,
    lora_r: Optional[int] = None,
    lora_alpha: Optional[int] = None,
    lora_dropout: Optional[float] = None,
    precision: Optional[str] = None,
    device: str = "auto",
    dtype: str = "fp32",
    gradient_accumulation_steps: int = 1,
    checkpoint_dir: Optional[Path] = None,
    save_steps: int = 100,
    keep_last: int = 3,
    best_metric: Optional[str] = "eval_loss",
    best_mode: str = "min",
    seed: int = 0,
    resume_from: Optional[str] = None,
    val_texts: Optional[Iterable[str]] = None,
    val_split: float = 0.0,
    split_cache: Optional[Path] = None,
    distributed: bool = True,
    tensorboard: bool = False,
    accelerate_kwargs: Optional[Dict[str, object]] = None,
    hydra_cfg: Optional[Dict[str, object]] = None,
    log_args: Optional[argparse.Namespace] = None,
) -> Dict[str, float]:
    """Train a causal LM using HuggingFace ``Trainer``."""
    # Set deterministic seeds
    set_reproducible(seed)
    set_seed(seed, output_dir)
    if torch.cuda.is_available() and dtype in {"fp32", "fp16", "bf16"}:
        assert (
            torch.backends.cudnn.deterministic
        ), "cuDNN must be deterministic; call set_reproducible()"
    log_env_info(output_dir / "env.json")
    try:
        snapshot_hydra_config({"model_name": model_name, "seed": seed}, output_dir)
    except Exception:
        pass
    resume_ckpt = Path(resume_from) if resume_from else None
    if resume_ckpt and not resume_ckpt.exists():
        print(f"Checkpoint {resume_ckpt} not found; starting fresh.")
        resume_ckpt = None
    if resume_ckpt is None and checkpoint_dir and CheckpointManager is not None:
        auto = CheckpointManager.find_resume(checkpoint_dir)
        if auto:
            resume_ckpt = Path(auto)
    custom_resume = resume_ckpt if resume_ckpt and resume_ckpt.is_file() else None

    # Resolve tokenizer configuration
    cfg: Dict[str, object] = {}
    if config_path and config_path.exists():
        try:
            cfg = yaml.safe_load(config_path.read_text()) or {}
        except Exception:
            cfg = {}
    tokenizer_path = tokenizer_path or cast(Optional[str], cfg.get("tokenizer_path"))
    use_fast_tokenizer = cast(bool, cfg.get("use_fast_tokenizer", use_fast_tokenizer))
    tokenizer_name = tokenizer_name or cast(Optional[str], cfg.get("tokenizer_name")) or model_name
    source = tokenizer_path or tokenizer_name
    tokenizer = AutoTokenizer.from_pretrained(source, use_fast=use_fast_tokenizer)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Optionally split dataset
    train_texts = texts
    if val_texts is None and val_split > 0:
        train_texts, val_texts = split_dataset(
            texts, train_ratio=1 - val_split, seed=seed, cache_path=split_cache
        )

    # Prepare datasets
    ds = prepare_dataset(train_texts, tokenizer)
    eval_ds = prepare_dataset(val_texts, tokenizer) if val_texts is not None else None
    collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    # Load model if not provided
    if model is None:
        model = AutoModelForCausalLM.from_pretrained(model_name)

    # Enforce device and precision placement
    resolved_device = (
        device if device != "auto" else ("cuda" if torch.cuda.is_available() else "cpu")
    )
    model = model.to(resolved_device)
    effective_precision = precision or (dtype if dtype != "fp32" else None)
    if effective_precision in {"fp16", "bf16"}:
        torch_dtype = torch.float16 if effective_precision == "fp16" else torch.bfloat16
        model = model.to(dtype=torch_dtype)

    # Handle distributed training setup
    no_ddp = not distributed
    if no_ddp:
        os.environ["CUDA_VISIBLE_DEVICES"] = ""

    # Multi-GPU support
    if distributed and torch.cuda.device_count() > 1 and torch.distributed.is_available():
        backend = "nccl" if torch.cuda.is_available() else "gloo"
        if not torch.distributed.is_initialized():
            torch.distributed.init_process_group(backend=backend)
        print(
            f"Using torch.distributed with backend={backend} for {torch.cuda.device_count()} GPUs"
        )

    set_reproducible(seed)
    # Determine precision settings
    prec = effective_precision or ("bf16" if bf16 else ("fp16" if fp16 else None))
    training_args = load_training_arguments(
        config_path,
        output_dir,
        prec if torch.cuda.is_available() else None,
        gradient_accumulation_steps=gradient_accumulation_steps,
        tensorboard=tensorboard,
        has_eval=eval_ds is not None,
        hydra_cfg=hydra_cfg,
    )

    # Setup LoRA via adapter when requested, pulling defaults from Hydra config
    if hydra_cfg:
        lora_r = lora_r or cast(Optional[int], hydra_cfg.get("lora_r"))
        if lora_alpha is None:
            lora_alpha = cast(Optional[int], hydra_cfg.get("lora_alpha"))
        if lora_dropout is None:
            lora_dropout = cast(Optional[float], hydra_cfg.get("lora_dropout"))
    if lora_alpha is None:
        lora_alpha = 16
    if lora_r:
        try:
            cfg = {"r": int(lora_r), "lora_alpha": int(lora_alpha)}
            if lora_dropout is not None:
                cfg["lora_dropout"] = float(lora_dropout)
            model = apply_lora(model, cfg)
        except Exception as exc:
            log_error("lora_import", str(exc), "peft")

    # Setup checkpoint callbacks
    callbacks = None
    if checkpoint_dir and CheckpointManager is not None:
        try:
            manager = CheckpointManager(
                Path(checkpoint_dir),
                keep_last=keep_last,
                metric=best_metric,
                mode=best_mode,
            )

            class _CheckpointCallback(TrainerCallback):  # type: ignore[misc]
                def __init__(self) -> None:
                    self.model = None
                    self.optimizer = None
                    self.lr_scheduler = None
                    self.scaler = None
                    self._logs: Dict[str, float] | None = None

                def on_train_begin(self, args, state, control, **kwargs):
                    self.model = kwargs.get("model")
                    self.optimizer = kwargs.get("optimizer")
                    self.lr_scheduler = kwargs.get("lr_scheduler")
                    self.scaler = kwargs.get("scaler")
                    return control

                def on_log(self, args, state, control, logs=None, **kwargs):
                    self._logs = dict(logs or {})
                    return control

                def on_step_end(self, args, state, control, **kwargs):
                    step = state.global_step
                    if (
                        step
                        and save_steps
                        and step % save_steps == 0
                        and self.model is not None
                        and self.optimizer is not None
                    ):
                        payload = build_payload_bytes(
                            self.model,
                            self.optimizer,
                            self.lr_scheduler,
                            self.scaler,
                            rng_state=True,
                        )
                        manager.maybe_save(step, payload, self._logs, save_steps)
                    return control

            callbacks = [_CheckpointCallback()]
        except Exception as exc:
            log_error("checkpoint_init", str(exc), str(checkpoint_dir))

    # Initialize logging only when explicitly requested
    loggers = CodexLoggers()
    if log_args is not None:
        use_tb = bool(tensorboard or getattr(log_args, "tensorboard", False))
        use_wb = bool(getattr(log_args, "enable_wandb", False))
        use_mf = bool(getattr(log_args, "mlflow_enable", False))
        if use_tb or use_wb or use_mf:
            os.environ.setdefault("WANDB_MODE", "offline")
            os.environ.setdefault("MLFLOW_TRACKING_URI", "file:./mlruns")
            try:
                loggers = _codex_logging_bootstrap(log_args)
            except Exception as exc:  # pragma: no cover - bootstrap is best-effort
                print(f"[telemetry] bootstrap skipped: {exc}")

    # If this code path needs an Accelerator (e.g., for non-Trainer ops), construct it via the shim.
    accelerate_kwargs = dict(accelerate_kwargs or {})
    _accelerator = _make_accelerator(**accelerate_kwargs)
    _ = _accelerator  # keep alive

    # Create and run trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ds,
        eval_dataset=eval_ds,
        data_collator=collator,
        compute_metrics=_compute_metrics if eval_ds is not None else None,
        callbacks=callbacks,
    )
    if custom_resume:
        try:
            train_dl = trainer.get_train_dataloader()
            steps_per_epoch = math.ceil(len(train_dl) / training_args.gradient_accumulation_steps)
            max_steps = (
                training_args.max_steps
                if training_args.max_steps > 0
                else steps_per_epoch * training_args.num_train_epochs
            )
            trainer.create_optimizer_and_scheduler(num_training_steps=max_steps)
            load_payload(
                str(custom_resume),
                trainer.model,
                trainer.optimizer,
                trainer.lr_scheduler,
                getattr(trainer, "scaler", None),
            )
            m = re.search(r"ckpt-(\d+)\.pt", custom_resume.name)
            if m:
                trainer.state.global_step = int(m.group(1))
        except Exception as exc:  # pragma: no cover - resume best effort
            print(f"Failed to load checkpoint {custom_resume}: {exc}")
        resume_ckpt = None

    # Train with optional checkpoint resumption
    result = trainer.train(resume_from_checkpoint=str(resume_ckpt) if resume_ckpt else None)
    trainer.save_model()

    # Collect metrics
    metrics = dict(result.metrics)
    if eval_ds is not None:
        eval_metrics = trainer.evaluate()
        metrics.update({f"eval_{k}": v for k, v in eval_metrics.items()})
    metrics.setdefault("global_step", trainer.state.global_step)

    # Codex offline logging
    try:
        sysd = _codex_sample_system()
        log_vals = {
            **{k: v for k, v in metrics.items() if isinstance(v, (int, float))},
            **sysd,
        }
        _codex_log_all(int(metrics.get("global_step", 0)), log_vals, loggers)
    except Exception:
        pass

    # TensorBoard logging
    if tensorboard and SummaryWriter is not None:
        try:
            writer = SummaryWriter(log_dir=str(output_dir / "tensorboard"))
            for k, v in metrics.items():
                if isinstance(v, (int, float)):
                    writer.add_scalar(k, v, trainer.state.global_step)
            writer.flush()
            writer.close()
        except Exception:
            pass

    # Persist metrics to JSON and NDJSON for downstream analytics
    metrics_json = output_dir / "metrics.json"
    with metrics_json.open("w", encoding="utf-8") as fh:
        json.dump(metrics, fh)
    record = dict(metrics)
    record["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    writer = NDJSONMetricsWriter(str(output_dir / "metrics.ndjson"))
    writer.write(record)
    writer.close()

    return metrics


def build_parser() -> argparse.ArgumentParser:
    """Build a parser including monitoring flags."""
    parser = argparse.ArgumentParser(description="HF Trainer")
    add = parser.add_argument
    add(
        "--device",
        type=str,
        default="auto",
        choices=["cpu", "cuda", "auto"],
        help="Device placement",
    )
    add(
        "--dtype",
        type=str,
        default="fp32",
        choices=["fp32", "fp16", "bf16"],
        help="Numerical precision",
    )
    add("--lora-r", type=int, default=None, help="LoRA rank parameter")
    add("--lora-alpha", type=int, default=None, help="LoRA alpha parameter")
    add("--lora-dropout", type=float, default=None, help="LoRA dropout rate")
    return _codex_patch_argparse(parser)

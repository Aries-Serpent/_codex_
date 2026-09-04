"""Minimal HuggingFace Trainer wrapper.

This module provides a thin convenience around ``transformers.Trainer``
for causal language modeling. It supports training either a pretrained
``AutoModelForCausalLM`` or a user supplied ``torch.nn.Module`` using a
``DataCollatorForLanguageModeling`` compatible collator.

Multi-GPU setups are enabled automatically when multiple CUDA devices are
available and ``torch.distributed`` is installed. NCCL is required for the
backend when GPUs are used. set ``distributed=False`` to disable distributed
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

import logging

logger = logging.getLogger(__name__)

# ruff: noqa: E402, I001


# --- Accelerate compatibility shim (must run before importing transformers.Trainer) ---
def _install_accelerate_compat() -> None:
    """
    Monkey-patch ``accelerate.Accelerator`` to accept both legacy kwargs
    (``dispatch_batches``, ``split_batches``, ``even_batches``, ``logging_dir``)
    and the new API (``dataloader_config``, ``project_dir``). Prints which path
    is chosen for CI visibility.
    """
    try:
        import accelerate
        from accelerate import Accelerator as _BaseAccelerator

        # presence of DataLoaderConfiguration indicates new-style API (v0.30+)
        DataLoaderConfiguration = getattr(
            getattr(accelerate, "utils", object()), "DataLoaderConfiguration", None
        )
    except (ValueError, TypeError, ModuleNotFoundError) as e:  # pragma: no cover
        type(e).__name__
        print("[codex][accelerate] failed to inspect accelerate: <ERROR_TYPE>")
        return

    class _CompatAccelerator(_BaseAccelerator):
        def __init__(self, *args, **kwargs) -> None:
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
                        kwargs.setdefault("dispatch_batches", bool(dlc.dispatch_batches))
                    if hasattr(dlc, "split_batches"):
                        kwargs.setdefault("split_batches", bool(dlc.split_batches))
                    if hasattr(dlc, "even_batches"):
                        kwargs.setdefault("even_batches", bool(dlc.even_batches))
                    print(
                        "[codex][accelerate] v<0.30: translated dataloader_config -> legacy kwargs"
                    )

                print("[codex][accelerate] v<0.30: using legacy kwargs path")

            super().__init__(*args, **kwargs)

    # Monkey-patch the module attribute so any downstream `from accelerate import Accelerator`
    # after this point will see the compat subclass.
    accelerate.Accelerator = _CompatAccelerator
    print("[codex][accelerate] installed compat Accelerator shim")


# Install the shim BEFORE importing transformers/Trainer
_install_accelerate_compat()

import argparse
import csv
import importlib
import importlib.util
import json
import math
import os
import random
import re
import shutil
import time
import warnings
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import Any, Optional, cast

try:  # pragma: no cover - numpy optional in offline environments
    import numpy as np
except (IOError, OSError, ModuleNotFoundError, ImportError):  # pragma: no cover - numpy missing
    np = None


try:  # pragma: no cover - optional datasets dependency
    from datasets import Dataset  # type: ignore[attr-defined]
except (ImportError, AttributeError):  # pragma: no cover - datasets missing

    class Dataset:  # type: ignore[no-redef]
        """Minimal stand-in for datasets.Dataset used in tests/offline.

        Provides enough surface to not explode during unit tests that don't
        actually exercise HF dataset transforms.
        """

        def __init__(self, data: dict[str, Any] | None = None) -> None:
            self._data = data or {}

        @classmethod
        def from_dict(cls, data: dict[str, Any]) -> Dataset:
            return cls(data)

        def to_dict(self) -> dict[str, Any]:
            return dict(self._data)

        def map(self, *args: Any, **kwargs: Any) -> Dataset:
            # No-op map for offline environments
            return self

        def __len__(self) -> int:
            if not self._data:
                return 0
            # Assume all columns have equal length; use first column
            first_key = next(iter(self._data))
            col = self._data[first_key]
            try:
                return len(col)
            except (ValueError, TypeError):
                logger.warning("Exception occurred", exc_info=True)
                return 0


from packaging.version import parse as _v

try:  # pragma: no cover - optional transformers dependency
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
except (ImportError, AttributeError):  # pragma: no cover - transformers missing
    _hf_version = "0.0.0-offline"

    class _MissingTransformersObject:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ImportError("transformers dependency not available in offline mode")

    AutoModelForCausalLM = _MissingTransformersObject  # type: ignore[misc,assignment]
    AutoTokenizer = _MissingTransformersObject  # type: ignore[misc,assignment]
    DataCollatorForLanguageModeling = _MissingTransformersObject  # type: ignore[misc,assignment]

    class EarlyStoppingCallback:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ImportError("transformers EarlyStoppingCallback unavailable in offline mode")

    class TrainerCallback:  # type: ignore[no-redef]
        pass

    class TrainingArguments:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.args = args
            self.kwargs = kwargs

    class Trainer:  # type: ignore[no-redef]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            raise ImportError("transformers.Trainer unavailable in offline mode")

        def add_callback(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
            raise ImportError("transformers.Trainer unavailable in offline mode")

        def create_scheduler(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
            raise ImportError("transformers.Trainer unavailable in offline mode")

    def get_scheduler(*args: Any, **kwargs: Any) -> Any:  # pragma: no cover
        raise ImportError("transformers.optimization.get_scheduler unavailable in offline mode")


try:  # pragma: no cover - optional torch dependency
    import torch
except (ImportError, AttributeError):  # pragma: no cover - torch missing or stubbed out by tests
    import types

    def _noop(*args: Any, **kwargs: Any) -> None:  # pragma: no cover - fallback helper
        return None

    class _Generator:
        def manual_seed(self, *_args: Any, **_kwargs: Any) -> None:  # pragma: no cover
            return None

    torch = types.SimpleNamespace(  # type: ignore[assignment]
        manual_seed=_noop,
        use_deterministic_algorithms=_noop,
        float16="float16",
        bfloat16="bfloat16",
        Generator=_Generator,
        nn=types.SimpleNamespace(
            Module=object,
            functional=types.SimpleNamespace(
                cross_entropy=_noop,
            ),
            utils=types.SimpleNamespace(
                clip_grad_norm_=_noop,
            ),
        ),
        cuda=types.SimpleNamespace(
            is_available=lambda: False,
            manual_seed_all=_noop,
            device_count=lambda: 0,
        ),
        backends=types.SimpleNamespace(
            cudnn=types.SimpleNamespace(deterministic=False, benchmark=False)
        ),
        distributed=types.SimpleNamespace(
            is_available=lambda: False,
            is_initialized=lambda: False,
            init_process_group=_noop,
        ),
    )

# Lazy imports to break circular dependencies with codex_ml
# These are deferred to avoid circular import at module load time
split_dataset: Any = None
AsyncLogFile: Any = None
CodexLoggers: Any = None
_codex_log_all: Any = None
_codex_logging_bootstrap: Any = None
_codex_patch_argparse: Any = None
_codex_sample_system: Any = None
LogRecord: Any = None
apply_lora: Any = None
build_payload_bytes: Any = None
load_payload: Any = None
set_seed: Any = None
log_error: Any = None
ensure_pinned_kwargs: Any = None
load_from_pretrained: Any = None
snapshot_hydra_config: Any = None
set_reproducible: Any = None
safe_load: Any = None
log_env_info: Any = None
MissingPyYAMLError: Any = None
YAMLError: Any = None


def _ensure_hf_trainer_imports() -> None:
    """Lazy load imports needed for HF trainer, breaking circular dependencies."""
    global split_dataset
    global AsyncLogFile
    global CodexLoggers
    global _codex_log_all
    global _codex_logging_bootstrap
    global _codex_patch_argparse
    global _codex_sample_system
    global LogRecord
    global apply_lora
    global build_payload_bytes
    global load_payload
    global set_seed
    global log_error
    global ensure_pinned_kwargs
    global load_from_pretrained
    global snapshot_hydra_config
    global set_reproducible
    global safe_load
    global log_env_info
    global MissingPyYAMLError
    global YAMLError
    
    if split_dataset is not None:
        return  # Already loaded
    
    try:
        from codex_ml.data_utils import split_dataset as _split_dataset
        split_dataset = _split_dataset
    except (ImportError, AttributeError):
        pass
    
    try:
        from codex_ml.monitoring.async_writer import AsyncLogFile as _AsyncLogFile
        AsyncLogFile = _AsyncLogFile
    except (ImportError, AttributeError):
        pass
    
    try:
        from codex_ml.monitoring.codex_logging import (
            CodexLoggers as _CodexLoggers,
            _codex_log_all as _CODEX_LOG_ALL,
            _codex_logging_bootstrap as _CODEX_BOOTSTRAP,
            _codex_patch_argparse as _CODEX_PATCH,
            _codex_sample_system as _CODEX_SAMPLE,
        )
        CodexLoggers = _CodexLoggers
        _codex_log_all = _CODEX_LOG_ALL
        _codex_logging_bootstrap = _CODEX_BOOTSTRAP
        _codex_patch_argparse = _CODEX_PATCH
        _codex_sample_system = _CODEX_SAMPLE
    except (ImportError, AttributeError):
        CodexLoggers = None
        def _codex_log_all(*args, **kwargs):
            pass
        def _codex_logging_bootstrap(*args, **kwargs):
            return {}
        def _codex_patch_argparse(*args, **kwargs):
            pass
        def _codex_sample_system(*args, **kwargs):
            return {}
    
    try:
        from codex_ml.monitoring.schema import LogRecord as _LogRecord
        LogRecord = _LogRecord
    except (ImportError, AttributeError):
        pass
    
    try:
        from codex_ml.peft.peft_adapter import apply_lora as _apply_lora
        apply_lora = _apply_lora
    except (ImportError, AttributeError):
        pass
    
    try:
        from codex_ml.utils.checkpointing import (  # type: ignore[attr-defined]
            build_payload_bytes as _build_payload_bytes,
            load_payload as _load_payload,
            set_seed as _set_seed,
        )
        build_payload_bytes = _build_payload_bytes
        load_payload = _load_payload
        set_seed = _set_seed
    except (ImportError, AttributeError):
        pass
    
    try:
        from codex_ml.utils.error_log import log_error as _log_error
        log_error = _log_error
    except (ImportError, AttributeError):
        def log_error(*args, **kwargs):
            pass
    
    try:
        from codex_ml.utils.hf_pinning import (
            ensure_pinned_kwargs as _ensure_pinned_kwargs,
            load_from_pretrained as _load_from_pretrained,
        )
        ensure_pinned_kwargs = _ensure_pinned_kwargs
        load_from_pretrained = _load_from_pretrained
    except (ImportError, AttributeError):
        pass
    
    try:
        from codex_ml.utils.provenance import snapshot_hydra_config as _snapshot_hydra_config
        snapshot_hydra_config = _snapshot_hydra_config
    except (ImportError, AttributeError):
        pass
    
    try:
        from codex_ml.utils.repro import set_reproducible as _set_reproducible
        set_reproducible = _set_reproducible
    except (ImportError, AttributeError):
        pass
    
    try:
        from codex_ml.utils.yaml_support import safe_load as _safe_load, MissingPyYAMLError as _MissingPyYAMLError, YAMLError as _YAMLError
        safe_load = _safe_load
        MissingPyYAMLError = _MissingPyYAMLError
        YAMLError = _YAMLError
    except (ImportError, AttributeError):
        pass
    
    try:
        from codex_utils.repro import log_env_info as _log_env_info
        log_env_info = _log_env_info
    except (ImportError, AttributeError):
        def log_env_info(*args, **kwargs):
            pass


from omegaconf import OmegaConf

# Optional dependencies with graceful fallbacks
try:  # optional checkpoint callback
    from training.checkpoint_manager import CheckpointManager
except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover - missing in some envs
    CheckpointManager = None  # type: ignore[misc,assignment]
    if log_error is not None:
        log_error("checkpoint_import", str(exc), "src.training.checkpoint_manager")


try:  # Optional TensorBoard integration
    from tools.monitoring_integrate import SummaryWriter
except (IOError, OSError, ModuleNotFoundError, ImportError):  # pragma: no cover - optional dep
    SummaryWriter = None


try:  # Optional accelerate integration
    from accelerate import Accelerator as _Accelerator
except (IOError, OSError, ModuleNotFoundError, ImportError):  # pragma: no cover - optional dep
    _Accelerator = None


def _make_accelerator(**accelerate_kwargs: Any) -> Any:
    """Construct an Accelerator using the global compatibility shim."""
    if _Accelerator is None:
        return None
    return _Accelerator(**accelerate_kwargs)


_LOCAL_PATH_PREFIXES = ("./", "../", "/")


def _normalize_identifier(identifier: os.PathLike[str] | str | None) -> str | None:
    if identifier is None:
        return None
    if isinstance(identifier, os.PathLike):
        return os.fspath(identifier)
    return str(identifier)


def _maybe_import_mlflow() -> Any:
    if importlib.util.find_spec("mlflow") is None:
        return None
    return importlib.import_module("mlflow")


def _log_mlflow_metrics(
    metrics: Mapping[str, Any],
    training_args: TrainingArguments,
    *,
    model_name: str,
    tracking_uri: str | None,
    log_args: Optional[argparse.Namespace],
) -> None:
    mlflow_module = _maybe_import_mlflow()
    if mlflow_module is None:
        return
    enabled = bool(tracking_uri)
    if not enabled and log_args is not None:
        enabled = bool(getattr(log_args, "mlflow_enable", False))
    if not enabled:
        return
    resolved_uri = tracking_uri
    if resolved_uri is None and log_args is not None:
        resolved_uri = getattr(log_args, "mlflow_tracking_uri", None)
    run_name = model_name
    if log_args is not None:
        run_name = getattr(log_args, "mlflow_run_name", None) or run_name
    try:
        if resolved_uri:
            mlflow_module.set_tracking_uri(resolved_uri)
        experiment = None
        if log_args is not None:
            experiment = getattr(log_args, "mlflow_experiment", None)
        if experiment:
            mlflow_module.set_experiment(experiment)
        params = {
            "model_name": model_name,
            "per_device_train_batch_size": getattr(
                training_args, "per_device_train_batch_size", None
            ),
            "per_device_eval_batch_size": getattr(
                training_args, "per_device_eval_batch_size", None
            ),
            "learning_rate": getattr(training_args, "learning_rate", None),
            "num_train_epochs": getattr(training_args, "num_train_epochs", None),
            "gradient_accumulation_steps": getattr(
                training_args, "gradient_accumulation_steps", None
            ),
            "seed": getattr(training_args, "seed", None),
        }
        with mlflow_module.start_run(run_name=run_name):
            mlflow_module.log_params({k: v for k, v in params.items() if v is not None})
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    mlflow_module.log_metric(key, float(value))
    except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover - defensive logging
        type(exc).__name__
        print("[codex][mlflow] skipped logging: <ERROR_TYPE>")


def _looks_like_local_source(identifier: os.PathLike[str] | str | None) -> bool:
    norm = _normalize_identifier(identifier)
    if norm is None:
        return False
    if norm.startswith(_LOCAL_PATH_PREFIXES):
        return True
    try:
        return Path(norm).expanduser().exists()
    except OSError as e:
        type(e).__name__
        logger.debug("OSError: <ERROR_TYPE>")
        logger.warning("OSError: <ERROR_TYPE>", exc_info=True)
        return False


@cache
def get_hf_revision(identifier: os.PathLike[str] | str) -> str:
    """Resolve a pinned Hugging Face revision for ``identifier``.

    When ``HF_REVISION`` is provided it is validated and used, otherwise we fall
    back to :func:`ensure_pinned_kwargs` to source either
    ``CODEX_HF_REVISION`` or known pinned commits. This keeps the prior
    behaviour of allowing smoke-test identifiers without forcing a new
    environment variable while still ensuring remote downloads are immutable.
    """

    norm = _normalize_identifier(identifier)
    if not norm:
        raise RuntimeError("A remote Hugging Face identifier is required to resolve a revision.")

    overrides: dict[str, Any] = {}
    env_revision = os.environ.get("HF_REVISION")
    if env_revision:
        overrides["revision"] = env_revision
    try:
        revision, _ = ensure_pinned_kwargs(norm, overrides)
    except ValueError as exc:
        type(exc).__name__
        logger.debug("ValueError: <ERROR_TYPE>")
        if env_revision:
            raise RuntimeError("HF_REVISION must be set to an immutable commit hash") from exc
        raise RuntimeError(
            "Remote Hugging Face identifiers require a pinned commit hash. "
            "set CODEX_HF_REVISION or add the identifier to KNOWN_MODEL_REVISIONS."
        ) from exc

    if revision is None:
        raise RuntimeError(
            f"Identifier '{norm}' resolved to a local path; revision should not be requested."
        )
    return revision


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
) -> Trainer:
    """Construct a HF Trainer with optional early stopping and named LR scheduler."""
    if early_stop_patience:
        # Early stop needs a coherent best-model metric setup
        args.load_best_model_at_end = True
        if not getattr(args, "metric_for_best_model", None):
            args.metric_for_best_model = "eval_loss"
        if getattr(args, "greater_is_better", None) is None:
            # default for loss-like metrics
            args.greater_is_better = False
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
        if max_steps > 0:
            num_steps = max_steps
        elif steps_per_epoch:
            num_steps = int(args.num_train_epochs * steps_per_epoch)
        else:
            num_steps = None
        trainer.create_scheduler(num_training_steps=num_steps)
        if scheduler_name:
            training_steps = num_steps
            if training_steps is None and hasattr(train_ds, "__len__"):
                try:
                    training_steps = args.num_train_epochs * (len(train_ds) // batch_size + 1)
                except TypeError as e:
                    type(e).__name__
                    logger.debug("TypeError: <ERROR_TYPE>")
                    logger.warning("TypeError: <ERROR_TYPE>", exc_info=True)
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
    "CSVMetricsWriter",
    "HFTrainerConfig",
    "NDJSONMetricsWriter",
    "_compute_metrics",
    "_seed_everything",
    "_worker_init_fn",
    "build_parser",
    "build_trainer",
    "build_training_args",
    "load_training_arguments",
    "prepare_dataset",
    "run_hf_trainer",
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


def _compute_metrics(eval_pred) -> dict[str, float]:
    """Compute token accuracy and perplexity for evaluation.

    Parameters
    ----------
    eval_pred : tuple
        tuple of (predictions, labels) from evaluation

    Returns
    -------
    dict
        Dictionary containing token_accuracy and perplexity metrics
    """
    preds, labels = eval_pred

    mask = labels != -100
    acc = (preds.argmax(-1)[mask] == labels[mask]).mean() if mask.any() else 0.0
    loss = None
    try:
        logits = preds[mask]
        lbl = labels[mask]
        log_probs = logits - logits.max(axis=-1, keepdims=True)
        log_probs = log_probs - np.log(np.exp(log_probs).sum(axis=-1, keepdims=True))
        loss = float(-log_probs[np.arange(logits.shape[0]), lbl].mean())
    except (ValueError, TypeError, RuntimeError):
        logger.warning("Exception occurred", exc_info=True)
        loss = None
    ppl = float("inf") if loss is None or loss == 0 else math.exp(loss)
    return {"token_accuracy": float(acc), "perplexity": ppl}


def _seed_everything(seed: int = 42) -> None:
    """set deterministic seeds across all libraries.

    Parameters
    ----------
    seed : int, default=42
        Seed value for reproducibility
    """
    random.seed(seed)
    if np is not None:
        np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)  # For single GPU
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    if "CUBLAS_WORKSPACE_CONFIG" not in os.environ:
        os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":4096:8"
    try:
        torch.use_deterministic_algorithms(True)
    except RuntimeError as e:
        try:
            torch.use_deterministic_algorithms(True, warn_only=True)
        except (ValueError, TypeError, RuntimeError):
            logger.warning("Could not enable deterministic algorithms: %s", e)


def _worker_init_fn(worker_id) -> None:
    """Initialize worker with deterministic seed.

    Parameters
    ----------
    worker_id : int
        Worker process identifier
    """
    if np is None:
        return
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

    def write(self, obj: dict[str, Any] | LogRecord) -> None:
        """Write ``obj`` as a JSON line respecting the strict schema."""

        if isinstance(obj, LogRecord):
            data = obj.redacted().dict()
        else:
            try:
                import dataclasses as _dc

                valid_keys = {f.name for f in _dc.fields(LogRecord)}
                filtered = {k: v for k, v in obj.items() if k in valid_keys}
                data = LogRecord(**filtered).redacted().dict()
            except (IOError, OSError, ModuleNotFoundError, ImportError):
                logger.warning("Exception occurred", exc_info=True)
                data = obj
        if self._async is not None:
            self._async.write(data)
        else:
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=True) + "\n")

    def close(self) -> None:
        if self._async is not None:
            try:
                self._async.close()
            finally:
                self._async = None


class CSVMetricsWriter:
    """Persist metrics to CSV with stable columns."""

    def __init__(self, path: str = ".codex/metrics.csv") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._header: list[str] | None = None

    def write(self, obj: Mapping[str, Any] | LogRecord) -> None:
        row = obj.redacted().dict() if isinstance(obj, LogRecord) else dict(obj)
        new_keys = set(row)
        if self._header is None:
            self._header = sorted(new_keys)
            with self.path.open("w", encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=self._header, extrasaction="ignore")
                writer.writeheader()
                writer.writerow(row)
            return

        existing_keys = set(self._header)
        if new_keys - existing_keys:
            # Expand the header to accommodate new metrics and rewrite the CSV.
            self._header = sorted(existing_keys | new_keys)
            existing_rows: list[dict[str, Any]] = []
            with self.path.open("r", encoding="utf-8", newline="") as fh:
                reader = csv.DictReader(fh)
                existing_rows.extend(reader)
            existing_rows.append(row)
            with self.path.open("w", encoding="utf-8", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=self._header, extrasaction="ignore")
                writer.writeheader()
                for rec in existing_rows:
                    writer.writerow(rec)
            return

        with self.path.open("a", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=self._header, extrasaction="ignore")
            writer.writerow(row)

    def close(self) -> None:  # pragma: no cover - no persistent handles
        return None


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
    cfg: dict[str, object] = {}

    # Always honor user-provided config files, then layer Hydra overrides when supplied.
    if path is not None:
        if path.exists():
            loaded = OmegaConf.to_container(OmegaConf.load(path), resolve=True)
            if isinstance(loaded, dict):
                cfg.update(loaded)
        else:
            print(f"[warning] config {path} missing, using default training args")

    if hydra_cfg is not None:
        cfg.update(hydra_cfg)
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

    resolved_grad_accum: int | None = None
    if hydra_cfg:
        if "gradient_accumulation_steps" in hydra_cfg:
            resolved_grad_accum = hydra_cfg["gradient_accumulation_steps"]
        elif "grad_accum" in hydra_cfg:
            resolved_grad_accum = hydra_cfg["grad_accum"]
    if resolved_grad_accum is None:
        resolved_grad_accum = gradient_accumulation_steps
    try:
        resolved_grad_accum = int(resolved_grad_accum)
    except (TypeError, ValueError):
        resolved_grad_accum = int(gradient_accumulation_steps)
    if resolved_grad_accum < 1:
        resolved_grad_accum = 1
    cfg["gradient_accumulation_steps"] = resolved_grad_accum

    # Remove non-TrainingArguments keys from config
    for extra in (
        "batch_size",
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
        "grad_accum",
        "model",
        "device",
        "dtype",
        "deterministic",
        "sanitize_prompts",
        "optimizer",
        "scheduler",
        "mixed_precision",
        "tensorboard",
        "mlflow_enable",
        "max_epochs",
        "dataset",
        "checkpoint_every_n_steps",
        "checkpoint_keep",
        "eval_split",
        "gradient_accumulation",
    ):
        cfg.pop(extra, None)

    # Drop unsupported label smoothing when transformers is too old
    if "label_smoothing_factor" in cfg and _v(_hf_version) < _v("4.3.0"):
        cfg.pop("label_smoothing_factor")

    # Final safety net: strip any keys that TrainingArguments doesn't accept.
    # This guards against OmegaConf interpolation artefacts when Hydra's global
    # config store is active (e.g. after importing tokenization.cli in the same
    # pytest process), which can cause the resolved dict to include extra keys
    # not stripped by the main extras loop above.
    _KNOWN_EXTRAS = frozenset(
        {
            "batch_size",
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
            "grad_accum",
            "model",
            "device",
            "dtype",
            "deterministic",
            "sanitize_prompts",
            "optimizer",
            "scheduler",
            "mixed_precision",
            "tensorboard",
            "mlflow_enable",
            "max_epochs",
            "dataset",
            "checkpoint_every_n_steps",
            "checkpoint_keep",
            "eval_split",
            "gradient_accumulation",
        }
    )
    for _extra_key in _KNOWN_EXTRAS & set(cfg.keys()):
        cfg.pop(_extra_key, None)

    return TrainingArguments(**cfg)


def prepare_dataset(texts: Iterable[str], tokenizer) -> Dataset:
    """Tokenize an iterable of texts into a ``Dataset``."""
    ds = Dataset.from_dict({"text": list(texts)})
    ds = ds.map(lambda ex: tokenizer(ex["text"], truncation=True), batched=True)
    # Set format to torch tensors to ensure compatibility with HF Trainer data collator
    available_cols = [c for c in ["input_ids", "attention_mask"] if c in ds.column_names]
    ds.set_format(type="torch", columns=available_cols)
    return ds


def _sanitize_config_snapshot(cfg: Mapping[str, Any] | None) -> dict[str, Any] | None:
    """Convert a config mapping into JSON-safe primitives for manifest storage."""

    if cfg is None:
        return None

    def _convert(value: Any) -> Any:
        if isinstance(value, Mapping):
            return {str(k): _convert(v) for k, v in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [_convert(v) for v in value]
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return str(value)

    try:
        normalized = _convert(cfg)
    except (ValueError, TypeError, RuntimeError):
        logger.warning("Exception occurred", exc_info=True)
        return None
    return normalized if isinstance(normalized, dict) else None


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
    lora_task_type: Optional[str] = None,
    precision: Optional[str] = None,
    device: str = "auto",
    dtype: str = "fp32",
    deterministic: Optional[bool] = None,
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
    accelerate_kwargs: Optional[dict[str, object]] = None,
    hydra_cfg: Optional[dict[str, object]] = None,
    mlflow_tracking_uri: Optional[str] = None,
    log_args: Optional[argparse.Namespace] = None,
    metrics_writer: str = "ndjson",
    metrics_path: Optional[str] = None,
    sys_metrics: bool = False,
) -> dict[str, float]:
    """Train a causal LM using HuggingFace ``Trainer``."""
    # Ensure lazy imports are loaded before use
    _ensure_hf_trainer_imports()
    
    resolved_det = True if deterministic is None else bool(deterministic)

    # set deterministic seeds
    set_reproducible(seed, deterministic=resolved_det)
    set_seed(seed, output_dir, deterministic=resolved_det)
    if (
        resolved_det
        and torch.cuda.is_available()
        and getattr(torch.backends, "cudnn", None) is not None
        and getattr(torch.backends.cudnn, "enabled", False)
    ) and not torch.backends.cudnn.deterministic:
        raise AssertionError("cuDNN must be deterministic; call set_reproducible()")
    try:
        log_env_info(output_dir / "env.json")
    except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover - logging best effort
        log_error("env_log", str(exc), "env")
    try:
        snapshot_hydra_config({"model_name": model_name, "seed": seed}, output_dir)
    except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover - logging best effort
        log_error("hydra_snapshot", str(exc), "env")
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
    config_snapshot = _sanitize_config_snapshot(hydra_cfg)
    copied_resume_config: Path | None = None
    cfg: dict[str, object] = {}
    if config_path and config_path.exists():
        try:
            cfg = safe_load(config_path.read_text()) or {}
        except MissingPyYAMLError as exc:
            type(exc).__name__
            logger.debug("MissingPyYAMLError: <ERROR_TYPE>")
            raise RuntimeError(
                "PyYAML is required to parse training configs passed to EngineHfTrainer. "
                'Install it via ``pip install "PyYAML>=6.0"`` before retrying.'
            ) from exc
        except YAMLError as exc:
            type(exc).__name__
            logger.debug("YAMLError: <ERROR_TYPE>")
            raise RuntimeError(f"Failed to parse training config {config_path}: {exc}") from exc
        except (IOError, OSError, ModuleNotFoundError, ImportError):
            logger.warning("Exception occurred", exc_info=True)
            cfg = {}
        if config_snapshot is None and cfg:
            config_snapshot = _sanitize_config_snapshot(cfg)
    tokenizer_path = tokenizer_path or cast(Optional[str], cfg.get("tokenizer_path"))
    use_fast_tokenizer = cast(bool, cfg.get("use_fast_tokenizer", use_fast_tokenizer))
    tokenizer_name = tokenizer_name or cast(Optional[str], cfg.get("tokenizer_name")) or model_name
    source = tokenizer_path or tokenizer_name
    tokenizer_kwargs: dict[str, Any] = {"use_fast": use_fast_tokenizer}
    if not _looks_like_local_source(source):
        tokenizer_kwargs["revision"] = get_hf_revision(source)
    tokenizer = load_from_pretrained(
        AutoTokenizer,
        source,
        **tokenizer_kwargs,
    )
    if tokenizer.pad_token is None:
        logger.warning(
            "Tokenizer from '%s' has no pad_token; falling back to eos_token. "
            "This may affect training behaviour.",
            type(tokenizer).__name__,
        )
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
        model_kwargs: dict[str, Any] = {}
        if not _looks_like_local_source(model_name):
            model_kwargs["revision"] = get_hf_revision(model_name)
        model = load_from_pretrained(
            AutoModelForCausalLM,
            model_name,
            **model_kwargs,
        )

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

    set_reproducible(seed, deterministic=resolved_det)
    # Determine precision settings
    prec = effective_precision or ("bf16" if bf16 else ("fp16" if fp16 else None))
    resolved_accum = max(1, int(gradient_accumulation_steps))
    training_args = load_training_arguments(
        config_path,
        output_dir,
        prec if torch.cuda.is_available() else None,
        gradient_accumulation_steps=resolved_accum,
        tensorboard=tensorboard,
        has_eval=eval_ds is not None,
        hydra_cfg=hydra_cfg,
    )

    # Setup LoRA via adapter when requested, pulling defaults from Hydra config
    if hydra_cfg:
        # Support either flattened keys (lora_r) or a nested ``lora`` mapping
        lora_section: dict[str, Any] | None = None
        if isinstance(hydra_cfg.get("lora"), dict):
            lora_section = cast(dict[str, Any], hydra_cfg.get("lora"))
        else:
            lora_section = cast(dict[str, Any], hydra_cfg)
        if lora_section and lora_section.get("enabled", True):
            lora_r = lora_r or cast(
                Optional[int], lora_section.get("r") or lora_section.get("lora_r")
            )
            if lora_alpha is None:
                lora_alpha = cast(
                    Optional[int],
                    lora_section.get("alpha") or lora_section.get("lora_alpha"),
                )
            if lora_dropout is None:
                lora_dropout = cast(
                    Optional[float],
                    lora_section.get("dropout") or lora_section.get("lora_dropout"),
                )
            if lora_task_type is None:
                lora_task_type = cast(Optional[str], lora_section.get("task_type"))
    if lora_alpha is None:
        lora_alpha = 16
    if lora_r and getattr(training_args, "gradient_accumulation_steps", 1) != 1:
        warnings.warn(
            "LoRA is enabled but gradient_accumulation_steps!=1; overriding to 1",
            UserWarning,
            stacklevel=2,
        )
        training_args.gradient_accumulation_steps = 1
    if lora_r:
        try:
            cfg = {"r": int(lora_r), "lora_alpha": int(lora_alpha)}
            if lora_dropout is not None:
                cfg["lora_dropout"] = float(lora_dropout)
            if lora_task_type:
                cfg["task_type"] = str(lora_task_type)
            model = apply_lora(model, cfg)
        except (ValueError, TypeError, RuntimeError) as exc:
            type(exc).__name__
            logger.debug("Exception: <ERROR_TYPE>")
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

            class _CheckpointCallback(TrainerCallback):
                def __init__(self) -> None:
                    self.model = None
                    self.optimizer = None
                    self.lr_scheduler = None
                    self.scaler = None
                    self._logs: dict[str, float] | None = None

                def on_train_begin(self, args, state, control, **kwargs) -> None:
                    self.model = kwargs.get("model")
                    self.optimizer = kwargs.get("optimizer")
                    self.lr_scheduler = kwargs.get("lr_scheduler")
                    self.scaler = kwargs.get("scaler")
                    return control

                def on_log(self, args, state, control, logs=None, **kwargs) -> None:
                    self._logs = dict(logs or {})
                    return control

                def on_step_end(self, args, state, control, **kwargs) -> None:
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
        except (ConnectionError, TimeoutError) as exc:
            type(exc).__name__
            logger.debug("Exception: <ERROR_TYPE>")
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
            except (IOError, OSError, ModuleNotFoundError, ImportError) as exc:  # pragma: no cover - bootstrap is best-effort
                type(exc).__name__
                print("[telemetry] bootstrap skipped: <ERROR_TYPE>")

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
            train_dl = trainer.get_train_dataloader()  # type: ignore[func-returns-value]
            steps_per_epoch = math.ceil(len(train_dl) / training_args.gradient_accumulation_steps)  # type: ignore[arg-type]
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
        except (ValueError, TypeError) as exc:  # pragma: no cover - resume best effort
            type(exc).__name__
            print(f"Failed to load checkpoint {custom_resume}: <ERROR_TYPE>")
        resume_ckpt = None

    # Train with optional checkpoint resumption
    result = trainer.train(resume_from_checkpoint=str(resume_ckpt) if resume_ckpt else None)  # type: ignore[func-returns-value]
    trainer.save_model()

    # Collect metrics
    metrics = dict(result.metrics)  # type: ignore[attr-defined]
    if eval_ds is not None:
        eval_metrics = trainer.evaluate()  # type: ignore[func-returns-value]
        metrics.update({f"eval_{k}": v for k, v in eval_metrics.items()})  # type: ignore[attr-defined]
    metrics.setdefault("global_step", trainer.state.global_step)

    # Codex offline logging
    if sys_metrics:
        try:
            sysd = _codex_sample_system()
            log_vals = {
                **{k: v for k, v in metrics.items() if isinstance(v, (int, float))},
                **sysd,
            }
            _codex_log_all(int(metrics.get("global_step", 0)), log_vals, loggers)
        except (IOError, OSError, ModuleNotFoundError, ImportError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning(
                f"Exception: {e}", exc_info=True
            )  # Logging failure; continue with training

    # TensorBoard logging
    if tensorboard and SummaryWriter is not None:
        try:
            writer = SummaryWriter(log_dir=str(output_dir / "tensorboard"))
            for k, v in metrics.items():
                if isinstance(v, (int, float)):
                    writer.add_scalar(k, v, trainer.state.global_step)
            writer.flush()
            writer.close()
        except (IOError, OSError, ModuleNotFoundError, ImportError) as e:
            type(e).__name__
            logger.debug("Exception: <ERROR_TYPE>")
            logger.warning(
                f"Exception: {e}", exc_info=True
            )  # TensorBoard logging failure; continue with training

    # Persist metrics to JSON and NDJSON for downstream analytics
    metrics_json = output_dir / "metrics.json"
    with metrics_json.open("w", encoding="utf-8") as fh:
        json.dump(metrics, fh)
    record = dict(metrics)
    record["ts"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    writer_choice = (metrics_writer or "ndjson").lower()
    if writer_choice != "none":
        path = (
            Path(metrics_path)
            if metrics_path
            else output_dir / ("metrics.csv" if writer_choice == "csv" else "metrics.ndjson")
        )
        if writer_choice == "csv":
            writer_obj: CSVMetricsWriter | NDJSONMetricsWriter = CSVMetricsWriter(str(path))
        else:
            writer_obj = NDJSONMetricsWriter(str(path))
        writer_obj.write(record)
        if hasattr(writer_obj, "close"):
            writer_obj.close()

    if config_path and config_path.exists():
        suffix = config_path.suffix or ".yaml"
        target_path = output_dir / f"resume_config{suffix}"
        try:
            if config_path.resolve() != target_path.resolve():
                target_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(config_path, target_path)
            copied_resume_config = target_path
        except (IOError, OSError, ModuleNotFoundError, ImportError):
            logger.warning("Exception occurred", exc_info=True)
            copied_resume_config = None

    manifest = {
        "manifest_version": 1,
        "checkpoint_dir": str(checkpoint_dir) if checkpoint_dir else None,
        "last_checkpoint": getattr(trainer.state, "last_model_checkpoint", None),
        "best_checkpoint": getattr(trainer.state, "best_model_checkpoint", None),
        "global_step": int(trainer.state.global_step),
        "resume_from": str(resume_ckpt) if resume_ckpt else None,
        "config_path": str(config_path) if config_path else None,
        "copied_config_path": str(copied_resume_config) if copied_resume_config else None,
        "config": config_snapshot,
    }
    (output_dir / "resume_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )

    _log_mlflow_metrics(
        metrics,
        training_args,
        model_name=model_name,
        tracking_uri=mlflow_tracking_uri,
        log_args=log_args,
    )

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
    add(
        "--lora-task-type",
        type=str,
        default=None,
        help="LoRA task type (e.g., CAUSAL_LM, SEQ_CLS)",
    )
    add(
        "--metrics-writer",
        choices=["ndjson", "csv", "none"],
        default="ndjson",
        help="Persist metrics to NDJSON (default), CSV, or disable persistence.",
    )
    add(
        "--metrics-path",
        type=str,
        default=None,
        help="Optional custom path for metrics output (overrides default file name).",
    )
    add(
        "--sys-metrics",
        action="store_true",
        help="Enable CPU/GPU/system metrics sampling and structured logging.",
    )
    return _codex_patch_argparse(parser)

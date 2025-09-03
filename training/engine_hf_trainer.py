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

import argparse
import json
import math
import os
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional

import numpy as np
import torch
import yaml
from datasets import Dataset
from packaging.version import parse as _v
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)
from transformers import __version__ as _hf_version

from codex_ml.monitoring.codex_logging import (
    CodexLoggers,
    _codex_log_all,
    _codex_logging_bootstrap,
    _codex_patch_argparse,
    _codex_sample_system,
)
from codex_ml.peft.peft_adapter import apply_lora
from codex_ml.utils.checkpointing import set_seed
from codex_ml.utils.error_log import log_error
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

__all__ = [
    "run_hf_trainer",
    "HFTrainerConfig",
    "build_training_args",
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

    Parameters
    ----------
    path : str, default=".codex/metrics.ndjson"
        Output path for metrics file
    """

    def __init__(self, path: str = ".codex/metrics.ndjson"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, obj: dict):
        """Write a dictionary as a JSON line.

        Parameters
        ----------
        obj : dict
            Dictionary to write as JSON
        """
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")


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
    lora_alpha : int
        LoRA alpha parameter
    precision : str, optional
        Precision setting override
    gradient_accumulation_steps : int
        Gradient accumulation steps
    checkpoint_dir : Path, optional
        Directory for checkpoints
    save_steps : int
        Steps between saves
    """

    model_name: str = "sshleifer/tiny-gpt2"
    tokenizer_name: Optional[str] = None
    config_path: Optional[Path] = None
    fp16: bool = False
    bf16: bool = False
    lora_r: Optional[int] = None
    lora_alpha: int = 16
    precision: Optional[str] = None
    gradient_accumulation_steps: int = 1
    checkpoint_dir: Optional[Path] = None
    save_steps: int = 100


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
    """Load ``TrainingArguments`` from YAML and apply runtime overrides.

    Parameters
    ----------
    path : Path, optional
        Path to YAML configuration file
    output_dir : Path
        Output directory for training
    precision : str, optional
        Precision setting ("fp16" or "bf16")
    gradient_accumulation_steps : int, default=1
        Gradient accumulation steps
    tensorboard : bool, default=False
        Enable TensorBoard logging
    has_eval : bool, default=False
        Whether evaluation dataset is provided
    hydra_cfg : dict, optional
        Hydra configuration dictionary for parameter overrides

    Returns
    -------
    TrainingArguments
        Configured training arguments
    """
    cfg: Dict[str, object] = {}
    # Load base config from Hydra when provided
    if hydra_cfg is not None:
        cfg.update(hydra_cfg)
    elif path is not None and path.exists():
        cfg.update(yaml.safe_load(path.read_text()))
    cfg.setdefault("output_dir", str(output_dir))
    cfg["output_dir"] = str(output_dir)

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
        "precision",
        "checkpoint_dir",
        "model_name",
        "tokenizer_name",
        "epochs",
        "val_split",
        "test_split",
        "logging",
        "checkpoint",
    ):
        cfg.pop(extra, None)

    # Drop unsupported label smoothing when transformers is too old
    if "label_smoothing_factor" in cfg and _v(_hf_version) < _v("4.3.0"):
        cfg.pop("label_smoothing_factor")

    return TrainingArguments(**cfg)


def prepare_dataset(texts: Iterable[str], tokenizer) -> Dataset:
    """Tokenize an iterable of texts into a ``Dataset``.

    Parameters
    ----------
    texts : Iterable[str]
        Text strings to tokenize
    tokenizer : transformers.PreTrainedTokenizer
        Tokenizer to use for encoding

    Returns
    -------
    Dataset
        Tokenized dataset ready for training
    """
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
    config_path: Optional[Path] = None,
    fp16: bool = False,
    bf16: bool = False,
    lora_r: Optional[int] = None,
    lora_alpha: int = 16,
    precision: Optional[str] = None,
    device: str = "auto",
    dtype: str = "fp32",
    gradient_accumulation_steps: int = 1,
    checkpoint_dir: Optional[Path] = None,
    save_steps: int = 100,
    seed: int = 0,
    resume_from: Optional[str] = None,
    val_texts: Optional[Iterable[str]] = None,
    distributed: bool = True,
    tensorboard: bool = False,
    log_args: Optional[argparse.Namespace] = None,
) -> Dict[str, float]:
    """Train a causal LM using HuggingFace ``Trainer``.

    Parameters
    ----------
    texts : Iterable[str]
        Iterable of raw text strings to train on.
    output_dir : Path
        Directory to place checkpoints and trainer state.
    model : torch.nn.Module, optional
        Optional model. If ``None``, ``model_name`` is loaded via ``AutoModelForCausalLM``.
    model_name : str, default="sshleifer/tiny-gpt2"
        Model name or path used when ``model`` is ``None``.
    tokenizer_name : str, optional
        Tokenizer name or path. Defaults to ``model_name`` if ``None``.
    config_path : Path, optional
        Path to YAML file defining ``TrainingArguments``.
    fp16 : bool, default=False
        Backwards compatibility flag for half precision. Use ``precision``.
    bf16 : bool, default=False
        Backwards compatibility flag for bfloat16 precision. Use ``precision``.
    lora_r : int, optional
        Rank for LoRA adapters; if ``None`` LoRA is disabled.
    lora_alpha : int, default=16
        Alpha for LoRA adapters.
    precision : str, optional
        One of {"fp32","fp16","bf16"}. Overrides ``fp16`` and ``bf16`` when provided.
    device : str, default="auto"
        ``"cpu"``, ``"cuda"`` or ``"auto"`` to infer.
    dtype : str, default="fp32"
        Numerical precision for model parameters.
    gradient_accumulation_steps : int, default=1
        Number of gradient accumulation steps.
    checkpoint_dir : Path, optional
        Directory for periodic checkpoints when provided.
    save_steps : int, default=100
        Interval of steps between checkpoint saves.
    seed : int, default=0
        RNG seed applied across libraries and recorded to ``seeds.json``.
    resume_from : str, optional
        Path to checkpoint for resuming training.
    val_texts : Iterable[str], optional
        Optional iterable of validation texts. Enables per-epoch evaluation.
    distributed : bool, default=True
        Enable multi-GPU training via ``torch.distributed``. Requires NCCL and driver support when using CUDA. Set to ``False`` to disable.
    tensorboard : bool, default=False
        If ``True``, log final metrics to TensorBoard when available.
    log_args : argparse.Namespace, optional
        Logging configuration arguments.

    Returns
    -------
    Dict[str, float]
        Training metrics returned by ``Trainer.train``.
    """
    # Set deterministic seeds
    set_reproducible(seed)
    set_seed(seed, output_dir)
    log_env_info(output_dir / "env.json")
    resume_ckpt: Optional[Path] = None
    if resume_from:
        ckpt = Path(resume_from)
        if ckpt.exists():
            print(f"Resuming from checkpoint {ckpt}")
            resume_ckpt = ckpt

    # Setup tokenizer
    tokenizer_name = tokenizer_name or model_name
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Prepare datasets
    ds = prepare_dataset(texts, tokenizer)
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
    )

    # Setup LoRA via adapter when requested
    if lora_r:
        try:
            model = apply_lora(model, {"r": int(lora_r), "lora_alpha": int(lora_alpha)})
        except Exception as exc:
            log_error("lora_import", str(exc), "peft")

    # Setup checkpoint callbacks
    callbacks = None
    if checkpoint_dir and CheckpointManager is not None:
        try:
            manager = CheckpointManager(Path(checkpoint_dir), save_steps)
            callbacks = [manager.callback()]
        except Exception as exc:
            log_error("checkpoint_init", str(exc), str(checkpoint_dir))

    # Initialize logging
    loggers: CodexLoggers = _codex_logging_bootstrap(log_args or argparse.Namespace())

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
    NDJSONMetricsWriter(str(output_dir / "metrics.ndjson")).write(record)

    return metrics


def build_parser() -> argparse.ArgumentParser:
    """Build a parser including monitoring flags.

    Returns
    -------
    argparse.ArgumentParser
        Configured argument parser with monitoring integration
    """
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
    return _codex_patch_argparse(parser)

"""Minimal HuggingFace Trainer wrapper.

This module provides a thin convenience around ``transformers.Trainer``
for causal language modeling. It supports training either a pretrained
``AutoModelForCausalLM`` or a user supplied ``torch.nn.Module`` using a
``DataCollatorForLanguageModeling`` compatible collator.

Multi-GPU setups are enabled automatically when multiple CUDA devices are
available and ``torch.distributed`` is installed. NCCL is required for the
backend when GPUs are used. Set ``distributed=False`` to disable distributed
initialisation.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional

import torch
import yaml
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)

from codex_ml.utils.checkpointing import set_seed

try:  # Optional TensorBoard integration
    from tools.monitoring_integrate import SummaryWriter  # type: ignore
except Exception:  # pragma: no cover - optional dep
    SummaryWriter = None


def _compute_metrics(eval_pred):
    """Compute token accuracy and perplexity for evaluation."""
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


@dataclass
class HFTrainerConfig:
    """Configuration for the HuggingFace Trainer."""

    model_name: str = "sshleifer/tiny-gpt2"
    tokenizer_name: Optional[str] = None
    config_path: Optional[Path] = None
    fp16: bool = False


def load_training_arguments(
    path: Optional[Path],
    output_dir: Path,
    fp16: bool,
    *,
    tensorboard: bool = False,
    has_eval: bool = False,
) -> TrainingArguments:
    """Load ``TrainingArguments`` from YAML and apply runtime overrides."""

    cfg: Dict[str, object] = {}
    if path is not None and path.exists():
        cfg = yaml.safe_load(path.read_text())
    cfg.setdefault("output_dir", str(output_dir))
    cfg["output_dir"] = str(output_dir)
    if fp16:
        cfg["fp16"] = True
    if tensorboard:
        cfg.setdefault("report_to", ["tensorboard"])
        cfg.setdefault("logging_dir", str(output_dir / "tensorboard"))
    if has_eval:
        cfg.setdefault("evaluation_strategy", "epoch")
        cfg.setdefault("logging_strategy", "epoch")
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
    config_path: Optional[Path] = None,
    fp16: bool = False,
    seed: int = 0,
    val_texts: Optional[Iterable[str]] = None,
    distributed: bool = True,
    tensorboard: bool = False,
) -> Dict[str, float]:
    """Train a causal LM using HuggingFace ``Trainer``.

    Parameters
    ----------
    texts:
        Iterable of raw text strings to train on.
    output_dir:
        Directory to place checkpoints and trainer state.
    model:
        Optional ``torch.nn.Module``. If ``None``, ``model_name`` is loaded
        via ``AutoModelForCausalLM``.
    model_name:
        Model name or path used when ``model`` is ``None``.
    tokenizer_name:
        Tokenizer name or path. Defaults to ``model_name`` if ``None``.
    config_path:
        Path to YAML file defining ``TrainingArguments``.
    fp16:
        If ``True`` and CUDA is available, enable half precision training.
    seed:
        RNG seed applied across libraries and recorded to ``seeds.json``.
    val_texts:
        Optional iterable of validation texts. Enables per-epoch evaluation.
    distributed:
        Enable multi-GPU training via ``torch.distributed``. Requires NCCL and driver support when using CUDA. Set to ``False`` to disable.
    tensorboard:
        If ``True``, log final metrics to TensorBoard when available.

    Returns
    -------
    Dict[str, float]
        Training metrics returned by ``Trainer.train``.
    """

    set_seed(seed, output_dir)

    tokenizer_name = tokenizer_name or model_name
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    ds = prepare_dataset(texts, tokenizer)
    eval_ds = (
        prepare_dataset(val_texts, tokenizer) if val_texts is not None else None
    )
    collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    if model is None:
        model = AutoModelForCausalLM.from_pretrained(model_name)

    if no_ddp:
        os.environ["CUDA_VISIBLE_DEVICES"] = ""

    # Multi-GPU support
    if (
        distributed
        and torch.cuda.device_count() > 1
        and torch.distributed.is_available()
    ):
        backend = "nccl" if torch.cuda.is_available() else "gloo"
        if not torch.distributed.is_initialized():
            torch.distributed.init_process_group(backend=backend)
        print(
            f"Using torch.distributed with backend={backend} for {torch.cuda.device_count()} GPUs"
        )

    training_args = load_training_arguments(
        config_path,
        output_dir,
        fp16 and torch.cuda.is_available(),
        tensorboard=tensorboard,
        has_eval=eval_ds is not None,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ds,
        eval_dataset=eval_ds,
        data_collator=collator,
        eval_dataset=val_ds,
        compute_metrics=_compute_metrics if val_ds is not None else None,
    )
    result = trainer.train()
    trainer.save_model()
    metrics = dict(result.metrics)
    if eval_ds is not None:
        eval_metrics = trainer.evaluate()
        metrics.update({f"eval_{k}": v for k, v in eval_metrics.items()})
    metrics.setdefault("global_step", trainer.state.global_step)

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

    return metrics


__all__ = ["run_hf_trainer", "HFTrainerConfig"]

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

import argparse
import importlib
import json
import math
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional

import numpy as np
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

from codex_ml.monitoring.codex_logging import (
    CodexLoggers,
    _codex_log_all,
    _codex_logging_bootstrap,
    _codex_patch_argparse,
    _codex_sample_system,
)
from codex_ml.utils.checkpointing import set_seed
from codex_ml.utils.error_log import log_error

try:  # optional checkpoint callback
    from training.checkpoint_manager import CheckpointManager
except Exception as exc:  # pragma: no cover - missing in some envs
    CheckpointManager = None  # type: ignore[assignment]
    log_error("checkpoint_import", str(exc), "training.checkpoint_manager")

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



def _seed_everything(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True)


def _worker_init_fn(worker_id):
    s = np.random.SeedSequence(42)
    np.random.seed(s.generate_state(1, dtype=np.uint32)[0] + worker_id)


class NDJSONMetricsWriter:
    def __init__(self, path: str = ".codex/metrics.ndjson"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, obj: dict):
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")

@dataclass
class HFTrainerConfig:
    """Configuration for the HuggingFace Trainer."""

    model_name: str = "sshleifer/tiny-gpt2"
    tokenizer_name: Optional[str] = None
    config_path: Optional[Path] = None
    fp16: bool = False
    lora_r: Optional[int] = None
    lora_alpha: int = 16
    precision: Optional[str] = None
    checkpoint_dir: Optional[Path] = None
    save_steps: int = 100


def load_training_arguments(
    path: Optional[Path],
    output_dir: Path,
    precision: Optional[str],
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
    lora_r: Optional[int] = None,
    lora_alpha: int = 16,
    precision: Optional[str] = None,
    checkpoint_dir: Optional[Path] = None,
    save_steps: int = 100,
    seed: int = 0,
    val_texts: Optional[Iterable[str]] = None,
    distributed: bool = True,
    tensorboard: bool = False,
    log_args: Optional[argparse.Namespace] = None,
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
        Backwards compatibility flag for half precision. Use ``precision``.
    lora_r:
        Rank for LoRA adapters; if ``None`` LoRA is disabled.
    lora_alpha:
        Alpha for LoRA adapters.
    precision:
        One of {"fp32","fp16","bf16"}. Overrides ``fp16`` when provided.
    checkpoint_dir:
        Directory for periodic checkpoints when provided.
    save_steps:
        Interval of steps between checkpoint saves.
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
    eval_ds = prepare_dataset(val_texts, tokenizer) if val_texts is not None else None
    collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    if model is None:
        model = AutoModelForCausalLM.from_pretrained(model_name)

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

    prec = precision or ("fp16" if fp16 else None)
    training_args = load_training_arguments(
        config_path,
        output_dir,
        prec if torch.cuda.is_available() else None,
        tensorboard=tensorboard,
        has_eval=eval_ds is not None,
    )

    if lora_r:
        try:
            peft = importlib.import_module("peft")
            LoraConfig = getattr(peft, "LoraConfig")
            get_peft_model = getattr(peft, "get_peft_model")
            config = LoraConfig(r=int(lora_r), lora_alpha=int(lora_alpha), task_type="CAUSAL_LM")
            model = get_peft_model(model, config)
        except Exception as exc:
            log_error("lora_import", str(exc), "peft")

    callbacks = None
    if checkpoint_dir and CheckpointManager is not None:
        try:
            manager = CheckpointManager(Path(checkpoint_dir), save_steps)
            callbacks = [manager.callback()]
        except Exception as exc:
            log_error("checkpoint_init", str(exc), str(checkpoint_dir))

    loggers: CodexLoggers = _codex_logging_bootstrap(log_args or argparse.Namespace())

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ds,
        eval_dataset=eval_ds,
        data_collator=collator,
        compute_metrics=_compute_metrics if eval_ds is not None else None,
        callbacks=callbacks,
    )
    result = trainer.train()
    trainer.save_model()
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


__all__ = ["run_hf_trainer", "HFTrainerConfig", "_seed_everything", "_worker_init_fn", "NDJSONMetricsWriter"]


def build_parser() -> argparse.ArgumentParser:
    """Build a parser including monitoring flags."""

    parser = argparse.ArgumentParser(description="HF Trainer")
    return _codex_patch_argparse(parser)

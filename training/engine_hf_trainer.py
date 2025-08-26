"""Minimal HuggingFace Trainer wrapper.

This module provides a thin convenience around ``transformers.Trainer``
for causal language modeling. It supports training either a pretrained
``AutoModelForCausalLM`` or a user supplied ``torch.nn.Module`` using a
``DataCollatorForLanguageModeling`` compatible collator.

Multi-GPU setups are enabled automatically when multiple CUDA devices are
available and ``torch.distributed`` is installed. NCCL is required for the
backend when GPUs are used.
"""

from __future__ import annotations

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


@dataclass
class HFTrainerConfig:
    """Configuration for the HuggingFace Trainer."""

    model_name: str = "sshleifer/tiny-gpt2"
    tokenizer_name: Optional[str] = None
    config_path: Optional[Path] = None
    fp16: bool = False


def load_training_arguments(
    path: Optional[Path], output_dir: Path, fp16: bool
) -> TrainingArguments:
    """Load ``TrainingArguments`` from YAML, overriding ``output_dir`` and ``fp16``."""

    cfg: Dict[str, object] = {}
    if path is not None and path.exists():
        cfg = yaml.safe_load(path.read_text())
    cfg.setdefault("output_dir", str(output_dir))
    cfg["output_dir"] = str(output_dir)
    if fp16:
        cfg["fp16"] = True
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
    collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    if model is None:
        model = AutoModelForCausalLM.from_pretrained(model_name)

    # Multi-GPU support
    if torch.cuda.device_count() > 1 and torch.distributed.is_available():
        backend = "nccl" if torch.cuda.is_available() else "gloo"
        if not torch.distributed.is_initialized():
            torch.distributed.init_process_group(backend=backend)
        print(
            f"Using torch.distributed with backend={backend} for {torch.cuda.device_count()} GPUs"
        )

    training_args = load_training_arguments(
        config_path, output_dir, fp16 and torch.cuda.is_available()
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=ds,
        data_collator=collator,
    )
    result = trainer.train()
    trainer.save_model()
    metrics = dict(result.metrics)
    metrics.setdefault("global_step", trainer.state.global_step)
    return metrics


__all__ = ["run_hf_trainer", "HFTrainerConfig"]

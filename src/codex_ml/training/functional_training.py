"""Simple fallback training loop for Codex models.

This module implements a minimal causal language model trainer for use
when the HuggingFace Trainer is unavailable or when running in a resource-
constrained environment.  It accepts raw text, tokenizes it using an
``AutoTokenizer``, and trains an ``AutoModelForCausalLM`` (or a provided
``torch.nn.Module``) with a standard cross-entropy loss.  A validation
split is optional, and metrics such as token accuracy and perplexity are
logged at the end of each epoch.

The loop supports gradient accumulation, deterministic seeding and
checkpoint saving via ``codex_ml.utils.checkpointing``.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional

from codex_ml.models.utils.peft import apply_lora_if_available
from codex_ml.utils.checkpointing import save_checkpoint
from codex_ml.utils.hf_pinning import load_from_pretrained
from codex_ml.utils.hf_revision import get_hf_revision
from codex_ml.utils.logging_mlflow import mlflow_run
from codex_ml.utils.optional import optional_import
from codex_ml.utils.provenance import export_environment
from codex_ml.utils.seeding import set_reproducible
from codex_ml.utils.train_helpers import clip_gradients, get_amp_scaler, maybe_autocast

torch, _HAS_TORCH = optional_import("torch")
transformers, _HAS_TRANSFORMERS = optional_import("transformers")
if _HAS_TRANSFORMERS:
    AutoModelForCausalLM = transformers.AutoModelForCausalLM  # type: ignore[attr-defined]
    AutoTokenizer = transformers.AutoTokenizer  # type: ignore[attr-defined]
else:  # pragma: no cover - optional dependency
    AutoModelForCausalLM = None  # type: ignore[assignment]
    AutoTokenizer = None  # type: ignore[assignment]


@dataclass
class TrainConfig:
    model_name: str = "sshleifer/tiny-gpt2"
    epochs: int = 1
    batch_size: int = 32
    lr: float = 5e-5
    seed: int = 0
    gradient_accumulation_steps: int = 1
    max_length: int = 512
    checkpoint_dir: Optional[str] = None
    tensorboard: bool = False
    mlflow_enable: bool = False
    amp_enable: bool = False
    amp_dtype: Optional[str] = None
    grad_clip_norm: Optional[float] = None
    lora_enable: bool = False
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05


def train(
    texts: Iterable[str],
    *,
    config: TrainConfig,
    val_texts: Optional[Iterable[str]] = None,
    model: Optional[torch.nn.Module] = None,
) -> dict[str, float]:
    """Train a causal language model on raw ``texts``.

    Args:
        texts: Iterable of training strings.
        config: Training hyper-parameters.
        val_texts: Optional iterable of validation strings.
        model: Optional ``torch.nn.Module``.  If ``None`` an ``AutoModelForCausalLM``
            is loaded from ``config.model_name``.

    Returns:
        A dictionary of final metrics (token accuracy and perplexity).
    """
    if not (_HAS_TORCH and _HAS_TRANSFORMERS):
        raise ImportError("torch and transformers are required for training")

    # Deterministic seeding
    set_reproducible(config.seed)

    # Load tokenizer and model
    tokenizer = load_from_pretrained(
        AutoTokenizer,
        config.model_name,
        revision=get_hf_revision(),
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = model or load_from_pretrained(
        AutoModelForCausalLM,
        config.model_name,
        revision=get_hf_revision(),
    )
    model.train()

    if config.lora_enable:
        model = apply_lora_if_available(
            model,
            r=config.lora_r,
            alpha=config.lora_alpha,
            dropout=config.lora_dropout,
        )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=config.lr)

    checkpoint_root: Optional[Path] = None
    if config.checkpoint_dir:
        checkpoint_root = Path(config.checkpoint_dir)
        checkpoint_root.mkdir(parents=True, exist_ok=True)
        export_environment(
            checkpoint_root / "provenance",
            seed=config.seed,
            command="train.functional",
        )

    writer = None
    if config.tensorboard:
        try:
            from torch.utils.tensorboard import SummaryWriter  # type: ignore

            tb_base = (
                (checkpoint_root / "tensorboard")
                if checkpoint_root is not None
                else Path("tensorboard")
            )
            tb_base.mkdir(parents=True, exist_ok=True)
            writer = SummaryWriter(log_dir=str(tb_base))
        except Exception:
            writer = None

    scaler = get_amp_scaler(config.amp_enable)

    # Tokenize the entire dataset once for simplicity
    def _prepare(batch_texts: Iterable[str]):
        enc = tokenizer(
            list(batch_texts),
            padding="max_length",
            truncation=True,
            max_length=config.max_length,
            return_tensors="pt",
        )
        return enc["input_ids"], enc["attention_mask"]

    train_ids, _ = _prepare(texts)
    val_ids, _ = _prepare(val_texts) if val_texts is not None else (None, None)

    optimizer.zero_grad(set_to_none=True)

    mlf_params: Dict[str, object] = {
        "model_name": config.model_name,
        "lr": float(config.lr),
        "batch_size": int(config.batch_size),
        "epochs": int(config.epochs),
        "amp": bool(config.amp_enable),
        "amp_dtype": config.amp_dtype,
        "grad_clip_norm": config.grad_clip_norm,
        "lora": bool(config.lora_enable),
    }

    global_step = 0
    num_batches = math.ceil(len(train_ids) / config.batch_size)

    with mlflow_run(enabled=config.mlflow_enable, params=mlf_params):
        for epoch in range(config.epochs):
            perm = list(range(len(train_ids)))
            random.shuffle(perm)
            for b in range(num_batches):
                start = b * config.batch_size
                end = start + config.batch_size
                idx = perm[start:end]
                batch = train_ids[idx].to(device)
                labels = batch.clone()
                with maybe_autocast(enabled=config.amp_enable, dtype=config.amp_dtype):
                    outputs = model(batch, labels=labels)
                    loss = outputs.loss / config.gradient_accumulation_steps
                scaled_loss = scaler.scale(loss)
                scaled_loss.backward()
                should_step = (b + 1) % config.gradient_accumulation_steps == 0
                if should_step:
                    scaler.unscale_(optimizer)
                    if config.grad_clip_norm:
                        clip_gradients(model.parameters(), float(config.grad_clip_norm))
                    scaler.step(optimizer)
                    scaler.update()
                    optimizer.zero_grad(set_to_none=True)

                global_step += 1
                if writer is not None:
                    try:
                        loss_value = float(loss.detach().cpu().item())
                        writer.add_scalar("train/loss", loss_value, global_step)
                    except Exception:
                        pass

            if checkpoint_root is not None:
                ckpt_path = checkpoint_root / f"epoch-{epoch}.pt"
                save_checkpoint(str(ckpt_path), model, optimizer, None, epoch, {})

    # Compute simple metrics on training set
    with torch.no_grad():
        model.eval()
        train_tensor = train_ids.to(device)
        with maybe_autocast(enabled=config.amp_enable, dtype=config.amp_dtype):
            logits = model(train_tensor).logits
        preds = logits.argmax(dim=-1)
        mask = train_tensor != tokenizer.pad_token_id
        acc = (preds[mask] == train_tensor[mask]).float().mean().item()
        loss_fn = torch.nn.CrossEntropyLoss(ignore_index=tokenizer.pad_token_id)
        with maybe_autocast(enabled=config.amp_enable, dtype=config.amp_dtype):
            train_loss_tensor = loss_fn(
                logits.view(-1, model.config.vocab_size),
                train_tensor.view(-1),
            )
        loss_val = float(train_loss_tensor.detach().cpu().item())
        ppl = math.exp(loss_val) if loss_val > 0 else float("inf")
        metrics = {"token_accuracy": acc, "perplexity": ppl}
        if val_ids is not None:
            val_tensor = val_ids.to(device)
            with maybe_autocast(enabled=config.amp_enable, dtype=config.amp_dtype):
                val_logits = model(val_tensor).logits
            val_preds = val_logits.argmax(dim=-1)
            val_mask = val_tensor != tokenizer.pad_token_id
            metrics["val_token_accuracy"] = (
                (val_preds[val_mask] == val_tensor[val_mask]).float().mean().item()
            )
            with maybe_autocast(enabled=config.amp_enable, dtype=config.amp_dtype):
                val_loss_tensor = loss_fn(
                    val_logits.view(-1, model.config.vocab_size),
                    val_tensor.view(-1),
                )
            val_loss = float(val_loss_tensor.detach().cpu().item())
            metrics["val_perplexity"] = (
                math.exp(val_loss) if val_loss > 0 else float("inf")
            )
            if writer is not None:
                try:
                    writer.add_scalar(
                        "val/perplexity", float(metrics["val_perplexity"]), global_step
                    )
                except Exception:
                    pass

    if writer is not None:
        try:
            writer.flush()
            writer.close()
        except Exception:
            pass
    return metrics

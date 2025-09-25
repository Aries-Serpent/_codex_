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
from typing import Iterable, Optional

from codex_ml.utils.checkpointing import save_checkpoint
from codex_ml.utils.hf_pinning import load_from_pretrained
from codex_ml.utils.hf_revision import get_hf_revision
from codex_ml.utils.optional import optional_import
from codex_ml.utils.provenance import export_environment
from codex_ml.utils.seeding import set_reproducible

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

    num_batches = math.ceil(len(train_ids) / config.batch_size)
    for epoch in range(config.epochs):
        perm = list(range(len(train_ids)))
        random.shuffle(perm)
        for b in range(num_batches):
            start = b * config.batch_size
            end = start + config.batch_size
            idx = perm[start:end]
            batch = train_ids[idx].to(device)
            # Labels are the inputs shifted left by one token
            labels = batch.clone()
            outputs = model(batch, labels=labels)
            loss = outputs.loss / config.gradient_accumulation_steps
            loss.backward()
            if (b + 1) % config.gradient_accumulation_steps == 0:
                optimizer.step()
                optimizer.zero_grad()
        # Save checkpoint at epoch end
        if checkpoint_root is not None:
            ckpt_path = checkpoint_root / f"epoch-{epoch}.pt"
            save_checkpoint(str(ckpt_path), model, optimizer, None, epoch, {})

    # Compute simple metrics on training set
    with torch.no_grad():
        model.eval()
        preds = model(train_ids.to(device)).logits.argmax(dim=-1)
        mask = train_ids != tokenizer.pad_token_id
        acc = (preds[mask] == train_ids.to(device)[mask]).float().mean().item()
        loss_fn = torch.nn.CrossEntropyLoss(ignore_index=tokenizer.pad_token_id)
        loss_val = loss_fn(
            model(train_ids.to(device)).logits.view(-1, model.config.vocab_size),
            train_ids.to(device).view(-1),
        ).item()
        ppl = math.exp(loss_val) if loss_val > 0 else float("inf")
        metrics = {"token_accuracy": acc, "perplexity": ppl}
        if val_ids is not None:
            val_preds = model(val_ids.to(device)).logits.argmax(dim=-1)
            val_mask = val_ids != tokenizer.pad_token_id
            metrics["val_token_accuracy"] = (
                (val_preds[val_mask] == val_ids.to(device)[val_mask]).float().mean().item()
            )
            val_loss = loss_fn(
                model(val_ids.to(device)).logits.view(-1, model.config.vocab_size),
                val_ids.to(device).view(-1),
            ).item()
            metrics["val_perplexity"] = math.exp(val_loss) if val_loss > 0 else float("inf")
    return metrics

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import torch
from torch.nn.utils import clip_grad_norm_
from torch.utils.data import DataLoader

from codex_ml.monitoring.codex_logging import (
    CodexLoggers,
    _codex_log_all,
    _codex_logging_bootstrap,
)
from codex_ml.utils.checkpointing import load_checkpoint, save_checkpoint, set_seed

try:  # optional LoRA support
    from peft import LoraConfig, get_peft_model  # type: ignore
except Exception:  # pragma: no cover - optional
    LoraConfig = None  # type: ignore
    get_peft_model = None  # type: ignore

from training.engine_hf_trainer import _compute_metrics


def _worker_init_fn(worker_id: int) -> None:
    """Initialise worker seed deterministically."""
    seed = torch.initial_seed() % 2**32
    np.random.seed(seed + worker_id)


@dataclass
class TrainCfg:
    epochs: int = 1
    batch_size: int = 8
    grad_accum: int = 1
    lr: float = 5e-4
    weight_decay: float = 0.0
    warmup_steps: int = 0
    max_steps: Optional[int] = None
    max_grad_norm: Optional[float] = 1.0
    dtype: str = "fp32"  # fp32|fp16|bf16
    log_every: int = 50
    save_every: int = 500
    patience: int = 100
    seed: int = 42
    resume_from: Optional[str] = None
    checkpoint_dir: str = "checkpoints"
    use_lora: bool = False
    device: Optional[str] = None
    limit_train_batches: Optional[int] = None
    limit_val_batches: Optional[int] = None


def run_custom_trainer(model, tokenizer, train_ds, val_ds, cfg: TrainCfg) -> Dict[str, Any]:
    """Train ``model`` on ``train_ds`` using a minimal deterministic loop."""

    device = torch.device(cfg.device or ("cuda" if torch.cuda.is_available() else "cpu"))
    model.to(device)
    set_seed(cfg.seed)
    loggers: CodexLoggers = _codex_logging_bootstrap(argparse.Namespace())

    if cfg.use_lora and LoraConfig and get_peft_model:
        try:
            lcfg = LoraConfig(r=4, lora_alpha=16, lora_dropout=0.0, bias="none")
            model = get_peft_model(model, lcfg)
        except Exception:
            pass

    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    scheduler = None
    if cfg.warmup_steps and cfg.max_steps:

        def lr_lambda(step: int) -> float:
            if step < cfg.warmup_steps:
                return step / float(max(1, cfg.warmup_steps))
            return max(
                0.0, (cfg.max_steps - step) / float(max(1, cfg.max_steps - cfg.warmup_steps))
            )

        scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

    start_epoch = 0
    global_step = 0
    best_val = float("inf")
    if cfg.resume_from:
        try:
            start_epoch, extra = load_checkpoint(cfg.resume_from, model, optimizer, scheduler)
            global_step = int(extra.get("global_step", 0))
            best_val = float(extra.get("best_val", best_val))
        except Exception:
            pass

    train_loader = DataLoader(
        train_ds,
        batch_size=cfg.batch_size,
        shuffle=True,
        drop_last=True,
        pin_memory=torch.cuda.is_available(),
        worker_init_fn=_worker_init_fn,
        generator=torch.Generator().manual_seed(cfg.seed),
    )
    val_loader = None
    if val_ds is not None:
        val_loader = DataLoader(
            val_ds,
            batch_size=cfg.batch_size,
            shuffle=False,
            drop_last=False,
            pin_memory=torch.cuda.is_available(),
            worker_init_fn=_worker_init_fn,
            generator=torch.Generator().manual_seed(cfg.seed),
        )

    use_amp = cfg.dtype in {"fp16", "bf16"} and torch.cuda.is_available()
    scaler = torch.cuda.amp.GradScaler(enabled=cfg.dtype == "fp16")
    autocast_dtype = {
        "fp16": torch.float16,
        "bf16": torch.bfloat16,
    }.get(cfg.dtype, torch.float32)

    history: list[float] = []
    patience_ctr = 0
    for epoch in range(start_epoch, cfg.epochs):
        model.train()
        optimizer.zero_grad(set_to_none=True)
        for step, batch in enumerate(train_loader):
            if cfg.limit_train_batches and step >= cfg.limit_train_batches:
                break
            for k, v in batch.items():
                batch[k] = v.to(device)
            with torch.autocast(device_type=device.type, dtype=autocast_dtype, enabled=use_amp):
                out = model(**batch)
                loss = out["loss"] if isinstance(out, dict) else out.loss
                loss = loss / cfg.grad_accum
            if cfg.dtype == "fp16":
                scaler.scale(loss).backward()
            else:
                loss.backward()
            if (step + 1) % cfg.grad_accum == 0:
                if cfg.max_grad_norm is not None:
                    if cfg.dtype == "fp16":
                        scaler.unscale_(optimizer)
                    clip_grad_norm_(model.parameters(), cfg.max_grad_norm)
                if cfg.dtype == "fp16":
                    scaler.step(optimizer)
                    scaler.update()
                else:
                    optimizer.step()
                optimizer.zero_grad(set_to_none=True)
                global_step += 1
                if scheduler:
                    scheduler.step()
                if global_step % cfg.log_every == 0:
                    loss_val = float(loss.detach().cpu().item() * cfg.grad_accum)
                    history.append(loss_val)
                    try:
                        _codex_log_all(global_step, {"train_loss": loss_val}, loggers)
                    except Exception:
                        print(f"step {global_step}: loss {loss_val:.4f}")
                if cfg.save_every and global_step % cfg.save_every == 0:
                    ckpt = Path(cfg.checkpoint_dir) / f"step{global_step}.pt"
                    save_checkpoint(
                        ckpt,
                        model,
                        optimizer,
                        scheduler,
                        epoch,
                        {"global_step": global_step, "best_val": best_val},
                    )
                if cfg.max_steps and global_step >= cfg.max_steps:
                    break
        if cfg.max_steps and global_step >= cfg.max_steps:
            break
        if val_loader is not None:
            model.eval()
            preds = []
            labels = []
            with torch.no_grad():
                for j, vb in enumerate(val_loader):
                    if cfg.limit_val_batches and j >= cfg.limit_val_batches:
                        break
                    for k, v in vb.items():
                        vb[k] = v.to(device)
                    outputs = model(**vb)
                    logits = outputs["logits"] if isinstance(outputs, dict) else outputs.logits
                    preds.append(logits.cpu().numpy())
                    labels.append(vb["labels"].cpu().numpy())
            if preds and labels:
                metrics = _compute_metrics((np.concatenate(preds), np.concatenate(labels)))
                val_ppl = metrics.get("perplexity", float("inf"))
                if val_ppl < best_val:
                    best_val = val_ppl
                    patience_ctr = 0
                    ckpt = Path(cfg.checkpoint_dir) / "best.pt"
                    save_checkpoint(
                        ckpt,
                        model,
                        optimizer,
                        scheduler,
                        epoch,
                        {"global_step": global_step, "best_val": best_val},
                    )
                else:
                    patience_ctr += 1
                if patience_ctr >= cfg.patience:
                    break
    return {"global_step": global_step, "history": history, "best_val": best_val}


def main(*cli_args: str) -> None:  # pragma: no cover - simple CLI wrapper
    parser = argparse.ArgumentParser(description="Custom training loop")
    parser.add_argument("texts", nargs="+", help="Inline training texts")
    parser.add_argument("--epochs", type=int, default=1)
    args = parser.parse_args(list(cli_args))

    from codex_ml.models import MiniLM, MiniLMConfig
    from training.data_utils import TextDataset, split_texts

    class _Tok:
        def __init__(self) -> None:
            self.vocab: Dict[str, int] = {}

        def encode(self, txt: str) -> list[int]:
            ids = []
            for tok in txt.split():
                if tok not in self.vocab:
                    self.vocab[tok] = len(self.vocab)
                ids.append(self.vocab[tok])
            return ids

    tokenizer = _Tok()
    train_txt, val_txt = split_texts(args.texts, seed=0)
    # prime vocab
    for t in train_txt + val_txt:
        tokenizer.encode(t)
    model = MiniLM(MiniLMConfig(vocab_size=len(tokenizer.vocab)))
    train_ds = TextDataset(train_txt, tokenizer, block_size=16)
    val_ds = TextDataset(val_txt, tokenizer, block_size=16)
    cfg = TrainCfg(epochs=args.epochs, log_every=1)
    run_custom_trainer(model, tokenizer, train_ds, val_ds, cfg)


if __name__ == "__main__":  # pragma: no cover
    main()

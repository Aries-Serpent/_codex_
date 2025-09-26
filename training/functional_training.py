from __future__ import annotations

# ruff: noqa: I001

import argparse
import os
from os import PathLike
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

import numpy as np

import torch
from torch.nn.utils import clip_grad_norm_
from torch.utils.data import DataLoader

# optional dependencies -----------------------------------------------------
try:  # pragma: no cover - optional config dependency
    from omegaconf import DictConfig, OmegaConf  # type: ignore
except Exception:  # pragma: no cover - omegaconf not installed
    DictConfig = Any  # type: ignore
    OmegaConf = None  # type: ignore

try:  # pragma: no cover - optional logging dependency
    from codex_ml.monitoring.codex_logging import (
        CodexLoggers,
        _codex_log_all,
        _codex_logging_bootstrap,
    )
except Exception:  # pragma: no cover - monitoring module missing
    CodexLoggers = Any  # type: ignore

    def _codex_log_all(*args: Any, **kwargs: Any) -> None:  # type: ignore
        """Fallback no-op logger when monitoring is unavailable."""

    def _codex_logging_bootstrap(*args: Any, **kwargs: Any) -> Dict[str, Any]:  # type: ignore
        return {}


try:  # pragma: no cover - optional model registry
    from codex_ml.models.registry import get_model
except Exception:  # pragma: no cover - minimal training may not need registry

    def get_model(*args: Any, **kwargs: Any):  # type: ignore
        raise RuntimeError("codex_ml.models.registry is unavailable")


from codex_ml.telemetry import EXAMPLES_PROCESSED, TRAIN_STEP_DURATION, track_time
from codex_ml.utils.hf_pinning import ensure_pinned_kwargs, load_from_pretrained
from codex_ml.utils.checkpointing import (
    dump_rng_state,
    load_rng_state,
    load_training_checkpoint,
    save_checkpoint,
    set_seed,
)

try:  # pragma: no cover - optional HF trainer helpers
    from training.engine_hf_trainer import _compute_metrics, get_hf_revision, run_hf_trainer
except Exception:  # pragma: no cover - hf trainer not available

    def run_hf_trainer(*args: Any, **kwargs: Any) -> None:  # type: ignore
        raise RuntimeError("HuggingFace trainer is unavailable")

    def _compute_metrics(*args: Any, **kwargs: Any) -> Dict[str, float]:  # type: ignore
        return {}

    def get_hf_revision(identifier: PathLike[str] | str) -> str:
        norm = os.fspath(identifier) if isinstance(identifier, PathLike) else str(identifier)
        overrides: Dict[str, Any] = {}
        env_revision = os.environ.get("HF_REVISION")
        if env_revision:
            overrides["revision"] = env_revision
        try:
            revision, _ = ensure_pinned_kwargs(norm, overrides)
        except ValueError as exc:  # pragma: no cover - environment misconfiguration
            if env_revision:
                raise RuntimeError("HF_REVISION must be set to an immutable commit hash") from exc
            raise
        if revision is None:
            raise RuntimeError("Expected a remote identifier when resolving HF revision")
        return revision


_LOCAL_PATH_PREFIXES = ("./", "../", "/")


def _normalize_identifier(identifier: PathLike[str] | str | None) -> str | None:
    if identifier is None:
        return None
    if isinstance(identifier, PathLike):
        return os.fspath(identifier)
    return str(identifier)


def _looks_like_local_source(identifier: PathLike[str] | str | None) -> bool:
    norm = _normalize_identifier(identifier)
    if norm is None:
        return False
    if norm.startswith(_LOCAL_PATH_PREFIXES):
        return True
    try:
        return Path(norm).expanduser().exists()
    except OSError:
        return False


try:  # optional LoRA support
    from peft import LoraConfig, get_peft_model  # type: ignore
except Exception:  # pragma: no cover - optional
    LoraConfig = None  # type: ignore
    get_peft_model = None  # type: ignore


def main(argv: Sequence[str] | None = None) -> int:
    """Training orchestrator entry point.

    Loads configuration via load_training_cfg, prepares datasets and dispatches
    to either the HuggingFace trainer or a minimal custom loop depending on --engine.
    """
    from codex_ml.utils.config_loader import load_training_cfg  # local import

    parser = argparse.ArgumentParser(description="Training orchestrator entry.")
    parser.add_argument("--engine", choices=["hf", "custom"], default="hf")
    parser.add_argument("--texts", nargs="*", help="Training texts (overrides cfg.training.texts)")
    parser.add_argument("--val-texts", nargs="*", default=None)
    parser.add_argument("--output-dir", type=Path, default=Path("training_runs"))
    parser.add_argument(
        "--cfg-override",
        dest="overrides",
        nargs="*",
        default=None,
        help="Hydra-style overrides for load_training_cfg",
    )
    parser.add_argument("--lora-r", type=int, default=None, help="LoRA rank parameter")
    parser.add_argument("--lora-alpha", type=int, default=None, help="LoRA alpha parameter")
    parser.add_argument("--lora-dropout", type=float, default=None, help="LoRA dropout rate")
    args = parser.parse_args(list(argv) if argv is not None else None)

    cfg: DictConfig = load_training_cfg(allow_fallback=True, overrides=args.overrides)
    # Flatten training.* into top-level dict for hydra_cfg propagation
    training_cfg: Dict[str, Any] = OmegaConf.to_container(cfg, resolve=True)  # type: ignore[assignment]
    nested = training_cfg.pop("training", {})
    if isinstance(nested, dict):
        training_cfg.update(nested)

    texts = args.texts or training_cfg.get("texts")
    if not texts:
        parser.error("Provide training texts via --texts or config.training.texts")
    val_texts = args.val_texts or training_cfg.get("val_texts")
    seed = int(training_cfg.get("seed", 0))

    if args.engine == "hf":
        # Prepare keyword args and propagate hydra_cfg for downstream compatibility
        kw: Dict[str, Any] = {"hydra_cfg": training_cfg, "seed": seed}
        for key in ("gradient_accumulation_steps", "precision"):
            if key in training_cfg:
                kw[key] = training_cfg[key]
        lora_cfg = training_cfg.get("lora")
        if isinstance(lora_cfg, dict) and lora_cfg.get("enable"):
            kw["lora_r"] = lora_cfg.get("r")
            kw["lora_alpha"] = lora_cfg.get("alpha", 16)
            kw["lora_dropout"] = lora_cfg.get("dropout")
        if args.lora_r is not None:
            kw["lora_r"] = args.lora_r
        if args.lora_alpha is not None:
            kw["lora_alpha"] = args.lora_alpha
        if args.lora_dropout is not None:
            kw["lora_dropout"] = args.lora_dropout
        run_hf_trainer(texts, args.output_dir, val_texts=val_texts, **kw)
    else:
        # Minimal custom path that mirrors HF inputs and labels suitable for CausalLM
        from datasets import Dataset  # type: ignore
        from transformers import AutoTokenizer  # type: ignore

        model_cfg = training_cfg.get(
            "model",
            {"name": training_cfg.get("model_name", "sshleifer/tiny-gpt2")},
        )
        model = get_model(model_cfg.get("name", "MiniLM"), model_cfg)
        tok_name = model_cfg.get("pretrained_model_name_or_path") or model_cfg.get("name")
        tokenizer_kwargs: Dict[str, Any] = {}
        if not _looks_like_local_source(tok_name):
            tokenizer_kwargs["revision"] = get_hf_revision(tok_name)
        tokenizer = load_from_pretrained(
            AutoTokenizer,
            tok_name,
            **tokenizer_kwargs,
        )
        if getattr(tokenizer, "pad_token", None) is None:
            tokenizer.pad_token = tokenizer.eos_token

        tokenized = tokenizer(list(texts), padding=True, return_tensors="pt")
        tokenized["labels"] = tokenized["input_ids"].clone()
        tokenized["labels"][tokenized["attention_mask"] == 0] = -100
        tokenized_np = {k: v.numpy() for k, v in tokenized.items()}
        train_ds = Dataset.from_dict(tokenized_np)

        val_ds = None
        if val_texts:
            val_tok = tokenizer(list(val_texts), padding=True, return_tensors="pt")
            val_tok["labels"] = val_tok["input_ids"].clone()
            val_tok["labels"][val_tok["attention_mask"] == 0] = -100
            val_ds = Dataset.from_dict({k: v.numpy() for k, v in val_tok.items()})

        train_kwargs = {
            f: training_cfg.get(f, getattr(TrainCfg, f)) for f in TrainCfg.__annotations__
        }
        lora_cfg = training_cfg.get("lora", {})
        train_kwargs["use_lora"] = bool(lora_cfg.get("enable", train_kwargs.get("use_lora")))
        train_kwargs["lora_r"] = lora_cfg.get("r", train_kwargs.get("lora_r"))
        train_kwargs["lora_alpha"] = lora_cfg.get("alpha", train_kwargs.get("lora_alpha"))
        train_kwargs["lora_dropout"] = lora_cfg.get("dropout", train_kwargs.get("lora_dropout"))
        train_cfg = TrainCfg(**train_kwargs)
        run_custom_trainer(model, tokenizer, train_ds, val_ds, train_cfg)
    return 0


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
    lora_r: int = 4
    lora_alpha: int = 16
    lora_dropout: float = 0.0
    device: Optional[str] = None
    limit_train_batches: Optional[int] = None
    limit_val_batches: Optional[int] = None
    dp_enabled: bool = False
    dp_noise_multiplier: float = 1.0
    dp_max_grad_norm: float = 1.0
    dp_target_delta: float = 1e-5


def evaluate_dataloader(model, dataloader, cfg: TrainCfg, device: torch.device) -> dict[str, float]:
    """Evaluate ``model`` on ``dataloader`` while aggregating metrics offline."""

    if dataloader is None:
        return {}

    was_training = model.training
    model.eval()
    preds: list[np.ndarray] = []
    labels: list[np.ndarray] = []
    batch_count = 0

    with torch.no_grad():
        for j, batch in enumerate(dataloader):
            if cfg.limit_val_batches and j >= cfg.limit_val_batches:
                break
            for key, value in batch.items():
                batch[key] = value.to(device)
            outputs = model(**batch)
            logits = outputs["logits"] if isinstance(outputs, dict) else outputs.logits
            preds.append(logits.detach().cpu().numpy())
            labels.append(batch["labels"].detach().cpu().numpy())
            batch_count += 1

    metrics: dict[str, float] = {"num_batches": float(batch_count)}
    if preds and labels:
        metrics.update(_compute_metrics((np.concatenate(preds), np.concatenate(labels))))

    if was_training:
        model.train()

    return metrics


def run_custom_trainer(model, tokenizer, train_ds, val_ds, cfg: TrainCfg) -> Dict[str, Any]:
    """Train ``model`` on ``train_ds`` using a minimal deterministic loop."""
    device = torch.device(cfg.device or ("cuda" if torch.cuda.is_available() else "cpu"))
    model.to(device)
    set_seed(cfg.seed)
    if device.type == "cuda" and cfg.dtype in {"fp32", "fp16", "bf16"}:
        assert (
            torch.backends.cudnn.deterministic
        ), "cuDNN must be deterministic; call set_reproducible()"
    loggers: CodexLoggers = _codex_logging_bootstrap(argparse.Namespace())

    if cfg.use_lora and LoraConfig and get_peft_model:
        try:
            lcfg = LoraConfig(
                r=cfg.lora_r,
                lora_alpha=cfg.lora_alpha,
                lora_dropout=cfg.lora_dropout,
                bias="none",
            )
            model = get_peft_model(model, lcfg)
        except Exception:
            pass

    optimizer = torch.optim.AdamW(model.parameters(), lr=cfg.lr, weight_decay=cfg.weight_decay)
    scheduler = None
    if cfg.warmup_steps and cfg.max_steps is not None:
        max_steps = cfg.max_steps

        def lr_lambda(step: int) -> float:
            if step < cfg.warmup_steps:
                return step / float(max(1, cfg.warmup_steps))
            return max(0.0, (max_steps - step) / float(max(1, max_steps - cfg.warmup_steps)))

        scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

    start_epoch = 0
    global_step = 0
    best_val = float("inf")
    start_step = 0
    if cfg.resume_from:
        try:
            state = load_training_checkpoint(cfg.resume_from, model, optimizer, scheduler)
            start_epoch = int(state.get("epoch") or 0)
            extra = state.get("extra", {})
            global_step = int(extra.get("global_step", 0))
            best_val = float(extra.get("best_val", best_val))
            start_step = int(extra.get("step_in_epoch", 0))
            if rng := extra.get("rng_state"):
                load_rng_state(rng)
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

    privacy_engine = None
    if cfg.dp_enabled:
        try:
            from opacus import PrivacyEngine  # type: ignore

            privacy_engine = PrivacyEngine()
            model, optimizer, train_loader = privacy_engine.make_private(
                module=model,
                optimizer=optimizer,
                data_loader=train_loader,
                noise_multiplier=cfg.dp_noise_multiplier,
                max_grad_norm=cfg.dp_max_grad_norm,
            )
        except Exception:
            privacy_engine = None

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
            if epoch == start_epoch and step < start_step:
                continue
            if cfg.limit_train_batches and step >= cfg.limit_train_batches:
                break

            @track_time(TRAIN_STEP_DURATION)
            def _step() -> float:
                for k, v in batch.items():
                    batch[k] = v.to(device)
                with torch.autocast(device_type=device.type, dtype=autocast_dtype, enabled=use_amp):
                    out = model(**batch)
                    loss_t = out["loss"] if isinstance(out, dict) else out.loss
                    loss_t = loss_t / cfg.grad_accum
                if cfg.dtype == "fp16":
                    scaler.scale(loss_t).backward()
                else:
                    loss_t.backward()
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
                return float(loss_t.detach())

            loss = _step()
            if EXAMPLES_PROCESSED:
                first = next(iter(batch.values()))
                EXAMPLES_PROCESSED.inc(int(getattr(first, "shape", [0])[0]))
            global_step += 1
            if scheduler:
                scheduler.step()
            if global_step % cfg.log_every == 0:
                loss_val = float(loss * cfg.grad_accum)
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
                    {
                        "global_step": global_step,
                        "best_val": best_val,
                        "step_in_epoch": step + 1,
                        "rng_state": dump_rng_state(),
                    },
                )
            if cfg.max_steps and global_step >= cfg.max_steps:
                break
        if cfg.max_steps and global_step >= cfg.max_steps:
            break
        if epoch == start_epoch:
            start_step = 0
        if val_loader is not None:
            metrics = evaluate_dataloader(model, val_loader, cfg, device)
            if metrics:
                numeric_metrics = {
                    f"val_{k}": float(v)
                    for k, v in metrics.items()
                    if isinstance(v, (int, float))
                }
                if numeric_metrics:
                    try:
                        _codex_log_all(global_step, numeric_metrics, loggers)
                    except Exception:
                        pass
            val_ppl = float(metrics.get("perplexity", float("inf")))
            if metrics.get("num_batches", 0) > 0 and val_ppl < best_val:
                best_val = val_ppl
                patience_ctr = 0
                ckpt = Path(cfg.checkpoint_dir) / "best.pt"
                save_checkpoint(
                    ckpt,
                    model,
                    optimizer,
                    scheduler,
                    epoch,
                    {
                        "global_step": global_step,
                        "best_val": best_val,
                        "step_in_epoch": 0,
                        "rng_state": dump_rng_state(),
                    },
                )
            else:
                patience_ctr += 1
            if patience_ctr >= cfg.patience:
                break
        if privacy_engine is not None:
            try:
                eps, _ = privacy_engine.get_privacy_spent(cfg.dp_target_delta)
                _codex_log_all(global_step, {"epsilon": float(eps)}, loggers)
            except Exception:
                pass
    return {"global_step": global_step, "history": history, "best_val": best_val}

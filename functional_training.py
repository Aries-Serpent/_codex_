# [Script]: functional_training.py
# > Generated: 2025-08-26 06:29:37 | Author: mbaetiong
"""Convenience wrapper around the symbolic pipeline with optional tokenization."""

# ruff: noqa: I001

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import torch
import torch.nn.functional as F
from torch.nn.utils import clip_grad_norm_

from codex_ml.models import MiniLM, MiniLMConfig
from codex_ml.monitoring.codex_logging import CodexLoggers, _codex_log_all, _codex_logging_bootstrap
from codex_ml.monitoring.codex_logging import _codex_patch_argparse as _codex_monitor_patch_argparse
from codex_ml.monitoring.codex_logging import _codex_sample_system
from codex_ml.symbolic_pipeline import (
    PretrainCfg,
    RewardModelCfg,
    RLHFCfg,
    SFTCfg,
    Weights,
    run_codex_symbolic_pipeline,
)
from codex_ml.tokenization import TokenizerAdapter, load_tokenizer
from codex_ml.utils.checkpointing import CheckpointManager, set_seed

try:  # Optional TensorBoard integration
    from tools.monitoring_integrate import SummaryWriter  # type: ignore
except Exception:  # pragma: no cover - optional dep
    SummaryWriter = None


# ---- Codex validation metrics helpers ----
def _codex_config_hash(d: Dict[str, Any]) -> str:
    """Return a stable SHA256 hash for a config dictionary."""
    blob = json.dumps(d, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def emit_validation_metric_record(path: str, payload: Dict[str, Any]) -> None:
    """Append a single validation metric record to ``path`` as NDJSON."""
    payload = dict(payload)
    payload.setdefault("ts", datetime.utcnow().isoformat() + "Z")
    cfg = payload.pop("config", {})
    payload.setdefault("split", "val")
    payload.setdefault("notes", "functional_training/_run_minilm_training")
    payload["config_hash"] = _codex_config_hash(cfg if isinstance(cfg, dict) else {"cfg": cfg})
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _safe_token_accuracy(y_true, y_pred) -> float:
    try:
        n = min(len(y_true), len(y_pred))
        if n == 0:
            return 0.0
        match = sum(1 for i in range(n) if y_true[i] == y_pred[i])
        return match / float(n)
    except Exception:
        return 0.0


def _safe_perplexity(nll_values) -> float:
    import math

    try:
        vals = list(nll_values)
        if not vals:
            return float("inf")
        mean = sum(vals) / float(len(vals))
        return float(math.exp(max(0.0, mean)))
    except Exception:
        return float("inf")


try:  # Attempt to import metrics; fall back to safe implementations
    from codex_ml.metrics import perplexity, token_accuracy
except Exception:  # pragma: no cover - fallback if metrics module missing

    def _fallback_perplexity(nll):
        """Simple perplexity wrapper used when metrics module is unavailable."""

        return _safe_perplexity(nll if hasattr(nll, "__iter__") else [nll])

    perplexity = _fallback_perplexity
    token_accuracy = _safe_token_accuracy


def run_functional_training(
    corpus: List[str],
    demos: List[Dict[str, Any]],
    prefs: List[tuple[str, str, str, int]],
    *,
    tokenizer_name: Optional[str] = None,
    tokenizer_path: Optional[str] = None,
    tokenizer: Optional[TokenizerAdapter] = None,
    weights: Weights = Weights(),
    pre_cfg: PretrainCfg = PretrainCfg(),
    sft_cfg: SFTCfg = SFTCfg(),
    rm_cfg: RewardModelCfg = RewardModelCfg(),
    rlhf_cfg: RLHFCfg = RLHFCfg(),
    use_deeplearning: bool = False,
    seed: int = 0,
    device: Optional[str] = None,
    grad_clip: Optional[float] = None,
    grad_accum: int = 1,
    precision: str = "fp32",
    # Accept both legacy boolean and new string-based scheduler identifiers:
    # - True behaves like "steplr"
    # - None/False disables scheduler
    scheduler: Optional[Union[bool, str]] = None,
    checkpoint_dir: Optional[str] = None,
    resume_from: Optional[str] = None,
    keep_last: int = 5,
    keep_best: int = 1,
    tensorboard: bool = False,
    val_split: float = 0.10,
    test_split: float = 0.0,
    monitoring_args: Optional[argparse.Namespace] = None,
    # LoRA hyper-parameters (optional)
    lora_r: int = 8,
    lora_alpha: int = 16,
    lora_dropout: float = 0.05,
    lora_bias: str = "none",
) -> Dict[str, Any]:
    """Run training pipeline, optionally using a tiny Torch model.

    When use_deeplearning is False, this routes to the symbolic pipeline.

    Args:
        corpus: List of raw training texts.
        demos: SFT demonstrations (symbolic pipeline).
        prefs: Preference data (symbolic pipeline).
        tokenizer_name: Optional tokenizer name to load.
        tokenizer_path: Optional tokenizer path to load.
        tokenizer: Pre-loaded tokenizer adapter.
        weights: Symbolic pipeline weights.
        pre_cfg, sft_cfg, rm_cfg, rlhf_cfg: Pipeline configs.
        use_deeplearning: Use tiny MiniLM demo trainer if True.
        seed: RNG seed applied across libraries.
        device: Torch device (e.g., "cuda", "cpu").
        grad_clip: Optional gradient clipping norm.
        grad_accum: Steps for gradient accumulation.
        precision: Training precision ('fp32', 'fp16', 'bf16').
        scheduler: Optional scheduler selector ("steplr") or legacy bool.
        checkpoint_dir: Directory for checkpoints and metrics.
        resume_from: Optional checkpoint to resume from.
        keep_last: How many recent checkpoints to keep.
        keep_best: How many best checkpoints to keep.
        tensorboard: Enable TensorBoard logging if available.

    Returns:
        Dict with training artifacts/metrics.
    """

    if tokenizer is None and (tokenizer_name or tokenizer_path):
        tokenizer = load_tokenizer(tokenizer_name, tokenizer_path)

    set_seed(seed, checkpoint_dir)

    if use_deeplearning:
        # Back-compat: also pass a derived legacy use_scheduler flag
        legacy_use_scheduler = bool(scheduler) if isinstance(scheduler, bool) else False
        # apply LoRA adapters if possible
        from codex_ml.peft.peft_adapter import apply_lora

        model = None
        if tokenizer is not None:
            vocab_size = getattr(tokenizer, "vocab_size", 0)
            model = MiniLM(MiniLMConfig(vocab_size=vocab_size))
            model = apply_lora(
                model,
                {
                    "r": lora_r,
                    "lora_alpha": lora_alpha,
                    "lora_dropout": lora_dropout,
                    "bias": lora_bias,
                },
            )

        return _run_minilm_training(
            corpus,
            tokenizer,
            device=device,
            grad_clip=grad_clip,
            grad_accum=grad_accum,
            precision=precision,
            use_scheduler=legacy_use_scheduler,
            checkpoint_dir=checkpoint_dir,
            resume_from=resume_from,
            keep_last=keep_last,
            keep_best=keep_best,
            scheduler=scheduler,
            tensorboard=tensorboard,
            val_split=val_split,
            test_split=test_split,
            monitoring_args=monitoring_args,
            model_override=model,
        )

    return run_codex_symbolic_pipeline(
        corpus=corpus,
        demos=demos,
        prefs=prefs,
        w=weights,
        pre_cfg=pre_cfg,
        sft_cfg=sft_cfg,
        rm_cfg=rm_cfg,
        rlhf_cfg=rlhf_cfg,
        tokenizer=tokenizer,
    )


def _run_minilm_training(
    corpus: List[str],
    tokenizer: Optional[TokenizerAdapter],
    *,
    device: Optional[str] = None,
    grad_clip: Optional[float] = None,
    grad_accum: int = 1,
    precision: str = "fp32",
    # Legacy flag (kept for backward compatibility). If `scheduler` is provided, it takes precedence.
    use_scheduler: bool = False,
    checkpoint_dir: Optional[str] = None,
    resume_from: Optional[str] = None,
    keep_last: int = 5,
    keep_best: int = 1,
    # New flexible scheduler selector: None/False->off, True->"steplr", "steplr"->StepLR
    scheduler: Optional[Union[bool, str]] = None,
    tensorboard: bool = False,
    val_split: float = 0.10,
    test_split: float = 0.0,
    monitoring_args: Optional[argparse.Namespace] = None,
    model_override: Optional[torch.nn.Module] = None,
) -> Dict[str, Any]:
    """Train a tiny MiniLM model on the provided corpus.

    When ``tensorboard`` is ``True`` and the optional SummaryWriter is
    available, training metrics are logged under ``<checkpoint_dir>/tensorboard``.
    """
    if not corpus:
        raise ValueError("corpus required for deep learning mode")

    # Ensure deterministic-ish behavior and initialize run directory
    run_dir = Path(checkpoint_dir or ".")
    run_dir.mkdir(parents=True, exist_ok=True)
    metrics_file = Path(os.getenv("METRICS_JSON_PATH", str(run_dir / "metrics.json")))
    metrics_file.touch(exist_ok=True)
    # Prepare tokenizer/encoding
    if tokenizer is None:
        vocab = sorted({ch for text in corpus for ch in text})
        stoi = {ch: i for i, ch in enumerate(vocab)}
        vocab_size = len(vocab)

        def encode(s: str) -> List[int]:
            return [stoi[c] for c in s]

    else:
        vocab_size = tokenizer.vocab_size

        def encode(s: str) -> List[int]:
            return tokenizer.encode(s)

    tokens = [tid for text in corpus for tid in encode(text)]

    # --- split into train/val/test ---
    total = len(tokens)
    val_split = max(0.0, min(0.999, float(val_split)))
    test_split = max(0.0, min(0.999, float(test_split)))
    if val_split + test_split >= 1.0:
        print("Warning: val_split + test_split >= 1; clamping to 0")
        val_split = 0.0
        test_split = 0.0
    n_val = int(total * val_split)
    n_test = int(total * test_split)
    n_train = total - n_val - n_test
    if n_train < 2:
        # Not enough data; fall back to all-train
        n_train = total
        n_val = 0
        n_test = 0
        if total > 0:
            print(
                "Warning: dataset too small for validation/test split; using all data for training"
            )
    train_tokens = tokens[:n_train]
    val_tokens = tokens[n_train : n_train + n_val]
    _ = tokens[n_train + n_val : n_train + n_val + n_test]

    data = torch.tensor(train_tokens, dtype=torch.long).unsqueeze(0)
    val_tensor = (
        torch.tensor(val_tokens, dtype=torch.long).unsqueeze(0) if len(val_tokens) > 1 else None
    )

    cfg = MiniLMConfig(
        vocab_size=vocab_size,
        n_layers=1,
        d_model=32,
        n_heads=4,
        max_seq_len=data.size(1),
    )
    dev = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    print(f"Using device: {dev}")
    model = model_override.to(dev) if model_override is not None else MiniLM(cfg).to(dev)
    opt = torch.optim.AdamW(model.parameters(), lr=1e-3)

    # Normalize scheduler selection (string selector takes precedence over legacy bool)
    _sched_selector: Optional[Union[bool, str]] = scheduler
    if _sched_selector is None and use_scheduler:
        _sched_selector = True

    if _sched_selector in (True, "steplr"):
        sched = torch.optim.lr_scheduler.StepLR(opt, step_size=10, gamma=0.9)
    else:
        sched = None

    # Checkpoint manager
    mgr: Optional[CheckpointManager] = None
    if checkpoint_dir:
        mgr = CheckpointManager(run_dir, keep_last=keep_last, keep_best=keep_best)
        if resume_from:
            try:
                mgr.resume_from(Path(resume_from), model=model, optimizer=opt, scheduler=sched)
            except Exception as e:
                # Non-fatal: continue training anew if resume fails
                print(f"Warning: failed to resume from {resume_from}: {e}")

    inputs = data[:, :-1].to(dev)
    targets = data[:, 1:].to(dev)
    if val_tensor is not None:
        val_inputs = val_tensor[:, :-1].to(dev)
        val_targets = val_tensor[:, 1:].to(dev)
    else:
        val_inputs = val_targets = None
    losses: List[float] = []

    # Hash the config for traceability (used by checkpoints)
    cfg_payload = dict(vars(cfg))
    cfg_payload["vocab_size"] = vocab_size

    writer = None
    if tensorboard and SummaryWriter is not None:
        tb_dir = run_dir / "tensorboard"
        tb_dir.mkdir(parents=True, exist_ok=True)
        try:
            writer = SummaryWriter(log_dir=str(tb_dir))
        except Exception:
            writer = None

    loggers: CodexLoggers = _codex_logging_bootstrap(monitoring_args or argparse.Namespace())

    for epoch in range(3):
        logits = None

        def _compute_loss(_):
            nonlocal logits
            logits = model(inputs)
            return F.cross_entropy(logits.reshape(-1, cfg.vocab_size), targets.reshape(-1))

        loss_val = codex_train_step(
            model,
            opt,
            sched,
            _compute_loss,
            None,
            accum_steps=grad_accum,
            precision=precision,
            grad_clip=grad_clip,
        )

        # Compute accuracy and perplexity with robust fallbacks across metric APIs
        preds = logits.argmax(dim=-1).reshape(-1).tolist()
        tgt = targets.reshape(-1).tolist()

        # token_accuracy: prefer (preds, tgt), fall back to (logits, targets)
        try:
            acc = float(token_accuracy(preds, tgt))  # type: ignore[call-arg]
        except Exception:
            try:
                acc = float(token_accuracy(logits, targets))  # type: ignore[call-arg]
            except Exception:
                acc = float("nan")

        # perplexity: prefer logits-based API with from_logits, fall back to loss-based
        try:
            ppl = float(
                perplexity(
                    logits.reshape(-1, cfg.vocab_size).detach().cpu().tolist(),
                    tgt,
                    from_logits=True,  # type: ignore[call-arg]
                )
            )
        except Exception:
            try:
                ppl = float(perplexity(loss_val))  # type: ignore[call-arg]
            except Exception:
                ppl = float("nan")

        if writer:
            writer.add_scalar("train/loss", loss_val, epoch + 1)
            writer.add_scalar("train/token_accuracy", acc, epoch + 1)
            writer.add_scalar("train/perplexity", ppl, epoch + 1)

        try:
            sysd = _codex_sample_system()
            scalars = {
                "train/loss": loss_val,
                "train/token_accuracy": acc,
                "train/perplexity": ppl,
                **{k: v for k, v in sysd.items() if v is not None},
            }
            _codex_log_all(epoch + 1, scalars, loggers)
        except Exception as exc:
            print(f"[monitoring-error] {exc}", file=sys.stderr)

        if mgr:
            try:
                mgr.save(
                    epoch,
                    model=model,
                    optimizer=opt,
                    scheduler=sched,
                    config={"vocab_size": vocab_size, **cfg_payload},
                    metrics={"loss": loss_val, "accuracy": acc, "perplexity": ppl},
                )
            except Exception as e:
                print(f"Warning: checkpoint save failed at epoch {epoch + 1}: {e}")

        if writer:
            writer.add_scalar("loss", loss_val, epoch)
            writer.add_scalar("accuracy", acc, epoch)
            writer.add_scalar("perplexity", ppl, epoch)

        losses.append(loss_val)

        if val_inputs is not None:
            with torch.no_grad():
                v_logits = model(val_inputs)
                v_loss = F.cross_entropy(
                    v_logits.reshape(-1, cfg.vocab_size),
                    val_targets.reshape(-1),
                )
                v_preds = v_logits.argmax(dim=-1).reshape(-1).tolist()
                v_tgt = val_targets.reshape(-1).tolist()
                try:
                    v_acc = float(token_accuracy(v_preds, v_tgt))
                except Exception:
                    v_acc = _safe_token_accuracy(v_tgt, v_preds)
                try:
                    v_ppl = float(perplexity(float(v_loss.item())))
                except Exception:
                    v_ppl = _safe_perplexity([float(v_loss.item())])

            try:
                sysd = _codex_sample_system()
                val_metrics = {
                    "val/token_accuracy": v_acc,
                    "val/perplexity": v_ppl,
                    **{k: v for k, v in sysd.items() if v is not None},
                }
                _codex_log_all(epoch + 1, val_metrics, loggers)
            except Exception as exc:
                print(f"[monitoring-error] {exc}", file=sys.stderr)
            emit_validation_metric_record(
                str(metrics_file),
                {
                    "epoch": epoch + 1,
                    "split": "val",
                    "token_accuracy": v_acc,
                    "perplexity": v_ppl,
                    "config": {
                        "val_split": val_split,
                        "test_split": test_split,
                        "epoch": epoch + 1,
                    },
                },
            )

    if writer:
        try:
            writer.flush()
            writer.close()
        except Exception as exc:
            print(f"[monitoring-error] {exc}", file=sys.stderr)

    return {"losses": losses, "metrics_path": str(metrics_file)}


__all__ = [
    "run_functional_training",
    "build_parser",
    "main",
    "emit_validation_metric_record",
]


def build_parser() -> "argparse.ArgumentParser":
    """Build an argument parser for the functional training demo."""
    p = argparse.ArgumentParser(description="Run functional training demo")
    p.add_argument("--use-deeplearning", action="store_true", help="use MiniLM training")
    p.add_argument("--device", type=str, default=None, help="torch device override")
    p.add_argument("--grad-clip", type=float, default=None, help="gradient clipping norm")

    # New string-based scheduler selector
    p.add_argument(
        "--scheduler",
        type=str,
        choices=["steplr"],
        default=None,
        help="optional LR scheduler (select type)",
    )
    # Legacy boolean for backward compatibility (equivalent to --scheduler steplr)
    p.add_argument(
        "--use-scheduler",
        action="store_true",
        help="legacy flag to enable a default scheduler (equivalent to --scheduler steplr)",
    )

    p.add_argument("--grad-accum", type=int, default=1, help="gradient accumulation steps")
    p.add_argument(
        "--precision",
        type=str,
        choices=["fp32", "fp16", "bf16"],
        default="fp32",
        help="training precision",
    )
    p.add_argument("--checkpoint-dir", type=str, default=None, help="checkpoint directory")
    p.add_argument(
        "--resume-from",
        type=str,
        default=None,
        help="path to checkpoint to resume from",
    )
    p.add_argument("--keep-last", type=int, default=5, help="how many recent checkpoints to keep")
    p.add_argument("--keep-best", type=int, default=1, help="how many best checkpoints to keep")
    p.add_argument("--seed", type=int, default=0, help="random seed for reproducibility")
    p.add_argument(
        "--tensorboard",
        action="store_true",
        help="enable TensorBoard logging under CHECKPOINT_DIR/runs",
    )
    p.add_argument(
        "--val-split",
        type=float,
        default=0.10,
        help="validation split fraction [0,1)",
    )
    p.add_argument(
        "--test-split",
        type=float,
        default=0.0,
        help="test split fraction [0,1)",
    )
    p.add_argument("--lora-r", type=int, default=8, help="LoRA rank")
    p.add_argument("--lora-alpha", type=int, default=16, help="LoRA alpha")
    p.add_argument("--lora-dropout", type=float, default=0.05, help="LoRA dropout")
    p.add_argument(
        "--lora-bias",
        type=str,
        default="none",
        choices=["none", "lora_only", "all"],
        help="LoRA bias handling",
    )
    _codex_monitor_patch_argparse(p)
    _functional_patch_argparse(p)
    return p


def main() -> None:  # pragma: no cover - convenience CLI
    parser = build_parser()
    args = parser.parse_args()

    # Determine scheduler preference with backward compatibility
    scheduler_opt: Optional[Union[bool, str]] = args.scheduler
    if scheduler_opt is None and getattr(args, "use_scheduler", False):
        scheduler_opt = True  # legacy flag behaves like enabling default "steplr"

    if not args.use_deeplearning:
        print("Symbolic pipeline is not wired for CLI; use programmatic API instead.")
        return

    run_functional_training(
        corpus=["hello world"],
        demos=[],
        prefs=[],
        use_deeplearning=True,
        device=args.device,
        grad_clip=args.grad_clip,
        grad_accum=args.grad_accum,
        precision=args.precision,
        scheduler=scheduler_opt,
        checkpoint_dir=args.checkpoint_dir,
        resume_from=args.resume_from,
        keep_last=args.keep_last,
        keep_best=args.keep_best,
        seed=args.seed,
        tensorboard=args.tensorboard,
        val_split=args.val_split,
        test_split=args.test_split,
        monitoring_args=args,
        lora_r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        lora_bias=args.lora_bias,
    )


if __name__ == "__main__":
    main()
# BEGIN: CODEX_FUNCTR_DEEPNN
# Codex injection: deep-learning toggles, device, grad-clip, scheduler, per-epoch metrics


def _codex_config_hash(cfg: dict) -> str:
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:16]


def _codex_autodevice(cli_device: str | None = None) -> str:
    try:
        import torch

        if cli_device:
            return cli_device
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return cli_device or "cpu"


def _codex_maybe_scheduler(optimizer, name: str | None, **kw):
    try:
        import torch.optim as optim

        if not name:
            return None
        name = name.lower()
        if name in ("cosine", "cosineannealinglr"):
            return optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=kw.get("t_max", 50))
        if name in ("step", "steplr"):
            return optim.lr_scheduler.StepLR(
                optimizer, step_size=kw.get("step_size", 10), gamma=kw.get("gamma", 0.1)
            )
    except Exception:
        return None
    return None


def _codex_epoch_metrics(y_true, y_pred) -> dict:
    try:
        from codex_ml.metrics import perplexity, token_accuracy

        return {
            "token_accuracy": float(token_accuracy(y_true, y_pred)),
            "perplexity": float(perplexity(y_true, y_pred)),
        }
    except Exception:
        return {"token_accuracy": 0.0, "perplexity": 0.0}


def _codex_write_metrics(run_dir: Path, record: dict):
    run_dir.mkdir(parents=True, exist_ok=True)
    f = run_dir / "metrics.json"
    with f.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")


def _codex_apply_training_integration(args, train_loop_fn, config: dict):
    if not getattr(args, "use_deeplearning", False):
        return train_loop_fn
    device = _codex_autodevice(getattr(args, "device", None))
    grad_clip = float(getattr(args, "grad_clip", 0.0) or 0.0)
    sched_name = getattr(args, "scheduler", None)

    def wrapped_train_loop(epoch_cb=None):
        last_sched = None
        if epoch_cb is None:

            def epoch_cb(epoch, model=None, optimizer=None, y_true=None, y_pred=None):
                pass

        def cb(epoch, model=None, optimizer=None, y_true=None, y_pred=None):
            nonlocal last_sched
            if grad_clip > 0 and model is not None:
                try:
                    import torch

                    torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
                except Exception:
                    pass
            if optimizer is not None and sched_name and last_sched is None:
                last_sched = _codex_maybe_scheduler(optimizer, sched_name)
            if last_sched is not None:
                try:
                    last_sched.step()
                except Exception:
                    pass
            rec = {
                "ts": int(time.time()),
                "epoch": int(epoch),
                "device": device,
                "config_hash": _codex_config_hash(config),
                "metrics": _codex_epoch_metrics(y_true, y_pred),
            }
            _codex_write_metrics(Path(config.get("run_dir", "runs/default")), rec)
            return epoch_cb(epoch, model=model, optimizer=optimizer, y_true=y_true, y_pred=y_pred)

        return train_loop_fn(epoch_cb=cb)

    return wrapped_train_loop


def _functional_patch_argparse(ap: argparse.ArgumentParser) -> None:
    added = [a.dest for g in ap._action_groups for a in g._group_actions]  # type: ignore
    if "use_deeplearning" not in added:
        ap.add_argument(
            "--use-deeplearning",
            action="store_true",
            help="Enable MiniLM training path and metrics",
        )
    if "device" not in added:
        ap.add_argument("--device", default=None, help="Override device (cpu/cuda)")
    if "grad_clip" not in added:
        ap.add_argument(
            "--grad-clip",
            dest="grad_clip",
            type=float,
            default=0.0,
            help="Max grad norm",
        )
    if "scheduler" not in added:
        ap.add_argument("--scheduler", default=None, help="LR scheduler (cosine, step)")


# END: CODEX_FUNCTR_DEEPNN


# --- Codex: grad-accum + AMP helpers (offline safe) ---
def _codex_amp_supported() -> bool:
    import torch

    return torch.cuda.is_available()


def codex_train_step(
    model,
    optimizer,
    scheduler,
    compute_loss,
    batch,
    accum_steps=1,
    precision="fp32",
    grad_clip=None,
):
    import torch

    use_fp16 = (precision == "fp16") and _codex_amp_supported()
    scaler = torch.cuda.amp.GradScaler() if use_fp16 else None
    optimizer.zero_grad(set_to_none=True)
    total_loss = 0.0

    if isinstance(batch, (list, tuple)):
        micro_batches = list(batch)
    else:
        micro_batches = [batch] * max(1, accum_steps)

    num_micro_batches = len(micro_batches)

    for mb in micro_batches:
        if use_fp16:
            with torch.autocast(device_type="cuda", dtype=torch.float16):
                loss = compute_loss(mb)
            scaler.scale(loss / num_micro_batches).backward()

        else:
            loss = compute_loss(mb)
            (loss / num_micro_batches).backward()
        total_loss += float(loss.detach().item())

    if grad_clip is not None:
        try:
            clip_grad_norm_(model.parameters(), grad_clip)
        except Exception:
            pass

    if scaler:
        scaler.step(optimizer)
        scaler.update()
    else:
        optimizer.step()

    if scheduler:
        scheduler.step()

    return total_loss / num_micro_batches

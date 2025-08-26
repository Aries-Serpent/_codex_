# [Script]: functional_training.py
# > Generated: 2025-08-26 06:29:37 | Author: mbaetiong
"""Convenience wrapper around the symbolic pipeline with optional tokenization."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import torch
import torch.nn.functional as F
from torch.nn.utils import clip_grad_norm_

from codex_ml.metrics import perplexity, token_accuracy
from codex_ml.models import MiniLM, MiniLMConfig
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
    # Accept both legacy boolean and new string-based scheduler identifiers:
    # - True behaves like "steplr"
    # - None/False disables scheduler
    scheduler: Optional[Union[bool, str]] = None,
    checkpoint_dir: Optional[str] = None,
    resume_from: Optional[str] = None,
    keep_last: int = 5,
    keep_best: int = 1,
    tensorboard: bool = False,
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
        scheduler: Optional scheduler selector ("steplr") or legacy bool.
        checkpoint_dir: Directory for checkpoints and metrics.
        resume_from: Optional checkpoint to resume from.
        keep_last: How many recent checkpoints to keep.
        keep_best: How many best checkpoints to keep.

    Returns:
        Dict with training artifacts/metrics.
    """

    if tokenizer is None and (tokenizer_name or tokenizer_path):
        tokenizer = load_tokenizer(tokenizer_name, tokenizer_path)

    set_seed(seed, checkpoint_dir)

    if use_deeplearning:
        # Back-compat: also pass a derived legacy use_scheduler flag
        legacy_use_scheduler = bool(scheduler) if isinstance(scheduler, bool) else False
        return _run_minilm_training(
            corpus,
            tokenizer,
            device=device,
            grad_clip=grad_clip,
            use_scheduler=legacy_use_scheduler,
            checkpoint_dir=checkpoint_dir,
            resume_from=resume_from,
            keep_last=keep_last,
            keep_best=keep_best,
            scheduler=scheduler,
            tensorboard=tensorboard,
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
    # Legacy flag (kept for backward compatibility). If `scheduler` is provided, it takes precedence.
    use_scheduler: bool = False,
    checkpoint_dir: Optional[str] = None,
    resume_from: Optional[str] = None,
    keep_last: int = 5,
    keep_best: int = 1,
    # New flexible scheduler selector: None/False->off, True->"steplr", "steplr"->StepLR
    scheduler: Optional[Union[bool, str]] = None,
    tensorboard: bool = False,
) -> Dict[str, Any]:
    """Train a tiny MiniLM model on the provided corpus."""
    if not corpus:
        raise ValueError("corpus required for deep learning mode")

    # Ensure deterministic-ish behavior and initialize run directory
    run_dir = Path(checkpoint_dir or ".")
    run_dir.mkdir(parents=True, exist_ok=True)
    metrics_file = run_dir / "metrics.json"
    writer = None
    if tensorboard:
        try:
            from torch.utils.tensorboard import SummaryWriter

            writer = SummaryWriter(log_dir=run_dir / "runs")
        except Exception:
            writer = None

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
    data = torch.tensor(tokens, dtype=torch.long).unsqueeze(0)

    cfg = MiniLMConfig(
        vocab_size=vocab_size,
        n_layers=1,
        d_model=32,
        n_heads=4,
        max_seq_len=data.size(1),
    )
    dev = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    print(f"Using device: {dev}")
    model = MiniLM(cfg).to(dev)
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
                mgr.resume_from(
                    Path(resume_from), model=model, optimizer=opt, scheduler=sched
                )
            except Exception as e:
                # Non-fatal: continue training anew if resume fails
                print(f"Warning: failed to resume from {resume_from}: {e}")

    inputs = data[:, :-1].to(dev)
    targets = data[:, 1:].to(dev)
    losses: List[float] = []

    # Hash the config for traceability
    cfg_payload = dict(vars(cfg))
    cfg_payload["vocab_size"] = vocab_size
    cfg_hash = hashlib.sha256(
        json.dumps(cfg_payload, sort_keys=True).encode("utf-8")
    ).hexdigest()

    # Load existing metrics (JSON list) if present
    metrics_history: List[Dict[str, Any]] = []
    if metrics_file.exists():
        try:
            existing = json.loads(metrics_file.read_text(encoding="utf-8"))
            if isinstance(existing, list):
                metrics_history = existing
        except Exception:
            # Corrupted metrics; start fresh
            metrics_history = []

    for epoch in range(3):
        opt.zero_grad(set_to_none=True)
        logits = model(inputs)
        loss = F.cross_entropy(logits.reshape(-1, cfg.vocab_size), targets.reshape(-1))
        loss.backward()
        if grad_clip is not None:
            try:
                clip_grad_norm_(model.parameters(), grad_clip)
            except Exception as e:
                print(f"Warning: grad clipping failed (grad_clip={grad_clip}): {e}")
        opt.step()
        if sched:
            try:
                sched.step()
            except Exception as e:
                print(f"Warning: scheduler step failed: {e}")

        loss_val = float(loss.item())

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

        payload = {
            "ts": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            "epoch": epoch + 1,
            "metrics": {"token_accuracy": acc, "perplexity": ppl, "loss": loss_val},
            "config_hash": cfg_hash,
        }

        metrics_history.append(payload)
        try:
            metrics_file.write_text(
                json.dumps(metrics_history, indent=2), encoding="utf-8"
            )
        except Exception as e:
            print(f"Warning: failed to write metrics to {metrics_file}: {e}")
        if writer:
            writer.add_scalar("train/loss", loss_val, epoch + 1)
            writer.add_scalar("train/token_accuracy", acc, epoch + 1)
            writer.add_scalar("train/perplexity", ppl, epoch + 1)

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

        losses.append(loss_val)

    if writer:
        writer.flush()
        writer.close()
    return {"losses": losses, "metrics_path": str(metrics_file)}


__all__ = ["run_functional_training", "build_parser", "main"]


def build_parser() -> "argparse.ArgumentParser":
    """Build an argument parser for the functional training demo."""
    p = argparse.ArgumentParser(description="Run functional training demo")
    p.add_argument(
        "--use-deeplearning", action="store_true", help="use MiniLM training"
    )
    p.add_argument("--device", type=str, default=None, help="torch device override")
    p.add_argument(
        "--grad-clip", type=float, default=None, help="gradient clipping norm"
    )

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

    p.add_argument(
        "--checkpoint-dir", type=str, default=None, help="checkpoint directory"
    )
    p.add_argument(
        "--resume-from",
        type=str,
        default=None,
        help="path to checkpoint to resume from",
    )
    p.add_argument(
        "--keep-last", type=int, default=5, help="how many recent checkpoints to keep"
    )
    p.add_argument(
        "--keep-best", type=int, default=1, help="how many best checkpoints to keep"
    )
    p.add_argument(
        "--seed", type=int, default=0, help="random seed for reproducibility"
    )
    p.add_argument(
        "--tensorboard",
        action="store_true",
        help="enable TensorBoard logging under CHECKPOINT_DIR/runs",
    )
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
        scheduler=scheduler_opt,
        checkpoint_dir=args.checkpoint_dir,
        resume_from=args.resume_from,
        keep_last=args.keep_last,
        keep_best=args.keep_best,
        seed=args.seed,
        tensorboard=args.tensorboard,
    )


if __name__ == "__main__":
    main()

"""Convenience wrapper around the symbolic pipeline with optional tokenization."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
import torch.nn.functional as F
from torch.nn.utils import clip_grad_norm_

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
from codex_ml.utils.checkpointing import CheckpointManager

try:  # Preferred interface
    from codex_ml import metrics as _metrics

    token_accuracy = _metrics.token_accuracy  # type: ignore[attr-defined]
    perplexity = _metrics.perplexity  # type: ignore[attr-defined]
except Exception:  # pragma: no cover - graceful fallback for older layouts
    from codex_ml.eval.metrics import perplexity, token_accuracy


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
    device: Optional[str] = None,
    checkpoint_dir: Optional[str] = None,
    resume_from: Optional[str] = None,
    keep_last: int = 5,
    keep_best: int = 1,
    grad_clip: Optional[float] = None,
    scheduler: Optional[str] = None,
) -> Dict[str, Any]:
    """Run training pipeline, optionally using a tiny Torch model."""

    if tokenizer is None and (tokenizer_name or tokenizer_path):
        tokenizer = load_tokenizer(tokenizer_name, tokenizer_path)

    if use_deeplearning:
        return _run_minilm_training(
            corpus,
            tokenizer,
            device=device,
            checkpoint_dir=checkpoint_dir,
            resume_from=resume_from,
            keep_last=keep_last,
            keep_best=keep_best,
            grad_clip=grad_clip,
            scheduler=scheduler,
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
    checkpoint_dir: Optional[str] = None,
    resume_from: Optional[str] = None,
    keep_last: int = 5,
    keep_best: int = 1,
    grad_clip: Optional[float] = None,
    scheduler: Optional[str] = None,
) -> Dict[str, Any]:
    if not corpus:
        raise ValueError("corpus required for deep learning mode")

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
    sched = None
    if scheduler == "steplr":
        sched = torch.optim.lr_scheduler.StepLR(opt, step_size=10, gamma=0.9)
    mgr: Optional[CheckpointManager] = None
    if checkpoint_dir:
        mgr = CheckpointManager(
            Path(checkpoint_dir), keep_last=keep_last, keep_best=keep_best
        )
        if resume_from:
            mgr.resume_from(
                Path(resume_from), model=model, optimizer=opt, scheduler=sched
            )

    inputs = data[:, :-1].to(dev)
    targets = data[:, 1:].to(dev)
    losses: List[float] = []
    run_dir = Path(checkpoint_dir or ".")
    run_dir.mkdir(parents=True, exist_ok=True)
    metrics_file = run_dir / "metrics.json"
    cfg_hash = hashlib.sha256(
        json.dumps(cfg.__dict__, sort_keys=True).encode("utf-8")
    ).hexdigest()
    for epoch in range(3):
        opt.zero_grad()
        logits = model(inputs)
        loss = F.cross_entropy(logits.reshape(-1, cfg.vocab_size), targets.reshape(-1))
        loss.backward()
        if grad_clip is not None:
            clip_grad_norm_(model.parameters(), grad_clip)
        opt.step()
        if sched:
            sched.step()
        loss_val = float(loss.item())
        preds = logits.argmax(dim=-1).reshape(-1).tolist()
        tgt = targets.reshape(-1).tolist()
        acc = token_accuracy(preds, tgt)
        ppl = perplexity(
            logits.reshape(-1, cfg.vocab_size).detach().cpu().tolist(),
            tgt,
            from_logits=True,
        )
        payload = {
            "ts": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            "epoch": epoch,
            "metrics": {"token_accuracy": acc, "perplexity": ppl, "loss": loss_val},
            "config_hash": cfg_hash,
        }
        prev: List[Dict[str, Any]] = []
        if metrics_file.exists():
            try:
                prev = json.loads(metrics_file.read_text(encoding="utf-8"))
                if not isinstance(prev, list):
                    prev = []
            except Exception:
                prev = []
        prev.append(payload)
        metrics_file.write_text(json.dumps(prev, indent=2), encoding="utf-8")
        if mgr:
            mgr.save(
                epoch,
                model=model,
                optimizer=opt,
                scheduler=sched,
                config={"vocab_size": vocab_size},
                metrics={"loss": loss_val},
            )
        losses.append(loss_val)

    return {"losses": losses, "metrics_path": str(metrics_file)}


__all__ = ["run_functional_training"]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run functional training demo")
    parser.add_argument(
        "--use-deeplearning", action="store_true", help="use MiniLM training"
    )
    parser.add_argument(
        "--device", type=str, default=None, help="torch device override"
    )
    parser.add_argument(
        "--grad-clip", type=float, default=None, help="gradient clipping norm"
    )
    parser.add_argument(
        "--scheduler",
        type=str,
        choices=["steplr"],
        default=None,
        help="optional LR scheduler",
    )
    parser.add_argument("--checkpoint-dir", type=str, default=None)
    parser.add_argument("--resume-from", type=str, default=None)
    return parser.parse_args()


def main() -> None:  # pragma: no cover - convenience CLI
    args = _parse_args()
    if not args.use_deeplearning:
        print("Symbolic pipeline not wired for CLI; use programmatic API instead.")
        return
    run_functional_training(
        corpus=["hello world"],
        demos=[],
        prefs=[],
        use_deeplearning=True,
        device=args.device,
        checkpoint_dir=args.checkpoint_dir,
        resume_from=args.resume_from,
        grad_clip=args.grad_clip,
        scheduler=args.scheduler,
    )


if __name__ == "__main__":
    main()

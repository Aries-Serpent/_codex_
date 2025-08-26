"""Convenience wrapper around the symbolic pipeline with optional tokenization."""

from __future__ import annotations

import json
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Optional

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
    device: Optional[str] = None,
    grad_clip: Optional[float] = None,
    scheduler: bool = False,
    checkpoint_dir: Optional[str] = None,
    resume_from: Optional[str] = None,
    keep_last: int = 5,
    keep_best: int = 1,
) -> Dict[str, Any]:
    """Run training pipeline, optionally using a tiny Torch model."""

    if tokenizer is None and (tokenizer_name or tokenizer_path):
        tokenizer = load_tokenizer(tokenizer_name, tokenizer_path)

    if use_deeplearning:
        return _run_minilm_training(
            corpus,
            tokenizer,
            device=device,
            grad_clip=grad_clip,
            use_scheduler=scheduler,
            checkpoint_dir=checkpoint_dir,
            resume_from=resume_from,
            keep_last=keep_last,
            keep_best=keep_best,
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
    use_scheduler: bool = False,
    checkpoint_dir: Optional[str] = None,
    resume_from: Optional[str] = None,
    keep_last: int = 5,
    keep_best: int = 1,
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
    sched = (
        torch.optim.lr_scheduler.StepLR(opt, step_size=10, gamma=0.9)
        if use_scheduler
        else None
    )
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
    metrics_path = Path(checkpoint_dir or ".") / "metrics.json"
    cfg_hash = sha256(
        json.dumps({"vocab_size": vocab_size}, sort_keys=True).encode()
    ).hexdigest()
    set_seed(0, checkpoint_dir)
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
        acc = token_accuracy(logits, targets)
        ppl = perplexity(loss_val)
        entry = {
            "epoch": epoch + 1,
            "loss": loss_val,
            "accuracy": acc,
            "perplexity": ppl,
            "ts": datetime.utcnow().isoformat(),
            "config_hash": cfg_hash,
        }
        with metrics_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")
        if mgr:
            mgr.save(
                epoch,
                model=model,
                optimizer=opt,
                scheduler=sched,
                config={"vocab_size": vocab_size},
                metrics={"loss": loss_val, "accuracy": acc, "perplexity": ppl},
            )
        losses.append(loss_val)

    return {"losses": losses}


__all__ = ["run_functional_training"]


def build_parser() -> "argparse.ArgumentParser":
    import argparse

    p = argparse.ArgumentParser(description="Run functional training")
    p.add_argument("--use-deeplearning", action="store_true")
    p.add_argument("--device")
    p.add_argument("--grad-clip", type=float)
    p.add_argument("--scheduler", action="store_true")
    return p


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run_functional_training(
        corpus=[],
        demos=[],
        prefs=[],
        use_deeplearning=args.use_deeplearning,
        device=args.device,
        grad_clip=args.grad_clip,
        scheduler=args.scheduler,
    )


if __name__ == "__main__":
    main()
